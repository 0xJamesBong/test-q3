
import json
import websocket
# https://stackoverflow.com/questions/67774825/binance-websocket-order-book-depths-change-every-time
socket = 'wss://stream.binance.com:9443/ws'


def on_open(self):
    print("opened")
    subscribe_message = {
        "method": "SUBSCRIBE",
        "params":
        [
            "btcusdt@depth@100ms"
        ],
        "id": 1
    }

    ws.send(json.dumps(subscribe_message))


def on_message(self, message):
    print("received a message")

    ###### depths of bid/ask ######
    d = json.loads(message)
    print(d)
    # for k, v in d.items():
    #     if k == "b":
    #         print(f"bid depth : {len(v)}")
    #     if k == "a":
    #         print(f"ask depth : {len(v)}")


def on_close(self):
    print("closed connection")


ws = websocket.WebSocketApp(socket,
                            on_open=on_open,
                            on_message=on_message,
                            on_close=on_close)

ws.run_forever()
