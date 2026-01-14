from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

# 設定 ChromeDriver 路徑（請改成你的實際路徑）
# chrome_driver_path = '/path/to/chromedriver'

# 可選：不顯示瀏覽器介面
options = Options()
# options.add_argument('--headless')  # 若不想開啟瀏覽器視窗就啟用這行

# 啟動 WebDriver
# service = Service(chrome_driver_path)
# driver = webdriver.Chrome(service=service, options=options)
driver = webdriver.Chrome(options=options)

# 打開 CKIP 網頁
driver.get("https://ckip.iis.sinica.edu.tw/service/typo/")

# 等網頁載入
time.sleep(2)

# 找到輸入欄位並輸入文字
input_box = driver.find_element(By.CSS_SELECTOR, '#input_area')
# actions = ActionChains(driver)
# actions.click(input_box).send_keys('最進比較忙').pause(0.5)   # 點擊欄位，輸入 email
input_box.clear()
input_box.send_keys("最進有點忙")


button = driver.find_element(By.CSS_SELECTOR, "input[value='送出']")
button.click()

# 找到左邊的輸入欄位並輸入文字
# input_box = driver.find_element(By.ID, "input_area")

# submitBtn = driver.find_element(By.CSS_SELECTOR, '#button')
# actions.click(submitBtn)

# 點擊「執行」按鈕
# submit_button = driver.find_element(By.ID, "submit_button")
# submit_button.click()

# 等待結果載入（最多等10秒）
# for i in range(10):
#     time.sleep(1)
#     output_box = driver.find_element(By.ID, "output_text")
#     result = output_box.text
#     if result.strip() != "":
#         break

# 輸出結果
# print("校正結果：", result)

# 關閉瀏覽器
# driver.quit()
