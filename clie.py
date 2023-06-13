import asyncio


class Client:
    def __init__(self):
        self.started = False
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None

    async def run(self):
        self.reader, self.writer = await asyncio.open_connection("localhost", 5556)
        self.started = True

    async def send_task(self) -> None:
        while not self.started:
            await asyncio.sleep(1)
        while True:
            self.writer.write(b"hello gg!")
            await self.writer.drain()
            await asyncio.sleep(1)
            print(await self.recv())

    async def receive_data(self) -> None:
        while not self.started:
            await asyncio.sleep(1)
        while True:
            print(await self.reader.read(1024))
            print("hello!")

    async def recv(self) -> bytes:
        return await self.reader.read(1024)


if __name__ == "__main__":
    client = Client()
    asyncio.run(
        asyncio.wait(
            [
                client.run(),
                # client.receive_data(),
                client.send_task(),
            ]
        )
    )
