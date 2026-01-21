from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

input_file = "numbers.txt"
output_valid = "valid_numbers.txt"
output_invalid = "invalid_numbers.txt"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get("https://my-ambassador.lifecell.ua")
wait = WebDriverWait(driver, 20)

client_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'label') and text()='Клієнт']"))
)
client_button.click()

input_field = wait.until(EC.presence_of_element_located((By.ID, "msisdn")))

with open(input_file, "r", encoding="utf-8") as f:
    numbers = [line.strip() for line in f if line.strip()]

for number in numbers:
    try:
        input_field.clear()
        input_field.send_keys(number)

        search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Пошук']]"))
        )
        search_button.click()

        status_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'text') and (contains(text(),'UNKNOWN') or contains(text(),'LTE') or contains(text(),'eSIM'))]")
            )
        )
        status_text = status_element.text.strip()

        if status_text in ["LTE", "eSIM"]:
            with open(output_valid, "a", encoding="utf-8") as f:
                f.write(number + "\n")

            reg_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'label') and text()='Реєстрація стартового пакету']"))
            )
            reg_button.click()
        else:
            with open(output_invalid, "a", encoding="utf-8") as f:
                f.write(number + "\n")

    except:
        with open(output_invalid, "a", encoding="utf-8") as f:
            f.write(number + " — ERROR\n")

driver.quit()
