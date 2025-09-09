import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import load_test_data  # <-- import hàm đọc json

BASE_URL = "https://submit.smartpro.edu.vn/login.php"
USERNAME = "admin"
PASSWORD = "SmartPro@123"

def parse_field(value):
    """Nếu value là object có repeat thì nhân chuỗi, ngược lại trả về value"""
    if isinstance(value, dict) and "repeat" in value:
        return value["text"] * value["repeat"]
    return value

@pytest.fixture(scope="session")
def browser():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(BASE_URL)
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.url_contains("index"))
    yield driver
    driver.quit()


def open_users_page(driver):
    driver.get("https://submit.smartpro.edu.vn/users.php")
    WebDriverWait(driver, 10).until(EC.url_contains("users.php"))


def open_add_user_modal(driver):
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-user-btn"))
    )
    add_btn.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "addUserModal"))
    )


def fill_add_user_form(driver, username, password, role):
    uname_input = driver.find_element(By.ID, "username")
    uname_input.clear()
    uname_input.send_keys(username)

    pwd_input = driver.find_element(By.ID, "password")
    pwd_input.clear()
    pwd_input.send_keys(password)

    role_select = driver.find_element(By.ID, "role")
    role_select.send_keys(role)


def get_swal_text(driver):
    swal = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "swal2-popup"))
    )
    return swal.text


# --- Load dữ liệu JSON ---
user_test_data = load_test_data("user_test_data.json")


@pytest.mark.parametrize("data", user_test_data["add_user"])
def test_add_user(browser, data):
    open_users_page(browser)
    open_add_user_modal(browser)
    
    password = parse_field(data["password"])

    fill_add_user_form(browser, data["username"], password, data["role"])


    browser.find_element(By.NAME, "add_user").click()
    time.sleep(1)

    text = get_swal_text(browser)
    print(f"[MONG ĐỢI]: {data['expected']}")
    print(f"[THỰC TẾ]: {text}")

    if data["expected"] == "success":
        assert "Thêm người dùng thành công" in text
    else:
        assert ("Lỗi" in text or "Vui lòng kiểm tra" in text or "Username đã tồn tại" in text)

    open_users_page(browser)


