from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from config import ElementConfig
from config import DateConfig

# 환경변수 로드
load_dotenv()

def init_firebase():
    """Firebase 초기화"""
    try:
        if not firebase_admin._apps:
            # 환경변수에서 JSON 문자열 가져오기
            firebase_json = os.getenv("FIREBASE_PRIVATE_KEY")
            
            if not firebase_json:
                raise ValueError("FIREBASE_PRIVATE_KEY 환경변수가 설정되지 않았습니다.")
            
            try:
                # JSON 문자열 → 딕셔너리로 파싱
                firebase_json = firebase_json.replace('\n', '\\n').replace('\r', '')
                cred_dict = json.loads(firebase_json)
                cred = credentials.Certificate(cred_dict)
                print("✅ 환경변수에서 Firebase 인증 정보 로드")
            except json.JSONDecodeError as e:
                raise ValueError(f"Firebase JSON 파싱 오류: {e}. .env 파일의 JSON 형식을 확인하세요.")
            
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        print(f"❌ Firebase 초기화 실패: {e}")
        return None

def get_deciderse_account(db):
    """디싸이더스 계정 정보 가져오기"""
    try:
        # 계정 검색 - account_type 필드명 사용
        target_accounts = db.collection("accounts") \
            .where("company_name", "==", "디싸이더스/애드프로젝트") \
            .where("account_type", "==", "sms") \
            .get()
        
        for account in target_accounts:
            account_data = account.to_dict()
            # url 필드명 변환
            account_data['url'] = account_data.get('site_url')
            # id 필드명 변환
            account_data['id'] = account_data.get('username')
            return account_data
        return None
    except Exception as e:
        print(f"❌ 계정 정보 조회 실패: {e}")
        return None

def setup_driver():
    """Chrome 드라이버 설정"""
    options = Options()
    options.add_experimental_option("detach", True)  # 브라우저 자동 종료 방지
    options.add_argument("--start-maximized")  # 최대화 상태로 시작
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    service = Service()  # ChromeDriver 자동 설치
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login(driver, account):
    """로그인 수행"""
    try:
        wait = WebDriverWait(driver, 10)
        
        # 로그인 페이지 접속
        driver.get(account['url'])
        time.sleep(2)
        
        # ID 입력
        id_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["id_input"])))
        id_element.send_keys(account['id'])
        
        # 비밀번호 입력
        pw_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["pw_input"])))
        pw_element.send_keys(account['password'])
        
        # 체크박스 클릭 (필요한 경우)
        try:
            checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["agree_checkbox"])))
            checkbox.click()
        except:
            print("✅ 체크박스 없음")
            pass
        
        # 로그인 버튼 클릭
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["login_btn"])))
        login_button.click()
        time.sleep(2)
        
        # 로그인 직후 알림창 처리
        try:
            alert_ok_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["alert_ok_btn"]))
            )
            alert_ok_button.click()
            print("✅ 로그인 후 알림창 닫기 완료")
            time.sleep(1)
        except:
            print("✅ 로그인 후 알림창 없음")  # 알림창이 없는 경우 (정상적인 상황)
            pass
        
        print("✅ 로그인 성공")
        return True
    except Exception as e:
        print(f"❌ 로그인 실패: {e}")
        return False

