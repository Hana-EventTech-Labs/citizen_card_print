from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class ValidationDialog(QDialog):
    """사용자 검증 결과를 표시하는 다이얼로그"""
    
    def __init__(self, parent=None, title="검증 결과", message="", is_warning=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(500, 300)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        
        # 메시지 라벨
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFont(QFont("맑은 고딕", 18))
        self.message_label.setWordWrap(True)
        
        # 경고인 경우 스타일 적용
        if is_warning:
            self.message_label.setStyleSheet("color: #E53E3E;")
        
        # 버튼 컨테이너
        button_container = QHBoxLayout()
        
        # 버튼 생성
        self.ok_button = QPushButton("확인")
        self.ok_button.setFixedSize(120, 50)
        self.ok_button.setFont(QFont("맑은 고딕", 14))
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #5B9279;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4A7A64;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        
        # 취소 버튼 (경고인 경우만 표시)
        if is_warning:
            self.cancel_button = QPushButton("취소")
            self.cancel_button.setFixedSize(120, 50)
            self.cancel_button.setFont(QFont("맑은 고딕", 14))
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #A0AEC0;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #718096;
                }
            """)
            self.cancel_button.clicked.connect(self.reject)
            button_container.addWidget(self.cancel_button)
        
        # 버튼 레이아웃에 추가
        button_container.addWidget(self.ok_button)
        button_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 메인 레이아웃에 추가
        layout.addWidget(self.message_label, 1)
        layout.addLayout(button_container)
        
        self.setLayout(layout)


class MessageDialog(QDialog):
    """메시지를 표시하는 간단한 다이얼로그"""
    
    def __init__(self, parent=None, title="알림", message="", auto_close_ms=0):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        
        # 메시지 라벨
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setFont(QFont("맑은 고딕", 16))
        self.message_label.setWordWrap(True)
        
        # 확인 버튼
        self.ok_button = QPushButton("확인")
        self.ok_button.setFixedSize(100, 40)
        self.ok_button.setFont(QFont("맑은 고딕", 12))
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #5B9279;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4A7A64;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        
        # 레이아웃에 추가
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.ok_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        
        # 자동 닫기 옵션
        if auto_close_ms > 0:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(auto_close_ms, self.accept)