3. Trading
   The objective of this task is to assess your ability to create modularised components for a comprehensive trading client.
   3.1. Stream Order Book Data
   -Task:
   Design and implement an abstract client that uses a WebSocket to stream orderbook data from
   a centralised exchange.

- Requirements:

1. The orderbook must be stored in memory (at least 5 levels).
2. Justify your choice of the data structure used to store the orderbook data.
3. Updating the local version of the orderbook must be done asynchronously.
4. The code design must be fail-safe such that the flow of the main application is not
   interrupted even if the exchange’s server goes down.
5. Provide an example by connecting to an exchange of your choice and streaming data.
6. Find the AWS instance that has the lowest latency with the server where the exchange’s
   matching engine resides. Explain your approach.
