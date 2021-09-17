import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import grpc
import sum_pb2
import sum_pb2_grpc


def make_request(num):
    return sum_pb2.RequestMessage(
        num=num
    )


def generate_requests(num_list):
    messages = [make_request(num) for num in num_list]
    for msg in messages:
        yield msg


async def request_loop(stub, req_queue, res_queue):
    while True:
        num = await req_queue.get()
        response = stub.SumServer(generate_requests([num]))
        req_queue.task_done()
        async for r in response:
            await res_queue.put(r.sum)


async def response_loop(res_queue):
    while True:
        sum = await res_queue.get()
        print(f"{sum} is return.")
        res_queue.task_done()


async def ainput(prompt: str = "") -> str:
    with ThreadPoolExecutor(1, "AsyncInput") as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)


async def run():
    print('init run...')
    req_queue = asyncio.Queue()
    res_queue = asyncio.Queue()
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = sum_pb2_grpc.SumServiceStub(channel)

        asyncio.create_task(request_loop(stub, req_queue, res_queue))
        asyncio.create_task(response_loop(res_queue))
        while True:
            number = await ainput('')
            if number.isdigit():
                await req_queue.put(int(number))
            else:
                print("input wrong.")


if __name__ == '__main__':
    logging.basicConfig()
    asyncio.run(run())