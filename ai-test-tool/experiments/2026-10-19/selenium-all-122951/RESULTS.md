# Kết quả Selenium đầy đủ

Run ID: 04d381c9-e06b-453e-9601-2a698141b34a.

85 ca: 75 PASS, 10 FAIL, 0 ERROR, 0 SKIP.

| Module | Tổng | PASS | FAIL | ERROR | SKIP |
| --- | ---: | ---: | ---: | ---: | ---: |
| selenium-tests.test_register | 9 | 8 | 1 | 0 | 0 |
| selenium-tests.test_login | 8 | 8 | 0 | 0 | 0 |
| selenium-tests.test_logout | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_vocabulary | 10 | 3 | 7 | 0 | 0 |
| selenium-tests.test_flashcard | 7 | 7 | 0 | 0 | 0 |
| selenium-tests.test_unlock | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_unlock_score | 3 | 3 | 0 | 0 | 0 |
| selenium-tests.test_unlock_retry | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_unlock_pinyin | 3 | 3 | 0 | 0 | 0 |
| selenium-tests.test_unlock_session | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_review | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_review_due | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_review_future | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_review_rate | 2 | 2 | 0 | 0 | 0 |
| selenium-tests.test_review_repeat | 2 | 2 | 0 | 0 | 0 |
| selenium-tests.test_review_history | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_progress | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_progress_cards | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_progress_completed | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_stats | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_stats_calendar | 1 | 0 | 1 | 0 | 0 |
| selenium-tests.test_stats_persistence | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_stats_session | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_data_isolation | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_writing | 5 | 5 | 0 | 0 | 0 |
| selenium-tests.test_writing_quiz | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_writing_complete | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_game | 3 | 3 | 0 | 0 | 0 |
| selenium-tests.test_game_hanzi | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_game_mixed | 1 | 1 | 0 | 0 | 0 |
| selenium-tests.test_game_complete | 3 | 3 | 0 | 0 | 0 |
| selenium-tests.test_search | 5 | 5 | 0 | 0 | 0 |
| selenium-tests.test_notebook | 5 | 4 | 1 | 0 | 0 |

### selenium-tests.test_register — test_register_whitespace_name

Trạng thái: failed; 6.388 giây.

```text
AssertionError: REG-09: hệ thống chấp nhận tên chỉ chứa khoảng trắng. Email thử nghiệm: [EMAIL ĐÃ ẨN]; URL: http://localhost:3000/register&#10;assert 'accepted' == 'rejected'&#10;  &#10;  - rejected&#10;  + accepted
def test_register_whitespace_name():
        driver = webdriver.Chrome()
        driver.set_window_size(1366, 900)
        wait = WebDriverWait(driver, 30)
        email = f"selenium.{uuid.uuid4().hex[:12]}@example.com"
    
        try:
            driver.get("http://localhost:3000/register")
    
            wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    'input[placeholder="Nguyễn Văn A"]'
                ))
            ).send_keys("   ")
    
            driver.find_element(
                By.CSS_SELECTOR, 'input[type="email"]'
            ).send_keys(email)
    
            driver.find_element(
                By.CSS_SELECTOR,
                'input[placeholder="Ít nhất 6 ký tự"]'
            ).send_keys("123456")
    
            driver.find_element(
                By.CSS_SELECTOR, 'button[type="submit"]'
            ).click()
    
            # Chờ kết quả rõ ràng: bị từ chối hoặc đăng ký thành công.
            def registration_result(browser):
                if "/vocabulary" in browser.current_url:
                    return "accepted"
    
                if browser.get_cookie("hsk_token") is not None:
                    return "accepted"
    
                errors = browser.find_elements(
                    By.CSS_SELECTOR, "form p"
                )
                for element in errors:
                    if (
                        element.is_displayed()
                        and element.value_of_css_property("color")
                        == "rgba(192, 57, 43, 1)"
                        and element.text.strip()
                    ):
                        return "rejected"
    
                return False
    
            result = wait.until(registration_result)
    
>           assert result == "rejected", (
                f"REG-09: hệ thống chấp nhận tên chỉ chứa khoảng trắng. "
                f"Email thử nghiệm: {email}; URL: {driver.current_url}"
            )
E           AssertionError: REG-09: hệ thống chấp nhận tên chỉ chứa khoảng trắng. Email thử nghiệm: [EMAIL ĐÃ ẨN]; URL: http://localhost:3000/register
E           assert 'accepted' == 'rejected'
E             
E             - rejected
E             + accepted

..\..\..\..\selenium-tests\test_register.py:327: AssertionError
```

### selenium-tests.test_vocabulary — test_select_level_and_return[HSK-1]

Trạng thái: failed; 9.145 giây.

