## OCNCONFIG

ocnconfig is an automatic configurator to connect OrangeCLI to One Click Node, essentially a script to create a One Click Orange

You need to install One Click Node first

https://github.com/AustP/austs-one-click-node

and perform the basic installation, without connecting any wallet, just wait for it to be synchronized. 

The miner comes from 

https://github.com/grzracz/OrangeCLI

where you can download the latest version and use the script from the source. Here, a pre-compiled executable version for Windows is provided for testing purposes.

## Usage

- Start One Click Node and make sure it is synchronized.
- Copy the files to a folder (either a new one or the same as OrangeCLI) and run `ocnconfig.bat`. At the end of the questions, you can run the miner by launching `juice.bat`. The miner wallet is newly created for security reasons (do not enter private keys of your important wallets), and a .png file with the QRCode is generated to easily import it into your mobile wallet.

To change the configuration without creating a new miner wallet (or to change it) do not run the script again, just edit the .env and juice.bat files


## Exe? Is that safe?

The .exe files are the compiled version of Python scripts created using PyInstaller. They contain all the necessary dependencies and the source code. It's important to note that the only sensitive data involved is the miner's private key, which is an empty wallet created on the fly, where it's recommended to store only a few ALGO. If one prefers not to use the .exe files, they can simply follow these steps:

- Delete the .exe files
- Install Python (https://www.python.org/)
- Execute from terminal (cmd or powershell)
  
  `pip install -r requirements.txt`
  `pip install -r ocnrequirements.txt`

- Run ocnconfig.bat, which will then work from from plain and open Python source
