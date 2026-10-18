import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.parametrize("level", range(1, 8), ids=[
    "HSK-1", "HSK-2", "HSK-3", "HSK-4",
    "HSK-5", "HSK-6", "HSK-7"
])
def test_select_level_and_return(level):
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)
    case_id = f"VOC-01-HSK-{level}"

    try:
        driver.get("http://localhost:3000/login")

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[type="email"]')
            )
        ).send_keys("selenium.09b083baae11@example.com")

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Chọn đúng thẻ cấp độ, không nhầm nút bắt đầu HSK 1.
        level_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[.//p[normalize-space(.)="HSK {level}"]]'
            ))
        )
        level_button.click()

        # Tiêu đề cấp độ phải hiển thị đúng.
        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                f'//h2[normalize-space(.)="HSK {level}"]'
            ))
        )

        # Bài đầu và các hành động học phải truy cập được.
        lesson_id = f"new-{level}-lesson-1"
        for mode in ["lesson", "flashcard", "writing", "game"]:
            link = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    f'a[href="/vocabulary/{mode}/{lesson_id}"]'
                ))
            )
            assert link.is_displayed(), (
                f"Không hiển thị hành động {mode} của {lesson_id}"
            )

        # Quay về màn hình chọn cấp độ.
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[normalize-space(.)="Chọn cấp độ"]'
            ))
        ).click()

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//h2[normalize-space(.)="Chọn cấp độ"]'
            ))
        )

        level_cards = driver.find_elements(
            By.XPATH,
            '//button[.//p[starts-with(normalize-space(.), "HSK ")]]'
        )
        assert len(level_cards) == 7, (
            f"Mong đợi 7 thẻ cấp độ, thực tế {len(level_cards)}"
        )

        driver.save_screenshot(f"{case_id}-pass.png")
        print(f"\n{case_id}: chọn cấp và quay lại thành công")

    except Exception:
        driver.save_screenshot(f"{case_id}-fail.png")
        raise

    finally:
        driver.quit()




def test_initial_lesson_locks():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    try:
        # Dùng tài khoản mới để bảo đảm chưa có kết quả mở khóa.
        import uuid
        email = f"vocab.lock.{uuid.uuid4().hex[:12]}@example.com"

        driver.get("http://localhost:3000/register")

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'input[placeholder="Nguyễn Văn A"]'
            ))
        ).send_keys("Kiểm thử khóa bài")

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

        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="HSK 1"]]'
            ))
        ).click()

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH, '//h2[normalize-space(.)="HSK 1"]'
            ))
        )

        # Nhóm đầu: bài 1–3 có đủ liên kết hành động.
        for lesson in range(1, 4):
            for mode in ["lesson", "flashcard", "writing", "game"]:
                link = wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        f'a[href="/vocabulary/{mode}/'
                        f'new-1-lesson-{lesson}"]'
                    ))
                )
                assert link.is_displayed()

        # Nhóm thứ hai phải hiển thị thông báo khóa.
        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//span[normalize-space(.)='
                '"Hoàn thành kiểm tra nhóm 1 để mở"]'
            ))
        )

        # Bài 4–6 vẫn có thẻ nhưng không có liên kết hành động.
        for lesson in range(4, 7):
            assert driver.find_elements(
                By.XPATH,
                f'//p[normalize-space(.)="Bài {lesson}"]'
            ), f"Không tìm thấy thẻ bài {lesson}"

            for mode in ["lesson", "flashcard", "writing", "game"]:
                links = driver.find_elements(
                    By.CSS_SELECTOR,
                    f'a[href="/vocabulary/{mode}/'
                    f'new-1-lesson-{lesson}"]'
                )
                assert not links, (
                    f"Bài {lesson} đang khóa nhưng có link {mode}"
                )

        driver.save_screenshot("VOC-02-pass.png")
        print("\nVOC-02: bài 1–3 mở, bài 4–6 khóa")

    except Exception:
        try:
            driver.save_screenshot("VOC-02-fail.png")
        except Exception:
            pass
        raise

    finally:
        try:
            driver.quit()
        except Exception:
            pass



