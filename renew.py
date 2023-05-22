from selenium import webdriver
from getpass import getpass
from time import sleep
from sys import argv
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import requests
import random
# from deep_translator import GoogleTranslator


def method1():
    return browser \
        .find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/div[2]/div/div/div[1]/div[1]/table/tbody") \
        .find_elements(By.TAG_NAME, "tr")


def method2():
    return browser \
        .find_element(By.ID, "host-panel") \
        .find_element(By.TAG_NAME, "table") \
        .find_element(By.TAG_NAME, "tbody") \
        .find_elements(By.TAG_NAME, "tr")


def translate(text):
    # return GoogleTranslator(source='auto', target='en').translate(text=text)
    return "Confirm"


def get_user_agent():
    return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    
    # It takes veeeeery long for http-request
    r = requests.get(url="https://jnrbsn.github.io/user-agents/user-agents.json")
    if r.status_code == 200 and len(list(r.json())) > 0:
        agents = r.json()
        return list(agents).pop(random.randint(0, len(agents) - 1))
    else:
        return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"


if __name__ == "__main__":
    LOGIN_URL = "https://www.noip.com/login?ref_url=console"
    HOST_URL = "https://my.noip.com/dynamic-dns"
    LOGOUT_URL = "https://my.noip.com/logout"

    # ASK CREDENTIALS
    if len(argv) == 3:
        email = argv[1]
        password = argv[2]
    else:
        email = str(input("Email: ")).replace("\n", "")
        password = getpass("Password: ").replace("\n", "")
    print(argv[0])

    # OPEN BROWSER
    print("-----------------------------------------------")
    now = datetime.now() 
    print(now , "  Opening browser\n")
    browserOptions = webdriver.FirefoxOptions()
    browserOptions.add_argument("--headless")
    browserOptions.add_argument("--no-sandbox")
    browserOptions.add_argument("disable-gpu")
    browserOptions.add_argument("user-agent=" + str(get_user_agent()))
    browserOptions.set_preference("intl.accept_languages", "en-US")

    browser = webdriver.Firefox(options=browserOptions)

    # LOGIN
    print("Opening login-url\n")
    browser.get(LOGIN_URL)

    if browser.current_url == LOGIN_URL:

        browser.find_element(By.NAME, "username").send_keys(email)
        field_pwd = browser.find_element(By.NAME, "password")
        field_pwd.send_keys(password)
        #field_pwd.send_keys(Keys.ENTER)
        #print("send_keys RETURN")

        login_button = False

        for button in browser.find_elements(By.TAG_NAME, "button"):
            if button.text == "Log In" or button.text == "Anmelden":
                print("Found button:" + button.text)
                button.click()
                print("Clicked Login_button")
                login_button = True
                break

        if not login_button:
            print("Login button has changed. Please contact support. ")
            exit(1)

        sleep(0.5)

        #print(browser.get_full_page_screenshot_as_base64())
        if str(browser.current_url).endswith("noip.com/"):

            print("Login successful:" + str(browser.current_url))
            print("\nFetching Hosts-Url:" + HOST_URL)
            browser.get(HOST_URL)
            sleep(0.20)

            aux = 1
            while not browser.title.startswith("My No-IP") and aux < 4:
                print("check BrowserTitle:" + browser.title + " Try:" + aux)
                browser.get(HOST_URL)
                sleep(0.25)
                aux += 1

            if browser.title.startswith("My No-IP") and aux < 5:
                print("Success with:" + browser.title)
                confirmed_hosts = 0

                # RENEW HOSTS
                try:
                    hosts = method2()
                    print("\nLooking for Hosts:")

                    for host in hosts:
                        try:
                            button = host.find_element(By.TAG_NAME, "button")
                        except NoSuchElementException as e:
                            print("Host-button not found")
                            break

                        print("Details for: " + host.find_element(By.TAG_NAME, "td").find_element(By.CLASS_NAME, "link-info").text)
                        #print(browser.find_elements(By.TAG_NAME, "td")[3].text)
                        #print("Host: ")
                        print("-------------------")
                        for td in browser.find_elements(By.TAG_NAME, "td"):
                            print(td.text)
                            if "IP / Target" == td.get_attribute("data-title"):
                                break
                        print("-------------------")


                        try:
                            days_label = host.find_element(By.CLASS_NAME, "no-link-style")
                            print("Label: " + days_label.text)
                            print(days_label.get_attribute("data-original-title"))
                            print("Found Host-Button: " + button.text)
                        except NoSuchElementException as e:
                            print("Days_label not found")

                        if button.text == "Confirm": # or translate(button.text) == "Confirm":
                            button.click()
                            print("Click " + button.text)
                            confirmed_hosts += 1
                            confirmed_host = host.find_element(By.TAG_NAME, "a").text
                            print("\nHost \"" + confirmed_host + "\" confirmed")
                            sleep(0.20)

                        #elif button.text == "Modify":
                            #button.click()
                            #print("Click " + button.text)
                            #sleep(0.20)
                            ##print(browser.get_full_page_screenshot_as_base64())
                            #ip_value = browser.find_element(By.NAME, "target").get_attribute("placeholder")
                            #print("Read Info from 'Modify-modal:' " + ip_value)
                            #print(browser.find_elements(By.CLASS_NAME, "modal-title").text)
                            ##//*[@id="content-wrapper"]/div[4]/div/div/div/div[3]/div/div[2]

                    if confirmed_hosts == 0:
                        print("\nNo host for confirm\n")
                    elif confirmed_hosts == 1:
                        print("\n1 host confirmed\n")
                    else:
                        print(str(confirmed_hosts) + " hosts confirmed\n")

                    print("Finished with hosts")

                except Exception as e:
                    print("Error: ", e)

                finally:
                    print("Logging off")
                    print(LOGOUT_URL)
                    browser.get(LOGOUT_URL)
        else:
            print("\nError: cannot login. Check if account is not blocked.")
            print("Logging off\n")
            browser.get(LOGOUT_URL)
    else:
        print("Cannot access login page:\t"   + LOGIN_URL)
        print("\nProvided browser page is:\t" + browser.current_url)

    browser.quit()
