# Balboa

Balboa is a lightweight Python web framework inspired by Ruby's Sinatra. It provides simple, intuitive APIs for HTTP routing, WebSocket handlers, Server-Sent Events (SSE), and static file serving.

## Features
- HTTP routing with URL parameters and query parsing
- Template rendering using plain HTML files
- Static file serving
- WebSocket endpoints for real-time communication
- Server-Sent Events (SSE) for server push updates

## How It Works

Balboa leverages Python's `with` statement and context managers to build its DSL for route definition. Each routing method (`app.get`, `app.post`, etc.) returns a context object that:

- Implements `__enter__` and `__exit__`.
- In `__enter__`, it yields a context (`RouteContext`, `WebSocketContext`, or `SSEContext`).
- Inside the `with` block, you specify your handler via `send`, `json`, or similar methods.
- On exiting the block (`__exit__`), the context automatically registers the route or handler with the framework.

Example:
```python
with app.get('/hello') as route:
    route.send(lambda: 'Hello, World!', 'text/plain')
```

This is equivalent to explicitly calling:
```python
response = Response(lambda: 'Hello, World!', 'text/plain')
app.add_route('GET', '/hello', response)
```

Similar patterns apply to WebSockets and SSE:
```python
with app.ws('/chat') as ws_ctx:
    ws_ctx.send(chat_handler)

with app.sse('/events') as sse_ctx:
    sse_ctx.send(event_handler)
```

## Installation
Requires Python 3.8 or higher.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/balboa.git
   cd balboa
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Example Applications

### Main Demo (`main.py`)
Demonstrates various HTTP routes and template rendering:
- `/` : Plain text response
- `/search?name=<name>` : Query parameter handling
- `/balboa?name=<name>&ri=1` : Renders HTML templates and images
- `/sphere?radius=<r>` : Sphere surface area calculator
- `/cylinder?radius=<r>&height=<h>` : Cylinder surface area calculator

Run:
```bash
python main.py
```
Browse to `http://127.0.0.1:9000`.

### Minimal Example (`minimal.py`)
Basic GET routes:
```bash
python minimal.py
```

### Sinatra-Style DSL (`sinatra.py`)
Similar to Ruby's Sinatra syntax:
```bash
python sinatra.py
```

### FastAPI WebSocket Chat (`fastapi_ws.py`)
Simple WebSocket chat server with FastAPI:
```bash
uvicorn fastapi_ws:app --reload --port 9000
```

### Other Demos
- `new_balboa.py`: Alternative decorator-based routing
- `await_with.py`: Async context manager example
- `with_exit.py`: Synchronous context manager example
- `love_types.py`: Python typing demo
- `db.py`: In-memory data store for examples

## Project Structure
```
. ├── balboa/            # Framework source and logo
│   ├── core.py
│   └── balboa.png
. ├── main.py            # Main Balboa app demo
. ├── minimal.py         # Minimal routing example
. ├── sinatra.py         # Sinatra-like DSL demo
. ├── new_balboa.py      # Decorator DSL example
. ├── fastapi_ws.py      # FastAPI WebSocket demo
. ├── await_with.py      # Async context manager demo
. ├── with_exit.py       # Context manager demo
. ├── love_types.py      # Typing demo
. ├── db.py              # Simple in-memory database
. ├── *.html             # HTML templates for demos
. ├── requirements.txt   # Python dependencies
. └── README.md          # Project overview
```

## Contributing
Contributions are welcome! Please open issues or pull requests for bug fixes, enhancements, or new examples.

## License
This project does not include a license. Add an appropriate `LICENSE` file to specify terms.