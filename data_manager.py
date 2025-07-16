from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from config import ElementConfig, SiteConfig, DateConfig

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
        
        try:
            # 회사 선택
            company_text = config.get('company_text', company_name)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{company_text}')]"))).click()
            time.sleep(1)
            
            # 콜데이터 선택
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '콜데이터')]"))).click()
            time.sleep(1)
            
            # 아웃바운드 설정
            outbound_selector = config.get('outbound_selector', "#uxtagfield-2171-inputEl")
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, outbound_selector)))
            element.click()
            time.sleep(0.3)
            element.send_keys(Keys.ARROW_DOWN, Keys.ENTER)
            
            # 호상태 설정
            call_status_selector = config.get('call_status_selector', "#uxtagfield-2172-inputEl")
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, call_status_selector)))
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            time.sleep(0.5)
            for _ in range(17):
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(0.05)
            actions.send_keys(Keys.ENTER).perform()
            
            # 날짜 설정
            if start_date:
                start_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['start_date_selector'])))
                start_input.clear()
                start_input.send_keys(start_date)

            if end_date:
                end_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['end_date_selector'])))
                end_input.clear()
                end_input.send_keys(end_date)
            
            # 검색 실행
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['search_btn_selector']))).click()
            time.sleep(2)
            
            # 다운로드 시도
            if download:
                # 엑셀 다운로드 버튼 클릭
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['download_btn_selector']))).click()
                time.sleep(1)
                
                # 데이터 없음 체크
                try:
                    alert = wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, config['no_data_alert_selector']))
                    )
                    if config['no_data_text'] in alert.text:
                        print("검색된 데이터가 없습니다. 다음 단계로 진행.")
                        return True
                except Exception:
                    pass
                
                # 데이터가 있는 경우 다운로드 진행
                print("✅ 다운로드 시작")
                time.sleep(3)
            
            print(f"{company_name} 데이터 수집 완료")
            return True
            
        except Exception as e:
            print(f"{company_name} 데이터 수집 실패: {e}")
            return False
    
    def _handle_alert(self, driver, check_iframe=False):
        """알림창 처리 (브랜드 선택 팝업 포함)"""
        try:
            if check_iframe:
                # iframe 2에서 알림창 확인
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                if len(iframes) > 1:
                    driver.switch_to.frame(iframes[1])
                    try:
                        alert = driver.find_element(By.CSS_SELECTOR, "button[data-dialog-btn='ok']")
                        alert.click()
                        print("✅ 브랜드 선택 팝업 닫기 완료")
                        driver.switch_to.default_content()
                        return True
                    except:
                        driver.switch_to.default_content()
                        return False
            else:
                # 일반 알림창 처리
                alert = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-dialog-btn='ok']"))
                )
                alert.click()
                print("✅ 알림창 처리 완료")
                return True
        except:
            return False

    def _wait_for_masks(self, driver, timeout=None):
        """로딩 마스크 대기"""
        if timeout is None:
            timeout = ElementConfig.WAIT['default']
            
        print("🔍 마스크 확인 중...")
        masks = driver.find_elements(By.CSS_SELECTOR, ElementConfig.COMMON['loading_mask'])
        if masks:
            print(f"⚠️ 마스크 발견: {len(masks)}개")
            for mask in masks:
                if mask.is_displayed():
                    print("마스크가 표시된 상태입니다. 대기 시작...")
                    WebDriverWait(driver, timeout).until(
                        EC.invisibility_of_element(mask)
                    )
            print("✅ 모든 마스크가 사라짐")
        else:
            print("✅ 마스크 없음")
    
    def _click_element(self, driver, element, js_click=True):
        """엘리먼트 클릭 (JavaScript 또는 일반)"""
        try:
            if js_click:
                driver.execute_script(ElementConfig.JS['click'], element)
            else:
                element.click()
            return True
        except Exception as e:
            print(f"⚠️ 클릭 실패: {e}")
            return False
    
    def _switch_to_iframe(self, driver, iframe_index):
        """iframe 전환"""
        print("🔍 iframe 확인 중...")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes and len(iframes) > iframe_index:
            driver.switch_to.frame(iframes[iframe_index])
            print(f"✅ iframe[{iframe_index}] 전환 완료")
            return True
        else:
            print(f"⚠️ iframe[{iframe_index}] 찾을 수 없음 (전체 {len(iframes)}개)")
            return False
    
    def _handle_download(self, driver, button_selector, brand=None):
        """다운로드 처리"""
        brand_text = f" ({brand})" if brand else ""
        
        # 마스크 대기
        self._wait_for_masks(driver)
        
        # 다운로드 버튼 찾기 및 클릭
        download_btn = driver.find_element(By.CSS_SELECTOR, button_selector)
        print(f"🔍 다운로드 버튼 상태: displayed={download_btn.is_displayed()}, enabled={download_btn.is_enabled()}")
        
        if self._click_element(driver, download_btn):
            print(f"✅ JavaScript로 다운로드 버튼 클릭 성공{brand_text}")
            print(f"✅ 엑셀 다운로드 시작{brand_text}")
            return True
        return False
    
    def _try_click_no_data_alert(self, driver, wait):
        """데이터 없음 알림창 확인 버튼 클릭"""
        try:
            ok_button = driver.find_element(By.CSS_SELECTOR, "#ax5-dialog-29 button[data-dialog-btn='ok']")
            ok_button.click()
            return True
        except Exception:
            return False

    def _handle_no_data_alert(self, driver, wait):
        """데이터 없음 알림창 처리"""
        try:
            alert = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#ax5-dialog-29 .ax-dialog-msg"))
            )
            if "검색된 데이터가 없습니다" in alert.text:
                print("검색된 데이터가 없습니다. 다음 단계로 진행.")
                return True
        except Exception:
            pass
        return False

    def _process_sms_data(self, driver, config, start_date=None, end_date=None, brand=None, is_last_brand=False):
        """SMS 데이터 처리 (검색 및 다운로드)"""
        wait = WebDriverWait(driver, 10)
        
        # 날짜 입력
        if start_date:
            start_date_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['start_date_selector'])))
            start_date_input.clear()
            start_date_input.send_keys(start_date)
            print(f"✅ 시작날짜 입력: {start_date}")
        
        if end_date:
            end_date_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['end_date_selector'])))
            end_date_input.clear()
            end_date_input.send_keys(end_date)
            print(f"✅ 종료날짜 입력: {end_date}")
        
        # 검색 버튼 클릭
        search_btn_text = config.get('search_btn_text', '조회')
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='btn']")
        for btn in buttons:
            if search_btn_text in btn.text:
                btn.click()
                print(f"✅ 검색 실행 ({brand if brand else ''})")
                break
        time.sleep(2)
        
        # 엑셀 다운로드
        if config.get('download_btn_selector'):
            download_dir = "/Users/haribo/Downloads"  # 맥북 기본 다운로드 폴더
            before_files = set(os.listdir(download_dir))
            download_btn = driver.find_element(By.CSS_SELECTOR, config['download_btn_selector'])
            download_btn.click()
            print(f"✅ 엑셀 다운로드 클릭 ({brand if brand else ''})")
            time.sleep(2)
        
        # 데이터 없음 알림 처리
        if brand:  # 브랜드가 있는 경우
            try:
                alert = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#ax5-dialog-29 .ax-dialog-msg"))
                )
                if "검색된 데이터가 없습니다" in alert.text:
                    print("검색된 데이터가 없습니다. 다음 단계로 진행.")
                    
                    if not is_last_brand:  # 마지막 브랜드가 아닌 경우에만 확인 버튼 클릭
                        if self._try_click_no_data_alert(driver, wait):
                            print("✅ 데이터 없음 알림창 확인 버튼 클릭 성공")
                        else:
                            print("❌ 데이터 없음 알림창 확인 버튼 클릭 실패")
                    return False  # 데이터 없음 표시
            except Exception:
                pass  # 알림창이 없으면 계속 진행
        else:  # 일반 사이트의 경우
            if self._handle_no_data_alert(driver, wait):
                return False  # 데이터 없음 표시
        
        # 다운로드 완료 대기 (최대 30초)
        if config.get('download_btn_selector'):
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
        
        return True  # 데이터 있음 표시

    def download_sms_data(self, company_name, start_date=None, end_date=None):
        """SMS 데이터 다운로드"""
        session = self.login_manager.get_active_session(company_name, "sms")
        if not session:
            print(f"{company_name} SMS 세션이 없습니다")
            return False
        
        driver = session['driver']
        config = session['account_data']['config']
        wait = WebDriverWait(driver, ElementConfig.WAIT['default'])
        
        print(f"{company_name} SMS 데이터 수집 시작")
        
        # SMS 기능이 없는 회사 체크
        if 'sms_service_selector' not in config:
            print(f"{company_name}는 SMS 기능이 없습니다")
            return False
        
        def click_menu_chain():
            """메뉴 클릭 체인"""
            try:
                # 메뉴 클릭 (볼드워크 등 새 어드민)
                if config.get('need_menu_click'):
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['menu_selector']))).click()
                    time.sleep(ElementConfig.WAIT['short'])
                
                # 문자서비스 클릭
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['sms_service_selector']))).click()
                time.sleep(ElementConfig.WAIT['short'])
                
                # 문자발송이력 클릭
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['sms_history_selector']))).click()
                time.sleep(ElementConfig.WAIT['short'])
                return True
            except Exception as e:
                print(f"❌ 메뉴 클릭 실패: {e}")
                return False
        
        # 최초 메뉴 클릭
        if not click_menu_chain():
            return False
        
        # 브랜드 선택이 필요한 회사들 처리
        if config.get('has_brands'):
            # 브랜드 선택 팝업 닫기
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > ElementConfig.IFRAME['brand_popup_index']:
                driver.switch_to.frame(iframes[ElementConfig.IFRAME['brand_popup_index']])
                try:
                    driver.find_element(By.CSS_SELECTOR, ElementConfig.COMMON['alert_ok']).click()
                    print("✅ 브랜드 선택 팝업 닫기 완료")
                except Exception as e:
                    print(f"❌ 브랜드 선택 팝업 닫기 실패: {e}")
                driver.switch_to.default_content()

            # 각 브랜드별로 처리
            for brand_index, brand in enumerate(config['brands']):
                is_last_brand = brand_index == len(config['brands']) - 1
                print(ElementConfig.BRAND['messages']['start'].format(brand))
                try:
                    # iframe 전환
                    print(ElementConfig.MESSAGES['iframe']['check'])
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    if len(iframes) <= ElementConfig.IFRAME['data_index']:
                        print(ElementConfig.MESSAGES['iframe']['error'].format(len(iframes)))
                        raise RuntimeError("iframe 없음")
                    
                    driver.switch_to.frame(iframes[ElementConfig.IFRAME['data_index']])
                    print(ElementConfig.MESSAGES['iframe']['success'].format(ElementConfig.IFRAME['data_index'] + 1))
                    
                    # 브랜드 선택
                    dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['brand_dropdown_selector'])))
                    dropdown.click()
                    time.sleep(ElementConfig.WAIT['brand_select'])
                    
                    brand_element = driver.switch_to.active_element
                    for _ in range(brand_index + 1):
                        brand_element.send_keys(ElementConfig.BRAND['key_sequence']['select'][0])
                        time.sleep(ElementConfig.WAIT['key_interval'])
                    brand_element.send_keys(ElementConfig.BRAND['key_sequence']['select'][1])
                    print(ElementConfig.BRAND['messages']['select'].format(brand))
                    time.sleep(ElementConfig.WAIT['short'])
                    
                    # SMS 데이터 처리
                    result = self._process_sms_data(driver, config, start_date, end_date, brand, is_last_brand)
                    
                    # 마지막 브랜드이고 데이터가 없으면 종료
                    if is_last_brand and not result:
                        print(ElementConfig.BRAND['messages']['no_data'].format(brand))
                        driver.switch_to.default_content()
                        return True
                    
                    # 다음 브랜드를 위해 X버튼 클릭
                    if not is_last_brand:
                        driver.execute_script(ElementConfig.JS['remove_brand'])
                        print(ElementConfig.BRAND['messages']['remove'])
                        time.sleep(ElementConfig.WAIT['short'])
                    
                    driver.switch_to.default_content()
                    print(ElementConfig.BRAND['messages']['complete'].format(brand))
                    
                except Exception as e:
                    print(ElementConfig.BRAND['messages']['error'].format(brand, e))
                    driver.switch_to.default_content()
                    if not is_last_brand:
                        click_menu_chain()
                        continue
                    else:
                        print(ElementConfig.BRAND['messages']['no_data'].format(brand))
                        return True
                
                time.sleep(ElementConfig.WAIT['short'])
        
        else:
            # 일반 회사 처리
            print(ElementConfig.MESSAGES['iframe']['check'])
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > ElementConfig.IFRAME['data_index']:
                driver.switch_to.frame(iframes[ElementConfig.IFRAME['data_index']])
                print(ElementConfig.MESSAGES['iframe']['success'].format(ElementConfig.IFRAME['data_index'] + 1))
                time.sleep(ElementConfig.WAIT['short'])
                
                self._process_sms_data(driver, config, start_date, end_date)
                driver.switch_to.default_content()
            else:
                print(ElementConfig.MESSAGES['iframe']['error'].format(len(iframes)))
                return False
        
        print(f"🎉 {company_name} SMS 데이터 수집 완료")
        return True
    
    def download_chat_data(self, company_name, start_date=None, end_date=None):
        """채팅 데이터 다운로드 (디싸이더스/애드프로젝트 전용)"""
        session = self.login_manager.get_active_session(company_name, "sms")  # SMS 세션 재사용
        if not session:
            print(f"{company_name} 채팅 세션이 없습니다")
            return False
        
        driver = session['driver']
        config = session['account_data']['config']
        wait = WebDriverWait(driver, ElementConfig.WAIT['default'])
        
        print(f"{company_name} 채팅 데이터 수집 시작")
        
        # 채팅 기능이 없는 회사 체크
        if not config.get('has_chat'):
            print(f"{company_name}는 채팅 기능이 없습니다")
            return False
        
        def click_chat_menu_chain():
            """채팅 메뉴 클릭 체인"""
            try:
                # 메인 프레임으로 돌아가기
                driver.switch_to.default_content()
                
                # 채팅서비스 클릭
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['chat_service_selector']))).click()
                time.sleep(ElementConfig.WAIT['short'])
                
                # 채팅이력 클릭
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['chat_history_selector']))).click()
                time.sleep(ElementConfig.WAIT['short'])
                return True
            except Exception as e:
                print(f"❌ 채팅 메뉴 클릭 실패: {e}")
                return False
        
        # 채팅 메뉴 클릭
        if not click_chat_menu_chain():
            return False
        
        # 채팅에서도 브랜드 선택이 필요한 경우
        if config.get('chat_has_brands'):
            # 브랜드 선택 팝업 닫기
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if len(iframes) > ElementConfig.IFRAME['brand_popup_index']:
                driver.switch_to.frame(iframes[ElementConfig.IFRAME['brand_popup_index']])
                try:
                    driver.find_element(By.CSS_SELECTOR, ElementConfig.COMMON['alert_ok']).click()
                    print("✅ 채팅 브랜드 선택 팝업 닫기 완료")
                except Exception as e:
                    print(f"❌ 채팅 브랜드 선택 팝업 닫기 실패: {e}")
                driver.switch_to.default_content()

            # 각 브랜드별로 처리
            for brand_index, brand in enumerate(config['chat_brands']):
                is_last_brand = brand_index == len(config['chat_brands']) - 1
                print(f"🔍 {brand} 채팅 브랜드 처리 시작")
                try:
                    # iframe 전환
                    print("🔍 채팅 iframe 확인 중...")
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    chat_iframe_index = config.get('chat_iframe_index', ElementConfig.IFRAME['data_index'])
                    
                    if len(iframes) <= chat_iframe_index:
                        print(f"❌ 채팅 iframe이 부족함 (현재 {len(iframes)}개)")
                        raise RuntimeError("채팅 iframe 없음")
                    
                    driver.switch_to.frame(iframes[chat_iframe_index])
                    print(f"✅ 채팅 iframe[{chat_iframe_index}] 전환 완료")
                    
                    # 팀 디폴트 태그 제거 (채팅에서만 필요)
                    if config.get('chat_need_team_tag_remove'):
                        try:
                            team_tag_remove_btn = driver.find_element(By.CSS_SELECTOR, 'div[data-ax5autocomplete-remove="true"]')
                            team_tag_remove_btn.click()
                            print("✅ 팀 디폴트 태그 제거 완료")
                            time.sleep(ElementConfig.WAIT['short'])
                        except Exception as e:
                            print(f"⚠️ 팀 디폴트 태그 제거 실패 (계속 진행): {e}")
                    
                    # 브랜드 선택
                    dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['chat_brand_dropdown_selector'])))
                    dropdown.click()
                    time.sleep(ElementConfig.WAIT['brand_select'])
                    
                    brand_element = driver.switch_to.active_element
                    for _ in range(brand_index + 1):
                        brand_element.send_keys(ElementConfig.BRAND['key_sequence']['select'][0])
                        time.sleep(ElementConfig.WAIT['key_interval'])
                    brand_element.send_keys(ElementConfig.BRAND['key_sequence']['select'][1])
                    print(f"✅ {brand} 채팅 브랜드 선택 완료")
                    time.sleep(ElementConfig.WAIT['short'])
                    
                    # 채팅 데이터 처리
                    result = self._process_chat_data(driver, config, start_date, end_date, brand, is_last_brand)
                    
                    # 마지막 브랜드이고 데이터가 없으면 종료
                    if is_last_brand and not result:
                        print(f"마지막 채팅 브랜드 {brand}에서 데이터 없음 - 종료")
                        driver.switch_to.default_content()
                        return True
                    
                    # 다음 브랜드를 위해 X버튼 클릭
                    if not is_last_brand:
                        try:
                            remove_btn = driver.find_element(By.CSS_SELECTOR, config['chat_brand_remove_btn_selector'])
                            remove_btn.click()
                            print("✅ 채팅 브랜드 X버튼 클릭 완료")
                        except Exception as e:
                            print(f"⚠️ 채팅 브랜드 X버튼 클릭 실패: {e}")
                        time.sleep(ElementConfig.WAIT['short'])
                    
                    driver.switch_to.default_content()
                    print(f"🎉 {brand} 채팅 브랜드 처리 완료")
                    
                except Exception as e:
                    print(f"❌ {brand} 채팅 브랜드 처리 중 예외 발생: {e}")
                    driver.switch_to.default_content()
                    if not is_last_brand:
                        click_chat_menu_chain()
                        continue
                    else:
                        print(f"마지막 채팅 브랜드 {brand}에서 데이터 없음 - 종료")
                        return True
                
                time.sleep(ElementConfig.WAIT['short'])
        
        else:
            # 일반 회사 처리 (브랜드 없는 경우)
            print("🔍 채팅 iframe 확인 중...")
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            chat_iframe_index = config.get('chat_iframe_index', ElementConfig.IFRAME['data_index'])
            
            if len(iframes) > chat_iframe_index:
                driver.switch_to.frame(iframes[chat_iframe_index])
                print(f"✅ 채팅 iframe[{chat_iframe_index}] 전환 완료")
                time.sleep(ElementConfig.WAIT['short'])
                
                self._process_chat_data(driver, config, start_date, end_date)
                driver.switch_to.default_content()
            else:
                print(f"❌ 채팅 iframe이 부족함 (현재 {len(iframes)}개)")
                return False
        
        print(f"🎉 {company_name} 채팅 데이터 수집 완료")
        return True

    def _process_chat_data(self, driver, config, start_date=None, end_date=None, brand=None, is_last_brand=False):
        """채팅 데이터 처리 (검색 및 다운로드)"""
        wait = WebDriverWait(driver, 10)
        
        # 날짜 입력
        if start_date:
            start_date_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['chat_start_date_selector'])))
            start_date_input.clear()
            start_date_input.send_keys(start_date)
            print(f"✅ 채팅 시작날짜 입력: {start_date}")
        
        if end_date:
            end_date_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['chat_end_date_selector'])))
            end_date_input.clear()
            end_date_input.send_keys(end_date)
            print(f"✅ 채팅 종료날짜 입력: {end_date}")
        
        # 검색 버튼 클릭
        search_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['chat_search_btn_selector'])))
        search_btn.click()
        print(f"✅ 채팅 검색 실행 ({brand if brand else ''})")
        time.sleep(2)
        
        # 엑셀 다운로드
        if config.get('chat_download_btn_selector'):
            download_dir = "/Users/haribo/Downloads"  # 맥북 기본 다운로드 폴더
            before_files = set(os.listdir(download_dir))
            
            try:
                download_btn = driver.find_element(By.CSS_SELECTOR, config['chat_download_btn_selector'])
                download_btn.click()
                print(f"✅ 채팅 엑셀 다운로드 클릭 ({brand if brand else ''})")
                time.sleep(2)
            except Exception as e:
                print(f"❌ 채팅 다운로드 버튼 클릭 실패: {e}")
                return False
        
        # 데이터 없음 알림 처리
        if brand:  # 브랜드가 있는 경우
            try:
                alert = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#ax5-dialog-29 .ax-dialog-msg"))
                )
                if "검색된 데이터가 없습니다" in alert.text:
                    print("채팅에서 검색된 데이터가 없습니다. 다음 단계로 진행.")
                    
                    if not is_last_brand:  # 마지막 브랜드가 아닌 경우에만 확인 버튼 클릭
                        if self._try_click_no_data_alert(driver, wait):
                            print("✅ 채팅 데이터 없음 알림창 확인 버튼 클릭 성공")
                        else:
                            print("❌ 채팅 데이터 없음 알림창 확인 버튼 클릭 실패")
                    return False  # 데이터 없음 표시
            except Exception:
                pass  # 알림창이 없으면 계속 진행
        else:  # 일반 사이트의 경우
            if self._handle_no_data_alert(driver, wait):
                return False  # 데이터 없음 표시
        
        # 다운로드 완료 대기 (최대 30초)
        if config.get('chat_download_btn_selector'):
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
                            print(f"채팅 다운로드 완료: {file}")
                            downloaded = True
                            break
                if downloaded:
                    break
                if i % 5 == 0:
                    print(f"채팅 다운로드 대기 중... ({i+1}/{max_wait}초)")
            else:
                print("채팅 다운로드 대기 시간 초과")
            time.sleep(1)
        
        return True  # 데이터 있음 표시