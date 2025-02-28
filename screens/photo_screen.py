from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QCoreApplication, Qt
from webcam_utils.webcam_controller import WebcamViewer, CountdownThread
import os

class PhotoScreen(QWidget):
    def __init__(self, stack, screen_size):
        super().__init__()
        self.stack = stack
        self.screen_size = screen_size
        self.setupUI()

        
    
    def setupUI(self):
        self.setupBackground()
        self.add_close_button()
        self.add_guide_text()

        self.preview_width = 960
        self.preview_height = 540
        self.webcam = WebcamViewer(
            preview_width=self.preview_width, 
            preview_height=self.preview_height, 
            x=(1920 - self.preview_width) / 2, 
            y=(1080 - self.preview_height) / 2, 
            countdown=3
        )
        self.webcam.setParent(self)

        self.capture_width = 960
        self.capture_height = 540
        self.webcam.set_capture_area(x=(1920 - self.capture_width) / 2, 
                                     y=(1080 - self.capture_height) / 2, 
                                     width=self.capture_width, 
                                     height=self.capture_height)

        # 웹캠의 photo_captured_signal을 on_photo_captured 메서드에 연결
        self.webcam.photo_captured_signal.connect(self.on_photo_captured)

        self.capture_button = self.add_capture_button()

        layout = QVBoxLayout()

        self.setLayout(layout)

    def setupBackground(self):
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

    def add_guide_text(self):
        self.guide_text = QLabel("촬영하기 버튼을 터치하면 3초 뒤 촬영됩니다.\n (전면 카메라를 봐주세요)", self)
        self.guide_text.setFixedWidth(1920)  # 전체 화면 너비로 설정
        self.guide_text.setFixedHeight(200)  # 높이를 200으로 설정
        self.guide_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guide_text.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 64px;  /* 폰트 크기 증가 */
                font-weight: bold;
                background: transparent;
                padding: 20px;  /* 여백 추가 */
                line-height: 1.5;  /* 줄 간격 조정 */
            }
        """)
        # 레이아웃에서 제거하고 직접 위치 지정
        self.guide_text.move(0, self.guide_text.y() + 40)  # x는 0, y는 현재 위치 유지

    def add_capture_button(self):
        self.capture_button = QPushButton("촬영하기", self)
        self.capture_button.setFixedSize(600, 120)
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #5B9279;
                color: white;
                border: 4px solid #4A7A64;
                border-radius: 60px;
                font-size: 48px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #4A7A64;
            }
            QPushButton:pressed {
                background-color: #3A6A54;
                padding-top: 10px;
                padding-left: 10px;
            }
        """)
        self.capture_button.move(
            (1920 - 600) // 2,
            1080 - 200
        )
        # 촬영하기 버튼 클릭 시 웹캠 촬영 이벤트 연결
        self.capture_button.clicked.connect(self.trigger_webcam_capture)
        return self.capture_button
        
    def trigger_webcam_capture(self):
        """촬영하기 버튼 클릭 시 웹캠의 촬영 기능 트리거"""
        # 이미 카운트다운 중인지 확인
        if hasattr(self.webcam, 'countdown_thread') and self.webcam.countdown_thread and self.webcam.countdown_thread.isRunning():
            print("카운트다운 중입니다. 잠시 기다려주세요.")
            return  # 이미 카운트다운 중이면 무시
        
        if self.webcam.countdown_time > 0:
            self.webcam.countdown_label.show()
            self.webcam.countdown_thread = CountdownThread(self.webcam.countdown_time)
            self.webcam.countdown_thread.countdown_signal.connect(self.webcam.update_countdown)
            self.webcam.countdown_thread.finished_signal.connect(self.webcam.capture_photo)
            self.webcam.countdown_thread.start()
        else:
            self.webcam.capture_photo()

    def on_photo_captured(self, file_path):
        self.captured_file_path = file_path
        file_name = os.path.basename(file_path)
        
        # InfoScreen에 파일 경로 전달
        if hasattr(self.stack.parent(), 'info_screen'):
            self.stack.parent().info_screen.captured_image_path = file_path
            
        self.stack.setCurrentIndex(2)

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
        # 화면이 표시될 때 카운트다운 초기화
        if hasattr(self, 'webcam'):
            self.webcam.reset_countdown()


