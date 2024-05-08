from concurrent import futures
import os
import time
import grpc
from grpc_reflection.v1alpha import reflection

from Test_pb2 import  ClientStreamResponse, FileUploadRequest, FileUploadResponse, TestResponse
import Test_pb2
from Test_pb2_grpc import TestServiceServicer, TestServiceStub, add_TestServiceServicer_to_server

channel = grpc.insecure_channel("localhost:50051")
stub = TestServiceStub(channel)

CHUNK_SIZE = 1024 * 300

def generate_file_chunks(filepath):
    with open(filepath, "rb") as file:
        while True:
            file_part = file.read(CHUNK_SIZE)

            if len(file_part) == 0:
                return
            
            yield FileUploadRequest(chunk=file_part)

def upload(chunks, filepath):
    start = time.time()
    with open(filepath, "wb") as f:
        for chunk in chunks:
            f.write(chunk.chunk)

    total = (time.time() - start) * 1000
    return f"{total:.2f}ms"

class MyTestService(TestServiceServicer):
    def UnaryRequest(self, request, context):
        print("Server received an unary request")
        print("Request contains : " + request.msg)        
        return TestResponse(reply="This is reply from grpc server")
    
    def ServerStreaming(self, request, context):
        n = request.n
        print(f"Server received a server stream request. Number : {request.n}")

        for i in range(n):
            resp = TestResponse(reply=f"{i+1}.Reply from server. Wait for remaining({i+1}/{n})")
            yield resp
            time.sleep(2)

    def FileUpload(self, request_iterator, context):
        print("server received file upload request")
        FILE_NAME = "uploads/test.mp4"

        time = upload(request_iterator, FILE_NAME)
        return FileUploadResponse(
            length=os.path.getsize(FILE_NAME),
            time = time
        )

    def ClientStreaming(self, request_iterator, context):
        client_stream_request = ClientStreamResponse()

        for request in request_iterator:
            print("server received request : " + request.msg)
            client_stream_request.requests.append(request)

        client_stream_request.noOfRequest = len(client_stream_request.requests)
        return client_stream_request

    def BiDirectionalRequest(self, request_iterator, context):
        print("Server received a bi directional request")
        for request in request_iterator:
            print("Request contains : " + request.msg)        
            yield TestResponse(reply="This is reply from grpc server")

    def FileUploadTest(self, request, context):
        print(request)
        path = request.path
        resp = stub.FileUpload(generate_file_chunks(path))
        return resp


def run():
    SERVICE_NAMES =  (
        Test_pb2.DESCRIPTOR.services_by_name["TestService"].full_name,
        reflection.SERVICE_NAME,
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    server.add_insecure_port("localhost:50051")
    
    add_TestServiceServicer_to_server(MyTestService(), server)

    reflection.enable_server_reflection(SERVICE_NAMES, server)

    print("server started at localhost:50051.....")
    server.start()
    
    server.wait_for_termination()

if __name__ == "__main__":
    run()
