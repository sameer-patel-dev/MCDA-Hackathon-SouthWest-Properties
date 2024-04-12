from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import html
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import re



def urbanCapital_script():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })


    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    driver.maximize_window()
    driver.get('https://www.urbancapital.ca/page-current')
    project_selector = "div.summary-item-list.sqs-gallery.sqs-gallery-design-autogrid > div"
    num_projects = len(driver.find_elements(By.CSS_SELECTOR, project_selector))


    answer = []
    for index in range(num_projects):
        temp = []
        try:

            direct_child_divs = driver.find_elements(By.CSS_SELECTOR, project_selector)
            direct_child_divs[index].click()
            
            if 'halifax' in driver.current_url:
                project_details_element = driver.find_element(By.CSS_SELECTOR, "p[style='white-space:pre-wrap;']")
                project_details_text = project_details_element.text

                location_match = re.search(r"Location\s*(.*?)(?=\s*Program)", project_details_text)
                program_match = re.search(r"Program\s*(.*?)(?=\s*Architects)", project_details_text)
                architects_match = re.search(r"Architects\s*(.*?)(?=\s*Development Partner)", project_details_text)
                development_partner_match = re.search(r"Development Partner\s*(.*)", project_details_text)

                

                if location_match:
                    location = location_match.group(1)
                if program_match:
                    program = program_match.group(1)
                if architects_match:
                    architects = architects_match.group(1)
                if development_partner_match:
                    partners = development_partner_match.group(1)

                temp.append(location)
                temp.append(program)
                temp.append(architects)
                temp.append(partners)
                answer.append(temp)

            
            driver.back()
            
        except NoSuchElementException:
            print("Content element not found on the page.")

        except Exception as e:
            print(f"Error processing project at index {index}: {str(e)}")
            break

    driver.close()
    return answer



def main():
    result = urbanCapital_script()
    print(result)


if __name__ == "__main__":
    main()
