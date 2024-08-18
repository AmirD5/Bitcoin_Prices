Overview:
This Python script tracks the Bitcoin Price Index (BPI) using the CoinDesk API. It fetches the current Bitcoin price every minute for an hour, saves the data to a JSON file, and generates a plot to visualize the price trend. Additionally, it sends an email notification with the highest price recorded during the hour.

Features:
Logging: Logs all actions and errors to both the console and a log file (bitcoin_price_log.log).
Fetch Bitcoin Prices: Retrieves the current Bitcoin price from the CoinDesk API every minute, adjusted to Jerusalem time (GMT+2).
Save Data: Saves the fetched prices to a JSON file (btc_price.json).
Plot Data: Generates a plot of the Bitcoin prices over the last hour.
Email Notification: Sends an email with the maximum Bitcoin price during the last hour.

Requirements:
Python 3.6+
External Python libraries:
requests
matplotlib
smtplib
email
json
logging
datetime
pytz
