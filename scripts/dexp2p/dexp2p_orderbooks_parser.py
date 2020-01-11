import json
import os

# loading nodes packages  nodeport[n] : ["id"]["hash"]
package_files_list = os.listdir('spam_p2p/packages')

nodes_packages = {}

for node_port in range(7000, 7010):
    nodes_packages[node_port] = {}
    for file in package_files_list:
        if int(file[4:-13]) == node_port:
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

nodes_orderbooks = {}

for node_port in range(7000, 7010):
    nodes_orderbooks[node_port] = {}
    for file in orderbook_files_list:
        if int(file[4:-13]) == node_port:
            with open('spam_p2p/orderbooks/' + file) as json_file:
                nodes_orderbooks[node_port][file[13:-4]] = json.loads(json_file.read())

# comparing broadcasted packages vs received orderbooks
for nodeport in nodes_packages:
    packages_amount_sent = nodes_packages[nodeport]["total"]
    print("Packages sent by node " + str(nodeport) + " : " + str(packages_amount_sent))
    for nodeport_orderbook in nodes_orderbooks:
        packages_amount_received = nodes_orderbooks[nodeport_orderbook][str(nodeport)]["result"]["n"]
        print("Received by node " + str(nodeport_orderbook) + " " + str(packages_amount_received))
    print("\n")
    print("\n")
