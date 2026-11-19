import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.apihelper import ApiTelegramException
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from threading import Thread
from web3 import Web3
import threading
import logging
import requests
import random
import time
import os
import re
# Token của bot (Thay bằng token thật của bạn)
BOT_TOKEN = "API_TOKEN_BOT"
bot = telebot.TeleBot(BOT_TOKEN)

# Lấy thông tin của bot
bot_info = bot.get_me()
bot_username = bot_info.username


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

mining_data = {}

# Quản lý dữ liệu người dùng
class User:
    data = {}
    

    @staticmethod
    def getData(key, user=None):
        if user is None:
            user = "global"
        return User.data.get(user, {}).get(key, None)

    @staticmethod
    def saveData(key, value, user=None):
        if user is None:
            user = "global"
        if user not in User.data:
            User.data[user] = {}
        User.data[user][key] = value

    @staticmethod
    def getAllData(field):
        # Lấy toàn bộ dữ liệu của field từ tất cả người dùng
        return {user: data.get(field) for user, data in User.data.items() if field in data}

    # Phương thức khởi tạo dữ liệu mining cho người dùng
      

# Quản lý dữ liệu bot
class Bot:
    data = {}
    next_command = {}

    @staticmethod
    def getData(key):
        return Bot.data.get(key, None)

    @staticmethod
    def saveData(key, data):
        Bot.data[key] = data

    @staticmethod
    def handleNextCommand(command, user_id):
        if user_id not in User.data:
            User.data[user_id] = {}
        User.data[user_id]['next_command'] = command

    @staticmethod
    def getNextCommand(user_id):
        return User.data.get(user_id, {}).get('next_command', None)


previous_data = {
    "bnb_price": None,
    "total_users": None,
    "total_transactions": None,
    "total_airdrop": None,
    "total_holders": None,
    "total_fee": None,
    "current_gas_gwei": None,
    "current_gas_price": None,
    "current_gas_usd": None,
    "total_fee_usd": None,
    "total_distributed_airdrop": None,
    "total_mined_tokens": None,
    "global_total_blocks": None,
    "total_hashrate": None,

}

updating = True
reduction_message = None
time.blocks = 600
captcha_store = {}

# Constants
MAX_BLOCKS_PER_DAY = 1_440  # Giới hạn số block khai thác mỗi ngày
MAX_BLOCKS_PER_YEAR = 3 #Tổng số block khai thác trong 1 năm


RPC_URL = 'https://data-seed-prebsc-1-s1.bnbchain.org:8545' # RPC Chain
# Địa chỉ hợp đồng và ABI
contract_address = '0xC7d07B5B64c98472d3EA44320aC86bf70d54e260'
abi = '[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"TokensBurned","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"TokensMinted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burnFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"burningPaused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getTotalFeesPaid","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getTotalHold","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getTotalHolders","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getTotalTransactions","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mintTo","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"mintingPaused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"toggleBurning","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"toggleMinting","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalFeesPaid","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalHold","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalHolders","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalTransactions","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'

# Khởi tạo web3 và hợp đồng
web3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = web3.eth.contract(address=contract_address, abi=abi)


bot_private_key = 'PRIVATE_BOT_WALLET'
wallet_airdrop_bot = Web3.to_checksum_address(
    '0xf67c04cf98fcc4d4d04f032e415551b11235cc23')

# Thiết lập Web3
w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.bnbchain.org:8545'))

# Địa chỉ hợp đồng và ABI của hợp đồng
contract_address = '0xC7d07B5B64c98472d3EA44320aC86bf70d54e260'
contract_abi = [{"inputs": [],"payable": False,"stateMutability": "nonpayable","type": "constructor"}, {"constant":False,"inputs": [{"internalType": "address","name": "recipient","type": "address"}, {"internalType": "uint256","name": "amount", "type": "uint256"}], "name": "transfer", "outputs": [{ "internalType": "bool", "name": "", "type": "bool" }],"payable": False, "stateMutability": "nonpayable", "type": "function"}, { "constant": True, "inputs": [{ "internalType": "address", "name": "account","type": "address"}], "name": "balanceOf", "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256"}], "payable":False, "stateMutability": "view", "type": "function" }, { "constant": True, "inputs": [], "name": "getTotalFeesPaid", "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function" }, { "constant": True, "inputs": [], "name": "getTotalHolders", "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function" }, { "constant": True, "inputs": [], "name": "getTotalTransactions", "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }], "payable": False, "stateMutability": "view", "type": "function"}]

contract =  w3.eth.contract(address=contract_address, abi= contract_abi)


def get_wallet_balance(wallet_address):
    try:
        # Chuyển đổi địa chỉ sang dạng checksum
        checksum_address = Web3.to_checksum_address(wallet_address)

        # Kiểm tra kết nối
        if not w3.is_connected():
            print("Không thể kết nối với BSC Testnet")
            return None

        # Lấy số dư
        balance = contract.functions.balanceOf(checksum_address).call()
        return balance
    except Exception as e:
        print(f"Error getting wallet balance: {e}")
        return None


def transfer_tokens(bot_wallet, user_wallet, amount):
    try:
        # Chuyển đổi địa chỉ sang dạng checksum
        bot_wallet = Web3.to_checksum_address(bot_wallet)
        user_wallet = Web3.to_checksum_address(user_wallet)

        print(f"Transferring {amount} from {bot_wallet} to {user_wallet}")  # In ra thông tin giao dịch

        # Kiểm tra kết nối
        if not w3.is_connected():
            print("Không thể kết nối với BSC Testnet")
            return None

        # Chuyển đổi số tiền sang uint256
        amount_in_wei = int(amount)

        # Tạo giao dịch
        nonce = w3.eth.get_transaction_count(bot_wallet)

        # Tạo transaction
        transaction = contract.functions.transfer(
            user_wallet, amount_in_wei).build_transaction({
                'chainId': 97,  # BSC Testnet
                'gas': 47000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })

        # Ký giao dịch
        signed_txn = w3.eth.account.sign_transaction(transaction, bot_private_key)

        # Gửi giao dịch
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)  # Sử dụng rawTransaction.hex()

        # Đợi giao dịch được xác nhận
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return w3.to_hex(tx_hash)
    except Exception as e:
        print(f"Transaction failed: {e}")
        return None


def get_total_fees_paid(contract_address):
    # Gọi API để lấy tổng phí từ hợp đồng
    url = f"https://api-testnet.bscscan.com/api?module=stats&action=tokeninfo&contractaddress={contract_address}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == '1':
        # Lấy tổng phí từ dữ liệu trả về
        total_fees = float(
            data['result']
            ['totalFees'])  # Thay đổi theo cấu trúc dữ liệu thực tế
        return total_fees  # Trả về tổng phí đã lấy từ API

    # Nếu không lấy được từ API, gọi hàm từ smart contract
    try:
        return contract.functions.getTotalFeesPaid().call() / (10**18)
    except Exception as e:
        logger.error(f"Error getting total fees from contract: {e}")
        return None  # Hoặc xử lý lỗi nếu cần


def get_total_holders(contract_address):
    # Gọi API để lấy thông tin tổng số lượng ví nắm giữ
    url = f"https://api-testnet.bscscan.com/api?module=stats&action=tokeninfo&contractaddress={contract_address}"
    response = requests.get(url)
    data = response.json()

    if data['status'] == '1':
        # Lấy tổng số lượng ví nắm giữ từ dữ liệu trả về
        total_holders = int(
            data['result']
            ['totalHolders'])  # Thay đổi theo cấu trúc dữ liệu thực tế
        return total_holders  # Trả về tổng số lượng ví đã lấy từ API

    # Nếu không lấy được từ API, gọi hàm từ smart contract
    try:
        return contract.functions.getTotalHolders().call()
    except Exception as e:
        logger.error(f"Error getting total holders from contract: {e}")
        return None  # Hoặc xử lý lỗi nếu cần


def get_total_transactions(contract_address):
    # Gọi API để lấy tổng số giao dịch từ hợp đồng
    url = f"https://api-testnet.bscscan.com/api?module=account&action=txlist&address={contract_address}&startblock=0&endblock=99999999&sort=asc"
    response = requests.get(url)
    data = response.json()

    if data['status'] == '1':
        total_transactions = len(data['result'])  # Số lượng giao dịch
        return total_transactions  # Trả về tổng số giao dịch đã lấy từ API

    # Nếu không lấy được từ API, gọi hàm từ smart contract
    try:
        return contract.functions.getTotalTransactions().call()
    except Exception as e:
        logger.error(f"Error getting total transactions from contract: {e}")
        return None  # Hoặc xử lý lỗi nếu cần


def get_current_gas_gwei():
    # Gọi RPC để lấy giá gas hiện tại từ BSC Testnet
    url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # Nút RPC cho BSC Testnet
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_gasPrice",
        "params": [],
        "id": 1
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if 'result' in data:
            # Chuyển đổi giá gas từ wei sang BNB
            gas_price_wei = int(data['result'],
                                16)  # Chuyển đổi từ hex sang int
            gas_price_bnb = gas_price_wei / (
                10**9)  # Chia cho 10^18 để chuyển đổi sang BNB
            return gas_price_bnb  # Trả về giá gas hiện tại
        else:
            logger.error(
                f"Error fetching gas price: {data.get('error', 'Unknown error')}"
            )
            return None  # Hoặc xử lý lỗi nếu cần
    except Exception as e:
        logger.error(f"Exception occurred while fetching gas price: {e}")
        return None  # Hoặc xử lý lỗi nếu cần


