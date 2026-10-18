import unicodedata
import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id",
    ["UNLOCK-06", "UNLOCK-07", "UNLOCK-08"],
)
def test_pinyin_validation(case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    base_url = "http://localhost:3000"
    email = f"unlock.pinyin.{uuid.uuid4().hex[:12]}@example.com"
    option_selector = "button.w-full.text-left"

    try:
        # Chuẩn bị tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Pinyin")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]',
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Lấy dữ liệu Pinyin của ba bài thuộc nhóm 1.
        pinyin_by_word = {}

        for lesson_number in range(1, 4):
            driver.get(
                f"{base_url}/vocabulary/lesson/"
                f"new-1-lesson-{lesson_number}"
            )

            words = wait.until(
                EC.visibility_of_all_elements_located((
                    By.CSS_SELECTOR,
                    "span.hanzi.text-2xl.font-bold",
                ))
            )

            for word in words:
                row = word.find_element(
                    By.XPATH,
                    './ancestor::div[contains(@class,"cursor-pointer")][1]',
                )

                character = word.text.strip()
                pinyin = row.find_element(
                    By.CSS_SELECTOR, "p.font-medium"
                ).text.strip()

                assert character
                assert pinyin

                if character in pinyin_by_word:
                    assert pinyin_by_word[character] == pinyin

                pinyin_by_word[character] = pinyin

        driver.get(
            f"{base_url}/vocabulary/test/new-1-set-1"
        )

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Bắt đầu kiểm tra"]',
            ))
        ).click()

        def options_ready(browser):
            options = browser.find_elements(
                By.CSS_SELECTOR, option_selector
            )

            if len(options) == 4 and all(
                option.is_displayed() and option.is_enabled()
                for option in options
            ):
                return options

            return False

        # Hai câu trắc nghiệm đầu chỉ là bước chuẩn bị.
        for position in (1, 2):
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="{position}/20"]',
                ))
            )

            options = wait.until(options_ready)
            options[0].click()

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)="3/20"]',
            ))
        )

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)="Điền Pinyin"]',
            ))
        )

        field = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="VD: nǐ hǎo …"]',
            ))
        )

        character = driver.find_element(
            By.CSS_SELECTOR,
            "p.hanzi.font-bold.mb-2",
        ).text.strip()

        assert character in pinyin_by_word
        original_pinyin = pinyin_by_word[character]

        # Chuẩn bị chuỗi Pinyin không dấu, không khoảng trắng.
        decomposed = unicodedata.normalize("NFD", original_pinyin)
        without_marks = "".join(
            char for char in decomposed
            if not ("\u0300" <= char <= "\u036f")
        )
        normalized = "".join(without_marks.lower().split())
        assert normalized

        if case_id == "UNLOCK-06":
            submitted_answer = (
                "  " + "  ".join(normalized.upper()) + "  "
            )
            expected_accepted = True
            description = "chuẩn hóa chữ hoa, dấu và khoảng trắng"

        elif case_id == "UNLOCK-07":
            # Thêm một ký tự: khoảng cách chỉnh sửa chính xác bằng 1.
            submitted_answer = normalized + "z"
            expected_accepted = True
            description = "thêm 1 ký tự, được chấp nhận"

        else:
            # Thêm hai ký tự: khoảng cách chỉnh sửa chính xác bằng 2.
            submitted_answer = normalized + "zz"
            expected_accepted = False
            description = "thêm 2 ký tự, bị từ chối"

        field.send_keys(submitted_answer)
        driver.save_screenshot(f"{case_id}-before-submit.png")

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="OK"]',
            ))
        ).click()

        feedback_wait = WebDriverWait(
            driver, 5, poll_frequency=0.05
        )

        if expected_accepted:
            feedback_wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    '//div[normalize-space(.)="✓ Chính xác!"]',
                ))
            )

        else:
            feedback = feedback_wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    '//div[starts-with(normalize-space(.), "✗ Đáp án:")]',
                ))
            )

            assert feedback.text.strip() == (
                f"✗ Đáp án: {original_pinyin}"
            ), feedback.text

            assert not driver.find_elements(
                By.XPATH,
                '//div[normalize-space(.)="✓ Chính xác!"]',
            )

        assert not driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="VD: nǐ hǎo …"]',
        ).is_enabled()

        driver.save_screenshot(f"{case_id}-feedback.png")

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)="4/20"]',
            ))
        )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: chữ {character}; "
            f"Pinyin gốc = {original_pinyin!r}; "
            f"nhập = {submitted_answer!r}; "
            f"{description}; chuyển sang câu 4/20"
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