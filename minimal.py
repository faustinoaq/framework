# from balboa import Balboa, WebSocket
from balboa import Balboa

app = Balboa(__name__)

with app.get('/') as r:
    r.send('Hello, World!')

with app.get('/{name}') as r:
    r.send(lambda name: f'Hello, {name}!')

# with app.get('/{name}') as ctx:
#     def hello(name):
#         return f'Hello, {name}!'
#     ctx.send(hello)

# with (app.get('/api') as api,
#       app.get('/data') as data):
#     handler = lambda: {'status': 'ok'}
#     api.json(handler)
#     data.json(handler)

# # Basic echo sockets server
# with app.ws('/ws') as ctx:
#     async def handler(ws: WebSocket, *args):
#         async for _ in ws.iter():
#             async with await ws.sender('pong'):
#                 break
#     ctx.send(handler)

# with app.sse('/see') as ctx:
#     async def handler(sse):
#         await sse.send(f'data: event\n\n')
#     ctx.send(handler)

# with app.get('/{name}') as (req, res):
#     res.send(f'<p>Hello, {req.params.name}!</p>')

# with app.get('/{name}') as r:
#     r.send(lambda name: f'Hello, {name}!')

# with app.get('/{name}') as r:
#     r.send(lambda name: (
#         name := name.capitalize(),
#         f'Hello, {name}!'
#     )[-1])

# with app.get('/{name}') as r:
#     def hello(name):
#         return f'Hello, {name}!'
#     r.send(hello)

# with app.get('/{name}') as r:
#     @r.send
#     def hello(name):
#         return f'Hello, {name}!'

# with app.get('/{name}') as route:
#     def hello(req: Request):
#         return f'Hello, {req.params.name}!'
#     route.bind(hello)

# route = app.get('/{name}')
# route.bind_exit(hello)
#     def hello(req: Request):
#         return f'Hello, {req.params.name}!'
#     route.bind(hello)
