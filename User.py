from collections import defaultdict
class User:
    def __init__(self, dai, eth):
        self.asset = {"dai": dai, "eth":eth}
        self.pool_tokens = defaultdict(int)
    
    def add_liquidity(self, dai, eth, pool):
        if eth > self.asset["eth"] or dai > self.asset["dai"]:
            raise Exception("Insufficient funds")
        self.pool_tokens[pool] += pool.add_liquidity(dai, eth)
        self.asset["dai"] -= dai
        self.asset["eth"] -= eth
    
    def remove_liquidity(self, pool_tokens, pool):
        if pool_tokens > self.pool_tokens[pool]:
            raise Exception("Insufficient pool tokens")
        self.pool_tokens[pool] -= pool_tokens
        dai, eth = pool.remove_liquidity(pool_tokens)
        self.asset["dai"] += dai
        self.asset["eth"] += eth
    
    def swap(self, pool, fro, to, amt):
        if amt > self.asset[fro]:
            raise Exception("Insufficient funds")
        self.asset[fro] -= amt
        self.asset[to] += pool.swap(fro, to, amt)