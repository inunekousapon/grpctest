## 目的

PythonでgRPCを双方向通信させる。
ただし、全て非同期で行う。

今回はクライアントで入力した数字をサーバー側に送信すると、過去に送信した全ての数字を加算したものを返却するものを作成する。

## 環境

- Python 3.9.7
- Windows10 Pro


## 手順

参考サイト。
https://grpc.io/docs/languages/python/basics/

VSCodeを管理者権限で実行します。

基本のバーチャル環境から作成します。

```sh
python -m venv venv
venv\Scripts\activate.bat
pip install -U pip
```


requirements.txtをルートディレクトリに作成します。

```requirements.txt
grpcio==1.40.0
grpcio-tools==1.40.0
```

下記コマンドを実行。

```sh
pip install -r requirements.txt
```

## サービスを定義する

`sum.proto` をルートディレクトリに作成します。

通信の種類は4種類ありますが、今回は双方向通信を取り扱います。

```sum.proto
syntax = "proto3";

package sum;

message RequestMessage {
    int32 num = 1;
}

message ReplyMessage {
    int32 sum = 1;
}

service SumService {
  rpc SumServer (stream RequestMessage) returns (stream ReplyMessage) {}
}
```

## 定義からコードを自動生成

`codegen.py` をルートディレクトリに作成します。

```codegen.py
from grpc.tools import protoc


protoc.main(
    (
        '',
        '-I.',
        '--python_out=.',
        '--grpc_python_out=.',
        './sum.proto',
    )
)
```

codegen.pyを実行します。

```sh
$ python codegen.py
```

ルートディレクトリに下記のファイルが生成されました。
- sum_pb2_grpc.py
- sum_pb2.py


## サーバーの実装

`server.py` をルートディレクトリに作成します。

```server.py
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
```


## クライアントの実装

`client.py` をルートディレクトリに作成します。
まずは非同期を考えないで書いてみます。

```client.py
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
```

サーバーを起動します。

```
python server.py
```

下記の出力が出るはずです。

```
init server...
start server.
```

続けてクライアントを実行します。

```
python client.py
```

下記の出力が出るはずです。

```
1
add 2
3
add 3
6
add 4
10
add 5
15
```