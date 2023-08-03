from Pool import Pool
from User import User
from Arbitrage import Arbitrage
import json
import unittest
import math
import threading
from time import sleep

class TestSwap(unittest.TestCase):
    def setUp(self):
        with open('config.json') as f:
            data = json.load(f)
        d = data["PoolA"]
        self.pool = Pool(d["dai"], d["eth"], d["swap_fee"])
        
        self.user = User(10, 10)
        self.user.add_liquidity(3, 1, self.pool)

    def test_add_liquidity(self):
        # user does not have sufficient funds to add liquidity
        with self.assertRaises(Exception):
            self.user.add_liquidity(12, 12, self.pool)
        
        # user adds inproprotionate amount into pool
        with self.assertRaises(Exception):
            self.user.add_liquidity(1, 1, self.pool)
        
        # user adds liquidity
        self.user.add_liquidity(3, 1, self.pool)
        self.assertAlmostEqual(self.pool.asset["dai"], 306, "Wrong Amount of dai in pool.")
        self.assertAlmostEqual(self.pool.asset["eth"], 102, "Wrong Amount of eth in pool.")
        self.assertAlmostEqual(self.pool.total_tokens, math.sqrt(306*102), msg="Wrong Amount of pool tokens in pool.")
    
    def test_remove_liquidity(self):
        # user does not possess sufficient pool tokens to remove liquidity
        with self.assertRaises(Exception):
            self.user.remove_liquidity(10, self.pool)
        
        # user removes liquidity
        pool_liquidity = self.pool.total_tokens
        pool_dai = self.pool.asset["dai"]
        pool_eth = self.pool.asset["eth"]
        new_dai = pool_dai - 1/pool_liquidity*pool_dai
        new_eth = pool_eth - 1/pool_liquidity*pool_eth
        
        self.user.remove_liquidity(1, self.pool)
        self.assertAlmostEqual(self.pool.asset["dai"], new_dai, "Wrong Amount of dai in pool.")
        self.assertAlmostEqual(self.pool.asset["eth"], new_eth, "Wrong Amount of eth in pool.")
        self.assertAlmostEqual(self.pool.total_tokens, math.sqrt(new_dai*new_eth), "Wrong Amount of pool tokens in pool.")

        # empties all liquidity from pool
        userA = User(0, 0)
        userA.pool_tokens[self.pool] = self.pool.total_tokens
        userA.remove_liquidity(self.pool.total_tokens, self.pool)

        self.assertAlmostEqual(self.pool.asset["dai"], 0, "Remaining DAI in pool.")
        self.assertAlmostEqual(self.pool.asset["eth"], 0, "Remaining ETH in pool.")
        self.assertAlmostEqual(self.pool.total_tokens, 0, "Remaining pool tokens in pool.")

    
    def test_swap(self):
        # test insufficient funds
        with self.assertRaises(Exception):
            self.user.swap_dai_to_eth(100, self.pool)
        
        # test normal swap 2 dai to eth
        prev_k = self.pool.asset["dai"] * self.pool.asset["eth"]
        amt = 2
        amt_to_swap = amt * (1-self.pool.swap_fee)
        change = self.pool.asset["eth"] - prev_k / (self.pool.asset["dai"]+amt_to_swap)
        self.user.swap(self.pool, "dai", "eth", amt)

        # assert user and pool having correct values
        self.assertAlmostEqual(self.user.asset["dai"], 7-amt, "incorrect dai amount for user.")
        self.assertAlmostEqual(self.user.asset["eth"], 9+change, "incorrect eth amount for user.")
        self.assertAlmostEqual(self.pool.asset["dai"], 303+amt, "incorrect dai amount in pool.")
        self.assertAlmostEqual(self.pool.asset["eth"], 101-change, "incorrect eth amount in pool.")
        self.assertGreater(self.pool.asset["dai"]*self.pool.asset["eth"], prev_k, "k did not increase after swap.")

class TestArbitrage(unittest.TestCase):
    def setUp(self):
        with open('config.json') as f:
            data = json.load(f)
        dataA = data["PoolA"]
        self.poolA = Pool(dataA["dai"], dataA["eth"], dataA["swap_fee"])
        dataB = data["PoolB"]
        self.poolB = Pool(dataB["dai"], dataB["eth"], dataB["swap_fee"])
        dataC = data["PoolC"]
        self.poolC = Pool(dataC["dai"], dataC["eth"], dataC["swap_fee"])
    
    def test_arbitrage_equal_k(self):
        self.poolB.asset["eth"] = self.poolA.asset["eth"] * self.poolB.asset["dai"] / self.poolA.asset["dai"]
        self.assertAlmostEqual(self.poolA.getK(), self.poolB.getK())
        result = Arbitrage().findArbitrage(self.poolA, self.poolB)
        self.assertEqual(result, (None, None, 0, 0), "Error in arbitrage no opportunity.")

    def test_arbitrage(self):
        firstPool, finalPool, amtEth, profit = Arbitrage().findArbitrage(self.poolA, self.poolB)
        print("Swap ETH", amtEth, firstPool)
        converted_dai = firstPool.swap("eth", "dai", amtEth)
        print("Get DAI", converted_dai, firstPool)
        print("Pool B", finalPool)
        eth_back = finalPool.swap("dai", "eth", converted_dai)
        print("New ETH", eth_back, finalPool)
        self.assertAlmostEqual(self.poolA.getK(), self.poolB.getK())
        self.assertGreater(profit, 0)
    
    def test_arbitrage_swap_order(self):
        # check if swap clause in code works
        firstPool, finalPool, amtEth, profit = Arbitrage().findArbitrage(self.poolB, self.poolA)
        converted_dai = firstPool.swap("eth", "dai", amtEth)
        eth_back = finalPool.swap("dai", "eth", converted_dai)
        self.assertAlmostEqual(self.poolA.getK(), self.poolB.getK())
        self.assertGreater(profit, 0)

    def test_arbitrage_high_fees(self):
        self.assertNotEqual(self.poolA.getK(), self.poolC.getK())
        result = Arbitrage().findArbitrage(self.poolA, self.poolC)
        self.assertEqual(result, (None, None, -1, 0), "Error in high fees.")
    
    def infinite_loop(self, stop_threads):
        while True:
            Arbitrage().findArbitrage(self.poolA, self.poolB)
            if stop_threads:
                break

    def test_non_blocking(self):
        stop_threads = False
        t = threading.Thread(target=self.infinite_loop, args =(lambda : stop_threads,))
        t.start()

        # user adds liquidity
        user = User(10, 10)
        user.add_liquidity(3, 1, self.poolA)

        sleep(0.5)

        # user performs swap
        prev_k = self.poolA.asset["dai"] * self.poolA.asset["eth"]
        amt = 2
        amt_to_swap = amt * (1-self.poolA.swap_fee)
        change = self.poolA.asset["eth"] - prev_k / (self.poolA.asset["dai"]+amt_to_swap)
        user.swap(self.poolA, "dai", "eth", amt)

        sleep(0.5)

        stop_threads = True
        t.join()


if __name__ == '__main__':
    unittest.main(verbosity=2)
    