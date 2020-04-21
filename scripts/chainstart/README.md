Script starts X komodo nodes locally, usage is simple:
`./run.sh`

Depends on:
```
python 3.6+

pip install wheel \
            setuptools \
            pycurl \
            ujson \
            slick-bitcoinrpc \
            wget

Or:

pip install -r requirements.txt
```

Nodes configuration with ENV vars:

note: ENV vars are exported in run.sh script, you can set variables separately and start nodes after with `python3 chainstart.py` 

`CLIENTS` - amount of nodes to start, for each node following vars should be set:

`TEST_ADDYN` - nodes address
`TEST_WIFN` - wif to be imported on startup
`TEST_PUBKEYN` - pubkey, will be used as start parameter `-pubkey=`
Here `N` is node number, starting from 0

`CHAIN_MODE` - set mode, available:
REGULAR - normal chain start
DEX1 - appends -dexp2p=1 to start args
DEX2 - appends -dexp2p=2
REGETST - appends -regtest

`IS_BOOTSTRAP_NEEDED` - Ture or False
If bootstrap param set to True script will look for bootstrap.tar.gz file in local directory, or bootstrap url set in following variable:
`BOOTSTRAP_URL` - url to download bootstrap from if IS_BOOTSTRAP_NEEDED is True

`BINARYPATH` - path to `komodod[.exe]` binary, defaults to ../../src/komodod if not set

`CHAIN` - chain to start
CHAIN should be set in `chainconfig.json`, similair to komodo's assetchains.json
Example:
```json
{ 
    "RICK": {
        "ac_supply": "90000000000",
        "ac_reward": "100000000",
        "ac_cc": "3",
        "ac_staked": "10",
        "ac_name": "RICK",
        "addnode": "138.201.136.145",
        "rpc_user": "ricktest",
        "rpcpassword": "ricktest",
        "rpcallowip": "0.0.0.0/0",
        "rpcport": 7000,
        "rpcbind": "0.0.0.0"
    },
    "MORTY": {
        "ac_supply": "90000000000",
        "ac_reward": "100000000",
        "ac_name": "MORTY",
        "ac_cc": "3",
        "ac_staked": "10",
        "rpc_user": "mortytest",
        "addnode": "95.217.44.58",
        "rpcpassword": "mortytest",
        "rpcallowip": "0.0.0.0/0",
        "rpcport": 7000,
        "rpcbind": "0.0.0.0"
    }
}
```

Values `"rpc_user", "rpcpassword", "rpcallowip", "rpcport", "rpcbind"` will be set in CHAIN.conf

Configuration files, blocks, .dats, etc are located in ./node_N directory.
Easy way to use komodo-cli with started nodes is to pass -conf= with rpc call, example:
`/komodo-clii -conf=$HOME/scripts/node_0/RICK.conf getinfo`
