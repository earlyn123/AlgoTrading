from pytrends.request import TrendReq
import matplotlib.pyplot as plt

pytrends = TrendReq(hl='en-US', tz=360)
keywords = ["Netflix", "Disney+"]
pytrends.build_payload(keywords, cat=0, timeframe='now 1-H', geo='', gprop='')
data = pytrends.interest_over_time()
print(data)

plt.figure(figsize=(10, 5))
for keyword in keywords:
    plt.plot(data.index, data[keyword], label=keyword)

plt.title('Search Interest Over Time')
plt.xlabel('Time')
plt.ylabel('Search Interest')
plt.legend()
plt.grid(True)
plt.show()