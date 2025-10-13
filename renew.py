from builtins import print

from selenium import webdriver
from getpass import getpass
from time import sleep
from sys import argv
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGIN_URL = "https://www.noip.com/login?ref_url=console"
MY_NOIP_URL = "https://my.noip.com/dns/records"
LOGOUT_URL = "https://my.noip.com/auth/logout"
LOGOUT_PATH = "/auth/logout"

CONFIRM_BTN_TEXTS = {"Confirm", "Bestätigen", "Conferma", "Confirmar"}
LOGIN_BTN_TEXTS = {"Log In", "Anmelden", "Entrar", "Accedi", "Iniciar Sesión"}



def show_time_diff(on_off, time_stp):
    if on_off:
        time_diff = datetime.now() - time_stp
        time_stp = datetime.now()
        print("> Time_diff: " + time_diff.__str__() + " ms")
        return time_stp


def do_trace_log(on_off, str_string):
    if on_off:
        print(str_string)


def init_browser():
    browser_options = webdriver.FirefoxOptions()
    browser_options.add_argument("--headless")
    browser_options.add_argument("--no-sandbox")
    browser_options.add_argument("disable-gpu")
    browser_options.add_argument("user-agent=" + str(get_user_agent()))
    browser_options.set_preference("intl.accept_languages", "en-US")
    browser = webdriver.Firefox(options=browser_options)
    return browser


# def findHosts_method1():
#    return browser \
#        .find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/div[2]/div/div/div[1]/div[1]/table/tbody") \
#        .find_elements(By.TAG_NAME, "tr")

# def findHosts_method2(browser):
#     return browser \
#         .find_element(By.ID, "host-panel") \
#         .find_element(By.TAG_NAME, "table") \
#         .find_element(By.TAG_NAME, "tbody") \
#         .find_elements(By.TAG_NAME, "tr")


def find_confirm_buttons(browser):
    buttons = browser \
        .find_element(By.ID, "zone-collection-wrapper") \
        .find_elements(By.TAG_NAME, "button")

    confirm_filtered = []
    for button in buttons:
        if button.text in CONFIRM_BTN_TEXTS:
            confirm_filtered.append(button)

    return confirm_filtered


def get_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"
    # return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    # return now this above because:
    # It takes veeeeery long for http-request (so unreachable)
    # r = requests.get(url="https://jnrbsn.github.io/user-agents/user-agents.json")
    # if r.status_code == 200 and len(list(r.json())) > 0:
    #    agents = r.json()
    #    return list(agents).pop(random.randint(0, len(agents) - 1))
    # else:
    #  return "Mozilla/5.0 (X11;Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36"


