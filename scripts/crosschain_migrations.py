from slickrpc import Proxy
import time
import sys
import datetime


def wait_for_confirmation(rpc_connection, tx_id, confirmations_amount_goal):
    confirmations_amount = 0
    while confirmations_amount < confirmations_amount_goal:
        time.sleep(15)
        confirmations_amount = int(rpc_connection.gettransaction(tx_id)["confirmations"])
        print("Have " + str(confirmations_amount) + " confirmations")
        print("Waiting for more confirmations: " + str(confirmations_amount_goal))
    print("Transaction confirmed!\n")


def print_balance(rpc_connection_source, rpc_connection_destination):
    balance_source = rpc_connection_source.getbalance()
    balance_destination = rpc_connection_destination.getbalance()
    source_chain_name = rpc_connection_source.getinfo()["name"]
    destination_chain_name = rpc_connection_destination.getinfo()["name"]
    print("Source chain " + source_chain_name + " balance: " + str(balance_source))
    print("Destination chain " + destination_chain_name + " balance: " + str(balance_destination))


# SET RPC CONNECTION DETAILS HERE
rpc_connection_sourcechain = Proxy("http://%s:%s@127.0.0.1:%d"%("user", "pass", 30667))
rpc_connection_destinationchain = Proxy("http://%s:%s@127.0.0.1:%d"%("user", "pass", 50609))
rpc_connection_kmdblockchain = Proxy("http://%s:%s@127.0.0.1:%d"%("user", "pass", 7771))
# SET ADDRESS AND MIGRATION AMOUNT HERE
address = "RHq3JsvLxU45Z8ufYS6RsDpSG4wi6ucDev"
amount = 0.1

t0 = time.time()

print_balance(rpc_connection_sourcechain, rpc_connection_destinationchain)

print("Sending " + str(amount) + " coins from " + rpc_connection_sourcechain.getinfo()["name"] + " chain " +\
      "to " + rpc_connection_destinationchain.getinfo()["name"] + " chain")

# Creating rawtransaction
raw_transaction = rpc_connection_sourcechain.createrawtransaction([], {address: amount})
export_data = rpc_connection_sourcechain.migrate_converttoexport(raw_transaction, rpc_connection_destinationchain.getinfo()["name"])
export_raw = export_data["exportTx"]

# Fund it
export_funded_data = rpc_connection_sourcechain.fundrawtransaction(export_raw)
export_funded_transaction = export_funded_data["hex"]
payouts = export_data["payouts"]

# Sign rawtx and export
signed_hex = rpc_connection_sourcechain.signrawtransaction(export_funded_transaction)
sent_tx = rpc_connection_sourcechain.sendrawtransaction(signed_hex["hex"])

# Check if export transaction was created successfully
if len(sent_tx) != 64:
    print(signed_hex)
    print(sent_tx)
    print("Export TX not successfully created")
    sys.exit()

# Wait for a confirmation on source chain
wait_for_confirmation(rpc_connection_sourcechain, sent_tx, 3)
print(rpc_connection_sourcechain.getinfo()["name"] + " : Confirmed export " + str(sent_tx))

# Use migrate_createimporttransaction to create the import TX
while True:
    # ?
    time.sleep(60)
    try:
        import_tx = rpc_connection_sourcechain.migrate_createimporttransaction(signed_hex["hex"], payouts)
    except Exception as e:
        print(e)
        print("Import transaction not created yet, waiting for 60 seconds more")
        pass
    else:
        print("Seems tx created")
        break

# Use migrate_completeimporttransaction on KMD to complete the import tx
while True:
    time.sleep(60)
    try:
        complete_tx = rpc_connection_kmdblockchain.migrate_completeimporttransaction(import_tx)
    except Exception as e:
        print(e)
        print("Import transaction on KMD not created yet, waiting for 60 seconds more")
        pass
    else:
        print("Seems tx created")
        break

# Broadcast tx to target chain
attempts = 0
while True:
    time.sleep(60)
    if attempts < 60:
        try:
            sent_itx = rpc_connection_destinationchain.sendrawtransaction(complete_tx)
        except Exception:
            attempts = attempts + 1
            print("Tried to broadcast " + str(attempts) + " times")
            print("Will try to do it 60 times in total")
        else:
            break
    else:
        print("To many attempts. Bye bye.")
        sys.exit()

final_confirmations = 0
#wait_for_confirmation(rpc_connection_destinationchain, sent_itx, 3)
while final_confirmations < 0:
    try:
        final_confirmations = int(rpc_connection_destinationchain.getrawtransaction(sent_itx, 1)["confirmations"])
    except Exception as e:
        print(e)
        pass
    else:
        print("Waiting")
print(rpc_connection_destinationchain.getinfo()["name"] + " : Confirmed import " + sent_itx + "  at: " + str(datetime.datetime.today().strftime('%Y-%m-%d')))
print_balance(rpc_connection_sourcechain, rpc_connection_destinationchain)
t1 = time.time()
print(str(t1-t0) + " migration time (sec)")