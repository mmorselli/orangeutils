"""
ORANGES JUICERS ACTIVITY 1.01
"""

from algosdk.v2client import algod
import json
import time


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
    count = 0
    juicers = ""
    winner = None
    oranges = 0
    unique_snd = set() # set of unique senders
    block_info = ALGOD_CLIENT.block_info(round_num)
    for tx in block_info['block']['txns']:
        # print(json.dumps(tx, indent=4))
        if 'apid' in tx['txn'] and tx['txn']['apid'] == app_id:
            if tx['txn']['snd'] != 'ORANGE46RBK7YJRWGGLMMCYJ2NZOJG3WAE2MCRSCK5ZDOJ5RKAZAE5P554':
                count += 1
                snd = tx['txn']['snd']
                unique_snd.add(snd)
            else:
                winner = tx['txn']['apat'][0]
                oranges = orange_count(winner)
    juicers += f"Number of transactions: {count}\n"
    juicers += f"Juicers: {len(unique_snd)}\n"
    for i, snd in enumerate(unique_snd, start=1):
        juicers += f"{i}) {snd}\n"

    return juicers, winner, oranges


def parse_juicers(maxround, print_juicers=True, print_winner=True):
    roundparsed = 0
    previous_round = None
    while roundparsed < maxround:
        last_round = ALGOD_CLIENT.status()['last-round']
        if last_round == previous_round:
            continue
        previous_round = last_round
        roundparsed += 1
        blocknum = f"BLOCK: {last_round}"
        juicers, winner, oranges = juicers_in_round(last_round)
        print(blocknum)
        if print_juicers:
            print(juicers)
        if winner and print_winner:
            formatted_oranges = "{:,.2f}".format(oranges / 100000000)
            print(f"Winner: {winner} (Balance: {formatted_oranges} ORA)")
        time.sleep(1)



maxround = 50 # max round to check
print_juicers=True
print_winner=True

parse_juicers(maxround, print_juicers, print_winner)