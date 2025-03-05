import os
import csv
from datetime import datetime

class CSVValidator:
    """이름/생년월일 데이터를 CSV 파일과 대조하여 검증하는 클래스"""
    
    def __init__(self, csv_path=None):
        if csv_path is None:
            # 구례군 명예 시민증 폴더 경로 설정
            folder_path = "resources/csv"
            
            # 폴더가 없으면 생성
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"폴더 생성 완료: {folder_path}")
            
            # 파일 경로 설정 (발급기록.csv)
            csv_path = os.path.join(folder_path, "record.csv")
            
            print(f"데이터 파일 경로: {csv_path}")
        
        self.csv_path = csv_path
        self._create_if_not_exists()
    
    def _create_if_not_exists(self):
        """CSV 파일이 없으면 새로 생성"""
        if not os.path.exists(self.csv_path):
            # 파일 생성 및 헤더 쓰기 - cp949 인코딩 사용
            with open(self.csv_path, 'w', newline='', encoding='cp949') as f:
                writer = csv.writer(f)
                writer.writerow(['이름', '생년월일', '발급일시'])
            print(f"새 CSV 파일 생성: {self.csv_path}")
    
    def is_duplicate(self, name, birth_date):
        """이름과 생년월일이 이미 등록되어 있는지 확인"""
        try:
            records = self._read_records()
            
            # 이름과 생년월일로 필터링
            matches = [r for r in records if r[0] == name and r[1] == birth_date]
            
            if matches:
                # 중복된 데이터가 있는 경우, 마지막 발급 일시 찾기
                last_issued = matches[-1][2]
                return True, f"이미 등록된 사용자입니다. 마지막 발급일시: {last_issued}"
            
            return False, "신규 사용자입니다."
            
        except Exception as e:
            print(f"중복 확인 중 오류 발생: {e}")
            return False, "데이터 검증 중 오류가 발생했습니다."
    
    def add_record(self, name, birth_date):
        """새 발급 기록을 CSV에 추가"""
        try:
            # 현재 기록 읽기
            records = self._read_records()
            
            # 발급 시간
            issue_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 새 레코드 추가
            records.append([name, birth_date, issue_time])
            
            # CSV에 저장 - cp949 인코딩 사용
            with open(self.csv_path, 'w', newline='', encoding='cp949') as f:
                writer = csv.writer(f)
                writer.writerow(['이름', '생년월일', '발급일시'])  # 헤더
                writer.writerows(records)  # 모든 레코드
            
            print(f"✅ 새 발급 기록 추가 완료: {name}, {birth_date}, {issue_time}")
            return True
            
        except Exception as e:
            import traceback
            print(f"발급 기록 추가 중 오류 발생: {e}")
            print(traceback.format_exc())
            return False
    
    def _read_records(self):
        """CSV 파일에서 모든 레코드 읽기"""
        if not os.path.exists(self.csv_path):
            self._create_if_not_exists()
            return []
        
        # 파일이 이미 존재하는 경우 인코딩 처리
        try:
            # 먼저 cp949로 시도
            records = self._try_read_with_encoding('cp949')
            return records
        except UnicodeDecodeError:
            try:
                # cp949로 안 되면 euc-kr 시도
                records = self._try_read_with_encoding('euc-kr')
                return records
            except UnicodeDecodeError:
                try:
                    # euc-kr로도 안 되면 utf-8 시도
                    records = self._try_read_with_encoding('utf-8')
                    return records
                except UnicodeDecodeError:
                    try:
                        # 마지막으로 utf-8-sig 시도
                        records = self._try_read_with_encoding('utf-8-sig')
                        return records
                    except UnicodeDecodeError:
                        # 모든 인코딩 실패 시 빈 리스트 반환
                        print("파일 인코딩을 결정할 수 없습니다. 파일이 손상되었을 수 있습니다.")
                        return []
    
    def _try_read_with_encoding(self, encoding):
        """지정된 인코딩으로 CSV 파일 읽기 시도"""
        records = []
        with open(self.csv_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            next(reader, None)  # 헤더 건너뛰기
            for row in reader:
                if len(row) >= 3:  # 최소 3개 컬럼 확인
                    records.append(row)
        return records