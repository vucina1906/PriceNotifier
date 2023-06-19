from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from bs4 import BeautifulSoup
import smtplib
import time

app = Flask(__name__)

scheduler = BackgroundScheduler()
scheduler.start()
scheduler_started = False

def send_email():
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login('youremailadress', 'yourapspassword')
    
    subject = "Snizena cena proizvoda koji pratite/Price is reduced on the products you are following"
    body = "Postovani, cena proizvoda koji pratite je snizena i ispunjava kriterijume koje ste zadali! Ne propusite priliku da kupite ovaj proizvod! / The price of the product you are following has been reduced and it meets the criteria you set! Don't miss the opportunity to buy this product!"
   
    msg = f"Subject: {subject}\n\n{body}"
    
    server.sendmail(
        'youremailadress',
        'youremailadress',
        msg
    )

def check_price(product_url, product_price):
    URL = product_url
    
    headers = {
        "User-Agent": "your user agent",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1"
    }

    page = requests.get(URL, headers=headers)
    soup1 = BeautifulSoup(page.content, "html.parser")
    soup2 = BeautifulSoup(soup1.prettify(), 'html.parser')

    price_element = soup2.find('h2', class_='AdViewInfo_price__RLvIy')

    price_text = price_element.get_text(strip=True)
    number_str = price_text.split(":")[1].split(" ")[0].replace(".", "")
    price = int(number_str)
    if price <= product_price:
        send_email()

@app.route('/', methods=['GET'])
def welcome():
    return render_template('home.html', scheduler_started=scheduler_started)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    global scheduler_started
    product_url = request.form.get('product_url')
    product_price = request.form.get('product_price')
    product_frequency = request.form.get('product_frequency')

    scheduler.add_job(
        check_price,
        'interval',
        minutes=int(product_frequency),
        args=(product_url, int(product_price))
    )
    scheduler_started = True
    
    return render_template('home.html', scheduler_started=scheduler_started)

if __name__ == '__main__':
    app.run(port=3000, debug=True)
