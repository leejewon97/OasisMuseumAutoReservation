from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.oasismuseum.com/ticket?date=2025-07-17&id=6")
wait = WebDriverWait(driver, 30)

def safe_find_elements():
    for attempt in range(3):
        try:
            return wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.btn-opened:not([disabled])"))
            )
        except TimeoutException:
            if attempt < 2:
                print(f"시도 {attempt + 1} 실패, 재시도 중...")
                driver.refresh()
                time.sleep(3)
            else:
                raise

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