def get_gas_fee():
    """
    Lấy giá gas hiện tại và tính toán gas fee trên mạng BSC Testnet.

    :param gas_limit: Gas limit của giao dịch.
    :return: Từ điển chứa giá gas hiện tại (BNB) và gas fee (BNB).
    """
    url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # Nút RPC cho BSC Testnet
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_gasPrice",
        "params": [],
        "id": 1
    }

    try:
        # Gửi yêu cầu tới RPC
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if 'result' in data:
            gas_limit = int(data['result'], 16)
            # Chuyển đổi giá gas từ hex sang wei
            gas_price_wei = int(data['result'], 16)

            # Tính toán giá gas (BNB)
            gas_price_bnb = gas_price_wei / (10 ** 18)

            # Tính toán gas fee (BNB)
            gas_fee_bnb = gas_price_bnb * gas_limit

            # Trả về giá gas và gas fee
            return {
                "gas_price_bnb": gas_price_bnb,
                "gas_fee_bnb": gas_fee_bnb
            }
        else:
            logger.error(f"Error fetching gas price: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching gas price: {e}")
        return None  # Hoặc xử lý lỗi nếu cần


def get_gas_limit(web3, data=None, value=0):
    """
    Lấy Gas Limit ước lượng trên BNB Testnet.
    Không yêu cầu from_address hoặc to_address.
    """
    try:
        # Thông tin cơ bản của giao dịch
        txn = {
            "to": None,  # Bạn có thể để None nếu không cần chỉ định to_address
            "value": value,  # Giá trị giao dịch (Wei)
            "data": data or b"",  # Dữ liệu giao dịch (mặc định rỗng)
        }

        # Ước tính Gas Limit
        gas_limit = web3.eth.estimate_gas(txn)
        return gas_limit
    except Exception as e:
        print(f"Lỗi khi ước tính Gas Limit: {e}")
        return None

def get_bnb_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"  # Lấy giá BNB/USDT từ Binance
    
    try:
        response = requests.get(url)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            data = response.json()
            if 'price' in data:
                return float(data['price'])  # Trả về giá BNB (USDT)
            else:
                logger.error(f"Error fetching BNB price: 'price' key missing.")
                return None
        else:
            logger.error(f"Error fetching BNB price: HTTP status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception occurred while fetching BNB price: {e}")
        return None
    except Exception as e:
        logger.error(f"Exception occurred while fetching BNB price: {e}")
        return None


def get_xaut_price():
    url = "https://www.okx.com/api/v5/market/ticker?instId=XAUT-USDT"  # API lấy giá XAUT từ OKX
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                return float(data["data"][0]["last"])  # Lấy giá từ trường 'last'
            else:
                logger.error(f"Error fetching XAUT price: 'data' key missing or empty.")
                return None
        else:
            logger.error(f"Error fetching XAUT price: HTTP status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception while fetching XAUT price: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching XAUT price: {e}")
        return None

def get_usdt_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "tether",  # Tether (USDT)
        "vs_currencies": "usd"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "tether" in data and "usd" in data["tether"]:
            return float(data["tether"]["usd"])
        else:
            print("Error: VNDC data not found.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def get_vndc_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "vndc",  # Tether (USDT)
        "vs_currencies": "usd"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "vndc" in data and "usd" in data["vndc"]:
            return float(data["vndc"]["usd"])
        else:
            print("Error: VNDC data not found.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    





def escape_markdown_v2(text):
    """Escape special characters for Markdown V2."""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)



@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    send_captcha(user_id)  # Gửi CAPTCHA ngay khi bắt đầu

def send_captcha(user_id):
    """Tạo và gửi CAPTCHA mới"""
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(["+", "-"])
    result = eval(f"{num1} {operator} {num2}")  # Tính kết quả

    # Lưu kết quả vào database
    User.saveData("captcha_answer", result, user=user_id)

    # Gửi CAPTCHA và lưu ID tin nhắn
    captcha_msg = bot.send_message(
        user_id,
        f"🔢 *CAPTCHA Challenge!*\n\n"
        f"👉 Solve: `{num1} {operator} {num2} = ?`\n"
        f"✏️ Reply with the correct answer.",
        parse_mode="Markdown"
    )
    
    # Lưu ID tin nhắn CAPTCHA
    User.saveData("captcha_message_id", captcha_msg.message_id, user=user_id)


@bot.message_handler(func=lambda message: User.getData("captcha_answer", user=message.chat.id) is not None)
def check_captcha(message):
    user_id = message.chat.id
    correct_answer = User.getData("captcha_answer", user=user_id)

    # Lấy ID tin nhắn CAPTCHA cũ để xóa
    captcha_message_id = User.getData("captcha_message_id", user=user_id)

    try:
        user_answer = int(message.text)
        if user_answer == correct_answer:
            # Xóa CAPTCHA sau khi trả lời đúng
            User.saveData("captcha_answer", None, user=user_id)

            # Xóa tin nhắn CAPTCHA cũ
            if captcha_message_id:
                bot.delete_message(user_id, captcha_message_id)

            # Xóa câu trả lời đúng của người dùng để tránh tràn tin nhắn
            bot.delete_message(user_id, message.message_id)

            # Gửi hướng dẫn tham gia kênh
            text = """<b>🔐 You have to join our channels:

🔹 @groupcryptochat  
🔹 @newlistingcryptochannel  
🔹 @transactionspayment</b>"""

            keyboard = InlineKeyboardMarkup()
            continue_btn = InlineKeyboardButton("➡ Continue", callback_data="continue")
            keyboard.add(continue_btn)

            continue_msg = bot.send_message(user_id, text=text, parse_mode="html", reply_markup=keyboard)

            # Lưu ID tin nhắn chứa nút "➡ Continue"
            User.saveData("continue_message_id", continue_msg.message_id, user=user_id)

        else:
            # Xóa tin nhắn CAPTCHA cũ
            if captcha_message_id:
                bot.delete_message(user_id, captcha_message_id)

            # Xóa tin nhắn chứa đáp án sai của người dùng
            bot.delete_message(user_id, message.message_id)

            # Xóa tin nhắn lỗi nhập sai số trước đó nếu có
            invalid_message_id = User.getData("invalid_message_id", user=user_id)
            if invalid_message_id:
                bot.delete_message(user_id, invalid_message_id)

            # Gửi tin nhắn thông báo sai
            error_msg = bot.send_message(user_id, "❌ Wrong answer! Generating a new challenge...", parse_mode="Markdown")

            # Lưu ID tin nhắn lỗi để xóa sau
            User.saveData("wrong_answer_message_id", error_msg.message_id, user=user_id)

            send_captcha(user_id)  # Gửi CAPTCHA mới nếu sai
    except:
        # Xóa tin nhắn không hợp lệ của người dùng
        bot.delete_message(user_id, message.message_id)

        # Xóa tất cả tin nhắn lỗi nhập sai số trước đó
        old_invalid_message_id = User.getData("invalid_message_id", user=user_id)
        if old_invalid_message_id:
            bot.delete_message(user_id, old_invalid_message_id)

        # Gửi tin nhắn thông báo lỗi
        invalid_msg = bot.send_message(user_id, "❌ Please enter a valid number.", parse_mode="Markdown")

        # Lưu ID tin nhắn lỗi nhập sai để xóa lần sau
        User.saveData("invalid_message_id", invalid_msg.message_id, user=user_id)


@bot.callback_query_handler(func=lambda call: call.data == "continue")
def continue_handler(call):
    user_id = call.message.chat.id

    # Xóa tin nhắn chứa nút "➡ Continue"
    continue_message_id = User.getData("continue_message_id", user=user_id)
    if continue_message_id:
        try:
            bot.delete_message(user_id, continue_message_id)
        except Exception as e:
            print(f"Error deleting '➡ Continue' message: {e}")

    # Xóa tin nhắn thông báo sai nếu còn tồn tại
    wrong_answer_message_id = User.getData("wrong_answer_message_id", user=user_id)
    if wrong_answer_message_id:
        try:
            bot.delete_message(user_id, wrong_answer_message_id)
        except Exception as e:
            print(f"Error deleting 'Wrong answer' message: {e}")

    # Xóa tin nhắn lỗi nhập sai số nếu còn tồn tại
    invalid_message_id = User.getData("invalid_message_id", user=user_id)
    if invalid_message_id:
        try:
            bot.delete_message(user_id, invalid_message_id)
        except Exception as e:
            print(f"Error deleting 'Invalid number' message: {e}")

    # Gửi tin nhắn hướng dẫn tham gia kênh
    join_channels_message = ("*🟢 Join our Telegram channels:*\n"
                             "**🔹@groupcryptochat**\n"
                             "**🔹@newlistingcryptochannel**\n"
                             "**🔹@transactionspayment**\n")

    # Giao diện nút "📌 Check"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📌 Check"))

    bot.send_message(chat_id=user_id,
                     text=join_channels_message,
                     parse_mode="Markdown",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "📌 Check")
def check_handler(message):
    u = message.chat.id

    channels = ['@groupcryptochat', '@newlistingcryptochannel', '@transactionspayment']

    def check_channels(u):
        for channel in channels:
            try:
                member = bot.get_chat_member(chat_id=channel, user_id=u)
                if member.status == "left":
                    return False
            except Exception as e:
                logger.error(f"Error checking channel membership: {e}")
                return False
        return True

    # Kiểm tra nếu người dùng đã tham gia đầy đủ kênh
    if check_channels(u):
        # Kiểm tra nếu là người dùng mới
        if User.getData("bot_user", user=u) is None:
            User.saveData("vndc_balance", 0, user=u)
            User.saveData("paxg_balance", 0, user=u)
            User.saveData("ref_count", 0, user=u)
            User.saveData("withdrawn", 0, user=u)
            User.saveData("ref_rewarded", False, user=u)
            User.saveData("bot_user", True, user=u)

        # Tăng tổng số người dùng của bot
        total_users = Bot.getData("total_users")
        Bot.saveData("total_users", (total_users or 0) + 1)

        referrer_id = User.getData("referrer", u)  # Lấy ID người mời
        if referrer_id:
            # Kiểm tra nếu chưa thưởng cho người giới thiệu
            ref_rewarded = User.getData("ref_rewarded", user=u)
            if not ref_rewarded:
                user_id = str(message.from_user.id)
                # Cộng thưởng cho người giới thiệu
                referrer_balance = User.data.get(user_id, {}).get('vndc_balance', 0)
                referrer_count = User.getData("ref_count", user=referrer_id) or 0
                referrer_bonus = 500000  # Cộng thưởng 500,000 VNDC cho người giới thiệu
                new_balance_referrer_bonus = referrer_balance + referrer_bonus
                referrer_count += 1  # Tăng số lượt giới thiệu
                User.saveData("vndc_balance", new_balance_referrer_bonus, referrer_id)
                User.saveData("ref_count", referrer_count, user=referrer_id)
                total_referrals = sum(
                    User.getData("ref_count", user) or 0
                    for user in User.data.keys())
                
                total_distributed_airdrop = User.getData("total_distributed_airdrop") or 0
                total_distributed_airdrop += referrer_bonus
                User.saveData("total_distributed_airdrop", total_distributed_airdrop)
                # Cập nhật trạng thái đã thưởng
                User.saveData("ref_rewarded", True, user=u)
                username = message.from_user.username or "Unknown"
                escaped_username = escape_markdown_v2(username)

                # Thông báo cho người giới thiệu
                bot.send_message(
                    chat_id=referrer_id,
                    text=
                    f"🎉 You receive *500,000 VNDC* for referrals to user @{escaped_username}\n"
                    f"👥 Total Referrals: {total_referrals}",
                    parse_mode="Markdown")
                
                bot.send_message(
                    chat_id=referrer_id,
                    text=f"*💵 Balance: {referrer_balance} VNDC*",
                    parse_mode="Markdown")

        # Gọi hàm `show_main_menu` để hiển thị menu chính
        show_main_menu(u)

    else:
        # Giao diện nút "➡ Continue"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("➡ Continue", callback_data="continue"))

        bot.send_message(
            chat_id=message.chat.id,
            text="*🔐 You have to join all channels first.*",
            parse_mode="Markdown",
            reply_markup=keyboard
        )


@bot.message_handler(func=lambda message: message.text == "🏦 My Assets")
def my_assets(message):
    user_id = str(message.from_user.id)
    balance_vndc = User.data.get(user_id, {}).get('vndc_balance', 0)
    balance_paxg = User.data.get(user_id, {}).get('paxg_balance', 0)
    vndc_price = get_vndc_price() or 0
    paxg_price = get_xaut_price() or 0
    usdt_price = get_usdt_price() or 0
    vndc_to_usdt = usdt_price * vndc_price
    vndc_usd = vndc_to_usdt * balance_vndc
    paxg_usd = paxg_price * balance_paxg
    total_assets_usd = paxg_usd + vndc_usd

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

        # Thêm các nút vào bàn phím
    keyboard.row(
        KeyboardButton("💵 VNDC"),
        KeyboardButton("🔹 PAXG"),
        KeyboardButton("🏠 Main Menu")
        )

    text = f"*🏦 Total Assets: ${total_assets_usd:,.2f}*"

        # Gửi tin nhắn với bàn phím mới
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="Markdown",  # Đảm bảo HTML được hỗ trợ
        disable_web_page_preview=True,  # Tắt preview của link
        reply_markup=keyboard
        )


