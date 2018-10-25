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
                token_hex = rpclib.token_create(rpc_connection, name, supply, description)
            except http.client.RemoteDisconnected:
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
                token_txid = rpclib.sendrawtransaction(rpc_connection, token_hex['hex'])
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
