import socket
import os
import struct
import logging
import select
import threading
import utils

# TFTP mode
MODE_OCTET = "octet"
MODE_NETASCII = "netascii"

# TFTP opcodes
OP_CODE_RRQ = 1
OP_CODE_WRQ = 2
OP_CODE_DATA = 3
OP_CODE_ACK = 4
OP_CODE_ERROR = 5
OP_CODE_OACK = 6

# TFTP error code
ERROR_CODE_UNDEF = 0  # Not defined, see error message (if any).
ERROR_CODE_NOTFOUND = 1  # File not found.
ERROR_CODE_ACCESS = 2  # Access violation.
ERROR_CODE_DISKFULL = 3  # Disk full or allocation exceeded.
ERROR_CODE_ILLEGAL = 4  # Illegal TFTP operation.
ERROR_CODE_BADOPID = 5  # Unknown transfer ID.
ERROR_CODE_EXISTS = 7  # File already exists.
ERROR_CODE_NOUSER = 8  # No such user.


class TFTPDClientHandler(threading.Thread):
    """
    This class implements a Client Handler to handle TFTP client requests.
    """

    def __init__(
        self,
        sock: socket,
        bind_ip,
        file_dir,
        wrq_enable=False,
        default_retries=3,
        timeout=5,
        logger=None,
        root_logger=None,
        mode_verbose=True,
        mode_debug=False,
    ) -> None:
        threading.Thread.__init__(self)

        data, address = sock.recvfrom(1024)

        self.data = data
        self.address = address
        self.default_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dl_sock = None
        self.ul_sock = None
        self.ip = bind_ip
        self.file_dir = file_dir
        self.wrq_enable = wrq_enable
        self.default_retries = default_retries
        self.timeout = timeout
        self.retries = self.default_retries
        self.blksize = 512
        self.dl_file = None
        self.dl_filename = ""
        self.ul_file = None
        self.ul_filename = ""

        self.mode_verbose = mode_verbose  # verbose mode
        self.mode_debug = mode_debug  # debug mode
        self.logger = logger if logger is not None else None

        if root_logger is not None:
            self.logger = utils.get_child_logger(
                root_logger, "Client-{}".format(address)
            )

        # setup logger
        if self.logger == None:
            self.logger = logging.getLogger("TFTP.Client.")
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

            if self.mode_debug:
                self.logger.setLevel(logging.DEBUG)
            elif self.mode_verbose:
                self.logger.setLevel(logging.INFO)
            else:
                self.logger.setLevel(logging.WARN)

        pass

    def send_error(self, sock, error_code, error_message="", filename=""):
        """send error"""
        msg = struct.pack("!H", OP_CODE_ERROR)  # error opcode
        msg += struct.pack("!H", error_code)  # error code
        msg += error_message.encode("ascii")
        msg += b"\x00"
        sock.sendto(msg, self.address)
        self.logger.info(
            "Sending Error {0}: {1} {2}".format(error_code, error_message, filename)
        )

    def send_data(self, sock, block_number, data):
        """send data"""
        msg = struct.pack("!HH%ds" % len(data), OP_CODE_DATA, block_number, data)
        sock.sendto(msg, self.address)
        self.logger.debug("Sending Data {0}: {1}".format(block_number, data))

    def send_ack(self, sock, block_number):
        """send ack"""
        msg = struct.pack("!HH", OP_CODE_ACK, block_number)
        sock.sendto(msg, self.address)
        self.logger.debug("Sending ACK: {0}".format(block_number))

    def handle_rrq(self, filename, mode):
        """handle read request"""
        self.dl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.dl_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.dl_sock.bind((self.ip, 0))
        # Check if the file read mode octet; if not, send an error.
        if mode != MODE_OCTET:
            self.send_error(
                self.dl_sock,
                ERROR_CODE_BADOPID,
                "Mode {0} not supported".format(mode),
                filename,
            )
            return
        # Check if the file exists under the file_dir, and if it is a file; if not, send an error.
        try:
            filename = utils.path_normalize(self.file_dir, filename)
        except Exception:
            self.send_error(
                self.dl_sock, ERROR_CODE_NOTFOUND, "Path traversal error", filename
            )
            return
        if not os.path.lexists(filename) or not os.path.isfile(filename):
            self.send_error(
                self.dl_sock, ERROR_CODE_NOTFOUND, "File Not Found", filename
            )
            return
        self.dl_filename = filename
        try:
            self.dl_file = open(filename, "rb")
            wrap = 0
            arm_wrap = False
            block_number = 1
            while True:
                self.dl_file.seek(self.blksize * (block_number - 1))
                data = self.dl_file.read(self.blksize)
                if not data:
                    # EOF, send last zero-length block
                    break
                self.send_data(self.dl_sock, block_number, data)
                if len(data) < self.blksize:
                    # rrq finished
                    self.logger.debug("Download {} finish".format(filename))
                    return
                try:
                    self.dl_sock.settimeout(self.timeout)
                    ack_data, addr = self.dl_sock.recvfrom(1024)
                except Exception as e:
                    self.logger.info("Download {} error: {}".format(filename, e))
                    # timeout and retry
                    if self.retries > 0:
                        self.retries -= 1
                        continue
                    break
                opcode, ack_block_number = struct.unpack("!HH", ack_data)
                if ack_block_number != ack_block_number:
                    # raise Exception("Incorrect block number in ACK")
                    # data loss and resend
                    self.logger.info(
                        "Incorrect block number: ack_block_number/block_number = {}/{}".format(
                            ack_block_number, ack_block_number
                        )
                    )
                    pass
                if opcode == OP_CODE_ACK:
                    if ack_block_number == 0 and arm_wrap:
                        wrap += 1
                        arm_wrap = False
                    if ack_block_number == 32768:
                        arm_wrap = True
                    if ack_block_number < block_number % 65536:
                        self.logger.warning(
                            "Ignoring duplicated ACK received for block {0}".format(
                                block_number
                            )
                        )
                    elif ack_block_number > block_number % 65536:
                        self.logger.warning(
                            "Ignoring out of sequence ACK received for block {0}".format(
                                block_number
                            )
                        )
                    elif ack_block_number + self.wrap * 65536 == self.lastblock:
                        if self.filesize % self.blksize == 0:
                            block_number = ack_block_number + 1
                            self.send_block()
                        self.logger.info("Completed sending {0}".format(self.filename))
                        self.complete()
                    else:
                        # data loss and resend
                        block_number = ack_block_number + 1
                        self.retries = self.default_retries
                        self.send_block()
            # Send last zero-length block to indicate EOF
            self.send_data(self.dl_sock, block_number, b"")
        except FileNotFoundError:
            self.send_error(
                self.dl_sock, ERROR_CODE_NOTFOUND, "File not found", filename
            )
        except Exception as e:
            self.send_error(self.dl_sock, ERROR_CODE_ILLEGAL, str(e), filename)

    def handle_wrq(self, filename, mode):
        """handle write request"""
        self.ul_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Check if the file read mode octet; if not, send an error.
        if mode != MODE_OCTET:
            print("Not OCTET", mode)
            self.send_error(
                self.ul_sock,
                ERROR_CODE_BADOPID,
                "Mode {0} not supported".format(mode),
                filename,
            )
            return
        # Check if the file exists under the file_dir, and if it is a file; if not, send an error.
        try:
            filename = utils.path_normalize(self.file_dir, filename)
        except Exception:
            self.send_error(
                self.ul_sock, ERROR_CODE_NOTFOUND, "Path traversal error", filename
            )
            return
        self.ul_filename = filename
        try:
            self.ul_file = open(filename, "wb")
            block_number = 0
            self.send_ack(self.ul_sock, block_number)
            block_number += 1
            while True:
                data, addr = self.ul_sock.recvfrom(1024)
                if len(data) < 4:
                    # Invalid packet or EOF
                    break
                (
                    opcode,
                    recv_block_number,
                ) = struct.unpack("!HH", data[:4])
                if opcode != OP_CODE_DATA or recv_block_number != block_number:
                    # raise Exception("Invalid DATA packet")
                    # data loss and resend
                    self.logger.info(
                        "Invalid DATA packet: recv_block_number/block_number = {}/{}".format(
                            recv_block_number, block_number
                        )
                    )
                    self.send_ack(self.ul_sock, block_number - 1)
                    continue
                self.ul_file.write(data[4:])
                self.ul_file.flush()
                self.send_ack(self.ul_sock, block_number)
                block_number += 1
        except Exception as e:
            self.send_error(self.ul_sock, ERROR_CODE_ILLEGAL, str(e), filename)

    def handle_request(self):
        """handle request from client"""
        (opcode,) = struct.unpack("!H", self.data[:2])
        if opcode == OP_CODE_RRQ:
            filename = self.data[2:].split(b"\x00")[0].decode("ascii").lstrip("/")
            mode = self.data[2:].split(b"\x00")[1].decode("ascii")
            self.logger.info(
                "handle request rrq: [{}][{}][{}]".format(self.address, filename, mode)
            )
            self.handle_rrq(filename, mode)
        elif opcode == OP_CODE_WRQ:
            filename = self.data[2:].split(b"\x00")[0].decode("ascii")
            mode = self.data[2:].split(b"\x00")[1].decode("ascii")
            if not self.wrq_enable:
                self.send_error(
                    self.default_socket,
                    ERROR_CODE_ILLEGAL,
                    "Write request is not enable",
                )
            else:
                self.logger.info(
                    "handle request wrq: [{}][{}][{}]".format(
                        self.address, filename, mode
                    )
                )
                self.handle_wrq(filename, mode)
        else:
            self.send_error(
                self.default_socket, ERROR_CODE_BADOPID, "Opcode not understood"
            )

    def run(self) -> None:
        # handel start
        self.logger.info("handle start: [{}]".format(self.address))
        self.handle_request()
        # handle end
        try:
            self.dl_file.close()
        except Exception:
            pass
        try:
            self.dl_sock.close()
        except Exception:
            pass
        try:
            self.ul_file.close()
        except Exception:
            pass
        try:
            self.ul_sock.close()
        except Exception:
            pass
        try:
            self.default_socket.close()
        except Exception:
            pass
        self.logger.info("handle   end: [{}]".format(self.address))


