import asyncio
import json
import re
import os
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)
from urllib.parse import parse_qs

Scope = Dict[str, Any]
Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]
Handler = Union[Callable[..., str], str]


class Request:
    def __init__(self, params):
        self.params: Dict[str, Any] = {
            k: (v if isinstance(v, str) else v[0]) for k, v in params.items()
        } | {f"{k}[]": v for k, v in params.items()}


class Response:
    def __init__(self, handler: Handler, content_type: str = "text/html"):
        self.handler = (
            handler if callable(handler) else lambda _: handler.format(**_.params)
        )
        self.content_type = content_type

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        params = {
            **scope["path_params"],
            **dict(parse_qs(scope["query_string"].decode())),
        }
        body = self.handler(Request(params)).encode()
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", self.content_type.encode())],
            }
        )
        await send({"type": "http.response.body", "body": body})


class SSEWrapper:
    def __init__(self, handler: Union[Callable[..., Awaitable[None]], str]):
        if callable(handler):
            self.handler = handler
        else:

            async def new_handler(sse: SSEvent) -> None:
                while True:
                    await sse.send(handler)
                    await asyncio.sleep(1)

            self.handler = new_handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        params = {
            **scope["path_params"],
            **dict(parse_qs(scope["query_string"].decode())),
        }
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"text/event-stream"),
                    (b"cache-control", b"no-cache"),
                    (b"connection", b"keep-alive"),
                ],
            }
        )
        try:
            await self.handler(SSEvent(sender=send), **params)
        except asyncio.CancelledError:
            pass


class SSEvent:
    """
    Server-Sent Events (SSE) is a server push technology enabling a client to
    receive automatic updates from a server via HTTP connection.
    """

    def __init__(self, sender: Send):
        self.sender = sender

    async def send(self, message: str) -> None:
        data = f"data: {message}\n\n".encode("utf-8")
        await self.sender(
            {"type": "http.response.body", "body": data, "more_body": True}
        )


class WebSocketWrapper:
    clients: Set["WebSocket"] = set()

    def __init__(
        self,
        handler: Union[Callable[["WebSocket", Set["WebSocket"]], Awaitable[None]], str],
    ):
        if callable(handler):
            self.handler = handler
        else:

            async def new_handler(ws: "WebSocket", cls: Set["WebSocket"]) -> None:
                async with await ws.sender(handler):
                    pass

            self.handler = new_handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ws = WebSocket(scope, receive, send)
        await ws.accept()
        self.clients.add(ws)
        await self.handler(ws, self.clients)


class WebSocket:
    """
    WebSocket is a communication protocol that provides full-duplex
    communication channels. It is a persistent connection between a client
    and server that both parties can use to start sending data at any time.
    """

    def __init__(self, scope: Scope, receive: Receive, send: Send):
        self.scope = scope
        self.receive = receive
        self.send = send
        self.connected = True

    async def accept(self) -> None:
        await self.send({"type": "websocket.accept"})

    async def sender(self, message: str):
        await self.send({"type": "websocket.send", "text": message})
        return self

    async def receiver(self) -> Optional[str]:
        event = await self.receive()
        print(f"Event: {event}")
        print(f"Client: {self}")
        print(f"Clients: {WebSocketWrapper.clients}")
        match event.get("type"):
            case "websocket.receive":
                return event.get("text", "")
            case "websocket.disconnect":
                self.connected = False
                WebSocketWrapper.clients.remove(self)
                return None
            case _:
                pass

    async def close(self) -> None:
        await self.send({"type": "websocket.close"})
        WebSocketWrapper.clients.remove(self)

    def __aenter__(self):
        return self

    def __await__(self):
        yield

    async def __aexit__(self, *_) -> None:
        await self.close()

    async def iter(self) -> AsyncGenerator[str, None]:
        while self.connected:
            message = await self.receiver()
            await asyncio.sleep(0.1)
            if message:
                yield message

    async def broadcast(self, clients: Set["WebSocket"], message: str) -> None:
        for client in clients:
            await client.sender(message)


class Framework:
    routes: List[Tuple[str, re.Pattern[str], Response]]
    ws_routes: List[Tuple[re.Pattern[str], WebSocketWrapper]]
    sse_routes: List[Tuple[re.Pattern[str], SSEWrapper]]
    static_files: Tuple[str, str]

    def add_route(self, method: str, path: str, response: Response) -> None:
        path_regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)
        self.routes.append((method, re.compile(f"^{path_regex}$"), response))

    def add_websocket_route(self, path: str, handler: WebSocketWrapper) -> None:
        path_regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)
        self.ws_routes.append((re.compile(f"^{path_regex}$"), handler))

    def add_sse_route(self, path: str, handler: SSEWrapper) -> None:
        path_regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)
        self.sse_routes.append((re.compile(f"^{path_regex}$"), handler))

    def _set_static_files(self, url_prefix: str, directory: str) -> None:
        self.static_files = (url_prefix, directory)

    def _get_mime_type(self, file_path: str) -> str:
        # Simplistic MIME type determination
        ext = os.path.splitext(file_path)[1]
        mime_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".json": "application/json",
            ".pdf": "application/pdf",
            # Add more MIME types as needed
        }
        return mime_types.get(ext, "application/octet-stream")


