from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import ttk, IntVar
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time, sys


TITLE = "Stocks"
STOCKS = ("BBAS3.SA", "KLBN3.SA", "PETR4.SA", "LREN3.SA")
PERIOD = "5d"
UPDATE = 5

def fetch_stock_data():
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
            data = pd.DataFrame(stock.history(period=PERIOD))
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
            ax1.set_title(f'Stock Price {PERIOD}')

            ax2.clear()
            ax2.bar(data['Volume'].index, data['Volume'], color='teal')
            ax2.set_ylabel('Volume')

            # Clear the previous graph and display the new graph
            canvas.draw()
            status.config(text="Done")
            lastUpdate.config(text="Last update: {}".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")), fg='black')

    except Exception as e:
        lastUpdate.config(text="Error fetching stock data", fg='red')

def refresh():
    root.update()
    threading.Thread(target=fetch_stock_data).start()
    root.after(5000, refresh)

def on_closing():
    sys.exit()

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

# Start the main event loop
refresh()
root.mainloop()