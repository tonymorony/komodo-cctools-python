import os
import time
import sys
import subprocess
from slickrpc import Proxy

# init params
nspv_clients_to_start = 500
ac_name = 'ILN'

# pre-creating separate folders
for i in range(nspv_clients_to_start):
    os.mkdir("node_" + str(i))
    open("node_" + str(i) + "/" + ac_name + ".conf", 'a').close()
    with open("node_" + str(i) + "/" + ac_name + ".conf", 'a') as conf:
        conf.write("rpcuser=test" + '\n')
        conf.write("rpcpassword=test" + '\n')
        conf.write("rpcport=" + str(7000 + i) + '\n')

#start numnodes daemons, changing folder name and port
for i in range(nspv_clients_to_start):
    subprocess.call(['./komodod', '-ac_name=ILN', '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                     '-rpcport=' + str(7000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                     '-ac_supply=10000000000', '-ac_cc=2', '-nSPV=1', '-connect=5.9.102.210', '-listen=0', '-daemon'])

time.sleep(2)

#creating rpc proxies for all nodes
for i in range(nspv_clients_to_start):
    rpcport = 7000 + i
    globals()['proxy_%s' % i] = Proxy("http://%s:%s@127.0.0.1:%d"%("test", "test", int(rpcport)))

while True:
    for i in range(nspv_clients_to_start):
        try:
            nspv_getinfo_output = globals()['proxy_%s' % i].nspv_getinfo()
            print(nspv_getinfo_output)
        except Exception as e:
            print(e)