@bot.message_handler(func=lambda message: message.text == "🔹 PAXG")
def paxg_balance_handle(message):
    username = message.from_user.username or "Unknown"
    user_id = str(message.from_user.id)

    escaped_username = escape_markdown_v2(username)
    user_balance = User.data.get(user_id, {}).get('paxg_balance', 0)
    formatted_balance = f"{user_balance:,.6f}"

    bot.send_message(chat_id=message.chat.id,
        text=f"*User =* @{escaped_username}\n\n"
             f"*🔹 Balance = {formatted_balance} PAXG*",
            parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "💵 VNDC")
def vndc_balance_handle(message):
    username = message.from_user.username or "Unknown"
    user_id = str(message.from_user.id)

    escaped_username = escape_markdown_v2(username)
    user_balance = User.data.get(user_id, {}).get('vndc_balance', 0)
    formatted_balance = f"{user_balance:,.0f}"

    bot.send_message(chat_id=message.chat.id,
        text=f"*User =* @{escaped_username}\n\n"
             f"*💵 Balance = {formatted_balance} VNDC*",
            parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "🎁 Bonus")
def bonus_handle(message):
    user_id = str(message.from_user.id)
    User.data.setdefault(user_id, {})['last_bonus_time'] = User.data.get(user_id, {}).get('last_bonus_time', 0)
    bonus_interval = 10  # 8640 giây ~ 24h
    current_time = int(datetime.now().timestamp())

    def format_time(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:0}h : {minutes:0}m : {seconds:0}s"

    # Tính toán thời gian còn lại
    time_since_last_bonus = current_time - User.data[user_id]['last_bonus_time']
    time_remaining = bonus_interval - time_since_last_bonus

    if time_remaining > 0:
        message_sent = bot.send_message(
            chat_id=message.chat.id,
            text=f"⏳ *Time Remaining for Bonus:* {format_time(time_remaining)}",
            parse_mode="Markdown"
        )

        previous_text = f"⏳ *Time Remaining for Bonus:* {format_time(time_remaining)}"

        while time_remaining > 0:
            current_time = int(datetime.now().timestamp())
            time_since_last_bonus = current_time - User.data[user_id]['last_bonus_time']
            time_remaining = bonus_interval - time_since_last_bonus

            if time_remaining >= 0:
                countdown_text = f"*⏳ Time Remaining for Bonus:*\n {format_time(time_remaining)}"

                if countdown_text != previous_text:
                    try:
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=message_sent.message_id,
                            text=countdown_text,
                            parse_mode="Markdown"
                        )
                        previous_text = countdown_text
                    except ApiTelegramException as e:
                        if e.result_json['error_code'] == 429:
                            retry_after = e.result_json['parameters']['retry_after']
                            print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                            time.sleep(retry_after + 0.5)
                            continue

            time.sleep(0.5)

    else:
        # Nhận thưởng Bonus
        bonus_amount = 500_000
        user_balance = User.data.get(user_id, {}).get('vndc_balance', 0)
        new_balance = user_balance + bonus_amount
        User.data[user_id]['vndc_balance'] = new_balance
        User.data[user_id]['last_bonus_time'] = current_time
        total_distributed_airdrop = User.getData("total_distributed_airdrop") or 0
        total_distributed_airdrop += bonus_amount
        User.saveData("total_distributed_airdrop", total_distributed_airdrop)

        # Kiểm tra số Block đã đào
        mining_data = User.getData("mining_data", user=user_id) or {"blocks_mined": 0}
        blocks_mined = mining_data.get("blocks_mined", 0)

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📦 Create Block", callback_data="create_block"))

        # Nếu đã đào đủ 1 Block, hiển thị nút "Mining PAXG"
        if blocks_mined >= 1.0:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton("⛏ Mining PAXG"), KeyboardButton("🏠 Main Menu"))

        bot.send_message(chat_id=message.chat.id,
                         text=f"🎁 Bonus Received + {bonus_amount:,.00f} VNDC\n",
                         parse_mode="Markdown")
        bonus_message = bot.send_message(
                            chat_id=message.chat.id,
                            text=f"💵 *Balance = {new_balance:,.0f} VNDC*",
                            reply_markup=keyboard,
                            parse_mode="Markdown"
                        )

        # Lưu message_id của tin nhắn chứa "📦 Create Block"
        User.saveData("bonus_message", bonus_message.message_id, user=user_id)



def format_time(seconds):
    seconds = int(seconds) 
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{minutes:00}m : {seconds:00}s"


