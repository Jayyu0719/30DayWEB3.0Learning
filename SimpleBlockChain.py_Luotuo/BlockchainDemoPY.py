# 区块链演示程序 - 使用Python实现一个简单的加密货币区块链系统
# 
# 导入的库详细说明：
# hashlib: Python标准库，提供多种哈希算法（如SHA256、MD5等）
#         用于生成数据的数字指纹，确保数据完整性
# 
# json: Python标准库，用于JSON数据的编码和解码
#       将Python对象转换为JSON字符串，便于数据序列化
# 
# time: Python标准库，提供时间相关的功能
#       用于获取当前时间戳，记录区块创建时间
# 
# typing: Python标准库，提供类型提示功能
#         用于指定函数参数和返回值的类型，提高代码可读性
# 
# cryptography.hazmat.primitives: 第三方加密库，提供底层加密原语
#                                包含哈希算法、数字签名、密钥生成等功能
# 
# cryptography.hazmat.primitives.asymmetric: 提供非对称加密功能
#                                           包括椭圆曲线加密（ECDSA）等
# 
# cryptography.hazmat.primitives.serialization: 提供密钥序列化功能
#                                              将密钥转换为字节格式或从字节格式恢复
# 
# cryptography.exceptions: 提供加密操作中的异常类
#                         用于处理签名验证失败等错误情况

import hashlib
import json
import time
from typing import List, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.exceptions import InvalidSignature


