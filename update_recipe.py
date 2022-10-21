import random
import time
from unittest import result
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By


def get_driver():

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent=Mozilla/5.{random.randint(1,9999)} (Windows NT 10.0; Win64; x647) AppleWebKit/537.{random.randint(1,9999)} (KHTML, like Gecko) Chrome/98.0.4788.{random.randint(1,9999)} Safari/557.36")
    driver = webdriver.Chrome(executable_path="chromedriver.exe", 
                            options=options,
                            desired_capabilities=caps,
                            )
    return driver

if __name__ == '__main__':


    driver = get_driver()

    driver.get('https://retext.ai/ru')

    input_area_xpath = '//*[@id="__next"]/div/div[3]/div/div/div[1]/div[2]/div[1]/div[1]/div/div[2]/div'


    text = 'Шоколад разломать на кусочки и вместе со сливочным маслом растопить на водяной бане, не переставая все время помешивать лопаткой или деревянной ложкой. Получившийся густой шоколадный соус снять с водяной бани и оставить остывать.'

    driver.find_element(By.XPATH, input_area_xpath).send_keys(text)

    submit_btn = '//*[@id="__next"]/div/div[3]/div/div/div[1]/div[3]/button'
    driver.find_element(By.XPATH, submit_btn).click()


    rounds = 10
    while True:

        status_xpath = '//*[@id="__next"]/div/div[3]/div/div/div[2]/div[1]/div/div/div[1]'

        status = driver.find_element(By.XPATH, status_xpath).text
        if not 'загрузка' in status.lower():
            rounds -= 1
            if not rounds:
                break
            time.sleep(0.2)
        else:
            rounds = 10


    result_xpath = '//*[@id="__next"]/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/div/div/div'
    result = driver.find_element(By.XPATH, result_xpath).text

    print()