@bot.callback_query_handler(func=lambda call: call.data == "create_block")  # Xử lý cả hai nút Inline
def create_block_handle(call):
    try:
        bot.answer_callback_query(call.id, "⛏ Start mining next block!")
        user_id = str(call.from_user.id)
        chat_id = call.message.chat.id

        # 🔥 Xóa tất cả tin nhắn cũ nếu tồn tại
        message_keys = ["bonus_message", "progress_message", "last_block_message", "pending_account_message"]
        for key in message_keys:
            message_id = User.getData(key, user=user_id)
            if message_id:
                try:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception as e:
                    print(f"⚠️ Error deleting {key}: {e}")

    except Exception as e:
        print(f"⚠️ Error handling block creation: {e}")
        return

    # 🔥 Khởi tạo dữ liệu đào block
    mining_data = User.getData("mining_data", user=user_id) or {}
    mining_data.setdefault("rate", 118.8)
    mining_data.setdefault("hashrate", 10000)
    mining_data.setdefault("last_mined_time", int(datetime.now().timestamp()))
    mining_data.setdefault("current_mined", 0)
    mining_data.setdefault("staked_tokens", 0)
    mining_data.setdefault("first_mining_done", 0)
    mining_data.setdefault("blocks_mined", 0)
    mining_data.setdefault("next_mine_time", 0)
    mining_data.setdefault("is_mining", False)

    # 🔥 Kiểm tra nếu còn thời gian chờ
    current_time = int(datetime.now().timestamp())
    if mining_data["is_mining"] and current_time < mining_data["next_mine_time"]:
        remaining_time = mining_data["next_mine_time"] - current_time
        bot.send_message(
            chat_id=chat_id,
            text=f"⏳ *Please wait {format_time(remaining_time)} before mining again!*",
            parse_mode="Markdown"
        )
        return

    mining_data["is_mining"] = True
    User.saveData("mining_data", mining_data, user=user_id)

    countdown_time = 10
    progress = 0.0
    mining_lock = threading.Lock()

    def update_progress():
        nonlocal progress, countdown_time
        with mining_lock:
            countdown_message = bot.send_message(
                chat_id=chat_id,
                text=f"🔄 *Block Progress:* ▱ {progress:.4f} Block\n⏳ *Mining Time:* {countdown_time}s",
                parse_mode="Markdown"
            )
            User.saveData("progress_message", countdown_message.message_id, user=user_id)

            while countdown_time > 0:
                time.sleep(1)
                countdown_time -= 1
                progress += 0.01  # Tăng tiến trình mỗi giây
                
                # Tính số thanh đầy dựa trên progress và đảm bảo có 10 thanh
                filled = int(progress * 100)  # Tính toán thanh đầy dựa trên 10 phần
                progress_bar = "▰" * filled + "▱" * (10 - filled)  # Luôn hiển thị đủ 10 thanh

                # Cập nhật thanh tải
                try:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=countdown_message.message_id,
                        text=f"🔄 *Block Progress:*\n {progress_bar} {progress:.4f - 0.01} Block\n⏳ *Mining Time:* {format_time(countdown_time)}",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"⚠️ Error updating progress: {e}")
                    break

            # ✅ Cập nhật số block đã đào
            mining_data = User.getData("mining_data", user=user_id) or {}
            mining_data["blocks_mined"] = round(mining_data.get("blocks_mined", 0) + 0.1, 1)
            User.saveData("mining_data", mining_data, user=user_id)

            # 🔥 Gửi tin nhắn xác nhận đào block
            keyboard = InlineKeyboardMarkup()
            if mining_data["blocks_mined"] >= 1.0:
                keyboard.add(InlineKeyboardButton("📜 Create Account Mining", callback_data="create_account_mining"))
                success_message = bot.send_message(
                    chat_id=chat_id,
                    text=f"🎉 *You have mined {mining_data['blocks_mined']:.0f} Block(s)!*\nClick below to create an account!",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                User.saveData("pending_account_message", success_message.message_id, user=user_id)
            else:
                keyboard.add(InlineKeyboardButton("📦 Next Create Block", callback_data="next_create_block"))
                block_message = bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ *Block Created Successfully!*\nTotal Blocks: {mining_data['blocks_mined']:.1f}",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                User.saveData("last_block_message", block_message.message_id, user=user_id)

    threading.Thread(target=update_progress, daemon=True).start()


@bot.callback_query_handler(func=lambda call: call.data == "next_create_block")
def next_create_block_handle(call):
    try:
        bot.answer_callback_query(call.id, "⛏ Start mining next block!")
        user_id = str(call.from_user.id)
        chat_id = call.message.chat.id

        # Xoá tin nhắn cũ nếu tồn tại
        message_keys = ["progress_message", "last_block_message", "pending_account_message"]
        for key in message_keys:
            message_id = User.getData(key, user=user_id)
            if message_id:
                try:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
                except Exception as e:
                    print(f"⚠️ Error deleting {key}: {e}")


    except Exception as e:
        print(f"⚠️ Error handling block creation: {e}")
        return

    # Khởi tạo dữ liệu đào block
    mining_data = User.getData("mining_data", user=user_id) or {}

    # Kiểm tra nếu còn thời gian chờ
    current_time = int(datetime.now().timestamp())
    if mining_data.get("is_mining") and current_time < mining_data.get("next_mine_time", 0):
        remaining_time = mining_data["next_mine_time"] - current_time
        bot.send_message(
            chat_id=chat_id,
            text=f"⏳ *Please wait {format_time(remaining_time)} before mining again!*",
            parse_mode="Markdown"
        )
        return

    mining_data["is_mining"] = True
    User.saveData("mining_data", mining_data, user=user_id)

    countdown_time = 10
    progress = 0.0
    mining_lock = threading.Lock()

    def update_progress():
        nonlocal progress, countdown_time
        with mining_lock:
            countdown_message = bot.send_message(
                chat_id=chat_id,
                text=f"🔄 *Block Progress:* ▱ {progress:.4f} Block\n⏳ *Mining Time:* {countdown_time}s",
                parse_mode="Markdown"
            )
            User.saveData("progress_message", countdown_message.message_id, user=user_id)

            while countdown_time > 0:
                time.sleep(1)
                countdown_time -= 1
                progress += 0.01

                filled = int(progress * 100)
                progress_bar = "▰" * filled + "▱" * (10 - filled)

                try:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=countdown_message.message_id,
                        text=f"🔄 *Block Progress:*\n{progress_bar} {progress:.4f - 0.01} Block\n⏳ *Mining Time:* {format_time(countdown_time)}",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    print(f"⚠️ Error updating progress: {e}")
                    break

            mining_data_local = User.getData("mining_data", user=user_id) or {}
            mining_data_local["blocks_mined"] = round(mining_data_local.get("blocks_mined", 0) + 0.1, 1)
            User.saveData("mining_data", mining_data_local, user=user_id)

            keyboard = InlineKeyboardMarkup()
            if mining_data_local["blocks_mined"] >= 1.0:
                keyboard.add(InlineKeyboardButton("📜 Create Account Mining", callback_data="create_account_mining"))
                success_message = bot.send_message(
                    chat_id=chat_id,
                    text=f"🎉 *You have mined {mining_data_local['blocks_mined']:.0f} Block(s)!*\nClick below to create an account!",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                User.saveData("pending_account_message", success_message.message_id, user=user_id)
            else:
                keyboard.add(InlineKeyboardButton("📦 Next Create Block", callback_data="next_create_block"))
                block_message = bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ *Block Created Successfully!*\nTotal Blocks: {mining_data_local['blocks_mined']:.1f}",
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
                User.saveData("last_block_message", block_message.message_id, user=user_id)

    threading.Thread(target=update_progress, daemon=True).start()




def measure_network_latency(url="https://api.telegram.org"):
    """ Đo thời gian phản hồi của mạng thực tế """
    try:
        start_time = time.time()
        response = requests.get(url, timeout=3)
        latency = time.time() - start_time
        return max(0.0001, latency)  # Giảm thời gian trễ tối thiểu để tăng tốc độ hiệu ứng
    except requests.RequestException:
        return 0.3  # Nếu lỗi mạng, giả lập độ trễ lớn hơn



@bot.callback_query_handler(func=lambda call: call.data == "create_account_mining")
def create_account_mining_handle(call):
    user_id = str(call.from_user.id)
    chat_id = call.message.chat.id

    # Xóa tin nhắn cũ
    pending_message_id = User.getData("pending_account_message", user=user_id)
    if pending_message_id:
        try:
            bot.delete_message(chat_id=chat_id, message_id=pending_message_id)
        except Exception as e:
            print(f"Error deleting account creation message: {e}")

    progress_message_id = User.getData("progress_message", user=user_id)
    if progress_message_id:
        try:
            bot.delete_message(chat_id=chat_id, message_id=progress_message_id)
        except Exception as e:
            print(f"Error deleting progress message: {e}")

    def account_creation_effect():
        steps = [
            "Checking the conditions for creating an account...",
            "Connecting to the system...",
            "Confirming information..."
        ]
        
        loading_icons = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]  # Hiệu ứng xoay vòng
        progress_message = bot.send_message(chat_id=chat_id, text=f"⠋ {steps[0]} 0%")
        
        for i, step in enumerate(steps):
            latency = measure_network_latency()  # Đo tốc độ mạng thực tế
            for percent in range(0, 101, 15):
                time.sleep(latency / 10)  # Điều chỉnh tốc độ nhanh hơn
                progress_bar = "▰" * (percent // 10) + "▱" * (10 - (percent // 10))
                loading_icon = loading_icons[(percent // 10) % len(loading_icons)]
                bot.edit_message_text(chat_id=chat_id, message_id=progress_message.message_id, text=f"{loading_icon} {step}\n[{progress_bar}] {percent}%")
            
            bot.edit_message_text(chat_id=chat_id, message_id=progress_message.message_id, text=f"✅ {step}")
        
        time.sleep(0.5)
        bot.edit_message_text(chat_id=chat_id, message_id=progress_message.message_id, text="✅ Loading Account...!")


        # Lưu dữ liệu tài khoản
        User.saveData("account_mining_initialized", True, user=user_id)

        # Hiển thị bàn phím mới
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("⛏ Mining PAXG"), KeyboardButton("🏠 Main Menu")) 
        bot.send_message(chat_id=chat_id, text="✅ *Account Mining Created Successfully!*\nNow you can start mining PAXG.", reply_markup=keyboard, parse_mode="Markdown")

    # Chạy hiệu ứng trong một luồng riêng để không làm chậm bot
    threading.Thread(target=account_creation_effect, daemon=True).start()




def format_hashrate(user_hashrate):
    if user_hashrate >= 10_000_000_000_000_000_000_000_000_000_000:  # Hashrate từ 10k tỷ vạn trở lên
        return "Infinite H/s" # Hiển thị vô hạn Hashrate
    elif user_hashrate < 100:  # Nếu là số nguyên, hiển thị 2 số thập phân
        return f"{user_hashrate:.2f} H/s"
    elif user_hashrate < 1000000:  # Nếu là hàng trăm, không có số thập phân
        return f"{user_hashrate:,.2f} H/s"

    units = ["M", "G", "T", "P", "E", "Z", "Y", "R", "Q", "X", "W", "V", "U"]  # Danh sách đơn vị
    index = 0
    while user_hashrate >= 1000000 and index < len(units):
        user_hashrate /= 1000000
        index += 1

    return f"{user_hashrate:.0f} {units[index-1]}H/s"  # Giữ 2 số thập phân cho đơn vị từ K trở lên


def generate_captcha_image(text, width=150, height=60):
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0))
    file_name = f"captcha_{random.randint(1000,9999)}.png"
    image.save(file_name)
    return file_name

def send_captcha_image(chat_id, captcha_file):
    with open(captcha_file, 'rb') as photo:
        bot.send_photo(chat_id, photo)

def verify_captcha(user_id, chat_id):
    captcha_type = random.choice(["number", "text"])
    if captcha_type == "number":
        captcha_value = str(random.randint(100, 999))
    else:
        captcha_value = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=5))
    captcha_file = generate_captcha_image(captcha_value)
    captcha_store[user_id] = captcha_value
    send_captcha_image(chat_id, captcha_file)
    os.remove(captcha_file)
    # Triển khai callback thực tế; ở đây mô phỏng 90% trả lời đúng.
    simulated_response = captcha_value if random.random() < 0.9 else "wrong"
    return simulated_response.upper() == captcha_value.upper()

