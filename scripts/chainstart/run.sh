#!/bin/bash

# chains start script params
export CLIENTS=2
export CHAIN="TICKER"
export TEST_ADDY0="example_address1"
export TEST_WIF0="example_wif1"
export TEST_PUBKEY0="example_pub1"
export TEST_ADDY1="example_address2"
export TEST_WIF1="example_wif2"
export TEST_PUBKEY1="example_pub2"
export CHAIN_MODE="REGULAR"
export IS_BOOTSTRAP_NEEDED="True"
export BOOTSTRAP_URL=""
export BINARYPATH=$HOME/komodo/src/komodod

# starting the chains
python3 chainstart.py
