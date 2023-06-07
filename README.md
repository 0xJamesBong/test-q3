I'm kinda stumped by this task.

# What I have done so far

I have made some attempts with task 3.1 but nothing much on 3.2.

# Attempt for task 3.1

I've built a `binance_websocket.py` is a websocket that draws data via the Binance websocket.

The OrderBookClient in `binance_orderbook.py` is takes data from the websocket and processes the data to give instantaneous buy and sell prices.

The steps to building a local orderbook is actually outlined in Binance's own [documentation](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#how-to-manage-a-local-order-book-correctly), where it says:

How to manage a local order book correctly

- Open a stream to wss://stream.binance.com:9443/ws/bnbbtc@depth.
- Buffer the events you receive from the stream.
- Get a depth snapshot from https://api.binance.com/api/v3/depth?symbol=BNBBTC&limit=1000 .
- Drop any event where u is <= lastUpdateId in the snapshot.
- The first processed event should have U <= lastUpdateId+1 AND u >= lastUpdateId+1.
- While listening to the stream, each new event's U should be equal to the previous event's u+1.
- The data in each event is the absolute quantity for a price level.
- If the quantity is 0, remove the price level.
- Receiving an event that removes a price level that is not in your local order book can happen and is normal.
- Note: Due to depth snapshots having a limit on the number of price levels, a price level outside of the initial snapshot that doesn't have a quantity change won't have an update in the Diff. Depth Stream. Consequently, those price levels will not be visible in the local order book even when applying all updates from the Diff. Depth Stream correctly and cause the local order book to have some slight differences with the real order book. However, for most use cases the depth limit of 5000 is enough to understand the market and trade effectively.

I've forked an orderbook implementation from [here](https://github.com/rayzhudev/Binance-Orderbook/blob/master/OrderBook.py) - which seems to follow the above instructions pretty well.

The code I forked uses an OrderedDict to store the bids and asks.

The function `get_depth_snapshot(self)` processes snapshots of the orderbook by calling a REST API.

The `snapshot` dictionary provides a snapshot of the current state of the order book. It contains the following keys and their corresponding descriptions:

- `'lastUpdateId'`: The last update ID associated with the order book.
- `'bids'`: A list of bid orders, where each order is represented as [price, quantity].
- `'asks'`: A list of ask orders, where each order is represented as [price, quantity].

Here's an example of a `snapshot` dictionary:

```python
{
    'lastUpdateId': 37180324109,
    'bids': [['26818.88000000', '0.02927000'], ['26818.87000000', '0.03114000'], ...],
    'asks': [['26818.89000000', '8.16771000'], ['26908.49000000', '0.00054000'], ...]
}
```

In the `bids` list, each bid order is represented as a list with two elements: the price of the bid order as a string and the quantity of the bid order as a string.

Similarly, in the `asks` list, each ask order is represented as a list with two elements: the price of the ask order as a string and the quantity of the ask order as a string.

The `snapshot` provides a snapshot of the current state of the order book, including the latest update ID, the current bid orders, and the current ask orders.

The `get_depth_snapshot()` basically mirrors the structure of the snapshot, except that we separate the storage of the bids and asks into separate properties of the orderbook, instead of storing them both in a dict. `self.bid` and `self.asks` are both orderedDicts, in which the price level serves as the key, which returns the quantity at that level.

This is a good data structure to employ because (1) it's intuitive, (2) we can directly just call the price level and see the quantity at that level, and (3) if we are going to process an order, the ordered nature of the dict allows us to just eat up the quantity stored at sequentially, by adding up the quantity as you move up or down the price level until the sum satisfies the order.

I don't think this code is asynchronous or can appropriate handle server failure in a fail safe manner. This I know because the websocket itself is not asynchronous. It should be modified. One way to modify is it use a publisher-consumer model, where the websocket would be a publisher, and the orderbook be a consumer - not unlike the logger in question 1.

