import asyncio


class Client:
    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self.reader = reader
        self.writer = writer

    async def handler(self):
        while True:
            print(await self.reader.read(1024))
            self.writer.write(b"hello!")
            await self.writer.drain()

    async def send_random(self, random: bytes):
        self.writer.write(random)
        await self.writer.drain()


class Server:
    def __init__(self) -> None:
        self.socket = None
        self.clients = []

    async def run(self) -> None:
        socket = self.socket = await asyncio.start_server(
            self.handle_client, "0.0.0.0", 5556
        )
        async with socket:
            await socket.serve_forever()

    async def handle_client(self, reader, writer):
        client = Client(reader, writer)
        self.clients.append(client)
        await client.handler()


async def ping(server: Server) -> None:
    """print dots to indicate idleness"""
    await asyncio.sleep(10)
    while True:
        await asyncio.sleep(0.5)
        # print("something!")
        await server.clients[0].send_random(b"7612561")


if __name__ == "__main__":
    server = Server()
    asyncio.run(asyncio.wait([server.run(), ping(server)]))
