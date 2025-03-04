from printer_utils.printer_thread import PrinterThread
from printer_utils.device_functions import (
    get_device_list, get_device_id, open_device, draw_image, get_preview_bitmap, 
    print_image, close_device, draw_text, draw_text2, load_font
)
from printer_utils.cffi_defs import SMART_OPENDEVICE_BYID, PAGE_FRONT, PANELID_COLOR
from printer_utils.image_utils import bitmapinfo_to_image
import os
from PySide6.QtCore import QThread, Signal
from utils.temp_path import get_temp_path, cleanup_temp_files

class CardPrinterThread(QThread):
    """이미지와 텍스트를 함께 출력하는 프린터 스레드 클래스"""
    finished = Signal()
    error = Signal(str)
    preview_ready = Signal(object)  # 미리보기 이미지 전달용
    
    def __init__(self, image_filename, name, show_preview=True):
        super().__init__()
        self.image_filename = image_filename
        self.name = name
        self.show_preview = show_preview
        self.is_canceled = False
        
    def cancel(self):
        """인쇄 작업 취소"""
        self.is_canceled = True
        
    def run(self):
        try:
            # 1. 장치 목록 조회
            result, printer_list = get_device_list()
            if result != 0:
                self.error.emit("프린터 목록 가져오기 실패")
                return
                
            # 2. 장치 선택 (첫 번째 장치 사용)
            device_index = 0
            device_id = get_device_id(printer_list, device_index)
            
            # 3. 장치 열기
            result, device_handle = open_device(device_id, SMART_OPENDEVICE_BYID)
            if result != 0:
                self.error.emit("장치 열기 실패")
                return
                
            try:
                # 작업 취소 확인
                if self.is_canceled:
                    return
                
                # base_result = draw_image(device_handle, PAGE_FRONT, PANELID_COLOR,
                #                           0, 0, 635, 1027, "gurye_base_card.jpg")
                # if base_result != 0:
                #     self.error.emit("배경 이미지 그리기 실패")
                #     return
                    
                # 4. 이미지 그리기
                # 카드 크기: 58mm x 90mm (스마트 프린터 기본 설정 635px x 1027px @ 300 DPI)
                card_width = 635    # 58mm
                card_height = 1027  # 90mm
                
                # 이미지 크기: 40mm x 40mm
                image_width = 438  # 40mm @ 300 DPI
                image_height = 438  # 40mm @ 300 DPI
                
                # 이미지 위치 계산 (가로 중앙 정렬)
                image_x = (card_width - image_width) // 2  # 카드 중앙 정렬
                image_y = 250  # 상단에서 아래로 적절한 위치
                
                # 이미지 그리기
                result = draw_image(device_handle, PAGE_FRONT, PANELID_COLOR, 
                                  image_x, image_y, image_width, image_height, 
                                  self.image_filename)
                                  
                if result != 0:
                    self.error.emit("사진 이미지 그리기 실패")
                    return
                
                # 작업 취소 확인
                if self.is_canceled:
                    return
                
                # 5. 텍스트 그리기 (중앙 정렬)
                # 폰트 설정
                font_name = "맑은 고딕"  # 한글 지원 폰트
                font_size = 16  # 적절한 크기
                
                # 텍스트 위치 계산 (가로 중앙, 이미지 아래)
                # 참고: draw_text 함수는 텍스트를 가로 중앙에 배치하는 옵션이 없음
                # 텍스트 너비를 대략 추정하여 위치 조정
                # 한글은 문자당 약 font_size 픽셀의 너비 가정
                text_width = 438  # 대략적인 텍스트 너비
                text_height = 100
                text_x = image_x
                text_y = image_y + image_height + 50  # 이미지 아래 여백
                
                # 이름 그리기
                name_result = draw_text2(device_handle, PAGE_FRONT, PANELID_COLOR,
                                      text_x, text_y, text_width, text_height, font_name, font_size, 0, 0x00,
                                      0x000000, self.name, 0, 0x01, 0)
                                      
                if name_result != 0:
                    # 기본 폰트로 재시도
                    font_name = "Arial"
                    name_result = draw_text2(device_handle, PAGE_FRONT, PANELID_COLOR,
                                      text_x, text_y, text_width, text_height, font_name, font_size, 0x00,
                                      0x000000, self.name, 0, 0x01, 0)
                    if name_result != 0:
                        self.error.emit("이름 텍스트 그리기 실패")
                
                # 작업 취소 확인
                if self.is_canceled:
                    return
                
                # 6. 미리보기 비트맵 가져오기 (필요한 경우)
                # if self.show_preview:
                #     result, bm_info = get_preview_bitmap(device_handle, PAGE_FRONT)
                #     if result == 0:
                #         image = bitmapinfo_to_image(bm_info)
                #         if image:
                #             self.preview_ready.emit(image)
                #     else:
                #         self.error.emit("미리보기 비트맵 가져오기 실패")
                        # 실패해도 계속 진행
                
                # 작업 취소 확인
                if self.is_canceled:
                    return
                
                # 7. 이미지 인쇄
                result = print_image(device_handle)
                if result != 0:
                    self.error.emit("이미지 인쇄 실패")
                    return
                    
                self.finished.emit()
            finally:
                # 8. 장치 닫기 (항상 실행)
                close_device(device_handle)
        except Exception as e:
            self.error.emit(f"인쇄 중 오류 발생: {str(e)}")


class PrintManager:
    """인쇄 관련 기능을 관리하는 클래스"""
    
    def __init__(self):
        self.printer_thread = None
    
    def print_card(self, image_path, name, on_finished_callback=None, show_preview=True):
        """이미지와 텍스트를 포함한 카드 인쇄 시작"""
        if not os.path.exists(image_path):
            print(f"인쇄할 이미지 파일({image_path})이 존재하지 않습니다.")
            return False
                
        image_filename = os.path.basename(image_path)
        self.printer_thread = CardPrinterThread(image_filename, name, show_preview)
        
        # 콜백 연결
        if on_finished_callback:
            self.printer_thread.finished.connect(on_finished_callback)
                
        # 에러 콜백 연결
        self.printer_thread.error.connect(self.on_print_error)
        
        # 미리보기 콜백 연결
        if show_preview:
            self.printer_thread.preview_ready.connect(self.show_preview)
                
        self.printer_thread.start()
        print(f"카드 인쇄 작업을 시작합니다: {image_filename}")
        return True
    
    def print_image(self, image_path, on_finished_callback=None):
        """기존 이미지만 인쇄하는 메서드 (이전 버전과의 호환성 유지)"""
        return self.print_card(image_path, "", on_finished_callback, False)
    
    def on_print_error(self, error_message):
        """인쇄 에러 처리"""
        print(f"인쇄 오류: {error_message}")
    
    def show_preview(self, image):
        """인쇄 미리보기 표시"""
        if image:
            # 미리보기 이미지 표시 (필요한 경우 구현)
            image.show()  # PIL Image 객체인 경우
            pass
    
    def cancel_printing(self):
        """인쇄 작업 취소"""
        if self.printer_thread and self.printer_thread.isRunning():
            self.printer_thread.cancel()
            print("인쇄 작업을 취소했습니다.")
            return True
        return False
    
    def clean_up_image_files(self, image_paths=[]):
        """인쇄 후 이미지 파일 정리"""
        cleanup_temp_files()