class TFTPD:
    """
    This class implements a TFTP server,
    implemented from RFC1350 and RFC2348(TBD)
    """

    def __init__(self, **server_settings):
        self.ip = server_settings.get("ip", "0.0.0.0")
        self.port = int(server_settings.get("port", 69))
        self.file_dir = server_settings.get("file_dir", "files")
        self.wrq_enable = server_settings.get("wrq_enable", False)
        self.mode_verbose = server_settings.get("mode_verbose", True)  # verbose mode
        self.mode_debug = server_settings.get("mode_debug", False)  # debug mode
        self.logger = server_settings.get("logger", None)
        self.default_retries = server_settings.get("default_retries", 3)
        self.timeout = server_settings.get("timeout", 5)

        # setup socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))

        # setup logger
        if self.logger == None:
            self.logger = logging.getLogger("TFTP")
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        if self.mode_debug:
            self.logger.setLevel(logging.DEBUG)
        elif self.mode_verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARN)

        self.logger.info(
            "NOTICE: TFTP server started in debug mode. TFTP server is using the following:"
        )
        self.logger.info("Server IP: {0}".format(self.ip))
        self.logger.info("Server Port: {0}".format(self.port))
        self.logger.info("TFTP File Root Directory: {0}".format(self.file_dir))

        self.ongoing = []

    def listen(self):
        """This method listens for incoming requests."""
        while True:
            rlist, _, _ = select.select([self.sock], [], [], 1)
            for sock in rlist:
                if sock == self.sock:
                    # Create a new thread to handle the client request
                    TFTPDClientHandler(
                        sock=self.sock,
                        bind_ip=self.ip,
                        file_dir=self.file_dir,
                        wrq_enable=self.wrq_enable,
                        default_retries=self.default_retries,
                        timeout=self.timeout,
                        logger=None,
                        root_logger=self.logger,
                        mode_verbose=self.mode_verbose,
                        mode_debug=self.mode_debug,
                    ).start()
                else:
                    # client socket, so tell the client object it's ready
                    sock.parent.ready()

    def start(self):
        self.listen()


if __name__ == "__main__":
    TFTPD().start()
