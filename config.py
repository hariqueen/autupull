from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys

class ElementConfig:
    """요소 관련 설정"""
    
    # 공통 셀렉터
    LOADING_MASK = ".loading-mask, .loading-overlay"
    
    # 공통 JavaScript
    JS = {
        "click": "arguments[0].click();",
        "remove_mask": "document.querySelector('.ax-mask-body').remove();",
        "remove_brand": "document.querySelector('div[data-ax5autocomplete-remove=\"true\"]').click();"
    }
    
    # 공통 대기 시간 (초)
    WAIT = {
        "default": 10,
        "short": 3,
        "long": 30,
        "key_interval": 0.5,  
        "download_check": 1,  
        "brand_select": 0.5   
    }
    
    # 공통 셀렉터
    COMMON = {
        "loading_mask": ".ax-mask-body",
        "alert_ok_button": "button[data-dialog-btn='ok']",
        "download_button": "button.btn-default",
        "search_button": "button.btn-primary",
        "excel_download_button": "button[data-grid-control='excel-download']",
        "alert_dialog": "#ax5-dialog-29",
        "alert_message": "#ax5-dialog-29 .ax-dialog-msg",
        "alert_ok": "#ax5-dialog-29 button[data-dialog-btn='ok']",
        "brand_remove": "div[data-ax5autocomplete-remove='true']",
        "no_data_text": "검색된 데이터가 없습니다"
    }

    # 파일 관련 설정
    FILE = {
        "download_dir": "/Users/haribo/Downloads",  # 다운로드 폴더
        "excel_extensions": [".xlsx", ".xls"],      # 엑셀 파일 확장자
        "temp_extension": ".crdownload"             # 임시 파일 확장자
    }

    # iframe 관련 설정
    IFRAME = {
        "default_index": 1,  # 기본 iframe 인덱스 (0-based)
        "brand_popup_index": 1,  # 브랜드 팝업용 iframe 인덱스
        "data_index": 1  # 데이터 처리용 iframe 인덱스
    }

    # 브랜드 선택 관련 설정
    BRAND = {
        "key_sequence": {
            "select": [Keys.ARROW_DOWN, Keys.ENTER],  # 브랜드 선택용 키 시퀀스
            "remove": [Keys.ESCAPE]  # 브랜드 제거용 키 시퀀스
        },
        "messages": {
            "start": "🔍 {} 브랜드 처리 시작",
            "select": "✅ {} 브랜드 선택 완료",
            "remove": "✅ X버튼 클릭 완료",
            "complete": "🎉 {} 브랜드 처리 완료",
            "no_data": "마지막 브랜드 {}에서 데이터 없음 - 종료",
            "error": "❌ {} 브랜드 처리 중 예외 발생: {}"
        }
    }

    # 상태 메시지
    MESSAGES = {
        "iframe": {
            "check": "🔍 iframe 확인 중...",
            "success": "✅ iframe {}로 전환 완료",
            "error": "❌ iframe이 부족함 (현재 {}개)"
        },
        "download": {
            "start": "✅ 다운로드 시작",
            "waiting": "⏳ 다운로드 대기 중... ({}/{}초)",
            "complete": "✅ 다운로드 완료: {}",
            "timeout": "❌ 다운로드 대기 시간 초과"
        },
        "alert": {
            "no_data": "검색된 데이터가 없습니다. 다음 단계로 진행.",
            "close_success": "✅ 데이터 없음 알림창 처리 완료 (방법: {})",
            "close_error": "❌ 데이터 없음 알림창 처리 실패"
        }
    }

