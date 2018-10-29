#!/usr/bin/env python3

import tuilib
import rpclib
import os
import readline
import time


header = "\
 _____       _                               _____  _____ \n\
|  __ \     | |                             /  __ \/  __ \\\n\
| |  \/ __ _| |_ _____      ____ _ _   _ ___| /  \/| /  \/\n\
| | __ / _` | __/ _ \ \ /\ / / _` | | | / __| |    | |    \n\
| |_\ \ (_| | ||  __/\ V  V / (_| | |_| \__ \ \__/\| \__/\\\n\
 \____/\__,_|\__\___| \_/\_/ \__,_|\__, |___/\____/ \____/\n\
                                    __/ |                 \n\
                                   |___/                  \n"


menuItems = [
    {"Check current connection": tuilib.getinfo_tui},
    {"Create token": tuilib.token_create_tui},
    {"Create oracle": tuilib.oracle_create_tui},
    {"Register as publisher for oracle": tuilib.oracle_register_tui},
    {"Subscribe on oracle (+UTXO generator)": tuilib.oracle_subscription_utxogen},
    {"Token converter": tuilib.token_converter_tui},
    {"Bind Gateway": tuilib.gateways_bind_tui},
    {"Exit": exit}
]


def main():
    while True:
        os.system('clear')
        print(tuilib.colorize(header, 'pink'))
        print(tuilib.colorize('CLI version 0.2 by Anton Lysakov\n', 'green'))
        for item in menuItems:
            print(tuilib.colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + list(item.keys())[0])
        choice = input(">> ")
        try:
            if int(choice) < 0:
                raise ValueError
            # Call the matching function
            list(menuItems[int(choice)].values())[0](rpc_connection)
        except (ValueError, IndexError):
            pass
        # getting this error sometimes randomly from rpc lib, i guess there is some timeout
        # trying to catch it
        except (ConnectionResetError, BrokenPipeError):
            print("Disconnected!")
            break


if __name__ == "__main__":
    while True:
        try:
            print(tuilib.colorize("Welcome to the GatewaysCC TUI!\nPlease provide RPC connection details for initialization", "blue"))
            rpc_connection = tuilib.rpc_connection_tui()
            rpclib.getinfo(rpc_connection)
        except Exception:
            print(tuilib.colorize("Cant connect to RPC! Please re-check credentials.", "pink"))
        else:
            print(tuilib.colorize("Succesfully connected!\n", "green"))
            with (open("logo.txt", "r")) as logo:
                for line in logo:
                    print(line, end='')
                    time.sleep(0.04)
                print("\n")
            break
    main()
