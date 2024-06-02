#!/bin/python3
import os
import sys
import argparse
try:
    from . import tftp
except:
    from tftp import tftp

SETTINGS = {
    "TFTP_SERVER_IP": "0.0.0.0",
    "TFTP_SERVER_PORT": 69,
    "TFTP_FILE_DIR": ".",
    "TFTP_WRQ_ENABLE": False,
    "TFTP_RETRIES": 3,
    "TFTP_TIMEOUT": 5,
    "MODE_DEBUG": False,
    "MODE_VERBOSE": True,
}


def parse_cli_arguments():
    # main service arguments
    parser = argparse.ArgumentParser(
        description="TFTP Server",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--tftp-server-ip",
        action="store",
        dest="TFTP_SERVER_IP",
        help="TFTP Server IP",
        default=SETTINGS["TFTP_SERVER_IP"],
    )
    parser.add_argument(
        "--tftp-port",
        action="store",
        dest="TFTP_SERVER_PORT",
        help="TFTP Server Port",
        default=SETTINGS["TFTP_SERVER_PORT"],
    )
    parser.add_argument(
        "--tftp-file-dir",
        action="store",
        dest="TFTP_FILE_DIR",
        help="TFTP File Directory",
        default=SETTINGS["TFTP_FILE_DIR"],
    )
    parser.add_argument(
        "--tftp-wrq",
        action="store_true",
        dest="TFTP_WRQ_ENABLE",
        help="TFTP WRQ Enable",
        default=SETTINGS["TFTP_WRQ_ENABLE"],
    )
    parser.add_argument(
        "--tftp-retries",
        action="store",
        dest="TFTP_RETRIES",
        help="TFTP Retry Number",
        default=SETTINGS["TFTP_RETRIES"],
    )
    parser.add_argument(
        "--tftp-timeout",
        action="store",
        dest="TFTP_TIMEOUT",
        help="TFTP Timeout",
        default=SETTINGS["TFTP_TIMEOUT"],
    )

    # TFTP server arguments
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="MODE_DEBUG",
        help="debug mode enable",
        default=SETTINGS["MODE_DEBUG"],
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        dest="MODE_VERBOSE",
        help="verbose mode enable",
        default=SETTINGS["MODE_VERBOSE"],
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
    tftpd = tftp.TFTPD(
        ip=args.TFTP_SERVER_IP,
        port=args.TFTP_SERVER_PORT,
        file_dir=args.TFTP_FILE_DIR,
        wrq_enable=args.TFTP_WRQ_ENABLE,
        retries=args.TFTP_RETRIES,
        timeout=args.TFTP_TIMEOUT,
        mode_debug=args.MODE_DEBUG,
        mode_verbose=args.MODE_VERBOSE,
        logger=None,
    )
    tftpd.start()


if __name__ == '__main__':
    main()
