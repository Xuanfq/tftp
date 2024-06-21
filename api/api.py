from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
import shutil
import os
from .fs import FileManagementSystem


class FileSystemAPID:
    def __init__(
        self,
        name,
        root_path,
        api_name: str = None,
        api_support_delete_file: bool = True,
        api_support_delete_folder: bool = False,
        api_support_create_folder: bool = True,
        api_support_list_path: bool = True,
        api_support_search_file: bool = True,
        api_support_upload_file: bool = True,
        api_support_download_file: bool = True,
        api_file_upload_max_size: int = 1024000,  # byte
        api_host: str = "localhost",
        api_port: int = 5000,
        app: Flask = None,
        fs: FileManagementSystem = None,
        debug: bool = False,
    ) -> None:
        self.name = name
        self.root_path = os.path.abspath(root_path)
        self.api_name = name if api_name is None else api_name
        self.app = app
        self.fs = fs
        self.api_support_delete_file = api_support_delete_file
        self.api_support_delete_folder = api_support_delete_folder
        self.api_support_create_folder = api_support_create_folder
        self.api_support_list_path = api_support_list_path
        self.api_support_search_file = api_support_search_file
        self.api_support_upload_file = api_support_upload_file
        self.api_support_download_file = api_support_download_file
        self.api_file_upload_max_size = api_file_upload_max_size
        self.api_host = api_host
        self.api_port = api_port
        self.debug = debug
        if app is None:
            self.app = Flask(self.name)
        if fs is None:
            self.fs = FileManagementSystem(root_path, debug=self.debug)
        self._init_app()

    def _uni_response(
        self, flag: bool, message: str = "", data: any = None, status_code: int = None
    ):
        if status_code is None:
            return jsonify(
                {
                    "flag": flag,
                    "message": message,
                    "data": data,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "flag": flag,
                        "message": message,
                        "data": data,
                    }
                ),
                status_code,
            )

    def _init_app(self):
        app = self.app
        app.config["FS_ROOT_PATH"] = self.root_path
        app.config["MAX_CONTENT_PATH"] = self.api_file_upload_max_size

        @app.errorhandler(Exception)
        def handle_exception(e):
            """Global exception handler."""
            if isinstance(e, FileNotFoundError):
                return self._uni_response(
                    False,
                    str(e)
                    .replace(f"{self.root_path}/", "")
                    .replace(f"{self.root_path}", ""),
                    None,
                    404,
                )
            elif isinstance(e, PermissionError):
                return self._uni_response(
                    False,
                    str(e)
                    .replace(f"{self.root_path}/", "")
                    .replace(f"{self.root_path}", ""),
                    None,
                    403,
                )
            else:
                return self._uni_response(
                    False,
                    str(e)
                    .replace(f"{self.root_path}/", "")
                    .replace(f"{self.root_path}", ""),
                    None,
                    500,
                )

        if self.api_support_delete_file:

            @app.route(f"/{self.api_name}/delete/file", methods=["POST"])
            def delete_file_api():
                path = request.form.get("path", None)
                if path is None:
                    raise Exception("Request parameter missing")
                success, msg = self.fs.delete_file(path)
                if success:
                    return self._uni_response(True, "Success")
                else:
                    raise Exception(msg)

        if self.api_support_delete_folder:

            @app.route(f"/{self.api_name}/delete/folder", methods=["POST"])
            def delete_folder_api():
                path = request.form.get("path", "")
                success, msg = self.fs.delete_folder(path)
                if success:
                    return self._uni_response(True, "Success")
                else:
                    raise Exception(msg)

        if self.api_support_create_folder:

            @app.route(f"/{self.api_name}/add/folder", methods=["POST"])
            def create_folder_api():
                path = request.form.get("path", "")
                success, msg = self.fs.create_folder(path)
                if success:
                    return self._uni_response(True, "Success")
                else:
                    raise Exception(msg)

        if self.api_support_list_path:

            @app.route(f"/{self.api_name}/get/list", methods=["GET"])
            def list_path_api():
                path = request.args.get("path", default="")
                success, data_or_error = self.fs.list_path_contents(path)
                if success:
                    return self._uni_response(True, "Success", data_or_error)
                else:
                    raise Exception(data_or_error)

        if self.api_support_search_file:

            @app.route(f"/{self.api_name}/search/file", methods=["GET"])
            def search_api():
                key = request.args.get("key")
                path = request.args.get("path", default="")
                success, results_or_error = self.fs.search(key, path)
                if success:
                    return self._uni_response(True, "Success", results_or_error)
                else:
                    raise Exception(results_or_error)

        if self.api_support_upload_file:

            @app.route(f"/{self.api_name}/upload/file", methods=["POST"])
            def upload_file_api():
                path = request.form.get("path", "")
                if "file" not in request.files:
                    raise Exception("Request parameter missing")
                file = request.files["file"]
                if file.filename == "":
                    raise Exception("No selected file")

                filename = file.filename
                filepath = Path(self.fs.root_path) / path / secure_filename(filename)

                # Generate a unique filename to avoid conflicts
                temp_filename = f"{filename}-{uuid.uuid4()}.filepart"
                temp_filepath = Path(self.fs.root_path) / path / temp_filename

                # Ensure the directory exists
                temp_filepath.parent.mkdir(parents=True, exist_ok=True)
                success, msg = self.fs.create_folder(temp_filepath.parent)

                file.save(str(temp_filepath))

                # cover the file named filename
                shutil.copy(temp_filepath, filepath)
                success, msg = self.fs.delete_file(temp_filepath)

                return self._uni_response(True, "Success")

        if self.api_support_download_file:

            @app.route(f"/{self.api_name}/download/file", methods=["GET"])
            def download_file_api():
                path = request.args.get("path", default=None)
                if path is None:
                    raise Exception("Request parameter missing")
                # Assuming 'uploads' is a subfolder where files are stored, adjust as needed.
                file_path = Path(self.fs.root_path) / path
                if not file_path.exists():
                    raise Exception("File is not exist")

                return send_from_directory(
                    str(self.fs.root_path), path, as_attachment=True
                )

    def run(self):
        self.app.run(host=self.api_host, port=self.api_port, debug=self.debug)


if __name__ == "__main__":
    fsapid = FileSystemAPID("TestFSAPI", "files", "api", debug=True)
    fsapid.run()
