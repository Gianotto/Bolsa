import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import threading
import sys, io
from telebot import TeleBot, util, types
import json, datetime
import time

TITLE = "Stocks"
STOCKS = ("BBAS3.SA", "BTC-USD", "BTC-BRL", "R2BL34.SA", "KLBN3.SA", "PETR4.SA", "LREN3.SA", "CYRE3.SA", "CPLE6.SA", "MDIA3.SA", "SANB11.SA", "SBFG3.SA", "BRFS3.SA", "VALE")
PERIOD = '1mo'
INTERVAL = '1wk'
UPDATE = 60

#stockdb = {
#        "BBAS3.SA": [42.0000, 49.0000],
#        "BTC-USD" : [25000.0000, 25999.0000]
#}


API_KEY = "6039135538:AAFZV6z2z-ns9I0tBG7O10M8WgKeenGa_qA"
telebot = TeleBot(API_KEY, threaded=True)

def writeData():
    with open("data_file.json", "w") as write_file:
        json.dump(stockdb, write_file)

def loadData():
    with open("data_file.json", "r") as read_file:
        return json.load(read_file)
    
stockdb = loadData()

def monitor_stocks():
    global is_alive #control while data is collected
    is_alive = True
    while is_alive:
        try:
            for stock in stockdb:
                stockyf = yf.Ticker(stock)
                pd.options.display.float_format = '{:,.2f}'.format
                data = pd.DataFrame(stockyf.history(period=PERIOD, interval=INTERVAL))
                data.index = data.index.strftime('%d/%m') # format date
                
                latest_price = data['Close'].iloc[-1]
                open = data['Open'].iloc[-1]
                high = data['High'].iloc[-1]
                low = data['Low'].iloc[-1]
                marketChange = latest_price - stockyf.info['previousClose']
                marketChangePct = ((latest_price / stockyf.info['previousClose']) - 1) * 100

                stocklow = stockdb[stock]['LOW']
                stockhigh = stockdb[stock]['HIGH']

                if latest_price <= stocklow:
                    print (f"{stock} atingiu loss em {latest_price:.4f} com target {stocklow}")
                elif latest_price >= stockhigh:
                    print (f"{stock} atingiu gain em {latest_price:.4f} com target {stockhigh}")
                else:
                    print (f"{stock} em monitoramento {latest_price:.4f}")

        except Exception as e:
            print(e)
            is_alive = False
        time.sleep(UPDATE)

def gen_graph(empresa):
    if empresa != "":
        stock = yf.Ticker(empresa)
        pd.options.display.float_format = '{:,.2f}'.format
        data = pd.DataFrame(stock.history(period=PERIOD, interval=INTERVAL))
        data.index = data.index.strftime('%d/%m') # format date

        latest_price = data['Close'].iloc[-1]
        open = data['Open'].iloc[-1]
        high = data['High'].iloc[-1]
        low = data['Low'].iloc[-1]
        marketChange = latest_price - stock.info['previousClose']
        marketChangePct = ((latest_price / stock.info['previousClose']) - 1) * 100

        # Figure for Telegrambot
        img, (bx1, bx2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(6, 5), dpi=75)
        bx1.clear()
        bx1.plot(data['Close'], color=('green' if marketChange > 0 else 'red'))
        bx1.set_ylabel('Price')
        bx1.set_title(f'{empresa}: {latest_price:.4f} | ({marketChangePct:.4f}%) | {PERIOD}\nOpen: {open:.2f} | High: {high:.2f} | Low: {low:.2f}')

        bx2.clear()
        bx2.bar(data['Volume'].index, data['Volume'], color='teal')
        bx2.set_ylabel('Volume')

        buffer = io.BytesIO()
        img.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        return image_png

def get_stock_data(empresa):
    try:
        if empresa != "":
            stock = yf.Ticker(empresa)
            pd.options.display.float_format = '{:,.2f}'.format
            data = pd.DataFrame(stock.history(period=PERIOD, interval=INTERVAL))
            data.index = data.index.strftime('%d/%m') # format date

            latest_price = data['Close'].iloc[-1]
            open = data['Open'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            marketChange = latest_price - stock.info['previousClose']
            marketChangePct = ((latest_price / stock.info['previousClose']) - 1) * 100
            #print(stock.info)
            return f"{stock.info['longName']} ({empresa}) : {latest_price:.4f} | {marketChange:.4f} | ({marketChangePct:.4f}%)\nPrevClose: {stock.info['previousClose']:.2f} | Open: {open:.2f} | High: {high:.2f} | Low: {low:.2f}"
    except Exception as e:
        return "Could not retrive ticker data."

def get_price(empresa):
    if empresa != "":
        stock = yf.Ticker(empresa)
        pd.options.display.float_format = '{:,.2f}'.format
        data = pd.DataFrame(stock.history(period=PERIOD, interval=INTERVAL))
        data.index = data.index.strftime('%d/%m') # format date

        latest_price = data['Close'].iloc[-1]

        return f"{empresa} : {latest_price:.4f}"

def bot_polling():
    telebot.polling(timeout=5)

def on_closing():
    if not is_alive:
        telebot.stop_bot()
        bot_thread.join()
        sys.exit()

@telebot.message_handler(commands=['chatid'])
def r_chatid(message):
    telebot.send_message(message.chat.id, "chatid: {}".format(message.chat.id))

@telebot.message_handler(commands=['help'])
def r_help(message):
    telebot.send_chat_action(message.chat.id, action='typing')
    telebot.send_message(message.chat.id, "Comandos:\n/stock EMPRESA\n/graph EMPRESA")

@telebot.message_handler(commands=['stock'])
def r_stock(message):
    empresa = util.extract_arguments(message.text)
    if len(empresa) <= 0:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        for st in STOCKS:
            markup.add(types.KeyboardButton("/stock " + st))
        telebot.send_message(message.chat.id, "Escolha uma", reply_markup=markup)

    else:
        telebot.send_chat_action(message.chat.id, action='typing')
        telebot.send_message(message.chat.id, get_stock_data(empresa.upper()))

@telebot.message_handler(commands=['top'])
def r_top(message):
    telebot.send_message(message.chat.id, get_price(util.extract_arguments(message.text).upper()))

@telebot.message_handler(commands=['graph'])
def r_graph(message):
    empresa = util.extract_arguments(message.text)
    if empresa != "":
        telebot.send_chat_action(message.chat.id, action='typing')
        telebot.send_photo(message.chat.id, photo=gen_graph(empresa.upper()))
    else:
        telebot.send_message(message.chat.id, "Use: /graph <EMPRESA>")

# Create the initial graph canvas
plt.style.use('seaborn-v0_8-dark-palette')
plt.tight_layout()

bot_thread = threading.Thread(target=bot_polling)
bot_thread.start()

monitor_thread = threading.Thread(target=monitor_stocks)
monitor_thread.start()