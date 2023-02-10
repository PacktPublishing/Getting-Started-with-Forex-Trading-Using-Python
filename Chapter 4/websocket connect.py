import websocket

url = "wss://public-data-api.london-demo.lmax.com/v1/web-socket"
ws = websocket.WebSocket()
ws.connect(url)
req = '{"type": "SUBSCRIBE","channels": [{"name": "ORDER_BOOK","instruments": ["eur-usd"]},{"name": "TICKER","instruments":["usd-jpy"]}]}'
ws.send(req)
print(ws.recv())