from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import Qt
import sys
import os

from webcam_utils.webcam_controller import release_camera
from webcam_utils.webcam_controller import WebcamViewer
from screens.splash_screen import SplashScreen
from screens.photo_screen import PhotoScreen
from screens.info_screen import InfoScreen

class KioskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PUBG 스냅샷")
        self.screen_size = (1920, 1080)
        self.setFixedSize(*self.screen_size)
        self.showFullScreen()

        if getattr(sys, 'frozen', False):
            # 실행파일로 실행한 경우,해당 파일을 보관한 디렉토리의 full path를 취득
            program_directory = os.path.dirname(os.path.abspath(sys.executable))
            program_directory = os.path.join(program_directory, "_internal")
        else:
            # 파이썬 파일로 실행한 경우,해당 파일을 보관한 디렉토리의 full path를 취득
            program_directory = os.path.dirname(os.path.abspath(__file__))
        os.chdir(program_directory)

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
            
    def closeEvent(self, event):
        """창이 닫힐 때 카메라 자원 해제 및 임시 파일 정리"""
        try:
            # 카메라 자원 해제
            if hasattr(self, 'photo_screen') and hasattr(self.photo_screen, 'webcam'):
                if hasattr(self.photo_screen.webcam, 'camera'):
                    release_camera(self.photo_screen.webcam.camera)
            
            # 임시 이미지 파일들 삭제
            temp_files = [
                "resources/captured_image.jpg",
                "resources/cropped_preview.jpg",
                "resources/preview_area.jpg"
            ]
            
            for file_path in temp_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"프로그램 종료 시 임시 파일 삭제: {file_path}")
                    
        except Exception as e:
            print(f"프로그램 종료 시 정리 중 오류 발생: {e}")
            
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KioskApp()
    window.show()
    sys.exit(app.exec())
