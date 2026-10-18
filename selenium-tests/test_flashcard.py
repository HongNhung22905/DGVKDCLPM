import uuid

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.parametrize(
    "case_id",
    ["FC-01", "FC-02", "FC-03", "FC-04", "FC-05", "FC-06", "FC-07"]
)
def test_open_flashcard(case_id):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)
    lesson_id = "new-1-lesson-1"
    email = f"flashcard.{uuid.uuid4().hex[:12]}@example.com"

    try:
        # Tạo tài khoản mới để bài học chưa có lịch ôn trước đó.
        driver.get("http://localhost:3000/register")
        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử Flashcard")
        driver.find_element(
            By.CSS_SELECTOR, 'input[type="email"]'
        ).send_keys(email)
        driver.find_element(
            By.CSS_SELECTOR, 'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")
        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()
        wait.until(EC.url_contains("/vocabulary"))

        # Lấy nội dung bài học làm dữ liệu đối chiếu với flashcard.
        driver.get(
            f"http://localhost:3000/vocabulary/lesson/{lesson_id}"
        )
        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR, "span.hanzi.text-2xl.font-bold"
            ))
        )
        total_words = len(words)
        first_word = words[0].text.strip()
        second_word = words[1].text.strip()
        assert total_words == 20, f"Số từ thực tế: {total_words}"
        assert first_word

        first_row = words[0].find_element(
            By.XPATH,
            './ancestor::div[contains(@class,"cursor-pointer")][1]'
        )
        expected_pinyin = first_row.find_element(
            By.CSS_SELECTOR, "p.font-medium"
        ).text.strip()
        expected_meaning = first_row.find_element(
            By.CSS_SELECTOR, "p.line-clamp-1"
        ).text.strip()
        assert expected_pinyin, "Bài học thiếu Pinyin của từ đầu."
        assert expected_meaning, "Bài học thiếu nghĩa của từ đầu."

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/flashcard/{lesson_id}"]'
            ))
        ).click()
        wait.until(EC.url_contains(f"/vocabulary/flashcard/{lesson_id}"))

        heading = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        assert heading.text.startswith("Flashcard ·"), heading.text
        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//span[normalize-space(.)="1/{total_words}"]'
            ))
        )
        front_word = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR, "p.hanzi.font-bold.mb-4"
            ))
        )
        assert front_word.text.strip() == first_word

        flip_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, '//button[normalize-space(.)="Lật thẻ"]'
            ))
        )
        rating_buttons = driver.find_elements(
            By.XPATH,
            '//button[normalize-space(.)="Không nhớ" '
            'or contains(normalize-space(.), "Nhớ rồi")]'
        )
        assert not rating_buttons, "Nút đánh giá xuất hiện trước khi lật."

        if case_id in ("FC-02", "FC-03", "FC-04"):
            flip_button.click()
            for label in ("Không nhớ", "Nhớ rồi"):
                wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        f'//button[contains(normalize-space(.), "{label}")]'
                    ))
                )

            # Kiểm tra trạng thái xoay của thẻ sau khi lật.
            wait.until(
                lambda browser: browser.find_elements(
                    By.CSS_SELECTOR,
                    'div[style*="preserve-3d"][style*="rotateY(180deg)"]'
                )
            )
            back_word = driver.find_element(
                By.CSS_SELECTOR, "p.hanzi.text-5xl"
            )
            back_content = back_word.find_element(By.XPATH, "..")
            assert back_word.get_attribute("textContent").strip() == first_word

            actual_pinyin = back_content.find_element(
                By.CSS_SELECTOR, "p.text-xl.font-semibold"
            ).get_attribute("textContent").strip()
            assert actual_pinyin == expected_pinyin, (
                f"Pinyin: mong đợi {expected_pinyin!r}, "
                f"thực tế {actual_pinyin!r}"
            )
            actual_meaning = back_content.find_element(
                By.CSS_SELECTOR, "p.font-bold.text-base.mb-2"
            ).get_attribute("textContent").strip()
            assert actual_meaning == expected_meaning, (
                f"Nghĩa: mong đợi {expected_meaning!r}, "
                f"thực tế {actual_meaning!r}"
            )
        if case_id == "FC-03":
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[contains(normalize-space(.), "Nhớ rồi")]'
                ))
            ).click()

            # Bộ đếm chuyển sang thẻ thứ hai, tổng vẫn là 20.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="2/{total_words}"]'
                ))
            )

            # Chữ ở mặt trước phải là từ thứ hai của bài học.
            wait.until(
                lambda browser: browser.find_element(
                    By.CSS_SELECTOR, "p.hanzi.font-bold.mb-4"
                ).get_attribute("textContent").strip() == second_word
            )

            # Thẻ mới trở về mặt trước.
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]'
                ))
            )

            wait.until(
                lambda browser: not browser.find_elements(
                    By.XPATH,
                    '//button[normalize-space(.)="Không nhớ" '
                    'or contains(normalize-space(.), "Nhớ rồi")]'
                )
            )

            wait.until(
                lambda browser: browser.find_elements(
                    By.CSS_SELECTOR,
                    'div[style*="preserve-3d"][style*="rotateY(0deg)"]'
                )
            )

            print(
                f"\nFC-03: chọn Nhớ rồi; chuyển đúng sang "
                f"thẻ {second_word}, bộ đếm 2/{total_words}; "
                "thẻ trở về mặt trước và ẩn nút đánh giá"
            )
        if case_id == "FC-04":
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Không nhớ"]'
                ))
            ).click()

            # Từ chưa nhớ được thêm vào cuối hàng đợi.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="2/{total_words + 1}"]'
                ))
            )

            # Chuyển sang đúng từ thứ hai.
            wait.until(
                lambda browser: browser.find_element(
                    By.CSS_SELECTOR, "p.hanzi.font-bold.mb-4"
                ).get_attribute("textContent").strip() == second_word
            )

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]'
                ))
            )

            wait.until(
                lambda browser: not browser.find_elements(
                    By.XPATH,
                    '//button[normalize-space(.)="Không nhớ" '
                    'or contains(normalize-space(.), "Nhớ rồi")]'
                )
            )

            wait.until(
                lambda browser: browser.find_elements(
                    By.CSS_SELECTOR,
                    'div[style*="preserve-3d"][style*="rotateY(0deg)"]'
                )
            )

            print(
                f"\nFC-04: chọn Không nhớ; chuyển sang {second_word}; "
                f"bộ đếm 2/{total_words + 1}; "
                "thẻ trở về mặt trước và ẩn nút đánh giá"
            )    
        if case_id in ("FC-05", "FC-06"):   
            for position in range(1, total_words + 1):
                # Đúng vị trí thẻ trước khi đánh giá.
                wait.until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        f'//span[normalize-space(.)="{position}/{total_words}"]'
                    ))
                )

                wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//button[normalize-space(.)="Lật thẻ"]'
                    ))
                ).click()

                wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//button[contains(normalize-space(.), "Nhớ rồi")]'
                    ))
                ).click()

            # Sau thẻ cuối phải hiện màn hình hoàn thành.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    '//h2[normalize-space(.)="Xong rồi!"]'
                ))
            )

            def get_stat(label):
                value = driver.find_element(
                    By.XPATH,
                    f'//p[normalize-space(.)="{label}"]/../p[1]'
                )
                return value.text.strip()

            assert get_stat("Thẻ ôn") == "20"
            assert get_stat("Đúng") == "20"
            assert get_stat("Điểm") == "100%"

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Học lại"]'
                ))
            )

            print(
                "\nFC-05: hoàn thành 20 thẻ; "
                "Thẻ ôn = 20, Đúng = 20, Điểm = 100%; "
                "có nút Học lại"
            )
        if case_id == "FC-06":
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Học lại"]'
                ))
            ).click()

            # Quay về thẻ đầu, tổng số thẻ vẫn bằng 20.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="1/{total_words}"]'
                ))
            )

            wait.until(
                lambda browser: browser.find_element(
                    By.CSS_SELECTOR, "p.hanzi.font-bold.mb-4"
                ).get_attribute("textContent").strip() == first_word
            )

            # Hiển thị mặt trước và nút Lật thẻ.
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]'
                ))
            )

            wait.until(
                lambda browser: browser.find_elements(
                    By.CSS_SELECTOR,
                    'div[style*="preserve-3d"][style*="rotateY(0deg)"]'
                )
            )

            # Chưa lật lại thì chưa hiện các nút đánh giá.
            wait.until(
                lambda browser: not browser.find_elements(
                    By.XPATH,
                    '//button[normalize-space(.)="Không nhớ" '
                    'or contains(normalize-space(.), "Nhớ rồi")]'
                )
            )

            # Màn hình kết quả của lượt trước đã đóng.
            wait.until(
                EC.invisibility_of_element_located((
                    By.XPATH,
                    '//h2[normalize-space(.)="Xong rồi!"]'
                ))
            )

            print(
                f"\nFC-06: Học lại trở về thẻ đầu {first_word}; "
                f"bộ đếm 1/{total_words}; "
                "hiển thị mặt trước và ẩn nút đánh giá"
            )
        if case_id == "FC-07":
            # Thẻ đầu: chọn Không nhớ để đưa vào cuối hàng đợi.
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]'
                ))
            ).click()

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Không nhớ"]'
                ))
            ).click()

            queue_size = total_words + 1

            # Các thẻ từ vị trí 2 đến 20: chọn Nhớ rồi.
            for position in range(2, total_words + 1):
                wait.until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        f'//span[normalize-space(.)="{position}/{queue_size}"]'
                    ))
                )

                wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//button[normalize-space(.)="Lật thẻ"]'
                    ))
                ).click()

                wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//button[contains(normalize-space(.), "Nhớ rồi")]'
                    ))
                ).click()

            # Thẻ cuối phải là từ đầu tiên đã chọn Không nhớ.
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//span[normalize-space(.)="{queue_size}/{queue_size}"]'
                ))
            )

            wait.until(
                lambda browser: browser.find_element(
                    By.CSS_SELECTOR, "p.hanzi.font-bold.mb-4"
                ).get_attribute("textContent").strip() == first_word
            )

            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]'
                ))
            )

            # Chưa đánh giá lại từ này thì chưa được kết thúc lượt ôn.
            assert not driver.find_elements(
                By.XPATH,
                '//h2[normalize-space(.)="Xong rồi!"]'
            )

            print(
                f"\nFC-07: từ {first_word} đã chọn Không nhớ "
                f"xuất hiện lại ở vị trí {queue_size}/{queue_size}; "
                "lượt ôn chưa kết thúc trước khi đánh giá lại"
            )
        driver.save_screenshot(f"{case_id}-pass.png")
        print(
            f"\n{case_id}: mở đúng flashcard, "
            f"thẻ đầu {first_word}, tổng {total_words} thẻ"
            + (
                "; lật thẻ có Pinyin và nghĩa khớp bài học"
                if case_id == "FC-02"
                else ""
            )
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
