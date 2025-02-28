import os

def read_config(file_path=None):
    """config.txt 파일을 읽어서 딕셔너리로 반환"""
    if file_path is None:
        # 스크립트 파일의 디렉토리 경로
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 프로젝트 루트 디렉토리 (상위 디렉토리)
        root_dir = os.path.dirname(script_dir)
        # config.txt 파일 경로
        file_path = os.path.join(root_dir, "config.txt")
    
    config = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 숫자로 변환 시도
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    config[key] = value
        return config
    except Exception as e:
        print(f"설정 파일 읽기 오류: {e}")
        return {}