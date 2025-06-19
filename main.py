from database import DatabaseManager
from login_manager import LoginManager
from data_manager import DataManager

class AccountManager:
    """통합 계정 관리 시스템"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.login_manager = LoginManager()
        self.data_manager = DataManager(self.login_manager)
    
    def test_all_logins(self):
        """모든 계정 로그인 테스트만"""
        print("통합 계정 로그인 테스트 시작")
        
        results = []
        
        # SMS 계정 테스트
        sms_accounts = self.db_manager.get_accounts_by_type("sms")
        for account in sms_accounts:
            success, _ = self.login_manager.login_account(account, keep_session=False)
            results.append({
                'company': account['company_name'], 
                'type': 'SMS', 
                'success': success
            })
        
        # CALL 계정 테스트
        call_accounts = self.db_manager.get_accounts_by_type("call")
        for account in call_accounts:
            success, _ = self.login_manager.login_account(account, keep_session=False)
            results.append({
                'company': account['company_name'], 
                'type': 'CALL', 
                'success': success
            })
        
        self._print_results(results)
    
    def call_data_workflow(self, download=False, start_date=None, end_date=None):
        """CALL 계정 전체 워크플로 (로그인 → 설정 → 검색 → 다운로드 → 닫기)"""
        print("CALL 계정 데이터 워크플로 시작")
        
        call_accounts = self.db_manager.get_accounts_by_type("call")
        results = []
        
        # 각 계정을 개별적으로 처리
        for account in call_accounts:
            company_name = account['company_name']
            print(f"\n{company_name} 처리 시작")
            
            # 1단계: 로그인 (세션 유지)
            login_success, _ = self.login_manager.login_account(account, keep_session=True)
            
            if login_success:
                print(f"{company_name} 로그인 성공")
                
                # 2단계: 데이터 수집 설정 + 검색 + 다운로드
                process_success = self.data_manager.setup_call_data_collection(
                    company_name, start_date, end_date, download
                )
                
                results.append({
                    'company': company_name, 
                    'login': True,
                    'process': process_success
                })
                
                # 3단계: 세션 종료
                self.login_manager.close_session(company_name, "call")
                print(f"{company_name} 세션 종료")
                
            else:
                print(f"{company_name} 로그인 실패")
                results.append({
                    'company': company_name, 
                    'login': False,
                    'process': False
                })
        
        # 최종 결과 출력
        self._print_call_results(results, download)
        return results
    
    def sms_data_workflow(self, start_date=None, end_date=None):
        """SMS 계정 전체 워크플로 (로그인 → 설정 → 검색 → 다운로드 → 닫기)"""
        print("SMS 계정 데이터 워크플로 시작")
        
        sms_accounts = self.db_manager.get_accounts_by_type("sms")
        results = []
        
        # 각 계정을 개별적으로 처리
        for account in sms_accounts:
            company_name = account['company_name']
            print(f"\n{company_name} 처리 시작")
            
            # 1단계: 로그인 (세션 유지)
            login_success, _ = self.login_manager.login_account(account, keep_session=True)
            
            if login_success:
                print(f"{company_name} 로그인 성공")
                
                # 2단계: 데이터 수집 설정 + 검색 + 다운로드 (download 파라미터 제거)
                process_success = self.data_manager.download_sms_data(
                    company_name, start_date, end_date  # download=True 제거!
                )
                
                results.append({
                    'company': company_name, 
                    'login': True,
                    'process': process_success
                })
                
                # 3단계: 세션 종료
                self.login_manager.close_session(company_name, "sms")
                print(f"{company_name} 세션 종료")
                
            else:
                print(f"{company_name} 로그인 실패")
                results.append({
                    'company': company_name, 
                    'login': False,
                    'process': False
                })
        
        # 최종 결과 출력
        self._print_sms_results(results)
        return results
    
    def _print_sms_results(self, results):
        """SMS 워크플로 결과 출력"""
        print("\n최종 결과:")
        login_success = sum(1 for r in results if r['login'])
        process_success = sum(1 for r in results if r['process'])
        
        for result in results:
            login_status = "성공" if result['login'] else "실패"
            process_status = "성공" if result['process'] else "실패"
            print(f"{result['company']}: 로그인 {login_status}, 다운로드 {process_status}") 
        
        print(f"로그인: {len(results)}개 중 {login_success}개 성공")
        print(f"다운로드: {len(results)}개 중 {process_success}개 성공")  
    
    def _print_results(self, results):
        """테스트 결과 출력"""
        print("\n최종 결과:")
        success_count = 0
        for result in results:
            status = "성공" if result['success'] else "실패"
            print(f"{result['company']} ({result['type']}): {status}")
            if result['success']:
                success_count += 1
        
        print(f"총 {len(results)}개 중 {success_count}개 성공")
    
    def _print_call_results(self, results, download):
        """CALL 워크플로 결과 출력"""
        print("\n최종 결과:")
        login_success = sum(1 for r in results if r['login'])
        process_success = sum(1 for r in results if r['process'])
        
        for result in results:
            login_status = "성공" if result['login'] else "실패"
            process_status = "성공" if result['process'] else "실패"
            action = "다운로드" if download else "검색"
            print(f"{result['company']}: 로그인 {login_status}, {action} {process_status}")
        
        print(f"로그인: {len(results)}개 중 {login_success}개 성공")
        action = "다운로드" if download else "검색"
        print(f"{action}: {len(results)}개 중 {process_success}개 성공")
    
    def cleanup(self):
        """정리"""
        self.login_manager.close_all_sessions()

def main():
    """메인 함수"""
    manager = AccountManager()
    
    try:
        # 사용 예시 1: 로그인 테스트만
        # manager.test_all_logins()
        
        # 사용 예시 2: CALL 데이터 검색까지 (다운로드 안함)
        # manager.call_data_workflow(download=False, start_date="2025-05-01", end_date="2025-05-31")
        
        # 사용 예시 3: CALL 데이터 검색 + 다운로드
        # manager.call_data_workflow(download=True, start_date="2025-05-01", end_date="2025-05-31")
        
        # 사용 예시 4: SMS 데이터 검색 + 다운로드
        manager.sms_data_workflow(start_date="20250501", end_date="20250531")
        
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main()