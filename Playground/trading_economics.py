    
import requests
api_key = '7f488aaa8a25435:hya2ksi0nuh9nif'
url = f'https://api.tradingeconomics.com/markets/commodities?c={api_key}'
data = requests.get(url).json()
print(data)