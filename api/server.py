#!/bin/python3
import os
import sys
import argparse
import uuid

try:
    from . import api
except:
    from api import api

SETTINGS = {
    "ROOT_PATH": "files",
    "API_NAME": "api",
    "API_HOST": "localhost",
    "API_PORT": 5000,
    "API_SUPPORT_DELETE_FILE": True,
    "API_SUPPORT_DELETE_FOLDER": False,
    "API_SUPPORT_CREATE_FOLDER": True,
    "API_SUPPORT_LIST_PATH": True,
    "API_SUPPORT_SEARCH_FILE": True,
    "API_SUPPORT_UPLOAD_FILE": True,
    "API_SUPPORT_DOWNLOAD_FILE": True,
    "API_FILE_UPLOAD_MAX_SIZE": 1024000,
    "API_AUTH": False,
    "API_AUTH_SECRET_KEY": "tftpapifdskfjdfjklsdjflkdsjfdkfjklsj",
    "API_AUTH_TOKEN_EXPIRES": 60 * 60 * 24,
    "API_AUTH_USERNAME": "admin",
    "API_AUTH_PASSWORD": "admin",
    "DEBUG": False,
}


def parse_cli_arguments():
    # main service arguments
    parser = argparse.ArgumentParser(
        description="TFTP API Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--root-path",
        action="store",
        dest="ROOT_PATH",
        help="file system root path",
        default=SETTINGS["ROOT_PATH"],
    )
    parser.add_argument(
        "--api-name",
        action="store",
        dest="API_NAME",
        help="api name for api path like /api_name/xxx/xxx",
        default=SETTINGS["API_NAME"],
    )
    parser.add_argument(
        "--api-host",
        action="store",
        dest="API_HOST",
        help="api host for binding",
        default=SETTINGS["API_HOST"],
    )
    parser.add_argument(
        "--api-port",
        action="store",
        dest="API_PORT",
        help="api port for binding",
        default=SETTINGS["API_PORT"],
    )
    parser.add_argument(
        "--disable-api-support-delete-file",
        action="store_false",
        dest="API_SUPPORT_DELETE_FILE",
        help="disable api supporting delete file",
        default=SETTINGS["API_SUPPORT_DELETE_FILE"],
    )
    parser.add_argument(
        "--enable-api-support-delete-folder",
        action="store_true",
        dest="API_SUPPORT_DELETE_FOLDER",
        help="enable api supporting delete folder",
        default=SETTINGS["API_SUPPORT_DELETE_FOLDER"],
    )
    parser.add_argument(
        "--disable-api-support-create-folder",
        action="store_false",
        dest="API_SUPPORT_CREATE_FOLDER",
        help="disable api supporting create folder",
        default=SETTINGS["API_SUPPORT_CREATE_FOLDER"],
    )
    parser.add_argument(
        "--disable-api-support-list-path",
        action="store_false",
        dest="API_SUPPORT_LIST_PATH",
        help="disable api supporting list path content",
        default=SETTINGS["API_SUPPORT_LIST_PATH"],
    )
    parser.add_argument(
        "--disable-api-support-search-file",
        action="store_false",
        dest="API_SUPPORT_SEARCH_FILE",
        help="disable api supporting search file",
        default=SETTINGS["API_SUPPORT_SEARCH_FILE"],
    )
    parser.add_argument(
        "--disable-api-support-upload-file",
        action="store_false",
        dest="API_SUPPORT_UPLOAD_FILE",
        help="disable api supporting upload file",
        default=SETTINGS["API_SUPPORT_UPLOAD_FILE"],
    )
    parser.add_argument(
        "--disable-api-support-download-file",
        action="store_false",
        dest="API_SUPPORT_DOWNLOAD_FILE",
        help="disable api supporting download file",
        default=SETTINGS["API_SUPPORT_DOWNLOAD_FILE"],
    )
    parser.add_argument(
        "--api-file-upload-max-size",
        action="store",
        dest="API_FILE_UPLOAD_MAX_SIZE",
        help="api file upload max size",
        default=SETTINGS["API_FILE_UPLOAD_MAX_SIZE"],
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="DEBUG",
        help="enable debug mode",
        default=SETTINGS["DEBUG"],
    )
    parser.add_argument(
        "--api-auth",
        action="store_true",
        dest="API_AUTH",
        help="enable api auth",
        default=SETTINGS["API_AUTH"],
    )
    parser.add_argument(
        "--api-auth-secret-key",
        action="store",
        dest="API_AUTH_SECRET_KEY",
        help="api auth secret key",
        default=SETTINGS["API_AUTH_SECRET_KEY"],
    )
    parser.add_argument(
        "--api-auth-token-expires",
        action="store",
        dest="API_AUTH_TOKEN_EXPIRES",
        help="api auth token expires (seconds)",
        default=SETTINGS["API_AUTH_TOKEN_EXPIRES"],
    )
    parser.add_argument(
        "--api-auth-username",
        action="store",
        dest="API_AUTH_USERNAME",
        help="api auth login username",
        default=SETTINGS["API_AUTH_USERNAME"],
    )
    parser.add_argument(
        "--api-auth-password",
        action="store",
        dest="API_AUTH_PASSWORD",
        help="api auth login password",
        default=SETTINGS["API_AUTH_PASSWORD"],
    )

    return parser.parse_args()


def main():
    global SETTINGS, args
    # configure
    args = parse_cli_arguments()

    # warn the user that they are starting PyPXE as non-root user
    if os.getuid() != 0:
        print(sys.stderr, "\nWARNING: Not root. Servers will probably fail to bind.\n")

    # setup TFTP
    fsapid = api.FileSystemAPID(
        name=f"{args.API_NAME}-{uuid.uuid4()}",
        root_path=args.ROOT_PATH,
        api_name=args.API_NAME,
        api_host=args.API_HOST,
        api_port=args.API_PORT,
        api_support_delete_file=args.API_SUPPORT_DELETE_FILE,
        api_support_delete_folder=args.API_SUPPORT_DELETE_FOLDER,
        api_support_create_folder=args.API_SUPPORT_CREATE_FOLDER,
        api_support_list_path=args.API_SUPPORT_LIST_PATH,
        api_support_search_file=args.API_SUPPORT_SEARCH_FILE,
        api_support_upload_file=args.API_SUPPORT_UPLOAD_FILE,
        api_support_download_file=args.API_SUPPORT_DOWNLOAD_FILE,
        api_file_upload_max_size=args.API_FILE_UPLOAD_MAX_SIZE,
        api_auth=args.API_AUTH,
        api_auth_secret_key=args.API_AUTH_SECRET_KEY,
        api_auth_token_expires=args.API_AUTH_TOKEN_EXPIRES,
        api_auth_username=args.API_AUTH_USERNAME,
        api_auth_password=args.API_AUTH_PASSWORD,
        debug=args.DEBUG,
    )
    fsapid.run()


if __name__ == "__main__":
    main()
