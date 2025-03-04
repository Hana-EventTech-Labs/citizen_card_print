from PySide6.QtWidgets import QFrame, QLabel, QSlider, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import os

class ImagePreviewManager:
    """이미지 프리뷰, 회전, 확대/축소 등 이미지 처리 관련 기능을 관리하는 클래스"""
    
    def __init__(self, parent_widget, preview_width=400, preview_height=457):
        self.parent = parent_widget
        self.preview_width = preview_width
        self.preview_height = preview_height
        self.drag_start_pos = None
        self.image_position = {"x": 0, "y": 0}
        self.rotation_angle = 0
        self.captured_image_path = "resources/captured_image.jpg"  # 기본 경로 설정
        
        # UI 요소 생성
        self.setup_ui()
    
    def setup_ui(self):
        """프리뷰 관련 UI 요소 설정"""
        # Preview Area
        self.preview_container = QFrame(self.parent)
        self.preview_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #888;
                border-radius: 5px;
            }
        """)
        self.preview_container.setFixedSize(self.preview_width, self.preview_height)
        
        self.preview_frame = QFrame(self.preview_container)
        self.preview_frame.setFixedSize(self.preview_width, self.preview_height)
        
        self.preview_label = QLabel(self.preview_frame)
        self.preview_label.setFixedSize(self.preview_width, self.preview_height)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 마우스 이벤트 추적을 위한 설정
        self.preview_frame.mousePressEvent = self.start_drag
        self.preview_frame.mouseMoveEvent = self.drag
        self.preview_frame.mouseReleaseEvent = self.stop_drag

        # Controls - preview frame 아래에 배치
        self.controls_container = QFrame()
        self.controls_container.setFixedWidth(self.preview_width)  # preview와 같은 너비
        controls_layout = QHBoxLayout(self.controls_container)
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
    
    def set_image_path(self, image_path):
        """이미지 경로 설정"""
        self.captured_image_path = image_path
        self.update_preview()
    
    def start_drag(self, event):
        """이미지 드래그 시작"""
        self.drag_start_pos = event.pos()
    
    def drag(self, event):
        """이미지 드래그 중"""
        if self.drag_start_pos:
            delta = event.pos() - self.drag_start_pos
            
            # 현재 줌 레벨에서의 이미지 크기 계산
            zoom = self.zoom_slider.value() / 10.0
            
            # 이미지 파일 경로
            image_path = self.captured_image_path
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
        """이미지 드래그 종료"""
        self.drag_start_pos = None
    
    def rotate_image(self):
        """이미지 회전"""
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.image_position = {"x": 0, "y": 0}
        self.update_preview()
    
    def update_preview(self):
        """이미지 프리뷰 업데이트"""
        # 이미지 파일 경로 사용
        image_path = self.captured_image_path
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
    
    def reset(self):
        """프리뷰 상태 초기화"""
        self.rotation_angle = 0
        self.zoom_slider.setValue(40)
        self.image_position = {"x": 0, "y": 0}
        self.update_preview()
    
    def get_preview_coordinates(self):
        """현재 프리뷰 영역의 원본 이미지 내 좌표와 크기 계산"""
        # 이미지 파일 경로
        image_path = self.captured_image_path
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
    
    def crop_preview_area(self, output_path=None):
        """현재 프리뷰 영역만 크롭하여 저장"""
        if output_path is None:
            output_path = "resources/cropped_preview.jpg"
            
        coords = self.get_preview_coordinates()
        if coords is None:
            print("이미지를 불러올 수 없습니다.")
            return None
            
        # 원본 이미지 로드
        image_path = self.captured_image_path
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
        
        return {
            "cropped_image": cropped_image,
            "output_path": output_path,
            "coordinates": coords
        }
    
    def show_preview_area(self, debug_mode=False):
        """현재 프리뷰 영역을 시각적으로 표시"""
        coords = self.get_preview_coordinates()
        if coords is None:
            print("이미지를 불러올 수 없습니다.")
            return
            
        # 원본 이미지 로드
        image_path = self.captured_image_path
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