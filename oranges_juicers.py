"""
ORANGES JUICERS ACTIVITY 1.02
"""

from algosdk.v2client import algod
import json
import time
import base64
from algosdk import transaction
from algosdk.transaction import SuggestedParams


# "testnet" or "mainnet"
NETWORK = "mainnet" 
TOKEN = ""
ALGOD_ADDRESS = f"https://{NETWORK}-api.algonode.cloud"
ALGOD_CLIENT = algod.AlgodClient(TOKEN, ALGOD_ADDRESS)


def file_logger(log_file, log):
    with open(log_file, "a") as f:
        f.write(f"{log}\n")
        f.close()


def get_appl_txid(tx):
    genesis_id = "mainnet-v1.0"
    genesis_hash = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="
    txn_dict = tx['txn']
    sp = SuggestedParams(
        fee=txn_dict['fee'],
        first=txn_dict['fv'],
        last=txn_dict['lv'],
        gh=genesis_hash,
        gen=genesis_id,
        flat_fee=True
    )
    txn = transaction.ApplicationNoOpTxn(
        sender=txn_dict['snd'],
        sp=sp,
        index=txn_dict['apid'],
        app_args=[base64.b64decode(a) for a in txn_dict.get('apaa', [])],
        accounts=txn_dict.get('apat', []),
        foreign_assets=txn_dict.get('apas', []),
        note=base64.b64decode(txn_dict.get('note', '')),
    )
    txid = txn.get_txid()
    return txid


def get_axfer_txid(txn_dict):
    genesis_id = "mainnet-v1.0"
    genesis_hash = "wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8="
    sender = txn_dict['snd']
    receiver = txn_dict['arcv']
    amount = txn_dict['aamt']
    index = txn_dict['xaid']

    sp = SuggestedParams(
        fee=0,
        first=txn_dict['fv'],
        last=txn_dict['lv'],
        gh=genesis_hash,
        gen=genesis_id,
        flat_fee=False
    )

    txn = transaction.AssetTransferTxn(
        sender=sender,
        sp=sp, 
        receiver=receiver,
        amt=amount,
        index=index
    )

    return txn.get_txid()


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
    app_id = 1284326447
    orange_address = "ORANGE46RBK7YJRWGGLMMCYJ2NZOJG3WAE2MCRSCK5ZDOJ5RKAZAE5P554"
    winner = None
    winnertxid = None
    effort = 0
    oranges = 0
    unique_snd = set() # set of unique senders
    block_info = ALGOD_CLIENT.block_info(round_num)
    for tx in block_info['block']['txns']:
        if 'apid' in tx['txn'] and tx['txn']['apid'] == app_id:
            if 'dt' in tx and 'itx' in tx['dt'] and 'txn' in tx['dt']['itx'][0] and 'arcv' in tx['dt']['itx'][0]['txn']:
                winner = tx['dt']['itx'][0]['txn']['arcv']
                oranges = orange_count(winner)
                # winnertxid = get_axfer_txid(tx['dt']['itx'][0]['txn'])
                winnertxid = get_appl_txid(tx)
                effort = tx['dt']['gd']['last_miner_effort']['ui']
                file_logger("winners.txt", json.dumps(tx, indent=4)+"\n\n")
            else:
                txcount += 1
                snd = tx['txn']['snd']
                unique_snd.add(snd)
                file_logger("miners.txt", json.dumps(tx, indent=4)+"\n\n")


    return unique_snd, txcount, winner, oranges, winnertxid, effort


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
        unique_snd, txcount, winner, oranges, winnertxid, effort = juicers_in_round(last_round)
        blocknum = f"BLOCK: {last_round} - juicers: {len(unique_snd)} - txcount: {txcount}"
        out +=  blocknum
        if print_juicers:
            juicers = "\n"
            for i, snd in enumerate(unique_snd, start=1):
                juicers += f"{i}) {snd}\n"
            out += juicers
        if winner and print_winners:
            formatted_oranges = "{:,.2f}".format(oranges / 100000000)
            formatted_effort = "{:,.2f}".format(effort / 1000000)
            out += f"\nWinner: {winner} - Effort: {formatted_effort} Balance: {formatted_oranges} ORA - txid: {winnertxid}\n"
        print(out)
        if logtofile:
            file_logger("juicers.txt", out)
        time.sleep(1)



maxround = 20000 # max round to check
print_juicers=False
print_winners=True
round=None # if None, parse from last round
logtofile = True

parse_juicers(maxround, print_juicers, print_winners, round, logtofile)

