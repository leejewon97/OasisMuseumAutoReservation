import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from selenium.webdriver.support.ui import Select
import tkinter.font as tkfont
from tkcalendar import DateEntry
import undetected_chromedriver as uc
from selenium_stealth import stealth

BASE_URL = "https://www.oasismuseum.com/ticket"
THEME_ID = "6"
priority_times = [
    "15:00",
    "13:20",
    "16:40",
    "18:20",
    "20:00",
    "21:40",
    "11:40",
    "10:00"
]

class PrintLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.tag_configure("reserve_number", font=(FONT[0], 24, "bold"), foreground="blue")

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

    def print_reserve_number(self, reserve_number):
        self.text_widget.insert(tk.END, f"예약번호: {reserve_number}\n", "reserve_number")
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def wait_for_alert_or_elements(driver, by, value, multiple=False):
    try:
        alert = driver.switch_to.alert
        return ("alert", alert)
    except:
        pass
    if by and value:
        try:
            if multiple:
                elems = driver.find_elements(by, value)
                if elems:
                    return ("elements", elems)
            else:
                elem = driver.find_element(by, value)
                return ("element", elem)
        except:
            pass
    return False

def handle_wait_result(result, alert_handler):
    if result[0] == "alert":
        alert = result[1]
        alert_text = alert.text
        return alert_handler(alert, alert_text)
    else:
        return result[1]

def safe_find_elements(driver, wait, FULL_URL):
    while True:
        print("페이지 로딩 완료 대기 중...")
        def unavailable_date_alert_handler(alert, alert_text):
            print(f"알림창 발견: {alert_text}")
            alert.accept()
            print("예약 불가능한 날짜입니다. 1초 후 다시 접속...")
            time.sleep(1)
            driver.get(FULL_URL)
            return None
        try:
            result = wait.until(lambda d: wait_for_alert_or_elements(d, By.CSS_SELECTOR, "button.btn-opened, button.btn-closed", multiple=True))
            buttons = handle_wait_result(result, unavailable_date_alert_handler)
            if buttons is None:
                continue
        except TimeoutException:
            print("30초 대기 후에도 페이지가 로드되지 않음. 새로고침...")
            driver.refresh()
            continue
        active_btns = [btn for btn in buttons if 'btn-opened' in btn.get_attribute('class')]
        if active_btns:
            print(f"예약 가능한 시간 {len(active_btns)}개 발견!")
            return active_btns
        print("예약 가능한 시간이 없습니다. 1초 후 새로고침...")
        time.sleep(1)
        driver.refresh()

driver = None

def start_reservation(name, phone, date):
    global driver
    try:
        print(f"예약자 이름: {name}")
        print(f"전화번호: {phone}")
        print(f"예약 날짜: {date}")
        FULL_URL = f"{BASE_URL}?date={date}&id={THEME_ID}"
        driver = uc.Chrome(headless=True)
        stealth(driver,
            languages=["ko-KR", "ko"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        driver.get(FULL_URL)
        wait = WebDriverWait(driver, 30)
        available_time_buttons = safe_find_elements(driver, wait, FULL_URL)

        print("예약 가능한 시간:")
        for btn in available_time_buttons:
            print(btn.text.strip())
        reserved = False
        for target_time in priority_times:
            for btn in available_time_buttons:
                if target_time in btn.text:
                    btn.click()
                    print(f"{target_time} 클릭 완료")
                    reserved = True
                    break
            if reserved:
                break
        
        name_input = wait.until(EC.presence_of_element_located((By.ID, "f_name")))
        name_input.clear()
        name_input.send_keys(name)
        
        phone_input = wait.until(EC.presence_of_element_located((By.ID, "f_tel")))
        phone_input.clear()
        phone_input.send_keys(phone)
        
        agree_checkbox = wait.until(EC.presence_of_element_located((By.ID, "f_agree")))
        if not agree_checkbox.is_selected():
            agree_checkbox.click()
        
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "f_submit")))
        submit_btn.click()

        def reserved_time_alert_handler(alert, alert_text):
            print(f"알림창 발견: {alert_text}")
            if "이미 예약된 테마 시간표입니다" in alert_text:
                alert.accept()
                print("이미 예약된 시간, 재시도합니다.")
                driver.quit()
                start_reservation(name, phone, date)
            return None

        result = wait.until(lambda d: wait_for_alert_or_elements(d, By.ID, "f_payment"))
        payment_select = handle_wait_result(result, reserved_time_alert_handler)
        if payment_select is None:
            return

        select = Select(payment_select)
        select.select_by_value("0")
        print("결제수단(현금) 선택 완료")
        final_submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "f_submit")))
        final_submit_btn.click()

        result = wait.until(lambda d: wait_for_alert_or_elements(d, By.XPATH, "//div[contains(text(), '예약번호')]/following-sibling::*[1][@class='col-8']"))
        reserve_number_div = handle_wait_result(result, reserved_time_alert_handler)
        if reserve_number_div is None:
            return

        reserve_number = reserve_number_div.get_attribute('innerHTML').strip()
        if reserve_number:
            sys.stdout.print_reserve_number(reserve_number)
        else:
            print("예약번호를 찾을 수 없습니다.")
            try:
                print("예약 완료 페이지 HTML 일부:")
                print(driver.page_source[:20000])
            except Exception as e2:
                print(f"HTML 출력 중 오류: {e2}")
        print("자동 예매 완료!")
        driver.quit()
    except Exception as e:
        print(f"오류 발생: {e}")
        try:
            if driver:
                driver.quit()
        except:
            pass

