from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 可選：不顯示瀏覽器介面
options = Options()
# options.add_argument('--headless')  # 若不想開啟瀏覽器視窗就啟用這行

# 啟動 WebDriver
driver = webdriver.Chrome(options=options)

try:
    # 打開 CKIP 網頁
    driver.get("https://ckip.iis.sinica.edu.tw/service/typo/")
    
    # 等網頁載入
    time.sleep(2)
    
    # 找到輸入欄位並輸入文字
    input_box = driver.find_element(By.CSS_SELECTOR, '#input_area')
    input_box.clear()
    input_box.send_keys("最進有點忙，晚上在來寫程式。")
    
    # 點擊送出按鈕
    button = driver.find_element(By.CSS_SELECTOR, "input[value='送出']")
    button.click()
    
    # 等待結果載入（使用 WebDriverWait 等待結果區域出現內容）
    wait = WebDriverWait(driver, 10)
    
    # 等待輸出區域出現並包含文字
    output_area = wait.until(
        EC.presence_of_element_located((By.ID, "output_area"))
    )
    
    # 等待一下確保內容完全載入
    time.sleep(2)
    
    # 獲取結果文字
    result = output_area.text
    
    # 輸出結果
    print("=" * 50)
    print("校正結果：")
    print("=" * 50)
    print(result)
    print("=" * 50)

finally:
    # 關閉瀏覽器
    input("按 Enter 鍵關閉瀏覽器...")
    driver.quit()
