#!/usr/bin/env python3

from lib import rpclib, tuilib
import os
import time

header = "\
______                 _____  _____ \n\
| ___ \               /  __ \/  __ \\\n\
| |_/ /___  _____  ___| /  \/| /  \/\n\
|  __// _ \|  _  |/ __| |    | |    \n\
| |  |  __/| |_| |\__ \ \__/\| \__/\\\n\
\_|   \___|\___  |/___/\____/ \____/\n\
             __/ |                 \n\
            |___/                 \n"

       
       

menuItems = [
    {"Pegs Module Readme": tuilib.readme_tui},
    {"Create a Pegs assetchain": tuilib.pegs_create_tui},
    {"Run oraclefeed": tuilib.oraclefeed_tui},
    {"Exit": exit}
]

def main():
    while True:
        os.system('clear')
        print(tuilib.colorize(header, 'pink'))
        print(tuilib.colorize('CLI version 0.1 by Thor Mennet\n', 'green'))
        for item in menuItems:
            print(tuilib.colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + list(item.keys())[0])
        choice = input(">> ")
        try:
            if int(choice) < 0:
                raise ValueError
            # Call the matching function
            if list(menuItems[int(choice)].keys())[0] == "Pegs Module Readme":
                list(menuItems[int(choice)].values())[0]('docs/pegs_module.md')
            else:
                list(menuItems[int(choice)].values())[0]()
        except (ValueError, IndexError):
            pass


if __name__ == "__main__":
    while True:
            with (open("lib/logo.txt", "r")) as logo:
                for line in logo:
                    print(line, end='')
                    time.sleep(0.04)
                print("\n")
            break
    main()
