from lib import rpclib
import json
import time
import re
import sys
import pickle
import platform
import os
import subprocess
import signal
from slickrpc import Proxy
from binascii import hexlify
from binascii import unhexlify
from functools import partial
from shutil import copy

home = os.environ['HOME']
cwd = os.getcwd()

operating_system = platform.system()
if operating_system != 'Win64' and operating_system != 'Windows':
    import readline


def colorize(string, color):

    colors = {
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'green': '\033[92m',
        'red': '\033[91m',
        'black': '\033[30m',
        'grey': '\033[90m',
        'pink': '\033[95m'        
    }
    if color not in colors:
        return string
    else:
        return colors[color] + string + '\033[0m'


def rpc_connection_tui():
    # TODO: possible to save multiply entries from successfull sessions and ask user to choose then
    while True:
        restore_choice = input("[U]se cached connection details, [S]elect smartchain, or [E]nter manually? [U/S/E]: ")
        if restore_choice == "U" or restore_choice == "u":
            try:
                with open("connection.json", "r") as file:
                    connection_json = json.load(file)
                    chain = connection_json["chain"]
                    rpc_user = connection_json["rpc_user"]
                    rpc_password = connection_json["rpc_password"]
                    rpc_port = connection_json["rpc_port"]
                    rpc_connection = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
                try:
                    ac_name = rpc_connection.getinfo()['name']
                    break
                except:
                    print("Connection failed! Is "+chain+" running?")
                    pass
            except FileNotFoundError:
                print(colorize("You do not have cached connection details. Please select [E] for connection setup, or [S] to select a smartchain", "red"))
        elif restore_choice == "S" or restore_choice == "s":
            chain = select_ac()
            rpc_info = rpclib.get_rpc_details(chain)
            connection_details = {"chain": chain,
                                  "rpc_user": rpc_info[0],
                                  "rpc_password": rpc_info[1],
                                  "rpc_port": rpc_info[2]}
            connection_json = json.dumps(connection_details)
            with open("connection.json", "w+") as file:
                file.write(connection_json)
            rpc_connection = rpclib.rpc_connect(rpc_info[0], rpc_info[1], int(rpc_info[2]))
            try:
                ac_name = rpc_connection.getinfo()['name']
                break
            except:
                print("Connection failed! Is "+chain+" running?")
                pass
        elif restore_choice == "E" or restore_choice == "e":
            chain = input("Input smartchain name: ")
            rpc_user = input("Input your rpc user: ")
            rpc_password = input("Input your rpc password: ")
            rpc_port = input("Input your rpc port: ")
            connection_details = {"chain": chain,
                                  "rpc_user": rpc_user,
                                  "rpc_password": rpc_password,
                                  "rpc_port": rpc_port}
            connection_json = json.dumps(connection_details)
            with open("connection.json", "w+") as file:
                file.write(connection_json)
            rpc_connection = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
            try:
                ac_name = rpc_connection.getinfo()['name']
                break
            except:
                print("Connection failed! Is "+chain+" running?")
                pass
        else:
            print(colorize("Please input u/U, s/S or e/E ", "red"))
    return rpc_connection


def readme_tui(readme):
    with open(readme, 'r') as f:
        i = 0
        for line in f:
            print(line)
            i += 1
            if i == 20:
                userinput = input(colorize("\nPress [Enter] to continue, or [X] to exit\n", "blue"))
                if userinput == 'x' or userinput == 'x':
                    break
                else:
                    i = 0
        input(colorize("\nPress [Enter] to return to the menu\n", "blue"))
    f.close()

def getinfo_tui(rpc_connection):

    info_raw = rpclib.getinfo(rpc_connection)
    if isinstance(info_raw, dict):
        for key in info_raw:
            print("{}: {}".format(key, info_raw[key]))
        input("Press [Enter] to continue...")
    else:
        print("Error!\n")
        print(info_raw)
        input("\nPress [Enter] to continue...")


def token_create_tui(rpc_connection, name='', supply='', description=''):

    while True:
        try:
            if name == '':
                name = input("Set your token name: ")
            if supply == '':
                supply = input("Set your token supply: ")
            if description == '':
                description = input("Set your token description: ")
        except KeyboardInterrupt:
            break
        token_hex = rpclib.token_create(rpc_connection, name, supply, description)
        if token_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "magenta"))
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
                return token_txid


def oracles_info(rpc_connection):
    oracle_txid = select_oracle_txid(rpc_connection)
    if oracle_txid != 'back to menu':
        info = rpc_connection.oraclesinfo(oracle_txid)
        print(info)
        input("Press [Enter] to continue...")


def oracle_create_tui(rpc_connection, name='', description='', oracle_data_type=''):
    while True:
        try:
            if name == '':
                name = input("Set your oracle name: ")
            if description == '':
                description = input("Set your oracle description: ")
            if oracle_data_type == '':
                oracle_data_type = select_oracleType()
        except KeyboardInterrupt:
            break
        else:
            oracle_hex = rpclib.oracles_create(rpc_connection, name, description, oracle_data_type)
        if oracle_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "magenta"))
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
                print(colorize("Confirming oracle creation txid\n", "blue"))
                check_if_tx_in_mempool(rpc_connection, oracle_txid)
                try:
                    print(colorize("Initializing with oraclesfund\n", "blue"))
                    oraclesfund_hex = rpclib.oracles_fund(rpc_connection, oracle_txid)
                except KeyError:
                    print(oracle_txid)
                    print("Error")
                    input("Press [Enter] to continue...")
                    break
                finally:
                    oraclesfund_txid = rpclib.sendrawtransaction(rpc_connection, oraclesfund_hex['hex'])
                    check_if_tx_in_mempool(rpc_connection, oraclesfund_txid)
                input("Press [Enter] to continue...")
                return oracle_txid

