from slickrpc import Proxy
import time
import sys
import datetime


def print_balance(rpc_connection_source, rpc_connection_destination):
    balance_source = rpc_connection_source.getbalance()
    balance_destination = rpc_connection_destination.getbalance()
    source_chain_name = rpc_connection_source.getinfo()["name"]
    destination_chain_name = rpc_connection_destination.getinfo()["name"]
    print("Source chain " + source_chain_name + " balance: " + str(balance_source))
    print("Destination chain " + destination_chain_name + " balance: " + str(balance_destination))


def create_import_transactions(rpc_connection, signed_hex, payouts, import_tx_list):
    while True:
        try:
            import_tx = rpc_connection.migrate_createimporttransaction(signed_hex["hex"], payouts)
        except Exception as e:
            print(e)
            print("Import transaction not created yet, waiting for 10 seconds more")
            time.sleep(10)
            pass
        else:
            print("Seems tx created")
            is_created = True
            import_tx_list.append(import_tx)
            break
    return is_created


def migrate_import_transactions(rpc_connection, import_tx, complete_tx_list):
    while True:
        try:
            complete_tx = rpc_connection.migrate_completeimporttransaction(import_tx)
        except Exception as e:
            print(e)
            print("Import transaction on KMD not created yet, waiting for 10 seconds more")
            time.sleep(10)
            pass
        else:
            print("Seems tx created")
            is_imported = True
            complete_tx_list.append(complete_tx)
            break
    return is_imported


def broadcast_on_destinationchain(rpc_connection, complete_tx, dest_tx_list):
    attempts = 0
    while True:
        if attempts < 60:
            try:
                sent_itx = rpc_connection.sendrawtransaction(complete_tx)
            except Exception:
                attempts = attempts + 1
                print("Tried to broadcast " + str(attempts) + " times")
                print("Will try to do it up to 60 times in total. Now rest for 15 seconds.")
                time.sleep(15)
            else:
                print("Transactinon broadcasted on destination chain")
                dest_tx_list.append(sent_itx)
                is_broadcasted = True
                break
        else:
            print("Too many attempts. Bye bye.")
            sys.exit()
    return is_broadcasted


# SET RPC CONNECTION DETAILS HERE
rpc_connection_sourcechain = Proxy("http://%s:%s@127.0.0.1:%d"%("user", "pass", 30667))
rpc_connection_destinationchain = Proxy("http://%s:%s@127.0.0.1:%d"%("user", "pass", 50609))
rpc_connection_kmdblockchain = Proxy("http://%s:%s@127.0.0.1:%d"%("user", "pass", 7771))
# SET ADDRESS AND MIGRATION AMOUNT HERE
address = "RHq3JsvLxU45Z8ufYS6RsDpSG4wi6ucDev"
amount = 2
migrations_amount = 500

t0 = time.time()

print_balance(rpc_connection_sourcechain, rpc_connection_destinationchain)

print("Sending " + str(amount) + " coins from " + rpc_connection_sourcechain.getinfo()["name"] + " chain " +\
      "to " + rpc_connection_destinationchain.getinfo()["name"] + " chain")

counter_raw = migrations_amount
sent_tx_list = []
payouts_list = []
signed_hex_list = []
while counter_raw > 0:
    raw_transaction = rpc_connection_sourcechain.createrawtransaction([], {address: amount})
    export_data = rpc_connection_sourcechain.migrate_converttoexport(raw_transaction, rpc_connection_destinationchain.getinfo()["name"])
    export_raw = export_data["exportTx"]
    export_funded_data = rpc_connection_sourcechain.fundrawtransaction(export_raw)
    export_funded_transaction = export_funded_data["hex"]
    payouts = export_data["payouts"]
    payouts_list.append(payouts)
    signed_hex = rpc_connection_sourcechain.signrawtransaction(export_funded_transaction)
    signed_hex_list.append(signed_hex)
    sent_tx = rpc_connection_sourcechain.sendrawtransaction(signed_hex["hex"])
    if len(sent_tx) != 64:
        print(signed_hex)
        print(sent_tx)
        print("Export TX not successfully created")
        sys.exit()
    sent_tx_list.append(sent_tx)
    counter_raw = counter_raw - 1

print(str(len(sent_tx_list)) + " export transactions sent:\n")
for sent_tx in sent_tx_list:
    print(sent_tx + "\n")


# Wait for a confirmation on source chain
while True:
    confirmed = all(int(rpc_connection_sourcechain.gettransaction(sent_tx)["confirmations"]) > 0 for sent_tx in sent_tx_list)
    if not confirmed:
        print("Waiting for all export transactions to be confirmed on source chain")
        time.sleep(5)
    else:
        print("All export transactions confirmed!")
        break

# Use migrate_createimporttransaction to create the import TX
import_list = []
while True:
    import_tx_created = all(create_import_transactions(rpc_connection_sourcechain, signed_hex, payouts, import_list) for signed_hex, payouts in zip(signed_hex_list, payouts_list))
    if not import_tx_created:
        print("Waiting for all import transactions to be created on source chain")
    else:
        print("All import transactions created!")
        break

# Use migrate_completeimporttransaction on KMD to complete the import tx
complete_list = []
while True:
    migration_complete = all(migrate_import_transactions(rpc_connection_kmdblockchain, import_tx, complete_list) for import_tx in import_list)
    if not migration_complete:
        print("Waiting for all migrations to be completed on Komodo blockchain")
    else:
        print("All migrations are completed on Komodo blockchain")
        break

# Broadcast tx to target chain
dest_txs = []
while True:
    broadcasted_on_target = all(broadcast_on_destinationchain(rpc_connection_destinationchain, complete_tx, dest_txs) for complete_tx in complete_list)
    if not broadcasted_on_target:
        print("Waiting for imports to be broadcasted on destination chain")
    else:
        print("All imports are broadcasted to destination chain")
        break

# Wait for a confirmation on destination chain
while True:
    try:
        confirmed = all(int(rpc_connection_destinationchain.getrawtransaction(dest_tx, 1)["confirmations"]) > 0 for dest_tx in dest_txs)
    except Exception as e:
        print(e)
        print("Transaction is not on blockchain yet. Let's wait a little.")
        time.sleep(10)
        pass
    else:
        if not confirmed:
            print("Waiting for all export transactions to be confirmed on source chain")
            time.sleep(5)
        else:
            print("All export transactions confirmed!")
            break

for sent_itx in dest_txs:
    print(rpc_connection_destinationchain.getinfo()["name"] + " : Confirmed import " + sent_itx + "  at: " + str(datetime.datetime.today().strftime('%Y-%m-%d-%M:%S')))

t1 = time.time()
print("Total migrations amount: " + str(migrations_amount))
print(str(t1-t0) + " migration time (sec)")