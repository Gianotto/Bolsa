import time
import os
import yfinance as yf

def monitor_options_chain(ticker_symbol, expiration_date, interval=5):
    """
    Monitors the options chain for a specific ticker and expiration date.
    """
    print(f"Monitoring options for {ticker_symbol} expiring on {expiration_date}...")
    while True:
        try:
            # Clear the terminal screen for a cleaner output
            #os.system('cls' if os.name == 'nt' else 'clear')
            
            ticker = yf.Ticker(ticker_symbol)
            options_chain = ticker.option_chain(expiration_date)

            print(f"--- Real-time Options Watch ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")
            print(f"Ticker: {ticker_symbol} | Expiration: {expiration_date}")

            # Display key Call options data (e.g., top 5 by open interest)
            print("\nTop Call Options (by open interest):")
            calls = options_chain.calls.sort_values(by='openInterest', ascending=False)
            print(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].head().to_string())

            # Display key Put options data (e.g., top 5 by open interest)
            print("\nTop Put Options (by open interest):")
            puts = options_chain.puts.sort_values(by='openInterest', ascending=False)
            print(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].head().to_string())

            time.sleep(interval)

        except Exception as e:
            print(f"Error fetching data: {e}")
            print(f"Retrying in {interval} seconds...")
            time.sleep(interval)

if __name__ == "__main__":
    ticker_symbol = input("Enter a stock ticker (e.g., MSFT): ").upper()
    
    # You will need to look up an expiration date manually from the first script
    # and provide it here, e.g., '2025-11-21'
    expiration_date = '2025-11-21'
    
    monitor_options_chain(ticker_symbol, expiration_date)

