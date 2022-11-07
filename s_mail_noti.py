import time
import smtplib, ssl
from colorama import init, Fore, Back, Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

init(convert=True)

smtp_server = "ZZZ"
port = 465  # For starttls
sender_email = "ZZZ"
receiver_email = "ZZZ"
password = "ZZZ"

driver_path = "ZZZ"

context = ssl.create_default_context()

DOMAIN = "https://www.schadeautos.nl"
URL = "https://www.schadeautos.nl/pl/szukaj/uszkodzony/samochody-osobowe/1/1/0/0/0/0/1/0"

def openUrl(url, checkClass):
    service = Service(driver_path)

    options = Options()
    options.headless = True # brak okienka
    options.add_argument("--window-size=1920,1800")

    driver = webdriver.Chrome(options=options, service=service)
    driver.get(url)
    ret = ''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(('class name', checkClass)))
    except TimeoutException:
        print(f'{Fore.YELLOW}ERR OPEN:\n{url}')
    else:
        ret = driver.page_source
        print(f'{Fore.GREEN}OK OPEN:\n{url}')
    finally:
        driver.quit()
        return ret


def checkContent():
    list = []
    html = openUrl(URL, "car")
    bs = BeautifulSoup(html, 'html.parser')

    contents = bs.find_all('div', class_="car")
    for content in contents:
        try:
            title = content.find("h2").text.strip()

            url = DOMAIN + content.find('a')['href']

            img = DOMAIN + content.find('img')['src']

            price = content.find("div", class_="label-price")
            if not price: price = content.find("div", class_="price")
            if not price: price = 0
            else: price = price.text.strip()

            year = content.find("div", attrs={"title":"data pierwszej rejestracji"}).text.strip()

            fuel = content.find("div", attrs={"title":"rodzaj paliwa"}).text.strip()

            distance = content.find("div", attrs={"title":"przebieg"}).text.strip()

            list.append([title,url,price,year,fuel,distance,img])
        except:
            print(f"{Fore.RED}ERR car details") 

    return list


def sendMail(car):

    subject = f"{car[0]}, {car[2]}, Rok: {car[3]}, {car[5]}"

    body = f"<!DOCTYPE html><html><body>Link: {car[1]}\n<img src='{car[6]}'>\nAutomatycznie wygenerowane.</body></html>"
    message = f'Subject: {subject}\n\n{body}'
    message = f"Subject: dwa\n\n<!DOCTYPE html><html><body>Link:Automatycznie wygenerowane.</body></html>"
    #message = message.encode("ascii","ignore")
    message = message.strip()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:

        server.login(sender_email , password)

        global maxMail
        if maxMail < 4:
            maxMail += 1

            server.sendmail(sender_email, receiver_email, message)

            print(f"{Fore.YELLOW}Wyslano Mail: {message}")


def compare(xB,yB):

    for y in yB:
        checkFlag = False

        for x in xB:
            if y[1] == x[1]: checkFlag = True

        if not checkFlag: 
            print(f"{Fore.YELLOW}{y[0]}, {y[2]}, {y[3]}, {y[4]}, {y[5]}")
            sendMail(y)
    
firstTime = True
listHolder = []
maxMail = 0

while True:

    t = time.strftime("%H:%M:%S  %d/%m/%Y", time.gmtime())
    print (f"{Fore.MAGENTA}Time: {t}")
    list = checkContent()

    if firstTime:
        firstTime = False
        listHolder = list
        sendMail(listHolder[0])
    else:
        compare(listHolder, list)
        listHolder = list
    time.sleep( 60*5 )