class SiteConfig:
    """사이트별 설정"""
    
    # 공통 새 어드민 시스템 설정
    NEW_ADMIN_CONFIG = {
        "menu": {
            "main_menu": "#sidebar > div > div.top.tab-wrap > ul > li:nth-child(2) > a",
            "sms_service": "#menuNav > li:nth-child(5) > a",
            "sms_history": "#menu_5423 > li:nth-child(2) > a"
        },
        "sms": {
            "iframe_index": 0,
            "date_selectors": ["#pickerViewdt", "#schForm > table > tbody > tr:nth-child(1) > td:nth-child(2) > div", "#startDt"],
            "brand_selector": "span.select2-selection",
            "search_button": "body > div.content-wrap > div.cont-top > div.title-wrap > div > button:nth-child(1)",
            "download_button": "body > div.content-wrap > div.cont-top > div.title-wrap > div > button:nth-child(2)",
            "no_data_alert": ".alert",
            "no_data_text": "데이터가 없습니다"
        }
    }
    
    # 디싸이더스/애드프로젝트 설정
    DECIDERS = {
        "login": {
            "url": "https://admin.deciders.co.kr/",
            "id_selector": "#username",
            "pw_selector": "#password",
            "submit_selector": "button[type='submit']",
            "success_check": ".user-info"
        },
        "sms": {
            "is_new_admin": True,  # 새 어드민 여부
            "menu": {
                "main_menu": "#sidebar > div > div.top.tab-wrap > ul > li:nth-child(2) > a",
                "sms_service": "#menuNav > li:nth-child(5) > a",
                "sms_history": "#menu_5423 > li:nth-child(2) > a"
            },
            "iframe_index": 1,
            "date_format": "%Y%m%d",
            "start_date_selector": "#startDate",
            "end_date_selector": "#endDate",
            "search_text": "조회",
            "no_data_alert": "#ax5-dialog-29 .ax-dialog-msg",
            "no_data_text": "검색된 데이터가 없습니다",
            "brand": {
                "enabled": True,
                "dropdown_selector": "div[data-ax5autocomplete]",
                "option_selector": ".ax-autocomplete-option-item",
                "option_index_attr": "data-option-index",
                "list": ["엑스퍼", "스마트웰컴", "바이오숨", "스마트웰", "유리제로"]
            }
        }
    }
    
    # 앤하우스 설정
    ANHOUSE = {
        "login": {
            "url": "https://anhouse-admin.com/",
            "id_selector": "#id",
            "pw_selector": "#password",
            "submit_selector": "button.login-btn",
            "success_check": ".user-profile"
        },
        "sms": {
            "is_new_admin": False,  # 새 어드민 여부
            "menu_selector": "a[href='/sms/list']",
            "iframe_index": 0,
            "date_format": "%Y-%m-%d",
            "start_date_selector": "#startDt",
            "end_date_selector": "#endDt",
            "search_text": "검색",
            "no_data_alert": ".alert",
            "no_data_text": "데이터가 없습니다"
        }
    }

class DateConfig:
    """날짜 설정"""
    
    _start_date = None
    _end_date = None
    
    @classmethod
    def set_dates(cls, start_date, end_date):
        """날짜 설정"""
        cls._start_date = start_date
        cls._end_date = end_date
    
    @classmethod
    def get_sms_format(cls):
        """SMS용 날짜 포맷"""
        if not cls._start_date or not cls._end_date:
            raise ValueError("날짜가 설정되지 않았습니다")
        
        from datetime import datetime
        start = datetime.strptime(cls._start_date, "%Y-%m-%d")
        end = datetime.strptime(cls._end_date, "%Y-%m-%d")
        
        return {
            "start_date": start.strftime("%Y%m%d"),
            "end_date": end.strftime("%Y%m%d")
        }
    
    @classmethod
    def get_call_format(cls):
        """CALL용 날짜 포맷"""
        if not cls._start_date or not cls._end_date:
            raise ValueError("날짜가 설정되지 않았습니다")
        
        return {
            "start_date": cls._start_date,
            "end_date": cls._end_date
        }
    
    @classmethod
    def get_new_admin_month(cls):
        """새 어드민용 월 추출"""
        if not cls._start_date:
            raise ValueError("날짜가 설정되지 않았습니다")
        
        # "2025-05-01"에서 "2025-05" 추출
        month_key = cls._start_date[:7]  # YYYY-MM
        month_num = cls._start_date[5:7]  # MM (05)
        
        return {
            "month_key": month_key,     # "2025-05" (li[data-range-key="2025-05"] 클릭용)
            "month_num": month_num,     # "05" (5월)
            "month_name": f"{int(month_num)}월"  # "5월" (로그용)
        }

