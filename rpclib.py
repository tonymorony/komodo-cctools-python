from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import http


# RPC connection
def rpc_connect(rpc_user, rpc_password, port):
    try:
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:%d"%(rpc_user, rpc_password, port))
    except (http.client.CannotSendRequest, http.client.RemoteDisconnected, ConnectionRefusedError, OSError):
        raise Exception("Connection error! Probably no daemon on selected port.")
    return rpc_connection


# Non CC calls
def getinfo(rpc_connection):

    try:
        getinfo = rpc_connection.getinfo()
    except (http.client.RemoteDisconnected, ConnectionRefusedError, OSError):
        raise Exception("Connection error!")
    return getinfo


def sendrawtransaction(rpc_connection, hex):
    tx_id = rpc_connection.sendrawtransaction(hex)
    return tx_id


# Token CC calls
def token_create(rpc_connection, name, supply, description):
    token_hex = rpc_connection.tokencreate(name, supply, description)
    return token_hex


def token_list(rpc_connection):
    token_list = rpc_connection.tokenlist()
    return token_list


def token_convert(rpc_connection, evalcode, token_id, pubkey, supply):
    token_convert_hex = rpc_connection(evalcode, token_id, pubkey, supply)
    return token_convert_hex


# Oracle CC calls
def oracles_create(rpc_connection, name, description, data_type):
    oracles_hex = rpc_connection.oraclescreate(name, description, data_type)
    return oracles_hex


def oracles_register(rpc_connection, oracle_id, data_fee):
    oracles_register_hex = rpc_connection.oraclesregister(oracle_id, data_fee)
    return oracles_register_hex


def oracles_subscribe(rpc_connection, oracle_id, publisher_id, data_fee):
    oracles_subscribe_hex = rpc_connection.oraclessubscribe(oracle_id, publisher_id, data_fee)
    return oracles_subscribe_hex


# Gateways CC calls
def gateways_bind(rpc_connection, token_id, oracle_id, coin_name, token_supply, M, N, pubkeys):
    gateways_bind_hex = rpc_connection.gatewaysbind(token_id, oracle_id, coin_name,\
                                                    token_supply, M, N, pubkeys)
    return gateways_bind_hex


def gateways_deposit(rpc_connection, gateway_id, height, coin_name,\
                     coin_txid, claim_vout, deposit_hex, proof, dest_pub, amount):
    gateways_deposit_hex = rpc_connection.gatewaysdeposit(gateway_id, height, coin_name,\
                     coin_txid, claim_vout, deposit_hex, proof, dest_pub, amount)
    return gateways_deposit_hex


def gateways_claim(rpc_connection, gateway_id, coin_name, deposit_txid, dest_pub, amount):
    gateways_claim_hex = rpc_connection.gatewaysclaim(gateway_id, coin_name, deposit_txid, dest_pub, amount)
    return gateways_claim_hex


def gateways_withdraw(rpc_connection, gateway_id, coin_name, withdraw_pub, amount):
    gateways_withdraw_hex = rpc_connection(gateway_id, coin_name, withdraw_pub, amount)
    return gateways_withdraw_hex