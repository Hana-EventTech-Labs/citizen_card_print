from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from keyboard_utils.virtual_keyboard import VirtualKeyboard

class KeyboardManager:
    """가상 키보드 관련 기능을 관리하는 클래스"""
    
    def __init__(self, parent_widget, screen_size):
        self.parent = parent_widget
        self.screen_size = screen_size
        self.active_input = None
        self.setup_virtual_keyboard()
    
    def setup_virtual_keyboard(self):
        """가상 키보드 초기화 및 설정"""
        # 초기에는 임시 빈 QLineEdit과 연결 (None으로 하면 오류 발생 가능)
        temp_input = QLineEdit()
        self.virtual_keyboard = VirtualKeyboard(temp_input)
        
        # 키보드 위치 및 크기 설정 - 화면 하단에 위치하도록 설정
        keyboard_width = 1200
        keyboard_height = 450
        self.virtual_keyboard.setFixedSize(keyboard_width, keyboard_height)
        self.virtual_keyboard.move(
            (self.screen_size[0] - keyboard_width) // 2,
            self.screen_size[1] - keyboard_height - 10
        )
        
        # 키보드가 처음에는 숨겨져 있게 설정
        self.virtual_keyboard.hide()
        self.virtual_keyboard.setParent(self.parent)
        
        # 초기 한/영 상태 설정 (한글로 시작)
        self.virtual_keyboard.is_hangul = True
        self.virtual_keyboard.update_keyboard_labels()
    
    def connect_input_field(self, input_field):
        """입력 필드에 클릭 이벤트 핸들러 연결"""
        if isinstance(input_field, QLineEdit):
            # 원본 이벤트 핸들러 백업
            original_mouse_press = input_field.mousePressEvent
            
            # 새 이벤트 핸들러 정의
            def new_mouse_press_event(event):
                # 원본 이벤트 핸들러 호출 (필요한 경우)
                if original_mouse_press is not None:
                    original_mouse_press(event)
                # 키보드 활성화
                self.activate_input(input_field)
            
            # 새 이벤트 핸들러 설정
            input_field.mousePressEvent = new_mouse_press_event
    
    def activate_input(self, input_field):
        """입력 필드 활성화 및 키보드 연결"""
        # 이전에 활성화된 필드가 있다면 비활성화
        if self.active_input is not None and self.active_input != input_field:
            self.active_input.clearFocus()
        
        self.active_input = input_field
        
        # 키보드의 입력 위젯을 현재 활성화된 필드로 변경
        self.virtual_keyboard.input_widget = input_field
        
        # 키보드 표시
        self.virtual_keyboard.show()
        
        # 필드에 포커스 설정
        input_field.setFocus()
        input_field.setCursorPosition(len(input_field.text()))
        
        self.virtual_keyboard.is_hangul = True
        
        # 키보드 레이블 업데이트
        self.virtual_keyboard.update_keyboard_labels()
    
    def hide_keyboard(self):
        """키보드 숨기기"""
        if self.virtual_keyboard:
            self.virtual_keyboard.hide()
            # 한글 작성 중이던 상태 초기화
            self.virtual_keyboard.hangul_composer.reset()
    
    def show_keyboard(self):
        """키보드 표시하기 (활성 입력 필드가 있을 경우)"""
        if self.active_input is not None and self.virtual_keyboard:
            self.virtual_keyboard.show()