def navigate_to_chat(driver, start_date_str=None, end_date_str=None):
    """채팅관리 -> 채팅진행건리스트로 이동하고 날짜 설정"""
    # DateConfig에서 날짜 자동 세팅
    if start_date_str is None or end_date_str is None:
        dates = DateConfig.get_sms_format()
        start_date_str = dates["start_date"]
        end_date_str = dates["end_date"]
    try:
        wait = WebDriverWait(driver, 10)
        
        # 채팅관리 메뉴 클릭
        chat_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH, ElementConfig.CHAT["menu_chat"])
        ))
        chat_menu.click()
        time.sleep(1)
        
        # 채팅진행건리스트 클릭
        chat_list = wait.until(EC.element_to_be_clickable(
            (By.XPATH, ElementConfig.CHAT["menu_chat_list"])
        ))
        chat_list.click()
        time.sleep(1)
        
        # iframe 전환
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if len(iframes) > 1:
            driver.switch_to.frame(iframes[1])
            print("✅ iframe 전환 완료")
            
            # iframe 로드 대기
            time.sleep(2)
            
            # 팀 태그 제거
            print("🔍 팀 태그 제거 시도 중...")
            try:
                team_tag = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["team_tag_remove"])))
                team_tag.click()
                print("✅ 팀 태그 제거 완료")
            except Exception as e:
                print(f"❌ 팀 태그 제거 실패: {e}")
            time.sleep(1)
            
            # 날짜 입력 시도
            print("📅 날짜 입력 시도 중...")
            
            # 날짜 문자열을 datetime 객체로 변환
            from datetime import datetime
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            try:
                # 달력 UI 활성화 (시작 날짜)
                start_date_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["start_date_input"])))
                start_date_input.click()
                time.sleep(1)  # 달력이 나타날 때까지 대기
                print("📅 시작 날짜 달력 활성화")
                
                # 시작일 선택 - 왼쪽 달력에서
                print("📅 시작일 달력 연월 확인 중...")
                current_year = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_left_year"]))).text)
                current_month = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_left_month"]))).text.replace("월", ""))
                
                # 목표 날짜의 연월
                target_year = start_date.year
                target_month = start_date.month
                
                print(f"시작일 달력: {current_year}년 {current_month}월 → {target_year}년 {target_month}월로 이동")
                
                # 필요한 만큼 이전/다음 버튼 클릭 (왼쪽 달력)
                while current_year != target_year or current_month != target_month:
                    if (current_year * 12 + current_month) > (target_year * 12 + target_month):
                        # 이전 버튼 클릭 (왼쪽 달력)
                        prev_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_left_prev"])))
                        prev_button.click()
                    else:
                        # 다음 버튼 클릭 (왼쪽 달력)
                        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_left_next"])))
                        next_button.click()
                    time.sleep(0.5)
                    
                    # 현재 연월 다시 확인 (왼쪽 달력)
                    current_year = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_left_year"]))).text)
                    current_month = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_left_month"]))).text.replace("월", ""))
                
                # 날짜 선택
                start_day = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_left_day"].format(start_date_str))))
                start_day.click()
                time.sleep(1)
                
                # 종료 날짜 달력 활성화
                end_date_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["end_date_input"])))
                end_date_input.click()
                time.sleep(1)
                print("📅 종료 날짜 달력 활성화")
                
                # 종료일 선택 - 오른쪽 달력에서
                print("📅 종료일 달력 연월 확인 중...")
                # 종료일 달력의 연월 확인 (오른쪽 달력)
                current_year = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_right_year"]))).text)
                current_month = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_right_month"]))).text.replace("월", ""))
                
                # 목표 날짜의 연월
                target_year = end_date.year
                target_month = end_date.month
                
                print(f"종료일 달력: {current_year}년 {current_month}월 → {target_year}년 {target_month}월로 이동")
                
                # 필요한 만큼 이전/다음 버튼 클릭 (오른쪽 달력)
                while current_year != target_year or current_month != target_month:
                    if (current_year * 12 + current_month) > (target_year * 12 + target_month):
                        # 이전 버튼 클릭 (오른쪽 달력)
                        prev_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_right_prev"])))
                        prev_button.click()
                    else:
                        # 다음 버튼 클릭 (오른쪽 달력)
                        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_right_next"])))
                        next_button.click()
                    time.sleep(0.5)
                    
                    # 현재 연월 다시 확인 (오른쪽 달력)
                    current_year = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_right_year"]))).text)
                    current_month = int(wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_right_month"]))).text.replace("월", ""))
                
                # 날짜 선택
                end_day = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_right_day"].format(end_date_str))))
                end_day.click()
                time.sleep(1)
                
                # OK 버튼 클릭
                ok_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["calendar_ok_btn"])))
                ok_button.click()
                time.sleep(1)
                print("✅ 날짜 입력 성공")
                
            except Exception as e:
                print(f"❌ 날짜 입력 실패: {str(e)}")
                print("❌ 날짜 입력이 실패했습니다.")
                
            return True
    except Exception as e:
        print(f"❌ 채팅 메뉴 이동 실패: {e}")
        return False

def click_brand_x_button(driver, wait):
    """브랜드 X버튼 클릭만 담당"""
    close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["x_btn"])))
    close_btn.click()
    print("✅ X버튼 클릭 성공")

def download_excel_for_brands(driver):
    """날짜/팀만 선택 후 바로 조회 및 엑셀 다운로드"""
    wait = WebDriverWait(driver, 10)
    # 브랜드 선택 부분 제거

    # 조회 버튼 클릭
    try:
        search_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["search_btn"])))
        search_btn.click()
        print("조회 버튼 클릭")
        time.sleep(2)
    except Exception as e:
        print(f"조회 버튼 클릭 실패: {e}")
    time.sleep(2)

    # 알림창 처리
    alert_closed = handle_alert(driver)
    if alert_closed:
        print("⚠️ 검색된 데이터 없음 - 알림창 닫음")
        time.sleep(1)
    else:
        # 알림창이 없으면 데이터가 있다는 뜻이므로 엑셀 다운로드
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if len(iframes) > ElementConfig.CHAT["iframe_index"]:
            driver.switch_to.frame(iframes[ElementConfig.CHAT["iframe_index"]])
        try:
            excel_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["excel_btn"])))
            excel_btn.click()
            print("엑셀 다운로드 버튼 클릭")
            time.sleep(2)
        except Exception as e:
            print(f"엑셀 다운로드 버튼 클릭 실패: {e}")
    # 필요시 X버튼 클릭 등 후처리

def handle_alert(driver):
    """데이터 없음 알림창 닫기 (현재 iframe에서만 시도, frame 전환 없음)"""
    try:
        alert_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ElementConfig.CHAT["alert_ok_btn"]))
        )
        alert_button.click()
        print("✅ 데이터 없음 알림창 닫기 완료")
        return True
    except Exception:
        print("ℹ️ 데이터 없음 알림창 없음")
        return False

def main():
    DateConfig.set_dates("2025-06-01", "2025-06-30")  # 날짜 세팅 (main.py와 동일하게)
    db = init_firebase()
    if not db:
        return
    account = get_deciderse_account(db)
    if not account:
        print("❌ 디싸이더스 계정 정보를 찾을 수 없습니다.")
        return
    driver = setup_driver()
    try:
        if not login(driver, account):
            return
        print("✅ 로그인 성공")
        time.sleep(2)
        dates = DateConfig.get_sms_format()
        start_date_str = dates["start_date"]
        end_date_str = dates["end_date"]
        start_date_str = f"{start_date_str[:4]}-{start_date_str[4:6]}-{start_date_str[6:]}"
        end_date_str = f"{end_date_str[:4]}-{end_date_str[4:6]}-{end_date_str[6:]}"
        if navigate_to_chat(driver, start_date_str, end_date_str):
            print("✅ 채팅 메뉴 이동 성공")
            download_excel_for_brands(driver)
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    main()