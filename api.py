from flask_restx import Api, Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage
from flask import Flask, request
import time

app = Flask(__name__)

api = Api(
    app=app,
    title="File Upload Test",
    description="This api is used to test File Upload",
    validate=True,
    version="1.0",
    doc="/"
)

file_upload_controller = Namespace("file-upload", path="/upload")

file_upload_args = reqparse.RequestParser()
file_upload_args.add_argument(
    name="file",
    location="files",
    type=FileStorage,
    required=True
)

@file_upload_controller.route("/")
class FileUploadResource(Resource):
    @file_upload_controller.expect(file_upload_args)
    def post(self):
        start = time.time()
        args = file_upload_args.parse_args()
        file = args["file"]
        # print(file)
        file_bytes = file.read()

        with open("uploads/test.mp4", "wb") as f:
            f.write(file_bytes)

        return {
            "status" : "ok",
            "time" : (time.time() - start) * 1000,
            "size" : len(file_bytes)
        }

api.add_namespace(file_upload_controller)

if __name__ == "__main__":
    app.run(debug=True)
