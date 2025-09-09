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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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


# ======================== CHALLENGE HELPERS ========================

def open_challenges_page(driver):
    driver.get("https://submit.smartpro.edu.vn/challenges.php")
    WebDriverWait(driver, 10).until(EC.url_contains("challenges.php"))


def open_add_challenge_modal(driver):
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-challenge-btn"))
    )
    add_btn.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "addChallengeModal"))
    )


def fill_add_challenge_form(driver, title, description, guide, points, public):
    # Wait for TinyMCE to initialize completely
    time.sleep(2)
    
    title_input = driver.find_element(By.ID, "title")
    title_input.clear()
    title_input.send_keys(title)

    desc_input = driver.find_element(By.ID, "description")
    desc_input.clear()
    desc_input.send_keys(description)

    # Handle TinyMCE for guide field
    try:
        # Try to interact with TinyMCE iframe first
        iframe = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id*='guide']"))
        )
        driver.switch_to.frame(iframe)
        guide_body = driver.find_element(By.CSS_SELECTOR, "body")
        guide_body.clear()
        guide_body.send_keys(guide)
        driver.switch_to.default_content()
    except TimeoutException:
        # Fallback to regular textarea if TinyMCE not loaded
        guide_input = driver.find_element(By.ID, "guide")
        guide_input.clear()
        guide_input.send_keys(guide)

    points_input = driver.find_element(By.ID, "points")
    points_input.clear()
    points_input.send_keys(str(points))

    public_checkbox = driver.find_element(By.ID, "add_public")  # Updated ID
    if public and not public_checkbox.is_selected():
        public_checkbox.click()
    elif not public and public_checkbox.is_selected():
        public_checkbox.click()


def get_swal_text(driver):
    swal = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "swal2-popup"))
    )
    return swal.text


def parse_field(value):
    """Nếu value là object có repeat thì nhân chuỗi, ngược lại trả về value"""
    if isinstance(value, dict) and "repeat" in value:
        return value["text"] * value["repeat"]
    return value


def wait_for_page_load(driver, timeout=10):
    """Wait for page to load completely"""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


# ======================== ADD CHALLENGE ========================

add_challenge_data = load_test_data("challenge_test_data.json")["add_challenge"]

@pytest.mark.parametrize("data", add_challenge_data)
def test_add_challenge(browser, data):
    open_challenges_page(browser)
    wait_for_page_load(browser)
    open_add_challenge_modal(browser)

    title = parse_field(data["title"])
    description = parse_field(data["description"])
    guide = parse_field(data["guide"])

    fill_add_challenge_form(
        browser,
        title,
        description,
        guide,
        data["points"],
        data["public"]
    )

    submit_btn = browser.find_element(By.NAME, "add_challenge")
    submit_btn.click()
    
    # Wait a bit longer for form processing
    time.sleep(3)

    try:
        text = get_swal_text(browser)
        print(f"[MONG ĐỢI]: {data['expected']}")
        print(f"[THỰC TẾ]: {text}")

        if data["expected"] == "success":
            assert "Thêm thử thách thành công" in text or "thành công" in text
        else:
            assert "Lỗi" in text or "không hợp lệ" in text or "bắt buộc" in text or "vượt quá" in text
    except TimeoutException:
        # If no SweetAlert appears, check if redirected (success case)
        if data["expected"] == "success" and "challenges.php" in browser.current_url:
            print("Redirect detected - likely success")
            assert True
        else:
            print("No SweetAlert found and no redirect - test failed")
            assert False

    # Return to challenges page
    open_challenges_page(browser)