```text
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>&#10;  (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception&#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2957a73]&#10;&#09;chromedriver!(No symbol) [0x7ff7c295567a]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29529b7]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2951880]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2943828]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29790ea]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29430a6]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
level = 1

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
            ).send_keys("[EMAIL ĐÃ ẨN]")
    
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
>           ).click()
              ^^^^^^^

..\..\..\..\selenium-tests\test_vocabulary.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:112: in click
    self._execute(Command.CLICK_ELEMENT)
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:504: in _execute
    return self._parent.execute(command, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py:506: in execute
    self.error_handler.check_response(response)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000022266D08F70>
response = {'status': 400, 'value': '{"value":{"error":"element click intercepted","message":"element click intercepted: Element ...ac2e4c]\\n\\tKERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]\\n\\tntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]\\n"}}'}

    def check_response(self, response: dict[str, Any]) -> None:
        """Check that a JSON response from the WebDriver does not have an error.
    
        Args:
            response: The JSON response from the WebDriver server as a dictionary
                object.
    
        Raises:
            WebDriverException: If the response contains an error message.
        """
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                try:
                    value = json.loads(value_json)
                    if isinstance(value, dict):
                        if len(value) == 1:
                            value = value["value"]
                        status = value.get("error", None)
                        if not status:
                            status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                            message = value.get("value") or value.get("message")
                            if not isinstance(message, str):
                                value = message
                                message = message.get("message") if isinstance(message, dict) else None
                        else:
                            message = value.get("message", None)
                except ValueError:
                    pass
    
        exception_class: type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException
    
        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]
    
        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]
    
        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            raise exception_class(message, screen, stacktrace, alert_text)
>       raise exception_class(message, screen, stacktrace)
E       selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>
E         (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c2957a73]
E       	chromedriver!(No symbol) [0x7ff7c295567a]
E       	chromedriver!(No symbol) [0x7ff7c29529b7]
E       	chromedriver!(No symbol) [0x7ff7c2951880]
E       	chromedriver!(No symbol) [0x7ff7c2943828]
E       	chromedriver!(No symbol) [0x7ff7c29790ea]
E       	chromedriver!(No symbol) [0x7ff7c29430a6]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py:232: ElementClickInterceptedException
```

### selenium-tests.test_vocabulary — test_select_level_and_return[HSK-2]

Trạng thái: failed; 9.100 giây.

```text
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>&#10;  (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception&#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2957a73]&#10;&#09;chromedriver!(No symbol) [0x7ff7c295567a]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29529b7]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2951880]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2943828]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29790ea]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29430a6]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
level = 2

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
            ).send_keys("[EMAIL ĐÃ ẨN]")
    
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
>           ).click()
              ^^^^^^^

..\..\..\..\selenium-tests\test_vocabulary.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:112: in click
    self._execute(Command.CLICK_ELEMENT)
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:504: in _execute
    return self._parent.execute(command, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py:506: in execute
    self.error_handler.check_response(response)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000022266CF68F0>
response = {'status': 400, 'value': '{"value":{"error":"element click intercepted","message":"element click intercepted: Element ...ac2e4c]\\n\\tKERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]\\n\\tntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]\\n"}}'}

    def check_response(self, response: dict[str, Any]) -> None:
        """Check that a JSON response from the WebDriver does not have an error.
    
        Args:
            response: The JSON response from the WebDriver server as a dictionary
                object.
    
        Raises:
            WebDriverException: If the response contains an error message.
        """
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                try:
                    value = json.loads(value_json)
                    if isinstance(value, dict):
                        if len(value) == 1:
                            value = value["value"]
                        status = value.get("error", None)
                        if not status:
                            status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                            message = value.get("value") or value.get("message")
                            if not isinstance(message, str):
                                value = message
                                message = message.get("message") if isinstance(message, dict) else None
                        else:
                            message = value.get("message", None)
                except ValueError:
                    pass
    
        exception_class: type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException
    
        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]
    
        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]
    
        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            raise exception_class(message, screen, stacktrace, alert_text)
>       raise exception_class(message, screen, stacktrace)
E       selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>
E         (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c2957a73]
E       	chromedriver!(No symbol) [0x7ff7c295567a]
E       	chromedriver!(No symbol) [0x7ff7c29529b7]
E       	chromedriver!(No symbol) [0x7ff7c2951880]
E       	chromedriver!(No symbol) [0x7ff7c2943828]
E       	chromedriver!(No symbol) [0x7ff7c29790ea]
E       	chromedriver!(No symbol) [0x7ff7c29430a6]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py:232: ElementClickInterceptedException
```

### selenium-tests.test_vocabulary — test_select_level_and_return[HSK-3]

Trạng thái: failed; 9.275 giây.

```text
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>&#10;  (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception&#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2957a73]&#10;&#09;chromedriver!(No symbol) [0x7ff7c295567a]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29529b7]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2951880]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2943828]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29790ea]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29430a6]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
level = 3

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
            ).send_keys("[EMAIL ĐÃ ẨN]")
    
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
>           ).click()
              ^^^^^^^

..\..\..\..\selenium-tests\test_vocabulary.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:112: in click
    self._execute(Command.CLICK_ELEMENT)
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:504: in _execute
    return self._parent.execute(command, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py:506: in execute
    self.error_handler.check_response(response)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000022266CF5C70>
response = {'status': 400, 'value': '{"value":{"error":"element click intercepted","message":"element click intercepted: Element ...ac2e4c]\\n\\tKERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]\\n\\tntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]\\n"}}'}

    def check_response(self, response: dict[str, Any]) -> None:
        """Check that a JSON response from the WebDriver does not have an error.
    
        Args:
            response: The JSON response from the WebDriver server as a dictionary
                object.
    
        Raises:
            WebDriverException: If the response contains an error message.
        """
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                try:
                    value = json.loads(value_json)
                    if isinstance(value, dict):
                        if len(value) == 1:
                            value = value["value"]
                        status = value.get("error", None)
                        if not status:
                            status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                            message = value.get("value") or value.get("message")
                            if not isinstance(message, str):
                                value = message
                                message = message.get("message") if isinstance(message, dict) else None
                        else:
                            message = value.get("message", None)
                except ValueError:
                    pass
    
        exception_class: type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException
    
        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]
    
        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]
    
        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            raise exception_class(message, screen, stacktrace, alert_text)
>       raise exception_class(message, screen, stacktrace)
E       selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>
E         (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c2957a73]
E       	chromedriver!(No symbol) [0x7ff7c295567a]
E       	chromedriver!(No symbol) [0x7ff7c29529b7]
E       	chromedriver!(No symbol) [0x7ff7c2951880]
E       	chromedriver!(No symbol) [0x7ff7c2943828]
E       	chromedriver!(No symbol) [0x7ff7c29790ea]
E       	chromedriver!(No symbol) [0x7ff7c29430a6]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py:232: ElementClickInterceptedException
```

