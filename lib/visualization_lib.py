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
            bets_rows_single.append(pricesinfo["profits"])
            bets_rows_single.append(pricesinfo["costbasis"])
            bets_rows_single.append(pricesinfo["positionsize"])
            bets_rows_single.append(pricesinfo["equity"])
            bets_rows_single.append(pricesinfo["addedbets"])
            bets_rows_single.append(pricesinfo["leverage"])
            bets_rows_single.append(pricesinfo["firstheight"])
            bets_rows_single.append(pricesinfo["firstprice"])
            bets_rows_single.append(pricesinfo["lastprice"])
            bets_rows_single.append(pricesinfo["height"])
            bets_rows.append(bets_rows_single)

    with open('betslist.csv', 'w') as f:
        filewriter = csv.writer(f, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(["txid", "is rekt", "profits", "costbasis", "positionsize", "equity", "addedbets", "leverage", "firstheight", "firstprice", "lastprice", "height"])
        for row in bets_rows:
            filewriter.writerow(row)
        f.close