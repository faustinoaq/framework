class AsyncContextManager:
    def __init__(self, resource):
        self.resource = resource

    async def __aenter__(self):
        # Asynchronous code to acquire the resource
        await self.acquire_resource()
        return self

    async def acquire_resource(self):
        # Simulate an asynchronous resource acquisition
        print("Acquiring resource...")
        await asyncio.sleep(1)
        print("Resource acquired.")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Asynchronous code to release the resource
        await self.release_resource()

    async def release_resource(self):
        # Simulate an asynchronous resource release
        print("Releasing resource...")
        await asyncio.sleep(1)
        print("Resource released.")

    def __await__(self):
        # This makes the object awaitable
        async def coro():
            return self
        return coro().__await__()

# Usage of the asynchronous context manager
async def main():
    async with AsyncContextManager("my_resource") as manager:
        print("Inside the context")

# Run the main coroutine
import asyncio
asyncio.run(main())
