import os
import pandas as pd
from datetime import datetime

class ExcelValidator:
    """이름/생년월일 데이터를 엑셀 파일과 대조하여 검증하는 클래스"""
    
    def __init__(self, excel_path=None):
        """
        엑셀 검증기 초기화
        
        Args:
            excel_path (str, optional): 엑셀 파일 경로. 없으면 기본 경로 사용.
        """
        if excel_path is None:
            # 스크립트 파일의 디렉토리 경로
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # 프로젝트 루트 디렉토리
            root_dir = os.path.dirname(script_dir)
            # 기본 엑셀 파일 경로
            excel_path = os.path.join(root_dir, "data", "user_registry.xlsx")
            
            # data 디렉토리가 없으면 생성
            data_dir = os.path.join(root_dir, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"데이터 디렉토리 생성: {data_dir}")
        
        self.excel_path = excel_path
        self.df = self._load_or_create_excel()
    
    def _load_or_create_excel(self):
        """
        엑셀 파일을 로드하거나 없으면 새로 생성
        
        Returns:
            pandas.DataFrame: 로드된 데이터프레임
        """
        try:
            if os.path.exists(self.excel_path):
                df = pd.read_excel(self.excel_path)
                # 필수 열이 있는지 확인
                required_cols = ['이름', '생년월일', '발급일시']
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = ''
                return df
            else:
                # 파일이 없으면 새로 생성
                df = pd.DataFrame(columns=['이름', '생년월일', '발급일시'])
                df.to_excel(self.excel_path, index=False)
                print(f"새 엑셀 파일 생성: {self.excel_path}")
                return df
        except Exception as e:
            print(f"엑셀 파일 로드 중 오류 발생: {e}")
            # 오류 발생 시 빈 데이터프레임 반환
            return pd.DataFrame(columns=['이름', '생년월일', '발급일시'])
    
    def is_duplicate(self, name, birth_date):
        """
        이름과 생년월일이 이미 등록되어 있는지 확인
        
        Args:
            name (str): 검증할 이름
            birth_date (str): 검증할 생년월일(YYYYMMDD 형식)
            
        Returns:
            tuple: (중복 여부, 메시지)
        """
        try:
            # 데이터프레임 다시 로드 (변경사항 반영)
            self.df = self._load_or_create_excel()
            
            # 이름과 생년월일로 필터링
            filtered = self.df[(self.df['이름'] == name) & (self.df['생년월일'] == birth_date)]
            
            if not filtered.empty:
                # 중복된 데이터가 있는 경우
                last_issued = filtered['발급일시'].iloc[-1]
                return True, f"이미 등록된 사용자입니다. 마지막 발급일시: {last_issued}"
            
            return False, "신규 사용자입니다."
            
        except Exception as e:
            print(f"중복 확인 중 오류 발생: {e}")
            return False, "데이터 검증 중 오류가 발생했습니다."
    
    def add_record(self, name, birth_date):
        """
        새 발급 기록을 엑셀에 추가
        
        Args:
            name (str): 사용자 이름
            birth_date (str): 생년월일(YYYYMMDD 형식)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 데이터프레임 다시 로드
            self.df = self._load_or_create_excel()
            
            # 발급 시간
            issue_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 새 레코드 생성
            new_record = {
                '이름': name,
                '생년월일': birth_date,
                '발급일시': issue_time
            }
            
            # 데이터프레임에 추가
            self.df = pd.concat([self.df, pd.DataFrame([new_record])], ignore_index=True)
            
            # 엑셀에 저장
            self.df.to_excel(self.excel_path, index=False)
            
            print(f"✅ 새 발급 기록 추가 완료: {name}, {birth_date}, {issue_time}")
            return True
            
        except Exception as e:
            print(f"발급 기록 추가 중 오류 발생: {e}")
            return False