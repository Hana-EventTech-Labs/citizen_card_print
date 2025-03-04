from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QSizePolicy, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from .hangul_composer import HangulComposer


class VirtualKeyboard(QWidget):
    # 기본 한글 매핑
    hangul_map = {
        'Q': 'ㅂ', 'W': 'ㅈ', 'E': 'ㄷ', 'R': 'ㄱ', 'T': 'ㅅ', 
        'Y': 'ㅛ', 'U': 'ㅕ', 'I': 'ㅑ', 'O': 'ㅐ', 'P': 'ㅔ',
        'A': 'ㅁ', 'S': 'ㄴ', 'D': 'ㅇ', 'F': 'ㄹ', 'G': 'ㅎ', 
        'H': 'ㅗ', 'J': 'ㅓ', 'K': 'ㅏ', 'L': 'ㅣ',
        'Z': 'ㅋ', 'X': 'ㅌ', 'C': 'ㅊ', 'V': 'ㅍ', 'B': 'ㅠ', 
        'N': 'ㅜ', 'M': 'ㅡ'
    }

    # Shift 상태일 때의 한글 매핑
    shift_hangul_map = {
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ',
        'Y': 'ㅛ', 'U': 'ㅕ', 'I': 'ㅑ', 'O': 'ㅒ', 'P': 'ㅖ',
        'A': 'ㅁ', 'S': 'ㄴ', 'D': 'ㅇ', 'F': 'ㄹ', 'G': 'ㅎ',
        'H': 'ㅗ', 'J': 'ㅓ', 'K': 'ㅏ', 'L': 'ㅣ',
        'Z': 'ㅋ', 'X': 'ㅌ', 'C': 'ㅊ', 'V': 'ㅍ', 'B': 'ㅠ',
        'N': 'ㅜ', 'M': 'ㅡ'
    }

    
    # 문자 제한 설정
    MAX_LOWERCASE = 100
    MAX_UPPERCASE = 100
    MAX_HANGUL = 100

    def __init__(self, input_widget):
        super().__init__()
        self.input_widget = input_widget

        self.is_hangul = True
        self.is_uppercase = False
        self.hangul_composer = HangulComposer()
        self.initUI()
        self.update_keyboard_labels()

        self.bumper = False

    def initUI(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setStyleSheet("background-color: #FFFFFF;")

        container_layout = QVBoxLayout(container)        
            
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]

        self.button_widgets = []
        for row in self.keys:
            row_layout = QGridLayout()
            row_layout.setSpacing(5)
            row_buttons = []
            for i, key in enumerate(row):
                button = QPushButton(self.get_display_key(key))
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                button.setFont(QFont('맑은 고딕', 28))
                button.clicked.connect(lambda checked, text=key: self.button_clicked(text))
                button.setStyleSheet(self.get_button_style())
                row_layout.addWidget(button, 0, i)
                row_buttons.append(button)
            container_layout.addLayout(row_layout)
            self.button_widgets.append(row_buttons)

        special_layout = QGridLayout()
        special_layout.setSpacing(5)

        # 각 버튼 설정
        hangul_btn = QPushButton('한/영')
        hangul_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        hangul_btn.setFont(QFont('맑은 고딕', 28))
        hangul_btn.clicked.connect(self.toggle_hangul)
        hangul_btn.setStyleSheet(self.get_special_button_style('#4299E1'))
        hangul_btn.setFixedWidth(100)  # 고정 너비 설정

        shift_btn = QPushButton('Shift')
        shift_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        shift_btn.setFont(QFont('맑은 고딕', 28))
        shift_btn.clicked.connect(self.toggle_shift)
        shift_btn.setStyleSheet(self.get_special_button_style('#3182CE'))
        shift_btn.setFixedWidth(100)  # 고정 너비 설정

        space_btn = QPushButton('Space')
        space_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        space_btn.setFont(QFont('맑은 고딕', 28))
        space_btn.clicked.connect(self.space_pressed)
        space_btn.setStyleSheet(self.get_button_style())

        backspace_btn = QPushButton('←')
        backspace_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        backspace_btn.setFont(QFont('맑은 고딕', 28))
        backspace_btn.clicked.connect(self.backspace)
        backspace_btn.setStyleSheet(self.get_special_button_style('#E53E3E'))

        # print_btn = QPushButton('인쇄')
        # print_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # print_btn.setFont(QFont('맑은 고딕', 20))
        # print_btn.clicked.connect(self.print_text)
        # print_btn.setStyleSheet(self.get_special_button_style('#48BB78'))
        # print_btn.setFixedWidth(80)
        
        # 레이아웃에 버튼 추가
        special_layout.addWidget(hangul_btn, 0, 0)
        special_layout.addWidget(shift_btn, 0, 1)
        special_layout.addWidget(space_btn, 0, 2)
        special_layout.addWidget(backspace_btn, 0, 3)
        # special_layout.addWidget(print_btn, 0, 4)
        
        # 열 비율 설정 (총 10을 기준으로)
        special_layout.setColumnStretch(0, 2)  # 한/영 버튼
        special_layout.setColumnStretch(1, 2)  # Shift 버튼
        special_layout.setColumnStretch(2, 4)  # Space 버튼
        special_layout.setColumnStretch(3, 2)  # Backspace 버튼
        # special_layout.setColumnStretch(4, 2)  # 인쇄 버튼

        container_layout.addLayout(special_layout)
        outer_layout.addWidget(container)
        self.setLayout(outer_layout)

    def button_clicked(self, key):
        # print(f"[VirtualKeyboard] bumper: {self.bumper}")
        if self.bumper and self.is_hangul and key in self.hangul_map:
            current_text = self.input_widget.text() + " "
        else:
            current_text = self.input_widget.text()
        
        if self.is_hangul and key in self.hangul_map:
            # 현재 텍스트 길이 체크 (완성된 글자 기준)
            completed_chars = len([c for c in current_text if 0xAC00 <= ord(c) <= 0xD7A3])
            
            # 연속된 자음/모음 입력 체크
            consecutive_jamo = len([c for c in current_text if 0x3131 <= ord(c) <= 0x3163])
            if consecutive_jamo >= self.MAX_HANGUL:
                # print(f"[VirtualKeyboard] Max consecutive jamo reached")
                return
            
            # 4글자 초과 시 입력 차단
            if completed_chars >= self.MAX_HANGUL and not (
                len(current_text) > 0 and 
                current_text[-1] == self.hangul_composer.current_text and 
                self.hangul_composer.cho and 
                self.hangul_composer.jung and 
                not self.hangul_composer.jong
            ):
                # print(f"[VirtualKeyboard] Max length reached: {completed_chars} characters")
                return
                
            jamo = self.shift_hangul_map[key] if self.is_uppercase else self.hangul_map[key]
            committed, current = self.hangul_composer.add_jamo(jamo)
            
            if current_text:
                if self.hangul_composer.current_text:
                    new_text = current_text[:-1]
                else:
                    new_text = current_text
            else:
                new_text = ""
            
            if committed:
                new_text += committed
            if current:
                new_text += current
                
            self.input_widget.setText(new_text)
            self.input_widget.setCursorPosition(len(new_text))
            self.bumper = False
        else:
            if not self.check_length_limit(current_text):
                return
            char = key.upper() if self.is_uppercase else key.lower()
            self.input_widget.setText(current_text + char)
            self.hangul_composer.reset()
            self.bumper = True
        
    def insert_text(self, char):
        if char:
            self.input_widget.setText(self.input_widget.text() + char)
            self.input_widget.setCursorPosition(len(self.input_widget.text()))

    def toggle_hangul(self):
        self.is_hangul = not self.is_hangul
        self.hangul_composer.reset()
        self.update_keyboard_labels()

    def toggle_shift(self):
        self.is_uppercase = not self.is_uppercase
        self.update_keyboard_labels()

    def space_pressed(self):
        if self.is_hangul:
            self.hangul_composer.reset()  # 현재 조합 상태만 초기화
        self.insert_text(' ')
        self.bumper = True
        
    def check_length_limit(self, current_text):
        """
        문자 수 제한을 확인하는 메서드
        """
        current_length = len(current_text)
        
        if self.is_hangul:
            # 항상 종성까지 입력 가능하도록 함
            return current_length < self.MAX_HANGUL
        elif self.is_uppercase:
            return current_length < self.MAX_UPPERCASE
        else:
            return current_length < self.MAX_LOWERCASE


    def backspace(self):
        text = self.input_widget.text()
        if not text:
            return

        last_char = text[-1]
        is_hangul = 0xAC00 <= ord(last_char) <= 0xD7A3

        try:
            if self.hangul_composer.current_text:
                current, changed = self.hangul_composer.backspace()
                if changed:
                    if len(text) > 0:
                        text = text[:-1]
                    if current:
                        text += current
                # print(f"[VirtualKeyboard] current: {current}")
                if len(current) == 0:
                    self.bumper = True
            elif is_hangul:
                char_code = ord(last_char) - 0xAC00
                jong_idx = char_code % 28
                if jong_idx > 0:
                    jung_idx = ((char_code - jong_idx) // 28) % 21
                    cho_idx = ((char_code - jong_idx) // 28) // 21
                    new_code = 0xAC00 + (cho_idx * 21 + jung_idx) * 28
                    text = text[:-1] + chr(new_code)
                else:
                    text = text[:-1]
                self.hangul_composer.reset()
            else:
                text = text[:-1]

        except AttributeError:
            # CHOSUNG/JUNGSUNG 참조 에러 발생 시 단순히 문자 하나 삭제
            text = text[:-1]
            self.hangul_composer.reset()

        self.input_widget.setText(text)
        self.input_widget.setCursorPosition(len(text))
            
    def print_text(self):
        if hasattr(self, 'second_screen') and self.second_screen:
            self.second_screen.print_input()
            
            
    def update_keyboard_labels(self):
        for row_buttons, row_keys in zip(self.button_widgets, self.keys):
            for button, key in zip(row_buttons, row_keys):
                if self.is_hangul:
                    if self.is_uppercase and key in self.shift_hangul_map:
                        button.setText(self.shift_hangul_map[key])
                    else:
                        button.setText(self.hangul_map.get(key, key))
                else:
                    button.setText(key.upper() if self.is_uppercase else key.lower())

    def get_display_key(self, key):
        if self.is_uppercase:
            return key.upper()
        return key.lower()

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #2D3748;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:pressed {
                background-color: #4A5568;
            }
        """

    def get_special_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """

    def darken_color(self, color):
        r, g, b = [int(color[i:i+2], 16) for i in (1, 3, 5)]
        return f'#{max(0, r-30):02X}{max(0, g-30):02X}{max(0, b-30):02X}'

