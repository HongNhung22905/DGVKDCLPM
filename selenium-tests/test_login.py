import pytest
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.parametrize(
    "case_id, uppercase_email, refresh_page",
    [
        pytest.param("LOGIN-01", False, False, id="LOGIN-01"),
        pytest.param("LOGIN-07", True, False, id="LOGIN-07"),
        pytest.param("LOGIN-08", False, True, id="LOGIN-08"),
    ],
)
def test_login_valid(case_id, uppercase_email, refresh_page):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)
    email = "selenium.09b083baae11@example.com"

    try:
        driver.get("http://localhost:3000/login")

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[type="email"]')
            )
        ).send_keys(email.upper() if uppercase_email else email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))
        if refresh_page:
            driver.refresh()
            wait.until(
                EC.visibility_of_element_located((By.TAG_NAME, "body"))
            )
        cookie = driver.get_cookie("hsk_token")
        assert cookie is not None, "Không có cookie đăng nhập"
        assert cookie.get("httpOnly"), "Cookie thiếu HttpOnly"

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
        assert result["body"]["user"]["email"] == email, result

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: đăng nhập và xác minh phiên thành công")

    except Exception:
        driver.save_screenshot(f"{case_id}-fail.png")
        raise

    finally:
        driver.quit()



@pytest.mark.parametrize(
    "case_id, use_existing_email",
    [
        pytest.param("LOGIN-02", True, id="LOGIN-02"),
        pytest.param("LOGIN-03", False, id="LOGIN-03"),
    ],
)
def test_login_invalid_credentials(case_id, use_existing_email):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    email = (
        "selenium.09b083baae11@example.com"
        if use_existing_email
        else f"notfound.{uuid.uuid4().hex}@example.com"
    )

    try:
        driver.get("http://localhost:3000/login")

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[type="email"]')
            )
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("WrongPassword@123")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        error = wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//form//p[normalize-space(.)='
                '"Email hoặc mật khẩu không đúng."]'
            ))
        )

        assert error.text == "Email hoặc mật khẩu không đúng."
        assert "/login" in driver.current_url
        assert driver.get_cookie("hsk_token") is None

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: từ chối thông tin đăng nhập sai")

    except Exception:
        driver.save_screenshot(f"{case_id}-fail.png")
        raise

    finally:
        driver.quit()



@pytest.mark.parametrize(
    "case_id, email, password, selector, flag",
    [
        pytest.param(
            "LOGIN-04", "", "1234567",
            'input[type="email"]',
            "valueMissing", id="LOGIN-04"
        ),
        pytest.param(
            "LOGIN-05", "selenium.09b083baae11@example.com", "",
            'input[placeholder="Ít nhất 6 ký tự"]',
            "valueMissing", id="LOGIN-05"
        ),
        pytest.param(
            "LOGIN-06", "abc", "1234567",
            'input[type="email"]',
            "typeMismatch", id="LOGIN-06"
        ),
    ],
)
def test_login_invalid_input(case_id, email, password, selector, flag):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("http://localhost:3000/login")

        email_input = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[type="email"]')
            )
        )

        if email:
            email_input.send_keys(email)

        if password:
            driver.find_element(
                By.CSS_SELECTOR,
                'input[placeholder="Ít nhất 6 ký tự"]'
            ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        field = driver.find_element(By.CSS_SELECTOR, selector)

        validation = driver.execute_script("""
            return {
                invalid: !arguments[0].validity.valid,
                expectedFlag: arguments[0].validity[arguments[1]],
                message: arguments[0].validationMessage,
                focused: document.activeElement === arguments[0]
            };
        """, field, flag)

        assert validation["invalid"], validation
        assert validation["expectedFlag"], validation
        assert validation["message"], validation
        assert validation["focused"], validation
        assert "/login" in driver.current_url
        assert driver.get_cookie("hsk_token") is None

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: {validation['message']}")

    except Exception:
        driver.save_screenshot(f"{case_id}-fail.png")
        raise

    finally:
        driver.quit()