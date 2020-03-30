import platform
import os
import re
import slickrpc
import shutil
import time
import threading
import math
import requests


"""
slickrpc.Proxy -> List
returns list with marmaraactivated addresses for provided MCL daemon proxy
"""


def marmara_list_addresses(marmara_proxy):
    marmara_list_activated_addresses = marmara_proxy.marmaralistactivatedaddresses()["WalletActivatedAddresses"]
    marmara_addresses_list = []
    for entry in marmara_list_activated_addresses:
        marmara_addresses_list.append(entry["activatedaddress"])
    return marmara_addresses_list


""" 
slickrpc.Proxy -> Dict
Desired RPC proxy providing as first arg. finding pubkeys for provided rpc proxy wallet and return dict
where keys marmaraactivated addresses and values pubkeys
"""


def marmara_find_pubkeys(marmara_proxy):
    listaddressgroupings = marmara_proxy.listaddressgroupings()
    pubkeys_list = []
    for group in listaddressgroupings[0]:
        usual_address = group[0]
        pubkey = marmara_proxy.validateaddress(usual_address)["pubkey"]
        pubkeys_list.append(pubkey)
    marmara_addy_pub = {}
    for pubkey in pubkeys_list:
        pubkey_marmara_info = marmara_proxy.marmarainfo("0", "0", "0", "0", pubkey)
        marmara_addy_pub[pubkey_marmara_info["myCCActivatedAddress"]] = pubkey
    return marmara_addy_pub



""" 
String -> slickrpc.Proxy
creating proxy object for provided ac_name by searching for rpc credentials locally 
"""


def def_credentials(chain, mode="usual"):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)
    return slickrpc.Proxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))
