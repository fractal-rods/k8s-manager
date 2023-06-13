import asyncio
from threading import Lock
import time
from typing import List
import subprocess
import random


class Task:
    def __init__(self, name) -> None:
        self.lock = Lock()
        self.counter = 1
        self.id = name


tasks_list: List[Task] = []


async def add_task():
    c = 1
    while c < 100:
        tasks_list.append(Task(c))
        c += 1
        await asyncio.sleep(0.01)


async def edit_task() -> None:
    while True:
        for t in tasks_list:
            # with t.lock:
            t.counter += 1

            print("task id:", t.id, "counter", t.counter)

        await asyncio.sleep(0.001)


def delete_task() -> None:
    while True:
        for t in tasks_list:
            # with t.lock:
            if t.counter > 6:
                tasks_list.remove(t)
                print("task deleted", t.id, t.counter)

        time.sleep(0.1)


async def rnd_sleep(t):
    # sleep for T seconds on average
    await asyncio.sleep(t * random.random() * 2)


async def producer(queue):
    while True:
        # produce a token and send it to a consumer
        token = random.random()
        print(f"produced {token}")
        if token < 0.05:
            break
        await queue.put(token)
        await rnd_sleep(0.1)


async def consumer(queue: asyncio.Queue):
    while True:
        token = await queue.get()
        # process the token received from a producer
        await rnd_sleep(0.3)
        queue.task_done()
        print(f"consumed {token}")


async def main():
    queue = asyncio.Queue()

    # fire up the both producers and consumers
    producers = [asyncio.create_task(producer(queue)) for _ in range(3)]
    consumers = [asyncio.create_task(consumer(queue)) for _ in range(10)]

    # with both producers and consumers running, wait for
    # the producers to finish
    await asyncio.gather(*producers)
    print("---- done producing")

    # wait for the remaining tasks to be processed
    await queue.join()

    # cancel the consumers, which are now idle
    for c in consumers:
        c.cancel()


def fun_sync_blocking():
    for i in range(10):
        print("sync_blocking outputs", i)
        # await asyncio.sleep(1)
        time.sleep(1)


async def async_blocking():
    for i in range(10):
        print("async blocking outputs", i)
        await asyncio.sleep(1)


async def main_test_async_sync():
    print("start main_test_async_sync")
    asyncio.to_thread(fun_sync_blocking)
    await fun_sync_blocking()
    print("end main_test_async_sync")


def run_thread_subprocess():
    print("running hello.py")
    process: subprocess.Popen = subprocess.Popen(
        ["python", "hello.py", "3"], stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    print("reading data")
    while True:
        line = process.stdout.readline()
        if line == b"":
            break
        print(line)


if __name__ == "__main__":
    # t = Thread(target=delete_task, args=())
    # t.start()
    # q = asyncio.Queue()
    # asyncio.run(
    #     asyncio.wait(
    #         [
    #             k1(q),
    #             main(q),
    #             # add_task(),
    #             # edit_task(),
    #             #delete_task(),
    #         ]
    #     )
    # )
    # asyncio.run(main())

    # asyncio.run(
    #     main_test_async_sync()
    # )

    run_thread_subprocess()
