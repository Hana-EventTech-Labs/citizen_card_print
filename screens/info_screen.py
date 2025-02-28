from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QSlider, QLineEdit
from PySide6.QtCore import QCoreApplication, Qt, QPoint
import cv2
import numpy as np
import os
from printer_utils.printer_thread import PrinterThread

class InfoScreen(QWidget):
    def __init__(self, stack, screen_size):
        super().__init__()
        self.stack = stack
        self.screen_size = screen_size
        self.drag_start_pos = None
        self.image_position = {"x": 0, "y": 0}
        self.rotation_angle = 0
        self.captured_image_path = "resources/captured_image.jpg"  # 기본 경로 설정
        self.setupUI()

    def setupUI(self):
        self.setupBackground()
        self.add_close_button()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        main_container = QFrame(self)
        main_container.setStyleSheet("background: transparent;")
        main_container.setFixedSize(900, 600)  # 전체 컨테이너 크기
        main_container.move(
            (1920 - 900) // 2,
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
        
        # Preview Area
        # 카드 크기 58 x 90, 사진 크기 35 x 40
        # 사진 비율 = 가로 / 세로 = 35 / 40 = 0.875
        # 카드 비율 = 가로 / 세로 = 58 / 90 = 0.644
        photo_ratio = 40 / 35  # 기존 비율 (세로 / 가로)
        card_ratio = 90 / 58   # 카드 비율 (세로 / 가로)
        preview_width = 400
        # 사진 비율에 맞게 프리뷰 높이 설정
        preview_height = int(preview_width * (40 / 35))  # 사진 비율 적용
        
        # 카드 프리뷰 크기 계산 (참고용)
        card_preview_width = 400
        card_preview_height = int(card_preview_width * (90 / 58))  # 카드 비율 적용
        print(f"사진 프리뷰 크기: {preview_width} x {preview_height}")
        print(f"카드 프리뷰 크기: {card_preview_width} x {card_preview_height}")
        
        preview_container = QFrame()
        preview_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #888;
                border-radius: 5px;
            }
        """)
        preview_container.setFixedSize(preview_width, preview_height)
        
        self.preview_frame = QFrame(preview_container)
        self.preview_frame.setFixedSize(preview_width, preview_height)
        
        self.preview_label = QLabel(self.preview_frame)
        self.preview_label.setFixedSize(preview_width, preview_height)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 마우스 이벤트 추적을 위한 설정
        self.preview_frame.mousePressEvent = self.start_drag
        self.preview_frame.mouseMoveEvent = self.drag
        self.preview_frame.mouseReleaseEvent = self.stop_drag

        # Controls - preview frame 아래에 배치
        controls_container = QFrame()
        controls_container.setFixedWidth(preview_width)  # preview와 같은 너비
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # 줌 슬라이더 컨테이너
        zoom_container = QFrame()
        zoom_layout = QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(10)
        
        zoom_label = QLabel("확대/축소")
        zoom_label.setStyleSheet("color: #333; font-size: 13px;")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(20, 100)
        self.zoom_slider.setValue(40)
        self.zoom_slider.setFixedWidth(200)  # 슬라이더 너비 고정
        self.zoom_slider.valueChanged.connect(self.update_preview)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #ddd;
            }
            QSlider::handle:horizontal {
                background: #5B9279;
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
        """)
        
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)
        
        rotate_btn = QPushButton("회전")
        rotate_btn.clicked.connect(self.rotate_image)
        rotate_btn.setFixedWidth(80)  # 버튼 너비 고정
        rotate_btn.setStyleSheet("""
            QPushButton {
                background-color: #5B9279;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4A7A64;
            }
        """)
        
        controls_layout.addWidget(zoom_container)
        controls_layout.addWidget(rotate_btn)
        
        # 왼쪽 컨테이너에 위젯 추가
        left_layout.addWidget(preview_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addWidget(controls_container, alignment=Qt.AlignmentFlag.AlignHCenter)
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

        # 생년월일 입력 
        birth_label = QLabel("생년월일")
        birth_label.setStyleSheet("font-weight: bold; font-size: 40px;")
        birth_hint = QLabel("예시) 19901231")
        birth_hint.setStyleSheet("color: gray; font-size: 20px;")
        self.birth_input = QLineEdit()
        self.birth_input.setFixedHeight(80)
        self.birth_input.setStyleSheet(input_style)
        # self.birth_input.textChanged.connect(self.validate_birth_input)
        
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
        retake_btn.clicked.connect(lambda: self.retake_photo())
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
        # 화면이 표시될 때 이미지 업데이트
        self.update_preview()
        
    def start_drag(self, event):
        if hasattr(self.stack.parent(), 'photo_screen') and hasattr(self.stack.parent().photo_screen, 'webcam'):
            if hasattr(self.stack.parent().photo_screen.webcam, 'camera'):
                self.drag_start_pos = event.pos()
    
    def drag(self, event):
        if self.drag_start_pos and hasattr(self.stack.parent(), 'photo_screen') and hasattr(self.stack.parent().photo_screen, 'webcam'):
            if hasattr(self.stack.parent().photo_screen.webcam, 'camera'):
                delta = event.pos() - self.drag_start_pos
                
                # 현재 줌 레벨에서의 이미지 크기 계산
                zoom = self.zoom_slider.value() / 10.0
                
                # 이미지 파일 경로
                image_path = self.captured_image_path if hasattr(self, 'captured_image_path') else "resources/captured_image.jpg"
                current_image = cv2.imread(image_path)
                
                if current_image is not None:
                    img_height, img_width = current_image.shape[:2]
                    
                    # 이미지 크기와 프리뷰 프레임의 비율 계산
                    frame_ratio = self.preview_frame.width() / self.preview_frame.height()
                    image_ratio = img_width / img_height
                    
                    if image_ratio > frame_ratio:
                        # 이미지가 더 넓은 경우
                        display_width = self.preview_frame.width() * zoom
                        display_height = display_width / image_ratio
                    else:
                        # 이미지가 더 높은 경우
                        display_height = self.preview_frame.height() * zoom
                        display_width = display_height * image_ratio
                    
                    # 드래그 범위 제한
                    if display_width > self.preview_frame.width() or display_height > self.preview_frame.height():
                        self.image_position["x"] += delta.x()
                        self.image_position["y"] += delta.y()
                        
                        # 최대 이동 범위 계산
                        max_x = (display_width - self.preview_frame.width()) / 2
                        max_y = (display_height - self.preview_frame.height()) / 2
                        
                        # 이동 범위 제한
                        self.image_position["x"] = max(-max_x, min(max_x, self.image_position["x"]))
                        self.image_position["y"] = max(-max_y, min(max_y, self.image_position["y"]))
                        
                        self.update_preview()
                
                self.drag_start_pos = event.pos()
    
    def stop_drag(self, event):
        self.drag_start_pos = None
    
    def rotate_image(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.image_position = {"x": 0, "y": 0}
        self.update_preview()
    
    def update_preview(self):
        # 이미지 파일 경로 사용
        image_path = self.captured_image_path if hasattr(self, 'captured_image_path') else "resources/captured_image.jpg"
        image = cv2.imread(image_path)
        
        if image is not None:
            # OpenCV BGR -> RGB 변환
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img_height, img_width = image_rgb.shape[:2]
            
            # 회전 적용
            if self.rotation_angle != 0:
                matrix = cv2.getRotationMatrix2D((img_width/2, img_height/2), self.rotation_angle, 1)
                image_rgb = cv2.warpAffine(image_rgb, matrix, (img_width, img_height))
            
            # 프리뷰 프레임과 이미지 비율 계산
            frame_ratio = self.preview_frame.width() / self.preview_frame.height()
            image_ratio = img_width / img_height
            
            # 줌 레벨 계산
            zoom = self.zoom_slider.value() / 10.0
            
            # 이미지 크기 계산
            if image_ratio > frame_ratio:
                # 이미지가 더 넓은 경우
                display_width = self.preview_frame.width() * zoom
                display_height = display_width / image_ratio
            else:
                # 이미지가 더 높은 경우
                display_height = self.preview_frame.height() * zoom
                display_width = display_height * image_ratio
            
            # 이미지 리사이즈
            image_rgb = cv2.resize(image_rgb, (int(display_width), int(display_height)))
            
            # 캔버스 생성 (프리뷰 프레임 크기)
            canvas = np.full((self.preview_frame.height(), self.preview_frame.width(), 3), 255, dtype=np.uint8)
            
            # 이미지 중앙 정렬 및 위치 조정
            x_offset = int((self.preview_frame.width() - display_width) / 2 + self.image_position["x"])
            y_offset = int((self.preview_frame.height() - display_height) / 2 + self.image_position["y"])
            
            # 이미지를 캔버스에 붙이기 (범위 체크)
            y1 = max(0, y_offset)
            y2 = min(self.preview_frame.height(), y_offset + image_rgb.shape[0])
            x1 = max(0, x_offset)
            x2 = min(self.preview_frame.width(), x_offset + image_rgb.shape[1])
            
            if y2 > y1 and x2 > x1:
                img_y1 = max(0, -y_offset)
                img_y2 = img_y1 + (y2 - y1)
                img_x1 = max(0, -x_offset)
                img_x2 = img_x1 + (x2 - x1)
                
                canvas[y1:y2, x1:x2] = image_rgb[img_y1:img_y2, img_x1:img_x2]
            
            # QImage로 변환 및 표시
            height, width = canvas.shape[:2]
            bytes_per_line = 3 * width
            qt_image = QImage(canvas.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            self.preview_label.setPixmap(QPixmap.fromImage(qt_image))

    def reset_form(self):
        """폼 초기화"""
        self.name_input.clear()
        self.birth_input.clear()
        self.rotation_angle = 0
        self.zoom_slider.setValue(40)
        self.image_position = {"x": 0, "y": 0}
        self.update_preview()
        
    def retake_photo(self):
        """재촬영 버튼 클릭 시 호출되는 메서드"""
        # 이미지 위치와 회전 각도 초기화
        self.rotation_angle = 0
        self.zoom_slider.setValue(40)
        self.image_position = {"x": 0, "y": 0}
        
        # 웹캠 카운트다운 초기화
        if hasattr(self.stack.parent(), 'photo_screen') and hasattr(self.stack.parent().photo_screen, 'webcam'):
            self.stack.parent().photo_screen.webcam.reset_countdown()
            
        # PhotoScreen으로 돌아가기
        self.stack.setCurrentIndex(1)

    def get_preview_coordinates(self):
        """현재 프리뷰에 표시된 이미지의 원본 이미지 내 좌표와 크기를 계산합니다."""
        # 이미지 파일 경로
        image_path = self.captured_image_path if hasattr(self, 'captured_image_path') else "resources/captured_image.jpg"
        image = cv2.imread(image_path)
        
        if image is None:
            return None
            
        # 원본 이미지 크기
        img_height, img_width = image.shape[:2]
        
        # 줌 레벨 계산
        zoom = self.zoom_slider.value() / 10.0
        
        # 프리뷰 프레임과 이미지 비율 계산
        frame_ratio = self.preview_frame.width() / self.preview_frame.height()
        image_ratio = img_width / img_height
        
        # 이미지 크기 계산
        if image_ratio > frame_ratio:
            # 이미지가 더 넓은 경우
            display_width = self.preview_frame.width() * zoom
            display_height = display_width / image_ratio
        else:
            # 이미지가 더 높은 경우
            display_height = self.preview_frame.height() * zoom
            display_width = display_height * image_ratio
        
        # 이미지 중앙 정렬 및 위치 조정
        x_offset = int((self.preview_frame.width() - display_width) / 2 + self.image_position["x"])
        y_offset = int((self.preview_frame.height() - display_height) / 2 + self.image_position["y"])
        
        # 프리뷰 프레임 내에서 보이는 영역 계산
        visible_x1 = max(0, -x_offset)
        visible_y1 = max(0, -y_offset)
        visible_x2 = min(display_width, self.preview_frame.width() - x_offset)
        visible_y2 = min(display_height, self.preview_frame.height() - y_offset)
        
        # 원본 이미지에서의 비율 계산
        scale_x = img_width / display_width
        scale_y = img_height / display_height
        
        # 원본 이미지에서의 좌표 계산
        orig_x1 = int(visible_x1 * scale_x)
        orig_y1 = int(visible_y1 * scale_y)
        orig_x2 = int(visible_x2 * scale_x)
        orig_y2 = int(visible_y2 * scale_y)
        
        # 회전이 적용된 경우 좌표 변환
        if self.rotation_angle != 0:
            # 회전 중심점 (원본 이미지 중심)
            center_x = img_width / 2
            center_y = img_height / 2
            
            # 회전 전 좌표를 중심점 기준으로 변환
            points = [
                (orig_x1, orig_y1),  # 좌상단
                (orig_x2, orig_y1),  # 우상단
                (orig_x2, orig_y2),  # 우하단
                (orig_x1, orig_y2)   # 좌하단
            ]
            
            # 회전 행렬 생성 (반시계 방향으로 회전)
            angle_rad = -np.radians(self.rotation_angle)
            cos_val = np.cos(angle_rad)
            sin_val = np.sin(angle_rad)
            
            # 회전된 좌표 계산
            rotated_points = []
            for x, y in points:
                # 중심점 기준으로 좌표 이동
                tx = x - center_x
                ty = y - center_y
                
                # 회전 적용
                rx = tx * cos_val - ty * sin_val
                ry = tx * sin_val + ty * cos_val
                
                # 다시 원래 좌표계로 이동
                rotated_points.append((int(rx + center_x), int(ry + center_y)))
            
            # 회전된 좌표의 경계 계산
            min_x = min(p[0] for p in rotated_points)
            min_y = min(p[1] for p in rotated_points)
            max_x = max(p[0] for p in rotated_points)
            max_y = max(p[1] for p in rotated_points)
            
            # 경계값이 이미지 범위를 벗어나지 않도록 조정
            min_x = max(0, min_x)
            min_y = max(0, min_y)
            max_x = min(img_width, max_x)
            max_y = min(img_height, max_y)
            
            return {
                "x1": min_x,
                "y1": min_y,
                "x2": max_x,
                "y2": max_y,
                "width": max_x - min_x,
                "height": max_y - min_y,
                "rotation_angle": self.rotation_angle,
                "rotated_points": rotated_points
            }
        
        return {
            "x1": orig_x1,
            "y1": orig_y1,
            "x2": orig_x2,
            "y2": orig_y2,
            "width": orig_x2 - orig_x1,
            "height": orig_y2 - orig_y1,
            "rotation_angle": self.rotation_angle
        }
        
    def show_preview_area(self, debug_mode=True):
        """현재 프리뷰 영역을 시각적으로 표시합니다."""
        coords = self.get_preview_coordinates()
        if coords is None:
            print("이미지를 불러올 수 없습니다.")
            return
            
        # 원본 이미지 로드
        image_path = self.captured_image_path if hasattr(self, 'captured_image_path') else "resources/captured_image.jpg"
        image = cv2.imread(image_path)
        
        if image is None:
            print("이미지를 불러올 수 없습니다.")
            return
            
        # 프리뷰 영역 표시
        if self.rotation_angle != 0 and "rotated_points" in coords:
            # 회전된 경우 다각형 그리기
            points = np.array(coords["rotated_points"], np.int32)
            points = points.reshape((-1, 1, 2))
            cv2.polylines(image, [points], True, (0, 255, 0), 2)
        else:
            # 회전되지 않은 경우 사각형 그리기
            cv2.rectangle(image, (coords["x1"], coords["y1"]), (coords["x2"], coords["y2"]), (0, 255, 0), 2)
        
        # 좌표 정보 출력
        print(f"프리뷰 영역 좌표: x1={coords['x1']}, y1={coords['y1']}, x2={coords['x2']}, y2={coords['y2']}")
        print(f"프리뷰 영역 크기: 너비={coords['width']}, 높이={coords['height']}")
        print(f"회전 각도: {coords['rotation_angle']}도")
        
        # 디버깅 모드일 때만 이미지 저장
        if debug_mode:
            preview_area_image_path = "resources/preview_area.jpg"
            cv2.imwrite(preview_area_image_path, image)
            print(f"프리뷰 영역이 표시된 이미지가 저장되었습니다: {preview_area_image_path}")
        
        return coords

    def crop_preview_area(self, output_path=None):
        """현재 프리뷰 영역만 크롭하여 저장합니다."""
        if output_path is None:
            output_path = "resources/cropped_preview.jpg"
            
        coords = self.get_preview_coordinates()
        if coords is None:
            print("이미지를 불러올 수 없습니다.")
            return None
            
        # 원본 이미지 로드
        image_path = self.captured_image_path if hasattr(self, 'captured_image_path') else "resources/captured_image.jpg"
        image = cv2.imread(image_path)
        
        if image is None:
            print("이미지를 불러올 수 없습니다.")
            return None
            
        # 회전이 적용된 경우
        if self.rotation_angle != 0:
            # 원본 이미지 크기
            img_height, img_width = image.shape[:2]
            
            # 회전 중심점 (원본 이미지 중심)
            center = (img_width // 2, img_height // 2)
            
            # 회전 행렬 생성
            rotation_matrix = cv2.getRotationMatrix2D(center, self.rotation_angle, 1)
            
            # 이미지 회전
            rotated_image = cv2.warpAffine(image, rotation_matrix, (img_width, img_height))
            
            # 회전된 이미지에서 프리뷰 영역 크롭
            cropped_image = rotated_image[coords["y1"]:coords["y2"], coords["x1"]:coords["x2"]]
        else:
            # 회전이 없는 경우 직접 크롭
            cropped_image = image[coords["y1"]:coords["y2"], coords["x1"]:coords["x2"]]
        
        # 결과 이미지 저장
        cv2.imwrite(output_path, cropped_image)
        print(f"프리뷰 영역이 크롭되어 저장되었습니다: {output_path}")
        
        # 원본 이미지 삭제
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"원본 이미지가 삭제되었습니다: {image_path}")
        except Exception as e:
            print(f"원본 이미지 삭제 중 오류 발생: {e}")
        
        return {
            "cropped_image": cropped_image,
            "output_path": output_path,
            "coordinates": coords
        }

    def process_and_print(self):
        """발급 버튼 클릭 시 호출되는 메서드"""
        # 이름과 생년월일 유효성 검사
        name = self.name_input.text().strip()
        birth = self.birth_input.text().strip()
        
        if not name:
            print("이름을 입력해주세요.")
            return
            
        if not birth or len(birth) != 8 or not birth.isdigit():
            print("생년월일을 8자리 숫자로 입력해주세요. (예: 19901231)")
            return
            
        # 프리뷰 영역 좌표 계산 (이미지 저장 없이)
        self.show_preview_area(debug_mode=False)
            
        # 프리뷰 영역 크롭
        crop_result = self.crop_preview_area()
        if crop_result is None:
            print("이미지 처리 중 오류가 발생했습니다.")
            return
            
        # 크롭된 이미지 경로
        cropped_image_path = crop_result["output_path"]
        cropped_image_filename = os.path.basename(cropped_image_path)  # 파일명만 추출
        
        # 좌표 정보 출력
        coords = crop_result["coordinates"]
        print(f"프리뷰 영역 좌표: x1={coords['x1']}, y1={coords['y1']}, x2={coords['x2']}, y2={coords['y2']}")
        print(f"프리뷰 영역 크기: 너비={coords['width']}, 높이={coords['height']}")
        print(f"회전 각도: {coords['rotation_angle']}도")
        
        # 디버깅용 이미지 삭제 (이제 필요 없음)
        preview_area_image_path = "resources/preview_area.jpg"
        try:
            if os.path.exists(preview_area_image_path):
                os.remove(preview_area_image_path)
                print(f"디버깅용 이미지가 삭제되었습니다: {preview_area_image_path}")
        except Exception as e:
            print(f"디버깅용 이미지 삭제 중 오류 발생: {e}")
        
        # 여기에 인쇄 로직 추가
        print(f"이름: {name}, 생년월일: {birth}")
        print(f"크롭된 이미지: {cropped_image_filename}")
        print("인쇄 작업을 시작합니다...")
        
        # 실제 카드 크기 (mm): 58 x 90
        # 실제 사진 크기 (mm): 35 x 40
        # 인쇄 시 사진 크기 설정 (픽셀 단위)
        # draw_image 함수의 cx, cy 파라미터는 픽셀 단위이며, 0인 경우 원래 크기 사용
        # 여기서는 실제 사진 크기를 픽셀로 변환하여 설정
        # 일반적인 ID 카드 프린터의 해상도는 300 DPI
        # 35mm x 300 DPI / 25.4mm = 413 픽셀 (가로)
        # 40mm x 300 DPI / 25.4mm = 472 픽셀 (세로)
        
        # 인쇄 기능 구현
        self.printer_thread = PrinterThread(cropped_image_filename)
        self.printer_thread.finished.connect(self.on_printing_finished)
        self.printer_thread.start()
        self.stack.setCurrentIndex(0)

    def on_printing_finished(self):
        """프린트 완료 후 이미지 파일 삭제"""
        cropped_image_path = "resources/cropped_preview.jpg"
        if os.path.exists(cropped_image_path):
            try:
                os.remove(cropped_image_path)
                print(f"크롭된 이미지 파일 삭제 완료: {cropped_image_path}")
            except Exception as e:
                print(f"크롭된 이미지 파일 삭제 실패: {e}")
        
        