class RouteContext:
    def __init__(self, method: str, path: str, framework: Framework):
        self.method = method
        self.path = path
        self.response: Optional[Response] = None
        self.framework = framework

    def __enter__(self):
        return self

    def __exit__(self, *_) -> None:
        if self.response:
            self.framework.add_route(self.method, self.path, self.response)
        del self.method
        # del self.path
        # del self.response

    def send(self, handler: Handler, type="text/html") -> None:
        self.response = Response(handler, type)

    def json(self, handler: Handler) -> None:
        self.response = Response(handler, "application/json")
    
    def render(self, template: str, kwargs) -> str:
        with open(template) as file:
            return file.read().format(**kwargs)


class WebSocketContext:
    def __init__(self, path: str, framework: Framework):
        self.path = path
        self.handler: Optional[WebSocketWrapper] = None
        self.framework = framework

    def __enter__(self):
        return self

    def __exit__(self, *_) -> None:
        if self.handler:
            self.framework.add_websocket_route(self.path, self.handler)
        del self.path
        del self.handler

    def send(
        self,
        handler: Union[Callable[["WebSocket", Set["WebSocket"]], Awaitable[None]], str],
    ) -> None:
        self.handler = WebSocketWrapper(handler)


class SSEContext:
    def __init__(self, path: str, framework: Framework):
        self.path = path
        self.handler: Optional[SSEWrapper] = None
        self.framework = framework

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        if self.handler:
            self.framework.add_sse_route(self.path, self.handler)
        del self.path
        del self.handler

    def send(self, handler: Union[Callable[..., Awaitable[None]], str]) -> None:
        self.handler = SSEWrapper(handler)


class Balboa(Framework):
    """
    Balboa is a simple web framework that provides routing for HTTP,
    WebSocket and Server-Sent Events (SSE) protocols.
    """

    def __init__(self, name: str = __name__):
        super()
        self.name = name
        self.routes = []
        self.ws_routes = []
        self.sse_routes = []
        self.static_files = ("/static", "static")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            path = scope["path"]
            method = scope["method"]

            # Serve static files
            static_prefix, static_dir = self.static_files
            if path.startswith(static_prefix):
                file_path = os.path.join(
                    static_dir, path[len(static_prefix) :].lstrip("/")
                )
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as file:
                        content = file.read()
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 200,
                            "headers": [
                                (
                                    b"content-type",
                                    self._get_mime_type(file_path).encode(),
                                ),
                                (b"content-length", str(len(content)).encode()),
                            ],
                        }
                    )
                    await send({"type": "http.response.body", "body": content})
                    return
                else:
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 404,
                            "headers": [(b"content-type", b"text/plain")],
                        }
                    )
                    await send(
                        {"type": "http.response.body", "body": b"File Not Found"}
                    )
                    return

            for route_method, route_regex, response in self.routes:
                if route_method == method:
                    match = route_regex.match(path)
                    if match:
                        scope["path_params"] = match.groupdict()
                        await response(scope, receive, send)
                        return
            for route_regex, handler in self.sse_routes:
                match = route_regex.match(path)
                if match:
                    scope["path_params"] = match.groupdict()
                    await handler(scope, receive, send)
                    return
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "headers": [(b"content-type", b"text/plain")],
                }
            )
            await send({"type": "http.response.body", "body": b"Not Found"})

        elif scope["type"] == "websocket":
            path = scope["path"]
            for route_regex, handler in self.ws_routes:
                match = route_regex.match(path)
                if match:
                    scope["path_params"] = match.groupdict()
                    await handler(scope, receive, send)
                    return
            await send({"type": "websocket.close"})

    def get(self, path: str) -> RouteContext:
        return RouteContext("GET", path, self)

    def post(self, path: str) -> RouteContext:
        return RouteContext("POST", path, self)

    def put(self, path: str) -> RouteContext:
        return RouteContext("PUT", path, self)

    def patch(self, path: str) -> RouteContext:
        return RouteContext("PATCH", path, self)

    def delete(self, path: str) -> RouteContext:
        return RouteContext("DELETE", path, self)

    def ws(self, path: str) -> WebSocketContext:
        return WebSocketContext(path, self)

    def sse(self, path: str) -> SSEContext:
        return SSEContext(path, self)

    def head(self, path: str) -> RouteContext:
        return RouteContext("HEAD", path, self)

    def options(self, path: str) -> RouteContext:
        return RouteContext("OPTIONS", path, self)
    
    def mount(self, parent_path: str, router=None, dir=None) -> None:
        if dir:
            self._set_static_files(parent_path, dir)
        elif isinstance(router, RouteContext):
            for route in self.routes:
                if router.response in route:
                    method = route[0]
                    child_path = '' if router.path == '/' else router.path
                    path = f'{parent_path}{child_path}'
                    self.routes.remove(route)
                    self.add_route(method, path, router.response)


    def run(self, host: str = "127.0.0.1", port: int = 9000) -> None:
        import uvicorn

        uvicorn.run(self, host=host, port=port)
