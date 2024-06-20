import os
import shutil
import logging
from pathlib import Path


class FileManagementSystem:
    def __init__(
        self, root_path, retry_count=1, read_max_bytes=1024 * 1024, debug=False
    ):
        self.root_path = os.path.abspath(root_path)
        self.retry_count = retry_count
        self.read_max_bytes = read_max_bytes
        if not os.path.isdir(self.root_path):
            raise FileNotFoundError("Specified root path does not exist.")
        logging.basicConfig(
            level=logging.INFO if not debug else logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def _validate_and_get_abs_path(self, path):
        abs_path = Path(self.root_path) / path
        if not abs_path.is_relative_to(self.root_path):
            return False, "Invalid path"
        return True, abs_path

    def _safe_operation(self, func, *args, **kwargs):
        """Operation with retry mechanism."""
        try_count = self.retry_count
        while try_count > 0:
            try_count -= 1
            try:
                func(*args, **kwargs)
                return True, None
            except Exception as e:
                if try_count > 0:
                    continue
                return False, str(e)

    def delete_file(self, file_path):
        valid, abs_path = self._validate_and_get_abs_path(file_path)
        if not valid:
            return valid, abs_path
        op_valid, op_msg = self._safe_operation(abs_path.unlink)
        if not op_valid:
            return op_valid, op_msg
        self.logger.info("File {} has been deleted.".format(abs_path))
        return True, None

    def delete_folder(self, folder_path, recursive=True):
        valid, abs_path = self._validate_and_get_abs_path(folder_path)
        if not valid:
            return valid, abs_path
        op_valid, op_msg = self._safe_operation(
            shutil.rmtree, str(abs_path), ignore_errors=True
        )
        if not op_valid:
            return op_valid, op_msg
        self.logger.info("Folder deleted: {}".format(abs_path))
        return True, None

    def create_folder(self, folder_path):
        valid, abs_path = self._validate_and_get_abs_path(folder_path)
        if not valid:
            return valid, abs_path
        op_valid, op_msg = self._safe_operation(
            abs_path.mkdir, parents=True, exist_ok=True
        )
        if not op_valid:
            return op_valid, op_msg
        self.logger.info("Folder created: {}".format(abs_path))
        return True, None

    def search(self, pattern, path=None):
        """Search for files or folders by name pattern."""
        search_dir = (
            Path(self.root_path)
            if path is None
            else self._validate_and_get_abs_path(path)[1]
        )
        if not search_dir:
            return False, "Invalid path"
        results = [
            {
                "name": p.name,
                "is_dir": p.is_dir(),
                "path": str(p.relative_to(self.root_path)),
                "size": p.stat().st_size if not p.is_dir() else None,
            }
            for p in search_dir.glob(pattern)
        ]
        return True, results

    def read_file_content(self, file_path):
        """Read file content safely, limiting size to prevent memory overflow."""
        valid, abs_path = self._validate_and_get_abs_path(file_path)
        if not valid:
            return valid, abs_path
        try:
            with abs_path.open("r", encoding="utf-8") as f:
                content = f.read(self.read_max_bytes)
            return True, content
        except Exception as e:
            return False, str(e)

    def list_path_contents(self, path=None):
        """List directory contents."""
        target_dir = (
            Path(self.root_path)
            if path is None
            else self._validate_and_get_abs_path(path)[1]
        )
        if not target_dir:
            return False, "Invalid path"
        return True, [
            {
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "path": str(entry.relative_to(self.root_path)),
                "size": entry.stat().st_size if not entry.is_dir() else None,
            }
            for entry in target_dir.iterdir()
        ]


# Usage example
if __name__ == "__main__":
    fs = FileManagementSystem("xxx")
    # Example operations...
