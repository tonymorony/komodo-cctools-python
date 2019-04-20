import csv
from datetime import datetime

from lib import tuilib


def create_prices_csv(rpc_connection, depth):
    prices_json = rpc_connection.prices(depth)
    timestamps = prices_json["timestamps"]
    dates = []
    for timestamp in timestamps:
        dates.append(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M'))
    prices_rows = []
    for pair in prices_json["pricefeeds"]:
        i = 0
        for price in pair["prices"]:
            pair_prices_row = []
            pair_prices_row.append(dates[i])
            pair_prices_row.append(price[0])
            pair_prices_row.append(price[1])
            pair_prices_row.append(price[2])
            pair_prices_row.append(pair["name"])
            i = i + 1
            prices_rows.append(pair_prices_row)

    with open('prices.csv', 'w') as f:
        filewriter = csv.writer(f, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(["date", "price1", "price2", "price3", "pair"])
        for row in prices_rows:
            filewriter.writerow(row)
        f.close()


def create_delayed_prices_csv(rpc_connection, depth):
    prices_json = rpc_connection.prices(depth)
    timestamps = prices_json["timestamps"]
    dates = []
    for timestamp in timestamps:
        dates.append(datetime.utcfromtimestamp(timestamp - 86400).strftime('%Y-%m-%dT%H:%M'))
    prices_rows = []
    for pair in prices_json["pricefeeds"]:
        i = 0
        for price in pair["prices"]:
            pair_prices_row = []
            pair_prices_row.append(dates[i])
            pair_prices_row.append(price[0])
            pair_prices_row.append(price[1])
            pair_prices_row.append(price[2])
            pair_prices_row.append(pair["name"])
            i = i + 1
            prices_rows.append(pair_prices_row)

    with open('delayed_prices.csv', 'w') as f:
        filewriter = csv.writer(f, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(["date", "price1", "price2", "price3", "pair"])
        for row in prices_rows:
            filewriter.writerow(row)
        f.close()


def get_pairs_names(rpc_connection):
    prices_json = rpc_connection.prices("1")
    pairs_names = []
    for pair in prices_json["pricefeeds"]:
        pairs_names.append(pair["name"])
    return pairs_names