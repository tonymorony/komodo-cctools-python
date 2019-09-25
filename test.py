#!/usr/bin/env python3

from lib import rpclib, tuilib

rpc = tuilib.rpc_connection_tui()
print(rpc.getinfo())