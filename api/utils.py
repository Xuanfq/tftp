import json
import os


def is_path_sub(parentpath, subpath):
    # Standardize paths to eliminate redundancy . 和 ..
    parentpath = os.path.realpath(parentpath)
    subpath = os.path.realpath(subpath)
    if subpath.startswith(parentpath):
        return len(subpath) > len(parentpath)
    else:
        return False


def is_path_same(parentpath, subpath):
    # Standardize paths to eliminate redundancy . 和 ..
    parentpath = os.path.realpath(parentpath)
    subpath = os.path.realpath(subpath)
    return subpath.startswith(parentpath) and len(subpath) == len(parentpath)


def is_valid_filename(filename):
    # Prevent path injection
    return filename.find("./") >= 0


def is_valid_filepath(filepath):
    # Prevent path injection
    return filepath.find("./") >= 0


if __name__ == "__main__":
    pass
