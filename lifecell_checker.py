from __future__ import annotations

import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INPUT_FILE = "numbers.txt"
OUTPUT_VALID = "valid_numbers.txt"
OUTPUT_INVALID = "invalid_numbers.txt"

LOGIN_WAIT_SECONDS = 300
ACTION_WAIT_SECONDS = 20


def wait_for_login(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, LOGIN_WAIT_SECONDS)
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'label') and text()='Клієнт']"))
    )


def open_client_tab(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, ACTION_WAIT_SECONDS)
    client_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'label') and text()='Клієнт']"))
    )
    client_button.click()


def get_input_field(driver: webdriver.Chrome):
    wait = WebDriverWait(driver, ACTION_WAIT_SECONDS)
    return wait.until(EC.element_to_be_clickable((By.ID, "msisdn")))


def click_search(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, ACTION_WAIT_SECONDS)
    search_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Пошук']]"))
    )
    search_button.click()


def wait_for_status(driver: webdriver.Chrome):
    wait = WebDriverWait(driver, ACTION_WAIT_SECONDS)
    unknown = (By.XPATH, "//div[contains(@class,'text') and contains(normalize-space(),'UNKNOWN')]")
    device_no_support = (
        By.XPATH,
        "//div[contains(@class,'header') and contains(@class,'device-no-support') and normalize-space()='LTE']",
    )
    support_lte = (
        By.XPATH,
        "//div[contains(@class,'header') and contains(@class,'support') and normalize-space()='LTE']",
    )
    return wait.until(EC.any_of(EC.presence_of_element_located(unknown),
                               EC.presence_of_element_located(device_no_support),
                               EC.presence_of_element_located(support_lte)))


def click_back(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, ACTION_WAIT_SECONDS)
    back_icon = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//mat-icon[normalize-space()='arrow_back']"))
    )
    back_icon.click()


def register_package(driver: webdriver.Chrome) -> None:
    wait = WebDriverWait(driver, ACTION_WAIT_SECONDS)
    reg_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class,'label') and text()='Реєстрація стартового пакету']")
        )
    )
    reg_button.click()

    submit_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Зареєструвати']]"))
    )
    submit_button.click()


def load_numbers(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def append_number(path: str, number: str) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{number}\n")


def main() -> None:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    driver.get("https://my-ambassador.lifecell.ua")

    try:
        wait_for_login(driver)
        open_client_tab(driver)

        numbers = load_numbers(INPUT_FILE)
        for number in numbers:
            try:
                input_field = get_input_field(driver)
                input_field.click()
                input_field.clear()
                input_field.send_keys(number)

                click_search(driver)
                status_element = wait_for_status(driver)
                status_text = status_element.text.strip()
                status_classes = status_element.get_attribute("class") or ""

                if "support" in status_classes and status_text == "LTE":
                    append_number(OUTPUT_VALID, number)
                    register_package(driver)
                    click_back(driver)
                else:
                    append_number(OUTPUT_INVALID, number)
                    click_back(driver)

                time.sleep(1)
            except (TimeoutException, WebDriverException) as exc:
                append_number(OUTPUT_INVALID, f"{number} — ERROR: {exc}")
                try:
                    click_back(driver)
                except (TimeoutException, WebDriverException):
                    pass
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
