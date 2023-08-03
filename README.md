# Implementation of UniSwap v2.0 in Python
### By Lee Yu Cong

## About the project
This project is an implementation of UniSwap v2.0 written in python 3.7. It has capabilities to add and remove liquidity in a pool as well as finding an arbitrage opportunity between two pools having the same crypto pair.

## Prerequisites
As simple libraries are used, simply using python3 should be sufficient to run the code.

## Code Organization
<ul>
  <li> *Arbitrage.py* contains the code to determine whether an arbitrage opportunity is available. If there is one, it returns a tuple stipulating the order of swaps, amount of ETH to swap and the profit after swaps in ETH. Otherwise, it returns *None* for the direction of swaps, a negative integer for the amount of ETH to swap as an error code and 0 profit.</li>
  <li> *Pool.py* is where the implementation of the pool is written. Instead of two different variables, it has a dictionary to store the crypto pairs. This is to allow for one function to perform the swap. It also has a swap fee which can be different for different pools and the pool token to keep track on the liquidity of the pool.</li>
  <li> *User.py* imitates a real person interacting with the Pool. An user can add or remove liquidity from the pool, perform swap operations using their own cryptocurrency and has their own wallet of DAI, ETH and pool tokens.</li>
  <li> *Test.py* holds the many unit test cases for the implementation. It is separated into two classes: one for testing the addition and removal of liquidity into a pool and also swapping tokens. The other tests the logic of arbitrage.</li>
</ul>

## Running code
To run the code, type <code>python3 Test.py</code> into your terminal. It will execute the different tests written in *Test.py*.