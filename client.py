import time
import grpc

from Test_pb2 import FileUploadRequest, FileUploadRequestStr, ServerStreamRequest, TestRequest
from Test_pb2_grpc import TestServiceStub


channel = grpc.insecure_channel("localhost:50051")
stub = TestServiceStub(channel)

CHUNK_SIZE = 1024 * 300

def generate_file_parts(filepath):
    with open(filepath, "rb") as file:
        while True:
            file_part = file.read(CHUNK_SIZE)

            if len(file_part) == 0:
                return
            
            yield FileUploadRequest(chunk=file_part)

def generate_client_request(n):
    for i in range(n):
        yield TestRequest(msg=f"This is request no:{i + 1}")
        time.sleep(1)


def server_stream_request():
    print("sending server stream request")

    responses = stub.ServerStreaming(ServerStreamRequest(n = 4))
    for response in responses:
        print(response.reply)

def unary_request():
    print("Sending unary request to client")

    resp = stub.UnaryRequest(TestRequest(msg="I am grpc client"))
    print(resp.reply)

def file_upload_request():
    print("Uploading file to server")

    filename = "test.mp4"
    resp = stub.FileUpload(generate_file_parts(filename))
    print(resp)

def file_upload_test_request():
    print("Uploading file to server")

    req = FileUploadRequestStr(path="test.mp4")
    resp = stub.FileUploadTest(req)
    print(resp)

def client_stream_request(n):
    print("making client stream request")

    resp = stub.ClientStreaming(generate_client_request(n))

    print(resp)
    print(f"server received {resp.noOfRequest} number of requests, They are")
    for request in resp.requests:
        print(request.msg)

def bi_directional_request(n):
    print("making bi directional request")

    responses = stub.BiDirectionalRequest(generate_client_request(n))
    for resp in responses:
        print(resp)

if __name__ == "__main__":
    # unary_request()
    # server_stream_request()
    # file_upload_request()
    # client_stream_request(3)
    # bi_directional_request(5)
    file_upload_test_request()