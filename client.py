import logging

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


def request_num(stub, num):
    responses = stub.SumServer(generate_requests([num]))
    for r in responses:
        print(r.sum)


def run():
    print('init run...')
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = sum_pb2_grpc.SumServiceStub(channel)
        print('add 1')
        request_num(stub, 1)
        print('add 2')
        request_num(stub, 2)
        print('add 3')
        request_num(stub, 3)
        print('add 4')
        request_num(stub, 4)
        print('add 5')
        request_num(stub, 5)


if __name__ == '__main__':
    logging.basicConfig()
    run()