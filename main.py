from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import Qt
import sys
import os

from webcam_utils.webcam_controller import release_camera
from webcam_utils.webcam_controller import WebcamViewer
from screens.splash_screen import SplashScreen
from screens.photo_screen import PhotoScreen
from screens.info_screen import InfoScreen
from utils.temp_path import cleanup_temp_files

class KioskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PUBG 스냅샷")
        self.screen_size = (1920, 1080)
        self.setFixedSize(*self.screen_size)
        self.showFullScreen()

        self.stack = QStackedWidget()
        self.setupStack()

        self.setCentralWidget(self.stack)

    def setupStack(self):
        self.stack = QStackedWidget()
        self.splash_screen = SplashScreen(self.stack, self.screen_size)
        self.photo_screen = PhotoScreen(self.stack, self.screen_size)
        self.info_screen = InfoScreen(self.stack, self.screen_size)

        # 스택에 화면 추가
        self.stack.addWidget(self.splash_screen)  # index 0
        self.stack.addWidget(self.photo_screen)  # index 1
        self.stack.addWidget(self.info_screen)  # index 2

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            
    # closeEvent 메서드 수정
    def closeEvent(self, event):
        """창이 닫힐 때 카메라 자원 해제 및 임시 파일 정리"""
        try:
            # 카메라 자원 해제
            if hasattr(self, 'photo_screen') and hasattr(self.photo_screen, 'webcam'):
                if hasattr(self.photo_screen.webcam, 'camera'):
                    release_camera(self.photo_screen.webcam.camera)
            
            # 모든 임시 파일 정리
            cleanup_temp_files()
                    
        except Exception as e:
            print(f"프로그램 종료 시 정리 중 오류 발생: {e}")
            
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KioskApp()
    window.show()
    sys.exit(app.exec())
