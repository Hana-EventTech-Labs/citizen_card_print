from excel_utils.csv_validator import CSVValidator
from utils.dialog_manager import ValidationDialog, MessageDialog

class ExcelManager:
    """엑셀 데이터 관리 및 발급 로직을 처리하는 클래스"""
    
    def __init__(self, parent_widget=None):
        """
        엑셀 매니저 초기화
        
        Args:
            parent_widget: 다이얼로그의 부모 위젯
        """
        self.parent = parent_widget
        self.validator = CSVValidator()
        
    def validate_user(self, name, birth_date):
        """
        사용자 정보를 검증하고 결과 다이얼로그 표시
        
        Args:
            name (str): 사용자 이름
            birth_date (str): 생년월일(YYYYMMDD 형식)
            
        Returns:
            bool: 발급 진행 가능 여부
        """
        if not name or not birth_date:
            # 이름 또는 생년월일이 누락된 경우
            dialog = MessageDialog(
                parent=self.parent,
                title="입력 오류",
                message="이름과 생년월일을 모두 입력해주세요."
            )
            dialog.exec()
            return False
            
        # 이름, 생년월일 검증
        is_duplicate, message = self.validator.is_duplicate(name, birth_date)
        
        if is_duplicate:
            # 중복된 경우 확인 다이얼로그
            dialog = ValidationDialog(
                parent=self.parent,
                title="중복 발급 확인",
                message=message,
                is_warning=True
            )
            
            # 사용자 선택에 따라 진행 여부 결정
            if dialog.exec() == ValidationDialog.Accepted:
                return True  # 확인 버튼 선택
            else:
                return False  # 초기 화면으로 돌아가기 버튼 선택
        else:
            # 중복이 아닌 경우
            return True
    
    def register_card(self, name, birth_date):
        """
        카드 발급 정보를 엑셀에 등록
        
        Args:
            name (str): 사용자 이름
            birth_date (str): 생년월일(YYYYMMDD 형식)
            
        Returns:
            bool: 등록 성공 여부
        """
        # 엑셀에 기록 추가
        success = self.validator.add_record(name, birth_date)
        return success