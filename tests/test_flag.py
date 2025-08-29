import pytest
import time
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://submit.smartpro.edu.vn/login.php"
USERNAME = "admin"
PASSWORD = "SmartPro@123"

def load_test_data(file_name):
    path = os.path.join(os.path.dirname(__file__), "data", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def open_flags_page(driver):
    driver.get("https://submit.smartpro.edu.vn/flag.php")
    WebDriverWait(driver, 10).until(EC.url_contains("flag.php"))


def open_add_flag_modal(driver):
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-flag-btn"))
    )
    add_btn.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "addFlagModal"))
    )


def fill_add_flag_form(driver, challenge_title, flag_value, description, is_image=False, image_path=None):
    challenge_select = driver.find_element(By.ID, "challenge_id")
    challenge_select.send_keys(challenge_title)

    flag_input = driver.find_element(By.ID, "flag_value")
    flag_input.clear()
    flag_input.send_keys(flag_value)

    desc_input = driver.find_element(By.ID, "description")
    desc_input.clear()
    desc_input.send_keys(description)

    is_image_checkbox = driver.find_element(By.ID, "is_image")
    if is_image:
        if not is_image_checkbox.is_selected():
            is_image_checkbox.click()
        if image_path:
            driver.find_element(By.ID, "flag_image").send_keys(image_path)
    else:
        if is_image_checkbox.is_selected():
            is_image_checkbox.click()


def get_swal_text(driver):
    swal = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "swal2-popup"))
    )
    return swal.text


add_flag_data = load_test_data("flag_test_data.json")["add_flag"]

def parse_description(desc):
    """Nếu desc là object có repeat thì nhân chuỗi, ngược lại trả về desc"""
    if isinstance(desc, dict) and "repeat" in desc:
        return desc["text"] * desc["repeat"]
    return desc

@pytest.mark.parametrize("data", add_flag_data)
def test_add_flag(browser, data):
    open_flags_page(browser)
    open_add_flag_modal(browser)

    description = parse_description(data["description"])

    fill_add_flag_form(
        browser,
        data["challenge_title"],
        data["flag_value"],
        description,
        data["is_image"],
        data["image_path"]
    )
    
    browser.find_element(By.NAME, "add_flag").click()
    time.sleep(1)
    
    text = get_swal_text(browser)
    print(f"[KẾT QUẢ MONG ĐỢI]: {data['expected']}")
    print(f"[KẾT QUẢ THỰC TẾ]: {text}")
    
    if data["expected"] == "success":
        assert "Thêm Flag thành công" in text
    else:
        assert "Lỗi" in text or "Vui lòng kiểm tra" in text

    open_flags_page(browser)




# ------------------ EDIT FLAG ------------------
def open_edit_flag_modal(driver):
    """Mở modal chỉnh sửa flag cuối cùng trong bảng."""
    edit_icons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".edit-icon"))
    )
    last_edit_icon = edit_icons[7]  # chọn flag cuối cùng
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_edit_icon)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".edit-icon")))
    ActionChains(driver).move_to_element(last_edit_icon).click().perform()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "editFlagModal"))
    )


def fill_edit_flag_form(driver, challenge_title, flag_value, description, is_image=False, image_path=None):
    driver.find_element(By.ID, "edit_challenge_id").send_keys(challenge_title)
    
    flag_input = driver.find_element(By.ID, "edit_flag_value")
    flag_input.clear()
    flag_input.send_keys(flag_value)
    
    desc_input = driver.find_element(By.ID, "edit_description")
    desc_input.clear()
    desc_input.send_keys(description)
    
    is_image_checkbox = driver.find_element(By.ID, "edit_is_image")
    if is_image and not is_image_checkbox.is_selected():
        is_image_checkbox.click()
        if image_path:
            driver.find_element(By.ID, "edit_flag_image").send_keys(image_path)
    elif not is_image and is_image_checkbox.is_selected():
        is_image_checkbox.click()


edit_flag_data = load_test_data("flag_test_data.json")["edit_flag"]

def parse_description(desc):
    """Nếu desc là object có repeat thì nhân chuỗi, ngược lại trả về desc"""
    if isinstance(desc, dict) and "repeat" in desc:
        return desc["text"] * desc["repeat"]
    return desc

@pytest.mark.parametrize("data", edit_flag_data)
def test_edit_flag(browser, data):
    open_flags_page(browser)
    open_edit_flag_modal(browser)
    
    description = parse_description(data["description"])
    
    fill_edit_flag_form(
        browser,
        data["challenge_title"],
        data["flag_value"],
        description,
        data["is_image"],
        data["image_path"]
    )
    
    browser.find_element(By.NAME, "update_flag").click()
    time.sleep(2)
    
    text = get_swal_text(browser)
    print(f"[KẾT QUẢ MONG ĐỢI]: {data['expected']}")
    print(f"[KẾT QUẢ THỰC TẾ]: {text}")
    
    if data["expected"] == "success":
        assert "Cập nhật Flag thành công" in text
    else:
        assert "Lỗi" in text or "Vui lòng kiểm tra" in text

    open_flags_page(browser)




def delete_flag_by_id(driver, flag_id, page_number=None):
    if page_number:
        driver.get(f"https://submit.smartpro.edu.vn/flag.php?page={page_number}")

    row = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//table//tbody//tr[td[1][normalize-space()='{flag_id}']]"
        ))
    )
    delete_btn = row.find_element(By.CSS_SELECTOR, ".delete-icon")
    
    # Scroll và click an toàn
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_btn)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(delete_btn))
    ActionChains(driver).move_to_element(delete_btn).click().perform()

    confirm_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "swal2-confirm"))
    )
    confirm_btn.click()



delete_flag_data = load_test_data("flag_test_data.json")["delete_flag"]

@pytest.mark.parametrize("data", delete_flag_data)
def test_delete_flag(browser, data):
    open_flags_page(browser)
    
    if data["scenario"] == "valid_delete":
        delete_flag_by_id(browser, data["flag_id"])
        text = get_swal_text(browser)
        assert "Thành công" in text
    
    elif data["scenario"] == "not_exist":
        browser.get(f"https://submit.smartpro.edu.vn/flag.php?delete_flag={data['flag_id']}")
        text = get_swal_text(browser)
        assert "không tồn tại" in text
    
    print(f"[KẾT QUẢ MONG ĐỢI]: {data['expected']}")
    print(f"[KẾT QUẢ THỰC TẾ]: {text}")
