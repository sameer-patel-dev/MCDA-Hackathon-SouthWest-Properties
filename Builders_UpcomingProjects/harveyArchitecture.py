from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def harveyArchitecture_script():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })


    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    driver.maximize_window()
    driver.get('https://www.harveyarchitecture.com/portfolio/')

    projects_wrapper = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/div/div[1]/div[1]/div/div/div/div/div/h3/a')
    projects_wrapper.click()
    sleep(3)

    # answer = []
    # for index, project in enumerate(parent_divs):
    #     try:
    #         print(index)
    #         sleep(5)
    #         driver.get('https://www.harveyarchitecture.com/portfolio/')
    #         projects_wrapper = driver.find_element(By.ID, 'portfolio-2')
    #         parent_divs = projects_wrapper.find_elements(By.XPATH, "./div")
    #         parent_divs[index].click()



    #     except Exception as e:
    #         print(f"Error processing project at index {index}: {str(e)}")
    #         break

            
    #         sleep(3)



    # driver.close()
    # # return answer


def main():
    result = harveyArchitecture_script()
    print(result)


if __name__ == "__main__":
    main()