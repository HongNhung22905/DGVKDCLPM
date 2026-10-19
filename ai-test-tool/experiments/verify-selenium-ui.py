"""Đối chiếu từng ca DOM/API/XML của lượt đầy đủ đã chạy; không thực thi test mới."""
import json
import os
from pathlib import Path
import sys
import urllib.request
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

tool=Path(__file__).resolve().parents[1]
run_id=sys.argv[1]
with urllib.request.urlopen('http://localhost:4317/api/runs/'+run_id) as response:
    run=json.load(response)
if run['status']=='running' or not run.get('reportFile'):
    raise RuntimeError('Chưa có XML cuối lượt')
with urllib.request.urlopen('http://localhost:4317/api/runs/'+run_id+'/xml') as response:
    xml=response.read()
reference=[]
for case in ET.fromstring(xml).iter('testcase'):
    status='ERROR' if case.find('error') is not None else 'FAIL' if case.find('failure') is not None else 'BỎ QUA' if case.find('skipped') is not None else 'PASS'
    reference.append({'name':case.get('name','Không có tên'),'status':status})
os.environ['SE_CACHE_PATH']=str(tool/'data/selenium-cache')
options=webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--window-size=1440,1100')
driver=webdriver.Chrome(options=options)
wait=WebDriverWait(driver,30)
try:
    driver.get('http://localhost:4317')
    wait.until(lambda browser:len(browser.find_elements(By.CSS_SELECTOR,'#group option'))==3)
    driver.find_element(By.CSS_SELECTOR,'.nav-item[data-view="history"]').click()
    wait.until(lambda browser:len(browser.find_elements(By.CSS_SELECTOR,f'#history-runs [data-run="{run_id}"]'))==1)
    driver.find_element(By.CSS_SELECTOR,f'#history-runs [data-run="{run_id}"]').click()
    wait.until(lambda browser:len(browser.find_elements(By.CSS_SELECTOR,'.case'))==len(reference))
    actual=[{'name':item.find_element(By.CSS_SELECTOR,'.case-name').text,'status':item.find_element(By.CSS_SELECTOR,'.badge').text} for item in driver.find_elements(By.CSS_SELECTOR,'.case')]
    key=lambda item:(item['name'],item['status'])
    match=sorted(reference,key=key)==sorted(actual,key=key)
    assert match
    result={'runId':run_id,'totalOriginalXml':len(reference),'totalDisplayed':len(actual),'allNamesAndStatusesMatchOriginalXml':match,'selectedFromHistory':True,'reranWebsiteTests':False}
    root=tool/'experiments/2026-10-19'
    (root/'selenium-dom-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    driver.save_screenshot(str(root/'selenium-history-result.png'))
    print(json.dumps(result,ensure_ascii=False))
finally:
    driver.quit()
