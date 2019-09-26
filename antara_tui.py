#!/usr/bin/env python3

from lib import rpclib, tuilib
import os
import time

oracles = {}
oracles['header'] = "\
                 _                       ____                 _               __  __           _       _       \n\
     /\         | |                     / __ \               | |             |  \/  |         | |     | |      \n\
    /  \   _ __ | |_ __ _ _ __ __ _    | |  | |_ __ __ _  ___| | ___  ___    | \  / | ___   __| |_   _| | ___  \n\
   / /\ \ | '_ \| __/ _` | '__/ _` |   | |  | | '__/ _` |/ __| |/ _ \/ __|   | |\/| |/ _ \ / _` | | | | |/ _ \ \n\
  / ____ \| | | | || (_| | | | (_| |   | |__| | | | (_| | (__| |  __/\__ \   | |  | | (_) | (_| | |_| | |  __/ \n\
 /_/    \_\_| |_|\__\__,_|_|  \__,_|    \____/|_|  \__,_|\___|_|\___||___/   |_|  |_|\___/ \__,_|\__,_|_|\___| \n"
                                                                                                              
oracles['menu'] = [
    # TODO: Have to implement here native oracle file uploader / reader, should be dope
    # TODO: data publisher / converter for different types
    {"Check current connection": tuilib.getinfo_tui},
    {"Check mempool": tuilib.print_mempool},
    {"View oracle info": tuilib.oracles_info},
    {"Create oracle": tuilib.oracle_create_tui},
    {"Register as publisher for oracle": tuilib.oracle_register_tui},
    {"Subscribe on oracle (+UTXO generator)": tuilib.oracle_subscription_utxogen},
    {"Upload file to oracle": tuilib.convert_file_oracle_D},
    {"Display list of files uploaded to this AC": tuilib.display_files_list},
    {"Download files from oracle": tuilib.files_downloader},
    {"Return to Antara modules menu": tuilib.exit_main},
    {"Exit TUI": tuilib.exit}
]
oracles['author'] = 'Welcome to the OraclesCC TUI!\n"CLI version 0.2 by Anton Lysakov & Thorn Mennet\n'

pegs_usage = {}
pegs_usage['header'] = "\
                 _                      _____                   __  __           _       _      \n\
     /\         | |                    |  __ \                 |  \/  |         | |     | |     \n\
    /  \   _ __ | |_ __ _ _ __ __ _    | |__) |__  __ _ ___    | \  / | ___   __| |_   _| | ___ \n\
   / /\ \ | '_ \| __/ _` | '__/ _` |   |  ___/ _ \/ _` / __|   | |\/| |/ _ \ / _` | | | | |/ _ \ \n\
  / ____ \| | | | || (_| | | | (_| |   | |  |  __/ (_| \__ \   | |  | | (_) | (_| | |_| | |  __/ \n\
 /_/    \_\_| |_|\__\__,_|_|  \__,_|   |_|   \___|\__, |___/   |_|  |_|\___/ \__,_|\__,_|_|\___| \n\
                                                   __/ |                                        \n\
                                                  |___/                                         \n"

pegs_usage['menu'] = [
    {"Pegs Module Readme": tuilib.readme_tui},
    {"Check connection to assetchain": tuilib.getinfo_tui},
    {"Check assetchain mempool": tuilib.print_mempool},
    {"Check connection to KMD": tuilib.getinfo_tui},
    {"Connect to KMD daemon": tuilib.rpc_kmd_connection_tui},
    {"View assetchain Gateway Info": tuilib.gateway_info_tui},
    {"Deposit KMD in Gateway and claim Tokens": tuilib.gateways_deposit_claim_tokens},
    {"Execute Pegs funding": tuilib.pegs_fund_tui},
    {"Execute Pegs get": tuilib.pegs_get_tui},
    {"Check Pegs info": tuilib.pegsinfo_tui},
    {"Check Pegs account history": tuilib.pegs_accounthistory_tui},
    {"Check Pegs account info": tuilib.pegs_accountinfo_tui},
    {"Check Pegs addresses": tuilib.pegs_addresses_tui},
    {"Check Pegs worst accounts": tuilib.pegs_worstaccounts_tui},
    {"Return to Antara modules menu": tuilib.exit_main},
    {"Exit TUI": tuilib.exit}
]
pegs_usage['author'] = 'Welcome to the Pegs Usage TUI!\n"CLI version 0.2 by Thorn Mennet\n'