def check_pos(user_id):
    mining_data = User.getData("mining_data", user=user_id) or {}
    staked = mining_data.get("staked_tokens")
    if staked is None:
        # Lần đầu, cấp token ban đầu cho user, ví dụ: 118.8 token.
        mining_data["staked_tokens"] = 118.8
        User.saveData("mining_data", mining_data, user=user_id)
        return True
    return staked >= 10

def apply_mining_fee(user_id, mining_fee):
    mining_data = User.getData("mining_data", user=user_id) or {}
    # Nếu đây là lần đầu khai thác, bỏ qua trừ phí.
    first_mining_done = mining_data.get("first_mining_done")
    if not first_mining_done:
        mining_data["first_mining_done"] = True
        User.saveData("mining_data", mining_data, user=user_id)
        return True
    # Sau lần đầu, kiểm tra số dư thanh toán.
    user_balance = User.getData("paxg_balance", user=user_id) or 0
    if user_balance < mining_fee:
        return False
    User.saveData("paxg_balance", user_balance - mining_fee, user=user_id)
    return True



def apply_dynamic_difficulty(rate_mining, total_hashrate):
    expected_block_time = 600
    if time.blocks < expected_block_time:
        difficulty_factor = time.blocks / expected_block_time
        rate_mining *= difficulty_factor
    return rate_mining

def apply_mining_rate_reduction(user_id, initial_rate, years_passed, user_hashrate, total_hashrate, method="integral"):
    if years_passed == 0:
        return initial_rate
    if method == "integral":
        new_rate = initial_rate / (2 ** years_passed)
    elif method == "sqrt":
        new_rate = initial_rate / ((years_passed + 1) ** 0.5)
    elif method == "percentage":
        reduction_rate = User.getData("custom_percentage", user=user_id) or 10
        new_rate = initial_rate * ((100 - reduction_rate * years_passed) / 100)
    else:
        new_rate = initial_rate
    if years_passed > 0 and total_hashrate > 0:
        hashrate_factor = max(0.5, user_hashrate / total_hashrate)
        new_rate *= hashrate_factor
    adjustment_factor = random.uniform(1.0027, 1.005)
    new_rate *= adjustment_factor
    return new_rate

