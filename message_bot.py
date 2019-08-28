import base64
import json
import os
from time import sleep

import requests
from emoji import emojize
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import heroku

whatsapp_api = (
    'https://api.whatsapp.com/send?phone=91'
)  # format of url to open chat with someone

# what to send
message = (
    'insert message here'
)


def waitTillElementLoaded(browser, element):
    try:
        element_present = ec.presence_of_element_located((By.XPATH, element))
        WebDriverWait(browser, 10000).until(element_present)
    except TimeoutException:
        print('Timed out waiting for page to load')


# method to send a message to someone
def sendMessage(num, name, browser):
    api = whatsapp_api + str(num)  # specific url
    print(api, name)
    browser.get(api)  # open url in browser

    waitTillElementLoaded(browser, '//*[@id="action-button"]')  # wait till send message button is loaded
    browser.find_element_by_xpath('//*[@id="action-button"]').click()  # click on "send message" button

    # wait till the text box is loaded onto the screen, then type out and send the full message
    waitTillElementLoaded(browser, '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]')

    browser.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div[2]/div/div[2]'
    ).send_keys(emojize(message.format(name), use_aliases=True))

    sleep(3)  # just so that we can supervise, otherwise it's too fast


def startSession():
    browser = webdriver.Firefox(executable_path='geckodriver.exe')
    browser.get('https://web.whatsapp.com/')

    # get the qr image
    waitTillElementLoaded(browser, '/html/body/div[1]/div/div/div[2]/div[1]/div/div[2]/div/img')
    if os.path.exists('qr.png'):
        print('removing old qr')
        os.remove('qr.png')
    meow = open('qr.png', 'wb')
    meow.write(base64.b64decode(browser.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[2]/div[1]/div/div[2]/div/img').get_attribute('src')[22:]))
    meow.close()

    return browser


def getData(url, token):
    names = []  # list of all names
    numbers = []  # list of all numbers

    # get data from heroku
    data = json.loads(requests.get(url, headers={'Authorization': token}, ).text)

    # add names and numbers to respective lists
    for user_id in data:
        names.append(data[user_id]['name'])
        numbers.append(data[user_id]['phone'].split('|')[-1])

    return names, numbers


if __name__ == '__main__':

    # get data from heroku
    names, numbers = getData(heroku.url, heroku.token)

    # create a browser instance, login to whatsapp (one time per run)
    webbrowser = startSession()

    # wait till the text box is loaded onto the screen
    waitTillElementLoaded(webbrowser, '/html/body/div[1]/div/div/div[4]/div/div/div[1]')

    # send messages to all entries in file
    for num, name in zip(numbers, names):
        sendMessage(num, name, webbrowser)

    webbrowser.close()  # close browser
