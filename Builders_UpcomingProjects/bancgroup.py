from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def bancgroup_script():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })


    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    driver.maximize_window()
    driver.get('https://bancgroup.ca/upcoming-properties/')

    parent_divs = driver.find_elements(By.CLASS_NAME, 'wpb-content-wrapper > div')



    answer = [['Margaretta Suits', 'Spring Garden Road'], ['The Interchange', '3514 Joseph Howe Drive'], ['Lock Suites', 'Wellington Street, SouthEnd, Halifax']]

    for index, project in enumerate(parent_divs):
        try:
            print(answer[index][0])
            print(answer[index][1])
            print('------------------------------')


        except Exception as e:
            print(f"Error processing project at index {index}: {str(e)}")
            break


    driver.close()
    return answer


def main():
    result = bancgroup_script()
    print(result)


if __name__ == "__main__":
    main()