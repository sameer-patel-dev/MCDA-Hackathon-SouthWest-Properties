from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException



def dexel_script():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })


    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    driver.maximize_window()
    driver.get('https://dexel.ca/projects.html')


    #Click Future Work Button
    button = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div/div[1]/div/div/label[3]')
    button.click()


    parent_div = driver.find_element(By.CLASS_NAME, 'project-gallery')
    future_projects = parent_div.find_elements(By.XPATH, ".//div[@data-status='future']")


    answer = []
    for index, project in enumerate(future_projects):
        try:
            parent_div = driver.find_element(By.CLASS_NAME, 'project-gallery')
            future_projects = parent_div.find_elements(By.XPATH, ".//div[@data-status='future']")
            
            future_projects[index].click()

            try:
                address_elements = driver.find_elements(By.CLASS_NAME, 'address')
                for address_element in address_elements:
                    answer.append(address_element.text)

            except NoSuchElementException:
                print("Content element not found on the page.")
            

            driver.back()
            
        except Exception as e:
            print(f"Error processing project at index {index}: {str(e)}")
            break



    driver.close()
    return answer




def main():
    result = dexel_script()
    result = [address.split('\n', 1) for address in result]
    print(result)


if __name__ == "__main__":
    main()