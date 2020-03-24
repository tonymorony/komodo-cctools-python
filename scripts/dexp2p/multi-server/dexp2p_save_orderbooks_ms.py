from slickrpc import Proxy, exc
import json
import os

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
        # separating by server IP
        for server_ip in server_ips:
            matches_for_ip = []
            for match in dex_list["matches"]:
                if server_ip in match["payload"]:
                    matches_for_ip.append(match)
            file_name = str(rpcport) + '_' + server_ip + "_" + str(iter_port) + ".json"
            matches_json = json.dumps(matches_for_ip)
            with open('spam_p2p/orderbooks/' + file_name, "w+") as json_file:
                json.dump(matches_json, json_file)
        iter_port = iter_port + 1