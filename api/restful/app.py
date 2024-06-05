from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import utils
import settings

API_DEBUG = settings.API_DEBUG
API_NAME = settings.API_NAME
API_UPLOAD_FOLDER = settings.API_UPLOAD_FOLDER
API_MAX_CONTENT_PATH = settings.API_MAX_CONTENT_PATH

app = Flask(API_NAME)

# Define the path for uploading folders
app.config["UPLOAD_FOLDER"] = API_UPLOAD_FOLDER
# Specify the maximum size of the file to be uploaded - in bytes
app.config["MAX_CONTENT_PATH"] = API_MAX_CONTENT_PATH


@app.route(f"/{API_NAME}/file/put", methods=["POST"])
def upload_file():
    f = request.files["file"]
    filename = os.path.join(API_UPLOAD_FOLDER, secure_filename(f.filename))
    f.save(filename)
    return utils.json_uni_return(flag=True, data=None, message="uploaded successfully")


@app.route(f"/{API_NAME}/file/get", methods=["GET"])
def download_file():
    filename = request.args.get("filename", None)
    if filename is None:
        return utils.json_uni_return(
            flag=False, data=None, message="missing parameters"
        )
    filename = os.path.join(API_UPLOAD_FOLDER, filename)
    if not os.path.exists(filename):
        return utils.json_uni_return(flag=False, data=None, message="file is not exist")
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=API_DEBUG)