class AccountConfig:
    """계정별 설정 관리"""
    
    # SMS 계정 설정
    SMS_CONFIG = {
        "앤하우스": {
            "id_selector": "#userCd",
            "pw_selector": "#userPs",
            "login_btn": "#formView01 > div.panel-body > div.panel-right > table > tbody > tr:nth-child(2) > td:nth-child(3) > button",
            "need_softphone_off": False,
            "checkbox_selector": "#agreeCheck",
            "sms_service_selector": "#aside-menu-0_31_a",
            "sms_history_selector": "#aside-menu-0_33_span",
            "start_date_selector": "input[name='schSdate']",
            "end_date_selector": "input[name='schEdate']",
            "search_btn_text": "조회",
            "download_btn_selector": "#titleBtn > button:nth-child(1)"
        },
        "디싸이더스/애드프로젝트": {
            "id_selector": "#userCd",
            "pw_selector": "#userPs",
            "login_btn": "#formView01 > div.panel-body > div.panel-right > table > tbody > tr:nth-child(2) > td:nth-child(3) > button",
            "need_softphone_off": False,
            "checkbox_selector": "#agreeCheck",
            "sms_service_selector": "#aside-menu-0_16_span",
            "sms_history_selector": "#aside-menu-0_18_span",
            "start_date_selector": "input[name='schSdate']",
            "end_date_selector": "input[name='schEdate']",
            "search_btn_text": "조회",
            "download_btn_selector": "#titleBtn > button:nth-child(1)",
            "has_brands": True,
            "brands": ["엑스퍼", "스마트웰컴", "바이오숨", "스마트웰", "유리제로"],
            "brand_dropdown_selector": "input[data-ax5autocomplete-display='input']",
            "brand_remove_btn_selector": "#searchView > div > div:nth-child(2) > div:nth-child(2) > div > div > div > div > a > div > div:nth-child(1)",
            "sms_iframe_index": 1  # iframe 2 (0-based index)
        },
        "매스프레소(콴다)": {
            "id_selector": "#userCd",
            "pw_selector": "#userPs",
            "login_btn": "#formView01 > div.panel-body > div.panel-right > table > tbody > tr:nth-child(2) > td:nth-child(3) > button",
            "need_softphone_off": False,
            "checkbox_selector": "#agreeCheck",
            "sms_service_selector": "#aside-menu-0_19_span",
            "sms_history_selector": "#aside-menu-0_21_span",
            "start_date_selector": "input[name='schSdate']",
            "end_date_selector": "input[name='schEdate']",
            "search_btn_text": "조회",
            "download_btn_selector": "#titleBtn > button:nth-child(1)",
            "has_brands": True,
            "brands": ["콴다"],  
            "brand_dropdown_selector": "input[data-ax5autocomplete-display='input']",
            "sms_iframe_index": 1  # iframe 2 (0-based index)
        }
    }
    
    # CALL 계정 설정
    CALL_CONFIG = {
        "앤하우스": {
            "id_selector": "#textfield-3551-inputEl", 
            "pw_selector": "#textfield-3552-inputEl",
            "checkbox_selector": "#chkAgree-displayEl",
            "login_btn": "#login-btn-btnInnerEl",
            "company_text": "앤하우스",
            "outbound_selector": "#uxtagfield-2171-inputEl",
            "call_status_selector": "#uxtagfield-2172-inputEl",
            "start_date_selector": "#datefield-2168-inputEl",
            "end_date_selector": "#datefield-2170-inputEl",
            "search_btn_selector": "#button-2153",
            "download_btn_selector": "#button-2155",
            "no_data_alert_selector": "#ax5-dialog-29 .ax-dialog-msg",
            "no_data_text": "검색된 데이터가 없습니다"
        }
    }
    # 세부 계정 설정
    ACCOUNTS = {
        "디싸이더스/애드프로젝트": {
            "type": "sms",
            "url": "https://admin.deciders.co.kr/",
            "id": "YOUR_ID",
            "pw": "YOUR_PASSWORD",
            "config": {
                "need_menu_click": True,
                "has_brands": True,
                "brands": ["엑스퍼", "스마트웰컴", "바이오숨", "스마트웰", "유리제로"],
                "brand_dropdown_selector": "div[data-ax5autocomplete]",
                "start_date_selector": "#startDate",
                "end_date_selector": "#endDate",
                "download_btn_selector": "button.btn-default"
            }
        }
    }