class Transaction:
    """表示带有数字签名的加密货币交易"""
    
    def __init__(self, from_address: Optional[str], to_address: str, amount: float):
        # 初始化交易对象
        # from_address: 发送方地址（挖矿奖励交易为None）
        # to_address: 接收方地址
        # amount: 交易金额
        # signature: 数字签名（初始为None）
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.signature = None
    
    def compute_hash(self) -> str:
        """计算交易数据的SHA256哈希值"""
        # 将交易信息拼接成字符串
        transaction_string = f"{self.from_address}{self.to_address}{self.amount}"
        # 使用SHA256算法计算哈希值并返回十六进制字符串
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def sign(self, private_key: ec.EllipticCurvePrivateKey):
        """使用私钥对交易进行签名"""
        # 计算交易的哈希值
        transaction_hash = self.compute_hash()
        # 使用ECDSA算法和SHA256哈希函数对交易进行签名
        self.signature = private_key.sign(
            transaction_hash.encode(),
            ec.ECDSA(hashes.SHA256())
        )
    
    def is_valid(self) -> bool:
        """验证交易签名的有效性"""
        # 挖矿奖励交易（from_address为None）始终有效
        if self.from_address is None:
            return True
        
        # 检查是否存在签名
        if not self.signature:
            raise ValueError("缺少签名")
        
        try:
            # 从地址重建公钥
            # 将十六进制地址转换为字节，然后重建椭圆曲线公钥
            public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256K1(),  # 使用比特币采用的椭圆曲线
                bytes.fromhex(self.from_address)
            )
            
            # 验证签名
            # 使用公钥验证交易哈希的签名
            public_key.verify(
                self.signature,
                self.compute_hash().encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except (InvalidSignature, ValueError):
            # 签名验证失败或地址格式错误
            return False


class Block:
    """表示区块链中的一个区块"""
    
    def __init__(self, transactions: List[Transaction], previous_hash: str):
        # 初始化区块对象
        # transactions: 区块中包含的交易列表
        # previous_hash: 前一个区块的哈希值
        # timestamp: 区块创建时间戳（毫秒）
        # nonce: 工作量证明的随机数
        # hash: 当前区块的哈希值
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = int(time.time() * 1000)  # 转换为毫秒
        self.nonce = 1
        self.hash = self.compute_hash()
    
    def compute_hash(self) -> str:
        """计算区块数据的SHA256哈希值"""
        # 将区块的所有信息拼接成字符串：
        # 1. 所有交易的JSON表示
        # 2. 前一个区块的哈希值
        # 3. 随机数（nonce）
        # 4. 时间戳
        block_string = (
            json.dumps([tx.__dict__ for tx in self.transactions], default=str) +
            self.previous_hash +
            str(self.nonce) +
            str(self.timestamp)
        )
        # 计算SHA256哈希值并返回十六进制字符串
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def get_answer(self, difficulty: int) -> str:
        """获取工作量证明的目标哈希前缀"""
        # 返回指定数量的零字符作为目标前缀
        # 难度越高，需要的零越多，挖矿越困难
        return "0" * difficulty
    
    def mine(self, difficulty: int):
        """使用工作量证明算法挖矿"""
        # 首先验证区块中的所有交易
        if not self.validate_transactions():
            raise ValueError("发现被篡改的交易，停止挖矿")
        
        # 工作量证明算法：不断尝试不同的nonce值
        # 直到找到满足难度要求的哈希值
        while True:
            self.hash = self.compute_hash()
            # 检查哈希值的前缀是否满足难度要求
            if self.hash[:difficulty] != self.get_answer(difficulty):
                self.nonce += 1  # 增加nonce值
                self.hash = self.compute_hash()  # 重新计算哈希
            else:
                break  # 找到满足条件的哈希值
        
        print(f"挖矿完成: {self.hash}")
    
    def validate_transactions(self) -> bool:
        """验证区块中的所有交易"""
        # 遍历区块中的每个交易并验证其有效性
        for transaction in self.transactions:
            if not transaction.is_valid():
                return False
        return True


class Chain:
    """表示整个区块链"""
    
    def __init__(self, difficulty: int = 4):
        # 初始化区块链
        # chain: 存储所有区块的列表
        # transaction_pool: 待处理交易的池子
        # miner_reward: 挖矿奖励金额
        # difficulty: 挖矿难度
        self.chain = [self.big_bang()]
        self.transaction_pool = []
        self.miner_reward = 50
        self.difficulty = difficulty
    
    def set_difficulty(self, difficulty: int):
        """设置挖矿难度"""
        self.difficulty = difficulty
    
    def big_bang(self) -> Block:
        """创建创世区块"""
        # 创世区块是区块链的第一个区块
        # 没有前一个区块，所以previous_hash为空字符串
        # 通常不包含任何交易
        genesis_block = Block([], "")
        return genesis_block
    
    def get_latest_block(self) -> Block:
        """获取区块链中最新的区块"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction):
        """将交易添加到交易池中"""
        # 打印交易信息用于调试
        print(transaction.__dict__)
        
        # 验证交易地址的有效性
        if not transaction.from_address or not transaction.to_address:
            raise ValueError("无效的发送方或接收方地址")
        
        # 验证交易签名的有效性
        if not transaction.is_valid():
            raise ValueError("无效的交易，可能被篡改或签名无效")
        
        # 将有效交易添加到交易池
        self.transaction_pool.append(transaction)
    
    def add_block_to_chain(self, new_block: Block):
        """将新区块添加到区块链中"""
        # 设置新区块的前一个哈希值
        new_block.previous_hash = self.get_latest_block().hash
        # 对新区块进行挖矿
        new_block.mine(self.difficulty)
        # 将挖矿完成的区块添加到链中
        self.chain.append(new_block)
    
    def mine_transaction_pool(self, miner_reward_address: str):
        """挖矿交易池中的所有交易并奖励矿工"""
        # 创建矿工奖励交易
        # 挖矿奖励交易的发送方地址为None
        miner_reward_transaction = Transaction(
            None,  # 挖矿奖励的发送方地址为None
            miner_reward_address,
            self.miner_reward
        )
        # 将奖励交易添加到交易池
        self.transaction_pool.append(miner_reward_transaction)
        
        # 使用交易池中的所有交易创建新区块
        new_block = Block(
            self.transaction_pool,
            self.get_latest_block().hash
        )
        # 对新区块进行挖矿
        new_block.mine(self.difficulty)
        
        # 将挖矿完成的区块添加到链中
        self.chain.append(new_block)
        # 清空交易池
        self.transaction_pool = []
    
    def validate_chain(self) -> bool:
        """验证整个区块链的有效性"""
        # 如果只有一个区块（创世区块）
        if len(self.chain) == 1:
            # 验证创世区块的哈希值是否正确
            if self.chain[0].hash != self.chain[0].compute_hash():
                return False
            return True
        
        # 从第二个区块开始验证
        for i in range(1, len(self.chain)):
            block_to_validate = self.chain[i]
            
            # 验证区块中的所有交易
            if not block_to_validate.validate_transactions():
                print("发现非法交易")
                return False
            
            # 检查区块数据是否被篡改
            # 通过重新计算哈希值并与存储的哈希值比较
            if block_to_validate.hash != block_to_validate.compute_hash():
                print("检测到数据篡改")
                return False
            
            # 检查区块链接是否正确
            # 验证当前区块的前一个哈希值是否等于前一个区块的哈希值
            previous_block = self.chain[i - 1]
            if block_to_validate.previous_hash != previous_block.hash:
                print("区块链链接断裂")
                return False
        
        return True


# 密钥生成和地址创建的实用函数
def generate_key_pair():
    """生成新的私钥/公钥对"""
    # 使用SECP256K1椭圆曲线生成私钥
    # 这是比特币和以太坊使用的相同曲线
    private_key = ec.generate_private_key(ec.SECP256K1())
    # 从私钥派生公钥
    public_key = private_key.public_key()
    
    # 获取压缩格式的公钥（用作地址）
    # 压缩格式更短，节省存储空间
    public_bytes = public_key.public_bytes(
        encoding=Encoding.X962,  # 使用X.962编码格式
        format=PublicFormat.CompressedPoint  # 压缩点格式
    )
    
    # 返回私钥和十六进制格式的公钥地址
    return private_key, public_bytes.hex()


# 示例使用和测试
if __name__ == "__main__":
    # 创建难度为4的区块链
    blockchain = Chain(difficulty=4)
    
    # 为测试生成密钥对
    private_key1, address1 = generate_key_pair()
    private_key2, address2 = generate_key_pair()
    miner_address = generate_key_pair()[1]  # 只获取地址部分
    
    print(f"地址1: {address1}")
    print(f"地址2: {address2}")
    print(f"矿工地址: {miner_address}")
    
    # 创建并签名一个交易
    transaction1 = Transaction(address1, address2, 100)
    transaction1.sign(private_key1)
    
    # 将交易添加到交易池
    blockchain.add_transaction(transaction1)
    
    # 挖矿交易池
    blockchain.mine_transaction_pool(miner_address)
    
    # 验证区块链
    is_valid = blockchain.validate_chain()
    print(f"区块链有效: {is_valid}")
    
    # 打印区块链信息
    print(f"区块链长度: {len(blockchain.chain)}")
    print(f"最新区块哈希: {blockchain.get_latest_block().hash}")
