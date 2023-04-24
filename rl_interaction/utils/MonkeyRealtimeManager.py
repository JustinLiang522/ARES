import socket
import logging


class MonkeyRealtimeManager:
    PORT_NUMBER = 29132
    RECONNECT_AFTER_NULL_INPUT = 1
    HOST = "10.92.83.4"
    CMD_GET_METHOD_ENTRIES = "get_entries"
    CMD_CLEAR_ENTRIES = "clear_entries"
    CMD_DISCONNECT = "disconnect"

    INSTANCE = None

    def __init__(self, host='127.0.0.1'):
        self.mSocket = None
        self.mReconnectCountdown = MonkeyRealtimeManager.RECONNECT_AFTER_NULL_INPUT
        self.mEnabled = True
        self.host = host

    @staticmethod
    def getInstance(host='127.0.0.1'):
        if MonkeyRealtimeManager.INSTANCE is None:
            MonkeyRealtimeManager.INSTANCE = MonkeyRealtimeManager(host)
        return MonkeyRealtimeManager.INSTANCE

    def setEnabled(self, enabled):
        self.mEnabled = enabled
        if not self.mEnabled and self.isConnected():
            self.disconnect()

    def getMethodEntries(self):
        methodEntries = None
        if self.mEnabled:
            try:
                if not self.isConnected():
                    self.connect()
                self.send(MonkeyRealtimeManager.CMD_GET_METHOD_ENTRIES)
                methodEntries = self.readLine()
                logging.info("Method entries: " + methodEntries)
            except Exception as e:
                logging.error("Exception getting method entries: " + str(e))
                self.disconnect()
        return methodEntries

    def connect(self):
        if not self.isConnected():
            logging.info("Connecting to realtime socket")
            self.mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.mSocket.settimeout(10)
            self.mSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 128)
            self.mSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 307200)
            self.mSocket.connect((self.host, MonkeyRealtimeManager.PORT_NUMBER))
            self.send(self.CMD_CLEAR_ENTRIES)

    def disconnect(self):
        try:
            if self.isConnected():
                logging.info("Disconnecting socket")
                self.send(MonkeyRealtimeManager.CMD_DISCONNECT)
                self.mSocket.close()
        except Exception as e:
            logging.error("Exception disconnecting: " + str(e))
        finally:
            self.mSocket = None

    def send(self, message):
        if not self.isConnected():
            raise Exception("Trying to send while not connected")
        logging.info("Sending message: " + message)
        out = self.mSocket.makefile(mode="w")
        out.write(message + "\n")
        out.flush()

    def readLine(self):
        if not self.isConnected():
            raise Exception("Trying to read while not connected")
        logging.info("Reading line")
        return self.mSocket.makefile(mode="r").readline().strip()

    def checkReconnect(self, input):
        if input is not None:
            self.mReconnectCountdown = MonkeyRealtimeManager.RECONNECT_AFTER_NULL_INPUT
            logging.info("读取覆盖率成功")
            logging.info("input length: " + str(len(input.encode())))
        else:
            logging.info("读取覆盖率失败")
            logging.info("no input, reconnect in " + str(self.mReconnectCountdown))
            if self.mReconnectCountdown < 0:
                self.mReconnectCountdown = MonkeyRealtimeManager.RECONNECT_AFTER_NULL_INPUT
                self.disconnect()

    def isConnected(self):
        return self.mSocket is not None and self.mSocket.fileno() != -1
