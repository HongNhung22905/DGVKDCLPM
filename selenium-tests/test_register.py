import uuid
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.parametrize(
    "password, case_id",
    [
        pytest.param("123456", "REG-01", id="REG-01"),
        pytest.param("1234567", "REG-06", id="REG-06"),
    ],
)
def test_register_valid(password, case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    # Email mới cho mỗi lần chạy, tránh trùng tài khoản.
    email = f"selenium.{uuid.uuid4().hex[:12]}@example.com"
    name = "Người dùng Selenium"

    try:
        driver.get("http://localhost:3000/register")

        name_input = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[placeholder="Nguyễn Văn A"]')
            )
        )
        name_input.send_keys(name)

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR, 'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        # Đăng ký thành công phải chuyển tới trang từ vựng.
        wait.until(EC.url_contains("/vocabulary"))

        # Cookie đăng nhập phải được tạo.
        cookie = driver.get_cookie("hsk_token")
        assert cookie is not None, "Không tìm thấy cookie đăng nhập"
        assert cookie.get("httpOnly"), "Cookie chưa có HttpOnly"

        # Kiểm tra server nhận diện đúng tài khoản vừa đăng ký.
        driver.set_script_timeout(30)
        result = driver.execute_async_script("""
            const done = arguments[arguments.length - 1];
            fetch("/api/auth/me", { credentials: "include" })
                .then(async response => done({
                    status: response.status,
                    body: await response.json()
                }))
                .catch(error => done({ error: String(error) }));
        """)

        assert result.get("status") == 200, result
        user = result["body"]["user"]
        assert user["email"] == email, result
        assert user["name"] == name, result

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: đăng ký thành công — {email}")

    except Exception:
        driver.save_screenshot(f"{case_id}-fail.png")
        raise

    finally:
        driver.quit()

def test_register_password_5_chars():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[placeholder="Nguyễn Văn A"]')
            )
        ).send_keys("Người dùng kiểm thử")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(f"selenium.{uuid.uuid4().hex[:12]}@example.com")

        driver.find_element(
            By.CSS_SELECTOR, 'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("12345")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        error = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//form//p[contains(., "Mật khẩu phải có ít nhất 6 ký tự.")]'
            ))
        )

        assert error.text == "Mật khẩu phải có ít nhất 6 ký tự."
        assert "/register" in driver.current_url
        assert driver.get_cookie("hsk_token") is None

        driver.save_screenshot("REG-05-pass.png")
        print("\nREG-05: từ chối mật khẩu 5 ký tự")

    except Exception:
        driver.save_screenshot("REG-05-fail.png")
        raise

    finally:
        driver.quit()



@pytest.mark.parametrize(
    "case_id, name, email, password, selector, validity_flag",
    [
        pytest.param(
            "REG-02", "", "valid@example.com", "123456",
            'input[placeholder="Nguyễn Văn A"]',
            "valueMissing", id="REG-02"
        ),
        pytest.param(
            "REG-03", "Người dùng A", "", "123456",
            'input[type="email"]',
            "valueMissing", id="REG-03"
        ),
        pytest.param(
            "REG-04", "Người dùng A", "valid@example.com", "",
            'input[placeholder="Ít nhất 6 ký tự"]',
            "valueMissing", id="REG-04"
        ),
        pytest.param(
            "REG-08", "Người dùng A", "abc", "123456",
            'input[type="email"]',
            "typeMismatch", id="REG-08"
        ),
    ],
)
def test_register_invalid_input(
    case_id, name, email, password, selector, validity_flag
):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("http://localhost:3000/register")

        name_input = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        )

        if name:
            name_input.send_keys(name)

        if email:
            driver.find_element(
                By.CSS_SELECTOR, 'input[type="email"]'
            ).send_keys(email)

        if password:
            driver.find_element(
                By.CSS_SELECTOR,
                'input[placeholder="Ít nhất 6 ký tự"]'
            ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        field = driver.find_element(By.CSS_SELECTOR, selector)

        # Kiểm tra trạng thái validation của trình duyệt.
        validation = driver.execute_script("""
            return {
                invalid: !arguments[0].validity.valid,
                expectedFlag: arguments[0].validity[arguments[1]],
                message: arguments[0].validationMessage,
                focused: document.activeElement === arguments[0]
            };
        """, field, validity_flag)

        assert validation["invalid"], validation
        assert validation["expectedFlag"], validation
        assert validation["message"], validation
        assert validation["focused"], validation

        assert "/register" in driver.current_url
        assert driver.get_cookie("hsk_token") is None

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: {validation['message']}")

    except Exception:
        driver.save_screenshot(f"{case_id}-fail.png")
        raise

    finally:
        driver.quit()


def test_register_duplicate_email():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Người dùng trùng email")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys("selenium.09b083baae11@example.com")

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        error = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//form//p[contains(., "Email này đã được đăng ký.")]'
            ))
        )

        assert error.text == "Email này đã được đăng ký."
        assert "/register" in driver.current_url
        assert driver.get_cookie("hsk_token") is None

        driver.save_screenshot("REG-07-pass.png")
        print("\nREG-07: từ chối email đã đăng ký")

    except Exception:
        driver.save_screenshot("REG-07-fail.png")
        raise

    finally:
        driver.quit()




def test_register_whitespace_name():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)
    email = f"selenium.{uuid.uuid4().hex[:12]}@example.com"

    try:
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("   ")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("123456")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        # Chờ kết quả rõ ràng: bị từ chối hoặc đăng ký thành công.
        def registration_result(browser):
            if "/vocabulary" in browser.current_url:
                return "accepted"

            if browser.get_cookie("hsk_token") is not None:
                return "accepted"

            errors = browser.find_elements(
                By.CSS_SELECTOR, "form p"
            )
            for element in errors:
                if (
                    element.is_displayed()
                    and element.value_of_css_property("color")
                    == "rgba(192, 57, 43, 1)"
                    and element.text.strip()
                ):
                    return "rejected"

            return False

        result = wait.until(registration_result)

        assert result == "rejected", (
            f"REG-09: hệ thống chấp nhận tên chỉ chứa khoảng trắng. "
            f"Email thử nghiệm: {email}; URL: {driver.current_url}"
        )

        assert "/register" in driver.current_url
        assert driver.get_cookie("hsk_token") is None

        driver.save_screenshot("REG-09-pass.png")
        print("\nREG-09: từ chối tên chỉ chứa khoảng trắng")

    except Exception:
        driver.save_screenshot("REG-09-fail.png")
        print(f"\nEmail dùng cho REG-09: {email}")
        raise

    finally:
        driver.quit()