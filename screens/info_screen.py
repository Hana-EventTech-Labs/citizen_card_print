from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QLineEdit
from PySide6.QtCore import QCoreApplication, Qt
import os
from datetime import datetime
from calendar import monthrange

# 분리된 모듈 임포트
from utils.image_preview_manager import ImagePreviewManager
from utils.keyboard_manager import KeyboardManager
from utils.print_manager import PrintManager
from utils.dialog_manager import MessageDialog
from excel_utils.manager import ExcelManager

class InfoScreen(QWidget):
    """정보 입력 및 이미지 편집 화면"""
    
    def __init__(self, stack, screen_size):
        super().__init__()
        self.stack = stack
        self.screen_size = screen_size
        self.captured_image_path = "resources/captured_image.jpg"  # 기본 경로 설정
        
        # 모듈화된 매니저 클래스 초기화
        self.image_manager = ImagePreviewManager(self)
        self.print_manager = PrintManager()
        self.excel_manager = ExcelManager(self)  # 엑셀 매니저 추가
        
        # UI 초기화 - 키보드 매니저는 입력 필드 생성 후 초기화
        self.setupUI()
        
        # 키보드 매니저 초기화 (입력 필드가 생성된 후)
        self.keyboard_manager = KeyboardManager(self, screen_size)
        self.connect_keyboard()
    
    def setupUI(self):
        """UI 구성요소 설정"""
        self.setupBackground()
        self.add_close_button()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        main_container = QFrame(self)
        main_container.setStyleSheet("background: transparent;")
        main_container.setFixedSize(950, 600)  # 전체 컨테이너 크기
        main_container.move(
            (1920 - 950) // 2,
            50
        )

        # 수평 레이아웃 생성
        h_layout = QHBoxLayout(main_container)
        h_layout.setSpacing(40)  # preview와 폼 사이 간격
        
        # === 왼쪽: Preview 영역 ===
        left_container = QFrame()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(20)  # 위젯 간 간격
        
        # ImagePreviewManager에서 생성한 UI 요소 추가
        left_layout.addWidget(self.image_manager.preview_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addWidget(self.image_manager.controls_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch()  # 남은 공간 채우기
        
        # === 오른쪽: 입력 폼 영역 ===
        right_container = QFrame()
        form_layout = QVBoxLayout(right_container)
        form_layout.setSpacing(10)

        # 공통 스타일시트 선언
        input_style = """
        QLineEdit {
        font-size: 62px;
        font-family: '맑은 고딕';
        padding: 5px;
        border: 2px solid #ccc;
        border-radius: 8px;
        }
        """

        # 이름 입력
        name_label = QLabel("이름")
        name_label.setStyleSheet("font-weight: bold; font-size: 40px;")
        name_hint = QLabel("예시) 홍길동")
        name_hint.setStyleSheet("color: gray; font-size: 20px;")
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(80)
        self.name_input.setStyleSheet(input_style)
        self.name_input.setObjectName("name_input")  # 객체 이름 설정

        # 생년월일 입력 
        birth_label = QLabel("생년월일")
        birth_label.setStyleSheet("font-weight: bold; font-size: 40px;")
        birth_hint = QLabel("예시) 19901231")
        birth_hint.setStyleSheet("color: gray; font-size: 20px;")
        self.birth_input = QLineEdit()
        self.birth_input.setFixedHeight(80)
        self.birth_input.setStyleSheet(input_style)
        self.birth_input.setObjectName("birth_input")  # 객체 이름 설정
        self.birth_input.textChanged.connect(self.validate_birth_input)  # 텍스트 변경 시 검증
        
        # 버튼 컨테이너
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(20)
        
        # 버튼들
        issue_btn = QPushButton("발급")
        retake_btn = QPushButton("재촬영")
        reset_btn = QPushButton("초기화")
        
        for btn in [issue_btn, retake_btn, reset_btn]:
            btn.setFixedSize(135, 90)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #5B9279;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 28px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4A7A64;
                }
            """)
        
        issue_btn.clicked.connect(self.process_and_print)
        retake_btn.clicked.connect(self.retake_photo)
        reset_btn.clicked.connect(self.reset_form)
        
        button_layout.addWidget(issue_btn)
        button_layout.addWidget(retake_btn)
        button_layout.addWidget(reset_btn)
        
        # 폼에 위젯 추가
        form_layout.addWidget(name_label)
        form_layout.addWidget(name_hint)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(birth_label)
        form_layout.addWidget(birth_hint)
        form_layout.addWidget(self.birth_input)
        form_layout.addWidget(button_container)
        form_layout.addStretch()  # 버튼과 입력 필드 사이 공간
        
        # 메인 레이아웃에 좌우 컨테이너 추가
        h_layout.addWidget(left_container)
        h_layout.addWidget(right_container)
    
    def connect_keyboard(self):
        """키보드와 입력 필드 연결"""
        self.keyboard_manager.connect_input_field(self.name_input)
        self.keyboard_manager.connect_input_field(self.birth_input)
        
        # 초기에 이름 입력 필드를 활성화
        self.keyboard_manager.activate_input(self.name_input)

    def setupBackground(self):
        """배경 이미지 설정"""
        pixmap = QPixmap("resources/bg.png")  # 이미지 로드
        background_label = QLabel(self)
        background_label.setPixmap(pixmap)
        background_label.setScaledContents(True)  # QLabel 크기에 맞게 이미지 조정
        background_label.resize(*self.screen_size)  # 전체 화면 크기로 설정

    def add_close_button(self):
        """오른쪽 상단에 닫기 버튼 추가"""
        self.close_button = QPushButton("X", self)
        self.close_button.setFixedSize(40, 40)
        self.close_button.move(self.screen_size[0] - 50, 10)  # 오른쪽 상단 위치
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5c5c;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e04a4a;
            }       
        """)
        self.close_button.clicked.connect(self.close_application)
        
    def close_application(self):
        """앱 종료 동작"""
        QCoreApplication.instance().quit()  # 전체 애플리케이션 종료
    
    def closeEvent(self, event):
        """위젯이 닫힐 때 호출되는 이벤트 핸들러"""
        QCoreApplication.instance().quit()  # 전체 애플리케이션 종료
        event.accept()
    
    def showEvent(self, event):
        """위젯이 표시될 때 호출되는 이벤트 핸들러"""
        super().showEvent(event)
        # 이미지 경로 설정
        self.image_manager.set_image_path(self.captured_image_path)
        # 이미지 미리보기 업데이트
        self.image_manager.update_preview()
        # 키보드 표시 (초기 설정된 필드에 연결)
        self.keyboard_manager.show_keyboard()
    
    def reset_form(self):
        """폼 초기화"""
        self.name_input.clear()
        self.birth_input.clear()
        # 이미지 미리보기 초기화
        self.image_manager.reset()
        # 이름 입력 필드에 포커스
        self.keyboard_manager.activate_input(self.name_input)
        
    def retake_photo(self):
        """재촬영 버튼 클릭 시 호출되는 메서드"""
        # 이미지 위치와 회전 각도 초기화
        self.image_manager.reset()
        
        # 키보드 숨기기
        self.keyboard_manager.hide_keyboard()
        
        # 웹캠 카운트다운 초기화
        if hasattr(self.stack.parent(), 'photo_screen') and hasattr(self.stack.parent().photo_screen, 'webcam'):
            self.stack.parent().photo_screen.webcam.reset_countdown()
            
        # 원본 이미지 삭제
        try:
            if hasattr(self, 'captured_image_path') and os.path.exists(self.captured_image_path):
                os.remove(self.captured_image_path)
                print(f"재촬영: 원본 이미지가 삭제되었습니다: {self.captured_image_path}")
        except Exception as e:
            print(f"재촬영: 원본 이미지 삭제 중 오류 발생: {e}")
            
        # PhotoScreen으로 돌아가기
        self.stack.setCurrentIndex(1)

    def process_and_print(self):
        """발급 버튼 클릭 시 호출되는 메서드"""
        # 이름과 생년월일 유효성 검사 (생년월일은 저장만 하고 출력하지 않음)
        name = self.name_input.text().strip()
        birth = self.birth_input.text().strip()
        
        if not name:
             # 이름이 없는 경우 메시지 표시
            dialog = MessageDialog(
                parent=self,
                title="입력 오류",
                message="이름을 입력해주세요."
            )
            dialog.exec()
            return
            
        if not birth or len(birth) != 8 or not birth.isdigit():
            # 생년월일 형식이 맞지 않는 경우 메시지 표시
            dialog = MessageDialog(
                parent=self,
                title="입력 오류",
                message="생년월일을 8자리 숫자로 입력해주세요. (예: 19901231)"
            )
            dialog.exec()
            return
        
        # 엑셀 검증 진행
        if not self.excel_manager.validate_user(name, birth):
            # 검증 실패 또는 사용자가 취소 선택
            return
            
        # 키보드 숨기기
        self.keyboard_manager.hide_keyboard()
            
        # 프리뷰 영역 좌표 계산 (이미지 저장 없이)
        self.image_manager.show_preview_area(debug_mode=False)
            
        # 프리뷰 영역 크롭
        crop_result = self.image_manager.crop_preview_area()
        if crop_result is None:
            # 이미지 처리 실패 시 메시지 표시
            dialog = MessageDialog(
                parent=self,
                title="이미지 처리 오류",
                message="이미지 처리 중 오류가 발생했습니다."
            )
            dialog.exec()
            return
            
        # 크롭된 이미지 경로
        cropped_image_path = crop_result["output_path"]
        
        # 원본 이미지 경로 저장
        self.original_image_path = crop_result["original_path"]
        # 엑셀에 카드 발급 정보 등록
        success = self.excel_manager.register_card(name, birth)
        
        if not success:
            # 등록 실패 시 메시지 표시
            dialog = MessageDialog(
                parent=self,
                title="등록 오류",
                message="카드 발급 정보 등록 중 오류가 발생했습니다."
            )
            dialog.exec()
            return
        
        # 인쇄 작업 시작 - 이름만 전달
        success = self.print_manager.print_card(
            cropped_image_path, 
            name,
            on_finished_callback=self.on_printing_finished,
            show_preview=True
        )
        
        if success:
            # 프린트 작업 시작 후 스플래시 화면으로 돌아가기
            self.stack.setCurrentIndex(0)
            self.reset_form()
  
            # 발급 완료 메시지 표시
            dialog = MessageDialog(
                parent=self.stack.parent(),
                title="발급 완료",
                message="카드 발급이 완료되었습니다.",
                auto_close_ms=3000  # 3초 후 자동 닫기
            )
            dialog.exec()
 
    def on_printing_finished(self):
        """인쇄 완료 후 처리"""
        # 임시 이미지 파일 정리
        self.print_manager.clean_up_image_files([
            "resources/cropped_preview.jpg",
            "resources/preview_area.jpg"
        ])
        
        # 원본 이미지 삭제
        try:
            if hasattr(self, 'original_image_path') and os.path.exists(self.original_image_path):
                os.remove(self.original_image_path)
                print(f"원본 이미지가 삭제되었습니다: {self.original_image_path}")
        except Exception as e:
            print(f"원본 이미지 삭제 중 오류 발생: {e}")

    def validate_birth_input(self, text):
        """생년월일 입력값 검증"""
        if not text:
            return
            
        numbers_only = ''.join(filter(str.isdigit, text))
        current = datetime.now()
        
        # 각 자릿수별 검증 함수 실행
        numbers_only = self._validate_by_length(numbers_only, current)
        
        if numbers_only != text:
            self.birth_input.setText(numbers_only)
            self.birth_input.setCursorPosition(len(numbers_only))
    
    def _validate_by_length(self, numbers, current):
        """자릿수별 유효성 검증"""
        length = len(numbers)
        
        # 검증 함수 매핑
        validators = {
            1: self._validate_first_digit,
            2: self._validate_second_digit,
            3: self._validate_third_digit,
            4: self._validate_year,
            5: self._validate_month_first_digit,
            6: self._validate_month,
            7: self._validate_day_first_digit,
            8: self._validate_full_date
        }
        
        # 해당 자릿수의 검증 함수 실행
        if length in validators:
            numbers = validators[length](numbers, current)
            
        return numbers[:8]  # 8자리로 제한
    
    def _validate_first_digit(self, numbers, _):
        """첫 자리는 1 또는 2만 허용"""
        return '' if not numbers.startswith(('1', '2')) else numbers
    
    def _validate_second_digit(self, numbers, _):
        """19 또는 20으로 시작하는지 검증"""
        return numbers[0] if not numbers.startswith(('19', '20')) else numbers
    
    def _validate_third_digit(self, numbers, current):
        """현재 연도의 앞 3자리보다 큰지 검증"""
        if int(numbers) > int(str(current.year)[:3]):
            return numbers[:2]
        return numbers
    
    def _validate_year(self, numbers, current):
        """연도 검증"""
        year = int(numbers[:4])
        return numbers[:3] if year > current.year else numbers
    
    def _validate_month_first_digit(self, numbers, current):
        """월의 첫 자리 검증"""
        year = int(numbers[:4])
        if numbers[4] not in ('0', '1'):
            return numbers[:4]
        if year == current.year:
            current_month = str(current.month).zfill(2)
            if int(numbers[4]) > int(current_month[0]):
                return numbers[:4]
        return numbers
    
    def _validate_month(self, numbers, current):
        """월 전체 검증"""
        year = int(numbers[:4])
        month = int(numbers[4:6])
        
        if month < 1 or month > 12:
            return numbers[:5]
        if year == current.year and month > current.month:
            return numbers[:5]
        return numbers
    
    def _validate_day_first_digit(self, numbers, current):
        """일의 첫 자리 검증"""
        year = int(numbers[:4])
        month = int(numbers[4:6])
        
        if not numbers[6].isdigit():
            return numbers[:6]
            
        if month == 2 and numbers[6] not in ('0', '1', '2'):
            return numbers[:6]
        if month != 2 and numbers[6] not in ('0', '1', '2', '3'):
            return numbers[:6]
            
        if year == current.year and month == current.month:
            current_day = str(current.day).zfill(2)
            if int(numbers[6]) > int(current_day[0]):
                return numbers[:6]
        return numbers
    
    def _validate_full_date(self, numbers, current):
        """전체 날짜 검증"""
        try:
            year = int(numbers[:4])
            month = int(numbers[4:6])
            day = int(numbers[6:8])
            
            _, last_day = monthrange(year, month)
            
            if year == current.year and month == current.month:
                if day > current.day:
                    return numbers[:7]
            elif day < 1 or day > last_day:
                return numbers[:7]
                
            return numbers
        except ValueError:
            return numbers[:7]