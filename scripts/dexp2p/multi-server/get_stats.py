from slickrpc import Proxy, exc
import json
import os

proxies_to_create = 10

for i in range(proxies_to_create):
    rpcport = 7000 + i
    globals()['proxy_%s' % i] = Proxy("http://%s:%s@127.0.0.1:%d" % ("test", "test", int(rpcport)))
    dex_stats = globals()['proxy_%s' % i].DEX_stats()
    print(dex_stats["perfstats"])