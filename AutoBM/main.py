try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
except ImportError: raise ImportError("Selenium not found")

try:
    from lxml.etree import HTML
    from lxml.html import tostring
except: raise ImportError("lxml not found")
import time
from configparser import ConfigParser
from pdb import set_trace as breakpoint
from pdb import post_mortem
import logging

def configread(): # reads the config.ini files for use
    config = ConfigParser()
    config.read("config.ini")
    return config

def listofconvo(driver): # EXPERIMENTAL CODE, PLEASE REPORT ANY FUCKUPS TO BONAKTAN
    convo = HTML(driver.find_elements(By.XPATH,
            '//div[@role="grid"]')[1].get_attribute("outerHTML")).xpath("div/div/*")
    convo = [message.xpath("div/div/*") for message in convo]
    for i in convo:
        if len(i) == 5: del i[1]
    convo = [[tostring(i[0], method='text'),
              i[1].xpath("div[2]/div[1]/div[1]/div[1]/span")[0]]
             for i in convo if len(i) >= 3]
    convo = [i for i in convo if i != []]

    for message in convo:
        content = tostring(message[1], method='text')
        if content == b'':
            content = message[1].xpath("div/div/a/div[1]/div/div/div/div/img")[0]
            message[1] = content.get("src").encode()
        else: message[1] = content
    convo = [[i.decode("utf-8").strip() for i in message] for message in convo]
    return convo




def main():
    # for termux, make sure vncserver is working properly,
    config = configread(); debug = config["Developer"].getboolean("Debug")
    options = Options(); options.headless = not debug
    logging.basicConfig(level=logging.INFO if debug else logging.WARNING)

    logging.info(f"Launching Firefox {'in debug' if debug else ''}")
    with webdriver.Firefox(options=options) as driver:
        driver.install_addon("plugins/ublock_origin.xpi", temporary=True) # DEBUG

        driver.get("https://www.messenger.com/login")
        logging.info("Fetched Messenger")
        form = driver.find_element(By.ID, "login_form") # returns a <form> element
        driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[2].value = arguments[3];",
            form.find_element(By.NAME, "email"), config["Login"]["Email"],
            form.find_element(By.NAME, "pass"), config["Login"]["Password"])
        logging.info("Signing In")
        form.submit()
        time.sleep(5)

        logging.info("Loading Converdation")
        driver.get(config["Chats"]["MonitorChat"])
        while True:
            try: driver.find_elements(By.XPATH, "//div[@role='grid']")[1]
            except: continue
            break
        logging.info("Monitoring")
        breakpoint()
        try:
            convo = listofconvo(driver)
            old = convo[-1]
            while True:
                convo = [i for i in listofconvo(driver)]
                if convo[-1] != old:
                    print(f"{convo[-1][0]}: {convo[-1][1]}"); old=convo[-1]
        except: post_mortem()
if __name__ == "__main__": main()
