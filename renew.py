from builtins import print

from selenium import webdriver
from getpass import getpass
from time import sleep
from sys import argv
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

LOGIN_URL = "https://www.noip.com/login?ref_url=console"
MY_NOIP_URL = "https://my.noip.com/dynamic-dns"
LOGOUT_URL = "https://my.noip.com/logout"
LOGOUT_PATH = "/logout"


def doTraceLog(on_off, str_string):
    if on_off:
        print(str_string)


# def findHosts_method1():
#    return browser \
#        .find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/div[2]/div/div/div[1]/div[1]/table/tbody") \
#        .find_elements(By.TAG_NAME, "tr")

def findHosts_method2(browser):
    return browser \
        .find_element(By.ID, "host-panel") \
        .find_element(By.TAG_NAME, "table") \
        .find_element(By.TAG_NAME, "tbody") \
        .find_elements(By.TAG_NAME, "tr")


def get_user_agent():
    return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    # return now this above because:
    # It takes veeeeery long for http-request (so unreachable)
    # r = requests.get(url="https://jnrbsn.github.io/user-agents/user-agents.json")
    # if r.status_code == 200 and len(list(r.json())) > 0:
    #    agents = r.json()
    #    return list(agents).pop(random.randint(0, len(agents) - 1))
    # else:
    #  return "Mozilla/5.0 (X11;Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"


def doLogOut_post_rq(browser, path, params):
    """
    Workaround for Selenium, because browser can't send POST-request for LogOut like 'curl'

    :param WebDriver browser:
    :param str path:
    :param dict params:
    :return:
    """

    browser.execute_script("""
        function do_post(path, params, method='POST') {
            const form = document.createElement('form');
            form.method = method;
            form.action = path;

            for (const key in params) {
                if (params.hasOwnProperty(key)) {
                    const hiddenField = document.createElement('input');
                    hiddenField.type = 'hidden';
                    hiddenField.name = key;
                    hiddenField.value = params[key];

                    form.appendChild(hiddenField);
                }
            }

            document.body.appendChild(form);
            form.submit();
        }

        do_post(arguments[0], arguments[1]);
        """, path, params)


