import sys
import json
import websockets
import asyncio
import time
from collections import defaultdict
import pprint
# https://binance-docs.github.io/apidocs/spot/en/#how-to-manage-a-local-order-book-correctly
# https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md
pp = pprint.PrettyPrinter(indent=4)


class BinanceWebsocket():
    def __init__(self, uri='wss://stream.binance.com:9443/ws'):
        self.uri = uri
        self.orderbook = defaultdict(list)
        self.ws = None

    def on_open(self, ws):
        print("WebSocket opened")
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params":
            [
                "btcusdt@depth@100ms"
            ],
            "id": 1
        }

        ws.send(json.dumps(subscribe_message))

    async def on_message(self, ws, message):
        print("Received a message")
        d = json.loads(message)
        bids = d.get('b')[:5]
        asks = d.get('a')[:5]
        u = d["u"]
        pp.pprint(d)
        self.orderbook['bids'] = bids
        self.orderbook['asks'] = asks
        self.orderbook['u'] = u

    # https://binance-docs.github.io/apidocs/spot/en/#partial-book-depth-streams
        # `'E'`: Event time. The time at which this update event was created, typically expressed as a UNIX timestamp in milliseconds.
        # `'U'`: Update ID. The update ID of this event. This can be used to keep track of updates and make sure they are processed in order.
        # `'a'`: Asks. The list of new ask orders (sell orders) from this update. Each item in the list is itself a list, with the first element being the price and the second element being the quantity. If the quantity is `'0.00000000'`, this means the ask order at this price has been fully filled or cancelled.
        # `'b'`: Bids. The list of new bid orders (buy orders) from this update. Like with asks, each item is a list with the price and quantity. A quantity of `'0.00000000'` indicates the bid order at this price has been fully filled or cancelled.
        # `'e'`: Event type. The type of this event. In this case, `'depthUpdate'` means it is an update to the order book's depth.
        # `'s'`: Symbol. The trading pair for which this update applies. In this case, `'BTCUSDT'` indicates the update is for the Bitcoin to Tether trading pair.
        # `'u'`: Last update ID. The last update ID processed on the Binance server for this event. It can be used to sync the local order book with the one on the server.
        # self.pp.pprint(d)

        # {
        #   "e": "depthUpdate", // Event type
        #   "E": 123456789,     // Event time
        #   "s": "BNBBTC",      // Symbol
        #   "U": 157,           // First update ID in event
        #   "u": 160,           // Final update ID in event
        #   "b": [              // Bids to be updated
        #     [
        #       "0.0024",       // Price level to be updated
        #       "10"            // Quantity
        #     ]
        #   ],
        #   "a": [              // Asks to be updated
        #     [
        #       "0.0026",       // Price level to be updated
        #       "100"           // Quantity
        #     ]
        #   ]
        # }
    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        while True:
            message = await self.websocket.recv()
            await self.on_message(message)

    def on_close(self, ws):
        print("WebSocket closed")

    def on_error(self, ws, error):
        print(f"Error occurred: {error}")

    async def connect(self):
        print("connected!")
        self.websocket = await websockets.connect(self.uri)
        while True:
            message = await self.websocket.recv()
            await self.on_message(message)

    async def start(self):
        print("started!")
        await self.connect()


async def main():
    ws = BinanceWebsocket()
    await ws.start()

if __name__ == '__main__':
    asyncio.run(main())