### selenium-tests.test_vocabulary — test_select_level_and_return[HSK-4]

Trạng thái: failed; 8.843 giây.

```text
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>&#10;  (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception&#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2957a73]&#10;&#09;chromedriver!(No symbol) [0x7ff7c295567a]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29529b7]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2951880]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2943828]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29790ea]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29430a6]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
level = 4

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
            ).send_keys("[EMAIL ĐÃ ẨN]")
    
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
>           ).click()
              ^^^^^^^

..\..\..\..\selenium-tests\test_vocabulary.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:112: in click
    self._execute(Command.CLICK_ELEMENT)
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:504: in _execute
    return self._parent.execute(command, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py:506: in execute
    self.error_handler.check_response(response)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000022266D00B00>
response = {'status': 400, 'value': '{"value":{"error":"element click intercepted","message":"element click intercepted: Element ...ac2e4c]\\n\\tKERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]\\n\\tntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]\\n"}}'}

    def check_response(self, response: dict[str, Any]) -> None:
        """Check that a JSON response from the WebDriver does not have an error.
    
        Args:
            response: The JSON response from the WebDriver server as a dictionary
                object.
    
        Raises:
            WebDriverException: If the response contains an error message.
        """
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                try:
                    value = json.loads(value_json)
                    if isinstance(value, dict):
                        if len(value) == 1:
                            value = value["value"]
                        status = value.get("error", None)
                        if not status:
                            status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                            message = value.get("value") or value.get("message")
                            if not isinstance(message, str):
                                value = message
                                message = message.get("message") if isinstance(message, dict) else None
                        else:
                            message = value.get("message", None)
                except ValueError:
                    pass
    
        exception_class: type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException
    
        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]
    
        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]
    
        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            raise exception_class(message, screen, stacktrace, alert_text)
>       raise exception_class(message, screen, stacktrace)
E       selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>
E         (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c2957a73]
E       	chromedriver!(No symbol) [0x7ff7c295567a]
E       	chromedriver!(No symbol) [0x7ff7c29529b7]
E       	chromedriver!(No symbol) [0x7ff7c2951880]
E       	chromedriver!(No symbol) [0x7ff7c2943828]
E       	chromedriver!(No symbol) [0x7ff7c29790ea]
E       	chromedriver!(No symbol) [0x7ff7c29430a6]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py:232: ElementClickInterceptedException
```

### selenium-tests.test_vocabulary — test_select_level_and_return[HSK-5]

Trạng thái: failed; 7.913 giây.

```text
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>&#10;  (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception&#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2957a73]&#10;&#09;chromedriver!(No symbol) [0x7ff7c295567a]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29529b7]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2951880]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2943828]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29790ea]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29430a6]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
level = 5

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
            ).send_keys("[EMAIL ĐÃ ẨN]")
    
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
>           ).click()
              ^^^^^^^

..\..\..\..\selenium-tests\test_vocabulary.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:112: in click
    self._execute(Command.CLICK_ELEMENT)
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:504: in _execute
    return self._parent.execute(command, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py:506: in execute
    self.error_handler.check_response(response)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000022268290BD0>
response = {'status': 400, 'value': '{"value":{"error":"element click intercepted","message":"element click intercepted: Element ...ac2e4c]\\n\\tKERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]\\n\\tntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]\\n"}}'}

    def check_response(self, response: dict[str, Any]) -> None:
        """Check that a JSON response from the WebDriver does not have an error.
    
        Args:
            response: The JSON response from the WebDriver server as a dictionary
                object.
    
        Raises:
            WebDriverException: If the response contains an error message.
        """
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                try:
                    value = json.loads(value_json)
                    if isinstance(value, dict):
                        if len(value) == 1:
                            value = value["value"]
                        status = value.get("error", None)
                        if not status:
                            status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                            message = value.get("value") or value.get("message")
                            if not isinstance(message, str):
                                value = message
                                message = message.get("message") if isinstance(message, dict) else None
                        else:
                            message = value.get("message", None)
                except ValueError:
                    pass
    
        exception_class: type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException
    
        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]
    
        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]
    
        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            raise exception_class(message, screen, stacktrace, alert_text)
>       raise exception_class(message, screen, stacktrace)
E       selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>
E         (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c2957a73]
E       	chromedriver!(No symbol) [0x7ff7c295567a]
E       	chromedriver!(No symbol) [0x7ff7c29529b7]
E       	chromedriver!(No symbol) [0x7ff7c2951880]
E       	chromedriver!(No symbol) [0x7ff7c2943828]
E       	chromedriver!(No symbol) [0x7ff7c29790ea]
E       	chromedriver!(No symbol) [0x7ff7c29430a6]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py:232: ElementClickInterceptedException
```

### selenium-tests.test_vocabulary — test_select_level_and_return[HSK-6]

