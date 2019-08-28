#!/usr/bin/env python3

from lib import tuilib


rpc_connection_ac = tuilib.def_credentials("ROGUE")

games_list = rpc_connection_ac.cclib("games", "17")

pastgames_list = games_list["pastgames"]

activegames_list = games_list["games"]


print(tuilib.colorize("\n*** Pastgames *** \n", "blue"))
print("TXID                                  SEED")
for game in pastgames_list:
    pastgame_info = tuilib.rogue_game_info(rpc_connection_ac, game)
    print(game + "                                  " + str(pastgame_info["seed"]))



print(tuilib.colorize("\n*** Active games *** \n", "blue"))
print("TXID                                  SEED")
for game in activegames_list:
    activegame_info = tuilib.rogue_game_info(rpc_connection_ac, game)
    print(game + "                                  " + str(activegame_info["seed"]))
