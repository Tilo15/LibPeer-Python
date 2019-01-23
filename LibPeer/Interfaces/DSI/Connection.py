from LibPeer.Formats.BinaryAddress import BinaryAddress
import struct
import queue
import time

class Connection:
    def __init__(self, dsi, peer: BinaryAddress):
        self._dsi = dsi

        self.connected = False
        self.peer = peer

        self._expected_ack = False
        self._expected_left = 0
        self._fifo = queue.Queue()
        self._current_hunk = b""


    def _connect(self):
            self._expected_ack = True
            self._send(b"C")


    def _send(self, data: bytes):
        self._dsi._send(b"DSI" + data, self.peer)


    def _receive(self, data: bytes):
        if(self._expected_left == 0 and data[:3] == b"DSI"):
            message_type = data[3:4]

            if(message_type == b"C" and not self.connected):
                # Connect
                self.connected = True
                self._send(b"A")

                # Inform application
                self._dsi.new_connection.on_next(self)

            elif(message_type == b"A" and self._expected_ack):
                # Connect ack
                self.connected = True
                self._expected_ack = False

            elif(message_type == b"D"):
                # Disconnect
                self.connected = False

            elif(message_type == b"S" and self.connected):
                # Stream data, get expected length
                self._expected_left = struct.unpack("!Q", data[4:12])[0]

                # Re-process the rest of the data
                self._receive(data[12:])

        elif(self._expected_left > 0):
            # Get up to the expected amount of data
            payload = data[:self._expected_left]

            # Preserve leftovers
            leftovers = data[self._expected_left:]

            # Add the payload to the queue
            self._fifo.put(payload)

            # Subtract what we got from what is expected
            self._expected_left -= len(payload)

            # If we have data left over, process that
            if(len(leftovers) != 0):
                self._receive(leftovers)


    def _wait_connected(self, timeout: int = 20):
        start = time.time()
        while(not self.connected):
            if(time.time() - start > timeout):
                raise TimeoutError("The peer did not respond")


    # App facing
    def read(self, count: int, timeout: int = 10) -> bytes:
        """Read from stream until count bytes have been received, and return them"""
        if(len(self._current_hunk) > 0):
            # Read up to the requested amount of data from the hunk
            data = self._current_hunk[:count]

            # Remove read data from hunk
            self._current_hunk = self._current_hunk[count:]

            # If there is more data to be read
            if(len(data) < count):
                # Get more data and append it to our current data
                return data + self.read(count - len(data), timeout)

            return data

        # Get the next hunk
        else:
            if(not self.connected and self._fifo.qsize() == 0):
                raise IOError("Cannot read from remote peer, connection closed")

            self._current_hunk = self._fifo.get(True, timeout)
            return self.read(count, timeout)


    def send(self, data: bytes):
        """Send specified data over stream"""
        if(not self.connected):
            raise IOError("Cannot send to remote peer, connection closed")

        self._send(b"S%b%b" % (struct.pack("!Q", len(data)), data))


    def close(self):
        """Close connection to the remote peer"""
        self._send(b"D")
        self.connected = False

