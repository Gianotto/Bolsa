from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import ttk
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from threading import Thread
import time


TITLE = "Stocks"
STOCKS = ("BBAS3.SA", "KLBN3.SA", "PETR4.SA", "LREN3.SA")
PERIOD = "5d"
UPDATE = 5

def fetch_stock_data(name):
    #try:
        while is_alive:
            stocksel = stocklist.get()
            if stocksel != "":
                stock = yf.Ticker(stocksel)
                pd.options.display.float_format = '{:,.2f}'.format
                data = pd.DataFrame(stock.history(period=PERIOD))
                data.index = data.index.strftime('%d/%m') # format date
                print(stock.info)

                latest_price = data['Close'].iloc[-1]
                open = data['Open'].iloc[-1]
                high = data['High'].iloc[-1]
                low = data['Low'].iloc[-1]
                marketChange = latest_price - stock.info['previousClose']
                marketChangePct = ((latest_price / stock.info['previousClose']) - 1) * 100

                # Update the label with the latest stock price
                stock1.config(text=f"-={stocksel}=- PrevClose: {stock.info['previousClose']:.2f} | Open: {open:.2f} | High: {high:.2f} | Low: {low:.2f}\n")
                price.config(text=f"{latest_price:.4f}", font="Sans 20 bold")
                market.config(text=f"{marketChange:.4f}", font="Arial", fg=('green' if marketChange > 0 else 'red'))
                indice.config(text=f"({marketChangePct:.4f}%)", font="Arial", fg=('green' if marketChangePct > 0 else 'red'))

                # Create the graph
                ax.clear()
                ax.plot(data['Close'])
                ax.set_xlabel('Date')
                ax.set_ylabel('Price')
                ax.set_title(f'{stocksel} Stock Price {PERIOD}')

                # Clear the previous graph and display the new graph
                canvas.draw()
                
                lastUpdate.config(text="Last update: {}".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
            time.sleep(UPDATE)

    #except Exception as e:
        #lastUpdate.config(text="Error fetching stock data")

def clicked():
    print("Clicked")

# Thread
is_alive = True
mainthread = Thread(target=fetch_stock_data, args=(1,))

# Create the main window
root = tk.Tk()
root.title(TITLE)

fr = tk.Frame(root)
fr.grid(column=0, row=1)

# Create labels to display the values
stock1 = tk.Label(root)
stock1.grid(column=0, row=0)
price = tk.Label(fr)
price.grid(column=0, row=1)
market = tk.Label(fr)
market.grid(column=1, row=1)
indice = tk.Label(fr)
indice.grid(column=2, row=1)


stocklist = ttk.Combobox(root, values=STOCKS, state="readonly", width=10)
stocklist.current(0)
stocklist.grid(column=2, row=0)

refresh = tk.Button(root, text="Refresh", command=clicked)
refresh.grid(column=3, row=0)

# Create the initial graph canvas
figure = plt.Figure(figsize=(6, 4), dpi=75)
ax = figure.add_subplot(111)
canvas = FigureCanvasTkAgg(figure, root)
#canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False)
canvas.get_tk_widget().grid(column=0, row=2)

lastUpdate = tk.Label(root)
lastUpdate.grid(column=0, row=3)
#lastUpdate.pack()

# Start updating the values
mainthread.start()

# Start the main event loop
root.mainloop()

# Finish the thread
is_alive = False
mainthread.join()