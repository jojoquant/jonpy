from jnpy.app.grpc_service.proto import hello_pb2, hello_pb2_grpc
import grpc

if __name__ == '__main__':
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = hello_pb2_grpc.GreeterStub(channel)
        rsp: hello_pb2.HelloReply = stub.SayHello(hello_pb2.HelloRequest(name="fangyang"))
        print(rsp.message)