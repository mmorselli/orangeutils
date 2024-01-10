"""
ORANGES JUICERS ACTIVITY 1.02
"""

from algosdk import encoding
from algosdk.v2client import algod
import json
import time
import hashlib
import base64
from algosdk import transaction
from algosdk.transaction import ApplicationNoOpTxn, LogicSig, SuggestedParams
import os



# "testnet" or "mainnet"
NETWORK = "mainnet" 

ALGOD_ADDRESS = f"https://{NETWORK}-api.algonode.cloud"
TOKEN = ""
ALGOD_CLIENT = algod.AlgodClient(TOKEN, ALGOD_ADDRESS)

app_id = 1284326447

# Get the latest application information
app_info = ALGOD_CLIENT.application_info(app_id)

# Get the address associated with the application
app_address = app_info['params']['creator']


def file_logger(log_file, log):
    with open(log_file, "a") as f:
        f.write(f"{log}\n")
        f.close()




def get_txid(tx):
    genesis_id = "mainnet-v1.0"
    genesis_hash = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="
    txn_dict = tx['txn']
    sender=txn_dict['snd']
    sp = SuggestedParams(
        fee=txn_dict['fee'],
        first=txn_dict['fv'],
        last=txn_dict['lv'],
        gh=genesis_hash,
        gen=genesis_id,
        flat_fee=True
    )
    note=base64.b64decode(txn_dict.get('note', ''))
    index=txn_dict['apid']
    app_args=[base64.b64decode(a) for a in txn_dict.get('apaa', [])]
    accounts=txn_dict.get('apat', [])
    foreign_assets=txn_dict.get('apas', [])
    note=base64.b64decode(txn_dict.get('note', ''))
    txn = transaction.ApplicationNoOpTxn(
        sender=sender,
        sp=sp,
        index=index,
        app_args=app_args,
        accounts=accounts,
        foreign_assets=foreign_assets,
        note=note,
    )
    txid = txn.get_txid()
    return txid



def orange_count(address):
    # Get the account information
    account_info = ALGOD_CLIENT.account_info(address)

    # Get the asset balance
    asset_id = 1284444444
    asset_balance = 0
    if 'assets' in account_info:
        for asset in account_info['assets']:
            if asset['asset-id'] == asset_id:
                asset_balance = asset['amount']
                break

    return asset_balance

# algod stores only the last 1000 blocks
def juicers_in_round(round_num):
    txcount = 0
    juicers = ""
    winner = None
    winnertxid = None
    oranges = 0
    unique_snd = set() # set of unique senders
    block_info = ALGOD_CLIENT.block_info(round_num)
    # file_logger("blocks.txt", json.dumps(block_info, indent=4))
    for tx in block_info['block']['txns']:
        # print(json.dumps(tx, indent=4))
        if 'apid' in tx['txn'] and tx['txn']['apid'] == app_id:
            if tx['txn']['snd'] != 'ORANGE46RBK7YJRWGGLMMCYJ2NZOJG3WAE2MCRSCK5ZDOJ5RKAZAE5P554':
                txcount += 1
                snd = tx['txn']['snd']
                unique_snd.add(snd)
            else:
                winner = tx['txn']['apat'][0]
                oranges = orange_count(winner)
                winnertxid = get_txid(tx)
                # print(json.dumps(tx, indent=4))

    return unique_snd, txcount, winner, oranges, winnertxid


def parse_juicers(maxround=50, print_juicers=True, print_winners=True, round=None, logtofile=False):
    roundparsed = 0
    previous_round = None
    roundcount = 0
    while roundparsed < maxround:
        
        out=""
        # parse from last round or from the round specified
        if round is not None:
            last_round = round + roundcount
            roundcount += 1
        else:
            last_round = ALGOD_CLIENT.status()['last-round']
        
        if last_round == previous_round:
            continue
        previous_round = last_round
        roundparsed += 1
        unique_snd, txcount, winner, oranges, winnertxid = juicers_in_round(last_round)
        blocknum = f"BLOCK: {last_round} - juicers: {len(unique_snd)} - txcount: {txcount}"
        out +=  blocknum
        if print_juicers:
            juicers = "\n"
            for i, snd in enumerate(unique_snd, start=1):
                juicers += f"{i}) {snd}\n"
            out += juicers
        if winner and print_winners:
            formatted_oranges = "{:,.2f}".format(oranges / 100000000)
            out += f"\nWinner: {winner} - Balance: {formatted_oranges} ORA - txid: {winnertxid}\n"
        print(out)
        if logtofile:
            file_logger("juicers.txt", out)
        time.sleep(1)



maxround = 20 # max round to check
print_juicers=False
print_winners=True
round=None # if None, parse from last round
logtofile = True

parse_juicers(maxround, print_juicers, print_winners, round, logtofile)

