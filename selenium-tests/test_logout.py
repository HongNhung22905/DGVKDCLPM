from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_api(driver, path):
    driver.set_script_timeout(30)
    return driver.execute_async_script("""
        const path = arguments[0];
        const done = arguments[arguments.length - 1];

        fetch(path, { credentials: "include", cache: "no-store" })
            .then(async response => done({
                status: response.status,
                body: await response.json()
            }))
            .catch(error => done({ error: String(error) }));
    """, path)


def test_logout():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)
    email = "selenium.09b083baae11@example.com"

    try:
        # Đăng nhập để chuẩn bị phiên.
        driver.get("http://localhost:3000/login")

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[type="email"]')
            )
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Lấy tên tài khoản từ phiên đã xác thực.
        before = get_api(driver, "/api/auth/me")
        assert before.get("status") == 200, before
        assert before["body"]["user"]["email"] == email, before
        name = before["body"]["user"]["name"]

        # Chứng minh API cá nhân truy cập được trước đăng xuất.
        progress_before = get_api(driver, "/api/progress/lesson")
        assert progress_before.get("status") == 200, progress_before

        # Mở menu tài khoản bằng tên hiển thị.
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[.//span[normalize-space(.)="{name}"]]'
            ))
        ).click()

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Đăng xuất"]'
            ))
        ).click()

        # Chờ cookie bị xóa và giao diện trở về trạng thái khách.
        wait.until(lambda browser:
                   browser.get_cookie("hsk_token") is None)

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//a[@href="/login" and '
                'normalize-space(.)="Đăng nhập"]'
            ))
        )

        after = get_api(driver, "/api/auth/me")
        assert after.get("status") == 401, after

        progress_after = get_api(driver, "/api/progress/lesson")
        assert progress_after.get("status") == 401, progress_after

        driver.save_screenshot("LOGOUT-01-pass.png")
        print("\nLOGOUT-01: đăng xuất thành công; API cá nhân trả 401")

    except Exception:
        driver.save_screenshot("LOGOUT-01-fail.png")
        raise

    finally:
        driver.quit()