pegs_create = {}
pegs_create['header'] = "\
                 _                      _____                   __  __           _       _      \n\
     /\         | |                    |  __ \                 |  \/  |         | |     | |     \n\
    /  \   _ __ | |_ __ _ _ __ __ _    | |__) |__  __ _ ___    | \  / | ___   __| |_   _| | ___ \n\
   / /\ \ | '_ \| __/ _` | '__/ _` |   |  ___/ _ \/ _` / __|   | |\/| |/ _ \ / _` | | | | |/ _ \ \n\
  / ____ \| | | | || (_| | | | (_| |   | |  |  __/ (_| \__ \   | |  | | (_) | (_| | |_| | |  __/ \n\
 /_/    \_\_| |_|\__\__,_|_|  \__,_|   |_|   \___|\__, |___/   |_|  |_|\___/ \__,_|\__,_|_|\___| \n\
                                                   __/ |                                        \n\
                                                  |___/                                         \n"

pegs_create['menu'] = [
    {"Pegs Module Readme": tuilib.readme_tui},
    {"Create a Pegs assetchain": tuilib.pegs_create_tui},
    {"Run oraclefeed": tuilib.oraclefeed_tui},
    {"Return to Antara modules menu": tuilib.exit_main},
    {"Exit TUI": tuilib.exit}
]
pegs_create['author'] = 'Welcome to the Pegs Creation TUI!\n"CLI version 0.2 by Thorn Mennet\n'



gw_create = {}
gw_create['header'] = "\
                 _                       _____       _                                   __  __           _       _      \n\
     /\         | |                     / ____|     | |                                 |  \/  |         | |     | |      \n \
    /  \   _ __ | |_ __ _ _ __ __ _    | |  __  __ _| |_ _____      ____ _ _   _ ___    | \  / | ___   __| |_   _| | ___  \n \
   / /\ \ | '_ \| __/ _` | '__/ _` |   | | |_ |/ _` | __/ _ \ \ /\ / / _` | | | / __|   | |\/| |/ _ \ / _` | | | | |/ _ \ \n \
  / ____ \| | | | || (_| | | | (_| |   | |__| | (_| | ||  __/\ V  V / (_| | |_| \__ \   | |  | | (_) | (_| | |_| | |  __/ \n \
 /_/    \_\_| |_|\__\__,_|_|  \__,_|    \_____|\__,_|\__\___| \_/\_/ \__,_|\__, |___/   |_|  |_|\___/ \__,_|\__,_|_|\___| \n \
                                                                            __/ |                                        \n \
                                                                           |___/                                         \n "


gw_create['menu'] = [
    {"Check current connection": tuilib.getinfo_tui},
    {"Check mempool": tuilib.print_mempool},
    {"Create token": tuilib.token_create_tui},
    {"Create oracle": tuilib.oracle_create_tui},
    {"Register as publisher for oracle": tuilib.oracle_register_tui},
    {"Subscribe on oracle (+UTXO generator)": tuilib.oracle_subscription_utxogen},
    {"Bind Gateway": tuilib.gateways_bind_tui},
    {"Return to Antara modules menu": tuilib.exit_main},
    {"Exit TUI": tuilib.exit}
]
gw_create['author'] = 'Welcome to the Gateways Creation TUI!\n"CLI version 0.2 by Anton Lysakov & Thorn Mennet\n'


gw_use = {}
gw_use['header'] = "\
                  _                       _____      _                                   __  __           _       _      \n\
     /\         | |                     / ____|     | |                                 |  \/  |         | |     | |      \n \
    /  \   _ __ | |_ __ _ _ __ __ _    | |  __  __ _| |_ _____      ____ _ _   _ ___    | \  / | ___   __| |_   _| | ___  \n \
   / /\ \ | '_ \| __/ _` | '__/ _` |   | | |_ |/ _` | __/ _ \ \ /\ / / _` | | | / __|   | |\/| |/ _ \ / _` | | | | |/ _ \ \n \
  / ____ \| | | | || (_| | | | (_| |   | |__| | (_| | ||  __/\ V  V / (_| | |_| \__ \   | |  | | (_) | (_| | |_| | |  __/ \n \
 /_/    \_\_| |_|\__\__,_|_|  \__,_|    \_____|\__,_|\__\___| \_/\_/ \__,_|\__, |___/   |_|  |_|\___/ \__,_|\__,_|_|\___| \n \
                                                                            __/ |                                        \n \
                                                                           |___/                                         \n "

