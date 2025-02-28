from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QCoreApplication

class SplashScreen(QWidget):
    def __init__(self, stack, screen_size):
        super().__init__()
        self.stack = stack
        self.screen_size = screen_size
        self.setupUI()

    def setupUI(self):
        self.setupBackground()
        self.add_close_button()
        layout = QVBoxLayout()

        self.setLayout(layout)
    
    def setupBackground(self):
        pixmap = QPixmap("resources/main.png")  # 이미지 로드
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

    def mousePressEvent(self, event):
        self.stack.setCurrentIndex(1)
