# import asyncio
# import json
# from db import db
# from balboa import Balboa, Request

from balboa import Balboa
import math

app = Balboa(__name__)

with app.get('/') as res:
    res.send('Hello, World!', 'text/plain')

with app.get('/search') as res:
    def hello(req):
        name = req.params.get('name')
        return f'Hello, {name}!' if name else 'Hello, World!'
    res.send(hello, 'text/plain')

app.mount('/framework', dir='balboa')

names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']

with app.get('/balboa') as res:
    def balboa(req):
        name = req.params.get('name')
        ri = req.params.get('ri')
        hello = ''
        for n in names:
            hello += res.render('hello.html', locals()) if name else ''
            name = n
        image = res.render('image.html', locals()) if ri == '1' else ''
        return res.render('balboa.html', locals())
    res.send(balboa)

with app.get('/') as about:
    about.send('Hello!')

with app.get('/{name}/hello') as about_hello:
    about_hello.send('Hello, {name}!')

with app.get('/{name}') as about_name:
    def handler(req):
        name = req.params.get('name')
        age = req.params.get('age') or 10
        detail = f' and you are {age} years old' if age else ''
        return f'Your name is {name}{detail}.'
    about_name.send(handler, 'text/plain')

# Sphere surface area endpoint
with app.get('/sphere') as res:
    def sphere(req):
        # read radius from query parameter 'radius' or 'r'
        radius = req.params.get('radius') or req.params.get('r')
        try:
            radius = float(radius)
        except (TypeError, ValueError):
            return '<p>Invalid radius provided.</p>'
        # compute surface area of a sphere
        area = 4 * math.pi * radius * radius
        # render HTML template with computed values
        return res.render('sphere.html', locals())
    res.send(sphere)

# Cylinder surface area endpoint
with app.get('/cylinder') as res:
    def cylinder(req):
        # read radius and height from query parameters
        radius = req.params.get('radius') or req.params.get('r')
        height = req.params.get('height') or req.params.get('h')
        try:
            radius = float(radius)
            height = float(height)
        except (TypeError, ValueError):
            return '<p>Invalid radius or height provided.</p>'
        # compute total surface area of cylinder: 2πr(r + h)
        area = 2 * math.pi * radius * (radius + height)
        # render HTML template with computed values
        return res.render('cylinder.html', locals())
    res.send(cylinder)

# with app.get('/.*') as any:
#     any.send('Hello anything!')

app.mount('/about', about_name)
app.mount('/about', about_hello)
app.mount('/about', about)

if __name__ == '__main__':
    app.run()

# with app.not_found() as res:
#     res.send('404 Not Found')

# with app.internal_server_error() as res:
#     res.send('500 Internal Server Error')

# with app.forbidden() as res:
#     res.send('403 Forbidden')

# with app.get('/search') as route:
#     def search(request: Request):
#         key = request.params.get('query', '')
#         result = db.get(key, 'Not found')
#         return json.dumps({'result': result})
#     route.json(search)

# with app.post('/{name}') as r:
#     r.send(lambda name: f'Hello, {name}!')

# with app.put('/update/{id}') as r:
#     def update(id, **params):
#         print(f'db {id}: {db}')
#         db.update(params)
#         print(f'db: {db}')
#         return json.dumps({"status": "updated", "params": db})
#     r.json(update)

# with app.patch('/update') as r:
#     def patch_body(**params):
#         return json.dumps({"status": "patched", "params": params})
#     r.json(patch_body)

# with app.delete('/delete') as r:
#     def delete_handler(**params):
#         return json.dumps({"status": "deleted", "params": params})
#     r.json(delete_handler)

# with app.ws('/chat') as socket:
#     async def chat_handler(ws: WebSocket, clients):
#         async for msg in ws.iter():
#             await ws.broadcast(clients, msg)
#     socket.send(chat_handler)

# with app.sse('/events') as sse:
#     async def event_handler(sse: SSEvent):
#         for i in range(5):
#             await sse.send(f'data: {i} This is a server-sent event\n\n')
#             await asyncio.sleep(1)
#     sse.send(event_handler)

# if __name__ == '__main__':
#     app.run()


# with app.get('/') as r:
#     r.send('Hello, World!')

# with app.get('/transaction') as r:
#     r.start_transaction()
#     # Perform database operations
#     r.commit_transaction()

# with app.get('/secured') as r:
#     r.use_middleware(auth_middleware)
#     r.send('Secured resource')

# with app.get('/log') as r:
#     r.start_logging()
#     r.send('This request is being logged')