@bot.message_handler(func=lambda message: message.text == "⛏ Mining PAXG")
def mining_paxg_handle(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id

    if not verify_captcha(user_id, chat_id):
        bot.send_message(chat_id, "Captcha không đúng, vui lòng thử lại!")
        return

    # Nếu lần đầu (chưa có dữ liệu stake), cấp token ban đầu cho user và không tính phí.
    if not check_pos(user_id):
        bot.send_message(chat_id, "Hệ thống đã cấp token ban đầu cho bạn. Vui lòng thử lại sau khi stake!")
        return

    # Từ lần thứ 2 trở đi, tính phí mining.
    mining_fee = 0.1
    if not apply_mining_fee(user_id, mining_fee):
        bot.send_message(chat_id, "Số dư của bạn không đủ để trả phí mining!")
        return

    mining_data = User.getData("mining_data", user=user_id) or {"current_mined": 0}
    global_total_blocks = User.getData("global_total_blocks") or 0
    next_reduction_block = User.getData("next_reduction_block") or MAX_BLOCKS_PER_YEAR

    global_total_blocks += 1
    User.saveData("global_total_blocks", global_total_blocks)

    years_passed = User.getData("years_passed") or 0
    rate_mining_initial = 118.8

    total_hashrate = User.getData("total_hashrate") or 0
    hashrate_users = User.getData("hashrate_users") or {}
    user_hashrate = hashrate_users.get(user_id, 10000)

    hashrate_increment = user_hashrate * 0.00248
    user_hashrate += hashrate_increment
    hashrate_users[user_id] = user_hashrate
    total_hashrate = sum(hashrate_users.values())
    User.saveData("hashrate_users", hashrate_users)
    User.saveData("total_hashrate", total_hashrate)

    if global_total_blocks >= next_reduction_block:
        years_passed += 1
        next_reduction_block += MAX_BLOCKS_PER_YEAR
        User.saveData("next_reduction_block", next_reduction_block)
        User.saveData("years_passed", years_passed)
        rate_mining = apply_mining_rate_reduction(user_id, rate_mining_initial, years_passed, user_hashrate, total_hashrate, method="integral")
        current_rate_display = int(rate_mining * 2) if years_passed == 1 else f"{rate_mining * 2:,.6f}"
        reduction_message = bot.send_message(
            chat_id,
            f"🔹*Mining Rate Halved!*\n"
            f"🔸*Current Rate:* {current_rate_display} PAXG/10min\n"
            f"🔻*New Halved Rate:* {rate_mining:,.6f} PAXG/10min",
            parse_mode="Markdown"
        )
        User.saveData("reduction_message_id", reduction_message.message_id, user=user_id)
    else:
        rate_mining = apply_mining_rate_reduction(user_id, rate_mining_initial, years_passed, user_hashrate, total_hashrate, method="integral")

    rate_mining = apply_dynamic_difficulty(rate_mining, total_hashrate)
    mining_data["rate"] = rate_mining
    countdown_time = 60
    tokens_mined_per_second = rate_mining / 60
    mining_share = user_hashrate / total_hashrate if total_hashrate > 0 else 1

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("💰 Claim PAXG", callback_data="claim"))
    formatted_hashrate = format_hashrate(user_hashrate)

    message_sent = bot.send_message(
        chat_id,
        text=f"⛏ *Mining Started*\n\n"
             f"🔸 *Rate:* {rate_mining:,.2f} PAXG/10min\n"
             f"⚡ *Hashrate:* {formatted_hashrate}\n"
             f"💎 *Tokens Mined:* 0.000000 PAXG",
        parse_mode="Markdown"
    )
    time_message = bot.send_message(
        chat_id,
        text=f"⏳ *Mining Time:* 00:00",
        parse_mode="Markdown"
    )
    while countdown_time > 0:
        time.sleep(1)
        countdown_time -= 1
        mining_data["current_mined"] += tokens_mined_per_second * mining_share
        try:
            bot.edit_message_text(
                chat_id,
                message_id=message_sent.message_id,
                text=f"⛏ *Mining Started*\n\n"
                     f"🔸 *Rate:* {rate_mining:,.2f} PAXG/10min\n"
                     f"⚡ *Hashrate:* {formatted_hashrate}\n"
                     f"💎 *Tokens Mined:* {mining_data['current_mined']:,.4f} PAXG",
                parse_mode="Markdown"
            )
            bot.edit_message_text(
                chat_id,
                message_id=time_message.message_id,
                text=f"⏳ *Mining Time:* {countdown_time // 60:02}:{countdown_time % 60:02}",
                parse_mode="Markdown"
            )
        except Exception as e:
            pass
    bot.edit_message_text(
        chat_id,
        message_id=message_sent.message_id,
        text=f"💎 *Total Tokens Mined:* {mining_data['current_mined']:,.6f} PAXG",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    mining_complete_message = bot.edit_message_text(
        chat_id,
        message_id=time_message.message_id,
        text=f"✅ *Mining Complete!*\n👉 Use the button below to claim your tokens.",
        parse_mode="Markdown"
    )
    User.saveData("mining_complete_message", mining_complete_message.message_id, user=user_id)
    User.saveData("mining_data", mining_data, user=user_id)


@bot.callback_query_handler(func=lambda call: call.data == "claim")
def handle_claim(call):
    user_id = str(call.from_user.id)
    mining_data = User.getData("mining_data", user=user_id)

    if not mining_data:
        bot.send_message(call.message.chat.id, "❌ *Mining data not found.*", parse_mode="Markdown")
        return

    mined_tokens = mining_data.get("current_mined", 0)
    total_mined_tokens = User.getData("total_mined_tokens", user=user_id) or 0
    total_mined_tokens += mined_tokens
    User.saveData("total_mined_tokens", total_mined_tokens, user=user_id)

    if mined_tokens > 0:
        current_balance = User.getData("paxg_balance", user=user_id) or 0
        new_balance = current_balance + mined_tokens
        mining_data["current_mined"] = 0

        User.saveData("paxg_balance", new_balance, user=user_id)
        User.saveData("mining_data", mining_data, user=user_id)

        # Xóa tin nhắn xác nhận khai thác hoàn thành trước
        mining_complete_message_id = User.getData("mining_complete_message", user=user_id)
        if mining_complete_message_id:
            try:
                bot.delete_message(call.message.chat.id, mining_complete_message_id)
            except Exception as e:
                print(f"⚠️ Error deleting mining complete message: {e}")

        # Xóa tin nhắn giảm tốc độ nếu tồn tại
        reduction_message_id = User.getData("reduction_message_id", user=user_id)
        if reduction_message_id:
            try:
                bot.delete_message(call.message.chat.id, reduction_message_id)
            except Exception as e:
                print(f"⚠️ Error deleting reduction message: {e}")
            finally:
                User.saveData("reduction_message_id", None, user=user_id)  # Xóa ID sau khi xóa thành công

        # Xóa tin nhắn yêu cầu claim
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bot.send_message(
            call.message.chat.id,
            f"✅ *Claim Successful!*\n"
            f"💰 *Claimed Tokens:* {mined_tokens:,.6f} *PAXG*",
            parse_mode="Markdown"
        )

        bot.send_message(
            call.message.chat.id,
            f"💵 *New Balance:* {new_balance:,.6f} *PAXG*",
            parse_mode="Markdown"
        )


@bot.message_handler(func=lambda message: message.text == "🏠 Main Menu")
def back_to_main_menu_handle(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

        # Thêm các nút vào bàn phím
    keyboard.row(
        KeyboardButton("🏦 My Assets"),
        KeyboardButton("🎁 Bonus"),
        KeyboardButton("👥 Ref"),
        KeyboardButton("💼 Wallet"),
        ),

    keyboard.row(
        KeyboardButton("⚙ Set Wallet"),
        KeyboardButton("💳 Withdrawal"),
        KeyboardButton("📨 Information"),
        KeyboardButton("📊 Statistics"),
        )

    text = f"<a href='https://t.me/{bot_username}'>🏠 Main Menu</a>"

        # Gửi tin nhắn với bàn phím mới
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="html",  # Đảm bảo HTML được hỗ trợ
        disable_web_page_preview=True,  # Tắt preview của link
        reply_markup=keyboard
        )


# Xử lý nút "👤 Referral"
@bot.message_handler(func=lambda message: message.text == "👥 Ref")
def handle_referral(message):
    user_id = str(message.from_user.id)  # ID người dùng
    
    # Lấy số lượt giới thiệu của người dùng hiện tại
    total_refer = User.getData("ref_count", user=user_id)
    if total_refer is None:
        total_refer = 0  # Nếu không có dữ liệu, gán mặc định là 0

    per_refer = "500,000"  # Số tiền cho mỗi lần giới thiệu
    get_bot = "vndctestnetbot"  # Tên bot
    link = f"https://t.me/{get_bot}?start={user_id}"  # Link giới thiệu

    # Tạo thông báo hiển thị thông tin về referral
    msg = f"""<b>🔗Your Referral Link: {link}

 🎁 Referral Bonus:  {per_refer}
 👥 Your Total Referrals: {total_refer} users

⭐ Refer And Earn Unlimited Crypto, Just Share above link</b>"""

    # Gửi thông báo cho người dùng
    bot.send_message(user_id, msg, parse_mode="html")


@bot.message_handler(func=lambda message: message.text == "💼 Wallet")
def wallet_handler(message):
    user_id = str(message.from_user.id)
    current_wallet = User.getData("wallet", user=user_id) or "No wallet"
    
    if current_wallet != "No wallet":
        bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>💼 Your Current Wallet Address:</b>\n<code>{current_wallet}</code>",
            parse_mode="html"
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="✏ *Please send your Wallet Address to set it.*",
            parse_mode="Markdown"
        )
        Bot.handleNextCommand("awaiting_wallet", user_id)

@bot.message_handler(func=lambda message: message.text == "⚙ Set Wallet")
def handle_set_wallet(message):
    user_id = str(message.from_user.id)
    current_wallet = User.getData("wallet", user=user_id) or "No wallet"
    
    if current_wallet != "No wallet":
        bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>💼 Your Current Wallet Address:</b>\n<code>{current_wallet}</code>",
            parse_mode="html"
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="✏ *Please send your Wallet Address to set it.*",
            parse_mode="Markdown"
        )
        Bot.handleNextCommand("awaiting_wallet", user_id)

@bot.message_handler(func=lambda message: Bot.getNextCommand(str(message.chat.id)) == "awaiting_wallet")
def handle_wallet_address(message):
    user_id = str(message.from_user.id)
    wallet_address = message.text.strip()
    
    # Kiểm tra định dạng địa chỉ ví
    if re.match(r'^(0x)?[0-9a-fA-F]{40}$', wallet_address):
        # Lấy danh sách tất cả địa chỉ ví từ database
        all_wallets = User.getAllData("wallet")  # Hàm lấy tất cả các địa chỉ ví
        if wallet_address in all_wallets.values():
            bot.send_message(
                chat_id=message.chat.id,
                text="❌ *This wallet address has been updated from another account.*",
                parse_mode="Markdown"
            )
            return
        
        # Lưu địa chỉ ví nếu không bị trùng
        User.saveData('wallet', wallet_address, user=user_id)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"*🖊 Done:* Your new *Wallet Address* is: `{wallet_address}`",
            parse_mode="markdown"
        )
        Bot.handleNextCommand(None, user_id)  # Xóa yêu cầu
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="❌ *Invalid wallet address format. Please try again.*",
            parse_mode="Markdown"
        )



@bot.message_handler(func=lambda message: message.text == "💳 Withdrawal")
def withdraw(message):
    user_id = str(message.from_user.id)
    wallet = User.getData("wallet", user=user_id) or "No wallet"
    user_balance = User.getData("balance", user=user_id) or 0
    min_withdraw_amount = 1000

    if wallet == "No wallet":
        bot.send_message(
            chat_id=message.chat.id,
            text="✏ *You need to set your Wallet Address before withdrawing.*",
            parse_mode="Markdown"
        )
        User.saveData('wallet', wallet, user=user_id)
        Bot.handleNextCommand(None, user_id)
        return

    if user_balance < min_withdraw_amount:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"❌ *Insufficient balance.*\n\n💰 *Your Balance:* {user_balance:,} VNDC\n💰 *Minimum Withdrawal:* {min_withdraw_amount:,} VNDC",
            parse_mode="Markdown"
        )
        return

    bot.send_message(
        chat_id=message.chat.id,
        text="*💸 Please enter the amount you want to withdraw:*\n\n"
              f"🔸 *Minimum Withdrawal:* {min_withdraw_amount:,} VNDC\n"
              f"🔸 *Maximum Withdrawal:* {user_balance:,} VNDC",
        parse_mode="Markdown"
    )
    User.saveData('withdraw_state', 'awaiting_amount', user=user_id)
    Bot.handleNextCommand("awaiting_amount", user_id) 


@bot.message_handler(func=lambda message: message.text == "📨 Information")
def info_token_handler(message):

    user_id = str(message.from_user.id)

    # Các thông tin liên quan đến token
    contract_address = "0xC7d07B5B64c98472d3EA44320aC86bf70d54e260"  # Thay bằng địa chỉ hợp đồng thực tế
    MIN_WITHDRAWAL_AMOUNT = 500_000

    # Tin nhắn thông báo thông tin token
    token_info_message = (
        "*📨 Info Token:*\n\n"
        "💠 *Token Name:* VNDC Token\n"
        "💠 *Token Symbol:* VNDC\n"
        "💠 *Decimals:* 18\n"
        "💠 *Total Supply:* 924,000,000,000,000,000 VNDC\n"
        "💠 *Network:* Binance Smart Chain (Testnet)\n"
        f"💠 *Contract:* {contract_address}\n\n"
        "🎁 *Bonus:* 500,000 $VNDC\n"
        "👥 *Ref:* 100,000 $VNDC\n"
        f"💳 *Withdrawal:* {MIN_WITHDRAWAL_AMOUNT:,.0f} $VNDC\n\n"
        "*✅If you have followed our Telegram Crypto Channel, you will instantly receive the payment✅*"
    )

    # Gửi tin nhắn thông tin token
    bot.send_message(chat_id=user_id,
                     text=token_info_message,
                     parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "📊 Statistics")
