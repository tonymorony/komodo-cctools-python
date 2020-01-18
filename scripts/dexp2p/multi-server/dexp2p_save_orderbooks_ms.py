import os
import time
import sys
import subprocess
from slickrpc import Proxy, exc
import random

proxies_to_create = int(os.getenv('NODESAMOUNT'))

server_ips = ["159.69.45.70", "95.217.44.58"]

# creating rpc proxies for NODESAMOUNT
for i in range(proxies_to_create):
    rpcport = 7000 + i
    globals()['proxy_%s' % i] = Proxy("http://%s:%s@127.0.0.1:%d" % ("test", "test", int(rpcport)))
    # getting DEX_list from each node for each port tag
    iter_port = 7000
    while iter_port < (7000 + proxies_to_create):
        dex_list = globals()['proxy_%s' % i].DEX_list("0", "0", str(iter_port))
        iter_port = iter_port + 1
        # separating by server IP