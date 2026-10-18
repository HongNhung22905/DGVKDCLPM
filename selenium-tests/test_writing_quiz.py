import uuid

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_wrong_stroke_not_completed():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)
    case_id = "WRITE-06"
    email = f"writing.quiz.{uuid.uuid4().hex[:12]}@example.com"

    def button(label):
        return (
            By.XPATH,
            f'//button[normalize-space(.)="{label}"]'
        )

    try:
        # Chuẩn bị tài khoản mới.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Nét viết")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        driver.get(
            "http://localhost:3000/vocabulary/writing/new-1-lesson-1"
        )

        wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-2"
            ))
        )

        first_word = driver.find_element(
            By.CSS_SELECTOR, "p.hanzi.font-bold.mb-2"
        ).text.strip()

        wait.until(
            EC.element_to_be_clickable(button("Kiểm tra nét"))
        ).click()

        wait.until(
            EC.element_to_be_clickable(button("Tự viết"))
        )

        # Chờ dữ liệu nét thực sự được tải.
        WebDriverWait(driver, 60).until(
            lambda browser: any(
                path.get_attribute("d")
                for path in browser.find_elements(
                    By.CSS_SELECTOR,
                    'svg[width="260"][height="260"] path'
                )
            )
        )

        # Khởi động lại quiz trước khi vẽ.
        wait.until(
            EC.element_to_be_clickable(button("Tự viết"))
        ).click()

        canvas = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                'svg[width="260"][height="260"]'
            ))
        )

        # Cuộn vùng vẽ vào màn hình trước khi thao tác chuột thật.
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            canvas
        )

        # Vẽ 3 đường ngắn ở góc trên trái, ngoài hình chữ.
        # Offset được tính từ tâm SVG 260x260.
        for offset_y in (-115, -105, -95):
            (
                ActionChains(driver)
                .move_to_element_with_offset(canvas, -115, offset_y)
                .click_and_hold()
                .move_by_offset(10, 0)
                .move_by_offset(10, 0)
                .release()
                .perform()
            )

        # Theo dõi trong 2 giây để bắt cả cập nhật hoàn thành trễ.
        # Assertion trong mỗi lần poll sẽ làm test fail ngay nếu sai.
        def remains_incomplete(browser):
            current_word = browser.find_element(
                By.CSS_SELECTOR,
                "p.hanzi.font-bold.mb-2"
            ).text.strip()

            assert current_word == first_word, (
                "Hệ thống chuyển chữ sau khi chỉ vẽ các nét sai."
            )

            assert browser.find_element(
                By.XPATH,
                '//span[normalize-space(.)="0/20"]'
            ).is_displayed(), "Tiến độ tăng sau khi chỉ vẽ các nét sai."

            assert not browser.find_elements(
                By.XPATH,
                '//span[contains(normalize-space(.), "Đã viết xong")]'
            ), "Hệ thống đánh dấu hoàn thành sau các nét sai."

            assert not browser.find_elements(
                By.XPATH,
                '//*[normalize-space(.)="✓ Xuất sắc! Thứ tự nét đúng"]'
            ), "Hệ thống báo thành công sau các nét sai."

            return False

        from selenium.common.exceptions import TimeoutException

        try:
            WebDriverWait(
                driver, 2, poll_frequency=0.2
            ).until(remains_incomplete)
        except TimeoutException:
            # Hết khoảng theo dõi và không assertion nào thất bại.
            pass

        assert driver.find_element(
            *button("Tự viết")
        ).is_enabled()

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: vẽ 3 đường sai ngoài hình chữ; "
            f"vẫn ở chữ {first_word}; tiến độ 0/20; "
            "không báo thành công hoặc đánh dấu hoàn thành"
        )

    except Exception:
        try:
            driver.save_screenshot(f"{case_id}-fail.png")
        except Exception as error:
            print(f"\nKhông chụp được ảnh: {error}")
        raise

    finally:
        try:
            driver.quit()
        except Exception:
            pass