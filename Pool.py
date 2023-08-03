import math

class Pool:
    def __init__(self, dai, eth, swap_fee):
        self.asset = {"dai": dai, "eth":eth}
        self.swap_fee = swap_fee
        self.total_tokens = math.sqrt(dai*eth)

    def getK(self):
        return self.asset["dai"]/self.asset["eth"]

    def __str__(self):
        return "DAI " + str(self.asset["dai"]) + ", ETH " + str(self.asset["eth"])

    def add_liquidity(self, dai, eth):
        if not math.isclose(dai/eth, self.asset["dai"]/self.asset["eth"], abs_tol=1e-5):
            raise Exception("Proportion of DAI and ETH is not same as the pool's proportion.")
        self.asset["dai"] += dai
        self.asset["eth"] += eth
        self.total_tokens += math.sqrt(dai*eth)
        return math.sqrt(dai*eth)

    def remove_liquidity(self, pool_tokens):
        if pool_tokens > self.total_tokens:
            raise Exception("Insufficient tokens in pool.")
        proportion = pool_tokens/self.total_tokens
        dai, eth = proportion * self.asset["dai"],  proportion * self.asset["eth"]
        self.asset["dai"] -= dai
        self.asset["eth"] -= eth
        self.total_tokens -= pool_tokens
        return dai, eth
    
    def swap(self, fro, to, amt):
        if self.asset[fro] < amt:
            raise Exception("Insufficient funds in pool to swap.")
        amt_to_swap = (1-self.swap_fee) * amt
        k = self.asset[to]*self.asset[fro]
        to_swap = self.asset[to] - k / (self.asset[fro]+amt_to_swap)
        self.asset[fro] += amt
        self.asset[to] -= to_swap
        return to_swap