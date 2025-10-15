import requests
import pandas as pd
import numpy as np

def get_crypto_data(crypto_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        prices = [entry[1] for entry in data["prices"]]
        volumes = [entry[1] for entry in data["total_volumes"]]
        return prices, volumes
    else:
        print(f"Erro ao buscar dados da API para {crypto_id}.")
        return [], []

def calculate_moving_average(prices, window=7):
    return pd.Series(prices).rolling(window=window).mean().tolist()

def analyze_trend(prices):
    if len(prices) < 10:
        return "Dados insuficientes para análise."
    
    short_ma = calculate_moving_average(prices, window=7)
    long_ma = calculate_moving_average(prices, window=25)
    
    if short_ma[-1] > long_ma[-1]:
        return f"Tendência de alta. {prices[-1]:6,.4f}"
    elif short_ma[-1] < long_ma[-1]:
        return f"Tendência de baixa. {prices[-1]:6,.4f}"
    else:
        return f"Mercado lateral - Não há tendência clara. {prices[-1]:6,.4f}"

def analyze_volume_growth(volumes):
    if len(volumes) < 2:
        return "Dados insuficientes para análise de volume."
    if volumes[-1] > volumes[-2]:
        return f"Volume em crescimento {volumes[-1]:12,.4f}"
    else:
        return f"Volume em declínio {volumes[-2]:12,.4f}"

def main():
    crypto_ids = ["bitcoin", "official-trump"]  # Lista de criptomoedas para análise
    for crypto_id in crypto_ids:
        prices, volumes = get_crypto_data(crypto_id)
        if prices and volumes:
            trend = analyze_trend(prices)
            volume_trend = analyze_volume_growth(volumes)
            print(f"{crypto_id}: {trend}")
            print(f"{crypto_id}: {volume_trend}\n")

if __name__ == "__main__":
    main()
