import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id",
    ["WRITE-01", "WRITE-02", "WRITE-03", "WRITE-04", "WRITE-05"]
)
def test_open_writing(case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    lesson_id = "new-1-lesson-1"
    email = f"writing.{uuid.uuid4().hex[:12]}@example.com"

    try:
        # Chuẩn bị tài khoản mới chưa có tiến độ.
        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Luyện viết")

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

        # Lấy dữ liệu bài học để đối chiếu với luyện viết.
        driver.get(
            f"http://localhost:3000/vocabulary/lesson/{lesson_id}"
        )

        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold"
            ))
        )

        total_words = len(words)
        assert total_words == 20, f"Số từ thực tế: {total_words}"

        def read_lesson_word(index):
            word = words[index]
            row = word.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"cursor-pointer")][1]'
            )

            character = word.text.strip()
            pinyin = row.find_element(
                By.CSS_SELECTOR, "p.font-medium"
            ).text.strip()
            meaning = row.find_element(
                By.CSS_SELECTOR, "p.line-clamp-1"
            ).text.strip()

            assert character, f"Từ thứ {index + 1} thiếu chữ Hán."
            assert pinyin, f"Từ thứ {index + 1} thiếu Pinyin."
            assert meaning, f"Từ thứ {index + 1} thiếu nghĩa."

            return character, pinyin, meaning

        first_word, first_pinyin, first_meaning = read_lesson_word(0)
        second_word, second_pinyin, second_meaning = read_lesson_word(1)
        last_word, last_pinyin, last_meaning = read_lesson_word(
            total_words - 1
        )

        # Mở luyện viết từ liên kết trong chi tiết bài học.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/writing/{lesson_id}"]'
            ))
        ).click()

        wait.until(
            EC.url_contains(f"/vocabulary/writing/{lesson_id}")
        )

        heading = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        assert heading.text.startswith("Luyện viết ·"), heading.text

        def button_locator(label):
            return (
                By.XPATH,
                f'//button[normalize-space(.)="{label}"]'
            )

        def click_button(label):
            wait.until(
                EC.element_to_be_clickable(button_locator(label))
            ).click()

        def check_word(expected_word, expected_pinyin, expected_meaning):
            def matches(browser):
                current = browser.find_element(
                    By.CSS_SELECTOR, "p.hanzi.font-bold.mb-2"
                )
                info = current.find_element(By.XPATH, "..")

                return (
                    current.text.strip() == expected_word
                    and info.find_element(
                        By.CSS_SELECTOR, "p.font-semibold.mt-2"
                    ).text.strip() == expected_pinyin
                    and info.find_element(
                        By.CSS_SELECTOR, "p.line-clamp-2"
                    ).text.strip() == expected_meaning
                )

            wait.until(matches)

        def check_zero_completed():
            # Đây là số từ hoàn thành, không phải vị trí từ.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="0/{total_words}"]'
                ))
            )

        def check_navigation(previous_enabled, next_enabled):
            previous = driver.find_element(*button_locator("Trước"))
            next_button = driver.find_element(*button_locator("Tiếp"))

            assert previous.is_enabled() == previous_enabled, (
                "Trạng thái nút Trước không đúng."
            )
            assert next_button.is_enabled() == next_enabled, (
                "Trạng thái nút Tiếp không đúng."
            )

        def select_word(index):
            button = driver.find_elements(
                By.CSS_SELECTOR, "button.hanzi"
            )[index]

            driver.execute_script(
                "arguments[0].scrollIntoView("
                "{block: 'center', inline: 'center'});",
                button
            )

            wait.until(EC.element_to_be_clickable(button)).click()

        def wait_for_stroke_data():
            # SVG 280x280 là lưới nền.
            # SVG 260x260 phải có dữ liệu path của chữ.
            return WebDriverWait(driver, 60).until(
                lambda browser: [
                    path
                    for path in browser.find_elements(
                        By.CSS_SELECTOR,
                        'svg[width="260"][height="260"] path'
                    )
                    if path.get_attribute("d")
                ]
            )

        # Các kiểm tra chung khi mở bài.
        check_word(first_word, first_pinyin, first_meaning)
        check_zero_completed()
        check_navigation(previous_enabled=False, next_enabled=True)

        selectors = driver.find_elements(
            By.CSS_SELECTOR, "button.hanzi"
        )
        assert len(selectors) == total_words
        assert selectors[0].text.strip() == first_word[0]

        for label in ("Tập viết", "Kiểm tra nét", "Xem thứ tự nét"):
            wait.until(
                EC.element_to_be_clickable(button_locator(label))
            )

        strokes = wait_for_stroke_data()

        if case_id == "WRITE-02":
            click_button("Tiếp")

            check_word(second_word, second_pinyin, second_meaning)
            check_zero_completed()
            check_navigation(previous_enabled=True, next_enabled=True)

            click_button("Trước")

            check_word(first_word, first_pinyin, first_meaning)
            check_zero_completed()
            check_navigation(previous_enabled=False, next_enabled=True)

            message = (
                f"Tiếp đến đúng {second_word}; "
                f"Trước về đúng {first_word}; "
                "Pinyin và nghĩa khớp bài học; "
                f"hoàn thành vẫn 0/{total_words}"
            )

        elif case_id == "WRITE-03":
            select_word(total_words - 1)

            check_word(last_word, last_pinyin, last_meaning)
            check_zero_completed()
            check_navigation(previous_enabled=True, next_enabled=False)

            select_word(0)

            check_word(first_word, first_pinyin, first_meaning)
            check_zero_completed()
            check_navigation(previous_enabled=False, next_enabled=True)

            message = (
                f"chọn đúng từ cuối {last_word} "
                f"và từ đầu {first_word}; "
                "Pinyin và nghĩa khớp; "
                "khóa đúng nút Tiếp/Trước ở hai đầu; "
                f"hoàn thành vẫn 0/{total_words}"
            )

        elif case_id == "WRITE-04":
            # Bật gợi ý.
            click_button("Xem gợi ý thứ tự nét")

            wait.until(
                EC.element_to_be_clickable(button_locator("Ẩn gợi ý"))
            )

            wait_for_stroke_data()
            check_word(first_word, first_pinyin, first_meaning)
            check_zero_completed()

            driver.save_screenshot("WRITE-04-hint-on.png")

            # Tắt gợi ý.
            click_button("Ẩn gợi ý")

            wait.until(
                EC.element_to_be_clickable(
                    button_locator("Xem gợi ý thứ tự nét")
                )
            )

            wait_for_stroke_data()
            check_word(first_word, first_pinyin, first_meaning)
            check_zero_completed()
            check_navigation(previous_enabled=False, next_enabled=True)

            message = (
                "bật/tắt gợi ý đổi đúng nhãn nút; "
                "dữ liệu nét vẫn tải; thông tin từ không đổi; "
                f"hoàn thành vẫn 0/{total_words}"
            )

        elif case_id == "WRITE-05":
            # Mặc định ở Tập viết: không có nút Tự viết.
            assert not driver.find_elements(
                *button_locator("Tự viết")
            ), "Nút Tự viết xuất hiện trong chế độ Tập viết."

            # Chuyển sang Kiểm tra nét.
            click_button("Kiểm tra nét")

            wait.until(
                EC.element_to_be_clickable(button_locator("Tự viết"))
            )
            wait_for_stroke_data()

            check_word(first_word, first_pinyin, first_meaning)
            check_zero_completed()

            assert not driver.find_elements(
                By.XPATH,
                '//*[normalize-space(.)="✓ Xuất sắc! Thứ tự nét đúng" '
                'or normalize-space(.)="✗ Thứ tự nét chưa đúng, thử lại"]'
            ), "Có kết quả chấm khi chưa thực hiện viết."

            driver.save_screenshot("WRITE-05-quiz-mode.png")

            # Trở về Tập viết: nút Tự viết phải biến mất.
            click_button("Tập viết")

            wait.until(
                lambda browser: not browser.find_elements(
                    *button_locator("Tự viết")
                )
            )
            wait_for_stroke_data()

            check_word(first_word, first_pinyin, first_meaning)
            check_zero_completed()
            check_navigation(previous_enabled=False, next_enabled=True)

            message = (
                "chuyển Tập viết sang Kiểm tra nét và quay lại; "
                "nút Tự viết xuất hiện đúng chế độ; "
                "chưa viết thì chưa có kết quả chấm; "
                f"hoàn thành vẫn 0/{total_words}"
            )

        else:
            message = (
                f"mở đúng luyện viết; chữ đầu {first_word}; "
                f"{total_words} nút chọn từ; "
                f"hoàn thành 0/{total_words}; "
                f"đã tải SVG với {len(strokes)} phần tử path"
            )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: {message}")

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