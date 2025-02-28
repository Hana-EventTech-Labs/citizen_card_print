from PySide6.QtCore import QThread, Signal
from .device_functions import get_device_list, get_device_id, open_device, draw_image, get_preview_bitmap, print_image, close_device, load_font, draw_text2
from .image_utils import bitmapinfo_to_image
from .cffi_defs import ffi, SMART_OPENDEVICE_BYID, PAGE_FRONT, PANELID_COLOR


class PrinterThread(QThread):
    finished = Signal()
    error = Signal(str)
    # preview_ready = Signal(object)  # 미리보기 이미지 전달용
    
    def __init__(self, file_name = None):
        super().__init__()
        self.file_name = file_name
    
        
    def run(self):

        try:
            # 장치 목록 조회
            result, printer_list = get_device_list()
            if result != 0:
                self.error.emit("프린터 목록 가져오기 실패")
                return
                
            # 장치 선택
            device_index = 0
            device_id = get_device_id(printer_list, device_index)
            
            # 장치 열기
            result, device_handle = open_device(device_id, SMART_OPENDEVICE_BYID)
            if result != 0:
                self.error.emit("장치 열기 실패")
                return
                
            try:
                print(self.file_name)
                result = draw_image(device_handle, PAGE_FRONT, PANELID_COLOR, 0, 0, 413, 472, self.file_name)
                if result != 0:
                    self.error.emit("사진 이미지 그리기 실패")
                    return
                
                # 미리보기 비트맵 가져오기
                result, bm_info = get_preview_bitmap(device_handle, PAGE_FRONT)
                if result == 0:
                    image = bitmapinfo_to_image(bm_info)
                    # self.preview_ready.emit(image)
                    image.show()
                else:
                    self.error.emit("미리보기 비트맵 가져오기 실패")
                    return
                
                # # 이미지 인쇄
                # result = print_image(device_handle)
                # if result != 0:
                #     self.error.emit("이미지 인쇄 실패")
                #     return
                    
                self.finished.emit()
            finally:
                # 장치 닫기 (항상 실행)
                close_device(device_handle)
        except Exception as e:
            self.error.emit(f"인쇄 중 오류 발생: {str(e)}")