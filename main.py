# ...existing code...
from selenium import webdriver
from selenium.webdriver.chrome.service import Service  
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

import pyautogui
import pykakasi
import keyboard
import time
import os
import sys

# ...existing code...
# ---------- Configuration ----------
chrome_driver_path = r"C:\code\chromedriver-win64\chromedriver.exe"  # full path to chromedriver.exe
if not os.path.isfile(chrome_driver_path):
    # fallback to chromedriver from PATH if explicit path not found
    chrome_driver_path = None

from selenium.webdriver.chrome.options import Options
options = Options()
# Optional: remove or comment out the next line in production
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
options.add_argument("--enable-logging")
options.add_argument("--v=1")

service = Service(executable_path=chrome_driver_path) if chrome_driver_path else Service()
kks = pykakasi.kakasi()
driver = webdriver.Chrome(service=service, options=options)
WAIT = WebDriverWait(driver, 10)
# ...existing code...

def switch_to_typing_iframe():
    """Switch context to iframe with ID 'typing_content' if available."""
    try:
        WAIT.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "typing_content")))
        return True
    except Exception:
        return False

def typing_kana():
    if not switch_to_typing_iframe():
        return
    try:
        while True:
            sentence_text_element = WAIT.until(EC.presence_of_element_located((By.ID, "kanaText")))
            text_content = sentence_text_element.text
            converted = kks.convert(text_content)
            hepburn_text = "".join(token.get("hepburn", token.get("hira", "")) for token in converted)
            if hepburn_text:
                print(hepburn_text)
                try:
                    sentence_text_element.click()
                except Exception:
                    pass
                for ch in hepburn_text:
                    if keyboard.is_pressed('space'):
                        print("Break key pressed. Returning...")
                        return
                    pyautogui.press(ch)
            if keyboard.is_pressed('space'):
                print("Break key pressed. Returning...")
                return
    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

def typing_romaji():
    try:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        if not switch_to_typing_iframe():
            return

        while True:
            sentence_text_element = WAIT.until(EC.presence_of_element_located((By.ID, "sentenceText")))
            text_content = sentence_text_element.text
            try:
                sentence_text_element.click()
            except Exception:
                pass

            for ch in text_content:
                if keyboard.is_pressed('space'):
                    print("Break key pressed. Returning...")
                    return
                pyautogui.press(ch)
                time.sleep(0.08)
    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass

if __name__ == "__main__":
    driver.maximize_window()
    driver.get('https://www.e-typing.ne.jp/roma/check/')

    # Prefer reading credentials from environment variables; fallback to hardcoded values if necessary
    email = os.environ.get("ETYPING_EMAIL", "tuong.lm225949@sis.hust.edu.vn")
    password = os.environ.get("ETYPING_PASSWORD", "tuongiang")

    email_field = WAIT.until(EC.presence_of_element_located((By.ID, "mail")))
    email_field.send_keys(email)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    login_button = driver.find_element(By.ID, "login_btn")
    login_button.click()
    # wait for next page / element
    time.sleep(3)

    try:
        check_button = WAIT.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#level_check_member a")))
        driver.execute_script("arguments[0].scrollIntoView(true);", check_button)
        driver.execute_script("arguments[0].click();", check_button)
    except Exception as e:
        print(f"Error clicking the button: {e}")

    try:
        if switch_to_typing_iframe():
            start_btn = WAIT.until(EC.element_to_be_clickable((By.ID, 'start_btn')))
            start_btn.click()
        else:
            print("Unable to locate typing iframe.")
    except Exception as e:
        print(f"Error interacting with iframe or start button: {e}")

    # Wait for user to press Space to start typing; Space again to stop
    try:
        while True:
            if keyboard.is_pressed('space'):
                print("start")
                time.sleep(0.5)
                typing_romaji()
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupted by user.")

    input("Press Enter to close...")
    driver.quit()
# ...existing code...