def statistics_handler(message):
    user_id = str(message.from_user.id)

    def update_statistics(chat_id, message_id):
        while True:  # Không giới hạn số lần lặp
            # Lấy dữ liệu mới
            current_bnb_price = get_bnb_price() or 0
            total_users = Bot.getData("total_users")
            total_transactions = get_total_transactions(contract_address)
            total_distributed_airdrop = User.getData("total_distributed_airdrop") or 0
            total_mining_tokens = User.getData("total_mined_tokens", user=user_id) or 0
            total_blocks_mining = User.getData("global_total_blocks") or 0
            total_hashrate = User.getData("total_hashrate") or 0
            total_holders = get_total_holders(contract_address)
            total_fee = get_total_fees_paid(contract_address) or 0
            gas_gwei = get_current_gas_gwei() or 0
            gas_prices = gas_gwei / (10**9)
            gas_limit = get_gas_limit(web3, data=None, value=0)
            gas_fees = gas_limit * gas_prices
            total_fee_usd = total_fee * current_bnb_price if total_fee and current_bnb_price else None
            gas_fees_usd = gas_fees * current_bnb_price if gas_fees and current_bnb_price else None
            gas_gwei_bnb = gas_gwei * (10**-9) if gas_gwei else None
            gas_gwei_usd = gas_gwei_bnb * current_bnb_price if gas_gwei_bnb and current_bnb_price else None
            

            # So sánh và thêm mũi tên
            def format_value(key, new_value, unit="", decimals=0):
                prev_value = previous_data.get(key)
                if prev_value is None or new_value is None:
                    arrow = ""
                elif new_value > prev_value:
                    arrow = " 🟢"
                elif new_value < prev_value:
                    arrow = " 🔴"
                else:
                    arrow = ""
                previous_data[key] = new_value  # Cập nhật giá trị trước đó
                # Định dạng số thập phân với số chữ số tuỳ chỉnh
                if isinstance(new_value, (int, float)):
                    return f"{new_value:,.{decimals}f}{unit}{arrow}" 
                return "No Data"

            # Định dạng các giá trị
            bnb_price_text = format_value("bnb_price", current_bnb_price, "$", decimals=2)
            total_users_text = format_value("total_users", total_users)
            total_transactions_text = format_value("total_transactions", total_transactions)
            total_airdrop_text = format_value("total_airdrop", total_distributed_airdrop, " VNDC")
            total_mining_tokens_text = format_value("total_mined_tokens", total_mining_tokens, " PAXG", decimals=6)
            total_blocks_mining_text = format_value("global_total_blocks", total_blocks_mining, " Block")
            total_hashrate_text = format_value("total_hashrate", total_hashrate, " Hashrate")
            total_holders_text = format_value("total_holders", total_holders)
            total_fee_text = format_value("total_fee", total_fee, " BNB", decimals=6)
            total_fee_bnb_text = format_value("total_fee_usd", total_fee_usd, decimals=2)
            gas_gwei_text = format_value("gas_gwei", gas_gwei, " Gwei", decimals=0)
            gas_fees_text = format_value("gas_fees", gas_fees, " BNB", decimals=8)
            gas_fees_usd_text = format_value("gas_fees_usd", gas_fees_usd, decimals=4)
            gas_limit_text = format_value("gas_limit", gas_limit, decimals=0)

            # Cập nhật thời gian
            formatted_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            # Cập nhật tin nhắn
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    f"*📊 Statistics:*\n\n"
                    f"💎 *BNB Price:* {bnb_price_text}\n"
                    f"🚀 *Total Users:* {total_users_text}\n"
                    f"🔗 *Total Transactions:* {total_transactions_text}\n"
                    f"💰 *Total Airdrop:* {total_airdrop_text}\n"
                    f"⛏ *Toatal Mining:* {total_mining_tokens_text}\n"
                    f"📦 *Toatal Block:* {total_blocks_mining_text}\n"
                    f"⚡ *Toatal Hashrate:* {total_hashrate_text}\n"
                    f"👤 *Total Hold:* {total_holders_text}\n"
                    f"💸 *Total Fees Paid:* {total_fee_text}\n 🌟 *Total Fees in USD:* ${total_fee_bnb_text}\n"
                    f"💧 *Gwei:* {gas_gwei_text}\n ✨ *Gwei in USD:* ${gas_gwei_usd:,.8f}\n"
                    f"⛽ *Gas:* {gas_fees_text}\n 💸 *Gas in USD:* ${gas_fees_usd_text}\n"
                    f"⚡*Gas Limit:* {gas_limit_text}\n"
                    f"🕒 *Server Time:* {formatted_time}"
                ),
                parse_mode="Markdown"
            )
            time.sleep(0.001)  # Chờ 5 giây trước khi làm mới

    # Gửi tin nhắn ban đầu
    initial_message = bot.send_message(
        chat_id=user_id,
        text=(
            f"*📊 Statistics:*\n\n"
                    f"💎 *BNB Price:* Loading...\n"
                    f"🚀 *Total Users:* Loading...\n"
                    f"🔗 *Total Transactions:* Loading...\n"
                    f"💰 *Total Airdrop:* Loading...\n"
                    f"⛏ *Toatal Mining:* Loading...\n"
                    f"📦 *Toatal Block:* Loading...\n"
                    f"👤 *Total Hold:* Loading...\n"
                    f"💸 *Total Fees Paid:* Loading...\n 🌟*Total Fees in USD:* Loading...\n"
                    f"💧 *Gwei:* Loading...\n ✨*Gwei in USD:* Loading...\n"
                    f"⚡*Gas Limit:* Loading...\n"
                    f"⛽ *Gas:* Loading...\n 💸*Gas in USD:* Loading...\n"
                    f"🕒 *Server Time:* Loading..."
        ),
        parse_mode="Markdown"
    )

    # Chạy luồng cập nhật tin nhắn
    Thread(target=update_statistics, args=(user_id, initial_message.message_id), daemon=True).start()



