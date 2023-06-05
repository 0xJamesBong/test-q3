import sys
from binance_websocket import BinanceWebsocket
import json
import websocket
import threading
import time
from collections import defaultdict
import requests
from collections import OrderedDict
import pprint as pp
import asyncio
...


# ws = BinanceWebsocket()
# ws.start()
#  # Add this line to delay the end of the program
# time.sleep(10)
    
class OrderBook():
    def __init__(self, websocket, depth_api, symbol, volume):
        self.websocket = websocket
        self.depth_api = depth_api
        self.symbol = symbol
        self.volume = volume
        self.updates = []
        self.bids = OrderedDict()  # ordered dictionary used to sort orders by price
        self.asks = OrderedDict()

    async def get_orders(self):
        received_snapshot = False
        print(self.symbol + " Average Execution Price for volume: " + str(self.volume))
        
        # Starts the BinanceWebsocket in a new thread.
        self.websocket.start()

        while True:
            # Now the updates are fetched from the orderbook of the BinanceWebsocket.
            depth_update = self.websocket.orderbook
            # print("depth_update",depth_update, "\n")
            self.updates.append(depth_update)

            if not received_snapshot:
                self.get_depth_snapshot()
                received_snapshot = True

            self.process_updates()
            self.update_console()
            await asyncio.sleep(0.01)  # You might need to adjust the sleep time.



    def get_depth_snapshot(self):
        snapshot = requests.get(self.depth_api)
        snapshot = json.loads(snapshot.content)
        self.snapshot = snapshot
        for order in snapshot["bids"]:
            self.bids[float(order[0])] = float(order[1])
        for order in snapshot["asks"]:
            self.asks[float(order[0])] = float(order[1])

    def process_updates(self):
        # print("hi!")

        for i in range(len(self.updates)):
            # pp.pprint(self.updates)
            # print(i, "u", self.updates[i]["u"])
            # print("snapshot['lastUpdatedId']", self.snapshot["lastUpdateId"])
            # if type(self.updates[i]["u"]) == int: 
            #     print(i, self.updates[i])
                # print("u", self.updates[i]["u"])
            if type(self.updates[i]["u"]) == list: 
                pass 
            else:
                # print(i, "u", self.updates[i]["u"])
                # print("snapshot['lastUpdatedId']", self.snapshot["lastUpdateId"])
                if self.updates[i]["u"] < self.snapshot["lastUpdateId"]:
                    self.updates.pop(i)
                else:
                    for bid in self.updates[i]["b"]:
                        self.bids[float(bid[0])] = float(bid[1])
                    for ask in self.updates[i]["a"]:
                        self.asks[float(ask[0])] = float(ask[1])
        # self.bids = dict(sorted(self.bids, reverse=True), )
        self.bids = OrderedDict(sorted(self.bids.items(), reverse=True))
        self.asks = OrderedDict(sorted(self.asks.items()))
        # print(self.bids)
        # print(list(self.bids.items())[0][0])


    def update_console(self):
        # pass
        print("\rBUY: %f\tSELL: %f" % (self.get_average_price(False), self.get_average_price(True)), end='')

    # bid has value of False, ask has value of True for parameter side
    def get_average_price(self, side):
        book = self.bids
        avg = float(0)
        if side:
            book = self.asks
        quantity = float(0)
        index = 0
        book = list(book.items())
        while quantity < self.volume:
            curr_order = book[index]
            price = curr_order[0]
            volume = curr_order[1]
            new_quantity = min(volume, self.volume-quantity) # volume filled
            quantity += new_quantity
            avg += new_quantity*price
            index += 1
        avg = avg / self.volume
        return avg


# if __name__ == "__main__":
#     if not len(sys.argv) == 3:
#         print("Need quantity and Pair")
#         sys.exit()
#     try:
#         pair = sys.argv[1]
#         volume = float(sys.argv[2])
#         if volume < 0:
#             raise ValueError
#     except Exception as e:
#         print("Invalid quantity")
#         sys.exit()

#     # instantiate websocket
#     websocket = BinanceWebsocket()

#     # instantiate orderbook
#     BTCUSDT_Book = OrderBook(websocket, f"https://www.binance.com/api/v1/depth?symbol={pair}&limit=1000", pair, volume)
    
#     # start receiving updates
#     asyncio.get_event_loop().run_until_complete(BTCUSDT_Book.get_orders())

websocket = BinanceWebsocket()
BTCUSDT_Book = OrderBook(websocket, f"https://www.binance.com/api/v1/depth?symbol=BTCUSDT&limit=1000", "BTCUSDT", 10)
asyncio.get_event_loop().run_until_complete(BTCUSDT_Book.get_orders())
# OrderBook.get_orders()