import os
import tempfile

def get_temp_path(filename):
    """표준 임시 디렉토리에 파일 경로 반환"""
    # 애플리케이션 전용 하위 폴더 생성
    app_temp_dir = os.path.join(tempfile.gettempdir(), "GureyCitizenCard")
    
    # 폴더가 없으면 생성
    if not os.path.exists(app_temp_dir):
        os.makedirs(app_temp_dir)
    
    # 전체 파일 경로 반환
    return os.path.join(app_temp_dir, filename)

def cleanup_temp_files():
    """임시 디렉토리 내 모든 파일 정리"""
    app_temp_dir = os.path.join(tempfile.gettempdir(), "GureyCitizenCard")
    if os.path.exists(app_temp_dir):
        for file in os.listdir(app_temp_dir):
            try:
                file_path = os.path.join(app_temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"임시 파일 삭제: {file_path}")
            except Exception as e:
                print(f"임시 파일 삭제 중 오류: {e}")