#!/usr/bin/env python3

from lib import tuilib

AC_NAME = "BETSTEST"

rpc_connection = tuilib.def_credentials(AC_NAME)

while True:
    # scanning list
    prices_list = rpc_connection.priceslist("open")
    print(tuilib.colorize("Looking for rekts... Current height is: " + str(rpc_connection.getinfo()["blocks"]), "blue"))
    for position in prices_list:
        position_info = rpc_connection.pricesinfo(position)
        if position_info["rekt"] == 1:
            try:
                rekt_raw = rpc_connection.pricesrekt(position, position_info["LastHeight"])["hex"]
                rekt_txid = rpc_connection.sendrawtransaction(rekt_raw)
                print(tuilib.colorize("MUAHAHA REEEEKTED! TXID: " + rekt_txid, "green"))
                print(tuilib.colorize("Position size: " + str(position_info["TotalPositionSize"]), "magenta"))
            except Exception as e:
                print(e)
    # waiting for next block to perform scan again
    prev_scan_height = int(rpc_connection.getinfo()["blocks"])
    while True:
        current_height = int(rpc_connection.getinfo()["blocks"])
        height_difference = current_height - prev_scan_height
        if height_difference == 0:
            # print(current_height)
            # print(prev_scan_height)
            # print(colorize("Waiting for next block before scan for rekts", "blue"))
            pass
        else:
            break
