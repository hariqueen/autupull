from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

class DataManager:
    """데이터 수집 설정 및 다운로드 관리 클래스"""
    
    def __init__(self, login_manager):
        self.login_manager = login_manager
    
    def setup_call_data_collection(self, company_name, start_date=None, end_date=None, download=False):
        """CALL 계정 데이터 수집 설정 및 다운로드"""
        session = self.login_manager.get_active_session(company_name, "call")
        if not session:
            print(f"{company_name} CALL 세션이 없습니다")
            return False
        
        driver = session['driver']
        config = session['account_data']['config']
        wait = WebDriverWait(driver, 10)
        
        print(f"{company_name} 데이터 수집 설정 시작")
        
        def safe_action(action_name, action_func):
            """안전한 액션 실행"""
            for attempt in range(3):
                try:
                    action_func()
                    print(action_name)
                    return True
                except:
                    if attempt < 2:
                        time.sleep(0.5)
            print(f"{company_name} {action_name} 실패")
            return False
        

        company_text = config.get('company_text', company_name)
        if not safe_action(f"회사 선택: {company_name}", 
                        lambda: wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{company_text}')]"))).click() or time.sleep(1)):
            return False
        

        if not safe_action("콜데이터 선택", 
                        lambda: wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '콜데이터')]"))).click() or time.sleep(1)):
            return False
        
        outbound_selector = config.get('outbound_selector', "#uxtagfield-2171-inputEl")
        def outbound_action():
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, outbound_selector)))
            element.click()
            time.sleep(0.3)
            element.send_keys(Keys.ARROW_DOWN)
            element.send_keys(Keys.ENTER)
        
        if not safe_action("아웃바운드 설정", outbound_action):
            return False
        
        call_status_selector = config.get('call_status_selector', "#uxtagfield-2172-inputEl")
        def status_action():
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, call_status_selector)))
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            time.sleep(0.5)
            for i in range(17):
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(0.05)
            actions.send_keys(Keys.ENTER).perform()
        
        if not safe_action("호상태 설정", status_action):
            return False
        
        if start_date:
            if not safe_action(f"시작일 설정: {start_date}", 
                            lambda: (wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#datefield-2168-inputEl"))).clear(), 
                                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#datefield-2168-inputEl"))).send_keys(start_date))):
                return False

        if end_date:
            if not safe_action(f"종료일 설정: {end_date}", 
                            lambda: (wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#datefield-2170-inputEl"))).clear(), 
                                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#datefield-2170-inputEl"))).send_keys(end_date))):
                return False
        
        if not safe_action("검색 실행", 
                        lambda: wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#button-2153"))).click() or time.sleep(2)):
            return False
        
        if download:
            if not safe_action("엑셀 다운로드", 
                            lambda: wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#button-2155"))).click() or time.sleep(3)):
                return False
            
        print(f"{company_name} 데이터 수집 완료")
        return True
    
    def download_sms_data(self, company_name, start_date=None, end_date=None):
        """SMS 데이터 다운로드"""
        session = self.login_manager.get_active_session(company_name, "sms")
        if not session:
            print(f"{company_name} SMS 세션이 없습니다")
            return False
        
        driver = session['driver']
        config = session['account_data']['config']
        wait = WebDriverWait(driver, 10)
        
        print(f"{company_name} SMS 데이터 수집 시작")
        
        # SMS 기능이 없는 회사 체크
        if 'sms_service_selector' not in config:
            print(f"{company_name}는 SMS 기능이 없습니다")
            return False
        
        # 알람창 닫기 (있는 경우만)
        try:
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ax5-dialog-29 > div.ax-dialog-body > div.ax-dialog-buttons > div > button"))).click()
            time.sleep(1)
        except:
            pass
        
        def click_menu_chain():
            """메뉴 클릭 체인 (iframe 초기화용)"""
            # 메뉴 클릭 (볼드워크 등 새 어드민)
            if config.get('need_menu_click'):
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['menu_selector']))).click()
                time.sleep(1)
            
            # 문자서비스 클릭
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['sms_service_selector']))).click()
            time.sleep(1)
            
            # 문자발송이력 클릭
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['sms_history_selector']))).click()
            time.sleep(2)
            return True
        
        # 최초 메뉴 클릭
        click_menu_chain()
        
        # 브랜드 선택이 필요한 회사들 처리
        if config.get('has_brands'):
            # 브랜드 선택 팝업 닫기 (iframe 2에서)
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > 1:
                driver.switch_to.frame(iframes[1])
                try:
                    driver.find_element(By.CSS_SELECTOR, "button[data-dialog-btn='ok']").click()
                    print("✅ 브랜드 선택 팝업 닫기 완료")
                except Exception as e:
                    print(f"❌ 브랜드 선택 팝업 닫기 실패: {e}")
                driver.switch_to.default_content()
            else:
                print(f"❌ 브랜드 선택 팝업용 iframe이 없음 (현재 {len(iframes)}개)")

            # 각 브랜드별로 처리
            for brand in config['brands']:
                print(f"🔍 {brand} 브랜드 처리 시작")
                try:
                    # 메뉴 재클릭으로 iframe 초기화
                    click_menu_chain()
                    time.sleep(2)  # 추가 대기
                    
                    # 페이지 로딩 대기
                    print("⏳ 페이지 로딩 대기 중...")
                    WebDriverWait(driver, 30).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    
                    # iframe 전환
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    if len(iframes) <= 1:
                        print(f"❌ 브랜드 드롭다운용 iframe이 없음 (현재 {len(iframes)}개)")
                        raise RuntimeError("iframe 없음")
                    
                    driver.switch_to.frame(iframes[1])
                    print(f"✅ iframe 2로 전환 완료")
                    
                    # 브랜드 드롭다운 클릭
                    brand_selector = config.get('brand_dropdown_selector')
                    dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, brand_selector)))
                    dropdown.click()
                    print("✅ 브랜드 드롭다운 클릭")
                    time.sleep(1)
                    
                    # 브랜드명 입력하여 검색
                    active = driver.switch_to.active_element
                    active.clear()
                    active.send_keys(brand)
                    time.sleep(1)
                    
                    # 검색된 브랜드 클릭
                    brand_option = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f"//span[normalize-space(text())='{brand}']")
                    ))
                    brand_option.click()
                    time.sleep(1)
                    
                    # 선택된 브랜드 확인
                    selected_brand = dropdown.get_attribute('value')
                    if brand not in selected_brand:
                        print(f"❌ 잘못된 브랜드가 선택됨: 의도={brand}, 실제={selected_brand}")
                        raise ValueError("잘못된 브랜드 선택")
                    print(f"✅ {brand} 브랜드 선택 완료")
                    
                    # SMS 데이터 처리
                    self._process_sms_data(driver, config, start_date, end_date, brand)
                    
                    # X버튼으로 브랜드 초기화
                    try:
                        x_btn = driver.find_element(By.CSS_SELECTOR, 'div[data-ax5autocomplete-remove="true"]')
                        x_btn.click()
                        print("✅ 브랜드 삭제 (X버튼 클릭)")
                        time.sleep(1)
                    except Exception as e:
                        print(f"❌ X버튼 클릭 실패: {e}")
                        # X버튼 실패 시 메뉴 재클릭으로 초기화
                        driver.switch_to.default_content()
                        click_menu_chain()
                        time.sleep(2)
                    
                    driver.switch_to.default_content()
                    print(f"🎉 {brand} 브랜드 처리 완료")
                    
                except Exception as e:
                    print(f"❌ {brand} 브랜드 처리 중 예외 발생: {e}")
                    driver.switch_to.default_content()
                    # 실패 시 메뉴 재클릭
                    click_menu_chain()
                    continue
                
                time.sleep(2)  # 브랜드 간 간격
        
        else:
            # 브랜드 선택이 필요없는 일반 회사들
            # SMS iframe으로 전환 후 데이터 처리
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframes[1])
            time.sleep(2)
            
            self._process_sms_data(driver, config, start_date, end_date)
            
            # iframe에서 나가기
            driver.switch_to.default_content()
        
        print(f"🎉 {company_name} SMS 데이터 수집 완료")
        return True

    def _find_brand_dropdown(self, driver, config, wait):
        """브랜드 드롭다운 찾기"""
        # SMS iframe으로 전환 (브랜드 드롭다운이 iframe 2에 있음)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        iframe_index = config.get('sms_iframe_index', 1)
        if len(iframes) <= iframe_index:
            raise RuntimeError(f"브랜드 드롭다운용 iframe[{iframe_index}]이 존재하지 않습니다. (현재 {len(iframes)}개)")
        driver.switch_to.frame(iframes[iframe_index])
        print(f"✅ iframe {iframe_index + 1}로 전환 완료")
        # 브랜드 드롭다운 클릭
        brand_selector = config.get('brand_dropdown_selector')
        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, brand_selector)))
        element.click()
        print(f"✅ 브랜드 드롭다운 클릭")
        time.sleep(1)
        return element

    def _select_brand(self, driver, brand, wait):
        """브랜드 선택"""
        if brand == "콴다":
            # 콴다는 엔터키로 선택 (브랜드가 1개뿐)
            brand_element = driver.switch_to.active_element
            brand_element.send_keys(Keys.ENTER)
            print(f"✅ {brand} 브랜드 선택 완료 (엔터키)")
        else:
            # 다른 브랜드는 텍스트로 선택
            brand_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{brand}')]")))
            brand_option.click()
            print(f"✅ {brand} 브랜드 선택 완료")
        
        time.sleep(1)
        return True

    def _remove_selected_brand(self, driver, config):
        """선택된 브랜드 삭제 (X버튼 클릭)"""
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        iframe_index = config.get('sms_iframe_index', 1)
        if len(iframes) > iframe_index:
            try:
                driver.switch_to.frame(iframes[iframe_index])
                print(f"✅ iframe {iframe_index + 1}로 전환 완료 (X버튼 시도)")
                try:
                    x_btn = driver.find_element(By.CSS_SELECTOR, 'div[data-ax5autocomplete-remove="true"]')
                    x_btn.click()
                    print("✅ 브랜드 삭제 (X버튼 클릭)")
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ X버튼 클릭 실패: {e}")
            finally:
                driver.switch_to.default_content()
        else:
            print(f"❌ iframe {iframe_index + 1}가 존재하지 않습니다. (현재 {len(iframes)}개) → X버튼 클릭 건너뜀")

    def debug_remove_brand(self, driver, config, brand_name):
        """브랜드 X버튼 클릭 디버깅: 단계별로 점검"""
        iframe_index = config.get('sms_iframe_index', 1)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if len(iframes) <= iframe_index:
            print(f"❌ iframe {iframe_index+1} 없음 (현재 {len(iframes)}개)")
            return

        driver.switch_to.frame(iframes[iframe_index])
        print(f"✅ iframe {iframe_index+1} 전환")

        # 1. X버튼 존재 여부
        try:
            x_btn = driver.find_element(By.CSS_SELECTOR, 'div[data-ax5autocomplete-remove="true"]')
            print("✅ X버튼 DOM에 존재")
        except Exception as e:
            print(f"❌ X버튼 DOM에 없음: {e}")
            driver.switch_to.default_content()
            return

        # 2. X버튼 표시/활성화 상태
        print("is_displayed:", x_btn.is_displayed())
        print("is_enabled:", x_btn.is_enabled())

        # 3. ActionChains로 마우스 이동 후 클릭 시도
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).move_to_element(x_btn).click().perform()
            print("✅ ActionChains로 클릭 시도")
            time.sleep(1)
        except Exception as e:
            print(f"❌ ActionChains 클릭 실패: {e}")

        # 4. JS 강제 클릭
        try:
            driver.execute_script("arguments[0].click();", x_btn)
            print("✅ JS로 강제 클릭 시도")
            time.sleep(1)
        except Exception as e:
            print(f"❌ JS 클릭 실패: {e}")

        # 5. 클릭 후 브랜드명 변화 확인 (예시: 브랜드명이 사라졌는지)
        try:
            brand_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{brand_name}')]")
            if not brand_elements:
                print(f"✅ {brand_name} 브랜드 삭제됨")
            else:
                print(f"❌ {brand_name} 브랜드 여전히 존재")
        except Exception as e:
            print(f"❌ 브랜드명 확인 실패: {e}")

        driver.switch_to.default_content()

    def _process_sms_data(self, driver, config, start_date, end_date, brand_name=None):
        """SMS 데이터 처리 (날짜 입력, 검색, 다운로드)"""
        print(f"📋 SMS 데이터 처리 시작 {f'({brand_name})' if brand_name else ''}")
        
        # 날짜 입력
        if start_date and config.get('start_date_selector'):
            start_input = driver.find_element(By.CSS_SELECTOR, config['start_date_selector'])
            start_input.clear()
            start_input.send_keys(start_date)
            print(f"✅ 시작날짜 입력: {start_date}")
        
        if end_date and config.get('end_date_selector'):
            end_input = driver.find_element(By.CSS_SELECTOR, config['end_date_selector'])
            end_input.clear()
            end_input.send_keys(end_date)
            print(f"✅ 종료날짜 입력: {end_date}")
        
        # 검색 버튼 클릭
        search_btn_text = config.get('search_btn_text', '조회')
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='btn']")
        for btn in buttons:
            if search_btn_text in btn.text:
                btn.click()
                brand_text = f" ({brand_name})" if brand_name else ""
                print(f"✅ 검색 실행{brand_text}")
                break
                
        time.sleep(3)
        
        # 엑셀 다운로드
        if config.get('download_btn_selector'):
            download_dir = "/Users/haribo/Downloads"  # 맥북 기본 다운로드 폴더
            before_files = set(os.listdir(download_dir))
            download_btn = driver.find_element(By.CSS_SELECTOR, config['download_btn_selector'])
            download_btn.click()
            brand_text = f" ({brand_name})" if brand_name else ""
            print(f"✅ 엑셀 다운로드{brand_text}")

            # 데이터 없음 알림 감지 및 처리
            try:
                alert = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#ax5-dialog-29 .ax-dialog-msg"))
                )
                if "검색된 데이터가 없습니다" in alert.text:
                    print("검색된 데이터가 없습니다. 다음 단계로 진행.")
                    return True
            except Exception:
                pass

            # 다운로드 완료 대기 (최대 30초)
            max_wait = 30
            check_interval = 1
            downloaded = False
            for i in range(max_wait):
                time.sleep(check_interval)
                current_files = set(os.listdir(download_dir))
                new_files = current_files - before_files
                for file in new_files:
                    if (file.endswith('.xlsx') or file.endswith('.xls')) and not file.endswith('.crdownload'):
                        file_path = os.path.join(download_dir, file)
                        prev_size = os.path.getsize(file_path)
                        time.sleep(2)
                        if os.path.getsize(file_path) == prev_size and prev_size > 0:
                            print(f"다운로드 완료: {file}")
                            downloaded = True
                            break
                if downloaded:
                    break
                if i % 5 == 0:
                    print(f"다운로드 대기 중... ({i+1}/{max_wait}초)")
            else:
                print("다운로드 대기 시간 초과")
            time.sleep(1)
        
        return True