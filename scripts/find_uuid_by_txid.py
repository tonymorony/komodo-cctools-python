#!/usr/bin/env python3
# Usage: $./find_uuid_by_txid.py  txid  path_to_jsons
# Where txid - transaction included in desired swap
# path_to_jsons - path to swaps json directory
import os
import json
import sys


def get_files_in_directory(dirpath):
    files = [f for f in os.listdir(dirpath) if os.path.isfile(f)]
    return files


def json_files_loader(jsons_list):  # jsons_list - list of files to read
    dicts_list = []
    for json_file in jsons_list:
        if ".json" in json_file:
            with open(json_file, 'r') as f:
                fstring = (f.read()).encode('utf-8').strip()
                jsf = json.loads(fstring)
            dicts_list.append(jsf)
    return dicts_list


def find_uuid_by_txhash(dirpath, txhash):
    jflist = get_files_in_directory(dirpath)
    dicts = json_files_loader(jflist)
    for d in dicts:
        swap_uuid = d.get('uuid')
        print('.. checking ' + swap_uuid)
        events = d.get('events')
        for event in events:
            try:
                tx = event.get('event').get('data').get('tx_hash')
                if tx == txhash:
                    return swap_uuid
                else:
                    pass
            except Exception as e:
                pass


def main():
    """Prints first swap uuid found by txhash, if any"""
    try:
        txhash = sys.argv[1]
        try:
            path = sys.argv[2]
            uuid = find_uuid_by_txhash(path, txhash)
            if uuid:
                print("\ntx found in swap : " + str(uuid))
            else:
                print("\n" + txhash + " not found")
        except Exception as e:
            print("Error: " + str(e))
    except Exception as e:
        print(e)
        print("Usage: ./find_uuid_by_txid.py txid path_to_jsons")


if __name__ == '__main__':
    main()