@bot.message_handler(func=lambda message: Bot.getNextCommand(str(message.chat.id)) == "awaiting_amount")
def process_withdrawal(message):
    user_id = str(message.from_user.id)
    try:
        amount = int(message.text.strip())  # Lấy số tiền từ người dùng
        user_balance = User.getData("balance", user=user_id) or 0
        wallet = User.getData("wallet", user=user_id)
        username = message.from_user.username or "Unknown"  # Username từ Telegram
        escaped_username = escape_markdown_v2(username)  # Escaping Markdown

        minimum_withdrawal_amount = 1000

        if amount < minimum_withdrawal_amount or amount > user_balance:
            bot.send_message(
                chat_id=message.chat.id,
                text=f"❌ *Amount invalid.*\n💰 Current Balance: {user_balance:,} VNDC\n💰 *Minimum Withdrawal:* {minimum_withdrawal_amount} VNDC",
                parse_mode="Markdown"
            )
            return

        User.saveData("withdrawal_amount", amount, user=user_id)

        keyboard = InlineKeyboardMarkup()

        comfirm_button = InlineKeyboardButton("✅ Confirm", callback_data="confirm_withdraw")
        cancel_button =  InlineKeyboardButton("❌ Cancel", callback_data="cancel_withdraw")
        keyboard.add(comfirm_button, cancel_button)

        confirmation_message = bot.send_message(
            chat_id=message.chat.id,
            text=f"🚀 *Confirm Withdrawal:*\n\n"
                 f"👤 *User:* Loading...\n\n"
                 f"💰 *Amount:* Loading...\n\n"
                 f"🤖 *Wallet Bot:* Loading...\n\n"
                 f"💼 *Wallet User:* Loading...\n\n"
                 f"⛽ *Network Fees:* Loading...\n\n"
                 f"💸 *Gas Price:* Loading...\n\n"
                 f"⏳ *Update time:* Loading...\n\n",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

        def update_message():
            countdown = 30  # Thời gian đếm ngược (giây)
            remaining_time = countdown  # Bắt đầu từ 30
            last_text = ""  # Lưu tin nhắn cuối cùng

            while True:
                try:
                    # Lấy giá BNB và phí gas
                    current_bnb_price = get_bnb_price() or 0
                    gas_gwei = get_current_gas_gwei() or 0
                    gas_prices = gas_gwei / (10**9)
                    gas_limit = 47000
                    gas_fees = gas_limit * gas_prices
                    network_gas_fees = gas_fees if gas_fees else None
                    gas_fees_usd = network_gas_fees * current_bnb_price if network_gas_fees and current_bnb_price else None

                    # Cập nhật nội dung tin nhắn
                    new_text = (
                        f"🚀 *Confirm Withdrawal:*\n\n"
                        f"👤 *User:* @{escaped_username}\n\n"
                        f"💰 *Amount:* {amount:,} VNDC\n\n"
                        f"🤖 *Wallet Bot:* {wallet_airdrop_bot}\n\n"
                        f"💼 *Wallet User:* {wallet}\n\n"
                        f"⛽ *Network Fees:* {network_gas_fees:,.4f} BNB\n\n"
                        f"💸 *Gas Fees in USD:* ${gas_fees_usd:,.4f}\n\n"
                        f"⏳ *Time remaining: {remaining_time}s*"
                    )

                    if new_text != last_text:  # Chỉ cập nhật nếu tin nhắn thay đổi
                        bot.edit_message_text(
                            chat_id=message.chat.id,
                            message_id=confirmation_message.message_id,
                            text=new_text,
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                        last_text = new_text  # Lưu tin nhắn cuối cùng

                    # Trừ 1 giây khỏi thời gian còn lại
                    remaining_time -= 1
                    if remaining_time < 0:  # Reset về countdown khi đếm hết
                        remaining_time = countdown

                    time.sleep(1)  # Dừng 1 giây trước khi lặp tiếp

                except Exception as e:
                    print(f"Error updating message: {e}")
                    break

        # Chạy hàm cập nhật trong một luồng riêng
        update_thread = Thread(target=update_message, daemon=True)
        update_thread.start()

    except ValueError:
        bot.send_message(
            chat_id=message.chat.id,
            text="❌ *Invalid input.* Please enter a valid amount.",
            parse_mode="Markdown"
        )       
   

# Xử lý callback cho các nút Inline
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_withdraw", "cancel_withdraw"])
def handle_callback_query(call):
    global updating  # Sử dụng biến toàn cục
    updating = False  # Dừng cập nhật
    if call.data == "confirm_withdraw":
        confirm_withdraw(call)  # Gọi hàm xác nhận rút tiền
    elif call.data == "cancel_withdraw":
        cancel_withdraw(call)



@bot.callback_query_handler(func=lambda call: call.data == "confirm_withdraw")
def confirm_withdraw(call):
    user_id = str(call.from_user.id)
    amount = User.getData("withdrawal_amount", user=user_id)
    
    # Kiểm tra xem amount có phải là None không
    if amount is None:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="❌ *Không tìm thấy số tiền rút. Vui lòng thử lại.*",
            parse_mode="Markdown"
        )
        return

    user_balance = User.getData("balance", user=user_id) or 0
    wallet = User.getData("wallet", user=user_id)
    username = call.from_user.username or "Unknown"  # Lấy username từ Telegram
    escaped_username = escape_markdown_v2(username)
    payment_channel = "@transactionspayment"
    bot_wallet_address = wallet_airdrop_bot
    current_bnb_price = get_bnb_price() or 0
    gas_gwei = get_current_gas_gwei() or 0
    gas_prices = gas_gwei / (10**9)
    gas_limit = 47000
    gas_fees = gas_limit * gas_prices 
                    # Tính toán chi phí
    network_gas_fees = gas_fees if gas_fees else None
    network_gas_fees_usd = network_gas_fees * current_bnb_price if network_gas_fees and current_bnb_price else None
    formatted_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Định dạng
    network_gas_fees_text = f"{network_gas_fees:,.4f} BNB" if network_gas_fees else "No Data"
    network_gas_fees_usd_text = f"${network_gas_fees_usd:,.6f}" if network_gas_fees_usd else "No Data"
    # Kiểm tra số tiền nhập có bằng số tiền tối thiểu không (Ví dụ: 100000 VNDC)
    minimum_withdrawal_amount = 1000 # Số tiền tối thiểu

    if amount < minimum_withdrawal_amount:
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"❌ *The withdrawal amount must be at least {minimum_withdrawal_amount:,} VNDC.*",
            parse_mode="Markdown"  # Sử dụng MarkdownV2
        )
        return

    # Kiểm tra số dư ví người dùng có đủ để thực hiện rút tiền không
    if amount > user_balance:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="❌ *Insufficient balance for this withdrawal.*",
            parse_mode="Markdown"  # Sử dụng MarkdownV2
        )
        return

    # Chuyển đổi số tiền từ VNDC sang Wei (1 VNDC = 1e18 Wei, điều này có thể thay đổi tùy vào token)
    amount_in_wei = amount * 10**2  # Chuyển đổi VNDC sang Wei, nếu cần thay đổi theo token của bạn

    # Trừ số dư và cập nhật
    new_balance = user_balance - amount
    User.saveData("balance", new_balance, user=user_id)


    

    # Tạo giao dịch
    transaction_hash = transfer_tokens(bot_wallet_address, wallet, amount_in_wei)
    if transaction_hash:
        tx_url = f"https://testnet.bscscan.com/tx/{transaction_hash}"
        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton(
            text="🔗 Check Transaction Details",  # Văn bản hiển thị trên nút
            url=tx_url  # Liên kết ẩn dưới nút
        )
        keyboard.add(button)
        with open("imagepayment.png", "rb") as photo:  # Đường dẫn đến hình ảnh
            bot.send_photo(
                chat_id=call.message.chat.id,
                photo=photo,
                caption=(
                    "✅ *Check your Withdrawal Proof in @transactionspayment*\n\n"
                    "❇️ *New VNDC Withdraw Paid!*\n\n"
                    "➖➖➖➖➖➖➖➖➖➖➖\n\n"
                    f"👤 *User:* @{escape_markdown_v2(username)}\n"
                    f"🏦 *Amount: {amount:,.0f} VNDC*\n\n"
                    "➖➖➖➖➖➖➖➖➖➖➖\n\n"
                    f"🔗 *Transaction URL:* [Open Link]({tx_url})\n"
                    f"⛽ *Network Fees:* {network_gas_fees_text} ≈ {network_gas_fees_usd_text}\n\n"
                    "⏳ *Status:* ✅ Successful\n\n"
                    f"🕒 *Time Payment:* {formatted_time}\n\n"
                    "➖➖➖➖➖➖➖➖➖➖➖\n"
                    "🤖 *Link Bot: @vndctestnetbot*"
                ),
                parse_mode="Markdown", reply_markup=keyboard
            )

        bot.send_message(chat_id=call.message.chat.id,
                         text=f"*🔹 Contract Address:* {contract_address}",
                         parse_mode="Markdown")
        show_main_menu(user_id)  # Sử dụng MarkdownV2

        with open("imagepayment.png", "rb") as photo_for_channel:
        # Gửi thông báo đến kênh
            bot.send_photo(payment_channel,photo=photo_for_channel,
                         caption=("*✅ Check your Withdrawal Proof in @transactionspayment*\n\n"
                               "*❇️ New VNDC Withdraw Paid!*\n\n"
                                "➖➖➖➖➖➖➖➖➖➖➖\n\n"
                               f"👤 *User:* @{escaped_username}\n"
                               f"🏦 *Amount: {amount:,.0f} VNDC*\n\n"
                                "➖➖➖➖➖➖➖➖➖➖➖\n\n"
                               f"🤖 *Wallet Bot:* {bot_wallet_address}\n"
                               f"💼 *Wallet User:* {wallet}\n\n"
                                "➖➖➖➖➖➖➖➖➖➖➖\n"
                               f"🔗 *Transaction URL:* [Open Link]({tx_url})\n"
                               f"⛽ *Network Fees:* {network_gas_fees_text} ≈ {network_gas_fees_usd_text}\n\n"
                                "⏳ *Status:*✅ Successful\n\n"
                               f"🕒 *Time Payment:* {formatted_time}\n\n"
                                "➖➖➖➖➖➖➖➖➖➖➖\n"
                                "🤖 *Link Bot: @vndctestnetbot*"),
                                        parse_mode="Markdown", reply_markup=keyboard)  # Sử dụng MarkdownV2
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="❌ *Transaction failed. Please try again later.*",
            parse_mode="Markdown"  # Sử dụng MarkdownV2
        )
    User.saveData('withdraw_state', None, user=user_id)


@bot.callback_query_handler(func=lambda call: call.data == "cancel_withdraw")
def cancel_withdraw(call):
    user_id = str(call.from_user.id)
    bot.send_message(
        chat_id=call.message.chat.id,
        text="❌ *Withdrawal cancelled.*",
        parse_mode="Markdown"  # Sử dụng MarkdownV2
    )
    show_main_menu(user_id)  # Quay về Main Menu


def show_main_menu(chat_id):
        # Tạo bàn phím với các nút
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

        # Thêm các nút vào bàn phím
    keyboard.row(
        KeyboardButton("🏦 My Assets"),
        KeyboardButton("🎁 Bonus"),
        KeyboardButton("👥 Ref"),
        KeyboardButton("💼 Wallet"),
        ),

    keyboard.row(
        KeyboardButton("⚙ Set Wallet"),
        KeyboardButton("💳 Withdrawal"),
        KeyboardButton("📨 Information"),
        KeyboardButton("📊 Statistics"),
        )

    text = f"<a href='https://t.me/{bot_username}'>🏠 Main Menu</a>"

        # Gửi tin nhắn với bàn phím mới
    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="html",  # Đảm bảo HTML được hỗ trợ
        disable_web_page_preview=True,  # Tắt preview của link
        reply_markup=keyboard
        )



# Chạy bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