gw_use['menu'] = [
    {"Check connection to assetchain": tuilib.getinfo_tui},
    {"Check assetchain mempool": tuilib.print_mempool},
    {"Check connection to KMD": tuilib.getinfo_tui},
    {"Connect to KMD daemon": tuilib.rpc_kmd_connection_tui},
    {"View assetchain Gateway Info": tuilib.gateway_info_tui},
    {"Send KMD gateway deposit transaction": tuilib.gateways_send_kmd},
    {"Execute gateways deposit": tuilib.gateways_deposit_tui},
    {"Execute gateways claim": tuilib.gateways_claim_tui},
    {"Execute gateways withdrawal": tuilib.gateways_withdrawal_tui},
    {"Return to Antara modules menu": tuilib.exit_main},
    {"Exit TUI": tuilib.exit}
]
gw_use['author'] = 'Welcome to the Gateways Creation TUI!\n"CLI version 0.2 by Anton Lysakov & Thorn Mennet\n'

payments = {}
payments['header'] = "\
                 _                      _____                                 _           __  __           _       _      \n\
     /\         | |                    |  __ \                               | |         |  \/  |         | |     | |     \n\
    /  \   _ __ | |_ __ _ _ __ __ _    | |__) |_ _ _   _ _ __ ___   ___ _ __ | |_ ___    | \  / | ___   __| |_   _| | ___  \n\
   / /\ \ | '_ \| __/ _` | '__/ _` |   |  ___/ _` | | | | '_ ` _ \ / _ \ '_ \| __/ __|   | |\/| |/ _ \ / _` | | | | |/ _ \ \n\
  / ____ \| | | | || (_| | | | (_| |   | |  | (_| | |_| | | | | | |  __/ | | | |_\__ \   | |  | | (_) | (_| | |_| | |  __/ \n\
 /_/    \_\_| |_|\__\__,_|_|  \__,_|   |_|   \__,_|\__, |_| |_| |_|\___|_| |_|\__|___/   |_|  |_|\___/ \__,_|\__,_|_|\___| \n\
                                                    __/ |                                                                 \n\
                                                   |___/                                                                  \n"

payments['menu'] = [
    {"Check current connection": tuilib.getinfo_tui},
    {"Check mempool": tuilib.print_mempool},
    {"View Payments contracts": tuilib.payments_info},
    {"Create Payments contract": tuilib.payments_create},
    {"Fund Payments contract": tuilib.payments_fund},
    {"Merge Payments contract funds": tuilib.payments_merge},
    {"Release Payments contract funds": tuilib.payments_release},
    {"Return to Antara modules menu": tuilib.exit_main},
    {"Exit TUI": tuilib.exit}
]
payments['author'] = '"Welcome to the Payments Module TUI!\n"CLI version 0.2 by Thorn Mennet\n'

antara = {}
antara['header'] = "\
                 _                       _____                      _       _           _           __  __           _       _           \n\
     /\         | |                     / ____|                    | |     | |         (_)         |  \/  |         | |     | |          \n\
    /  \   _ __ | |_ __ _ _ __ __ _    | (___  _ __ ___   __ _ _ __| |_ ___| |__   __ _ _ _ __     | \  / | ___   __| |_   _| | ___  ___ \n\
   / /\ \ | '_ \| __/ _` | '__/ _` |    \___ \| '_ ` _ \ / _` | '__| __/ __| '_ \ / _` | | '_ \    | |\/| |/ _ \ / _` | | | | |/ _ \/ __| \n\
  / ____ \| | | | || (_| | | | (_| |    ____) | | | | | | (_| | |  | || (__| | | | (_| | | | | |   | |  | | (_) | (_| | |_| | |  __/\__ \ \n\
 /_/    \_\_| |_|\__\__,_|_|  \__,_|   |_____/|_| |_| |_|\__,_|_|   \__\___|_| |_|\__,_|_|_| |_|   |_|  |_|\___/ \__,_|\__,_|_|\___||___/ \n"

antara['menu'] = [
    {"Oracles": oracles},
    {"Gateways Creation": gw_create},
    {"Gateways Usage": gw_use},
    {"Pegs Creation": pegs_create},
    {"Pegs Usage": pegs_usage},
    {"Payments": payments},
    {"Exit TUI": tuilib.exit}
]
antara['author'] = "Welcome to the Antara Modules TUI!\nCLI version 0.2 by Anton Lysakov & Thorn Mennet\n"



