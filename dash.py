from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import ttk, IntVar
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import sys, io, time
from telebot import TeleBot, util, types

TITLE = "Stocks"
STOCKS = ("BBAS3.SA", "R2BL34.SA", "KLBN3.SA", "PETR4.SA", "LREN3.SA", "CYRE3.SA", "CPLE6.SA", "MDIA3.SA", "SANB11.SA", "SBFG3.SA", "BRFS3.SA")
PERIOD = '1mo'
INTERVAL = '1d'
UPDATE = 5 * 1000

API_KEY = "6039135538:AAFZV6z2z-ns9I0tBG7O10M8WgKeenGa_qA"
telebot = TeleBot(API_KEY, threaded=True)

def fetch_stock_data():
    global is_alive
    is_alive = True
    try:
        if checkloop.get():
            index = stocklist.current() + 1
            if index >= len(STOCKS): index = 0
            stocklist.current(index)

        stockselected = stocklist.get()
        if stockselected in STOCKS:
            status.config(text="reading...")
            stock = yf.Ticker(stockselected)
            pd.options.display.float_format = '{:,.2f}'.format
            data = pd.DataFrame(stock.history(period=PERIOD, interval=INTERVAL))
            data.index = data.index.strftime('%d/%m') # format date

            latest_price = data['Close'].iloc[-1]
            open = data['Open'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            marketChange = latest_price - stock.info['previousClose']
            marketChangePct = ((latest_price / stock.info['previousClose']) - 1) * 100

            # Update the label with the latest stock price
            stock1.config(text=f"PrevClose: {stock.info['previousClose']:.2f} | Open: {open:.2f} | High: {high:.2f} | Low: {low:.2f}\n")
            stocksel.config(text=f"{stockselected}", font="Sans 16 bold", padx=8, justify='left')
            price.config(text=f"{latest_price:.4f}", font="Sans 20 bold")
            market.config(text=f"{marketChange:.4f}", font="Arial", fg=('green' if marketChange > 0 else 'red'))
            indice.config(text=f"({marketChangePct:.4f}%)", font="Arial", fg=('green' if marketChangePct > 0 else 'red'))

            # Create the graph
            ax1.clear()
            ax1.plot(data['Close'], color=('green' if marketChange > 0 else 'red'))
            ax1.set_ylabel('Price')
            ax1.set_title(f'{stockselected} : {PERIOD}')

            ax2.clear()
            ax2.bar(data['Volume'].index, data['Volume'], color='teal')
            ax2.set_ylabel('Volume')

            # Clear the previous graph and display the new graph
            canvas.draw()
            status.config(text="Done")
            lastUpdate.config(text="Last update: {}".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")), fg='black')
        is_alive = False
    except Exception as e:
        is_alive = False
        lastUpdate.config(text="Error fetching stock data", fg='red')

def download_stocks():
    dw = yf.download(STOCKS, period='5d', auto_adjust=True, group_by='ticker')
    pd.options.display.float_format = '{:,.2f}'.format
    dw = pd.DataFrame(dw)
    dw.index = dw.index.strftime('%d/%m') # format date
    mktChg = []
    mktChgPct = []

    for t, df in dw.groupby(level=0):

        for s in STOCKS:
            latest_price = df[s]['Close']
            open = df[s]['Open']
            high = df[s]['High']
            low = df[s]['Low']
            
            marketChange = latest_price - df[s]['Close'].iloc[-1]
            marketChangePct = ((latest_price / df[s]['Close'].iloc[-1]) - 1) * 100

            mktChg.append(marketChange)
            mktChgPct.append(marketChangePct)
            
            print(f"{s} {marketChange} ({marketChangePct}%) Close: {latest_price} | Open: {open} | High: {high} | Low: {low}")
            dw[s, 'MktChg'] = marketChange
        
        
    #dw[s, 'MktChg'] = mktChg
    #dw.sort_index(axis=1)
    #print(dw)

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

        return f"{empresa} : {latest_price:.4f} | {marketChange:.4f} | ({marketChangePct:.4f}%)\nPrevClose: {stock.info['previousClose']:.2f} | Open: {open:.2f} | High: {high:.2f} | Low: {low:.2f}"

def bot_polling():
    telebot.polling(timeout=5)

def refresh():
    root.update()
    threading.Thread(target=fetch_stock_data).start()
    root.after(UPDATE, refresh)

def on_closing():
    if not is_alive:
        telebot.stop_bot()
        bot_thread.join()
        sys.exit()
    else:
        lastUpdate.config(text="Waiting for updates to complete", fg='black')

@telebot.message_handler(commands=['chatid'])
def r_chatid(message):
    telebot.send_message(message.chat.id, "chatid: {}".format(message.chat.id))

@telebot.message_handler(commands=['help'])
def r_help(message):
    telebot.send_message(message.chat.id, "Comandos:\n/stock <EMPRESA>\n/graph <EMPRESA>")

@telebot.message_handler(commands=['stock'])
def r_stock(message):
    empresa = util.extract_arguments(message.text)
    if  empresa in STOCKS:
        telebot.send_chat_action(message.chat.id, action='typing')
        telebot.send_message(message.chat.id, get_stock_data(empresa.upper()))

    elif empresa not in STOCKS:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        for st in STOCKS:
            markup.add(types.KeyboardButton("/stock " + st))
        telebot.send_message(message.chat.id, "Escolha um:", reply_markup=markup)

    else:
        telebot.send_message(message.chat.id, "Use: /stock <EMPRESA>")

@telebot.message_handler(commands=['top'])
def r_top(message):
    dw = download_stocks()
    telebot.send_message(message.chat.id, "dw")

@telebot.message_handler(commands=['graph'])
def r_graph(message):
    empresa = util.extract_arguments(message.text)
    if empresa != "":
        telebot.send_chat_action(message.chat.id, action='typing')
        telebot.send_photo(message.chat.id, photo=gen_graph(empresa.upper()))
    else:
        telebot.send_message(message.chat.id, "Use: /graph <EMPRESA>")

# Create the main window
root = tk.Tk()
root.geometry("640x480")
root.title(TITLE)
root.protocol("WM_DELETE_WINDOW", on_closing)

fr = tk.Frame(root)
fr.grid(column=0, row=1)

# Create labels to display the values
stock1 = tk.Label(root)
stock1.grid(column=0, row=0)

stocksel = tk.Label(fr)
stocksel.grid(column=0, row=1)
price = tk.Label(fr)
price.grid(column=1, row=1)
market = tk.Label(fr)
market.grid(column=2, row=1)
indice = tk.Label(fr)
indice.grid(column=3, row=1)

stocklist = ttk.Combobox(root, values=STOCKS, state="readonly", width=10)
stocklist.current(0)
stocklist.grid(column=2, row=0)
status = tk.Label(root)
status.grid(column=3, row=0)
checkloop = IntVar()
loop = tk.Checkbutton(root, text="Loop", variable=checkloop)
loop.select()
loop.grid(column=2, row=1)

# Create the initial graph canvas
plt.style.use('seaborn-v0_8-dark-palette')
plt.tight_layout()
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(6, 5), dpi=75)
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().grid(column=0, row=2)

bt = tk.Frame(root)
bt.grid(column=0, row=4)
lastUpdate = tk.Label(bt, border=2)
lastUpdate.grid(column=0, row=1)

#download_stocks()
#sys.exit()

bot_thread = threading.Thread(target=bot_polling)
bot_thread.start()

# Start the main event loop
refresh()
root.mainloop()