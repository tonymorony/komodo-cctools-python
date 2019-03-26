#!/usr/bin/env python3

from lib import tuilib

rpc_connection = tuilib.def_credentials("ROGUE")

players_list = rpc_connection.cclib("players", "17")["playerdata"]

players_tokenids_list = []

for player_txid in players_list:
    players_tokenids_list.append(tuilib.rogue_player_info(rpc_connection, player_txid)["player"]["tokenid"])

for token_txid in players_tokenids_list:
    player_vouts = rpc_connection.getrawtransaction(token_txid, 1)["vout"]
    for vout in player_vouts:
        if vout["value"] == 0:
            print(vout["scriptPubKey"]["hex"])
