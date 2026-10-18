import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id,target_correct",
    [
        pytest.param("UNLOCK-02", 15, id="UNLOCK-02"),
        pytest.param("UNLOCK-03", 16, id="UNLOCK-03"),
        pytest.param("UNLOCK-04", 17, id="UNLOCK-04"),
    ],
)
def test_group_unlock_by_score(case_id, target_correct):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    base_url = "http://localhost:3000"
    email = f"unlock.score.{uuid.uuid4().hex[:12]}@example.com"
    expected_score = target_correct * 5
    expected_wrong = 20 - target_correct
    should_unlock = expected_score >= 80
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
        # Tài khoản mới chưa có kết quả đạt trước đó.
        driver.get(f"{base_url}/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]',
            ))
        ).send_keys("Kiểm thử Ngưỡng mở khóa")

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

        # Lấy dữ liệu đối chiếu từ ba bài của nhóm 1.
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
                    assert pool[character] == item, (
                        f"Dữ liệu trùng không nhất quán: {character}"
                    )

                pool[character] = item

        driver.get(
            f"{base_url}/vocabulary/test/new-1-set-1"
        )
        click_text("button", "Bắt đầu kiểm tra")

        # Các câu đầu trả lời đúng, các câu còn lại trả lời sai.
        for position in range(1, 21):
            visible_text("span", f"{position}/20")

            should_be_correct = position <= target_correct
            question_type = (position - 1) % 3

            if question_type == 2:
                # Điền Pinyin.
                field = wait.until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        'input[placeholder="VD: nǐ hǎo …"]',
                    ))
                )

                character = driver.find_element(
                    By.CSS_SELECTOR, "p.hanzi.font-bold.mb-2"
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
                    # Nhìn chữ -> chọn nghĩa.
                    character = driver.find_element(
                        By.CSS_SELECTOR, "p.hanzi.font-bold.mb-3"
                    ).text.strip()
                    assert character in pool
                    expected_answer = pool[character]["meaning"]

                else:
                    # Nhìn nghĩa và Pinyin -> chọn chữ.
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
                        f"Câu {position}: không xác định duy nhất "
                        f"từ có nghĩa {meaning!r}, Pinyin {pinyin!r}."
                    )
                    expected_answer = matches[0]["hanzi"]

                correct_options = [
                    option for option in options
                    if option.text.strip() == expected_answer
                ]

                assert len(correct_options) == 1, (
                    f"Câu {position}: có {len(correct_options)} "
                    f"lựa chọn khớp đáp án {expected_answer!r}. "
                    f"Các lựa chọn: {[o.text.strip() for o in options]}"
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
                f"Câu {position}/20: "
                f"{'đúng' if should_be_correct else 'sai'}"
            )

        # Kiểm tra màn hình kết quả.
        heading_fragment = (
            "Nhóm tiếp theo đã mở"
            if should_unlock
            else "Chưa đủ điểm qua"
        )
        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//h2[contains(normalize-space(.), "{heading_fragment}")]',
            ))
        )

        visible_text("div", f"{expected_score}%")

        def get_stat(label):
            return driver.find_element(
                By.XPATH,
                f'//span[normalize-space(.)="{label}"]/../span[1]',
            ).text.strip()

        assert get_stat("Tổng câu") == "20"
        assert get_stat("Đúng") == str(target_correct)
        assert get_stat("Sai") == str(expected_wrong)

        visible_text(
            "p",
            "Nhóm 2 đã được mở khóa!"
            if should_unlock
            else "Nhóm 2 vẫn bị khóa",
        )

        driver.save_screenshot(
            f"{case_id}-result-{expected_score}.png"
        )

        click_text(
            "a", "Học tiếp" if should_unlock else "Ôn lại bài"
        )
        wait.until(EC.url_to_be(f"{base_url}/vocabulary"))

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="HSK 1"]]',
            ))
        ).click()

        visible_text("h2", "HSK 1")

        # Nhóm đầu vẫn có liên kết học.
        for lesson_number in range(1, 4):
            wait.until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR,
                    f'a[href="/vocabulary/lesson/'
                    f'new-1-lesson-{lesson_number}"]',
                ))
            )

        if should_unlock:
            # Nhóm 2 phải có đủ các chế độ cho bài 4–6.
            for lesson_number in range(4, 7):
                for mode in ("lesson", "flashcard", "writing", "game"):
                    wait.until(
                        EC.visibility_of_element_located((
                            By.CSS_SELECTOR,
                            f'a[href="/vocabulary/{mode}/'
                            f'new-1-lesson-{lesson_number}"]',
                        ))
                    )

            driver.save_screenshot(
                f"{case_id}-group-2-open.png"
            )

            wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    'a[href="/vocabulary/lesson/new-1-lesson-4"]',
                ))
            ).click()

            wait.until(
                EC.url_contains(
                    "/vocabulary/lesson/new-1-lesson-4"
                )
            )
            wait.until(
                EC.visibility_of_all_elements_located((
                    By.CSS_SELECTOR,
                    "span.hanzi.text-2xl.font-bold",
                ))
            )

            result_message = (
                "nhóm 2 mở; bài 4–6 đủ liên kết học; "
                "mở được chi tiết bài 4"
            )

        else:
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    '//*[contains(normalize-space(.), '
                    '"Hoàn thành kiểm tra nhóm 1 để mở") '
                    'and not(.//*[contains(normalize-space(.), '
                    '"Hoàn thành kiểm tra nhóm 1 để mở")])]',
                ))
            )

            for lesson_number in range(4, 7):
                for mode in ("lesson", "flashcard", "writing", "game"):
                    assert not driver.find_elements(
                        By.CSS_SELECTOR,
                        f'a[href="/vocabulary/{mode}/'
                        f'new-1-lesson-{lesson_number}"]',
                    ), (
                        f"Bài {lesson_number} có liên kết {mode} "
                        f"dù chỉ đạt {expected_score}%."
                    )

            result_message = (
                "nhóm 2 vẫn khóa; bài 1–3 mở, "
                "bài 4–6 chưa có liên kết học"
            )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: {target_correct} đúng, "
            f"{expected_wrong} sai, đạt {expected_score}%; "
            f"{result_message}"
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