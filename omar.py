from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

BASE_URL = "https://www.oasismuseum.com/ticket"
TARGET_DATE = "2025-07-19"
THEME_ID = "6"
FULL_URL = f"{BASE_URL}?date={TARGET_DATE}&id={THEME_ID}"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(FULL_URL)
wait = WebDriverWait(driver, 30)

def safe_find_elements():
    while True:
        print("페이지 로딩 완료 대기 중...")
        try:
            def check_page_loaded(driver):
                try:
                    alert = driver.switch_to.alert
                    return True
                except:
                    pass
                if len(driver.find_elements(By.CSS_SELECTOR, "button.btn-opened, button.btn-closed")) > 0:
                    return True
                return False
            
            wait.until(check_page_loaded)
            
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"알림창 발견: {alert_text}")
                alert.accept()
                print("예약 불가능한 날짜입니다. 1초 후 다시 접속...")
                time.sleep(1)
                driver.get(FULL_URL)
                continue
            except:
                pass
        except TimeoutException:
            print("30초 대기 후에도 페이지가 로드되지 않음. 새로고침...")
            driver.refresh()
            continue
        
        active_btns = driver.find_elements(By.CSS_SELECTOR, "button.btn-opened")
        if active_btns:
            print(f"예약 가능한 시간 {len(active_btns)}개 발견!")
            return active_btns
        
        print("예약 가능한 시간이 없습니다. 1초 후 새로고침...")
        time.sleep(1)
        driver.refresh()

available_time_buttons = safe_find_elements()

print("예약 가능한 시간:")
for btn in available_time_buttons:
    print(btn.text.strip())

for btn in available_time_buttons:
    if "10:00" in btn.text:
        btn.click()
        print("10:00 클릭 완료")
        break

name_input = wait.until(EC.presence_of_element_located((By.ID, "f_name")))
name_input.clear()
name_input.send_keys("홍길동")

phone_input = wait.until(EC.presence_of_element_located((By.ID, "f_tel")))
phone_input.clear()
phone_input.send_keys("01000000000")

agree_checkbox = wait.until(EC.presence_of_element_located((By.ID, "f_agree")))
if not agree_checkbox.is_selected():
    agree_checkbox.click()

submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "f_submit")))
submit_btn.click()

payment_select = wait.until(EC.presence_of_element_located((By.ID, "f_payment")))
from selenium.webdriver.support.ui import Select
select = Select(payment_select)
select.select_by_value("0")

# final_submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "f_submit")))
# final_submit_btn.click()

input("Press enter to quit.")
driver.quit()
