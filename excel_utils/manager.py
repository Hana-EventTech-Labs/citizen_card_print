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
            int: 0 - 발급 진행 (신규 사용자), 1 - 발급 중단 (중복 사용자), 2 - 초기화면으로 돌아가기
        """
        if not name or not birth_date:
            # 이름 또는 생년월일이 누락된 경우
            dialog = MessageDialog(
                parent=self.parent,
                title="입력 오류",
                message="이름과 생년월일을 모두 입력해주세요."
            )
            dialog.exec()
            return 1  # 발급 중단
            
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
            
            # 사용자 선택에 따라 반환값 결정
            result = dialog.exec()
            if result == ValidationDialog.Accepted:
                return 1  # 확인 버튼 선택 - 발급 중단
            else:
                return 2  # 초기 화면으로 돌아가기 버튼 선택
        else:
            # 중복이 아닌 경우
            return 0  # 발급 진행
    
    def register_card(self, name, birth_date):
        """
        카드 발급 정보를 엑셀에 등록
        
        Args:
            name (str): 사용자 이름
            birth_date (str): 생년월일(YYYYMMDD 형식)
            
        Returns:
            tuple: (성공 여부, 오류 메시지)
        """
        # 엑셀에 기록 추가
        success, error_message = self.validator.add_record(name, birth_date)
        
        # 저장 실패 시 오류 메시지 표시
        if not success and error_message:
            dialog = MessageDialog(
                parent=self.parent,
                title="데이터 저장 오류",
                message=error_message
            )
            dialog.exec()
            
        return success