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
    fill_add_user_form(browser, data["username"], data["password"], data["role"])

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


def open_edit_user_modal(driver, user_row_index=1):
    edit_icons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".edit-icon"))
    )
    edit_icons[user_row_index].click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "editUserModal"))
    )


def fill_edit_user_form(driver, username, password, role):
    uname_input = driver.find_element(By.ID, "edit_username")
    uname_input.clear()
    uname_input.send_keys(username)

    pwd_input = driver.find_element(By.ID, "edit_password")
    pwd_input.clear()
    pwd_input.send_keys(password)

    role_select = driver.find_element(By.ID, "edit_role")
    role_select.send_keys(role)


@pytest.mark.parametrize("data", user_test_data["edit_user"])
def test_edit_user(browser, data):
    open_users_page(browser)
    open_edit_user_modal(browser)

    fill_edit_user_form(browser, data["username"], data["password"], data["role"])
    browser.find_element(By.NAME, "update_user").click()
    time.sleep(2)

    text = get_swal_text(browser)
    print(f"[MONG ĐỢI]: {data['expected']}")
    print(f"[THỰC TẾ]: {text}")

    if data["expected"] == "success":
        assert "Cập nhật người dùng thành công" in text
    else:
        assert "Lỗi" in text

    open_users_page(browser)


def delete_user_by_name(driver, username, page_number=None):
    if page_number:
        driver.get(f"https://submit.smartpro.edu.vn/users.php?page={page_number}")

    row = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//table//tbody//tr[td[2][normalize-space()='{username}']]"
        ))
    )
    delete_btn = row.find_element(By.CSS_SELECTOR, ".delete-icon")
    driver.execute_script("arguments[0].scrollIntoView(true);", delete_btn)
    delete_btn.click()

    confirm_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "swal2-confirm"))
    )
    confirm_btn.click()


@pytest.mark.parametrize("data", user_test_data["delete_user"])
def test_delete_user(browser, data):
    open_users_page(browser)
    scenario = data["scenario"]

    if scenario == "valid_delete":
        delete_user_by_name(browser, data["username"], page_number=data.get("page_number"))
        text = get_swal_text(browser)
        assert "Thành công" in text

    elif scenario == "self_delete":
        delete_user_by_name(browser, data["username"], page_number=data.get("page_number"))
        text = get_swal_text(browser)
        assert "Không thể xóa" in text

    elif scenario == "not_exist":
        browser.get(f"https://submit.smartpro.edu.vn/users.php?delete_user={data['user_id']}")
        text = get_swal_text(browser)
        assert "không tồn tại" in text

    print(f"[MONG ĐỢI]: {data['expected']}")
    print(f"[THỰC TẾ]: {text}")