def main():

    trace_on_off = False

    # ASK CREDENTIALS
    if len(argv) >= 3:
        email = argv[1]
        password = argv[2]
    else:
        email = str(input("Email: ")).replace("\n", "")
        password = getpass("Password: ").replace("\n", "")

    if len(argv) > 3:  # any value for debug-TraceLog-on/off supplied?
        trace_on_off = argv[3]

    doTraceLog(trace_on_off, argv[0])

    # OPEN BROWSER
    print("-----------------------------------------------")
    now = datetime.now()
    print(now, "  \nOpening browser (wait 5 sec plz)...\n")
    browser_options = webdriver.FirefoxOptions()
    browser_options.add_argument("--headless")
    browser_options.add_argument("--no-sandbox")
    browser_options.add_argument("disable-gpu")
    browser_options.add_argument("user-agent=" + str(get_user_agent()))
    browser_options.set_preference("intl.accept_languages", "en-US")

    browser = webdriver.Firefox(options=browser_options)

    # LOGIN
    print("Opening login-url (wait 7 sec)... ")
    browser.get(LOGIN_URL)

    if browser.current_url == LOGIN_URL:
        doTraceLog(trace_on_off, "...entering noip-login credentials...\n")
        browser.find_element(By.NAME, "username").send_keys(email)
        field_pwd = browser.find_element(By.NAME, "password")
        field_pwd.send_keys(password)
        # field_pwd.send_keys(Keys.RETURN)
        # doTraceLog("send_keys RETURN")

        login_status = False

        for button in browser.find_elements(By.TAG_NAME, "button"):
            if button.text == "Log In" \
                    or button.text == "Anmelden" \
                    or button.text == "Entrar" \
                    or button.text == "Accedi" \
                    or button.text == "Iniciar Sesión":
                doTraceLog(trace_on_off, "Found button: '" + button.text + "', Waiting for Click...")
                button.click()
                doTraceLog(trace_on_off, "Clicked 'Log In' button")
                login_status = True
                break

        if not login_status:
            print("Login button has changed. Please check script or contact support. ")
            exit(1)

        sleep(0.100)

        # print(browser.get_full_page_screenshot_as_base64())
        if str(browser.current_url).endswith("noip.com/"):

            print("Login successful")
            doTraceLog(trace_on_off, str(browser.current_url) + ' |' + browser.title)
            doTraceLog(trace_on_off, "\nFetching Hosts-Url:" + MY_NOIP_URL + " ...")
            browser.get(MY_NOIP_URL)
            sleep(0.100)

            aux = 1
            while not browser.title.startswith("My No-IP") and aux < 4:
                print("check BrowserTitle:" + browser.title + " Attempt:" + str(aux))
                browser.get(MY_NOIP_URL)
                sleep(0.250)
                aux += 1

            if browser.title.startswith("My No-IP") and aux < 5:
                doTraceLog(trace_on_off, "Success with:" + str(browser.current_url) + ' |' + browser.title)
                confirmed_hosts = 0

                # RENEW HOSTS
                try:
                    hosts = findHosts_method2(browser)
                    doTraceLog(trace_on_off, "\nLooking for Hosts:")

                    for host in hosts:
                        print("Details for: " + host.find_element(
                            By.TAG_NAME, "td").find_element(
                            By.CLASS_NAME, "link-info").text)
                        print("-------------------")

                        for td in browser.find_elements(By.TAG_NAME, "td"):
                            doTraceLog(trace_on_off, td.text)
                            if "IP / Target" == td.get_attribute("data-title"):
                                # not needed all other info's
                                break
                        doTraceLog(trace_on_off, "-------------------")

                        try:
                            days_label = host.find_element(By.CLASS_NAME, "no-link-style")
                            print("Host_Label: " + days_label.text)
                            if days_label.get_attribute("data-original-title"):
                                print(days_label.get_attribute("data-original-title"))

                        except NoSuchElementException:
                            print("'Days_label' not found")

                        try:
                            button = host.find_element(By.TAG_NAME, "button")
                            doTraceLog(trace_on_off, "Found Host-Button: " + button.text)
                        except NoSuchElementException:
                            print("Host-button not found")
                            break

                        if button.text == "Confirm" \
                                or button.text == "Bestätigen" \
                                or button.text == "Conferma" \
                                or button.text == "Confirmar":
                            # # browser.get_full_page_screenshot_as_file('01_found_confirm-button.png')
                            doTraceLog(trace_on_off, "Click: " + button.text)
                            button.click()
                            sleep(0.200)
                            # # print(browser.get_full_page_screenshot_as_base64())
                            # # browser.get_full_page_screenshot_as_file('02_after_clicked_confirm.png')
                            for button in browser.find_elements(By.TAG_NAME, "a"):
                                if button.text.startswith("No thanks"):
                                    print("== ALARM !!! Emergency mode! ==")
                                    print("Found Element:" + button.text)
                                    print("Click: " + button.text)
                                    button.click()
                                    print("Waiting for Captcha (not implemented yet)...")
                                    print("...Just please check and confirm hosts manually, when errors appear.")
                                    print("-------------------")
                                    # Doku: after unconfirmed expiration period host become "blocked" status",
                                    # and you need reset/confirm it unlikely with Captcha
                                    # manually back to "active" status.

                            # browser.get_full_page_screenshot_as_file('03.png')
                            confirmed_hosts += 1
                            confirmed_host = host.find_element(By.TAG_NAME, "a").text
                            print("\nHost \"" + confirmed_host + "\" confirmed")
                            sleep(0.100)

                        print("===================")

                        # for testing purposes:
                        # elif button.text == "Modify":
                        # button.click()
                        # print("Click " + button.text)
                        # sleep(0.200)
                        # #print(browser.get_full_page_screenshot_as_base64())
                        # ip_value = browser.find_element(By.NAME, "target").get_attribute("placeholder")
                        # print("Read Info from 'Modify-modal:' " + ip_value)
                        # print(browser.find_elements(By.CLASS_NAME, "modal-title").text)
                        # #//*[@id="content-wrapper"]/div[4]/div/div/div/div[3]/div/div[2]

                    if confirmed_hosts == 0:
                        print("\nNo host(s) for confirm\n")
                    elif confirmed_hosts == 1:
                        print("\n1 host confirmed\n")
                    else:
                        print(str(confirmed_hosts) + " hosts confirmed\n")

                    doTraceLog(trace_on_off, "Finished with hosts")

                except Exception as e:
                    print("Error: ", e)

                finally:
                    # print(browser.get_full_page_screenshot_as_base64())
                    # browser.get_full_page_screenshot_as_png()
                    doTraceLog(trace_on_off, "\nLogging off, exec JS-function...")
                    # browser.get(LOGOUT_URL) - not working, need 'special' POST-request
                    doLogOut_post_rq(browser, path=LOGOUT_PATH, params={})
                    doTraceLog(trace_on_off, "browser page is: " + browser.current_url)
                    doTraceLog(trace_on_off, "Waiting...")
                    attmpt = 0
                    while browser.title.startswith("My No-IP"):
                        sleep(0.010)
                        attmpt += 10
                    doTraceLog(trace_on_off, "Awaited LogOut for: " + str(attmpt) + "ms")
                    doTraceLog(trace_on_off, "browser page is: " + browser.current_url)
                    doTraceLog(trace_on_off, "Changed BrowserTitle: " + browser.title)
                    doTraceLog(trace_on_off, "NoIP logged out...")

        else:
            print("\nError: cannot login. Check if account is not blocked.")
            print(browser.current_url, browser.title)
            print("NoIP - Log off\n")
            browser.get(LOGOUT_URL)
    else:
        print("Cannot access login page:\t" + LOGIN_URL)
        print("\nProvided browser page is:\t" + browser.current_url)

    doTraceLog(trace_on_off, "Close Browser...")
    browser.quit()
    doTraceLog(trace_on_off, "Browser quit.")


if __name__ == "__main__":
    main()
