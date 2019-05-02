import csv
from datetime import datetime
import sys
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
            expression = pricesinfo["expression"].split(",")
            adopted_expression = ""
            for element in expression:
                adopted_expression = adopted_expression + element
            bets_rows_single.append(adopted_expression)
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
        filewriter.writerow(["txid", "is rekt", "expression", "leverage", "TotalPositionSize", "TotalProfits", "equity", "LastPrice", "LastHeight"])
        for row in bets_rows:
            filewriter.writerow(row)
        f.close


# function checking if prices for pair or inversed pair availiable on chain
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


# function returning list with prices for pair name if it presist in list
# with inverted price if it inverted price, and with error if no such pair in prices call output
def return_prices_for_pair(rpc_connection, pair, depth):
    prices_json = rpc_connection.prices(depth)
    timestamps = prices_json["timestamps"]
    # checking if it possible to get price for pair
    pair_availability = is_pair_availiable(rpc_connection, pair)
    # no such pair in prices output
    if not pair_availability[0] and not pair_availability[1]:
        print("Can't get price for this pair. Aborting.")
    # pair available in prices output
    if pair_availability[0] and not pair_availability[1]:
        for feed in prices_json["pricefeeds"]:
            if feed["name"] == pair:
                prices = []
                for price in feed["prices"]:
                    for price_value in price:
                        prices.append(price_value)
                return prices, timestamps
    # pair reversed version of some prices output pair
    if pair_availability[0] and pair_availability[1]:
        splitted_operator = pair.split("_")
        reversed_operator = splitted_operator[1] + "_" + splitted_operator[0]
        for pair in prices_json["pricefeeds"]:
            if pair["name"] == reversed_operator:
                prices = []
                for price in pair["prices"]:
                    for price_value in price:
                        prices.append(1/price_value)
                return prices, timestamps


# function returning list with stacks lists
def split_synthetic_on_stacks(rpc_connection, synthetic, depth):
    stacks_list = []
    stack_end = 0
    for i in range(0, len(synthetic)):
        if synthetic[i] == '*' or synthetic[i] == '/':
            temp = synthetic[stack_end:(i + 1)]
            stacks_list.append(temp)
            stack_end = i + 1
    return stacks_list


def count_stack(rpc_connection, stack, depth):
    # 2 pairs in stack case
    if len(stack) == 4:
        prices1 = return_prices_for_pair(rpc_connection, stack[0], depth)
        prices2 = return_prices_for_pair(rpc_connection, stack[1], depth)
        # if operator is / dividing stuff, if operator is * multiplying stuff
        if stack[2] == "/":
            stack_prices = [(float(prices1[0][i])) / (float(prices2[0][i])) for i in range(len(prices1[0]))]
        elif stack[2] == "*":
            stack_prices = [float(prices1[0][i]) * float(prices2[0][i]) for i in range(len(prices1[0]))]
    # 3 pairs in stack case
    elif len(stack) == 5:
        prices1 = return_prices_for_pair(rpc_connection, stack[0], depth)
        prices2 = return_prices_for_pair(rpc_connection, stack[1], depth)
        prices3 = return_prices_for_pair(rpc_connection, stack[2], depth)
        if stack[3] == "/":
            stack_prices = [(float(prices1[0][i])) / (float(prices2[0][i])) / (float(prices3[0][i])) for i in range(len(prices1[0]))]
        elif stack[3] == "*":
            stack_prices = [float(prices1[0][i]) * float(prices2[0][i]) * float(prices3[0][i]) for i in range(len(prices1[0]))]
    else:
        return "Incorrect stack!"
    print(stack)
    return stack_prices


def make_csv_for_stack(rpc_connection, stack, stack_name, depth):
    stack_prices = count_stack(rpc_connection, stack, depth)
    timestamps = rpc_connection.prices(depth)["timestamps"]
    dates = []
    for timestamp in timestamps:
        dates.append(datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M'))
    prices_rows = []
    pair_prices_row = []
    j = 0
    pair_name = ""
    for element in stack:
        pair_name = pair_name + element
    for i in range(0, len(stack_prices), 3):
        pair_prices_row.append(dates[j])
        j = j + 1
        pair_prices_row.append(stack_prices[i])
        pair_prices_row.append(stack_prices[i+1])
        pair_prices_row.append(stack_prices[i+2])
        pair_prices_row.append(pair_name)
        prices_rows.append(pair_prices_row)
        pair_prices_row = []

    with open(sys.path[0] + '/usergraphs/' + pair_name + '_user', 'w') as f:
        filewriter = csv.writer(f, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(["date", "price1", "price2", "price3", "pair"])
        for row in prices_rows:
            filewriter.writerow(row)
        f.close()


def draw_a_graph():
    pass
