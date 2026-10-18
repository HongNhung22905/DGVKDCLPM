import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_lower_retry_preserves_unlock():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "UNLOCK-05"
    base_url = "http://localhost:3000"
    email = f"unlock.retry.{uuid.uuid4().hex[:12]}@example.com"
    option_selector = "button.w-full.text-left"

    def visible_text(tag, text):
        return wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
            ))
        )

    def click_text(tag, text):
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//{tag}[normalize-space(.)="{text}"]',
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

    try:
        # Tạo tài khoản mới.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Giữ quyền mở khóa")

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

        # Đọc dữ liệu ba bài thuộc nhóm 1.
        pool = {}

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

                item = {
                    "hanzi": character,
                    "meaning": row.find_element(
                        By.CSS_SELECTOR, "p.line-clamp-1"
                    ).text.strip(),
                    "pinyin": row.find_element(
                        By.CSS_SELECTOR, "p.font-medium"
                    ).text.strip(),
                }

                assert all(item.values())

                if character in pool:
                    assert pool[character] == item

                pool[character] = item

        def answer_round(target_correct, round_number):
            for position in range(1, 21):
                visible_text("span", f"{position}/20")

                should_be_correct = position <= target_correct
                question_type = (position - 1) % 3

                if question_type == 2:
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
                    assert character in pool

                    answer = (
                        pool[character]["pinyin"]
                        if should_be_correct
                        else "z" * 40
                    )
                    field.clear()
                    field.send_keys(answer)
                    click_text("button", "OK")

                else:
                    options = wait.until(options_ready)

                    if question_type == 0:
                        character = driver.find_element(
                            By.CSS_SELECTOR,
                            "p.hanzi.font-bold.mb-3",
                        ).text.strip()
                        assert character in pool
                        expected_answer = pool[character]["meaning"]

                    else:
                        prompt = visible_text(
                            "p", "Chữ Hán nào có nghĩa sau?"
                        )
                        panel = prompt.find_element(By.XPATH, "..")

                        meaning = panel.find_element(
                            By.CSS_SELECTOR,
                            "p.text-xl.font-semibold.mb-2",
                        ).text.strip()
                        pinyin = panel.find_element(
                            By.CSS_SELECTOR, "p.text-base"
                        ).text.strip()

                        matches = [
                            item for item in pool.values()
                            if item["meaning"] == meaning
                            and item["pinyin"] == pinyin
                        ]
                        assert len(matches) == 1, (
                            f"Lượt {round_number}, câu {position}: "
                            "không xác định duy nhất từ đang hỏi."
                        )
                        expected_answer = matches[0]["hanzi"]

                    correct_options = [
                        option for option in options
                        if option.text.strip() == expected_answer
                    ]
                    assert len(correct_options) == 1, (
                        f"Lượt {round_number}, câu {position}: "
                        f"có {len(correct_options)} lựa chọn khớp "
                        f"{expected_answer!r}; các lựa chọn: "
                        f"{[o.text.strip() for o in options]}"
                    )

                    if should_be_correct:
                        chosen = correct_options[0]
                    else:
                        wrong_options = [
                            option for option in options
                            if option.text.strip() != expected_answer
                        ]
                        assert wrong_options
                        chosen = wrong_options[0]

                    chosen.click()

                print(
                    f"Lượt {round_number}, câu {position}/20: "
                    f"{'đúng' if should_be_correct else 'sai'}"
                )

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Làm lại"]',
                ))
            )

            def get_stat(label):
                return driver.find_element(
                    By.XPATH,
                    f'//span[normalize-space(.)="{label}"]/../span[1]',
                ).text.strip()

            visible_text("div", f"{target_correct * 5}%")
            assert get_stat("Tổng câu") == "20"
            assert get_stat("Đúng") == str(target_correct)
            assert get_stat("Sai") == str(20 - target_correct)

        # Lượt đầu đạt đúng ngưỡng 80%.
        driver.get(
            f"{base_url}/vocabulary/test/new-1-set-1"
        )
        click_text("button", "Bắt đầu kiểm tra")

        answer_round(target_correct=16, round_number=1)
        visible_text("p", "Nhóm 2 đã được mở khóa!")
        driver.save_screenshot("UNLOCK-05-first-80.png")

        # Làm lại cùng bài, chỉ đạt 60%.
        click_text("button", "Làm lại")

        answer_round(target_correct=12, round_number=2)
        driver.save_screenshot("UNLOCK-05-retry-60.png")

        # Kết quả lượt này có thể báo chưa đạt.
        # Quyền mở và điểm cao nhất phải kiểm tra tại danh sách.
        click_text("a", "Ôn lại bài")

        wait.until(EC.url_to_be(f"{base_url}/vocabulary"))

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="HSK 1"]]',
            ))
        ).click()

        visible_text("h2", "HSK 1")

        # Bài 4–6 phải tiếp tục mở sau lượt điểm thấp.
        for lesson_number in range(4, 7):
            for mode in ("lesson", "flashcard", "writing", "game"):
                wait.until(
                    EC.visibility_of_element_located((
                        By.CSS_SELECTOR,
                        f'a[href="/vocabulary/{mode}/'
                        f'new-1-lesson-{lesson_number}"]',
                    ))
                )

        # Thanh kiểm tra nhóm 1 phải giữ điểm cao nhất 80%.
        visible_text("span", "Đã qua · 80%")
        visible_text("span", "2 lần thử")

        driver.save_screenshot("UNLOCK-05-preserved-score.png")

        # Xác nhận bài 4 vẫn truy cập được qua liên kết.
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'a[href="/vocabulary/lesson/new-1-lesson-4"]',
            ))
        ).click()

        wait.until(
            EC.url_contains("/vocabulary/lesson/new-1-lesson-4")
        )
        wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold",
            ))
        )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: lượt đầu 80%, làm lại 60%; "
            "giữ điểm cao nhất 80%, ghi 2 lần thử; "
            "bài 4–6 vẫn mở và truy cập được bài 4"
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