ac_rpc_options = []
main_menu_options = ["Oracles", "Gateways Creation", "Gateways Usage", "Pegs Creation", "Pegs Usage", "Payments"]
kmd_ac_rpc_options = ["Deposit KMD in Gateway and claim Tokens"]
kmd_rpc_options = ["Check connection to KMD", "Send KMD gateway deposit transaction", "Execute gateways deposit"]
kmd_connect_options = ["Connect to KMD daemon"]
no_param_options = ["Exit TUI"]
# TODO: add more readme docs
docs_options = ["Pegs Module Readme"]
readme_files = ['docs/pegs_module.md']
def submenu(menu):
    menuItems = menu['menu']
    while True:
        os.system('clear')
        print(tuilib.colorize(menu['header'], 'blue'))
        print(tuilib.colorize(menu['author'], 'green'))
        for item in menuItems:
            print(tuilib.colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + list(item.keys())[0])
        choice = input(">> ")
        try:
            if int(choice) < 0:
                raise ValueError
            if list(menuItems[int(choice)].keys())[0] == "Return to Antara modules menu":
                submenu(antara)
            elif list(menuItems[int(choice)].keys())[0] in main_menu_options:
                submenu(list(menuItems[int(choice)].values())[0])
            elif list(menuItems[int(choice)].keys())[0] in no_param_options:
                list(menuItems[int(choice)].values())[0]()
            elif list(menuItems[int(choice)].keys())[0] in docs_options:
                index = docs_options.index(list(menuItems[int(choice)].keys())[0])
                list(menuItems[int(choice)].values())[0](readme_files[index])
            elif list(menuItems[int(choice)].keys())[0] in kmd_connect_options:
                rpc_connection_kmd = list(menuItems[int(choice)].values())[0]()
            elif list(menuItems[int(choice)].keys())[0] in kmd_rpc_options:
                while True:
                    try:
                        list(menuItems[int(choice)].values())[0](rpc_connection_kmd)
                        break
                    except Exception as e:
                        print("Please connect to KMD daemon first!")
                        input("Press [Enter] to continue...")
                        break
            elif list(menuItems[int(choice)].keys())[0] in kmd_ac_rpc_options:
                while True:
                    try:
                        list(menuItems[int(choice)].values())[0](rpc_connection, rpc_connection_kmd)
                        break
                    except Exception as e:
                        print(e)
                        print("Please connect to KMD daemon first!")
                        input("Press [Enter] to continue...")
                        break
            else:
                list(menuItems[int(choice)].values())[0](rpc_connection)
        except (ValueError, IndexError):
            pass

def main():
    menuItems = antara['menu']
    while True:
        os.system('clear')
        print(tuilib.colorize(antara['header'], 'blue'))
        print(tuilib.colorize(antara['author'], 'green'))
        for item in menuItems:
            print(tuilib.colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + list(item.keys())[0])
        choice = input(">> ")
        try:
            if int(choice) < 0:
                raise ValueError
            # Call the matching function
            if list(menuItems[int(choice)].keys())[0] == "Exit TUI":
                list(menuItems[int(choice)].values())[0]()
            else:
                submenu(list(menuItems[int(choice)].values())[0])
        except (ValueError, IndexError):
            pass


if __name__ == "__main__":
    while True:
        try:
            info = rpclib.getinfo(rpc_connection)
            chain = info['name']
            if "pubkey" in info.keys():
                print("Pubkey is already set")
            else:
                valid_address = rpc_connection.getaccountaddress("")
                print(valid_address)
                valid_pubkey = rpc_connection.validateaddress(valid_address)["pubkey"]
                print(valid_pubkey)
                rpc_connection.setpubkey(valid_pubkey)
                print(tuilib.colorize("Pubkey is succesfully set!", "green"))
        except Exception as e:
            try:
                print(antara['author'])
                rpc_connection = tuilib.rpc_connection_tui()
            except Exception as e:
                print(e)
                print(tuilib.colorize("Cant connect to RPC! Please re-check credentials and make sure smartchain is running.", "red"))
                pass
            pass
        else:
            print(tuilib.colorize("Succesfully connected to "+chain+" smartchain!\n", "green"))
            time.sleep(1.6)
            with (open("lib/logo.txt", "r")) as logo:
                for line in logo:
                    parts = line.split(' ')
                    row = ''
                    for part in parts:
                        if part.find('.') == -1:
                            row += tuilib.colorize(part, 'blue')
                        else:
                            row += tuilib.colorize(part, 'black')
                    print(row, end='')
                    #print(line, end='')
                    time.sleep(0.04)
                time.sleep(0.4)
            print("\n")
            break
    main()
