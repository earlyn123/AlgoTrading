import pandas as pd

# Path to the input CSV file
input_csv = r'C:\Users\early\AlgoTrading\BacktestLayer\data\nasdaq_stocks.csv'
# Path to the output CSV file
output_csv = 'C:/Users/early/AlgoTrading/BacktestLayer/data/nasdaq_stocks_last_year.csv'

# Desired date range
start_date = '2023-06-01'
end_date = '2024-06-01'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(input_csv, parse_dates=['ts_event'])

# Filter the DataFrame for rows within the desired date range
filtered_df = df[(df['ts_event'] >= start_date) & (df['ts_event'] < end_date)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv(output_csv, index=False)

print(f"Filtered data saved to {output_csv}")