Trạng thái: failed; 7.937 giây.

```text
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>&#10;  (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception&#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2957a73]&#10;&#09;chromedriver!(No symbol) [0x7ff7c295567a]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29529b7]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2951880]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2943828]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29790ea]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29430a6]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
level = 6

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
            ).send_keys("[EMAIL ĐÃ ẨN]")
    
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
>           ).click()
              ^^^^^^^

..\..\..\..\selenium-tests\test_vocabulary.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:112: in click
    self._execute(Command.CLICK_ELEMENT)
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:504: in _execute
    return self._parent.execute(command, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py:506: in execute
    self.error_handler.check_response(response)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x000002226818F950>
response = {'status': 400, 'value': '{"value":{"error":"element click intercepted","message":"element click intercepted: Element ...ac2e4c]\\n\\tKERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]\\n\\tntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]\\n"}}'}

    def check_response(self, response: dict[str, Any]) -> None:
        """Check that a JSON response from the WebDriver does not have an error.
    
        Args:
            response: The JSON response from the WebDriver server as a dictionary
                object.
    
        Raises:
            WebDriverException: If the response contains an error message.
        """
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                try:
                    value = json.loads(value_json)
                    if isinstance(value, dict):
                        if len(value) == 1:
                            value = value["value"]
                        status = value.get("error", None)
                        if not status:
                            status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                            message = value.get("value") or value.get("message")
                            if not isinstance(message, str):
                                value = message
                                message = message.get("message") if isinstance(message, dict) else None
                        else:
                            message = value.get("message", None)
                except ValueError:
                    pass
    
        exception_class: type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException
    
        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]
    
        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]
    
        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            raise exception_class(message, screen, stacktrace, alert_text)
>       raise exception_class(message, screen, stacktrace)
E       selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>
E         (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c2957a73]
E       	chromedriver!(No symbol) [0x7ff7c295567a]
E       	chromedriver!(No symbol) [0x7ff7c29529b7]
E       	chromedriver!(No symbol) [0x7ff7c2951880]
E       	chromedriver!(No symbol) [0x7ff7c2943828]
E       	chromedriver!(No symbol) [0x7ff7c29790ea]
E       	chromedriver!(No symbol) [0x7ff7c29430a6]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py:232: ElementClickInterceptedException
```

### selenium-tests.test_vocabulary — test_select_level_and_return[HSK-7]

Trạng thái: failed; 8.174 giây.

```text
selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>&#10;  (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception&#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2957a73]&#10;&#09;chromedriver!(No symbol) [0x7ff7c295567a]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29529b7]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2951880]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2943828]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29790ea]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29430a6]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
level = 7

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
            ).send_keys("[EMAIL ĐÃ ẨN]")
    
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
>           ).click()
              ^^^^^^^

..\..\..\..\selenium-tests\test_vocabulary.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:112: in click
    self._execute(Command.CLICK_ELEMENT)
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webelement.py:504: in _execute
    return self._parent.execute(command, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py:506: in execute
    self.error_handler.check_response(response)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.remote.errorhandler.ErrorHandler object at 0x0000022266D7DB00>
response = {'status': 400, 'value': '{"value":{"error":"element click intercepted","message":"element click intercepted: Element ...ac2e4c]\\n\\tKERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]\\n\\tntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]\\n"}}'}

    def check_response(self, response: dict[str, Any]) -> None:
        """Check that a JSON response from the WebDriver does not have an error.
    
        Args:
            response: The JSON response from the WebDriver server as a dictionary
                object.
    
        Raises:
            WebDriverException: If the response contains an error message.
        """
        status = response.get("status", None)
        if not status or status == ErrorCode.SUCCESS:
            return
        value = None
        message = response.get("message", "")
        screen: str = response.get("screen", "")
        stacktrace = None
        if isinstance(status, int):
            value_json = response.get("value", None)
            if value_json and isinstance(value_json, str):
                try:
                    value = json.loads(value_json)
                    if isinstance(value, dict):
                        if len(value) == 1:
                            value = value["value"]
                        status = value.get("error", None)
                        if not status:
                            status = value.get("status", ErrorCode.UNKNOWN_ERROR)
                            message = value.get("value") or value.get("message")
                            if not isinstance(message, str):
                                value = message
                                message = message.get("message") if isinstance(message, dict) else None
                        else:
                            message = value.get("message", None)
                except ValueError:
                    pass
    
        exception_class: type[WebDriverException]
        e = ErrorCode()
        error_codes = [item for item in dir(e) if not item.startswith("__")]
        for error_code in error_codes:
            error_info = getattr(ErrorCode, error_code)
            if isinstance(error_info, list) and status in error_info:
                exception_class = getattr(ExceptionMapping, error_code, WebDriverException)
                break
        else:
            exception_class = WebDriverException
    
        if not value:
            value = response["value"]
        if isinstance(value, str):
            raise exception_class(value)
        if message == "" and "message" in value:
            message = value["message"]
    
        screen = None  # type: ignore[assignment]
        if "screen" in value:
            screen = value["screen"]
    
        stacktrace = None
        st_value = value.get("stackTrace") or value.get("stacktrace")
        if st_value:
            if isinstance(st_value, str):
                stacktrace = st_value.split("\n")
            else:
                stacktrace = []
                try:
                    for frame in st_value:
                        line = frame.get("lineNumber", "")
                        file = frame.get("fileName", "<anonymous>")
                        if line:
                            file = f"{file}:{line}"
                        meth = frame.get("methodName", "<anonymous>")
                        if "className" in frame:
                            meth = f"{frame['className']}.{meth}"
                        msg = "    at %s (%s)"
                        msg = msg % (meth, file)
                        stacktrace.append(msg)
                except TypeError:
                    pass
        if exception_class == UnexpectedAlertPresentException:
            alert_text = None
            if "data" in value:
                alert_text = value["data"].get("text")
            elif "alert" in value:
                alert_text = value["alert"].get("text")
            raise exception_class(message, screen, stacktrace, alert_text)
>       raise exception_class(message, screen, stacktrace)
E       selenium.common.exceptions.ElementClickInterceptedException: Message: element click intercepted: Element <button class="transition-colors" style="color: rgb(168, 149, 106);">...</button> is not clickable at point (234, 10). Other element would receive the click: <div class="flex items-center gap-1 text-xs font-medium flex-1 justify-center">...</div>
E         (Session info: chrome=154.0.8037.100); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c2957a73]
E       	chromedriver!(No symbol) [0x7ff7c295567a]
E       	chromedriver!(No symbol) [0x7ff7c29529b7]
E       	chromedriver!(No symbol) [0x7ff7c2951880]
E       	chromedriver!(No symbol) [0x7ff7c2943828]
E       	chromedriver!(No symbol) [0x7ff7c29790ea]
E       	chromedriver!(No symbol) [0x7ff7c29430a6]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py:232: ElementClickInterceptedException
```

