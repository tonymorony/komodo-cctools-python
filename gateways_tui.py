#!/usr/bin/env python3

import tuilib
import os
import readline


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
    {"Subscribe on oracle (+UTXO generator)": tuilib.oracle_register_utxogen},
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


if __name__ == "__main__":
    while True:
        try:
            rpc_connection = tuilib.rpc_connection_tui()
        except ValueError:
            print("Not correct details!")
        try:
            print("\n\n\n")
            tuilib.getinfo_tui(rpc_connection)
            print("\n\n\n")
            break
        # TODO: have to handle as adequate people do
        except Exception:
            print(tuilib.colorize("Cant connect to RPC! Please re-check credentials.", "pink"))
    main()
