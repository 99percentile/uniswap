import math
import json
from Pool import Pool

class Arbitrage:
    def clonePool(self, pool):
        return Pool(pool.asset["dai"], pool.asset["eth"], pool.swap_fee)

    def findArbitrage(self, poolA, poolB, verbose=False):
        # returns a tuple (pool for first swap, pool for second swap, amount of ETH to swap, profit in ETH)
        kA, kB = poolA.getK(), poolB.getK()
        
        # no opportunity as both pools have same k value
        if math.isclose(kA, kB):
            if verbose: print("No Arbitrage opportunity detected")
            return None, None, 0, 0

        # make A the pool with smaller k value
        swap = False
        if kB > kA:
            poolA, poolB = poolB, poolA
            kA, kB = kB, kA
            swap = True
        
        # using binary search to find amount to swap
        l, r = 0, min(poolA.asset["eth"], poolB.asset["eth"])
        while not math.isclose(l, r):
            m = l+(r-l)/2
            # recreate pools as swaps will change k
            pA, pB = self.clonePool(poolA), self.clonePool(poolB)
            converted_dai = pA.swap("eth", "dai", m)
            eth_back = pB.swap("dai", "eth", converted_dai)
            if pA.getK() > pB.getK():
                l = m
            else:
                r = m
        
        # profit is negative as swap fees is higher than arbitrage opportunity
        if eth_back - m < 0:
            if verbose: print("Fees too high for arbitrage.")
            return None, None, -1, 0

        if verbose:
            if swap:
                print("Swap ETH to DAI in pool B, then swap same amount of DAI to ETH in pool A, amount:", str(m), "ETH, profit", str(eth_back-m), "ETH")
            else:
                print("Swap ETH to DAI in pool A, then swap same amount of DAI to ETH in pool B, amount:", str(m), "ETH, profit", str(eth_back-m), "ETH")
        return poolA, poolB, m, eth_back-m

if __name__ == "__main__":
    with open('config.json') as f:
        data = json.load(f)
    dataA = data["PoolA"]
    poolA = Pool(dataA["dai"], dataA["eth"], dataA["swap_fee"])
    dataB = data["PoolB"]
    poolB = Pool(dataB["dai"], dataB["eth"], dataB["swap_fee"])
    dataC = data["PoolC"]
    poolC = Pool(dataC["dai"], dataC["eth"], dataC["swap_fee"])
    
    print(Arbitrage().findArbitrage(poolA, poolB, True))
    print(Arbitrage().findArbitrage(poolA, poolC, True))