import uuid
from urllib.parse import parse_qs, urlparse

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = 'http://localhost:3000'
INPUT = (By.CSS_SELECTOR, 'input[placeholder="Ví dụ: 你好, nihao, xin chào..."]')
CARDS = 'div.grid.grid-cols-1.sm\\:grid-cols-2.gap-3 > div'


@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    driver.set_window_size(1366, 900)
    driver.set_script_timeout(15)
    wait = WebDriverWait(driver, 30)
    try:
        driver.get(BASE_URL + '/register')
        wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, 'input[placeholder="Nguyễn Văn A"]',
        ))).send_keys('Kiem thu Tra tu')
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(
            f'search.{uuid.uuid4().hex[:12]}@example.com'
        )
        driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Ít nhất 6 ký tự"]').send_keys('1234567')
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        wait.until(EC.url_contains('/vocabulary'))
        # Chỉ quan sát request thật của trang; không sửa response.
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                window.__searchReads = [];
                const original = window.fetch;
                window.fetch = async function(...args) {
                    const input = args[0];
                    const raw = typeof input === 'string' ? input
                        : input instanceof URL ? input.href : input.url;
                    const url = new URL(raw, location.href);
                    const response = await original.apply(this, args);
                    if (url.pathname === '/api/search') {
                        try {
                            const body = await response.clone().json();
                            window.__searchReads.push({
                                url:url.href, status:response.status, body:body
                            });
                        } catch (e) {
                            window.__searchReads.push({
                                url:url.href, status:response.status, error:String(e)
                            });
                        }
                    }
                    return response;
                };
            '''
        })
        driver.get(BASE_URL + '/search')
        wait.until(EC.element_to_be_clickable(INPUT))
        visible(driver, 'p', 'Nhập từ để tra cứu')
        yield driver
    finally:
        driver.quit()


def visible(driver, tag, text):
    return WebDriverWait(driver, 30).until(EC.visibility_of_element_located((
        By.XPATH, f'//{tag}[normalize-space(.)="{text}"]',
    )))


def cards(driver):
    return driver.find_elements(By.CSS_SELECTOR, CARDS)


def request_count(driver):
    return driver.execute_script('return window.__searchReads.length;')


def results_loaded(driver, query, level, since):
    wait = WebDriverWait(driver, 30)

    def completed(browser):
        records = browser.execute_script('return window.__searchReads;')
        for record in reversed(records[since:]):
            params = parse_qs(urlparse(record['url']).query)
            if params.get('q', [''])[0] != query:
                continue
            if params.get('level', [''])[0] != level:
                continue
            assert record['status'] == 200, record
            assert 'error' not in record, record
            return record
        return False

    record = wait.until(completed)
    data = record['body']
    assert isinstance(data['results'], list), data
    assert isinstance(data['total'], int), data
    assert data['total'] >= len(data['results'])

    # Chờ React cập nhật xong và thanh số lượng xuất hiện.
    def rendered(browser):
        if len(cards(browser)) != len(data['results']):
            return False
        if browser.find_elements(By.CSS_SELECTOR, 'svg.animate-spin'):
            return False
        if data['total']:
            count = browser.find_elements(By.XPATH, '//p[starts-with(normalize-space(.),"Tìm thấy ")]')
            return bool(count and count[0].is_displayed())
        return bool(browser.find_elements(By.XPATH,
            '//p[starts-with(normalize-space(.),"Không tìm thấy kết quả cho ")]'))

    wait.until(rendered)
    if data['total']:
        bar = driver.find_element(By.XPATH, '//p[starts-with(normalize-space(.),"Tìm thấy ")]')
        numbers = bar.find_elements(By.CSS_SELECTOR, 'span.font-semibold')
        assert numbers[0].text == str(data['total'])
        if data['total'] > len(data['results']):
            assert numbers[1].text == str(len(data['results']))
        for card, word in zip(cards(driver), data['results']):
            assert card.find_element(By.CSS_SELECTOR, 'span.font-black').text.strip() == word['simplified']
            assert card.find_element(By.CSS_SELECTOR, 'p.text-lg.font-semibold').text.strip() == word['pinyin']
    assert not driver.find_elements(By.XPATH,
        '//div[contains(@class,"text-red-600") and contains(.,"Không thể kết nối")]')
    return data


def search(driver, query):
    since = request_count(driver)
    field = driver.find_element(*INPUT)
    field.send_keys(Keys.CONTROL, 'a')
    field.send_keys(query)
    return results_loaded(driver, query, '', since)


def target_card(driver, simplified):
    for card in cards(driver):
        if card.find_element(By.CSS_SELECTOR, 'span.font-black').text.strip() == simplified:
            return card
    raise AssertionError(f'Không có thẻ từ {simplified!r} trong kết quả hiển thị.')


def reference_word(driver):
    # Từ đã dùng trong bài HSK 1 ở các ca trước.
    data = search(driver, '的')
    assert data['total'] > 0
    card = target_card(driver, '的')
    return {
        'hanzi': '的',
        'pinyin': card.find_element(By.CSS_SELECTOR, 'p.text-lg.font-semibold').text.strip(),
        'meaning_vi': card.find_element(By.CSS_SELECTOR, 'p.text-sm.font-semibold.mb-1').text.strip(),
    }


@pytest.mark.parametrize('case_id', [
    'SEARCH-01', 'SEARCH-02', 'SEARCH-03', 'SEARCH-04', 'SEARCH-05',
], ids=lambda value: value)
def test_search(browser, case_id):
    driver = browser
    try:
        ref = reference_word(driver)
        if case_id == 'SEARCH-01':
            assert ref['pinyin'] and ref['meaning_vi']
            assert target_card(driver, ref['hanzi']).is_displayed()
            message = 'Tìm chữ Hán 的; hiển thị chữ, Pinyin và nghĩa Việt.'

        elif case_id == 'SEARCH-02':
            # Dùng Pinyin hiển thị thật; không tự giả định quy tắc bỏ dấu.
            data = search(driver, ref['pinyin'])
            assert data['total'] > 0
            card = target_card(driver, ref['hanzi'])
            assert card.find_element(By.CSS_SELECTOR, 'p.text-lg.font-semibold').text.strip() == ref['pinyin']
            message = f'Tìm Pinyin {ref["pinyin"]!r}; có đúng từ tham chiếu.'

        elif case_id == 'SEARCH-03':
            assert ref['meaning_vi'], 'Từ tham chiếu thiếu nghĩa Việt.'
            data = search(driver, ref['meaning_vi'])
            assert data['total'] > 0
            card = target_card(driver, ref['hanzi'])
            assert card.find_element(By.CSS_SELECTOR, 'p.text-sm.font-semibold.mb-1').text.strip() == ref['meaning_vi']
            message = f'Tìm nghĩa Việt {ref["meaning_vi"]!r}; có đúng từ tham chiếu.'

        elif case_id == 'SEARCH-04':
            baseline = [c.find_element(By.CSS_SELECTOR, 'span.font-black').text for c in cards(driver)]
            since = request_count(driver)
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((
                By.XPATH, '//button[normalize-space(.)="HSK 1"]',
            ))).click()
            data = results_loaded(driver, ref['hanzi'], '1', since)
            assert data['total'] > 0, 'HSK 1 phải có từ 的.'
            assert all(w['level'] == 'new-1' for w in data['results'])
            for card in cards(driver):
                assert card.find_element(By.XPATH, './/span[normalize-space(.)="HSK 1"]').is_displayed()
            target_card(driver, ref['hanzi'])
            driver.save_screenshot(f'{case_id}-filtered.png')

            since = request_count(driver)
            driver.find_element(By.XPATH, '//button[normalize-space(.)="Tất cả"]').click()
            results_loaded(driver, ref['hanzi'], '', since)
            restored = [c.find_element(By.CSS_SELECTOR, 'span.font-black').text for c in cards(driver)]
            assert restored == baseline, 'Bỏ lọc không khôi phục tập kết quả ban đầu.'
            message = 'Lọc HSK 1 đúng; Tất cả khôi phục kết quả ban đầu.'

        else:
            query = 'zzzz_no_hsk_' + uuid.uuid4().hex
            data = search(driver, query)
            assert data['total'] == 0
            assert data['results'] == []
            visible(driver, 'p', 'Thử tìm bằng chữ Hán, pinyin hoặc nghĩa khác')
            empty = driver.find_element(By.XPATH,
                '//p[starts-with(normalize-space(.),"Không tìm thấy kết quả cho ")]')
            assert query in empty.text
            assert not cards(driver)
            driver.save_screenshot(f'{case_id}-empty.png')
            # Nút X là button trong cùng khối với input.
            field = driver.find_element(*INPUT)
            field.find_element(By.XPATH, '../button').click()
            WebDriverWait(driver, 30).until(lambda b: b.find_element(*INPUT).get_attribute('value') == '')
            visible(driver, 'p', 'Nhập từ để tra cứu')
            assert not cards(driver)
            assert driver.execute_script('return document.activeElement === arguments[0];', field)
            message = 'Truy vấn không tồn tại có trạng thái rỗng; nút X xóa và đưa focus về ô tìm.'

        driver.save_screenshot(f'{case_id}-pass.png')
        print(f'\n{case_id}: PASS — {message}')
    except Exception:
        try:
            driver.save_screenshot(f'{case_id}-fail.png')
        except Exception as error:
            print(f'Không chụp được ảnh: {error}')
        raise
