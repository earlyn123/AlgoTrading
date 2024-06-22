import databento as db

FILE_PATH = r".\historical_data\google_trade_data\xnas-itch-20221230.trades.dbn"

stored_data = db.from_dbn(FILE_PATH)

stored_data.to_csv("one_day_google.csv")