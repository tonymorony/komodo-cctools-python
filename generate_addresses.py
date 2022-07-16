# test purposes script, generates needed amount of pre-funded addresses
from slickrpc import Proxy
from lib import rpclib
import json
import time

# settings
amount_of_addresses = 2
amount_of_funding = 1

# generate addresses to fund
kmd_rpc_proxy_auth = rpclib.get_rpc_details("KMD")

rpc_user = kmd_rpc_proxy_auth[0]
rpc_password = kmd_rpc_proxy_auth[1]
rpc_port = int(kmd_rpc_proxy_auth[2])

rpc_proxy_kmd = Proxy("http://%s:%s@127.0.0.1:%d"%(rpc_user, rpc_password, rpc_port))

addresses_to_fund = {}

while amount_of_addresses > 0:
    new_address = rpc_proxy_kmd.getnewaddress()
    new_privkey = rpc_proxy_kmd.dumpprivkey(new_address)
    addresses_to_fund[new_address] = { "private_key" : new_privkey,
                                       "is_funded_rick": False, "is_funded_morty": False }
    amount_of_addresses -= 1


# fund RICK
rick_rpc_proxy_auth = rpclib.get_rpc_details("RICK")
rick_txs_count = 0
rpc_proxy_rick = Proxy("http://%s:%s@127.0.0.1:%d"%(rick_rpc_proxy_auth[0], rick_rpc_proxy_auth[1], int(rick_rpc_proxy_auth[2])))
for address in addresses_to_fund:
    if not addresses_to_fund[address]["is_funded_rick"]:
        rick_funding_txid = rpc_proxy_rick.sendtoaddress(address, amount_of_funding)
        print(rick_funding_txid)
        # TODO: confirm that its really mined
        addresses_to_fund[address]["is_funded_rick"] = True
        rick_txs_count += 1
        # to not fill the blocks completely
        if rick_txs_count % 1000 == 0:
            time.sleep(60)


# TODO: funding processes can be parallel since its different blockchains

# fund MORTY
morty_rpc_proxy_auth = rpclib.get_rpc_details("MORTY")
morty_txs_count = 0
rpc_proxy_morty = Proxy("http://%s:%s@127.0.0.1:%d"%(morty_rpc_proxy_auth[0], morty_rpc_proxy_auth[1], int(morty_rpc_proxy_auth[2])))
for address in addresses_to_fund:
    if not addresses_to_fund[address]["is_funded_morty"]:
        morty_funding_txid = rpc_proxy_morty.sendtoaddress(address, amount_of_funding)
        print(morty_funding_txid)
        # TODO: confirm that its really mined
        addresses_to_fund[address]["is_funded_morty"] = True
        morty_txs_count += 1
        # to not fill the blocks completely
        if morty_txs_count % 1000 == 0:
            time.sleep(60)


addys_json = json.dumps(addresses_to_fund, indent=4)
with open("funded_addresses.json", "w+") as file:
    file.write(addys_json)

