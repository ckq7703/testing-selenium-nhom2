import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

URL = "https://submit.smartpro.edu.vn/login.php"

# Các bộ dữ liệu test
test_data = [
    # 1. Hợp lệ
    ("admin", "SmartPro@123", True, "Đăng nhập thành công"),
    
    # 2-4. Sai thông tin
    ("admin", "sai_password", False, "Sai mật khẩu"),
    ("sai_admin", "SmartPro@123", False, "Sai username"),
    ("fakeuser", "fakepass", False, "Sai cả username và password"),

    # 5-7. Trường trống
    ("", "SmartPro@123", False, "Bỏ trống username"),
    ("admin", "", False, "Bỏ trống password"),
    ("", "", False, "Bỏ trống cả 2"),

    # 8-9. Độ dài
    ("a" * 256, "SmartPro@123", False, "Username quá dài"),
    ("admin", "a" * 256, False, "Password quá dài"),

    # 10. Ký tự đặc biệt
    ("admin' OR '1'='1", "abc123", False, "Thử SQL injection"),
]

@pytest.mark.parametrize("username,password,expected,desc", test_data)
def test_login(browser, username, password, expected, desc):
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
