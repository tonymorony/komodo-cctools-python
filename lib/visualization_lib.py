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

# opened bets
def create_csv_with_bets(rpc_connection, open_or_closed):
    priceslist = rpc_connection.mypriceslist(open_or_closed)
    bets_rows = []
    for price in priceslist:
        if price == "48194bab8d377a7fa0e62d5e908474dae906675395753f09969d4c4bea4a7518":
            pass
        else:
            pricesinfo = rpc_connection.pricesinfo(price)
            bets_rows_single = []
            bets_rows_single.append(price)
            bets_rows_single.append(pricesinfo["rekt"])
            bets_rows_single.append(pricesinfo["leverage"])
            bets_rows_single.append(pricesinfo["TotalPositionSize"])
            bets_rows_single.append(pricesinfo["TotalProfits"])
            bets_rows_single.append(pricesinfo["equity"])
            bets_rows_single.append(pricesinfo["LastPrice"])
            bets_rows_single.append(pricesinfo["LastHeight"])
            bets_rows.append(bets_rows_single)
    if open_or_closed == 'open':
        filename = 'betlist.csv'
    if open_or_closed == 'closed':
        filename = 'betlist_history.csv'
    with open(filename, 'w') as f:
        filewriter = csv.writer(f, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(["txid", "is rekt", "leverage", "TotalPositionSize", "TotalProfits", "equity", "LastPrice", "LastHeight"])
        for row in bets_rows:
            filewriter.writerow(row)
        f.close


def is_pair_availiable(rpc_connection, pair):
    is_pair_in_list = False
    is_pair_reversed = False
    # getting known pairs list
    known_pair_names = []
    prices_output = rpc_connection.prices("1")
    # getting reversed version of pairname
    try:
        splitted_synthetic = pair.split("_")
        reversed_synthetic = splitted_synthetic[1] + "_" + splitted_synthetic[0]
    except Exception:
        return is_pair_in_list, is_pair_reversed
    for feed in prices_output["pricefeeds"]:
        known_pair_names.append(feed["name"])
    if pair in known_pair_names:
        is_pair_in_list = True
    elif reversed_synthetic in known_pair_names:
        is_pair_in_list = True
        is_pair_reversed = True
    return is_pair_in_list, is_pair_reversed


def custom_prices_generator(rpc_connection, synthetic):
    while True:
        pair_name = input("Input your pair name: ")
        print(is_pair_availiable(rpc_connection,pair_name))