class AccountConfig:
    """계정별 설정 관리"""
    
    # SMS 계정 설정
    SMS_CONFIG = {
        "SK일렉링크": {
            "id_selector": "#userCd",
            "pw_selector": "#userPs", 
            "login_btn": "#formView01 > div.panel-body > div.panel-right > table > tbody > tr:nth-child(2) > td:nth-child(3) > button",
            "need_softphone_off": False,
            "checkbox_selector": "#agreeCheck",
            "sms_service_selector": "#aside-menu-0_25_span",
            "sms_history_selector": "#aside-menu-0_27_span",
            "start_date_selector": "input[name='schSdate']",
            "end_date_selector": "input[name='schEdate']",
            "search_btn_text": "조회",
            "download_btn_selector": "#titleBtn > button:nth-child(1)"
        },
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
        },
        "W컨셉": {
            "id_selector": "#userCd",
            "pw_selector": "#userPs",
            "login_btn": "#formView01 > div.panel-body > div.panel-right > table > tbody > tr:nth-child(2) > td:nth-child(3) > button",
            "need_softphone_off": False,
            "checkbox_selector": "#agreeCheck"
            # SMS 기능 없음
        },
        "볼드워크": {
            "id_selector": "#projUserCd",
            "pw_selector": "#userPs",
            "login_btn": "#loginBtn",
            "need_softphone_off": True,
            "checkbox_selector": "#agreeCheck",
            "need_menu_click": True,  # 새 어드민 여부
            "menu_selector": "#sidebar > div > div.top.tab-wrap > ul > li.tab-item.active",
            "sms_service_selector": "#menuNav > li:nth-child(5) > a",
            "sms_history_selector": "#menu_5423 > li:nth-child(2) > a",
            "start_date_selector": "input[name='schSdate']",
            "end_date_selector": "input[name='schEdate']",
            "search_btn_text": "조회",
            "download_btn_selector": "#titleBtn > button:nth-child(1)"
        },
        "메디빌더": {
            "id_selector": "#projUserCd", 
            "pw_selector": "#userPs",
            "login_btn": "#loginBtn",
            "need_softphone_off": True,
            "checkbox_selector": "#agreeCheck",
            "need_menu_click": True, 
            "menu_selector": "#sidebar > div > div.top.tab-wrap > ul > li.tab-item.active"
            # SMS 기능 없음
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
            "call_status_selector": "#uxtagfield-2172-inputEl"
        }
    }
    
    # CALL 계정 설정
    CALL_CONFIG = {
        # "SK일렉링크": {
        #     "id_selector": "#textfield-3558-inputEl", 
        #     "pw_selector": "input[type='password']",
        #     "checkbox_selector": "#chkAgree-displayEl",
        #     "login_btn": "#login-btn-btnInnerEl",
        #     "company_text": "일렉링크",
        #     "outbound_selector": "#uxtagfield-2171-inputEl",
        #     "call_status_selector": "#uxtagfield-2172-inputEl"
        # },
        # "볼드워크": {
        #     "id_selector": "#textfield-3558-inputEl", 
        #     "pw_selector": "input[type='password']",
        #     "checkbox_selector": "#chkAgree-displayEl",
        #     "login_btn": "#login-btn-btnInnerEl",
        #     "company_text": "볼드워크",
        #     "outbound_selector": "#uxtagfield-2171-inputEl",
        #     "call_status_selector": "#uxtagfield-2172-inputEl"
        # },
        # "매스프레소(콴다)": {
        #     "id_selector": "#textfield-3551-inputEl", 
        #     "pw_selector": "#textfield-3552-inputEl",
        #     "checkbox_selector": "#chkAgree-displayEl",
        #     "login_btn": "#login-btn-btnInnerEl",
        #     "company_text": "콴다",
        #     "outbound_selector": "#uxtagfield-2171-inputEl",
        #     "call_status_selector": "#uxtagfield-2172-inputEl"
        # },
        "앤하우스": {
            "id_selector": "#textfield-3551-inputEl", 
            "pw_selector": "#textfield-3552-inputEl",
            "checkbox_selector": "#chkAgree-displayEl",
            "login_btn": "#login-btn-btnInnerEl",
            "company_text": "앤하우스",
            "outbound_selector": "#uxtagfield-2171-inputEl",
            "call_status_selector": "#uxtagfield-2172-inputEl"
        # },
        # "W컨셉": {
        #     "id_selector": "#textfield-3556-inputEl", 
        #     "pw_selector": "#textfield-3557-inputEl",
        #     "checkbox_selector": "#chkAgree-displayEl",
        #     "login_btn": "#login-btn-btnInnerEl",
        #     "company_text": "wConcept",
        #     "outbound_selector": "#uxtagfield-2172-inputEl",
        #     "call_status_selector": "#uxtagfield-2173-inputEl"
        # },
        # "디싸이더스/애드프로젝트": {
        #     "id_selector": "#textfield-3556-inputEl", 
        #     "pw_selector": "#textfield-3557-inputEl",
        #     "checkbox_selector": "#chkAgree-displayEl",
        #     "login_btn": "#login-btn-btnInnerEl",
        #     "company_text": "디싸이더스",
        #     "outbound_selector": "#uxtagfield-2172-inputEl",
        #     "call_status_selector": "#uxtagfield-2173-inputEl"
        }
    }