### selenium-tests.test_stats_calendar — test_stats_calendar_and_ranges

Trạng thái: failed; 38.564 giây.

```text
AssertionError: API và dòng lịch sử xác nhận hôm nay có 20 từ, nhưng lịch dạng lưới không hiển thị đúng:&#10;  4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.&#10;  6 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.&#10;  1 năm: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.&#10;  4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.&#10;assert not ['4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.', '6 tháng: mong đợi 1 ô chứa phiê...-19), thực tế có 0 ô có dữ liệu.', '4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.']
def test_stats_calendar_and_ranges():
        driver = webdriver.Chrome()
        driver.set_window_size(1366, 900)
        driver.set_script_timeout(15)
        wait = WebDriverWait(driver, 30)
    
        case_id = "STATS-03"
        base_url = "http://localhost:3000"
        email = f"stats.calendar.{uuid.uuid4().hex[:12]}@example.com"
    
        def visible_text(tag, text):
            return wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    f'//{tag}[normalize-space(.)="{text}"]',
                ))
            )
    
        def stat_value(label):
            return driver.find_element(
                By.XPATH,
                f'//p[normalize-space(.)="{label}"]/../'
                'p[contains(@class,"text-2xl")]',
            ).text.strip()
    
        def local_today():
            return driver.execute_script(
                """
                const now = new Date();
                const pad = value => String(value).padStart(2, "0");
                return now.getFullYear() + "-"
                    + pad(now.getMonth() + 1) + "-"
                    + pad(now.getDate());
                """
            )
    
        try:
            # Tạo tài khoản mới.
            driver.get(f"{base_url}/register")
    
            wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    'input[placeholder="Nguyễn Văn A"]',
                ))
            ).send_keys("Kiểm thử Lịch ôn")
    
            driver.find_element(
                By.CSS_SELECTOR,
                'input[type="email"]',
            ).send_keys(email)
    
            driver.find_element(
                By.CSS_SELECTOR,
                'input[placeholder="Ít nhất 6 ký tự"]',
            ).send_keys("1234567")
    
            driver.find_element(
                By.CSS_SELECTOR,
                'button[type="submit"]',
            ).click()
    
            wait.until(EC.url_contains("/vocabulary"))
    
            # Mở Flashcard để khởi tạo 20 thẻ đến hạn.
            driver.get(
                f"{base_url}/vocabulary/flashcard/new-1-lesson-1"
            )
    
            visible_text("span", "1/20")
            wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//button[normalize-space(.)="Lật thẻ"]',
                ))
            )
    
            # Chờ thẻ được lưu trước khi mở phiên ôn.
            session_date = local_today()
    
            def cards_ready(browser):
                response = browser.execute_async_script(
                    """
                    const date = arguments[0];
                    const done = arguments[arguments.length - 1];
    
                    fetch(
                        "/api/review?date=" + encodeURIComponent(date),
                        { credentials: "include", cache: "no-store" }
                    )
                        .then(async r => done({
                            status: r.status,
                            body: await r.json()
                        }))
                        .catch(error => done({error: String(error)}));
                    """,
                    session_date,
                )
    
                assert "error" not in response, response
                assert response["status"] == 200, response
    
                data = response["body"]
                return (
                    len(data.get("allCards", [])) == 20
                    and len(data.get("cards", [])) == 20
                )
    
            wait.until(cards_ready)
    
            driver.get(f"{base_url}/review")
            visible_text("span", "0/20 từ")
    
            # Hoàn thành phiên ôn bằng giao diện.
            seen_words = set()
    
            for reviewed_before in range(20):
                visible_text("span", f"{reviewed_before}/20 từ")
    
                flip_button = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//button[normalize-space(.)="Lật thẻ"]',
                    ))
                )
    
                word = driver.find_element(
                    By.CSS_SELECTOR,
                    "p.hanzi.font-bold.mb-4",
                ).text.strip()
    
                assert word, "Thẻ không hiển thị từ."
                assert word not in seen_words, (
                    f"Từ bị lặp trong phiên ôn: {word}"
                )
                seen_words.add(word)
    
                flip_button.click()
    
                wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        '//button[.//p[normalize-space(.)="Đã thuộc"]]',
                    ))
                ).click()
    
            visible_text("h2", "Ôn tập xong!")
            assert len(seen_words) == 20
            assert local_today() == session_date, (
                "Ngày local đổi trong lúc chạy; cần chạy lại."
            )
    
            # Chỉ đọc API để chờ dữ liệu được lưu.
            def session_saved(browser):
                response = browser.execute_async_script(
                    """
                    const date = arguments[0];
                    const done = arguments[arguments.length - 1];
    
                    fetch(
                        "/api/review/history?days=119&date="
                            + encodeURIComponent(date),
                        { credentials: "include", cache: "no-store" }
                    )
                        .then(async r => done({
                            status: r.status,
                            body: await r.json()
                        }))
                        .catch(error => done({error: String(error)}));
                    """,
                    session_date,
                )
    
                assert "error" not in response, response
                assert response["status"] == 200, response
    
                data = response["body"]
                stats = data["stats"]
    
                assert stats["totalSessions"] <= 1, (
                    "Tài khoản mới có lịch sử phiên bị lưu trùng."
                )
    
                if (
                    stats["totalSessions"] == 1
                    and stats["allCards"] == 20
                    and stats["dueToday"] == 0
                ):
                    return data
    
                return False
    
            history = wait.until(session_saved)
            assert len(history["daily"]) == 1
    
            daily = history["daily"][0]
            assert daily["date"] == session_date
            assert daily["totalCards"] == 20
            assert daily["correctCards"] == 20
            assert daily["sessions"] == 1
            assert daily["score"] == 100
    
            driver.get(f"{base_url}/stats")
            visible_text("h1", "Thống kê ôn tập")
    
            expected_stats = {
                "Chuỗi ngày": "1 ngày",
                "Từ đã ôn": "20",
                "Điểm TB": "100%",
                "Ngày đã học": "1 ngày",
                "Tổng thẻ đang ôn": "20",
                "Cần ôn hôm nay": "0",
                "Đã ôn ngày mai trở đi": "20",
            }
    
            for label, expected in expected_stats.items():
                wait.until(
                    lambda browser, name=label, value=expected:
                    stat_value(name) == value
                )
    
            # Đối chiếu dòng lịch sử trước khi kiểm tra lịch lưới.
            history_heading = visible_text(
                "h2", "Lịch sử phiên ôn tập"
            )
            history_panel = history_heading.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"rounded-2xl")][1]',
            )
    
            rows = history_panel.find_elements(
                By.CSS_SELECTOR,
                "div.flex.items-center.px-5.py-3",
            )
            assert len(rows) == 1
            row = rows[0]
    
            date_label = driver.execute_script(
                """
                return new Date(arguments[0]).toLocaleDateString(
                    "vi-VN",
                    { day: "2-digit", month: "2-digit" }
                );
                """,
                session_date,
            )
    
            assert row.find_element(
                By.XPATH,
                f'.//p[normalize-space(.)="{date_label}"]',
            ).is_displayed()
    
            for value in ("20 từ", "100%", "20/20"):
                assert row.find_element(
                    By.XPATH,
                    f'.//span[normalize-space(.)="{value}"]',
                ).is_displayed()
    
            # Kiểm tra lịch dạng lưới.
            calendar_heading = visible_text(
                "h2", "Lịch học theo ngày"
            )
            calendar_panel = calendar_heading.find_element(
                By.XPATH,
                './ancestor::div[contains(@class,"rounded-2xl")][1]',
            )
    
            expected_tooltip_date = driver.execute_script(
                """
                return new Date(arguments[0]).toLocaleDateString(
                    "vi-VN",
                    {
                        weekday: "short",
                        year: "numeric",
                        month: "short",
                        day: "numeric"
                    }
                );
                """,
                session_date,
            )
    
            def calendar_cells():
                # Ô ngày: 14 × 14 px; ô chú thích màu: 12 × 12 px.
                return calendar_panel.find_elements(
                    By.CSS_SELECTOR,
                    'div[style*="width: 14px"][style*="height: 14px"]',
                )
    
            calendar_errors = []
    
            for label, weeks in (
                ("4 tháng", 17),
                ("6 tháng", 26),
                ("1 năm", 52),
                ("4 tháng", 17),
            ):
                range_button = calendar_panel.find_element(
                    By.XPATH,
                    f'.//button[normalize-space(.)="{label}"]',
                )
    
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    range_button,
                )
                range_button.click()
    
                wait.until(
                    lambda browser: len(calendar_cells()) == weeks * 7
                )
    
                wait.until(
        lambda browser:
        calendar_panel.find_element(
            By.XPATH,
            f'.//button[normalize-space(.)="{label}"]',
        ).value_of_css_property("background-color")
        == "rgba(180, 83, 9, 1)",
        message=f"Nút {label} chưa hiển thị trạng thái được chọn.",
    )
    
                cells = calendar_cells()
                active_cells = [
                    cell for cell in cells
                    if cell.value_of_css_property("cursor") == "pointer"
                ]
    
                print(
                    f"\n{label}: {len(cells)} ô ngày; "
                    f"{len(active_cells)} ô có dữ liệu"
                )
    
                screenshot_label = {
                    "4 tháng": "4-months",
                    "6 tháng": "6-months",
                    "1 năm": "1-year",
                }[label]
    
                # Ghi nhận lỗi nhưng vẫn kiểm tra các khoảng còn lại.
                if len(active_cells) != 1:
                    calendar_errors.append(
                        f"{label}: mong đợi 1 ô chứa phiên hôm nay "
                        f"({session_date}), thực tế có "
                        f"{len(active_cells)} ô có dữ liệu."
                    )
    
                    driver.save_screenshot(
                        f"{case_id}-{screenshot_label}-fail.png"
                    )
    
                else:
                    active_cell = active_cells[0]
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        active_cell,
                    )
    
                    ActionChains(driver).move_to_element(
                        active_cell
                    ).perform()
    
                    tooltip = wait.until(
                        EC.visibility_of_element_located((
                            By.CSS_SELECTOR,
                            "div.fixed.z-50.pointer-events-none",
                        ))
                    )
    
                    assert tooltip.find_element(
                        By.XPATH,
                        f'.//p[normalize-space(.)='
                        f'"{expected_tooltip_date}"]',
                    ).is_displayed(), (
                        f"{label}: tooltip không ghi đúng ngày hôm nay."
                    )
    
                    assert tooltip.find_element(
                        By.XPATH,
                        './/p[normalize-space(.)='
                        '"20 từ ôn · 100% đúng"]',
                    ).is_displayed()
    
                    driver.save_screenshot(
                        f"{case_id}-{screenshot_label}.png"
                    )
    
                    ActionChains(driver).move_to_element(
                        calendar_heading
                    ).perform()
    
                    wait.until(
                        EC.invisibility_of_element_located((
                            By.CSS_SELECTOR,
                            "div.fixed.z-50.pointer-events-none",
                        ))
                    )
    
                # Các chỉ số phải giữ nguyên sau khi đổi khoảng.
                for stat_label, expected in expected_stats.items():
                    wait.until(
                        lambda browser, name=stat_label, value=expected:
                        stat_value(name) == value
                    )
    
                assert local_today() == session_date, (
                    "Ngày local đổi trong lúc chạy; cần chạy lại."
                )
    
>           assert not calendar_errors, (
                "API và dòng lịch sử xác nhận hôm nay có 20 từ, "
                "nhưng lịch dạng lưới không hiển thị đúng:\n"
                + "\n".join(calendar_errors)
            )
E           AssertionError: API và dòng lịch sử xác nhận hôm nay có 20 từ, nhưng lịch dạng lưới không hiển thị đúng:
E             4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.
E             6 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.
E             1 năm: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.
E             4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.
E           assert not ['4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.', '6 tháng: mong đợi 1 ô chứa phiê...-19), thực tế có 0 ô có dữ liệu.', '4 tháng: mong đợi 1 ô chứa phiên hôm nay (2026-10-19), thực tế có 0 ô có dữ liệu.']

..\..\..\..\selenium-tests\test_stats_calendar.py:419: AssertionError
```

