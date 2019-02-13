#!/usr/bin/env python3

from lib import rpclib, tuilib
import os
import time


header = "\
______                       _____  _____ \n\
| ___ \                     /  __ \/  __ \\\n\
| |_/ /___   __ _ _   _  ___| /  \/| /  \/\n\
|    // _ \ / _` | | | |/ _ \ |    | |\n\
| |\ \ (_) | (_| | |_| |  __/ \__/\| \__/\\\n\
\_| \_\___/ \__, |\__,_|\___|\____/ \____/\n\
             __/ |\n\
            |___/\n"


menuItems = [
    {"Check current connection": tuilib.getinfo_tui},
    {"Check mempool": tuilib.print_mempool},
    {"Check my players list": tuilib.print_players_list},
    {"Start singleplayer training game (creating, registering and starting game)": tuilib.rogue_newgame_singleplayer},
    # {"Create multiplayer game": tuilib.rogue_newgame_multiplayer},
    # {"Join (register) multiplayer game": tuilib.rogue_join_multiplayer_game},
    # {"Start multiplayer game": "test"},
    # {"Manually exit the game (bailout)": "test"},
    # {"Manually claim ROGUE coins for game (highlander)": "test"},
    {"Exit": exit}
]

def main():
    while True:
        os.system('clear')
        print(tuilib.colorize(header, 'pink'))
        print(tuilib.colorize('TUI v0.0.1\n', 'green'))
        for item in menuItems:
            print(tuilib.colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + list(item.keys())[0])
        choice = input(">> ")
        try:
            if int(choice) < 0:
                raise ValueError
            # Call the matching function
            if list(menuItems[int(choice)].keys())[0] == "Exit":
                list(menuItems[int(choice)].values())[0]()
            else:
                list(menuItems[int(choice)].values())[0](rpc_connection)
        except (ValueError, IndexError):
            pass


if __name__ == "__main__":
    while True:
        chain = "ROGUE"
        try:
            print(tuilib.colorize("Welcome to the RogueCC TUI!\n"
                                  "Please provide asset chain RPC connection details for initialization", "blue"))
            rpc_connection = tuilib.def_credentials(chain)
            rpclib.getinfo(rpc_connection)
        except Exception:
            print(tuilib.colorize("Cant connect to ROGUE daemon RPC! Please check if daemon is up.", "pink"))
            exit()
        else:
            print(tuilib.colorize("Succesfully connected!\n", "green"))
            with (open("lib/logo.txt", "r")) as logo:
                for line in logo:
                    print(line, end='')
                    time.sleep(0.04)
                print("\n")
            break
    main()
