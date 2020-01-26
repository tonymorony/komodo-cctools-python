from pssh.clients import ParallelSSHClient
from pssh.clients import SSHClient
import time

# init params, write down servers IPs below
hosts = []
amount_of_nodes_per_host = 10
spam_duration_seconds = 5

# 1 - Preparing nodes
command = "rm -rf * && wget https://raw.githubusercontent.com/tonymorony/komodo-cctools-python/master/scripts/dexp2p/multi-server/prepare_dexp2p_node_ms.sh " \
          "&& chmod u+x prepare_dexp2p_node_ms.sh && ./prepare_dexp2p_node_ms.sh"

client = ParallelSSHClient(hosts, user="root")
output = client.run_command(command, sudo=True)

for node in output:
    for line in output[node]['stdout']:
        print(line)

# 2 - Preparing "started nodes" file on each server
i = 0
for host in hosts:
    print("Preparing file on node " + str(i+1))
    non_parallel_client = SSHClient(host, user="root")
    if i == 0:
        non_parallel_client.run_command("touch ip_list")
    else:
        line_with_hosts = ""
        for host in hosts[:i]:
            line_with_hosts += host + "\n"
        non_parallel_client.run_command("echo -e " + line_with_hosts + " >> ip_list")
    i = i + 1
print("Test nodes software prepared. Starting network.")

# 3 - Starting network (need to do one by one)
i = 0
for host in hosts:
    print("Starting network on node " + str(i+1))
    non_parallel_client = SSHClient(host, user="root")
    if i == 0:
        is_first_env = "export IS_FIRST=True"
    else:
        is_first_env = "export IS_FIRST=False"
    ip_env = "NODE_IP=" + host
    network_start_command = "export NODESAMOUNT=" + str(amount_of_nodes_per_host) + " && " + is_first_env \
                            + " && " + ip_env + " && " + "python3 clients_spawn_multi_server.py"
    output = non_parallel_client.run_command(network_start_command, sudo=True)
    time.sleep(3 * amount_of_nodes_per_host + 3)
    i = i + 1
print("Network setup completed. Starting to spam.")

# 3 - Starting spam
for host in hosts:
    non_parallel_client = SSHClient(host, user="root")
    output = non_parallel_client.run_command("export NODESAMOUNT=" + str(amount_of_nodes_per_host) + " && ./dexp2p_start_spam_ms.sh " + host + " " + str(spam_duration_seconds), sudo=True)
time.sleep(spam_duration_seconds)

# 4 - Collecting results
print("Spam is finished. Collecting results")
client = ParallelSSHClient(hosts, user="root")
output = client.run_command("export NODESAMOUNT=" + str(amount_of_nodes_per_host) + " && python3 get_stats.py", sudo=True)
for node in output:
    for line in output[node]['stdout']:
        print(line)