def do_logout_post_rq(browser, path, params):
    """
    Workaround for Selenium, because browser can't send POST-request for LogOut like 'curl'
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


def do_login(browser, email, password, login_status, time_st, trace_on_off):
    """
    Check avaliability of LogIn-button and click it to login
    """
    do_trace_log(trace_on_off, "> ...entering noip-login credentials...")
    browser.find_element(By.NAME, "username").send_keys(email)
    browser.find_element(By.NAME, "password").send_keys(password)
    time_st = show_time_diff(trace_on_off, time_st)

    for button in browser.find_elements(By.TAG_NAME, "button"):
        if button.text in LOGIN_BTN_TEXTS:
            do_trace_log(trace_on_off, "\n> Found button: '" + button.text + "', Waiting for Click-response...")
            button.click()
            time_st = show_time_diff(trace_on_off, time_st)
            do_trace_log(trace_on_off, "> Clicked 'Log In' button")
            login_status = True
            break

    return login_status, time_st


def fetch_hosts_page(browser, trace_on_off):
    """GET Hosts-page with Confirm-buttons"""
    do_trace_log(trace_on_off, "\n> Fetching Hosts-Url:" + MY_NOIP_URL + " ...")
    browser.get(MY_NOIP_URL)
    sleep(0.050)
    aux = 1
    # double-check safe transit to Hosts-page
    while not browser.title.startswith("My No-IP") and aux < 4:
        print("check BrowserTitle:" + browser.title + " Attempt:" + str(aux))
        browser.get(MY_NOIP_URL)
        sleep(0.150)
        aux += 1

    return aux


def do_click_confirm_button(browser, button, confirmed_hosts, trace_on_off):
    """ Check and Click Confirm-button for Noip-host """

    host_name = browser.find_element(By.ID, "zone-collection-wrapper").find_element(By.TAG_NAME, "h4").text
    do_trace_log(trace_on_off, ">   Click: " + button.text)
    # browser.get_full_page_screenshot_as_file('000_before_click_confirm.png')  # Debug-trace
    button.click()
    # browser.get_full_page_screenshot_as_file('010_after_clicked_confirm.png')  # Debug-trace

    # wait Confirm-button disappear
    WebDriverWait(browser, 10).until(EC.staleness_of(button))
    do_trace_log(trace_on_off, ">     Confirm-button disappear")

    # wait Wrapper-container after page-reload
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, 'zone-collection-wrapper'))
    )
    do_trace_log(trace_on_off, ">     Buttons-wrapper is visible again")

    # # print(browser.get_full_page_screenshot_as_base64())          # Debug-trace
    # browser.get_full_page_screenshot_as_file('030_after_wrapper_appearing.png')
    for btn in browser.find_elements(By.TAG_NAME, "a"):
        if btn.text.startswith("No thanks"):
            print("== ALARM !!! Emergency mode! ==")
            print("Found Element:" + btn.text)
            print("Click: " + btn.text)
            btn.click()
            print("Waiting for Captcha (not implemented yet)...")
            print("...please just logIn, check and confirm hosts manually, when this error appear.")
            print("-------------------")
            # Doku: after unconfirmed expiration period (~~7 days)
            # host become "blocked" status", and you need reset/confirm it
            # unlikely with Captcha manually back to "active" status.

    # browser.get_full_page_screenshot_as_file('035_function_end.png')            # Debug-trace
    confirmed_hosts += 1
    print("Host \"" + host_name + "\" confirmed")
    print("-------------------")

    return confirmed_hosts


def do_confirm_hosts(browser, confirmed_hosts_count, trace_on_off):
    """ Main biz-logic for confirming all hosts"""
    confirm_btns = find_confirm_buttons(browser)
    do_trace_log(trace_on_off,
                 "\n> Looking for Confirm_buttons in div-wrapper: " + str(len(confirm_btns)))
    # browser.get_full_page_screenshot_as_file('01_found_confirm-button.png') # Debug-trace
    while True:
        if not confirm_btns:  # Confirm-button disappear after Click and reloading the web-page
            break

        button = confirm_btns[0]
        try:
            do_trace_log(trace_on_off, ">   Found button: " + button.text)
            do_trace_log(trace_on_off, ">   " +
                         browser.find_element(By.ID, "zone-collection-wrapper")
                         .find_element(By.TAG_NAME, "h4").text)

            confirmed_hosts_count = do_click_confirm_button(browser, button,
                                                            confirmed_hosts_count, trace_on_off)
            # find Confirm_Buttons AGAIN after click and page-reload
            confirm_btns = find_confirm_buttons(browser)

        except NoSuchElementException as e:
            do_trace_log(trace_on_off, "> 'ERROR: Click Confirm-button goes wrong...")
            print(f"Error: {type(e).__name__}: {e}")
            break
    return confirmed_hosts_count


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

    do_trace_log(trace_on_off, ">Executing: " + argv[0])

    # OPEN BROWSER
    print("-----------------------------------------------")
    time_stmp = datetime.now()
    print(time_stmp, "  \nOpening browser (wait 5-15 sec plz)..")
    if not trace_on_off: print("0%", end="")

    browser = init_browser()
    time_stmp = show_time_diff(trace_on_off, time_stmp)

    try:
        # FETCH Start-page and LOGIN
        do_trace_log(trace_on_off, "\n> Opening login-url (wait 7-15 sec)... ")
        if not trace_on_off: print("..10%", end="")
        browser.get(LOGIN_URL)
        time_stmp = show_time_diff(trace_on_off, time_stmp)
        if not trace_on_off: print("..20%", end="")

        if browser.current_url == LOGIN_URL:
            login_status = False
            if not trace_on_off: print("..30%..login...", end="")

            # DO LOGIN to NOIP
            do_trace_log(trace_on_off, "\n> Prepare to login... ")
            login_status, time_stmp = do_login(browser, email, password, login_status, time_stmp, trace_on_off)

            if not login_status:
                print("Login button has changed. Please check script or contact support. ")
                exit(1)

            # FETCH HOSTS-Records-page
            # # print(browser.get_full_page_screenshot_as_base64())   # Debug-trace
            # browser.get_full_page_screenshot_as_file('0.png') # Debug-trace
            if str(browser.current_url).endswith("noip.com/"):
                if not trace_on_off:  # just notify Login-OK by trace-off
                    print("\nLogin successful.")
                do_trace_log(trace_on_off, "> Login successful. Page-url is:")
                do_trace_log(trace_on_off, str("> " + browser.current_url) + ' |' + browser.title)

                attempts = fetch_hosts_page(browser, trace_on_off)

                # browser.get_full_page_screenshot_as_file('00.png') # Debug-trace
                if browser.title.startswith("My No-IP") and attempts < 4:
                    time_stmp = show_time_diff(trace_on_off, time_stmp)
                    do_trace_log(trace_on_off, "> Success with:" + str(browser.current_url) + ' |' + browser.title)
                    confirmed_hosts_count = 0

                    # CONFIRM_RENEW_HOSTS
                    try:
                        confirmed_hosts_count = do_confirm_hosts(browser, confirmed_hosts_count, trace_on_off)

                        if confirmed_hosts_count == 0:
                            print("No host(s) for confirm\n")
                        elif confirmed_hosts_count == 1:
                            print("1 host confirmed\n")
                        else:
                            print(str(confirmed_hosts_count) + " hosts confirmed\n")

                        time_stmp = show_time_diff(trace_on_off, time_stmp)
                        do_trace_log(trace_on_off, "> Finished with hosts")

                    except Exception as e:
                        print(f"Error while RENEW_HOSTS: {type(e).__name__}: {e}")

                    finally:
                        # LOGOFF
                        # print(browser.get_full_page_screenshot_as_base64())     # Debug-trace
                        # browser.get_full_page_screenshot_as_file('04_finally.png')
                        do_trace_log(trace_on_off, "\n> Logging off, exec JS-function...")
                        do_trace_log(trace_on_off, "> browser page is: " + browser.current_url + ' |' + browser.title)
                        # browser.get(LOGOUT_URL) - not working, need 'special' POST-request
                        do_logout_post_rq(browser, path=LOGOUT_PATH, params={})
                        do_trace_log(trace_on_off, "> Waiting...")
                        attmpt = 0
                        while browser.title.startswith("My No-IP"):
                            sleep(0.005)
                            attmpt += 5
                        do_trace_log(trace_on_off, "> Awaited LogOut for: " + str(attmpt) + " ms")
                        do_trace_log(trace_on_off, "> now browser page is: " + browser.current_url)
                        do_trace_log(trace_on_off, "> Changed BrowserTitle to: " + browser.title)
                        do_trace_log(trace_on_off, "> NoIP is logged out...")

            else:
                print("\nError: cannot login. Check if account is not blocked.")
                print(browser.current_url, browser.title)
                print("NoIP - switch to Log off\n")
                browser.get(LOGOUT_URL)
        else:
            print("Cannot access login page:\t" + LOGIN_URL)
            print("\nProvided browser page is:\t" + browser.current_url)
    finally:
        # CLOSE Browser
        time_stmp = show_time_diff(trace_on_off, time_stmp)
        do_trace_log(trace_on_off, "> Closing Browser...")
        browser.quit()
        show_time_diff(trace_on_off, time_stmp)
        do_trace_log(trace_on_off, "> Browser closed.")


if __name__ == "__main__":
    main()