def oracle_fund_tui(rpc_connection):
    try:
        print(colorize("Oracles created from this instance by TUI: \n", "blue"))
        with open("oracles_list", "r") as file:
            for oracle in file:
                print(oracle)
        print(colorize('_' * 65, "blue"))
        print("\n")
    except FileNotFoundError:
        print("Seems like a no oracles created from this instance yet\n")
        pass
    while True:
        try:
            oracle_txid = input("Input txid of oracle you want to register to: ")
        except KeyboardInterrupt:
            break   
        oracle_fund_hex = rpclib.oracles_fund(rpc_connection, oracle_txid)
        if oracle_fund_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "magenta"))
            print(oracle_fund_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                oracle_fund_txid = rpclib.sendrawtransaction(rpc_connection, oracle_fund_hex['hex'])
            except KeyError:
                print(oracle_fund_hex)
                print("Error")
                input("Press [Enter] to continue...")
                break
            else:
                print(colorize("Oracle fund transaction broadcasted: " + oracle_fund_txid, "green"))
                input("Press [Enter] to continue...")
                break

def oracle_register_tui(rpc_connection, oracle_txid='', data_fee=''):
    #TODO: have an idea since blackjoker new RPC call
    #grab all list and printout only or which owner match with node pubkey
    while True:
        try:
            if oracle_txid == '':
                oracle_txid = select_oracle_txid(rpc_connection)
            if data_fee == '':
                data_fee = input("Set publisher datafee (e.g. 0.001): ")
        except KeyboardInterrupt:
            break
        oracle_register_hex = rpclib.oracles_register(rpc_connection, oracle_txid, data_fee)
        if oracle_register_hex['result'] == "error":
            if oracle_register_hex['error'] == "error adding inputs from your Oracles CC address, please fund it first with oraclesfund rpc!":
                oraclesfund_hex = rpclib.oracles_fund(rpc_connection, oracle_txid)
                oraclesfund_txid = rpclib.sendrawtransaction(rpc_connection, oraclesfund_hex['hex'])
                check_if_tx_in_mempool(rpc_connection, oraclesfund_txid)
            else:
                print(colorize("\nSomething went wrong!\n", "magenta"))
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
                


def oracle_subscription_utxogen(rpc_connection, oracle_txid='', publisher_id='', data_fee='', utxo_num=''):
    # TODO: have an idea since blackjoker new RPC call
    # grab all list and printout only or which owner match with node pubkey
    if oracle_txid == '':
        oracle_txid = select_oracle_txid(rpc_connection)
    while True:
        try:
            if publisher_id == '':
                publisher_id = select_oracle_publisher(rpc_connection, oracle_txid)
            if data_fee == '':
                data_fee = input("Input subscription fee (in COINS!): ")
            if utxo_num == '':
                utxo_num = int(input("Input how many transactions you want to broadcast: "))
        except KeyboardInterrupt:
            break
        while utxo_num > 0:
            while True:
                oracle_subscription_hex = rpclib.oracles_subscribe(rpc_connection, oracle_txid, publisher_id, data_fee)
                oracle_subscription_txid = rpclib.sendrawtransaction(rpc_connection, oracle_subscription_hex['hex'])
                mempool = rpclib.get_rawmempool(rpc_connection)
                if oracle_subscription_txid in mempool:
                    break
                else:
                    pass
            print(colorize("Oracle subscription transaction broadcasted: " + oracle_subscription_txid, "green"))
            utxo_num = utxo_num - 1
            time.sleep(1)
            check_if_tx_in_mempool(rpc_connection, oracle_subscription_txid)
        input("Press [Enter] to continue...")
        break

def gateways_bind_tui(rpc_connection, token_id='', token_supply='', oracle_txid='',
                     coin_name=''):
    # main loop with keyboard interrupt handling
    while True:
        try:
            while True:
                if token_id == '':
                    token_id = select_tokenid(rpc_connection)                
                try:
                    token_name = rpclib.token_info(rpc_connection, token_id)["name"]
                except KeyError:
                    print(colorize("Not valid tokenid. Please try again.", "red"))
                    input("Press [Enter] to continue...")
                if token_supply == '':
                    token_info = rpclib.token_info(rpc_connection, token_id)
                    print(colorize("\n{} token total supply: {}\n".format(token_id, token_info["supply"]), "blue"))
                    token_supply = input("Input supply for token binding: ")
                if oracle_txid == '':
                    oracle_txid = input("Input id of oracle you want to use in gw bind: ")
                try:
                    oracle_name = rpclib.oracles_info(rpc_connection, oracle_txid)["name"]
                except KeyError:
                    print(colorize("Not valid oracle_txid. Please try again.", "red"))
                    input("Press [Enter] to continue...")
                while True:
                    if coin_name == '':
                        coin_name = input("Input external coin ticker (binded oracle and token need to have same name!): ")
                    if token_name == oracle_name and token_name == coin_name:
                        break
                    else:
                        print(colorize("Token name, oracle name and external coin ticker should match!", "red"))
                while True:
                    M = input("Input minimal amount of pubkeys needed for transaction confirmation (1 for non-multisig gw): ")
                    N = input("Input maximal amount of pubkeys needed for transaction confirmation (1 for non-multisig gw): ")
                    if (int(N) >= int(M)):
                        break
                    else:
                        print("Maximal amount of pubkeys should be more or equal than minimal. Please try again.")
                pubkeys = []
                print("Your pubkey is "+rpc_connection.getinfo()['pubkey'])
                for i in range(int(N)):
                    pubkeys.append(input("Input pubkey {}: ".format(i+1)))
                print(colorize("pubtype, wiftype and p2shtype of many coins can be viewed at https://github.com/jl777/coins/blob/master/coins", "blue"))
                # TODO: integrate coins repo to autofill these values if possible
                pubtype = input("Input pubtype of external coin ("+coin_name+"): ")
                p2shtype = input("Input p2shtype of external coin ("+coin_name+"): ")
                wiftype = input("Input wiftype of external coin ("+coin_name+"): ")
                args = [rpc_connection, token_id, oracle_txid, coin_name, str(token_supply), str(M), str(N)]
                new_args = [str(pubtype), str(p2shtype), str(wiftype)]
                args = args + pubkeys + new_args
                # broadcasting block
                try:
                    gateways_bind_hex = rpclib.gateways_bind(*args)
                except Exception as e:
                    print(e)
                    input("Press [Enter] to continue...")
                    break
                try:
                    gateways_bind_txid = rpclib.sendrawtransaction(rpc_connection, gateways_bind_hex["hex"])
                except Exception as e:
                    print(e)
                    print(gateways_bind_hex)
                    input("Press [Enter] to continue...")
                    break
                else:
                    print(colorize("Gateway bind transaction broadcasted: " + gateways_bind_txid, "green"))
                    file = open("gateways_list", "a")
                    file.writelines(gateways_bind_txid + "\n")
                    file.close()
                    print(colorize("Entry added to gateways_list file!\n", "green"))
                    input("Press [Enter] to continue...")
                    return gateways_bind_txid
            break
        except KeyboardInterrupt:
            break

# temporary :trollface: custom connection function solution
# to have connection to KMD daemon and cache it in separate file


def rpc_kmd_connection_tui():
    while True:
        restore_choice = input("Do you want to use KMD daemon connection details from previous session? [y/n]: ")
        if restore_choice == "y":
            try:
                with open("connection_kmd.json", "r") as file:
                    connection_json = json.load(file)
                    rpc_user = connection_json["rpc_user"]
                    rpc_password = connection_json["rpc_password"]
                    rpc_port = connection_json["rpc_port"]
                    rpc_connection_kmd = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
                    try:
                        print(rpc_connection_kmd.getinfo())
                        print(colorize("Successfully connected!\n", "green"))
                        input("Press [Enter] to continue...")
                        break
                    except Exception as e:
                        print(e)
                        print(colorize("NOT CONNECTED!\n", "red"))
                        input("Press [Enter] to continue...")
                        break
            except FileNotFoundError:
                print(colorize("You do not have cached KMD daemon connection details."
                               " Please select n for connection setup", "red"))
                input("Press [Enter] to continue...")
        elif restore_choice == "n":
            rpc_user = input("Input your rpc user: ")
            rpc_password = input("Input your rpc password: ")
            rpc_port = input("Input your rpc port: ")
            connection_details = {"rpc_user": rpc_user,
                                  "rpc_password": rpc_password,
                                  "rpc_port": rpc_port}
            connection_json = json.dumps(connection_details)
            with open("connection_kmd.json", "w+") as file:
                file.write(connection_json)
            rpc_connection_kmd = rpclib.rpc_connect(rpc_user, rpc_password, int(rpc_port))
            try:
                print(rpc_connection_kmd.getinfo())
                print(colorize("Successfully connected!\n", "green"))
                input("Press [Enter] to continue...")
                break
            except Exception as e:
                print(e)
                print(colorize("NOT CONNECTED!\n", "red"))
                input("Press [Enter] to continue...")
                break
        else:
            print(colorize("Please input y or n", "red"))
    return rpc_connection_kmd


def z_sendmany_twoaddresses(rpc_connection, sendaddress, recepient1, amount1, recepient2, amount2):
    str_sending_block = "[{{\"address\":\"{}\",\"amount\":{}}},{{\"address\":\"{}\",\"amount\":{}}}]".format(recepient1, amount1, recepient2, amount2)
    sending_block = json.loads(str_sending_block)
    operation_id = rpc_connection.z_sendmany(sendaddress,sending_block)
    return operation_id


def operationstatus_to_txid(rpc_connection, zstatus):
    str_sending_block = "[\"{}\"]".format(zstatus)
    sending_block = json.loads(str_sending_block)
    operation_json = rpc_connection.z_getoperationstatus(sending_block)
    operation_dump = json.dumps(operation_json)
    operation_dict = json.loads(operation_dump)[0]
    txid = operation_dict['result']['txid']
    return txid


def gateways_send_kmd(rpc_connection, gw_deposit_addr=''):
    # TODO: have to handle CTRL+C on text input
    print(colorize("Please be carefull when input wallet addresses and amounts since all transactions doing in real KMD!", "magenta"))
    print("Your addresses with balances: ")
    sendaddress = select_address(rpc_connection)
    amount1 = 0.0001
    if gw_deposit_addr == '':
       gw_deposit_addr = input("Input gateway deposit address: ")
    while True:
        gw_recipient_addr = input("Input Gateway recipient address (linked to pubkey which will receive tokens): ")
        if gw_deposit_addr == gw_recipient_addr:
            print("Gateway recipient address must be different to Gateway address! Try again.")
        else:
            break
    file = open("deposits_list", "a")
    #have to show here deposit addresses for gateways created by user
    gw_deposit_amount = float(input("Input how many KMD you want to deposit on this gateway: "))
    operation = z_sendmany_twoaddresses(rpc_connection, sendaddress, gw_recipient_addr,
                                     amount1, gw_deposit_addr, gw_deposit_amount)
    print("Operation proceed! " + str(operation) + " Let's wait 2 seconds to get txid")
    # trying to avoid pending status of operation
    time.sleep(2)
    gw_sendmany_txid = operationstatus_to_txid(rpc_connection, operation)
    file.writelines(gw_sendmany_txid + "\n")
    file.close()
    check_if_tx_in_mempool(rpc_connection, gw_sendmany_txid)
    print(colorize("KMD Transaction ID: " + str(gw_sendmany_txid) + " Entry added to deposits_list file", "green"))
    input("Press [Enter] to continue...")
    return gw_sendmany_txid, gw_recipient_addr, gw_deposit_amount


def gateways_deposit_tui(rpc_connection_assetchain, rpc_connection_komodo,
                        bind_txid='', coin_name='', coin_txid='', amount='',
                        recipient_addr=''):
    while True:
        if bind_txid == '':
            bind_txid = input("Input your gateway bind txid: ")
        if coin_name == '':
            coin_name = input("Input your external coin ticker (e.g. KMD): ")
        if coin_txid == '':
            coin_txid = input("Input your deposit txid: ")
        if recipient_addr == '':
            dest_pub = input("Input pubkey of gateways deposit recipient address: ")
        else:
            dest_pub = input("Input pubkey of gateways deposit recipient address ("+recipient_addr+"): ")
        if amount == '':
            amount = input("Input amount of your deposit: ")
        raw_tx_info = rpc_connection_komodo.getrawtransaction(coin_txid, 1)
        height = raw_tx_info["height"]
        last_ntx_height = raw_tx_info['last_notarized_height']
        while last_ntx_height < height:
            print("Waiting 60 sec for deposit txid to be notarized...")
            print("Deposit txid height ["+str(height)+"] vs last notarization height ["+str(last_ntx_height)+"]")
            time.sleep(60)
            raw_tx_info = rpc_connection_komodo.getrawtransaction(coin_txid, 1)
            height = raw_tx_info["height"]
            last_ntx_height = raw_tx_info['last_notarized_height']
        deposit_hex = raw_tx_info["hex"]
        claim_vout = "0"
        proof_sending_block = "[\"{}\"]".format(coin_txid)
        proof = rpc_connection_komodo.gettxoutproof(json.loads(proof_sending_block))
        deposit_hex = rpclib.gateways_deposit(rpc_connection_assetchain, bind_txid, height, coin_name, \
                         coin_txid, claim_vout, deposit_hex, proof, dest_pub, amount)
        deposit_txid = rpclib.sendrawtransaction(rpc_connection_assetchain, deposit_hex["hex"])
        check_if_tx_in_mempool(rpc_connection_assetchain, deposit_txid)
        print("Done! Gateways deposit txid is: " + deposit_txid + " Please not forget to claim your deposit!")
        input("Press [Enter] to continue...")
        return deposit_txid, dest_pub
        
def gateways_claim_tui(rpc_connection, bind_txid='', coin_name='', deposit_txid='',
                       dest_pub='', amount=''):
    while True:
        if bind_txid == '':
            bind_txid = input("Input your gateway bind txid: ")
        if coin_name == '':
            coin_name = input("Input your external coin ticker (e.g. KMD): ")
        if deposit_txid == '':
            deposit_txid = input("Input your gateways deposit txid: ")
        if dest_pub == '':
            dest_pub = input("Input pubkey which claim deposit: ")
        ac_info = rpc_connection.getinfo()
        if dest_pub != ac_info['pubkey']:
            print("Error: Destination pubkey must be used to launch daemon!")
            print("Destination pubkey: "+dest_pub)
            print("Daemon pubkey: "+ac_info['pubkey'])
            input("Press [Enter] to continue...")
            break
        if amount == '':
            amount = input("Input amount of your deposit: ")
        claim_hex = rpclib.gateways_claim(rpc_connection, bind_txid, coin_name, deposit_txid, dest_pub, amount)
        try:
            claim_txid = rpclib.sendrawtransaction(rpc_connection, claim_hex["hex"])
        except Exception as e:
            print(e)
            print(claim_hex)
            input("Press [Enter] to continue...")
            break
        else:
            check_if_tx_in_mempool(rpc_connection, claim_txid)
            print("Succesfully claimed! Claim transaction id: " + claim_txid)
            input("Press [Enter] to continue...")
            return claim_txid
            break


def gateways_withdrawal_tui(rpc_connection):
    while True:
        bind_txid = input("Input your gateway bind txid: ")
        coin_name = input("Input your external coin ticker (e.g. KMD): ")
        withdraw_pub = input("Input pubkey to which you want to withdraw: ")
        amount = input("Input amount of withdrawal: ")
        withdraw_hex = rpclib.gateways_withdraw(rpc_connection, bind_txid, coin_name, withdraw_pub, amount)
        withdraw_txid = rpclib.sendrawtransaction(rpc_connection, withdraw_hex["hex"])
        print(withdraw_txid)
        input("Press [Enter] to continue...")
        break


def print_mempool(rpc_connection):
    while True:
        mempool = rpclib.get_rawmempool(rpc_connection)
        tx_counter = 0
        print(colorize("Transactions in mempool: \n", "magenta"))
        for transaction in mempool:
            print(transaction + "\n")
            tx_counter = tx_counter + 1
        print("Total: " + str(tx_counter) + " transactions\n")
        print("R + Enter to refresh list. E + Enter to exit menu." + "\n")
        is_refresh = input("Choose your destiny: ")
        if is_refresh == "R":
            print("\n")
            pass
        elif is_refresh == "E":
            print("\n")
            break
        else:
            print("\nPlease choose R or E\n")


def print_tokens_list(rpc_connection):
    # TODO: have to print it with tokeninfo to have sense
    pass


def print_tokens_balances(rpc_connection):
    # TODO: checking tokenbalance for each token from tokenlist and reflect non zero ones
    pass


def hexdump(filename, chunk_size=1<<15):
    data = ""
    #add_spaces = partial(re.compile(b'(..)').sub, br'\1 ')
    #write = getattr(sys.stdout, 'buffer', sys.stdout).write
    with open(filename, 'rb') as file:
        for chunk in iter(partial(file.read, chunk_size), b''):
            data += str(hexlify(chunk).decode())
    return data


def convert_file_oracle_d(rpc_connection):
    while True:
        path = input("Input path to file you want to upload to oracle: ")
        try:
            hex_data = (hexdump(path, 1))[2:]
        except Exception as e:
            print(e)
            print("Seems something goes wrong (I guess you've specified wrong path)!")
            input("Press [Enter] to continue...")
            break
        else:
            length = round(len(hex_data) / 2)
            if length > 256:
                print("Length: " + str(length) + " bytes")
                print("File is too big for this app")
                input("Press [Enter] to continue...")
                break
            else:
                hex_length = format(length, '#04x')[2:]
                data_for_oracle = str(hex_length) + hex_data
                print("File hex representation: \n")
                print(data_for_oracle + "\n")
                print("Length: " + str(length) + " bytes")
                print("File converted!")
                new_oracle_hex = rpclib.oracles_create(rpc_connection, "tonyconvert", path, "d")
                new_oracle_txid = rpclib.sendrawtransaction(rpc_connection, new_oracle_hex["hex"])
                time.sleep(0.5)
                oracle_register_hex = rpclib.oracles_register(rpc_connection, new_oracle_txid, "10000")
                oracle_register_txid = rpclib.sendrawtransaction(rpc_connection, oracle_register_hex["hex"])
                time.sleep(0.5)
                oracle_subscribe_hex = rpclib.oracles_subscribe(rpc_connection, new_oracle_txid, rpclib.getinfo(rpc_connection)["pubkey"], "0.001")
                oracle_subscribe_txid = rpclib.sendrawtransaction(rpc_connection, oracle_subscribe_hex["hex"])
                time.sleep(0.5)
                while True:
                    mempool = rpclib.get_rawmempool(rpc_connection)
                    if oracle_subscribe_txid in mempool:
                        print("Waiting for oracle subscribtion tx to be mined" + "\n")
                        time.sleep(6)
                        pass
                    else:
                        break
                oracles_data_hex = rpclib.oracles_data(rpc_connection, new_oracle_txid, data_for_oracle)
                try:
                    oracle_data_txid = rpclib.sendrawtransaction(rpc_connection, oracles_data_hex["hex"])
                except Exception as e:
                    print(oracles_data_hex)
                    print(e)
                print("Oracle created: " + str(new_oracle_txid))
                print("Data published: " + str(oracle_data_txid))
                input("Press [Enter] to continue...")
                break


def convert_file_oracle_D(rpc_connection):
    while True:
        path = input("Input path to file you want to upload to oracle: ")
        try:
            hex_data = (hexdump(path, 1))
        except Exception as e:
            print(e)
            print("Seems something goes wrong (I guess you've specified wrong path)!")
            input("Press [Enter] to continue...")
            break
        else:
            length = round(len(hex_data) / 2)
            # if length > 800000:
            #     print("Too big file size to upload for this version of program. Maximum size is 800KB.")
            #     input("Press [Enter] to continue...")
            #     break
            if length > 8000:
                # if file is more than 8000 bytes - slicing it to <= 8000 bytes chunks (16000 symbols = 8000 bytes)
                data = [hex_data[i:i + 16000] for i in range(0, len(hex_data), 16000)]
                chunks_amount = len(data)
                # TODO: have to create oracle but subscribe this time chunks amount times to send whole file in same block
                # TODO: 2 - on some point file will not fit block - have to find this point
                # TODO: 3 way how I want to implement it first will keep whole file in RAM - have to implement some way to stream chunks to oracle before whole file readed
                # TODO: have to "optimise" registration fee
                # Maybe just check size first by something like a du ?
                print("Length: " + str(length) + " bytes.\n Chunks amount: " + str(chunks_amount))
                new_oracle_hex = rpclib.oracles_create(rpc_connection, "tonyconvert_" + str(chunks_amount), path, "D")
                new_oracle_txid = rpclib.sendrawtransaction(rpc_connection, new_oracle_hex["hex"])
                time.sleep(0.5)
                oracle_register_hex = rpclib.oracles_register(rpc_connection, new_oracle_txid, "10000")
                oracle_register_txid = rpclib.sendrawtransaction(rpc_connection, oracle_register_hex["hex"])
                # subscribe chunks_amount + 1 times, but lets limit our broadcasting 100 tx per block (800KB/block)
                if chunks_amount > 100:
                    utxo_num = 101
                else:
                    utxo_num = chunks_amount
                while utxo_num > 0:
                    while True:
                        oracle_subscription_hex = rpclib.oracles_subscribe(rpc_connection, new_oracle_txid, rpclib.getinfo(rpc_connection)["pubkey"], "0.001")
                        oracle_subscription_txid = rpclib.sendrawtransaction(rpc_connection,
                                                                             oracle_subscription_hex['hex'])
                        mempool = rpclib.get_rawmempool(rpc_connection)
                        if oracle_subscription_txid in mempool:
                            break
                        else:
                            pass
                    print(colorize("Oracle subscription transaction broadcasted: " + oracle_subscription_txid, "green"))
                    utxo_num = utxo_num - 1
                # waiting for last broadcasted subscribtion transaction to be mined to be sure that money are on oracle balance
                while True:
                    mempool = rpclib.get_rawmempool(rpc_connection)
                    if oracle_subscription_txid in mempool:
                        print("Waiting for oracle subscribtion tx to be mined" + "\n")
                        time.sleep(6)
                        pass
                    else:
                        break
                print("Oracle preparation is finished. Oracle txid: " + new_oracle_txid)
                # can publish data now
                counter = 0
                for chunk in data:
                    hex_length_bigendian = format(round(len(chunk) / 2), '#06x')[2:]
                    # swap to get little endian length
                    a = hex_length_bigendian[2:]
                    b = hex_length_bigendian[:2]
                    hex_length = a + b
                    data_for_oracle = str(hex_length) + chunk
                    counter = counter + 1
                    # print("Chunk number: " + str(counter) + "\n")
                    # print(data_for_oracle)
                    try:
                        oracles_data_hex = rpclib.oracles_data(rpc_connection, new_oracle_txid, data_for_oracle)
                    except Exception as e:
                        print(data_for_oracle)
                        print(e)
                        input("Press [Enter] to continue...")
                        break
                    # on broadcasting ensuring that previous one reached mempool before blast next one
                    while True:
                        mempool = rpclib.get_rawmempool(rpc_connection)
                        oracle_data_txid = rpclib.sendrawtransaction(rpc_connection, oracles_data_hex["hex"])
                        #time.sleep(0.1)
                        if oracle_data_txid in mempool:
                            break
                        else:
                            pass
                    # blasting not more than 100 at once (so maximum capacity per block can be changed here)
                    # but keep in mind that registration UTXOs amount needs to be changed too !
                    if counter % 100 == 0 and chunks_amount > 100:
                        while True:
                            mempool = rpclib.get_rawmempool(rpc_connection)
                            if oracle_data_txid in mempool:
                                print("Waiting for previous data chunks to be mined before send new ones" + "\n")
                                print("Sent " + str(counter) + " chunks from " + str(chunks_amount))
                                time.sleep(6)
                                pass
                            else:
                                break

                print("Last baton: " + oracle_data_txid)
                input("Press [Enter] to continue...")
                break
            # if file suits single oraclesdata just broadcasting it straight without any slicing
            else:
                hex_length_bigendian = format(length, '#06x')[2:]
                # swap to get little endian length
                a = hex_length_bigendian[2:]
                b = hex_length_bigendian[:2]
                hex_length = a + b
                data_for_oracle = str(hex_length) + hex_data
                print("File hex representation: \n")
                print(data_for_oracle + "\n")
                print("Length: " + str(length) + " bytes")
                print("File converted!")
                new_oracle_hex = rpclib.oracles_create(rpc_connection, "tonyconvert_" + "1", path, "D")
                new_oracle_txid = rpclib.sendrawtransaction(rpc_connection, new_oracle_hex["hex"])
                time.sleep(0.5)
                oracle_register_hex = rpclib.oracles_register(rpc_connection, new_oracle_txid, "10000")
                oracle_register_txid = rpclib.sendrawtransaction(rpc_connection, oracle_register_hex["hex"])
                time.sleep(0.5)
                oracle_subscribe_hex = rpclib.oracles_subscribe(rpc_connection, new_oracle_txid, rpclib.getinfo(rpc_connection)["pubkey"], "0.001")
                oracle_subscribe_txid = rpclib.sendrawtransaction(rpc_connection, oracle_subscribe_hex["hex"])
                time.sleep(0.5)
                while True:
                    mempool = rpclib.get_rawmempool(rpc_connection)
                    if oracle_subscribe_txid in mempool:
                        print("Waiting for oracle subscribtion tx to be mined" + "\n")
                        time.sleep(6)
                        pass
                    else:
                        break
                oracles_data_hex = rpclib.oracles_data(rpc_connection, new_oracle_txid, data_for_oracle)
                try:
                    oracle_data_txid = rpclib.sendrawtransaction(rpc_connection, oracles_data_hex["hex"])
                except Exception as e:
                    print(oracles_data_hex)
                    print(e)
                    input("Press [Enter] to continue...")
                    break
                else:
                    print("Oracle created: " + str(new_oracle_txid))
                    print("Data published: " + str(oracle_data_txid))
                    input("Press [Enter] to continue...")
                    break


def get_files_list(rpc_connection):

    start_time = time.time()
    oracles_list = rpclib.oracles_list(rpc_connection)
    files_list = []
    for oracle_txid in oracles_list:
        oraclesinfo_result = rpclib.oracles_info(rpc_connection, oracle_txid)
        description = oraclesinfo_result['description']
        name = oraclesinfo_result['name']
        if name[0:12] == 'tonyconvert_':
            new_file = '[' + name + ': ' + description + ']: ' + oracle_txid
            files_list.append(new_file)
    print("--- %s seconds ---" % (time.time() - start_time))
    return files_list


def display_files_list(rpc_connection):
    print("Scanning oracles. Please wait...")
    list_to_display = get_files_list(rpc_connection)
    while True:
        for file in list_to_display:
            print(file + "\n")
        input("Press [Enter] to continue...")
        break


def files_downloader(rpc_connection):
    while True:
        display_files_list(rpc_connection)
        print("\n")
        oracle_txid = input("Input oracle ID you want to download file from: ")
        output_path = input("Input output path for downloaded file (name included) e.g. /home/test.txt: ")
        oracle_info = rpclib.oracles_info(rpc_connection, oracle_txid)
        name = oracle_info['name']
        latest_baton_txid = oracle_info['registered'][0]['batontxid']
        if name[0:12] == 'tonyconvert_':
            # downloading process here
            chunks_amount = int(name[12:])
            data = rpclib.oracles_samples(rpc_connection, oracle_txid, latest_baton_txid, str(chunks_amount))["samples"]
            for chunk in reversed(data):
                with open(output_path, 'ab+') as file:
                    file.write(unhexlify(chunk[0]))
            print("I hope that file saved to " + output_path + "\n")
            input("Press [Enter] to continue...")
            break

        else:
            print("I cant recognize file inside this oracle. I'm very sorry, boss.")
            input("Press [Enter] to continue...")
            break


def marmara_receive_tui(rpc_connection):
    while True:
        issuer_pubkey = input("Input pubkey of person who do you want to receive MARMARA from: ")
        issuance_sum = input("Input amount of MARMARA you want to receive: ")
        blocks_valid = input("Input amount of blocks for cheque matures: ")
        try:
            marmara_receive_txinfo = rpc_connection.marmarareceive(issuer_pubkey, issuance_sum, "MARMARA", blocks_valid)
            marmara_receive_txid = rpc_connection.sendrawtransaction(marmara_receive_txinfo["hex"])
            print("Marmara receive txid broadcasted: " + marmara_receive_txid + "\n")
            print(json.dumps(marmara_receive_txinfo, indent=4, sort_keys=True) + "\n")
            with open("receive_txids.txt", 'a+') as file:
                file.write(marmara_receive_txid + "\n")
                file.write(json.dumps(marmara_receive_txinfo, indent=4, sort_keys=True) + "\n")
            print("Transaction id is saved to receive_txids.txt file.")
            input("Press [Enter] to continue...")
            break
        except Exception as e:
            print(marmara_receive_txinfo)
            print(e)
            print("Something went wrong. Please check your input")


def marmara_issue_tui(rpc_connection):
    while True:
        receiver_pubkey = input("Input pubkey of person who do you want to issue MARMARA: ")
        issuance_sum = input("Input amount of MARMARA you want to issue: ")
        maturing_block = input("Input number of block on which issuance mature: ")
        approval_txid = input("Input receiving request transaction id: ")
        try:
            marmara_issue_txinfo = rpc_connection.marmaraissue(receiver_pubkey, issuance_sum, "MARMARA", maturing_block, approval_txid)
            marmara_issue_txid = rpc_connection.sendrawtransaction(marmara_issue_txinfo["hex"])
            print("Marmara issuance txid broadcasted: " + marmara_issue_txid + "\n")
            print(json.dumps(marmara_issue_txinfo, indent=4, sort_keys=True) + "\n")
            with open("issue_txids.txt", "a+") as file:
                file.write(marmara_issue_txid + "\n")
                file.write(json.dumps(marmara_issue_txinfo, indent=4, sort_keys=True) + "\n")
            print("Transaction id is saved to issue_txids.txt file.")
            input("Press [Enter] to continue...")
            break
        except Exception as e:
            print(marmara_issue_txinfo)
            print(e)
            print("Something went wrong. Please check your input")


def marmara_creditloop_tui(rpc_connection):
    while True:
        loop_txid = input("Input transaction ID of credit loop you want to get info about: ")
        try:
            marmara_creditloop_info = rpc_connection.marmaracreditloop(loop_txid)
            print(json.dumps(marmara_creditloop_info, indent=4, sort_keys=True) + "\n")
            input("Press [Enter] to continue...")
            break
        except Exception as e:
            print(marmara_creditloop_info)
            print(e)
            print("Something went wrong. Please check your input")


def marmara_settlement_tui(rpc_connection):
    while True:
        loop_txid = input("Input transaction ID of credit loop to make settlement: ")
        try:
            marmara_settlement_info = rpc_connection.marmarasettlement(loop_txid)
            marmara_settlement_txid = rpc_connection.sendrawtransaction(marmara_settlement_info["hex"])
            print("Loop " + loop_txid + " succesfully settled!\nSettlement txid: " + marmara_settlement_txid)
            with open("settlement_txids.txt", "a+") as file:
                file.write(marmara_settlement_txid + "\n")
                file.write(json.dumps(marmara_settlement_info, indent=4, sort_keys=True) + "\n")
            print("Transaction id is saved to settlement_txids.txt file.")
            input("Press [Enter] to continue...")
            break
        except Exception as e:
            print(marmara_settlement_info)
            print(e)
            print("Something went wrong. Please check your input")
            input("Press [Enter] to continue...")
            break


def marmara_lock_tui(rpc_connection):
    while True:
        amount = input("Input amount of coins you want to lock for settlement and staking: ")
        unlock_height = input("Input height on which coins should be unlocked: ")
        try:
            marmara_lock_info = rpc_connection.marmaralock(amount, unlock_height)
            marmara_lock_txid = rpc_connection.sendrawtransaction(marmara_lock_info["hex"])
            with open("lock_txids.txt", "a+") as file:
                file.write(marmara_lock_txid + "\n")
                file.write(json.dumps(marmara_lock_info, indent=4, sort_keys=True) + "\n")
            print("Transaction id is saved to lock_txids.txt file.")
            input("Press [Enter] to continue...")
            break
        except Exception as e:
            print(e)
            print("Something went wrong. Please check your input")
            input("Press [Enter] to continue...")
            break


def marmara_info_tui(rpc_connection):
    while True:
        firstheight = input("Input first height (default 0): ")
        if not firstheight:
            firstheight = "0"
        lastheight = input("Input last height (default current (0) ): ")
        if not lastheight:
            lastheight = "0"
        minamount = input("Input min amount (default 0): ")
        if not minamount:
            minamount = "0"
        maxamount = input("Input max amount (default 0): ")
        if not maxamount:
            maxamount = "0"
        issuerpk = input("Optional. Input issuer public key: ")
        try:
            if issuerpk:
                marmara_info = rpc_connection.marmarainfo(firstheight, lastheight, minamount, maxamount, "MARMARA", issuerpk)
            else:
                marmara_info = rpc_connection.marmarainfo(firstheight, lastheight, minamount, maxamount)
            print(json.dumps(marmara_info, indent=4, sort_keys=True) + "\n")
            input("Press [Enter] to continue...")
            break
        except Exception as e:
            print(marmara_info)
            print(e)
            print("Something went wrong. Please check your input")
            input("Press [Enter] to continue...")
            break


def rogue_game_info(rpc_connection, game_txid):
    game_info_arg = '"' + "[%22" + game_txid + "%22]" + '"'
    game_info = rpc_connection.cclib("gameinfo", "17", game_info_arg)
    return game_info


def rogue_game_register(rpc_connection, game_txid, player_txid = False):
    if player_txid:
        registration_info_arg = '"' + "[%22" + game_txid + "%22,%22" + player_txid + "%22]" + '"'
    else:
        registration_info_arg = '"' + "[%22" + game_txid + "%22]" + '"'
    registration_info = rpc_connection.cclib("register", "17", registration_info_arg)
    return registration_info


def rogue_pending(rpc_connection):
    rogue_pending_list = rpc_connection.cclib("pending", "17")
    return rogue_pending_list


def rogue_bailout(rpc_connection, game_txid):
    bailout_info_arg = '"' + "[%22" + game_txid + "%22]" + '"'
    bailout_info = rpc_connection.cclib("bailout", "17", bailout_info_arg)
    return bailout_info


def rogue_highlander(rpc_connection, game_txid):
    highlander_info_arg = '"' + "[%22" + game_txid + "%22]" + '"'
    highlander_info = rpc_connection.cclib("highlander", "17", highlander_info_arg)
    return highlander_info


def rogue_players_list(rpc_connection):
    rogue_players_list = rpc_connection.cclib("players", "17")
    return rogue_players_list


def rogue_player_info(rpc_connection, playertxid):
    player_info_arg = '"' + "[%22" + playertxid + "%22]" + '"'
    player_info = rpc_connection.cclib("playerinfo", "17", player_info_arg)
    return player_info


def rogue_extract(rpc_connection, game_txid, pubkey):
    extract_info_arg = '"' + "[%22" + game_txid + "%22,%22" + pubkey + "%22]" + '"'
    extract_info = rpc_connection.cclib("extract", "17", extract_info_arg)
    return extract_info


def rogue_keystrokes(rpc_connection, game_txid, keystroke):
    rogue_keystrokes_arg = '"' + "[%22" + game_txid + "%22,%22" + keystroke + "%22]" + '"'
    keystroke_info = rpc_connection.cclib("keystrokes", "17", rogue_keystrokes_arg)
    return keystroke_info


def print_multiplayer_games_list(rpc_connection):
    while True:
        pending_list = rogue_pending(rpc_connection)
        multiplayer_pending_list = []
        for game in pending_list["pending"]:
            if rogue_game_info(rpc_connection, game)["maxplayers"] > 1:
                multiplayer_pending_list.append(game)
        print("Multiplayer games availiable to join: \n")
        for active_multiplayer_game in multiplayer_pending_list:
            game_info = rogue_game_info(rpc_connection, active_multiplayer_game)
            print(colorize("\n================================\n", "green"))
            print("Game txid: " + game_info["gametxid"])
            print("Game buyin: " + str(game_info["buyin"]))
            print("Game height: " + str(game_info["gameheight"]))
            print("Start height: " + str(game_info["start"]))
            print("Alive players: " + str(game_info["alive"]))
            print("Registered players: " + str(game_info["numplayers"]))
            print("Max players: " + str(game_info["maxplayers"]))
            print(colorize("\n***\n", "blue"))
            print("Players in game:")
            for player in game_info["players"]:
                print("Slot: " + str(player["slot"]))
                if "baton" in player.keys():
                    print("Baton: " + str(player["baton"]))
                if "tokenid" in player.keys():
                    print("Tokenid: " + str(player["tokenid"]))
                print("Is mine?: " + str(player["ismine"]))
        print(colorize("\nR + Enter - refresh list.\nE + Enter - to the game choice.\nCTRL + C - back to main menu", "blue"))
        is_refresh = input("Choose your destiny: ")
        if is_refresh == "R":
            print("\n")
            pass
        elif is_refresh == "E":
            print("\n")
            break
        else:
            print("\nPlease choose R or E\n")


def rogue_newgame_singleplayer(rpc_connection, is_game_a_rogue=True):
    try:
        new_game_txid = rpc_connection.cclib("newgame", "17", "[1]")["txid"]
        print("New singleplayer training game succesfully created. txid: " + new_game_txid)
        while True:
            mempool = rpc_connection.getrawmempool()
            if new_game_txid in mempool:
                print(colorize("Waiting for game transaction to be mined", "blue"))
                time.sleep(5)
            else:
                print(colorize("Game transaction is mined", "green"))
                break
        players_list = rogue_players_list(rpc_connection)
        if len(players_list["playerdata"]) > 0:
            print_players_list(rpc_connection)
            while True:
                is_choice_needed = input("Do you want to choose a player for this game? [y/n] ")
                if is_choice_needed == "y":
                    player_txid = input("Please input player txid: ")
                    newgame_regisration_txid = rogue_game_register(rpc_connection, new_game_txid, player_txid)["txid"]
                    break
                elif is_choice_needed == "n":
                    set_warriors_name(rpc_connection)
                    newgame_regisration_txid = rogue_game_register(rpc_connection, new_game_txid)["txid"]
                    break
                else:
                    print("Please choose y or n !")
        else:
            print("No players available to select")
            input("Press [Enter] to continue...")
            newgame_regisration_txid = rogue_game_register(rpc_connection, new_game_txid)["txid"]
        while True:
            mempool = rpc_connection.getrawmempool()
            if newgame_regisration_txid in mempool:
                print(colorize("Waiting for registration transaction to be mined", "blue"))
                time.sleep(5)
            else:
                print(colorize("Registration transaction is mined", "green"))
                break
        game_info = rogue_game_info(rpc_connection, new_game_txid)
        start_time = time.time()
        while True:
            if is_game_a_rogue:
                subprocess.call(["cc/rogue/rogue", str(game_info["seed"]), str(game_info["gametxid"])])
            else:
                subprocess.call(["cc/games/tetris", str(game_info["seed"]), str(game_info["gametxid"])])
            time_elapsed = time.time() - start_time
            if time_elapsed > 1:
                break
            else:
                print("Game less than 1 second. Trying to start again")
                time.sleep(1)
        game_end_height = int(rpc_connection.getinfo()["blocks"])
        while True:
            current_height = int(rpc_connection.getinfo()["blocks"])
            height_difference = current_height - game_end_height
            if height_difference == 0:
                print(current_height)
                print(game_end_height)
                print(colorize("Waiting for next block before bailout", "blue"))
                time.sleep(5)
            else:
                break
        #print("\nKeystrokes of this game:\n")
        #time.sleep(0.5)
        while True:
            keystrokes_rpc_responses = find_game_keystrokes_in_log(new_game_txid)[1::2]
            if len(keystrokes_rpc_responses) < 1:
                print("No keystrokes broadcasted yet. Let's wait 5 seconds")
                time.sleep(5)
            else:
                break
        #print(keystrokes_rpc_responses)
        for keystroke in keystrokes_rpc_responses:
            json_keystroke = json.loads(keystroke)["result"]
            if "status" in json_keystroke.keys() and json_keystroke["status"] == "error":
                while True:
                    print("Trying to re-brodcast keystroke")
                    keystroke_rebroadcast = rogue_keystrokes(rpc_connection, json_keystroke["gametxid"], json_keystroke["keystrokes"])
                    if "txid" in keystroke_rebroadcast.keys():
                        print("Keystroke broadcasted! txid: " + keystroke_rebroadcast["txid"])
                        break
                    else:
                        print("Let's try again in 5 seconds")
                        time.sleep(5)
        # waiting for last keystroke confirmation here
        last_keystroke_json = json.loads(keystrokes_rpc_responses[-1])
        while True:
            while True:
                try:
                    rpc_connection.sendrawtransaction(last_keystroke_json["result"]["hex"])
                except Exception as e:
                    pass
                try:
                    confirmations_amount = rpc_connection.getrawtransaction(last_keystroke_json["result"]["txid"], 1)["confirmations"]
                    break
                except Exception as e:
                    print(e)
                    print("Let's wait a little bit more")
                    time.sleep(5)
                    pass
            if confirmations_amount < 2:
                print("Last keystroke not confirmed yet! Let's wait a little")
                time.sleep(10)
            else:
                print("Last keystroke confirmed!")
                break
        while True:
            print("\nExtraction info:\n")
            extraction_info = rogue_extract(rpc_connection, new_game_txid, rpc_connection.getinfo()["pubkey"])
            if extraction_info["status"] == "error":
                print(colorize("Your warrior died or no any information about game was saved on blockchain", "red"))
                print("If warrior was alive - try to wait a little (choose n to wait for a next block). If he is dead - you can bailout now (choose y).")
            else:
                print("Current game state:")
                print("Game txid: " + extraction_info["gametxid"])
                print("Information about game saved on chain: " + extraction_info["extracted"])
            print("\n")
            is_bailout_needed = input("Do you want to make bailout now [y] or wait for one more block [n]? [y/n]: ")
            if is_bailout_needed == "y":
                bailout_info = rogue_bailout(rpc_connection, new_game_txid)
                while True:
                    try:
                        confirmations_amount = rpc_connection.getrawtransaction(bailout_info["txid"], 1)["confirmations"]
                        break
                    except Exception as e:
                        print(e)
                        print("Bailout not on blockchain yet. Let's wait a little bit more")
                        time.sleep(20)
                        pass
                break
            elif is_bailout_needed == "n":
                game_end_height = int(rpc_connection.getinfo()["blocks"])
                while True:
                    current_height = int(rpc_connection.getinfo()["blocks"])
                    height_difference = current_height - game_end_height
                    if height_difference == 0:
                        print(current_height)
                        print(game_end_height)
                        print(colorize("Waiting for next block before bailout", "blue"))
                        time.sleep(5)
                    else:
                        break
            else:
                print("Please choose y or n !")
        print(bailout_info)
        print("\nGame is finished!\n")
        bailout_txid = bailout_info["txid"]
        input("Press [Enter] to continue...")
    except Exception as e:
        print("Something went wrong.")
        print(e)
        input("Press [Enter] to continue...")


def play_multiplayer_game(rpc_connection):
    # printing list of user active multiplayer games
    active_games_list = rpc_connection.cclib("games", "17")["games"]
    active_multiplayer_games_list = []
    for game in active_games_list:
        gameinfo = rogue_game_info(rpc_connection, game)
        if gameinfo["maxplayers"] > 1:
            active_multiplayer_games_list.append(gameinfo)
    games_counter = 0
    for active_multiplayer_game in active_multiplayer_games_list:
        games_counter = games_counter + 1
        is_ready_to_start = False
        try:
            active_multiplayer_game["seed"]
            is_ready_to_start = True
        except Exception as e:
            pass
        print(colorize("\n================================\n", "green"))
        print("Game txid: " + active_multiplayer_game["gametxid"])
        print("Game buyin: " + str(active_multiplayer_game["buyin"]))
        if is_ready_to_start:
            print(colorize("Ready for start!", "green"))
        else:
            print(colorize("Not ready for start yet, wait until start height!", "red"))
        print("Game height: " + str(active_multiplayer_game["gameheight"]))
        print("Start height: " + str(active_multiplayer_game["start"]))
        print("Alive players: " + str(active_multiplayer_game["alive"]))
        print("Registered players: " + str(active_multiplayer_game["numplayers"]))
        print("Max players: " + str(active_multiplayer_game["maxplayers"]))
        print(colorize("\n***\n", "blue"))
        print("Players in game:")
        for player in active_multiplayer_game["players"]:
            print("Slot: " + str(player["slot"]))
            print("Baton: " + str(player["baton"]))
            print("Tokenid: " +  str(player["tokenid"]))
            print("Is mine?: " + str(player["ismine"]))
    # asking user if he want to start any of them
    while True:
        start_game = input("\nDo you want to start any of your pendning multiplayer games?[y/n]: ")
        if start_game == "y":
            new_game_txid = input("Input txid of game which you want to start: ")
            game_info = rogue_game_info(rpc_connection, new_game_txid)
            try:
                start_time = time.time()
                while True:
                    subprocess.call(["cc/rogue/rogue", str(game_info["seed"]), str(game_info["gametxid"])])
                    time_elapsed = time.time() - start_time
                    if time_elapsed > 1:
                        break
                    else:
                        print("Game less than 1 second. Trying to start again")
                        time.sleep(1)
            except Exception as e:
                print("Maybe game isn't ready for start yet or your input was not correct, sorry.")
                input("Press [Enter] to continue...")
                break
            game_end_height = int(rpc_connection.getinfo()["blocks"])
            while True:
                current_height = int(rpc_connection.getinfo()["blocks"])
                height_difference = current_height - game_end_height
                if height_difference == 0:
                    print(current_height)
                    print(game_end_height)
                    print(colorize("Waiting for next block before bailout or highlander", "blue"))
                    time.sleep(5)
                else:
                    break
            while True:
                keystrokes_rpc_responses = find_game_keystrokes_in_log(new_game_txid)[1::2]
                if len(keystrokes_rpc_responses) < 1:
                    print("No keystrokes broadcasted yet. Let's wait 5 seconds")
                    time.sleep(5)
                else:
                    break
            for keystroke in keystrokes_rpc_responses:
                json_keystroke = json.loads(keystroke)["result"]
                if "status" in json_keystroke.keys() and json_keystroke["status"] == "error":
                    while True:
                        print("Trying to re-brodcast keystroke")
                        keystroke_rebroadcast = rogue_keystrokes(rpc_connection, json_keystroke["gametxid"],
                                                                 json_keystroke["keystrokes"])
                        if "txid" in keystroke_rebroadcast.keys():
                            print("Keystroke broadcasted! txid: " + keystroke_rebroadcast["txid"])
                            break
                        else:
                            print("Let's try again in 5 seconds")
                            time.sleep(5)
            last_keystroke_json = json.loads(keystrokes_rpc_responses[-1])
            while True:
                while True:
                    try:
                        confirmations_amount = rpc_connection.getrawtransaction(last_keystroke_json["result"]["txid"], 1)["confirmations"]
                        break
                    except Exception as e:
                        print(e)
                        print("Let's wait a little bit more")
                        rpc_connection.sendrawtransaction(last_keystroke_json["result"]["hex"])
                        time.sleep(5)
                        pass
                if confirmations_amount < 2:
                    print("Last keystroke not confirmed yet! Let's wait a little")
                    time.sleep(10)
                else:
                    print("Last keystroke confirmed!")
                    break
                while True:
                    print("\nExtraction info:\n")
                    extraction_info = rogue_extract(rpc_connection, new_game_txid, rpc_connection.getinfo()["pubkey"])
                    if extraction_info["status"] == "error":
                        print(colorize("Your warrior died or no any information about game was saved on blockchain", "red"))
                        print("If warrior was alive - try to wait a little (choose n to wait for a next block). If he is dead - you can bailout now (choose y).")
                    else:
                        print("Current game state:")
                        print("Game txid: " + extraction_info["gametxid"])
                        print("Information about game saved on chain: " + extraction_info["extracted"])
                    print("\n")
                    is_bailout_needed = input(
                        "Do you want to make bailout now [y] or wait for one more block [n]? [y/n]: ")
                    if is_bailout_needed == "y":
                        if game_info["alive"] > 1:
                            bailout_info = rogue_bailout(rpc_connection, new_game_txid)
                            try:
                                bailout_txid = bailout_info["txid"]
                                print(bailout_info)
                                print("\nGame is finished!\n")
                                input("Press [Enter] to continue...")
                                break
                            except Exception:
                                highlander_info = rogue_highlander(rpc_connection, new_game_txid)
                                highlander_info = highlander_info["txid"]
                                print(highlander_info)
                                print("\nGame is finished!\n")
                                input("Press [Enter] to continue...")
                                break
                        else:
                            highlander_info = rogue_highlander(rpc_connection, new_game_txid)
                            if 'error' in highlander_info.keys() and highlander_info["error"] == 'numplayers != maxplayers':
                                bailout_info = rogue_bailout(rpc_connection, new_game_txid)
                                print(bailout_info)
                                print("\nGame is finished!\n")
                                input("Press [Enter] to continue...")
                                break
                            else:
                                print(highlander_info)
                                print("\nGame is finished!\n")
                                input("Press [Enter] to continue...")
                                break
                    elif is_bailout_needed == "n":
                        game_end_height = int(rpc_connection.getinfo()["blocks"])
                        while True:
                            current_height = int(rpc_connection.getinfo()["blocks"])
                            height_difference = current_height - game_end_height
                            if height_difference == 0:
                                print(current_height)
                                print(game_end_height)
                                print(colorize("Waiting for next block before bailout", "blue"))
                                time.sleep(5)
                            else:
                                break
                break
            break
        if start_game == "n":
            print("As you wish!")
            input("Press [Enter] to continue...")
            break
        else:
            print(colorize("Choose y or n!", "red"))


def rogue_newgame_multiplayer(rpc_connection):
    while True:
        max_players = input("Input game max. players (>1): ")
        if int(max_players) > 1:
            break
        else:
            print("Please re-check your input")
            input("Press [Enter] to continue...")
    while True:
        buyin = input("Input game buyin (>0.001): ")
        if float(buyin) > 0.001:
            break
        else:
            print("Please re-check your input")
            input("Press [Enter] to continue...")
    try:
        new_game_txid = rpc_connection.cclib("newgame", "17", '"[' + max_players + "," + buyin + ']"')["txid"]
        print(colorize("New multiplayer game succesfully created. txid: " + new_game_txid, "green"))
        input("Press [Enter] to continue...")
    except Exception as e:
        print("Something went wrong.")
        print(e)
        input("Press [Enter] to continue...")


def rogue_join_multiplayer_game(rpc_connection):
    while True:
        try:
            print_multiplayer_games_list(rpc_connection)
            # TODO: optional player data txid (print players you have and ask if you want to choose one)
            game_txid = input("Input txid of game you want to join: ")
            try:
                while True:
                    print_players_list(rpc_connection)
                    is_choice_needed = input("Do you want to choose a player for this game? [y/n] ")
                    if is_choice_needed == "y":
                        player_txid = input("Please input player txid: ")
                        newgame_regisration_txid = rogue_game_register(rpc_connection, game_txid, player_txid)["txid"]
                        break
                    elif is_choice_needed == "n":
                        set_warriors_name(rpc_connection)
                        newgame_regisration_txid = rogue_game_register(rpc_connection, game_txid)["txid"]
                        break
                    else:
                        print("Please choose y or n !")
            except Exception as e:
                print("Something went wrong. Maybe you're trying to register on game twice or don't have enough funds to pay buyin.")
                print(e)
                input("Press [Enter] to continue...")
                break
            print(colorize("Succesfully registered.", "green"))
            while True:
                mempool = rpc_connection.getrawmempool()
                if newgame_regisration_txid in mempool:
                    print(colorize("Waiting for registration transaction to be mined", "blue"))
                    time.sleep(5)
                else:
                    print(colorize("Registration transaction is mined", "green"))
                    break
            print(newgame_regisration_txid)
            input("Press [Enter] to continue...")
            break
        except KeyboardInterrupt:
            break


def print_players_list(rpc_connection):
    players_list = rogue_players_list(rpc_connection)
    print(colorize("\nYou own " + str(players_list["numplayerdata"]) + " warriors\n", "blue"))
    warrior_counter = 0
    for player in players_list["playerdata"]:
        warrior_counter = warrior_counter + 1
        player_data = rogue_player_info(rpc_connection, player)["player"]
        print(colorize("\n================================\n","green"))
        print("Warrior " + str(warrior_counter))
        print("Name: " + player_data["pname"] + "\n")
        print("Player txid: " + player_data["playertxid"])
        print("Token txid: " + player_data["tokenid"])
        print("Hitpoints: " + str(player_data["hitpoints"]))
        print("Strength: " + str(player_data["strength"]))
        print("Level: " + str(player_data["level"]))
        print("Experience: " + str(player_data["experience"]))
        print("Dungeon Level: " + str(player_data["dungeonlevel"]))
        print("Chain: " + player_data["chain"])
        print(colorize("\nInventory:\n","blue"))
        for item in player_data["pack"]:
            print(item)
        print("\nTotal packsize: " + str(player_data["packsize"]) + "\n")
    input("Press [Enter] to continue...")


def sell_warrior(rpc_connection):
    print(colorize("Your brave warriors: \n", "blue"))
    print_players_list(rpc_connection)
    print("\n")
    while True:
        need_sell = input("Do you want to place order to sell any? [y/n]: ")
        if need_sell == "y":
            playertxid = input("Input playertxid of warrior you want to sell: ")
            price = input("Input price (in ROGUE coins) you want to sell warrior for: ")
            try:
                tokenid = rogue_player_info(rpc_connection, playertxid)["player"]["tokenid"]
            except Exception as e:
                print(e)
                print("Something went wrong. Be careful with input next time.")
                input("Press [Enter] to continue...")
                break
            token_ask_raw = rpc_connection.tokenask("1", tokenid, price)
            try:
                token_ask_txid = rpc_connection.sendrawtransaction(token_ask_raw["hex"])
            except Exception as e:
                print(e)
                print(token_ask_raw)
                print("Something went wrong. Be careful with input next time.")
                input("Press [Enter] to continue...")
                break
            print(colorize("Ask succesfully placed. Ask txid is: " + token_ask_txid, "green"))
            input("Press [Enter] to continue...")
            break
        if need_sell == "n":
            print("As you wish!")
            input("Press [Enter] to continue...")
            break
        else:
            print(colorize("Choose y or n!", "red"))


#TODO: have to combine into single scanner with different cases
def is_warrior_alive(rpc_connection, warrior_txid):
    warrior_alive = False
    raw_transaction = rpc_connection.getrawtransaction(warrior_txid, 1)
    for vout in raw_transaction["vout"]:
        if vout["value"] == 0.00000001 and rpc_connection.gettxout(raw_transaction["txid"], vout["n"]):
            warrior_alive = True
    return warrior_alive


def warriors_scanner(rpc_connection):
    start_time = time.time()
    token_list = rpc_connection.tokenlist()
    my_warriors_list = rogue_players_list(rpc_connection)
    warriors_list = {}
    for token in token_list:
        player_info = rogue_player_info(rpc_connection, token)
        if "status" in player_info and player_info["status"] == "error":
            pass
        elif player_info["player"]["playertxid"] in my_warriors_list["playerdata"]:
            pass
        elif not is_warrior_alive(rpc_connection, player_info["player"]["playertxid"]):
            pass
        else:
            warriors_list[token] = player_info["player"]
    print("--- %s seconds ---" % (time.time() - start_time))
    return warriors_list


def warriors_scanner_for_rating(rpc_connection):
    print("It can take some time")
    token_list = rpc_connection.tokenlist()
    my_warriors_list = rogue_players_list(rpc_connection)
    actual_playerids = []
    warriors_list = {}
    for token in token_list:
        player_info = rogue_player_info(rpc_connection, token)
        if "status" in player_info and player_info["status"] == "error":
            pass
        else:
            while True:
                if "batontxid" in player_info["player"].keys():
                    player_info = rogue_player_info(rpc_connection, player_info["player"]["batontxid"])
                else:
                    actual_playerids.append(player_info["player"]["playertxid"])
                    break
    for player_id in actual_playerids:
        player_info = rogue_player_info(rpc_connection, player_id)
        if not is_warrior_alive(rpc_connection, player_info["player"]["playertxid"]):
            pass
        else:
            warriors_list[player_id] = player_info["player"]
    return warriors_list


def warriors_scanner_for_dex(rpc_connection):
    start_time = time.time()
    token_list = rpc_connection.tokenlist()
    my_warriors_list = rogue_players_list(rpc_connection)
    warriors_list = {}
    for token in token_list:
        player_info = rogue_player_info(rpc_connection, token)
        if "status" in player_info and player_info["status"] == "error":
            pass
        elif player_info["player"]["tokenid"] in my_warriors_list["playerdata"]:
            pass
        else:
            warriors_list[token] = player_info["player"]
    print("--- %s seconds ---" % (time.time() - start_time))
    return warriors_list


def print_warrior_list(rpc_connection):
    players_list = warriors_scanner(rpc_connection)
    print(colorize("All warriors on ROGUE chain: \n", "blue"))
    warrior_counter = 0
    for player in players_list:
        warrior_counter = warrior_counter + 1
        player_data = rogue_player_info(rpc_connection, player)["player"]
        print(colorize("\n================================\n","green"))
        print("Warrior " + str(warrior_counter))
        print("Name: " + player_data["pname"] + "\n")
        print("Player txid: " + player_data["playertxid"])
        print("Token txid: " + player_data["tokenid"])
        print("Hitpoints: " + str(player_data["hitpoints"]))
        print("Strength: " + str(player_data["strength"]))
        print("Level: " + str(player_data["level"]))
        print("Experience: " + str(player_data["experience"]))
        print("Dungeon Level: " + str(player_data["dungeonlevel"]))
        print("Chain: " + player_data["chain"])
        print(colorize("\nInventory:\n","blue"))
        for item in player_data["pack"]:
            print(item)
        print("\nTotal packsize: " + str(player_data["packsize"]) + "\n")
    input("Press [Enter] to continue...")


def place_bid_on_warriror(rpc_connection):
    warriors_list = print_warrior_list(rpc_connection)
    # TODO: have to drop my warriors or at least print my warriors ids
    while True:
        need_buy = input("Do you want to place order to buy some warrior? [y/n]: ")
        if need_buy == "y":
            playertxid = input("Input playertxid of warrior you want to place bid for: ")
            price = input("Input price (in ROGUE coins) you want to buy warrior for: ")
            tokenid = rogue_player_info(rpc_connection, playertxid)["player"]["tokenid"]
            token_bid_raw = rpc_connection.tokenbid("1", tokenid, price)
            try:
                token_bid_txid = rpc_connection.sendrawtransaction(token_bid_raw["hex"])
            except Exception as e:
                print(e)
                print(token_bid_raw)
                print("Something went wrong. Be careful with input next time.")
                input("Press [Enter] to continue...")
                break
            print(colorize("Bid succesfully placed. Bid txid is: " + token_bid_txid, "green"))
            input("Press [Enter] to continue...")
            break
        if need_buy == "n":
            print("As you wish!")
            input("Press [Enter] to continue...")
            break
        else:
            print(colorize("Choose y or n!", "red"))


def check_incoming_bids(rpc_connection):
    # TODO: have to scan for warriors which are in asks as well
    players_list = rogue_players_list(rpc_connection)
    incoming_orders = []
    for player in players_list["playerdata"]:
        token_id = rogue_player_info(rpc_connection, player)["player"]["tokenid"]
        orders = rpc_connection.tokenorders(token_id)
        if len(orders) > 0:
            for order in orders:
                if order["funcid"] == "b":
                    incoming_orders.append(order)
    return incoming_orders


def print_icoming_bids(rpc_connection):
    incoming_bids = check_incoming_bids(rpc_connection)
    for bid in incoming_bids:
        print("Recieved bid for warrior " + bid["tokenid"])
        player_data = rogue_player_info(rpc_connection, bid["tokenid"])["player"]
        print(colorize("\n================================\n", "green"))
        print("Name: " + player_data["pname"] + "\n")
        print("Player txid: " + player_data["playertxid"])
        print("Token txid: " + player_data["tokenid"])
        print("Hitpoints: " + str(player_data["hitpoints"]))
        print("Strength: " + str(player_data["strength"]))
        print("Level: " + str(player_data["level"]))
        print("Experience: " + str(player_data["experience"]))
        print("Dungeon Level: " + str(player_data["dungeonlevel"]))
        print("Chain: " + player_data["chain"])
        print(colorize("\nInventory:\n", "blue"))
        for item in player_data["pack"]:
            print(item)
        print("\nTotal packsize: " + str(player_data["packsize"]) + "\n")
        print(colorize("\n================================\n", "blue"))
        print("Order info: \n")
        print("Bid txid: " + bid["txid"])
        print("Price: " + str(bid["price"]) + "\n")
    if len(incoming_bids) == 0:
        print(colorize("There is no any incoming orders!", "blue"))
        input("Press [Enter] to continue...")
    else:
        while True:
            want_to_sell = input("Do you want to fill any incoming bid? [y/n]: ")
            if want_to_sell == "y":
                bid_txid = input("Input bid txid you want to fill: ")
                for bid in incoming_bids:
                    if bid_txid == bid["txid"]:
                        tokenid = bid["tokenid"]
                        fill_sum = bid["totalrequired"]
                fillbid_hex = rpc_connection.tokenfillbid(tokenid, bid_txid, str(fill_sum))
                try:
                    fillbid_txid = rpc_connection.sendrawtransaction(fillbid_hex["hex"])
                except Exception as e:
                    print(e)
                    print(fillbid_hex)
                    print("Something went wrong. Be careful with input next time.")
                    input("Press [Enter] to continue...")
                    break
                print(colorize("Warrior succesfully sold. Txid is: " + fillbid_txid, "green"))
                input("Press [Enter] to continue...")
                break
            if want_to_sell == "n":
                print("As you wish!")
                input("Press [Enter] to continue...")
                break
            else:
                print(colorize("Choose y or n!", "red"))


def find_warriors_asks(rpc_connection):
    warriors_list = warriors_scanner_for_dex(rpc_connection)
    warriors_asks = []
    for player in warriors_list:
        orders = rpc_connection.tokenorders(player)
        if len(orders) > 0:
            for order in orders:
                if order["funcid"] == "s":
                    warriors_asks.append(order)
    for ask in warriors_asks:
        print(colorize("\n================================\n", "green"))
        print("Warrior selling on marketplace: " + ask["tokenid"])
        player_data = rogue_player_info(rpc_connection, ask["tokenid"])["player"]
        print("Name: " + player_data["pname"] + "\n")
        print("Player txid: " + player_data["playertxid"])
        print("Token txid: " + player_data["tokenid"])
        print("Hitpoints: " + str(player_data["hitpoints"]))
        print("Strength: " + str(player_data["strength"]))
        print("Level: " + str(player_data["level"]))
        print("Experience: " + str(player_data["experience"]))
        print("Dungeon Level: " + str(player_data["dungeonlevel"]))
        print("Chain: " + player_data["chain"])
        print(colorize("\nInventory:\n", "blue"))
        for item in player_data["pack"]:
            print(item)
        print("\nTotal packsize: " + str(player_data["packsize"]) + "\n")
        print(colorize("Order info: \n", "red"))
        print("Ask txid: " + ask["txid"])
        print("Price: " + str(ask["price"]) + "\n")
    while True:
        want_to_buy = input("Do you want to buy any warrior? [y/n]: ")
        if want_to_buy == "y":
            ask_txid = input("Input asktxid which you want to fill: ")
            for ask in warriors_asks:
                if ask_txid == ask["txid"]:
                    tokenid = ask["tokenid"]
            try:
                fillask_raw = rpc_connection.tokenfillask(tokenid, ask_txid, "1")
            except Exception as e:
                print("Something went wrong. Be careful with input next time.")
                input("Press [Enter] to continue...")
                break
            try:
                fillask_txid = rpc_connection.sendrawtransaction(fillask_raw["hex"])
            except Exception as e:
                print(e)
                print(fillask_raw)
                print("Something went wrong. Be careful with input next time.")
                input("Press [Enter] to continue...")
                break
            print(colorize("Warrior succesfully bought. Txid is: " + fillask_txid, "green"))
            input("Press [Enter] to continue...")
            break
        if want_to_buy == "n":
            print("As you wish!")
            input("Press [Enter] to continue...")
            break
        else:
            print(colorize("Choose y or n!", "red"))


def warriors_orders_check(rpc_connection):
    my_orders_list = rpc_connection.mytokenorders("17")
    warriors_orders = {}
    for order in my_orders_list:
        player_info = rogue_player_info(rpc_connection, order["tokenid"])
        if "status" in player_info and player_info["status"] == "error":
            pass
        else:
            warriors_orders[order["tokenid"]] = order
    bids_list = []
    asks_list = []
    for order in warriors_orders:
        if warriors_orders[order]["funcid"] == "s":
            asks_list.append(warriors_orders[order])
        else:
            bids_list.append(order)
    print(colorize("\nYour asks:\n", "blue"))
    print(colorize("\n********************************\n", "red"))
    for ask in asks_list:
        print("txid: " + ask["txid"])
        print("Price: " + ask["price"])
        print("Warrior tokenid: " + ask["tokenid"])
        print(colorize("\n================================\n", "green"))
        print("Warrior selling on marketplace: " + ask["tokenid"])
        player_data = rogue_player_info(rpc_connection, ask["tokenid"])["player"]
        print("Name: " + player_data["pname"] + "\n")
        print("Player txid: " + player_data["playertxid"])
        print("Token txid: " + player_data["tokenid"])
        print("Hitpoints: " + str(player_data["hitpoints"]))
        print("Strength: " + str(player_data["strength"]))
        print("Level: " + str(player_data["level"]))
        print("Experience: " + str(player_data["experience"]))
        print("Dungeon Level: " + str(player_data["dungeonlevel"]))
        print("Chain: " + player_data["chain"])
        print(colorize("\nInventory:\n", "blue"))
        for item in player_data["pack"]:
            print(item)
        print("\nTotal packsize: " + str(player_data["packsize"]) + "\n")
        print(colorize("\n================================\n", "green"))
    print(colorize("\nYour bids:\n", "blue"))
    print(colorize("\n********************************\n", "red"))
    for bid in bids_list:
        print("txid: " + bid["txid"])
        print("Price: " + bid["price"])
        print("Warrior tokenid: " + bid["tokenid"])
        print(colorize("\n================================\n", "green"))
        print("Warrior selling on marketplace: " + bid["tokenid"])
        player_data = rogue_player_info(rpc_connection, bid["tokenid"])["player"]
        print("Name: " + player_data["pname"] + "\n")
        print("Player txid: " + player_data["playertxid"])
        print("Token txid: " + player_data["tokenid"])
        print("Hitpoints: " + str(player_data["hitpoints"]))
        print("Strength: " + str(player_data["strength"]))
        print("Level: " + str(player_data["level"]))
        print("Experience: " + str(player_data["experience"]))
        print("Dungeon Level: " + str(player_data["dungeonlevel"]))
        print("Chain: " + player_data["chain"])
        print(colorize("\nInventory:\n", "blue"))
        for item in player_data["pack"]:
            print(item)
        print("\nTotal packsize: " + str(player_data["packsize"]) + "\n")
        print(colorize("\n================================\n", "green"))
    while True:
        need_order_change = input("Do you want to cancel any of your orders? [y/n]: ")
        if need_order_change == "y":
            while True:
                ask_or_bid = input("Do you want cancel ask or bid? [a/b]: ")
                if ask_or_bid == "a":
                    ask_txid = input("Input txid of ask you want to cancel: ")
                    warrior_tokenid = input("Input warrior token id for this ask: ")
                    try:
                        ask_cancellation_hex = rpc_connection.tokencancelask(warrior_tokenid, ask_txid)
                        ask_cancellation_txid = rpc_connection.sendrawtransaction(ask_cancellation_hex["hex"])
                    except Exception as e:
                        print(colorize("Please re-check your input!", "red"))
                    print(colorize("Ask succefully cancelled. Cancellation txid: " + ask_cancellation_txid, "green"))
                    break
                if ask_or_bid == "b":
                    bid_txid = input("Input txid of bid you want to cancel: ")
                    warrior_tokenid = input("Input warrior token id for this bid: ")
                    try:
                        bid_cancellation_hex = rpc_connection.tokencancelbid(warrior_tokenid, bid_txid)
                        bid_cancellation_txid = rpc_connection.sendrawtransaction(bid_cancellation_hex["hex"])
                    except Exception as e:
                        print(colorize("Please re-check your input!", "red"))
                    print(colorize("Bid succefully cancelled. Cancellation txid: " + bid_cancellation_txid, "green"))
                    break
                else:
                    print(colorize("Choose a or b!", "red"))
            input("Press [Enter] to continue...")
            break
        if need_order_change == "n":
            print("As you wish!")
            input("Press [Enter] to continue...")
            break
        else:
            print(colorize("Choose y or n!", "red"))


def set_warriors_name(rpc_connection):
    warriors_name = input("What warrior name do you want for legends and tales about your brave adventures?: ")
    warrior_name_arg = '"' + "[%22" + warriors_name + "%22]" + '"'
    set_name_status = rpc_connection.cclib("setname", "17", warrior_name_arg)
    print(colorize("Warrior name succesfully set", "green"))
    print("Result: " + set_name_status["result"])
    print("Name: " + set_name_status["pname"])
    input("Press [Enter] to continue...")


def top_warriors_rating(rpc_connection):
    start_time = time.time()
    warriors_list = warriors_scanner_for_rating(rpc_connection)
    warriors_exp = {}
    for warrior in warriors_list:
        warriors_exp[warrior] = warriors_list[warrior]["experience"]
    warriors_exp_sorted = {}
    temp = [(k, warriors_exp[k]) for k in sorted(warriors_exp, key=warriors_exp.get, reverse=True)]
    for k,v in temp:
        warriors_exp_sorted[k] = v
    counter = 0
    for experienced_warrior in warriors_exp_sorted:
        if counter < 20:
            counter = counter + 1
            print("\n" + str(counter) + " place.")
            print(colorize("\n================================\n", "blue"))
            player_data = rogue_player_info(rpc_connection, experienced_warrior)["player"]
            print("Name: " + player_data["pname"] + "\n")
            print("Player txid: " + player_data["playertxid"])
            print("Token txid: " + player_data["tokenid"])
            print("Hitpoints: " + str(player_data["hitpoints"]))
            print("Strength: " + str(player_data["strength"]))
            print("Level: " + str(player_data["level"]))
            print("Experience: " + str(player_data["experience"]))
            print("Dungeon Level: " + str(player_data["dungeonlevel"]))
            print("Chain: " + player_data["chain"])
    print("--- %s seconds ---" % (time.time() - start_time))
    input("Press [Enter] to continue...")


def exit():
    sys.exit()

def exit_main():
    return 'back to Antara modules menu'


def warrior_trasnfer(rpc_connection):
    print(colorize("Your brave warriors: \n", "blue"))
    print_players_list(rpc_connection)
    print("\n")
    while True:
        need_transfer = input("Do you want to transfer any warrior? [y/n]: ")
        if need_transfer == "y":
            warrior_tokenid = input("Input warrior tokenid: ")
            recepient_pubkey = input("Input recepient pubkey: ")
            try:
                token_transfer_hex = rpc_connection.tokentransfer(warrior_tokenid, recepient_pubkey, "1")
                token_transfer_txid = rpc_connection.sendrawtransaction(token_transfer_hex["hex"])
            except Exception as e:
                print(e)
                print("Something went wrong. Please be careful with your input next time!")
                input("Press [Enter] to continue...")
                break
            print(colorize("Warrior succesfully transferred! Transfer txid: " + token_transfer_txid, "green"))
            input("Press [Enter] to continue...")
            break
        if need_transfer == "n":
            print("As you wish!")
            input("Press [Enter] to continue...")
            break
        else:
            print(colorize("Choose y or n!", "red"))


def check_if_config_is_here(rpc_connection, assetchain_name):
    config_name = assetchain_name + ".conf"
    if os.path.exists(config_name):
        print(colorize("Config is already in daemon folder", "green"))
    else:
        if operating_system == 'Darwin':
            path_to_config = os.environ['HOME'] + '/Library/Application Support/Komodo/' + assetchain_name + '/' + config_name
        elif operating_system == 'Linux':
            path_to_config = os.environ['HOME'] + '/.komodo/' + assetchain_name + '/' + config_name
        elif operating_system == 'Win64' or operating_system == 'Windows':
            path_to_config = '%s/komodo/' + assetchain_name + '/' + config_name % os.environ['APPDATA']
        try:
            copy(path_to_config, os.getcwd())
        except Exception as e:
            print(e)
            print("Can't copy config to current daemon directory automatically by some reason.")
            print("Please copy it manually. It's locating here: " + path_to_config)


def find_game_keystrokes_in_log(gametxid):

    operating_system = platform.system()
    if operating_system == 'Win64' or operating_system == 'Windows':
        p1 = subprocess.Popen(["type", "keystrokes.log"], stdout=subprocess.PIPE, shell=True)
        p2 = subprocess.Popen(["findstr", gametxid], stdin=p1.stdout, stdout=subprocess.PIPE, shell=True)
    else:
        p1 = subprocess.Popen(["cat", "keystrokes.log"], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", gametxid], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    keystrokes_log_for_game = bytes.decode(output).split("\n")
    return keystrokes_log_for_game


def check_if_tx_in_mempool(rpc_connection, txid):
    while True:
        mempool = rpc_connection.getrawmempool()
        if txid in mempool:
            print(colorize("Waiting for " + txid + " transaction to be mined", "blue"))
            time.sleep(5)
        else:
            print(colorize("Transaction is mined", "green"))
            break

def gateway_info_tui(rpc_connection, gw_index=''):
    if gw_index == '':
        while True:
            print(colorize("\nGateways created on this assetchain: \n", "blue"))
            gateways_list = rpc_connection.gatewayslist()
            if len(gateways_list) == 0:
                print("Seems like a no gateways created on this assetchain yet!\n")
                input("Press [Enter] to continue...")
                break
            else:
                i = 1
                for gateway in gateways_list:
                    print("["+str(i)+"] "+gateway)
                    i += 1
                print(colorize('_' * 65, "blue"))
                print("\n")
                gw_selected = input("Select Gateway Bind TXID: ")
                gw_index = int(gw_selected)-1
                try:
                    bind_txid = gateways_list[gw_index]
                    break
                except:
                    print("Invalid selection, must be number between 1 and "+str(len(gateways_list)))
                    pass
    else:
        while True:
            try:
                bind_txid = gateways_list[gw_index]
                break
            except:
                print("Invalid gateway index, select manually...")
                gateway_info_tui(rpc_connection)
                pass
    try:    
        info = rpc_connection.gatewaysinfo(bind_txid)
        print(colorize("Gateways Bind TXID         ["+str(bind_txid)+"]", 'green'))
        print(colorize("Gateways Oracle TXID       ["+str(info['oracletxid'])+"]", 'green'))
        print(colorize("Gateways Token TXID        ["+str(info['tokenid'])+"]", 'green'))
        print(colorize("Gateways Coin              ["+str(info['coin'])+"]", 'green'))
        print(colorize("Gateways Pubkeys           ["+str(info['pubkeys'])+"]", 'green'))
        print(colorize("Gateways Deposit Address   ["+str(info['deposit'])+"]", 'green'))
        print(colorize("Gateways Total Supply      ["+str(info['totalsupply'])+"]", 'green'))
        print(colorize("Gateways Remaining Supply  ["+str(info['remaining'])+"]", 'green'))
        print(colorize("Gateways Issued Supply     ["+str(info['issued'])+"]", 'green'))
        input("Press [Enter] to continue...")
        return gw_index
    except Exception as e:
        print(info)
        print(e)
        print("Something went wrong. Please check your input")
        input("Press [Enter] to continue...")

def gateways_deposit_claim_tokens(rpc_connection_assetchain, rpc_connection_komodo):
    selected_gateway = gateway_info_tui(rpc_connection_assetchain)
    gateways_list = rpc_connection_assetchain.gatewayslist()
    bind_txid = gateways_list[selected_gateway]
    gw_info = rpc_connection_assetchain.gatewaysinfo(bind_txid)
    gw_sendmany = gateways_send_kmd(rpc_connection_komodo, gw_info['deposit'])
    gw_sendmany_txid = gw_sendmany[0]
    gw_recipient_addr = gw_sendmany[1]
    gw_deposit_amount = gw_sendmany[2]
    deposit_info = gateways_deposit_tui(rpc_connection_assetchain, rpc_connection_komodo,
                        bind_txid, gw_info['coin'], gw_sendmany_txid, gw_deposit_amount,
                        gw_recipient_addr)
    deposit_txid = deposit_info[0]
    dest_pub = deposit_info[1]
    claim_txid = gateways_claim_tui(rpc_connection_assetchain, bind_txid, gw_info['coin'],
                 deposit_txid, dest_pub, gw_deposit_amount)
    tokenbalance = rpc_connection_assetchain.tokenbalance(gw_info['tokenid'])
    print("Gateway transfer complete!")
    print(colorize("Deposit TXID         ["+str(bind_txid)+"]", 'green'))
    print(colorize("Claim TXID           ["+str(bind_txid)+"]", 'green'))
    print(colorize("Token Balance        ["+str(bind_txid)+"]", 'green'))











def pegs_fund_tui(rpc_connection):
    while True:
        try:
            pegs_txid = input("Enter Pegs TXID: ")
            token_txid = select_tokenid(rpc_connection)
            tokenbalance = rpc_connection.tokenbalance(token_txid)['balance']/100000000
            amount = int(input("Set pegs funding amount ("+str(tokenbalance)+" available): "))
        except KeyboardInterrupt:
            break
        else:
            fund_hex = rpclib.pegs_fund(rpc_connection, pegs_txid, token_txid, amount)
            print(fund_hex)
        if fund_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "magenta"))
            print(fund_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                pegsfund_txid = rpclib.sendrawtransaction(rpc_connection,
                                                       fund_hex['hex'])
            except KeyError:
                print(pegsfund_txid)
                print("Error")
                input("Press [Enter] to continue...")
                break
            finally:
                print(colorize("Pegs Fund transaction broadcasted: " + pegsfund_txid, "green"))
                input("Press [Enter] to continue...")
                break


def pegs_get_tui(rpc_connection):
    while True:
        try:
            pegs_txid = input("Enter Pegs TXID: ")
            token_txid = select_tokenid(rpc_connection)
            info = rpc_connection.pegsaccountinfo(pegs_txid)
            if info['result'] == "success":
                if len(info['account info']) > 0:
                    for item in info['account info']:
                        print("Token: "+item['token'])
                        print("Deposit: "+str(item['deposit']))
                        print("Debt: "+str(item['debt']))
                        print("Ratio "+item['ratio'])
            else:
                print("Something went wrong.")
                print(info)
                input("Press [Enter] to continue...")
                break
            amount = input("Set pegs get amount: ")
        except KeyboardInterrupt:
            break
        else:
            pegsget_hex = rpclib.pegs_get(rpc_connection, pegs_txid, token_txid, amount)
        if pegsget_hex['result'] == "error":
            print(colorize("\nSomething went wrong!\n", "magenta"))
            print(pegsget_hex)
            print("\n")
            input("Press [Enter] to continue...")
            break
        else:
            try:
                pegsget_txid = rpclib.sendrawtransaction(rpc_connection,
                                                       pegsget_hex['hex'])
            except KeyError:
                print(pegsget_hex)
                print("Error")
                input("Press [Enter] to continue...")
                break
            finally:
                print(colorize("Pegs Get transaction broadcasted: " +pegsget_txid, "green"))
                input("Press [Enter] to continue...")
                break

# pegs_txid = 5ccdff0d29f2f47fb1e349c1ff9ae17977a58763abacf693cd27e98b38fad3f3
def pegsinfo_tui(rpc_connection):
    while True:
        try:
            pegs_txid = input("Enter Pegs TXID: ")
            info = rpc_connection.pegsinfo(pegs_txid)
            if info['result'] == "success":
                if len(info['info']) > 0:
                    for item in info['info']:
                        print("Token: "+item['token'])
                        print("Total deposit: "+str(item['total deposit']))
                        print("Total debt: "+str(item['total debt']))
                        print("Ratio : "+str(item['total ratio']))
                print("Global ratio: "+info['global ratio'])
            else:
                print("Something went wrong.")
                print(info)
                input("Press [Enter] to continue...")
                break
        except KeyError:
            print(info)
            print("Error")
            input("Press [Enter] to continue...")
            break
        finally:
            input("Press [Enter] to continue...")
            break

def pegs_accounthistory_tui(rpc_connection):
    while True:
        try:
            pegs_txid = input("Enter Pegs TXID: ")
            history = rpc_connection.pegsaccounthistory(pegs_txid)
            if history['result'] == "success":
                if len(history['account history']) > 0:
                    for item in history['account history']:
                        print("-----------------------")
                        print("Action: "+item['action'])
                        print("Amount: "+str(item['amount']))
                        print("Account TXID: "+item['accounttxid'])
                        print("Token: "+item['token'])
                        print("Deposit: "+str(item['deposit']))
                        print("Debt: "+str(item['debt']))
                    print("-----------------------")

#[{'action': 'fund', 'amount': 100000000, 'accounttxid': '1e9409af6e391f996de434a3f86d765df43251d61cc1e720fa9a6457078d0f61', 'token': 'KMD', 'deposit': 100000000, 'debt': 0}, {'action': 'get', 'amount': 50000000, 'accounttxid': '752ef21dfbe313f229a4a396554b3ee0630ea2b4cc3264bd1cbdbe22bbf190e8', 'token': 'KMD', 'deposit': 100000000, 'debt': 50000000}]}

        except KeyError:
            print(history)
            print("Key Error: "+str(KeyError))
            input("Press [Enter] to continue...")
            break
        finally:
            input("Press [Enter] to continue...")
            break


def pegs_accountinfo_tui(rpc_connection):
    while True:
        try:
            pegs_txid = input("Enter Pegs TXID: ")
            info = rpc_connection.pegsaccountinfo(pegs_txid)
            if info['result'] == "success":
                if len(info['account info']) > 0:
                    for item in info['account info']:
                        print("Token: "+item['token'])
                        print("Deposit: "+str(item['deposit']))
                        print("Debt: "+str(item['debt']))
                        print("Ratio "+item['ratio'])
            else:
                print("Something went wrong.")
                print(info)
                input("Press [Enter] to continue...")
                break
        except KeyError:
            print(info)
            print("Error")
            input("Press [Enter] to continue...")
            break
        finally:
            input("Press [Enter] to continue...")
            break

def pegs_addresses_tui(rpc_connection):
    while True:
        try:
            address = rpc_connection.pegsaddress()
            if address['result'] == "success":
                print("PegsCCAddress: "+address['PegsCCAddress'])
                print("PegsCCBalance: "+str(address['PegsCCBalance']))
                print("PegsNormalAddress: "+address['PegsNormalAddress'])
                print("PegsNormalBalance: "+address['PegsNormalBalance'])
                print("PegsCCTokensAddress: "+address['PegsCCTokensAddress'])
                print("myCCAddress(Pegs): "+address['myCCAddress(Pegs)'])
                print("myCCbalance(Pegs): "+str(address['myCCbalance(Pegs)']))
                print("myaddress: "+address['myaddress'])
                print("mybalance: "+str(address['mybalance']))
            else:
                print("Something went wrong.")
                print(address)
                input("Press [Enter] to continue...")
                break
        except KeyError:
            print(address)
            print("Error")
            input("Press [Enter] to continue...")
            break
        finally:
            input("Press [Enter] to continue...")
            break



def pegs_worstaccounts_tui(rpc_connection):
    while True:
        try:
            pegs_txid = input("Enter Pegs TXID: ")
            worst = rpc_connection.pegsworstaccounts(pegs_txid)
            if worst['result'] == "success":
                if 'KMD' in worst:
                    if len(worst['KMD']) > 0:
                        for item in worst['KMD']:
                            print("Account TXID: "+item['accounttxid'])
                            print("Deposit: "+str(item['deposit']))
                            print("Debt: "+str(item['debt']))
                            print("Ratio "+item['ratio'])
                else:
                    print("No accounts at risk of liquidation at the moment.")
                    info = rpc_connection.pegsinfo(pegs_txid)
                    if info['result'] == "success":
                        if len(info['info']) > 0:
                            for item in info['info']:
                                print("Token: "+item['token'])
                                print("Total deposit: "+str(item['total deposit']))
                                print("Total debt: "+str(item['total debt']))
                                print("Ratio : "+str(item['total ratio']))
                        print("Global ratio: "+info['global ratio'])
        except KeyError:
            print(worst)
            print("Key Error: "+str(KeyError))
            input("Press [Enter] to continue...")
            break
        finally:
            input("Press [Enter] to continue...")
            break


def pegs_create_tui():
    paramlist = ["-ac_supply=5000", "-ac_reward=800000000",
                 "-ac_sapling=1", "-addnode=localhost", "-ac_snapshot=1440",
                 "-ac_cc=2", "-ac_import=PEGSCC", "-debug=gatewayscc-2",
                 "-ac_end=1", "-ac_perc=0", "-ac_cbopret=7"
                ]
    while True:
        kmd_path = input("Input komodod path (e.g. /home/user/komodo/src): ")
        if not os.path.isfile(kmd_path+'/komodod'):
            print("komodod not found in "+kmd_path+"! Try again.")
        else:
            break
    # check if komodod exists in path
    coin = input("Enter name of Pegs chain to create: ")
    #check for bad chars
    external_coin = input("Enter ticker of external coin to Peg (e.g. KMD): ")
    #check for bad chars
    token_supply = input("How many tokens to create?: ")
    paramlist.append("-ac_name="+coin)
    # launch chains, get rpcs
    rpcs = spawn_chain_pair(coin, kmd_path, paramlist)
    primary_rpc = rpcs[0]
    secondary_rpc = rpcs[1]
    secondary_rpc.setgenerate(True, 1)
    # get address, wif and pubkeys
    primary_addr = primary_rpc.getnewaddress()
    primary_wif = primary_rpc.dumpprivkey(primary_addr)
    primary_pubkey = primary_rpc.validateaddress(primary_addr)['pubkey']
    primary_rpc.setpubkey(primary_pubkey)
    # selfsend to avoid coinbase errors
    balance = primary_rpc.getbalance()
    selfsend_txid = primary_rpc.sendtoaddress(primary_addr, int(balance)/2)
    check_if_tx_in_mempool(primary_rpc, selfsend_txid)
    token_txid = token_create_tui(primary_rpc, external_coin, token_supply, external_coin+"_tether")
    oracle_txid = oracle_create_tui(primary_rpc, external_coin, external_coin+"_tether", 'IhhL')
    oracle_register_tui(primary_rpc, oracle_txid, '0.001')
    oracle_subscription_utxogen(primary_rpc, oracle_txid, primary_pubkey, '50', 10)
    tokensupply = str(primary_rpc.tokeninfo(token_txid)['supply'])
    bind_txid = gateways_bind_tui(primary_rpc, token_txid, tokensupply, oracle_txid, external_coin)
    oraclefeed_launch_str = spawn_oraclefeed(coin, kmd_path, oracle_txid, primary_pubkey, bind_txid)
    # Create the Peg
    pegs_funding = input("Enter amount of Pegs funding (e.g. 100): ")
    num_binds = 1
    resp = primary_rpc.pegscreate(str(pegs_funding), str(num_binds), bind_txid)
    print(resp)
    if 'hex' in resp:
        pegs_txid = primary_rpc.sendrawtransaction(resp['hex'])
        check_if_tx_in_mempool(primary_rpc, pegs_txid)
        print(colorize("Pegs TXID                ["+str(pegs_txid)+"]", 'green'))
        paramlist.append("-earlytxid="+pegs_txid)
        print(colorize("The Pegs Contract has been created successfully!", 'green'))
        info = primary_rpc.gatewaysinfo(bind_txid)
        with open(cwd+"/"+coin+"_pegsinfo.json", "w+") as file:
            file.write('{\n"Pegs_Launch_Parameters":"'+" ".join(paramlist)+'",\n')
            file.write('"Oraclefeed_Launch_Parameters":"'+oraclefeed_launch_str+'",\n')
            file.write('"Pegs_Creation_TXID":"'+str(pegs_txid)+'",\n')
            file.write('"Gateways_Bind_TXID":"'+str(bind_txid)+'",\n')
            file.write('"Oracle_TXID":"'+str(info['oracle_txid'])+'",\n')
            file.write('"Token_TXID":"'+str(info['tokenid'])+'",\n')
            file.write('"Coin":"'+str(info['coin'])+'",\n')
            file.write('"Pubkeys":"'+str(info['pubkeys'])+'",\n')
            file.write('"Gateways_Deposit_Address":"'+str(info['deposit'])+'"\n}')

        print("Pegs Launch Parameters: "+' '.join(paramlist))
        print("Pegs Creation TXID         ["+str(bind_txid)+"]")
        print("Gateways Bind TXID         ["+str(bind_txid)+"]")
        print("Oracle TXID                ["+str(info['oracle_txid'])+"]")
        print("Token TXID                 ["+str(info['tokenid'])+"]")
        print("Coin                       ["+str(info['coin'])+"]")
        print("Pubkeys                    ["+str(info['pubkeys'])+"]")
        print("Gateways Deposit Address   ["+str(info['deposit'])+"]")
            
        print(colorize("Details have been written to "+coin+"_pegsinfo.json", 'blue'))
        input("Press [Enter] to continue...")
        return pegs_txid
    else:
        print(colorize("Pegs TXID failed!        ["+str(result)+"]", 'red'))
        input("Press [Enter] to continue...")
        return 'back to menu'
    
def spawn_oraclefeed(dest_chain, kmd_path, oracle_txid, pubkey, bind_txid):
    oraclefeed_build_log = str(dest_chain)+"_oraclefeed_build.log"
    oraclefeed_build = open(oraclefeed_build_log,'w+')
    print("Building oraclefeed ")
    subprocess.Popen(["gcc", kmd_path+"/cc/dapps/oraclefeed.c", "-lm", "-o", kmd_path+"/oraclefeed"], stdout=oraclefeed_build, stderr=oraclefeed_build, universal_newlines=True)
    oraclefeed_log = str(dest_chain)+"_oraclefeed.log"
    oraclefeed_output = open(oraclefeed_log,'w+')
    print("running oraclefeed ")
    subprocess.Popen([kmd_path+"/oraclefeed", dest_chain, oracle_txid, pubkey, "IhhL", bind_txid, kmd_path+"/komodo-cli"], stdout=oraclefeed_output, stderr=oraclefeed_output, universal_newlines=True)
    print(" Use tail -f "+kmd_path+"/"+oraclefeed_log+" for oraclefeed log console messages")
    print(colorize("IMPORTANT: The oraclefeed must be running at all times for the Pegs contract to work!", "red"))
    oraclefeed_launch_str = str(kmd_path+"/oraclefeed "+dest_chain+" "+oracle_txid+" "+pubkey+" IhhL "+bind_txid+" "+kmd_path+"/komodo-cli")
    print(colorize("Launch it with "+oraclefeed_launch_str, "blue"))
    input("Press [Enter] to continue...")
    return oraclefeed_launch_str

def oraclefeed_tui(jsonfile=''):
    if jsonfile == '':
        choice = input("select json file from list? (y/n)")
        if choice == 'y' or choice == 'Y':
            jsonfile = select_file(cwd, 'json')
    if jsonfile == '':
        while True:
            try:
                dest_chain = input('Enter name of Pegs chain')
                rpc = rpclib.def_credentials(dest_chain)
            except:
                print(colorize(dest_chain+" conf file does not exist! Try again.", "red"))
                break
        while True:
            kmd_path = input("Input komodod path (e.g. /home/user/komodo/src): ")
            if not os.path.isfile(kmd_path+'/komodod'):
                print("komodod not found in "+kmd_path+"! Try again.")
            else:
                break
        oracle_txid = select_oracle_txid(rpc)
        pubkey = rpc.getinfo()['pubkey']
        bind_txid = select_gateway(rpc)
    else:
        try:
            with open(jsonfile, 'r') as f:
                oraclefeed_json = json.loads(f.read())
            oraclefeed_params = oraclefeed_json['Oraclefeed_Launch_Parameters'].split(" ")
            kmd_path = oraclefeed_params[0].replace("oraclefeed","")
            dest_chain = oraclefeed_params[1]
            oracle_txid = oraclefeed_params[2]
            pubkey = oraclefeed_params[3]
            bind_txid = oraclefeed_params[5]
        except Exception as e:
            print("Something wrong with json file.")
            print(e)
    spawn_oraclefeed(dest_chain, kmd_path, oracle_txid, pubkey, bind_txid)

def get_commit_hash(repo_path):
    os.chdir(repo_path)
    proc = subprocess.run(['git', 'log', '-n', '1'], check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = proc.stdout
    return output.split()[1]

def launch_chain(coin, kmd_path, params, pubkey=''):
    if pubkey != '':
        params.append("-pubkey="+pubkey)
    print(params)
    commit = get_commit_hash(kmd_path)
    test_log = coin+"_"+commit+".log"
    test_output = open(test_log,'w+')
    print("Launching "+coin+" daemon")
    print(colorize("Launch Params: ["+str(' '.join([kmd_path+"/komodod"]+params))+"]", "green"))
    subprocess.Popen([kmd_path+"/komodod"]+params, stdout=test_output, stderr=test_output, universal_newlines=True)
    print(" Use `tail -f "+kmd_path+"/"+test_log+"` for "+coin+" console messages")
    loop = 0
    started = 0
    print("Waiting for "+coin+" to start...")
    while started == 0:
        time.sleep(30)
        print("Waiting for "+coin+" to start...")
        loop += 1
        try:
            pegs_rpc = rpclib.def_credentials(coin)
            coin_info = pegs_rpc.getinfo()
            print(coin_info)
            started = 1
            break
        except:
            print("Waiting for "+coin+" to start...")
            pass
        if started == 1:
            break
        if loop > 10:
            print("Something went wrong. Check "+test_log)
            break

def spawn_chain_pair(coin, kmd_path, paramlist):
    secondary_params = paramlist[:]
    launch_chain(coin, kmd_path, paramlist)
    primary_conf = home+'/.komodo/'+coin+"/"+coin+".conf"
    conf_lines = []
    with open(primary_conf, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
                conf_lines.append(l+'_secondary')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
                conf_lines.append(l+'_secondary')
            elif re.search('rpcport', l):
                rpcport = int(l.replace('rpcport=', ''))
                conf_lines.append('rpcport='+str(rpcport+7))
            else:
                conf_lines.append(l)
        primary_rpc=Proxy("http://%s:%s@127.0.0.1:%d"%(rpcuser, rpcpassword, int(rpcport)))
    f.close()
    secondary_datadir = home+'/.komodo2/'+coin
    if not os.path.exists(home+'/.komodo2'):
        os.mkdir(home+'/.komodo2')
    if not os.path.exists(secondary_datadir):
        os.mkdir(secondary_datadir)
    secondary_conf = home+'/.komodo2/'+coin+"/"+coin+".conf"
    rpcport2 = rpcport+7
    p2pport2 = rpcport+6
    conf_lines.append("port="+str(p2pport2))
    with open(secondary_conf, 'w+') as f2:
        for line in conf_lines:
            f2.write(line+"\r\n")
    f2.close() 
    secondary_rpc=Proxy("http://%s:%s@127.0.0.1:%d"%(rpcuser+'_secondary', rpcpassword+'_secondary', int(rpcport2)))
    # read primary conf file, update rpcuser/pass and port
    secondary_params.append('-datadir='+secondary_datadir)
    secondary_params.append('-addnode=localhost')
    launch_chain(coin, kmd_path, secondary_params)
    # create addresses, set pubkeys, start mining.
    primary_rpc.setgenerate(True, 1)
    height = primary_rpc.getblockcount()
    while height < 3:
        height = primary_rpc.getblockcount()
        print("Premining first 3 blocks... ("+str(height)+"/3)")
        time.sleep(20)
    balance = primary_rpc.getbalance()
    balance2 = secondary_rpc.getbalance()
    print("Premine complete!")
    print("Primary balance: "+str(balance))
    print("Secondary balance: "+str(balance2))
    return primary_rpc, secondary_rpc

# Payments Module

def payments_info(rpc_connection):
    payments_txid = select_payments(rpc_connection)
    if payments_txid != 'back to menu':
        info = rpc_connection.paymentsinfo('[\"{}\"]'.format(payments_txid))
        print(info)
        input("Press [Enter] to continue...")

def payments_create(rpc_connection, locked_blocks='', min_release='', opret_list=[]):
    if locked_blocks == '':
        locked_blocks = int(input("How many blocks to lock before release possible?"))
    if min_release == '':
        min_release = int(input("Minimum release amount?"))
    # Get txidopret list
    if len(opret_list) == 0:
        num_recipients = int(input("How many recipients?"))
        for i in range(num_recipients):
            opret_txid = payments_txidopret(rpc_connection)
            opret_list.append(opret_txid)
    opret_params = str(opret_list).strip('[]')
    params = "[{},{},{}]".format(locked_blocks, min_release, opret_params)
    raw_hex = rpc_connection.paymentscreate(str(params))
    try:
        txid = rpc_connection.sendrawtransaction(raw_hex['hex'])
        print(colorize("Payments Create Txid: "+txid, 'green'))
        print(colorize("Confirming transaction\n", "blue"))
        check_if_tx_in_mempool(rpc_connection, txid)
        input("Press [Enter] to continue...")
        return txid
    except Exception as e:
        print("Something went wrong!")
        print(e)
        print(raw_hex)
        input("Press [Enter] to continue...")

def payments_fund(rpc_connection, createtxid='', amount='', useopret=0):
    if createtxid == '':
        createtxid = select_payments(rpc_connection)
    if amount == '':
        amount = float(input("Amount of funds to send: "))
    if useopret == 1:
        params = "[\"{}\",{},{}]".format(createtxid, amount, useopret)
    else:
        params = "[\"{}\",{}]".format(createtxid, amount)
    raw_hex = rpc_connection.paymentsfund(str(params))
    try:
        txid = rpc_connection.sendrawtransaction(raw_hex['hex'])
        print(colorize("Payments Fund Txid: "+txid, 'green'))
        print(colorize("Confirming transaction\n", "blue"))
        check_if_tx_in_mempool(rpc_connection, txid)
        input("Press [Enter] to continue...")
        return txid
    except Exception as e:
        print("Something went wrong!")
        print(e)
        print(raw_hex)
        input("Press [Enter] to continue...")

def payments_merge(rpc_connection, createtxid=''):
    if createtxid == '':
        createtxid = select_payments(rpc_connection)
    params = "[\"{}\"]".format(createtxid)
    raw_hex = rpc_connection.paymentsmerge(str(params))
    try:
        txid = rpc_connection.sendrawtransaction(raw_hex['hex'])
        print(colorize("Payments Merge Txid: "+txid, 'green'))
        print(colorize("Confirming transaction\n", "blue"))
        check_if_tx_in_mempool(rpc_connection, txid)
        input("Press [Enter] to continue...")
        return txid
    except Exception as e:
        print("Something went wrong!")
        print(e)
        print(raw_hex)
        input("Press [Enter] to continue...")


def payments_release(rpc_connection, createtxid='', amount='', skip_min=0):
    if createtxid == '':
        createtxid = select_payments(rpc_connection)
    if amount == '':
        amount = float(input("Amount of funds to release: "))
    if skip_min == 1:
        params = "[\"{}\",{},{}]".format(createtxid, amount, skip_min)
    else:
        params = "[\"{}\",{}]".format(createtxid, amount)
    raw_hex = rpc_connection.paymentsrelease(str(params))
    try:
        txid = rpc_connection.sendrawtransaction(raw_hex['hex'])
        print(colorize("Payments Release Txid: "+txid, 'green'))
        print(colorize("Confirming transaction\n", "blue"))
        check_if_tx_in_mempool(rpc_connection, txid)
        input("Press [Enter] to continue...")
        return txid
    except Exception as e:
        print("Something went wrong!")
        print(e)
        print(raw_hex)
        input("Press [Enter] to continue...")


def payments_txidopret(rpc_connection, allocation='', pubkey='', destopret=''):
    if pubkey == '':
        pubkey = input("Recipient pubkey: ")
    scriptPubKey = "21"+pubkey+"ac"
    if allocation == '':
        allocation = input("Allocation: ")
    if destopret == '':
        add_destopret = input("Do you want to add destination OPRET data? (y/n): ")
        if add_destopret == 'y' or add_destopret == 'Y':
            destopret = input("Enter destination OPRET data: ")
            params = "[{},\"{}\",\"{}\"]".format(allocation, scriptPubKey, destopret)
        else:
            params = "[{},\"{}\"]".format(allocation, scriptPubKey)
    elif destopret is False:
        params = "[{},\"{}\"]".format(allocation, scriptPubKey)
    else:
        params = "[{},\"{}\",\"{}\"]".format(allocation, scriptPubKey, destopret)
    raw_hex = rpc_connection.paymentstxidopret(str(params))
    try:
        txid = rpc_connection.sendrawtransaction(raw_hex['hex'])
        print(colorize("OPRET TXID: "+txid, 'green'))
        print(colorize("Confirming transaction\n", "blue"))
        check_if_tx_in_mempool(rpc_connection, txid)
        input("Press [Enter] to continue...")
        return txid
    except Exception as e:
        print("Something went wrong!")
        print(e)
        print(raw_hex)
        input("Press [Enter] to continue...")

# Selection menus and validation

def validate_selection(interrogative, selection_list):
    while True:
        index = int(input(interrogative))-1
        try:
            selected = selection_list[index]
            return selected
        except:
            print("Invalid selection, must be number between 1 and "+str(len(selection_list)))
            pass

def select_ac():
    while True:
        dir_list = next(os.walk(home+"/.komodo"))[1]
        ac_list = []
        row = ''
        i = 1
        for folder in dir_list:
            if folder not in ['notarisations', 'blocks', 'database', 'chainstate']:
                ac_list.append(folder)
                if i < 10:
                    row += " ["+str(i)+"] "+'{:^14}'.format(folder)
                else:
                    row += "["+str(i)+"] "+'{:^14}'.format(folder)
                if len(row) > 64:
                    print(row)
                    row = ''
                i += 1
        selection = validate_selection("Select Smart Chain: ", ac_list)
        return selection

def select_address(rpc_connection):
    list_address_groupings = rpc_connection.listaddressgroupings()
    addresses = []
    for address_list in list_address_groupings:
        for address in address_list:
            if address[1] > 0:
                addresses.append([address[0],address[1]])
    i = 1
    for address in addresses:
        print("["+str(i)+"] "+address[0]+" (balance: "+str(address[1])+")")
        i +=1
    while True:
        address_index = int(input("Select Address: "))-1
        try:
            sendaddress = addresses[address_index][0]
            return sendaddress
        except:
            print("Invalid selection, must be number between 1 and "+str(len(gateways_list)))
            pass
    
def select_tokenid(rpc_connection):
    token_list = rpc_connection.tokenlist()
    tokenids = []
    i = 1
    for tokenid in token_list:
        token_info = rpc_connection.tokeninfo(tokenid)
        print("["+str(i)+"] "+token_info['tokenid']+" | "+token_info['name'] \
             +" | "+token_info['description']+" | Supply: "+str(token_info['supply'])+" |")
        i +=1
    selection = validate_selection("Select Token Contract: ", token_list)
    return selection

def select_oracle_txid(rpc_connection):
    oracle_list = rpc_connection.oracleslist()
    if len(oracle_list) == 0:
        print(colorize("No oracles on this smart chain!", "red"))
        input("Press [Enter] to continue...")
        return 'back to menu'
    i = 1
    header = "|"+'{:^6}'.format("[#]")+"|" \
            +'{:^66}'.format("ORACLE TXID")+"|" \
            +'{:^32}'.format("NAME")+"|" \
            +'{:^75}'.format("DESCRIPTION")+"|" \
            +'{:^6}'.format("TYPE")+"|" 
    table_dash = "-"*len(header)
    print(" "+table_dash)
    print(" "+header)
    print(" "+table_dash)
    for oracle_txid in oracle_list:
        info = rpc_connection.oraclesinfo(oracle_txid)
        row = "|"+'{:^6}'.format("["+str(i)+"]")+"|" \
            +'{:^66}'.format(info['txid'])+"|" \
            +'{:^32}'.format(info['name'])+"|" \
            +'{:^75}'.format(info['description'])+"|" \
            +'{:^6}'.format(info['format'])+"|" 
        print(" "+row)
        i +=1
    print(" "+table_dash)
    selection = validate_selection("Select Oracle: ", oracle_list)
    return selection

def select_oracleType():
    oracles_data_types = [
        { "type":"IhhL", "desc":"height, blockhash, merkleroot (used by oraclefeed dapp)" },
        { "type":"s", "desc":"String less than 256 bytes" },
        { "type":"S", "desc":"String, less than 65563 bytes" },
        { "type":"d", "desc":"Binary less than 256 bytes" },
        { "type":"D", "desc":"Binary, less than 65563 bytes" },
        { "type":"c", "desc":"1 byte little endian number (signed)" },
        { "type":"C", "desc":"1 byte little endian number (unsigned)" },
        { "type":"t", "desc":"2 byte little endian number (signed)" },
        { "type":"T", "desc":"2 byte little endian number (unsigned)" },
        { "type":"i", "desc":"4 byte little endian number (signed)" },
        { "type":"I", "desc":"4 byte little endian number (unsigned)" },
        { "type":"l", "desc":"8 byte little endian number (signed)" },
        { "type":"L", "desc":"8 byte little endian number (unsigned)" },
        { "type":"h", "desc":"32 byte hash" }
    ]
    i = 1
    type_list = []
    header = "|"+'{:^6}'.format("[#]")+"|" \
            +'{:^6}'.format("TYPE")+"|" \
            +'{:^57}'.format("DESCRIPTION")+"|" 
    table_dash = "-"*len(header)
    print(" "+table_dash)
    print(" "+header)
    print(" "+table_dash)
    for option in oracles_data_types:
        type_list.append(option['type'])
        row = "|"+'{:^6}'.format("["+str(i)+"]")+"|" \
            +'{:^6}'.format(option['type'])+"|" \
            +'{:^57}'.format(option['desc'])+"|" 
        print(" "+row)
        i += 1
    print(" "+table_dash)
    selection = validate_selection("Select Oracle Data Type: ", type_list)
    return selection
        

def select_gateway(rpc_connection):
    gw_list = rpc_connection.gatewayslist()
    if len(gw_list) == 0:
        print(colorize("No gateways on this smart chain!", "red"))
        input("Press [Enter] to continue...")
        return 'back to menu'
    i = 1
    for gw in gw_list:
        info = rpc_connection.gatewaysinfo(gw)
        print("["+str(i)+"] "+info['txid']+" | "+info['coin']+" |")
        i +=1
    selection = validate_selection("Select Gateway: ", gw_list)
    return selection

def select_payments(rpc_connection):
    payments_list = rpc_connection.paymentslist()['createtxids']
    if len(payments_list) == 0:
        print(colorize("No Payments contracts on this smart chain!", "red"))
        input("Press [Enter] to continue...")
        return 'back to menu'
    i = 1
    header = "|"+'{:^5}'.format("[#]")+"|" \
            +'{:^66}'.format("Transaction Hash")+"|" \
            +'{:^16}'.format("Eligible Funds")+"|" \
            +'{:^13}'.format("Total Funds")+"|" \
            +'{:^20}'.format("Min Release Amount")+"|" \
            +'{:^20}'.format("Min Release Height")+"|" \
            +'{:^23}'.format("Blocks Until Eligible")+"|" \
            +'{:^7}'.format("UTXOs")+"|"
    table_dash = "-"*len(header)
    print(" "+table_dash)
    print(" "+header)
    print(" "+table_dash)
    block_height = rpc_connection.getblockcount()
    for txid in payments_list:
        info = rpc_connection.paymentsinfo('[\"{}\"]'.format(txid))
        blocks_until_eligible = info['min_release_height'] - block_height
        if blocks_until_eligible < 1:
            blocks_until_eligible = colorize('{:^23}'.format("Eligible"), 'green')
        row = "|"+'{:^5}'.format("["+str(i)+"]")+"|" \
             +'{:^66}'.format(txid)+"|" \
             +'{:^16}'.format(str(info['elegiblefunds']))+"|" \
             +'{:^13}'.format(str(info['totalfunds']))+"|" \
             +'{:^20}'.format(str(info['minrelease']))+"|" \
             +'{:^20}'.format(str(info['min_release_height']))+"|" \
             +'{:^23}'.format(str(blocks_until_eligible))+"|" \
             +'{:^7}'.format(str(info['utxos']))+"|"
        print(" "+row)
        i += 1
    print(" "+table_dash)
    selection = validate_selection("Select Payments contract: ", payments_list)
    return selection


def select_oracle_publisher(rpc_connection, oracle_txid):
    info = rpc_connection.oraclesinfo(oracle_txid)
    publisher_list = []
    i = 1
    if len(info['registered']) == 0:
        print(colorize("No publishers registered on this oracle!", "red"))
        input("Press [Enter] to continue...")
        return 'back to menu'
    i = 1
    header = "|"+'{:^5}'.format("[#]")+"|" \
            +'{:^68}'.format("PUBLISHER (green = your pubkey")+"|" \
            +'{:^36}'.format("BATON ADDRESS")+"|" \
            +'{:^14}'.format("FUNDS")+"|" \
            +'{:^14}'.format("DATAFEE")+"|" 
    table_dash = "-"*len(header)
    print(" "+table_dash)
    print(" "+header)
    print(" "+table_dash)
    for publisher in info['registered']:
        publisher_list.append(publisher['publisher'])
        info = rpc_connection.oraclesinfo(oracle_txid)
        if publisher['publisher'] == rpc_connection.getinfo()['pubkey']:
            row = "|"+'{:^5}'.format("["+str(i)+"]")+"|" \
                    +'{:^68}'.format(publisher['publisher'])+"|" \
                    +'{:^36}'.format(publisher['baton'])+"|" \
                    +'{:^14}'.format(str(publisher['funds'])[:12])+"|" \
                    +'{:^14}'.format(str(publisher['datafee'])[:12])+"|" 
            print(colorize(" "+row, "green"))
        else: 
            row = "|"+'{:^5}'.format("["+str(i)+"]")+"|" \
                    +'{:^68}'.format(publisher['publisher'])+"|" \
                    +'{:^36}'.format(publisher['baton'])+"|" \
                    +'{:^14}'.format(str(publisher['funds'])[:12])+"|" \
                    +'{:^14}'.format(str(publisher['datafee'])[:12])+"|" 
            print(colorize(" "+row, "blue"))
        i +=1
    selected = validate_selection("Select Oracle Publisher to subscribe to: ", publisher_list)
    return selected

def select_file(path, ext=''):
    file_list = []
    with os.scandir(path) as ls:
        for item in ls:
            if item.is_file():
                filename = str(item.name)
                if ext == '':
                    file_list.append(filename)
                    interrogative = "Select a file: "
                elif filename.endswith(ext):
                    file_list.append(filename)
                    interrogative = "Select "+ext+" file: "
    i = 1
    for file in file_list:
        print("["+str(i)+"] "+file)
        i += 1
    selected = validate_selection(interrogative, file_list)
    return selected
