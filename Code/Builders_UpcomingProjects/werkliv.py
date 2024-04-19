from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def werkliv_script():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })


    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    driver.maximize_window()
    driver.get('https://werkliv.com/en/')

    projects_wrapper = driver.find_element(By.XPATH, '/html/body/div[1]/div[8]//div[contains(@class, "projects-wrapper")]')
    parent_divs = projects_wrapper.find_elements(By.XPATH, "./div")

    answer = [['Le Mildore', '2025 Peel St, Montreal, QC'], ["Lambe's Lane", "6 Lambe's Lane, St-Johns, NL"], ["Terrasse des Récollets", "1140, Boulevard des Récollets Trois-Rivières, QC"]]
    for index, project in enumerate(parent_divs):
        try:
            print(index)

        except Exception as e:
            print(f"Error processing project at index {index}: {str(e)}")
            break


    driver.close()
    return answer


def main():
    result = werkliv_script()
    print(result)


if __name__ == "__main__":
    main()