NAME_HINT = "박선아"
PHONE_HINT = "01012340422"

def set_placeholder(entry, hint):
    entry.insert(0, hint)
    entry.config(fg="gray")

def clear_placeholder(event, entry, hint):
    if entry.get() == hint:
        entry.delete(0, tk.END)
        entry.config(fg="black")

def restore_placeholder(event, entry, hint):
    if not entry.get():
        entry.insert(0, hint)
        entry.config(fg="gray")

def on_start():
    name = entry_name.get()
    phone = entry_phone.get()
    date = entry_date.get()
    if entry_name.cget("fg") == "gray":
        name = ""
    if entry_phone.cget("fg") == "gray":
        phone = ""
    if not name or not phone:
        messagebox.showwarning("입력 오류", "이름과 전화번호를 모두 입력하세요.")
        return
    if not (phone.isdigit() and phone.startswith("010") and 10 <= len(phone) <= 11):
        messagebox.showwarning("입력 오류", "전화번호는 010으로 시작하고, 숫자만 입력하며, 10~11자리여야 합니다.")
        return
    btn_start.config(state=tk.DISABLED)
    threading.Thread(target=lambda: [start_reservation(name, phone, date), btn_start.config(state=tk.NORMAL)], daemon=True).start()

def on_close():
    if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
        try:
            if driver:
                driver.quit()
        except:
            pass
        root.destroy()
        sys.exit(0)

root = tk.Tk()
root.title("채재선정 전율미궁 프리퀄 자동 예매")
root.iconbitmap(resource_path("my_icon.ico"))
root.geometry("400x400")
root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - (500 // 2)
y = (root.winfo_screenheight() // 2) - (400 // 2)
root.geometry(f"400x400+{x}+{y}")

frame = tk.Frame(root)
frame.pack(pady=10)

FONT = (tkfont.nametofont("TkDefaultFont").actual()["family"], 12)
ENTRY_WIDTH = 12

tk.Label(frame, text="이름:", font=FONT).grid(row=0, column=0, sticky="e")
entry_name = tk.Entry(frame, font=FONT, width=ENTRY_WIDTH, justify="center")
entry_name.grid(row=0, column=1, padx=5, sticky="w")
set_placeholder(entry_name, NAME_HINT)
entry_name.bind("<FocusIn>", lambda e: clear_placeholder(e, entry_name, NAME_HINT))
entry_name.bind("<FocusOut>", lambda e: restore_placeholder(e, entry_name, NAME_HINT))

tk.Label(frame, text="전화번호:", font=FONT).grid(row=1, column=0, sticky="e")
entry_phone = tk.Entry(frame, font=FONT, width=ENTRY_WIDTH, justify="center")
entry_phone.grid(row=1, column=1, padx=5, sticky="w")
set_placeholder(entry_phone, PHONE_HINT)
entry_phone.bind("<FocusIn>", lambda e: clear_placeholder(e, entry_phone, PHONE_HINT))
entry_phone.bind("<FocusOut>", lambda e: restore_placeholder(e, entry_phone, PHONE_HINT))

tk.Label(frame, text="날짜:", font=FONT).grid(row=2, column=0, sticky="e")
entry_date = DateEntry(frame, font=FONT, date_pattern="yyyy-mm-dd", state="readonly", width=ENTRY_WIDTH, justify="center")
entry_date.grid(row=2, column=1, padx=5, sticky="w")

btn_start = tk.Button(root, text="예매 시작", command=on_start, font=FONT)
btn_start.pack(pady=5)

log_text = ScrolledText(root, height=15, font=FONT)
log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)

sys.stdout = PrintLogger(log_text)
sys.stderr = PrintLogger(log_text)

root.mainloop()
