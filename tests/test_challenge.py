import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException

BASE_URL = "https://submit.smartpro.edu.vn/login.php"
USERNAME = "admin"
PASSWORD = "SmartPro@123"

@pytest.fixture(scope="session")
def browser():
    driver = webdriver.Chrome()
    driver.maximize_window()

    # --- Đăng nhập ---
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)

    WebDriverWait(driver, 10).until(EC.url_contains("index"))
    yield driver
    driver.quit()

def get_alert_text_and_accept(driver):
    """Nếu có alert thì lấy text rồi accept."""
    try:
        alert = driver.switch_to.alert
        text = alert.text
        alert.accept()
        return text
    except NoAlertPresentException:
        return None
    
def open_challenges_page(browser):
    browser.get("https://submit.smartpro.edu.vn/challenges.php")

    # 🔄 Đợi modal (nếu có) biến mất để tránh bị che
    try:
        WebDriverWait(browser, 3).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "modal-backdrop"))
        )
    except TimeoutException:
        pass

    # 🔄 Đợi alert (nếu có) biến mất
    try:
        WebDriverWait(browser, 3).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert"))
        )
    except TimeoutException:
        pass

    WebDriverWait(browser, 10).until(EC.url_contains("challenges.php"))

def open_add_modal(driver):
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-challenge-btn"))
    )
    add_btn.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "addChallengeModal"))
    )

def fill_form(driver, title, description, guide, points, is_public):
    # Title
    title_input = driver.find_element(By.ID, "title")
    title_input.clear()
    title_input.send_keys(title)

    # Description
    desc_input = driver.find_element(By.ID, "description")
    desc_input.clear()
    desc_input.send_keys(description)

    # Guide (TinyMCE)
    driver.execute_script(f"tinymce.get('guide').setContent(`{guide}`);")

    # Points
    points_input = driver.find_element(By.ID, "points")
    points_input.clear()
    points_input.send_keys(str(points))

    # Checkbox Công khai
    checkbox = driver.find_element(By.ID, "add_public")
    if checkbox.is_selected() != is_public:
        checkbox.click()

def get_validation_message(driver, field_id):
    """Trả về thông báo validation HTML5"""
    return driver.execute_script(
        f"return document.getElementById('{field_id}').validationMessage;"
    )

@pytest.mark.parametrize("title,description,guide,points,is_public,expected", [
    # Hợp lệ
    ("Test1", "Mô tả ngắn", "", 100, False, True),
    # Title required
    ("", "Mô tả", "", 100, False, False),
    ("A"*101, "Mô tả", "", 100, False, False),
    # Description required
    ("Test3", "", "", 100, False, False),
    ("Test4", "A"*1001, "", 100, False, False),
    # Guide dài quá
    ("Test5", "Mô tả", "A"*5001, 100, False, False),
    # Points invalid
    ("Test6", "Mô tả", "", 0, False, False),
    ("Test7", "Mô tả", "", -10, False, False),
    ("Test8", "Mô tả", "", 1001, False, False),
    # Biên
    ("T", "M", "", 1, False, True),
    ("A"*100, "M", "", 10, False, True),
    ("Test9", "D", "", 1000, False, True),
    ("Test10", "A"*1000, "", 100, False, True),
    ("Test11", "M", "", 1, False, True),
    ("Test12", "M", "", 1000, False, True),
])
def test_add_challenge(browser, title, description, guide, points, is_public, expected):
    print(f"\n=== Test case ===")
    print(f"Input: title='{title}', description='{description}', guide='{guide[:50]}...', points={points}, is_public={is_public}")
    print(f"Kết quả mong đợi: {'Thành công' if expected else 'Thất bại'}")

    open_challenges_page(browser)
    open_add_modal(browser)
    fill_form(browser, title, description, guide, points, is_public)

    submit_btn = browser.find_element(By.NAME, "add_challenge")
    submit_btn.click()
    time.sleep(1)

    if expected:
        # ✅ Trường hợp hợp lệ → thông báo thành công
        try:
            success_alert = WebDriverWait(browser, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-success"))
            )
            actual_result = success_alert.text
            print(f"Kết quả thực tế: {actual_result}")
            assert "Thêm thử thách thành công" in actual_result, \
                f"Kết quả mong đợi: 'Thêm thử thách thành công'. Kết quả thực tế: '{actual_result}'"
        except TimeoutException:
            print("Kết quả thực tế: Không tìm thấy alert thành công")
            assert False, "Không tìm thấy alert thành công"
    else:
        # ❌ Trường hợp không hợp lệ
        if title == "":
            msg = get_validation_message(browser, "title")
            print(f"Kết quả thực tế: Validation error - {msg}")
            assert "Please fill out this field" in msg
        elif len(title) > 100:
            alert_text = get_alert_text_and_accept(browser)
            print(f"Kết quả thực tế: JS alert - {alert_text}")
            assert "Tiêu đề bắt buộc và <= 100 ký tự" in alert_text
        elif len(description) > 1000:
            alert_text = get_alert_text_and_accept(browser)
            print(f"Kết quả thực tế: JS alert - {alert_text}")
            assert "Mô tả bắt buộc và <= 1000 ký tự." in alert_text
        elif description == "":
            msg = get_validation_message(browser, "description")
            print(f"Kết quả thực tế: Validation error - {msg}")
            assert "Please fill out this field" in msg
        elif points < 1 or points > 1000:
            alert_text = get_alert_text_and_accept(browser)
            print(f"Kết quả thực tế: JS alert - {alert_text}")
            assert "Điểm số phải từ 1 đến 1000" in alert_text
        else:
            try:
                alert = WebDriverWait(browser, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
                )
                print(f"Kết quả thực tế: Alert danger - {alert.get_attribute('class')}")
                assert "alert" in alert.get_attribute("class")
            except TimeoutException:
                print("Kết quả thực tế: Không tìm thấy alert danger")
                assert False, "Không tìm thấy alert danger"

    # 🔄 Reset lại về trang quản lý thử thách
    open_challenges_page(browser)