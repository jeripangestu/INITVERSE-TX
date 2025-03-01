import logging
from web3 import Web3
from eth_account import Account
import asyncio
from headers import headers
from playwright.async_api import async_playwright
import json
from rich.console import Console
from rich.table import Table
from rich import box
import gc

# Initialize rich console
console = Console()

# Define colors and symbols
SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
INFO_COLOR = "blue"

SUCCESS_SYMBOL = "✅"
ERROR_SYMBOL = "❌"
WARNING_SYMBOL = "⚠️"
INFO_SYMBOL = "ℹ️"

try:
    # Load data from the JSON file
    with open('config.json', "r") as file:
        data = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"config.json file does not exist. Create one")
except json.JSONDecodeError:
    raise ValueError(f"The config file is not a valid JSON file.")

# Extract values from config
private_keys = data['private_keys']
timeout_after_trades = data['timeout_after_trades']
timeout_within_trades = data['timeout_within_trades']
send_amount = data['send_amount']

RPC_URL = 'http://rpc-mainnet.inichain.com'
BASE_URL = 'https://candyapi-mainnet.inichain.com/airdrop/api/v1'

web3 = Web3(Web3.HTTPProvider(RPC_URL))


def short_address(wallet_address):
    address = f"{''.join(wallet_address[:5])}..{''.join(wallet_address[-5:])}"
    return address


def generate_new_eth_address():
    # Generate a new Ethereum account
    account = Account.create()
    # Return the address and private key
    return account.address


def send_testnet_eth(private_key: str, receiver_address: str, amount_in_ether: float, retries: int = 3):
    """
    Sends testnet ETH with retries, increasing gas price by 10% for each retry if sending fails.

    :param private_key: Sender's private key as a string
    :param receiver_address: Receiver's wallet address as a string
    :param amount_in_ether: Amount to send in Ether
    :param retries: Number of retries (default: 3)
    :return: Transaction hash as a string if successful
    """
    sender_address = web3.eth.account.from_key(private_key).address
    amount_in_wei = web3.to_wei(amount_in_ether, 'ether')

    nonce = web3.eth.get_transaction_count(sender_address, 'pending')
    gas_price = web3.eth.gas_price  # Fetch the current gas price

    for attempt in range(1, retries + 1):
        try:
            # Build the transaction
            transaction = {
                'to': receiver_address,
                'value': amount_in_wei,
                'gas': 21000,
                'gasPrice': int(gas_price * 1.5),
                'nonce': nonce,
                'chainId': web3.eth.chain_id
            }

            # Sign and send the transaction
            signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for transaction receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)

            if receipt['status'] == 1:
                log_table("SUCCESS", f"Account {short_address(sender_address)}: Transferred {amount_in_ether} INI to {receiver_address} successfully!", SUCCESS_COLOR, SUCCESS_SYMBOL)
                return tx_hash.hex()  # Return transaction hash if successful
            else:
                raise Exception(f"Account {short_address(sender_address)}: Transaction failed")

        except Exception as e:
            log_table("ERROR", f"Account {short_address(sender_address)}: Transaction failed ({attempt}) with error: {str(e)}", ERROR_COLOR, ERROR_SYMBOL)

            if attempt < retries:
                gas_price = int(gas_price * 1.5)  # Increase gas price by 50% for the next attempt
                log_table("WARNING", f"Account {short_address(sender_address)}: Increasing gas price and retrying ({attempt + 1})...", WARNING_COLOR, WARNING_SYMBOL)
            else:
                log_table("ERROR", f"Account {short_address(sender_address)}: Max retries reached. Token send failed.", ERROR_COLOR, ERROR_SYMBOL)
                raise e  # Re-raise the exception if retries are exhausted


def log_table(log_type, message, color, symbol):
    """
    Log messages in a table format with colors and symbols.
    """
    table = Table(show_header=False, box=box.ROUNDED, style=color, border_style=color)
    table.add_row(f"{symbol} {log_type}", message)
    console.print(table)


async def requests_via_playwright(url, wallet_address):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Set headers
        headers['address'] = wallet_address
        await page.set_extra_http_headers(headers)

        response = await page.goto(url)

        if response.status == 200:
            body = await response.body()
            data = json.loads(body)
            data = data['data']
            await browser.close()
            return data
        else:
            text = await response.text()
            await browser.close()
            raise Exception(f"Possible Cloudflare blockade")


async def list_tasks(wallet_address):
    url = f"{BASE_URL}/task/list?address={wallet_address}"
    response_data = await requests_via_playwright(url, wallet_address)
    return response_data


async def get_user_info(wallet_address):
    url = f'{BASE_URL}/user/userInfo?address={wallet_address}'
    response_data = await requests_via_playwright(url, wallet_address)
    return response_data


async def get_points_trades(wallet_address):
    # get trades
    list_tasks_data = await list_tasks(wallet_address)
    day_trading_count = int(list_tasks_data['dayTradingCount'])
    trades = list_tasks_data['tasks']['dailyTask'][0]['tag']
    trade_count = int(trades.split('/')[0])
    trade_left = day_trading_count - trade_count

    # points
    points = await get_user_info(wallet_address)
    points = points['points']

    return trade_left, trade_count, points


async def send_tokens(private_key, private_keys):
    wallet_address = web3.eth.account.from_key(private_key).address
    abridged_address = short_address(wallet_address)
    other_private_keys = [pk for pk in private_keys if pk != private_key]  # Exclude self

    try:
        trade_left, trade_count, points = await get_points_trades(wallet_address)
        log_table("INFO", f"Account {abridged_address}: Trades {trade_count}. Points {points}", INFO_COLOR, INFO_SYMBOL)

        for _ in range(trade_left):
            if not other_private_keys:
                log_table("WARNING", f"Account {abridged_address}: No other private keys available for sending tokens.", WARNING_COLOR, WARNING_SYMBOL)
                break

            # Select a random private key from the list (excluding self)
            receiver_private_key = other_private_keys[_ % len(other_private_keys)]
            receiver_address = web3.eth.account.from_key(receiver_private_key).address

            try:
                log_table("INFO", f"Account {abridged_address}: Prepping to send tokens to {short_address(receiver_address)}...", INFO_COLOR, INFO_SYMBOL)
                tx = send_testnet_eth(private_key, receiver_address, send_amount)
                log_table("SUCCESS", f"Account {abridged_address}: Send Token Successful! Tx Hash: {tx}", SUCCESS_COLOR, SUCCESS_SYMBOL)
                await asyncio.sleep(timeout_within_trades)

            except Exception as e:
                log_table("ERROR", f"Account {abridged_address}: Error when sending token \n{e}", ERROR_COLOR, ERROR_SYMBOL)
                await asyncio.sleep(30)

        trades, trade_count, points = await get_points_trades(wallet_address)
        log_table("INFO", f"Account {abridged_address}: Trading complete. Trades ({trade_count}/10). Points {points}", INFO_COLOR, INFO_SYMBOL)
        # Hapus sleep setelah selesai
        # await asyncio.sleep(60 * 60 * timeout_after_trades)  # Hapus baris ini

    except Exception as e:
        log_table("ERROR", f"Account {abridged_address}: Error during trades. {e}. Restarting", ERROR_COLOR, ERROR_SYMBOL)
    finally:
        # Bersihkan resource
        gc.collect()


# Run tasks for all private keys sequentially
async def run_all(private_keys: list):
    for private_key in private_keys:
        await send_tokens(private_key, private_keys)


if __name__ == "__main__":
    asyncio.run(run_all(private_keys))