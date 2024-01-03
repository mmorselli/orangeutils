"""
OCN Config for OrangeCLI
License: MIT
"""

import click
import os
import platform
import re
import json
import qrcode
import shutil
from datetime import datetime
from algosdk import account, mnemonic, encoding

VERSION = '0.1 beta'

OCNPATH = os.path.expandvars('%appdata%\\Austs One-Click Node\\')

def intro():
    click.echo("****************************************\n")
    click.echo(f"OCN Config for OrangeCLI - v{VERSION}\n")
    click.echo("****************************************\n")

def lock_ocnconfig():
    with open('.ocnconfig.lock', 'w') as f:
        f.write(f"VERSION = '{VERSION}'\n")

def check_ocnconfig_exists():
    return os.path.isfile('.ocnconfig.lock')

def check_ocn_exists():
    return os.path.isfile(OCNPATH + 'algorand.mainnet.json')

def check_OrangeCLI_exists():
    return os.path.isfile('main.py')

def check_if_windows():
    return platform.system() == 'Windows'


def get_data_dir():
    with open(OCNPATH + 'algorand.mainnet.json', 'r') as f:
        data = json.load(f)
    return data.get('dataDir')


def get_port_number(datadir):
    with open(os.path.join(datadir, 'algod.net'), 'r') as f:
        content = f.read()
    match = re.search(r'\]:([0-9]+)', content)
    if match:
        return int(match.group(1))
    else:
        return None
    
def get_token(datadir):
    with open(os.path.join(datadir, 'algod.token'), 'r') as f:
        content = f.read()
    return content

def create_wallet():
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    return {'mnemonic': passphrase, 'address': address}

def create_qr_code(wallet):
    img = qrcode.make(wallet['mnemonic'])
    img.save(wallet['address']+'.png')
    return os.path.isfile(wallet['address']+'.png')


def get_deposit_address():
    while True:
        address = click.prompt('Please enter the DEPOSIT address (blank to exit)', default='', show_default=False)
        if address == '':
            return False
        elif encoding.is_valid_address(address):
            return address
        else:
            click.echo('Invalid Algorand address. Please try again.')

def get_minimum_balance():
    min_balance = click.prompt('Please enter the minimum balance in ALGO', default=1, type=int, show_default=True)
    return min_balance

def get_tpm():
    tpm = click.prompt('How many transactions per minute?', default=30, type=int, show_default=True)
    return tpm

def get_fee():
    fee = click.prompt('How much fee do you want to pay per transaction?', default=0.02, type=float, show_default=True)
    return fee


def backup_env_file():
    if not os.path.isfile('.env'):
        return
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copy2('.env', f'.env.{timestamp}.backup')


def create_env_file(token, port, minerwallet, deposit, minbalance, tpm, fee):
    minimum_balance = minbalance * 1000000
    content = f"""APP_TESTNET=513940990
ALGOD_TESTNET_SERVER=https://testnet-api.algonode.cloud
ALGOD_TESTNET_TOKEN=
ALGOD_TESTNET_PORT=443

APP_MAINNET=1284326447
ALGOD_MAINNET_SERVER=http://127.0.0.1
ALGOD_MAINNET_TOKEN={token}
ALGOD_MAINNET_PORT={port}

MINER_MNEMONIC={minerwallet['mnemonic']}
MINER_ADDRESS={minerwallet['address']}
MINIMUM_BALANCE_THRESHOLD={minimum_balance}

DEPOSIT_ADDRESS={deposit}
DEPOSIT_MNEMONIC=
"""
    

    click.echo(f"\nPlease verify this data")
    click.echo(f"Miner Wallet (I created it for you): {minerwallet['address']}")
    click.echo(f"Deposit Wallet: {deposit}")
    click.echo(f"Minimum Balance: {minbalance} ALGO")
    click.echo(f"TPM: {tpm}")
    click.echo(f"Fee: {fee}")

    if click.confirm('Do you want to overwrite the .env file with these values?', default=True):
        backup_env_file()
        with open('.env', 'w') as f:
            f.write(content)
        create_juice_bat(tpm, fee)
        return True
    
    return False


def create_juice_bat(tpm, fee):
    microfee = int(fee * 1000000)
    content = f"""@echo off
cd /d %~dp0

if exist main.exe (
    main.exe mainnet --tpm {tpm} --fee {microfee}
) else (
    python main.py mainnet --tpm {tpm} --fee {microfee}
)

PAUSE
"""
    if os.path.exists('juice.bat'):
        os.remove('juice.bat')

    with open('juice.bat', 'w') as f:
        f.write(content)


def system_check():
    if not check_OrangeCLI_exists():
        click.secho("the program must be run in the same folder as OrangeCLI")
        return False
    
    if check_ocnconfig_exists():
        click.secho("please delete the .ocnconfig.lock file to reconfigure\n")
        click.secho("*** WARNING *** : reconfiguring will change the miner wallet")
        return False

    if not check_ocn_exists():
        click.secho("One Click Node not found")
        return False
    
    if not check_if_windows():
        click.secho("this configurator can only be used on Windows systems")
        return False
    
    return True


def create_config():
    if system_check():
        deposit = get_deposit_address()
        if deposit:
            datadir = get_data_dir()
            port = get_port_number(datadir)
            token = get_token(datadir)
            minerwallet = create_wallet()
            minbalance = get_minimum_balance()
            tpm = get_tpm()
            fee = get_fee()
            if create_env_file(token, port, minerwallet, deposit, minbalance, tpm, fee):
                if create_qr_code(minerwallet):
                    click.echo("\n\n*********************\n")
                    click.echo(f"QR Code created as {minerwallet['address']}.png")
                    click.echo("Please scan the QR Code with your phone to save the wallet")
                    click.echo("Remember to send some ALGOs to this wallet")
                    click.echo("for your safety delete the .png after importing it. Your private key is also inside the .env file")
                    click.echo("Use juice.bat to launch your juicer")
                    lock_ocnconfig()
                else:
                    click.echo(f"QR Code creation failed")
            else:
                click.echo(f"Bye, see you next time")

    click.echo("\n")


intro()
create_config()