def test_open_lesson_detail():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)
    lesson_id = "new-1-lesson-1"

    try:
        # Chuẩn bị phiên đăng nhập.
        driver.get("http://localhost:3000/login")

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[type="email"]')
            )
        ).send_keys("selenium.09b083baae11@example.com")

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))

        # Chọn HSK 1 và nhấn Học ở bài đầu.
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                '//button[.//p[normalize-space(.)="HSK 1"]]'
            ))
        ).click()

        wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/lesson/{lesson_id}"]'
            ))
        ).click()

        wait.until(
            EC.url_contains(f"/vocabulary/lesson/{lesson_id}")
        )

        # Chờ nội dung bài học xuất hiện sau kiểm tra khóa.
        heading = wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        assert heading.text.strip(), "Tiêu đề bài học rỗng"

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH,
                '//button[normalize-space(.)="Học từng từ"]'
            ))
        )

        # Danh sách phải có chữ Hán.
        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR,
                "span.hanzi.text-2xl.font-bold"
            ))
        )
        assert all(word.text.strip() for word in words), (
            "Có mục chữ Hán rỗng"
        )

        # Kiểm tra liên kết luyện tập trỏ tới đúng bài.
        for mode in ["flashcard", "writing", "game"]:
            link = driver.find_element(
                By.CSS_SELECTOR,
                f'a[href="/vocabulary/{mode}/{lesson_id}"]'
            )
            assert link.is_displayed(), (
                f"Không hiển thị liên kết {mode}"
            )

        driver.save_screenshot("VOC-03-pass.png")
        print(
            f"\nVOC-03: mở đúng bài, có {len(words)} từ "
            "và đủ liên kết luyện tập"
        )

    except Exception:
        try:
            driver.save_screenshot("VOC-03-fail.png")
        except Exception as error:
            print(f"\nKhông chụp được ảnh: {error}")
        raise

    finally:
        try:
            driver.quit()
        except Exception:
            pass


def test_study_word_navigation():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    wait = WebDriverWait(driver, 30)

    def click_button(text):
        wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                f'//button[normalize-space(.)="{text}"]'
            ))
        ).click()

    try:
        driver.get("http://localhost:3000/login")

        wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'input[type="email"]')
            )
        ).send_keys("selenium.09b083baae11@example.com")

        driver.find_element(
            By.CSS_SELECTOR,
            'input[placeholder="Ít nhất 6 ký tự"]'
        ).send_keys("1234567")

        driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        ).click()

        wait.until(EC.url_contains("/vocabulary"))
        driver.get(
            "http://localhost:3000/vocabulary/lesson/new-1-lesson-1"
        )

        # Lấy thứ tự từ và nghĩa đang hiển thị trong danh sách.
        words = wait.until(
            EC.visibility_of_all_elements_located((
                By.CSS_SELECTOR, "span.hanzi.text-2xl.font-bold"
            ))
        )
        expected_words = [word.text.strip() for word in words]
        assert len(expected_words) >= 2

        first_row = words[0].find_element(
            By.XPATH, './ancestor::div[contains(@class,"cursor-pointer")][1]'
        )
        expected_meaning = first_row.find_element(
            By.CSS_SELECTOR, "p.line-clamp-1"
        ).text.strip()
        assert expected_meaning, "Nghĩa từ đầu tiên rỗng"

        click_button("Học từng từ")

        def current_word():
            return driver.find_element(
                By.CSS_SELECTOR, "p.hanzi.font-bold.mb-3"
            ).text.strip()

        def wait_position(index):
            wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//p[normalize-space(.)='
                    f'"{index} / {len(expected_words)}"]'
                ))
            )
            wait.until(
                lambda browser:
                current_word() == expected_words[index - 1]
            )

        wait_position(1)

        reveal = wait.until(
            EC.element_to_be_clickable((
                By.XPATH, '//button[normalize-space(.)="Xem nghĩa"]'
            ))
        )
        card = reveal.find_element(
            By.XPATH, './ancestor::div[contains(@class,"max-w-lg")][1]'
        )
        reveal.click()

        wait.until(
            EC.invisibility_of_element_located((
                By.XPATH, '//button[normalize-space(.)="Xem nghĩa"]'
            ))
        )
        wait.until(lambda browser: expected_meaning in card.text)

        click_button("Tiếp")
        wait_position(2)

        # Chuyển từ phải ẩn nghĩa trở lại.
        wait.until(
            EC.visibility_of_element_located((
                By.XPATH, '//button[normalize-space(.)="Xem nghĩa"]'
            ))
        )

        click_button("Trước")
        wait_position(1)

        wait.until(
            EC.visibility_of_element_located((
                By.XPATH, '//button[normalize-space(.)="Xem nghĩa"]'
            ))
        )

        driver.save_screenshot("VOC-04-pass.png")
        print("\nVOC-04: xem nghĩa, chuyển tiếp và quay lại đúng từ")

    except Exception:
        try:
            driver.save_screenshot("VOC-04-fail.png")
        except Exception as error:
            print(f"\nKhông chụp được ảnh: {error}")
        raise

    finally:
        try:
            driver.quit()
        except Exception:
            pass