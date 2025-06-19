import firebase_admin
from firebase_admin import credentials, firestore

class DatabaseManager:
    """Firebase 데이터베이스 관리"""
    
    def __init__(self):
        self.db = self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Firebase 초기화"""
        if not firebase_admin._apps:
            cred = credentials.Certificate("services-e42af-firebase-adminsdk-fbsvc-1728237b98.json")
            firebase_admin.initialize_app(cred)
        return firestore.client()
    
    def get_accounts_by_type(self, account_type):
        """타입별 계정 조회"""
        from config import AccountConfig
        
        if account_type == "sms":
            companies = list(AccountConfig.SMS_CONFIG.keys())
            config_map = AccountConfig.SMS_CONFIG
        else:  # call
            companies = list(AccountConfig.CALL_CONFIG.keys())
            config_map = AccountConfig.CALL_CONFIG
        
        accounts = []
        for company in companies:
            docs = self.db.collection("accounts").where("company_name", "==", company).where("account_type", "==", account_type).get()
            if docs:
                account = docs[0].to_dict()
                account['config'] = config_map.get(company)
                accounts.append(account)
                print(f"✅ {company} {account_type.upper()} 계정 로드")
        
        return accounts