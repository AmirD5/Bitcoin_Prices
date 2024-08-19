import requests
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import smtplib
from email.mime.text import MIMEText
import logging
import json
from datetime import datetime
import pytz


def config_logging():
    """configures the logging type and creates a console handler so all the logging information will print on console"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='bitcoin_price_log.log',
        filemode='w'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)


def fetch_btc_prices():
    """fetching the current btc price, and converting the time format from UTC to GMT+2(Jerusalem time)"""
    try:
        url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        price_usd = data['bpi']['USD']['rate_float']
        utc_time = datetime.strptime(data["time"]["updated"], "%b %d, %Y %H:%M:%S UTC")
        jerusalem_tz = pytz.timezone('Asia/Jerusalem')
        price_time = utc_time.replace(tzinfo=pytz.utc).astimezone(jerusalem_tz)

        price_time_str = price_time.strftime('%H:%M:%S')

        logging.info(f"Fetched Bitcoin price at {price_time_str}: ${price_usd:.2f}")
        return {"time": price_time_str, "price": price_usd}

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Bitcoin price: {e}")
        return None


def save_to_file(prices, filename="btc_price.json"):
    """Saves the information to a JSON file with each element on a new line."""
    try:
        json_string = json.dumps(prices, separators=(',', ':'))
        json_string = json_string.replace('},{', '},\n{') #makes json nicer to read

        with open(filename, 'w') as file:
            file.write("[" + json_string[1:-1] + "\n]\n")

        logging.info(f"Saved {len(prices)} prices to {filename}")
    except IOError as e:
        logging.error(f"Error saving prices to file: {e}")


def collect_prices_for_an_hour():
    """creates a prices list for BTC every minute for an hour"""
    prices = []
    for i in range(60):
        price = fetch_btc_prices()
        if price is not None:
            prices.append(price)
            save_to_file(prices)
        else:
            logging.warning("Skipped saving price due to fetch error")
        if i != 59:
            time.sleep(60)
    return prices


def plot_bitcoin_prices(prices):
    """created a plot for the prices of BTC in the last hour"""
    times = [datetime.strptime(entry['time'], '%H:%M:%S') for entry in prices]
    values = ([entry['price'] for entry in prices])
    plt.rcdefaults()
    plt.figure(figsize=(15, 9))
    plt.plot(times, values, marker='o', linestyle='--', color='b')
    plt.title('BTC Price Index (BPI) - Last Hour')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def send_email(max_price, max_time):
    """connect to Gmail SMTP server using SSL and sending an email for the max price in the last hour"""
    sender_email = "AmirD0407@gmail.com"
    receiver_email = "AmirD0407@gmail.com"

    subject = "Bitcoin Price Index (BPI) - Maximum Price Last Hour"
    body = f"The maximum Bitcoin price in the last hour was ${max_price:.2f} at {max_time}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        logging.info("sending email...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, "Input app password here")
            server.sendmail(sender_email, receiver_email, msg.as_string())
        logging.info(f"Sent email to {receiver_email} with max price ${max_price:.2f} at {max_time}")
    except smtplib.SMTPException as e:
        logging.error(f"Error sending email: {e}")


def send_max_price(prices):
    """finds the max price and time of that price then uses the send_email function"""
    max_entry = max(prices, key=lambda entry: entry['price'])
    max_price = max_entry['price']
    max_time = max_entry['time']
    send_email(max_price, max_time)


def main():
    config_logging()
    logging.info("Starting the Bitcoin price tracking script.")
    try:
        prices = collect_prices_for_an_hour()
        if prices:
            logging.info("Collected prices successfully.")
            send_max_price(prices)
            plot_bitcoin_prices(prices)
        else:
            logging.warning("No prices were collected, skipping graph generation and email.")
    except Exception as e:
        logging.critical(f"Critical failure in the main function: {e}")
    logging.info("Script completed.")


if __name__ == "__main__":
    main()
