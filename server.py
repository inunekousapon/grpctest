import logging
from concurrent import futures
import time

import grpc
import sum_pb2
import sum_pb2_grpc


class SumServicer(sum_pb2_grpc.SumServiceServicer):
    def __init__(self):
        self.sum = 0

    def SumServer(self, request_iterator, context):
        for new_request in request_iterator:
            time.sleep(1)
            self.sum += new_request.num
            yield sum_pb2.ReplyMessage(sum=self.sum)


def serve():
    print("init server...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sum_pb2_grpc.add_SumServiceServicer_to_server(SumServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('start server.')
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()