### selenium-tests.test_notebook — test_notebook[NOTE-04]

Trạng thái: failed; 42.410 giây.

```text
selenium.common.exceptions.TimeoutException: Message: &#10;Stacktrace:&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2acf540]&#10;&#09;chromedriver!(No symbol) [0x7ff7c28f45fd]&#10;&#09;chromedriver!(No symbol) [0x7ff7c294fca1]&#10;&#09;chromedriver!(No symbol) [0x7ff7c294ff6c]&#10;&#09;chromedriver!(No symbol) [0x7ff7c29a3077]&#10;&#09;chromedriver!(No symbol) [0x7ff7c299fcd9]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2941a12]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2942823]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]&#10;&#09;chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2adcb55]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad7f64]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ad80f4]&#10;&#09;chromedriver!(No symbol) [0x7ff7c2ac2e4c]&#10;&#09;KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]&#10;&#09;ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]
browser = <selenium.webdriver.chrome.webdriver.WebDriver (session="d3421ab59f48042e6665bfd5ce3edaf6")>
case_id = 'NOTE-04'

    @pytest.mark.parametrize('case_id', ['NOTE-01','NOTE-02','NOTE-03','NOTE-04','NOTE-05'],
                             ids=lambda value: value)
    def test_notebook(browser, case_id):
        driver = browser
        try:
            open_search(driver)
            assert entries(driver) == [], 'Tài khoản mới có sẵn dữ liệu sổ tay.'
    
            if case_id == 'NOTE-02':
                # Hai trang cùng thấy trạng thái chưa lưu, rồi lần lượt lưu
                # cùng một từ bằng UI. Không dùng nút Bỏ lưu như thao tác thêm.
                first_tab = driver.current_window_handle
                driver.switch_to.new_window('tab')
                second_tab = driver.current_window_handle
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                    window.__notebookWrites = [];
                    const original = window.fetch;
                    window.fetch = async function(...args) {
                        const raw = typeof args[0] === 'string' ? args[0] : args[0].url;
                        const url = new URL(raw, location.href);
                        const method = (args[1]?.method || args[0]?.method || 'GET').toUpperCase();
                        const response = await original.apply(this,args);
                        if (url.pathname === '/api/user/notebook' && method !== 'GET') {
                            window.__notebookWrites.push({method, status:response.status});
                        }
                        return response;
                    };
                '''
                })
                open_search(driver)
                target(driver).find_element(By.CSS_SELECTOR, 'button[title="Lưu vào sổ tay"]')
                driver.switch_to.window(first_tab)
                original = save_from_search(driver)
                driver.switch_to.window(second_tab)
                save_from_search(driver)
                data = entries(driver)
                assert len(data) == 1
                assert data[0]['wordId'] == original['wordId']
                open_notebook(driver)
                driver.refresh()
                wait(driver).until(target)
                assert len(entries(driver)) == 1
                assert len(driver.find_elements(By.CSS_SELECTOR, GRID)) == 1
                message = 'Lưu cùng từ từ hai trang không tạo bản ghi trùng.'
    
            else:
                original = save_from_search(driver)
                card = open_notebook(driver)
                assert card.find_element(By.CSS_SELECTOR, 'p.text-base.font-semibold').text.strip() == original['pinyin']
    
                if case_id == 'NOTE-01':
                    driver.refresh()
                    wait(driver).until(target)
                    assert len(entries(driver)) == 1
                    assert entries(driver)[0]['wordId'] == original['wordId']
                    message = 'Thêm từ 的 thành công; tải lại vẫn có đúng một từ.'
    
                elif case_id == 'NOTE-03':
                    edit_note(driver, 'Ghi chú ban đầu')
                    revised = 'Ghi chú đã sửa: của tôi — 我的'
                    edit_note(driver, revised)
                    driver.refresh()
                    card = wait(driver).until(target)
                    note = wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                        'div.grid div.border-l-2')))
                    assert note.text == revised
                    assert entries(driver)[0]['note'] == revised
                    card.find_element(By.CSS_SELECTOR, 'button[title="Ghi chú"]').click()
                    area = wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'textarea')))
                    assert area.get_attribute('value') == revised
                    card.find_element(By.XPATH, './/button[normalize-space(.)="Huỷ"]').click()
                    message = 'Sửa ghi chú; server và giao diện giữ nội dung sau tải lại.'
    
                elif case_id == 'NOTE-04':
                    since = write_count(driver)
                    card.find_element(By.CSS_SELECTOR, 'button[title="Xóa khỏi sổ tay"]').click()
                    wait_write(driver, 'DELETE', since)
                    wait(driver).until(lambda b: entries(b) == [])
>                   visible(driver, 'p', 'Sổ tay trống')

..\..\..\..\selenium-tests\test_notebook.py:227: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
..\..\..\..\selenium-tests\test_notebook.py:56: in visible
    return wait(driver).until(EC.visibility_of_element_located((
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <selenium.webdriver.support.wait.WebDriverWait (session="d3421ab59f48042e6665bfd5ce3edaf6")>
method = <function visibility_of_element_located.<locals>._predicate at 0x0000022266D4F950>
message = ''

    def until(self, method: Callable[[D], Literal[False] | T], message: str = "") -> T:
        """Wait until the method returns a value that is not False.
    
        Calls the method provided with the driver as an argument until the
        return value does not evaluate to ``False``.
    
        Args:
            method: A callable object that takes a WebDriver instance as an
                argument.
            message: Optional message for TimeoutException.
    
        Returns:
            The result of the last call to `method`.
    
        Raises:
            TimeoutException: If 'method' does not return a truthy value within
                the WebDriverWait object's timeout.
    
        Example:
            >>> from selenium.webdriver.common.by import By
            >>> from selenium.webdriver.support.wait import WebDriverWait
            >>> from selenium.webdriver.support import expected_conditions as EC
            >>>
            >>> # Wait until an element is visible on the page
            >>> wait = WebDriverWait(driver, 10)
            >>> element = wait.until(EC.visibility_of_element_located((By.ID, "exampleId")))
            >>> print(element.text)
        """
        screen = None
        stacktrace = None
    
        end_time = time.monotonic() + self._timeout
        while True:
            try:
                value = method(self._driver)
                if value:
                    return value
            except self._ignored_exceptions as exc:
                screen = getattr(exc, "screen", None)
                stacktrace = getattr(exc, "stacktrace", None)
            if time.monotonic() > end_time:
                break
            time.sleep(self._poll)
>       raise TimeoutException(message, screen, stacktrace)
E       selenium.common.exceptions.TimeoutException: Message: 
E       Stacktrace:
E       	chromedriver!GetHandleVerifier [0x7ff7c2ba9d55+5a55]
E       	chromedriver!(No symbol) [0x7ff7c2acf540]
E       	chromedriver!(No symbol) [0x7ff7c28f45fd]
E       	chromedriver!(No symbol) [0x7ff7c294fca1]
E       	chromedriver!(No symbol) [0x7ff7c294ff6c]
E       	chromedriver!(No symbol) [0x7ff7c29a3077]
E       	chromedriver!(No symbol) [0x7ff7c299fcd9]
E       	chromedriver!(No symbol) [0x7ff7c2941a12]
E       	chromedriver!(No symbol) [0x7ff7c2942823]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fc04b1+41c1b1]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fee26b+449f6b]
E       	chromedriver!GetHandleVerifier [0x7ff7c2fe274e+43e44e]
E       	chromedriver!GetHandleVerifier [0x7ff7c2ca32fe+feffe]
E       	chromedriver!(No symbol) [0x7ff7c2adcb55]
E       	chromedriver!(No symbol) [0x7ff7c2ad7f64]
E       	chromedriver!(No symbol) [0x7ff7c2ad80f4]
E       	chromedriver!(No symbol) [0x7ff7c2ac2e4c]
E       	KERNEL32!BaseThreadInitThunk [0x7ffb55c9dda7+17]
E       	ntdll!RtlUserThreadStart [0x7ffb57cbee4c+2c]

..\..\..\.venv\Lib\site-packages\selenium\webdriver\support\wait.py:121: TimeoutException
```
