import pytest
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

URL = "https://submit.smartpro.edu.vn/login.php"

from utils import load_test_data  # <-- import hàm đọc json

login_data = load_test_data("login_test_data.json")["login"]

@pytest.mark.parametrize("data", login_data)
def test_login(browser, data):
    username = data["username"]
    password = data["password"]
    expected = data["expected"]
    desc = data["desc"]

    browser.get(URL)

    # Điền username
    user_input = browser.find_element(By.ID, "username")
    user_input.clear()
    user_input.send_keys(username)

    # Điền password
    pass_input = browser.find_element(By.ID, "password")
    pass_input.clear()
    pass_input.send_keys(password)

    # Submit form
    pass_input.send_keys(Keys.RETURN)
    time.sleep(2)

    current_url = browser.current_url.lower()

    # In ra thông tin test
    print(f"\n[Test case]: {desc}")
    print(f"[Username]: {username} | [Password]: {password}")
    print(f"[Expected]: {'Đăng nhập thành công' if expected else 'Đăng nhập thất bại'}")
    print(f"[Actual URL]: {current_url}")

    if expected:
        assert "index" in current_url, f"Fail: {desc}"
    else:
        assert "login" in current_url, f"Fail: {desc}"
