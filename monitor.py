import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import threading
import sys, io
from telebot import TeleBot, util, types
import json
import time

TITLE = "Stocks"
STOCKS = ("BBAS3.SA", "BTC-USD", "BTC-BRL", "R2BL34.SA", "KLBN3.SA", "PETR4.SA", "LREN3.SA", "CYRE3.SA", "CPLE6.SA", "MDIA3.SA", "SANB11.SA", "SBFG3.SA", "BRFS3.SA", "VALE")
PERIOD = '3mo'
INTERVAL = '1wk'
UPDATE = 60
API_KEY = "6039135538:AAFZV6z2z-ns9I0tBG7O10M8WgKeenGa_qA"
CHATID = "-954957403"
telebot = TeleBot(API_KEY, threaded=True)
telebot.set_my_commands(['help', 'stock', 'graph', 'monitor'])
plt.style.use('seaborn-v0_8-dark-palette')

# Hotkey to close program
event = threading.Event()

def writeData():
    with open("data_file.json", "w") as write_file:
        json.dump(stockdb, write_file)

def loadData():
    with open("data_file.json", "r") as read_file:
        return json.load(read_file)
stockdb = loadData()

def gen_graph(empresa):
    if empresa != "":
        stock = yf.Ticker(empresa)
        pd.options.display.float_format = '{:,.2f}'.format        
        datac = pd.DataFrame(stock.history(period=PERIOD, interval=INTERVAL))

        latest_price = datac['Close'].iloc[-1]
        marketChange = latest_price - stock.info['previousClose']
        marketChangePct = ((latest_price / stock.info['previousClose']) - 1) * 100
        sign = '+' if marketChange > 0 else '-'

        # Figure for Telegrambot
        width_config = {'candle_linewidth':0.8, 'candle_width':0.525, 'volume_width': 0.525}
        scale_config = {'left': 0.1, 'top': 1, 'right': 1, 'bottom': 1}

        img, bx1 = mpf.plot(datac, type='candle', style='yahoo', mav=4, volume=True, datetime_format='%d - %m - %Y',
                            scale_padding = scale_config, update_width_config = width_config, 
                            returnfig=True, figsize=(12, 8),
                            title=f'\n{stock.info["longName"]}({empresa}) | {PERIOD}\nPrice: {latest_price:.4f} | {sign}{marketChange:.2f} | {marketChangePct:.4f}%')
        
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

@telebot.message_handler(commands=['monitor'])
def r_monitor(message):
    msg = ''
    for stock in stockdb:
        msg += f"{stock} targets L:{stockdb[stock]['LOW']:.4f} | H:{stockdb[stock]['HIGH']:.4f}\n"
    telebot.send_message(message.chat.id, msg)

@telebot.message_handler(commands=['graph'])
def r_graph(message):
    empresa = util.extract_arguments(message.text)
    if len(empresa) <= 0:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        for st in STOCKS:
            markup.add(types.KeyboardButton("/graph " + st))
        telebot.send_message(message.chat.id, "Escolha uma", reply_markup=markup)

    else:
        telebot.send_chat_action(message.chat.id, action='typing')
        telebot.send_photo(message.chat.id, photo=gen_graph(empresa.upper()))

if __name__ == '__main__':
        
    def bot_polling():
        #telebot.polling(non_stop=True, skip_pending=True, timeout=5)
        telebot.infinity_polling()

    def telebotSend(text):
        telebot.send_message(CHATID, text)

    def monitor_stocks():
        while not event.is_set():
            try:
                stockdb = loadData()
                for stock in stockdb:
                    stockyf = yf.Ticker(stock)
                    pd.options.display.float_format = '{:,.2f}'.format
                    data = pd.DataFrame(stockyf.history(period=PERIOD, interval=INTERVAL))
                    data.index = data.index.strftime('%d/%m') # format date
                    
                    latest_price = data['Close'].iloc[-1]
                    stocklow = stockdb[stock]['LOW']
                    stockhigh = stockdb[stock]['HIGH']

                    if latest_price <= stocklow:
                        telebotSend(f":stop_sign:ALERT: {stockyf.info['longName']}({stock}) atingiu loss em {latest_price:.4f} com target L:{stocklow}")
                        print (f"{stock} atingiu loss em {latest_price:.4f} com target {stocklow}")
                    elif latest_price >= stockhigh:
                        telebotSend(f"ALERT: {stockyf.info['longName']}({stock}) atingiu gain em {latest_price:.4f} com target H:{stockhigh}")
                        print (f"{stock} atingiu gain em {latest_price:.4f} com target {stockhigh}")
                    else:
                        print (f"{stock} em monitoramento {latest_price:.4f}")

            except Exception as e:
                print(e)
                break

            startTime = time.time()
            while True:
                elapsedTime = time.time() - startTime
                print('-', end='')
                time.sleep(0.5)
                if elapsedTime >= UPDATE:
                    print('')
                    break

    bot_thread = threading.Thread(target=bot_polling)
    monitor_thread = threading.Thread(target=monitor_stocks)

    while not event.is_set():
        if not bot_thread.is_alive():
            print("Telegram BOT polling started.")
            bot_thread.start()

        if not monitor_thread.is_alive():
            print("Stocks Monitor started.")
            monitor_thread.start()

        time.sleep(1)
        
    if event.is_set():
        #End processes
        telebot.stop_bot()
        bot_thread.join()
        sys.exit()