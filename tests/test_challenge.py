import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

URL = "https://submit.smartpro.edu.vn/login.php"

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

def test_add_challenge(browser):
    # --- Bước 1: Login ---
    browser.get(URL)
    browser.find_element(By.ID, "username").send_keys("admin")
    browser.find_element(By.ID, "password").send_keys("SmartPro@123" + Keys.RETURN)

    WebDriverWait(browser, 10).until(
        EC.url_contains("index")
    )

    # --- Bước 2: Mở menu QUẢN LÝ → Quản lý Thử thách ---
    menu = browser.find_element(By.LINK_TEXT, "QUẢN LÝ")
    menu.click()

    challenge_menu = browser.find_element(By.LINK_TEXT, "Quản lý Thử thách")
    challenge_menu.click()

    WebDriverWait(browser, 10).until(
        EC.url_contains("challenges.php")
    )

    # --- Bước 3: Nhấn nút "Thêm Thử Thách" ---
    add_btn = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".add-challenge-btn"))
    )
    add_btn.click()

    # --- Bước 4: Điền form trong modal ---
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "addChallengeModal"))
    )

    browser.find_element(By.ID, "title").send_keys("Thử thách tự động")
    browser.find_element(By.ID, "description").send_keys("Mô tả thử thách tự động")
    browser.find_element(By.ID, "guide").send_keys("<p>Hướng dẫn test</p>")
    browser.find_element(By.ID, "points").clear()
    browser.find_element(By.ID, "points").send_keys("200")

    # --- Bước 5: Submit form ---
    browser.find_element(By.NAME, "add_challenge").click()

    time.sleep(2)

    # --- Bước 6: Kiểm tra thử thách đã xuất hiện trong danh sách ---
    page_source = browser.page_source
    assert "Thử thách tự động" in page_source
