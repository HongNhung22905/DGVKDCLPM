"""Kiểm tra giao diện công cụ local, không chạy Selenium trên website HSK.

Chạy khi công cụ đã mở ở localhost:4317. Hai báo cáo Vitest thực được lưu vào
lịch sử: một lần chạy nhóm ngưỡng điểm và một lần nhập XML có sẵn.
"""
import json
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

tool = Path(__file__).resolve().parents[1]
qa = tool / "data" / "qa"
qa.mkdir(parents=True, exist_ok=True)
os.environ["SE_CACHE_PATH"] = str(qa / "selenium-cache")
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1440,1100")
options.add_argument(f"--user-data-dir={qa / 'chrome-profile'}")
options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 40)
checks = []

def click(selector):
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))).click()

try:
    driver.get("http://localhost:4317")
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "#group option")) == 3)
    assert "HSK Test Lab" in driver.title
    checks.append("Trang và cấu hình tải thành công")

    click('[data-engine="selenium"]')
    assert len(driver.find_elements(By.CSS_SELECTOR, "#group option")) == 9
    assert "localhost:3000" in driver.find_element(By.ID, "engine-note").text
    click('[data-engine="vitest"]')
    Select(driver.find_element(By.ID, "group")).select_by_value("vitest-gate")
    assert driver.find_element(By.ID, "timeout").get_attribute("value") == "120"
    click("#run-button")
    wait.until(lambda browser: "Ngưỡng điểm" in browser.find_element(By.ID, "run-header").text)
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "#run-header .badge.passed")) == 1)
    assert driver.find_element(By.CSS_SELECTOR, ".metric-value").text == "5"
    assert len(driver.find_elements(By.CSS_SELECTOR, ".case")) == 5
    checks.append("Chọn nhóm và chạy 5 test Vitest thật qua giao diện")

    click('[data-tab="log"]')
    wait.until(lambda browser: "5 passed" in browser.find_element(By.CSS_SELECTOR, "pre.log").text)
    click('[data-tab="ai"]')
    assert "GEMINI_API_KEY" in driver.find_element(By.ID, "result-content").text
    checks.append("Nhật ký và chế độ thiếu Gemini key hoạt động")

    existing_xml = tool.parent / "hsk-app" / "frontend" / "whitebox-results.xml"
    driver.find_element(By.ID, "xml-file").send_keys(str(existing_xml))
    wait.until(lambda browser: "whitebox-results.xml" in browser.find_element(By.ID, "run-header").text)
    assert driver.find_element(By.CSS_SELECTOR, ".metric-value").text == "22"
    assert "không phải kết quả chạy mới" in driver.find_element(By.ID, "result-content").text
    Select(driver.find_element(By.ID, "case-filter")).select_by_value("issues")
    assert len(driver.find_elements(By.CSS_SELECTOR, ".case")) == 0
    Select(driver.find_element(By.ID, "case-filter")).select_by_value("all")
    click(".case summary")
    assert driver.find_element(By.CSS_SELECTOR, ".case").get_attribute("open") is not None
    checks.append("Nhập XML thật, phân biệt nguồn, lọc và mở chi tiết testcase")

    click('.nav-item[data-view="history"]')
    driver.find_element(By.ID, "history-search").send_keys("whitebox-results.xml")
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, "#history-runs .run-link")) >= 1)
    click("#history-runs .run-link")
    wait.until(lambda browser: "whitebox-results.xml" in browser.find_element(By.ID, "run-header").text)
    driver.refresh()
    wait.until(lambda browser: len(browser.find_elements(By.CSS_SELECTOR, ".case")) == 22)
    checks.append("Tìm lịch sử, chọn báo cáo và tải lại trang không mất kết quả")

    driver.save_screenshot(str(qa / "desktop.png"))
    driver.set_window_size(390, 900)
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True})
    assert driver.execute_script("return document.documentElement.scrollWidth <= window.innerWidth + 1")
    driver.save_screenshot(str(qa / "mobile.png"))
    checks.append("Giao diện mobile không tràn ngang")

    errors = [item for item in driver.get_log("browser") if item["level"] == "SEVERE" and "favicon.ico" not in item["message"]]
    assert not errors, errors
    checks.append("Không có lỗi JavaScript hoặc CSP trong trình duyệt")
    print(json.dumps({"passed": len(checks), "checks": checks, "screenshots": str(qa)}, ensure_ascii=False))
finally:
    driver.quit()
