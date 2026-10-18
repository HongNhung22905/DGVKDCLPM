import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_unlock_restored_in_new_browser():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    case_id = "UNLOCK-09"
    base_url = "http://localhost:3000"
    email = f"unlock.session.{uuid.uuid4().hex[:12]}@example.com"
    password = "1234567"
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
        # Tạo tài khoản mới trong phiên Chrome thứ nhất.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Khôi phục mở khóa")

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]',
        ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Lấy dữ liệu ba bài để trả lời kiểm tra.
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

        driver.get(
            f"{base_url}/vocabulary/test/new-1-set-1"
        )
        click_text("button", "Bắt đầu kiểm tra")

        # Đúng 16 câu, sai 4 câu -> 80%.
        for position in range(1, 21):
            visible_text("span", f"{position}/20")
            should_be_correct = position <= 16
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
                        f"Câu {position}: không xác định duy nhất từ."
                    )
                    expected_answer = matches[0]["hanzi"]

                correct_options = [
                    option for option in options
                    if option.text.strip() == expected_answer
                ]
                assert len(correct_options) == 1, (
                    f"Câu {position}: có {len(correct_options)} "
                    f"lựa chọn khớp {expected_answer!r}; "
                    f"các lựa chọn: {[o.text.strip() for o in options]}"
                )

                if should_be_correct:
                    selected = correct_options[0]
                else:
                    wrong_options = [
                        option for option in options
                        if option.text.strip() != expected_answer
                    ]
                    assert wrong_options
                    selected = wrong_options[0]

                selected.click()

            print(
                f"Câu {position}/20: "
                f"{'đúng' if should_be_correct else 'sai'}"
            )

        visible_text("div", "80%")
        visible_text("p", "Nhóm 2 đã được mở khóa!")

        # Chỉ đọc API để chờ thao tác lưu nền hoàn thành.
        # Không tạo hoặc sửa kết quả bằng API.
        driver.set_script_timeout(15)

        def server_has_saved_result(browser):
            result = browser.execute_async_script(
                """
                const done = arguments[arguments.length - 1];

                fetch("/api/progress/gate", {
                    credentials: "include",
                    cache: "no-store"
                })
                    .then(async response => {
                        if (!response.ok) {
                            done(false);
                            return;
                        }

                        const data = await response.json();
                        done(
                            Array.isArray(data.gates)
                            && data.gates.some(gate =>
                                gate.setId === "new-1-set-1"
                                && gate.passed === true
                                && gate.score === 80
                            )
                        );
                    })
                    .catch(() => done(false));
                """
            )
            return result is True

        wait.until(server_has_saved_result)
        driver.save_screenshot("UNLOCK-09-before-new-browser.png")

        # Đóng phiên cũ, mở Chrome với hồ sơ tạm mới.
        driver.quit()
        driver = webdriver.Chrome()
        driver.set_window_size(1366, 900)
        wait = WebDriverWait(driver, 30)

        driver.get(f"{base_url}/login")

        # Xác nhận phiên mới không có cookie hoặc cache tiến độ cũ.
        assert driver.get_cookie("hsk_token") is None

        old_progress = driver.execute_script(
            """
            return {
                gate: localStorage.getItem("hsk_gate_v1"),
                lesson: localStorage.getItem("hsk_lesson_progress")
            };
            """
        )
        assert old_progress["gate"] in (None, "{}")
        assert old_progress["lesson"] in (None, "{}")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 'input[type="email"]'
            ))
        ).send_keys(email)

        driver.find_element(
            By.CSS_SELECTOR, 'input[type="password"]'
        ).send_keys(password)

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="HSK 1"]]',
            ))
        ).click()

        visible_text("h2", "HSK 1")
        visible_text("span", "Đã qua · 80%")

        # Mở khóa phải được khôi phục từ dữ liệu tài khoản.
        for lesson_number in range(4, 7):
            for mode in ("lesson", "flashcard", "writing", "game"):
                wait.until(
                    EC.visibility_of_element_located((
                        By.CSS_SELECTOR,
                        f'a[href="/vocabulary/{mode}/'
                        f'new-1-lesson-{lesson_number}"]',
                    ))
                )

        driver.save_screenshot("UNLOCK-09-restored-group.png")

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
            f"\n{case_id}: đạt 80% và server đã lưu; "
            "Chrome mới không có cookie/cache tiến độ cũ; "
            "đăng nhập lại giữ điểm 80%, mở bài 4–6 "
            "và truy cập được bài 4"
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