To find the AWS instance that has the lowest latency with the server where the exchange’s
matching engine resides, I would follow the approach [here](https://elitwilliams.medium.com/geographic-latency-in-crypto-how-to-optimally-co-locate-your-aws-trading-server-to-any-exchange-58965ea173a8).

As I understand it, I would have to deploy a server on AWS. The server would host a script in which I will ping the CEX. I will have to deploy servers on all of AWS's locations, ping the CEX, and the compare the response times. The one that responds the fastest is the one with the lowest latency.

# Attempt for task 3.2

For task 3.2, I suppose I will create a new class called `Order` which would have properties like exchange, symbol, price, amount, side (buy or sell), and timestamp. The exchange property can be used to tag the order's origin.

I would then store orders streamed from different exchanges, with their data repackaged into the `Order` class, into an `Orderbook` class, modified from the above 3.1 attempt.

The `Orderbook` class will store the `Orders` by their price level key in the 'bid' and 'ask' dictionaries, which would be replace by an array that looks like `[aggregate_quantity, {Order1, Order2,...} ]` where `Order1.amount + Order2.amount + ... = aggregate_quantity`

For incoming orders, if it is a new limit order, I just add it to the Orderbook. If it is a modification I just have to change the existing order. If it is a market order (say a buy order), I will have to iterate over the "ask" price levels of that CEX from whence the order came, aggregate the amounts until the amount of asks matches the buy order, and then remove the asks and the incoming buy order.

I don't have a good clue on how to deal with cases of slippage and frontrunning. In fact I'm little bit confused how slippage or frontrunning in this context would even look like. As far as I understand, we are basically replicating the orderbooks of the individual CEXes by first taking a snapshot of the orderbook depth, and then changing it as new orders come in. In this context, how would slippage even look like? A buyer submits a buy order at the average price calculated by the Orderbook, but by the time it is time to process its order, previous pending orders have already transformed the average price such that the market order he has submitted is no longer at the average price he was reported his trade could be exceuted at - it's unfortunate, but not sure I can do anything about it. As for frontrunning, I am confused how this is done in a CEX context without reordering or third party access to incoming orders.

Confused.

To build a client based on a dummy strategy to create fake orders on both sides of the order book, I will monitor the lowests asks and the highest bids, and then place orders at price levels above the lowests asks and the highest bids. At precisely the boundary, I will place the smallest size, and as I deviate from the boundary, I will place larger sizes. The sizes I put will be a fraction of the historical sizes placed at those levels - because I want to be in line with the market and I don't want to provide stupidly excessive amounts of liquidity. As for how the size placed will change as I move away from the boundary, I will decide that by looking at the historical volatility of the token over a given timeframe - say x number of the smallest kline at the exchange. The greater the variance, the smaller the size increases of the amount place at each level.

For example, if we are dealing with USDT, you can sleep pretty sound with bid orders like [0.99999, 1], [0.9999, 10],[0.999, 100], [0.9, 1000], because it's very unlikely those orders will ever be executed and if it does you're probably ok.

Similarly, in the case of bitcoin, if it is trading at 27000, you don't want to put all your fake orders at 26990, but you might want to put a lot of fake orders at 22000, in case a red dick happens.

And of course, one should reference historical volatility because while it might be wise to put orders at 22000 while bitcoin is trading at 27k, but if would unwise to maintain that order if btc has already drifted to 23k.

# Task specification

3. Trading
   The objective of this task is to assess your ability to create modularised components for a comprehensive trading client.

3.1. Stream Order Book Data

- Task:
  Design and implement an abstract client that uses a WebSocket to stream orderbook data from a centralised exchange.

- Requirements:

1. The orderbook must be stored in memory (at least 5 levels).
2. Justify your choice of the data structure used to store the orderbook data.
3. Updating the local version of the orderbook must be done asynchronously.
4. The code design must be fail-safe such that the flow of the main application is not
   interrupted even if the exchange’s server goes down.
5. Provide an example by connecting to an exchange of your choice and streaming data.
6. Find the AWS instance that has the lowest latency with the server where the exchange’s
   matching engine resides. Explain your approach.

3.2. Management & Execution

- Task:
  Design and implement an order management and execution system based on the following requirements.
- Requirements:

1. Choose a token (e.g. ETH) and create an internal module or structure (i.e. “consumer book”) to hold orders for the token from multiple exchanges (at least two).
   • The order must hold a tag of identifier specifying its origin.
2. Justify the design approach and explain how incoming orders will be held and how
   existing ones will be updated, taking edge cases into account.
   • For example, a common approach is to aggregate orders on the same side of
   the book with the same price. However, when executing, unpacking your size into smaller orders for their respective exchanges may not occur at the same rate or price. Pay attention to cases of slippage or front-running.
   • Provide an example by streaming orders into the “consumer book”.
3. Build a client based on a dummy strategy to create fake orders on both sides of the book
   (i.e. “trader book”). Be reasonable with the prices and sizes.
   • Provide an example of how the “trader book” is being continuously updated.
4. Build an abstract client that handles execution in a fail-safe manner.
5. Match orders on the “trader book” with those on the “consumer book”.
6. Submit transactions for execution.
7. Explain your order fill and order execution approach.

# Other notes

- Technically one can review the structure of the [python-binance](https://python-binance.readthedocs.io/en/latest/) library and see how it's done.
- https://mmquant.net/replicating-orderbooks-from-websocket-stream-with-python-and-asyncio/
