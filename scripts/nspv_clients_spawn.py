import os
import sys
import subprocess

# init params
nspv_clients_to_start = 2000
ac_name = 'ZEXO'

# pre-creating separate folders
for i in range(nspv_clients_to_start):
    os.mkdir("node_" + str(i))
    open("node_" + str(i) + "/" + ac_name + ".conf", 'a').close()

#start numnodes daemons, changing folder name and port
for i in range(nspv_clients_to_start):
    subprocess.call(['./komodod', '-ac_name=ZEXO', '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                     '-rpcport=' + str(7000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                     '-ac_supply=100000000', '-ac_reward=1478310502','-ac_halving=525600','-ac_cc=42',
                     '-ac_ccenable=236', '-ac_perc=77700', '-ac_staked=93',
                     '-ac_pubkey=02713bd85e054db923694b6b7a85306264edf4d6bd6d331814f2b40af444b3ebbc',
                     '-ac_public=1', '-nSPV=1', '-addnode=95.217.44.58', '-listen=0', '-daemon'])
