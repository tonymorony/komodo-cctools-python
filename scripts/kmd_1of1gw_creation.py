#!/usr/bin/env python3

from lib import tuilib
import time
import subprocess

ac_name = "GWTEST5"
start_time = time.time()

# proxies for ac_name assetchain and KMD daemon (both should be up)\
rpc_connection_ac = tuilib.def_credentials(ac_name)
rpc_connection_kmd = tuilib.def_credentials("KMD")

print(tuilib.colorize("\nSetting up 1of1 test GW for KMD. Please be patient - it can take some time.\n", "green"))

# creating token
token_hex = rpc_connection_ac.tokencreate("KMD", "1", "Test")["hex"]
token_txid = rpc_connection_ac.sendrawtransaction(token_hex)

# create oracle
oracle_hex = rpc_connection_ac.oraclescreate("KMD", "Test", "Ihh")["hex"]
oracle_txid = rpc_connection_ac.sendrawtransaction(oracle_hex)

# register as publisher with 10000 sat datafee
register_hex = rpc_connection_ac.oraclesregister(oracle_txid, "10000")["hex"]
register_txid = rpc_connection_ac.sendrawtransaction(register_hex)

# waiting until registration transaction is mined
tuilib.check_if_tx_in_mempool(rpc_connection_ac, register_txid)

# subscribing on this publisher utxo_num times
utxo_num = 10
while utxo_num > 0:
    publisher_id = rpc_connection_ac.getinfo()["pubkey"]
    while True:
        oracle_subscription_hex = rpc_connection_ac.oraclessubscribe(oracle_txid, publisher_id, "0.1")["hex"]
        oracle_subscription_txid = rpc_connection_ac.sendrawtransaction(oracle_subscription_hex)
        mempool = rpc_connection_ac.getrawmempool()
        if oracle_subscription_txid in mempool:
            break
        else:
            pass
    print(tuilib.colorize("Oracle subscription transaction broadcasted: " + oracle_subscription_txid, "green"))
    utxo_num = utxo_num - 1

# bind gateway
pubkey = rpc_connection_ac.getinfo()["pubkey"]
gateways_bind_hex = rpc_connection_ac.gatewaysbind(token_txid, oracle_txid, "KMD", "100000000", "1", "1", pubkey, "60", "85", "188")["hex"]
gateways_bind_txid = rpc_connection_ac.sendrawtransaction(gateways_bind_hex)

tuilib.check_if_tx_in_mempool(rpc_connection_ac, gateways_bind_txid)

# export privkey for gateways deposit address from AC to KMD daemon
deposit_address = rpc_connection_ac.gatewaysinfo(gateways_bind_txid)["deposit"]
deposit_address_privkey = rpc_connection_ac.dumpprivkey(deposit_address)
rpc_connection_kmd.importprivkey(deposit_address_privkey)

# save all params to file
timestamp = str(int(time.time()))
file_name = "gateway_binded_at_" + timestamp + ".txt"
with open(file_name, "w+") as file:
    file.writelines("Bind txid: " + gateways_bind_txid)
    file.writelines("Token txid: " + token_txid)
    file.writelines("Oracle txid: " + oracle_txid)

print(tuilib.colorize("Gateway succesfully binded! Information saved to file: " + file_name, "green"))
print("--- %s seconds ---" % (time.time() - start_time))

# start oraclefeed for this gateway
subprocess.call(["./oraclefeed", ac_name, oracle_txid, pubkey, "Ihh", gateways_bind_txid])