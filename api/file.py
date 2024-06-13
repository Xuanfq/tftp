import os
import shutil


class FileInterface:
    @staticmethod
    def delete_file(file_path):
        """
        Delete the file at the specified path.

        :param file_path: The complete path of the file
        :return: If the file exists and is successfully deleted, return True; Otherwise, return False
        """
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return True
            else:
                print(f"File [{file_path}] is not exist.")
                return False
        except Exception as e:
            print(f"An error occurred while deleting the file: {e}")
            return False

    @staticmethod
    def delete_folder(folder_path, recursive=True):
        """
        Delete the folder with the specified path, and optionally recursively delete sub folders and their contents.

        :param folder_path: The complete path of the folder
        :param recursive: Whether to recursively delete, default to True
        :return: If the folder exists and is successfully deleted, return True; Otherwise, return False
        """
        try:
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path) if recursive else os.rmdir(folder_path)
                return True
            else:
                print(f"Folder [{folder_path}] is not exist.")
                return False
        except Exception as e:
            print(f"An error occurred while deleting the folder: {e}")
            return False

    @staticmethod
    def create_folder(folder_path):
        """
        Create a new folder at the specified path.

        :param folder_path: The full path of the new folder
        :return: If the folder is successfully created, return True; Otherwise, return False
        """
        try:
            os.makedirs(folder_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"An error occurred while creating the folder: {e}")
            return False


# Usage examples
if __name__ == "__main__":
    # Example of deleting files
    file_to_delete = "example.txt"
    FileInterface.delete_file(file_to_delete)

    # Example of deleting folders, including recursive deletion of sub folders
    folder_to_delete = "test_folder"
    FileInterface.delete_folder(folder_to_delete)

    # Example of creating a folder
    new_folder = "new_folder"
    FileInterface.create_folder(new_folder)
