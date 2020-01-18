import json
import os

# loading nodes packages  nodeport[n] : ["id"]["hash"]
package_files_list = os.listdir('spam_p2p/packages')

nodes_packages = {}
last_port = 7000 + int(os.getenv('NODESAMOUNT'))

self_ip = "159.69.45.70"

for node_port in range(7000, last_port):
    nodes_packages[node_port] = {}
    for file in package_files_list:
        if int(file.split("_")[2]) == node_port:
            with open('spam_p2p/packages/' + file) as json_file:
                packages_counter = 0
                list_of_pacakges = json_file.readlines()
                for package in list_of_pacakges:
                    package_json = json.loads(package)
                    packages_counter = packages_counter + 1
                    nodes_packages[node_port][packages_counter] = {}
                    nodes_packages[node_port][packages_counter]["id"] = package_json["result"]["id"]
                    nodes_packages[node_port][packages_counter]["hash"] = package_json["result"]["hash"]
                nodes_packages[node_port]["total"] = packages_counter


# loading nodes orderbooks  nodeport[n] : [tag][orderbook]
orderbook_files_list = os.listdir('spam_p2p/orderbooks')

# comparing broadcasted packages vs received orderbooks
for nodeport in nodes_packages:
    packages_amount_sent = nodes_packages[nodeport]["total"]
    print("Packages sent by node " + self_ip + ":" + str(nodeport) + " : " + str(packages_amount_sent))
for file in orderbook_files_list:
    with open('spam_p2p/orderbooks/' + file) as json_file:
        file_content = json.load(json_file)
    packages_amount = len(json.loads(file_content))
    node_address = file.split("_")[1] + ":" +  file.split("_")[2][:-5]
    print("Packages received from node " + node_address + " "  + str(packages_amount) + " by node " + self_ip + ":" + file.split("_")[0])