#!/usr/bin/env python3
# Usage: $./find_uuids_by_addr.py  address  path_to_jsons
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


def find_uuids_by_addr(dirpath, address):
    """Returns list with all swaps(uuids) made to/from address"""
    jflist = get_files_in_directory(dirpath)
    dicts = json_files_loader(jflist)
    swaps_list = []
    for d in dicts:
        swap_uuid = d.get('uuid')
        print('.. checking ' + swap_uuid)
        events = d.get('events')
        for event in events:
            try:
                from_field = event.get('event').get('data').get('from')
                if address in from_field:
                    swaps_list.append(swap_uuid)
                    break
                to_field = event.get('event').get('data').get('to')
                if address in to_field:
                    swaps_list.append(swap_uuid)
                    break
            except Exception as e:
                pass
    return swaps_list


def main():
    """Prints all swaps(uuids) made to/from address if any"""
    try:
        address = sys.argv[1]
        try:
            path = sys.argv[2]
            swaps = find_uuids_by_addr(path, address)
            if swaps:
                print("\nfound in swaps : " + str(swaps))
            else:
                print("\n" + address + " not found")
        except Exception as e:
            print("Error: " + str(e))
    except Exception as e:
        print(e)
        print("Usage: ./find_uuids_by_addr.py address path_to_jsons")


if __name__ == '__main__':
    main()
