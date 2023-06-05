import websocket


def on_message(_wsa, data):
    print(data)


def run():
    stream_name = "btcusdt@depth"
    wss = f'wss://stream.binance.com:9443/ws/{stream_name}'
    wsa = websocket.WebSocketApp(wss, on_message=on_message)
    wsa.run_forever()


if __name__ == "__main__":
    run()
