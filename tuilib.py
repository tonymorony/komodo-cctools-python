import rpclib
import http


def colorize(string, color):

    colors = {
        'blue': '\033[94m',
        'pink': '\033[95m',
        'green': '\033[92m',
    }
    if color not in colors:
        return string
    else:
        return colors[color] + string + '\033[0m'


def rpc_connection_tui():

    rpc_user = input("Input your rpc user: ")
    rpc_password = input("Input your rpc password: ")
    rpc_port = input("Input your rpc port: ")

    rpc_connection = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))

    return rpc_connection


def getinfo_tui(rpc_connection):

    info_raw = rpclib.getinfo(rpc_connection)
    if isinstance(info_raw, dict):
        for key in info_raw:
            print("{}: {}".format(key, info_raw[key]))
        input("Press [Enter] to continue...")
    else:
        print("Error!\n")
        print(info_raw)
        input("Press [Enter] to continue...")


def token_create_tui(rpc_connection):

    while True:
        try:
            name = input("Set your token name: ")
            supply = input("Set your token supply: ")
            description = input("Set your token description: ")
        except KeyboardInterrupt:
            break
        else:
            try:
                token_hex = rpclib.token_create(rpc_connection, name,
                                                supply, description)
            except (http.client.RemoteDisconnected,
                    http.client.CannotSendRequest, ConnectionRefusedError):
                print("Connection error!")
                input("Press [Enter] to continue...")
                break
        if token_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "pink"))
            print(token_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                token_txid = rpclib.sendrawtransaction(rpc_connection,
                                                       token_hex['hex'])
            except KeyError:
                print(token_txid)
                print("Error")
                input("Press [Enter] to continue...")
                break
            finally:
                print(colorize("Token creation transaction broadcasted: " + token_txid, "green"))
                file = open("tokens_list", "a")
                file.writelines(token_txid + "\n")
                file.close()
                print(colorize("Entry added to tokens_list file!\n", "green"))
                input("Press [Enter] to continue...")
                break


def oracle_create_tui(rpc_connection):

    print(colorize("\nAvailiable data types:\n", "blue"))
    oracles_data_types = ["Ihh -> height, blockhash, merkleroot\ns -> <256 char string\nS -> <65536 char string\nd -> <256 binary data\nD -> <65536 binary data",
                "c -> 1 byte signed little endian number, C unsigned\nt -> 2 byte signed little endian number, T unsigned",
                "i -> 4 byte signed little endian number, I unsigned\nl -> 8 byte signed little endian number, L unsigned",
                "h -> 32 byte hash\n"]
    for oracles_type in oracles_data_types:
        print(str(oracles_type))
    while True:
        try:
            name = input("Set your oracle name: ")
            description = input("Set your oracle description: ")
            oracle_data_type = input("Set your oracle type (e.g. Ihh): ")
        except KeyboardInterrupt:
            break
        else:
            try:
                oracle_hex = rpclib.oracles_create(rpc_connection, name, description, oracle_data_type)
            except (http.client.RemoteDisconnected, http.client.CannotSendRequest, ConnectionRefusedError):
                print("Connection error!")
                input("Press [Enter] to continue...")
                break
        if oracle_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "pink"))
            print(oracle_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                oracle_txid = rpclib.sendrawtransaction(rpc_connection, oracle_hex['hex'])
            except KeyError:
                print(oracle_txid)
                print("Error")
                input("Press [Enter] to continue...")
                break
            finally:
                print(colorize("Oracle creation transaction broadcasted: " + oracle_txid, "green"))
                file = open("oracles_list", "a")
                file.writelines(oracle_txid + "\n")
                file.close()
                print(colorize("Entry added to oracles_list file!\n", "green"))
                input("Press [Enter] to continue...")
                break

def oracle_register_tui(rpc_connection):

    while True:
        try:
            oracle_id = input("Input txid of oracle you want to register to: ")
            data_fee = input("Set publisher datafee (in satoshis): ")
        except KeyboardInterrupt:
            break
        try:
            oracle_register_hex = rpclib.oracles_register(rpc_connection, oracle_id, data_fee)
        except (http.client.RemoteDisconnected, http.client.CannotSendRequest, ConnectionRefusedError):
            print("Connection error!")
            input("Press [Enter] to continue...")
            break
        if oracle_register_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "pink"))
            print(oracle_register_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                oracle_register_txid = rpclib.sendrawtransaction(rpc_connection, oracle_register_hex['hex'])
            except KeyError:
                print(oracle_register_hex)
                print("Error")
                input("Press [Enter] to continue...")
                break
            else:
                print(colorize("Oracle registration transaction broadcasted: " + oracle_register_txid, "green"))
                input("Press [Enter] to continue...")
                break

def oracle_register_utxogen(rpc_connection):

    while True:
        try:
            oracle_id = input("Input oracle ID you want to subscribe to: ")
            publisher_id = input("Input oracle publisher id you want to subscribe to: ")
            data_fee = input("Input subscribtion fee (in COINS!): ")
            utxo_num = int(input("Input how many transactions you want to broadcast: "))
        except KeyboardInterrupt:
            break
        try:
            while utxo_num > 0:
                oracle_subscription_hex = rpclib.oracles_subscribe(rpc_connection, oracle_id, publisher_id, data_fee)
                if oracle_subscription_hex['result'] == "error":
                    print(colorize("\nSomething went wrong!\n", "pink"))
                    print(oracle_subscription_hex)
                    print("\n")
                    input("Press [Enter] to continue...")
                    break
                else:
                    oracle_subscription_txid = rpclib.sendrawtransaction(rpc_connection, oracle_subscription_hex['hex'])
                    print(colorize("Oracle subscription transaction broadcasted: " + oracle_subscription_txid, "green"))
                    utxo_num = utxo_num - 1
            input("Press [Enter] to continue...")
            break
        except (http.client.RemoteDisconnected, http.client.CannotSendRequest, ConnectionRefusedError):
            print("Connection error!")
            input("Press [Enter] to continue...")
            break
