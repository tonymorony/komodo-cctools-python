import os
import time
import sys
import subprocess
from slickrpc import Proxy, exc
import random

# init params, nodes amount can't be < than 5
dexp2p_clients_to_start = 100
ac_name = 'DEXTEST'
node_ip = '127.0.0.1'

# pre-creating separate folders
for i in range(dexp2p_clients_to_start):
    os.mkdir("node_" + str(i))
    open("node_" + str(i) + "/" + ac_name + ".conf", 'a').close()
    with open("node_" + str(i) + "/" + ac_name + ".conf", 'a') as conf:
        conf.write("rpcuser=test" + '\n')
        conf.write("rpcpassword=test" + '\n')
        conf.write("rpcport=" + str(7000 + i) + '\n')
        conf.write("port=" + str(6000 + i) + '\n')

# start numnodes daemons, changing folder name and port
for i in range(dexp2p_clients_to_start):
    # first node doesn't connect to any node
    if i == 0:
        subprocess.call(['./komodod', '-ac_name=' + ac_name,
                         '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-dexp2p=2', '-whitelist=127.0.0.1', '-daemon'])
        time.sleep(5)
    # let's connect first few nodes to the seed node to surely have a network
    elif i < 4:
        subprocess.call(['./komodod', '-ac_name=' + ac_name,
                         '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-dexp2p=2', '-addnode=127.0.0.1:6000', '-whitelist=127.0.0.1', '-daemon'])
        time.sleep(5)
    else:
        # choosing 4 random pre-determined already started nodes ports to connect
        nodes_ports_to_connect = []
        for j in range(4):
            node_port = random.randint(6000, 6000 + i - 1)
            while True:
                # to not connect to the same node twice
                if node_port in nodes_ports_to_connect:
                    node_port = random.randint(6000, 6001 + dexp2p_clients_to_start - 1)
                else:
                    nodes_ports_to_connect.append(node_port)
                    break
        daemon_args = ['./komodod', '-ac_name=' + ac_name,
                         '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-dexp2p=2', '-whitelist=127.0.0.1', '-daemon']
        for node_port in nodes_ports_to_connect:
            daemon_args.append("-addnode=" + node_ip + ":" + str(node_port))
        subprocess.call(daemon_args)
        time.sleep(5)

# creating rpc proxies for all nodes
for i in range(dexp2p_clients_to_start):
    rpcport = 7000 + i
    globals()['proxy_%s' % i] = Proxy("http://%s:%s@127.0.0.1:%d" % ("test", "test", int(rpcport)))
    try:
        dex_stats_output = globals()['proxy_%s' % i].DEX_stats()
        print(dex_stats_output)
    except Exception as e:
        print(e)

# since connection ports were chosen randomly let's try to interconnect orphan nodes
for i in range(dexp2p_clients_to_start):
    connections_amount = globals()['proxy_%s' % i].getinfo()["connections"]
    print(connections_amount)

print("All nodes started (hopefully) - you can proceed to loading test")
