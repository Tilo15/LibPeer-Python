from LibPeer.Formats.BinaryAddress import BinaryAddress

import queue
import struct
import uuid
import msgpack

class Reply:
    def __init__(self, peer: BinaryAddress, data: bytes):
        self.peer = peer
        self.token = None

        self._has_object = False
        self._is_complete = False

        self._object_data = b""
        self._object_data_size = 0
        self._binary_data = queue.Queue()
        self._binary_data_size = 0
        self._binary_data_received = 0
        self._binary_data_read = 0
        self._received_binary_size = False


        # Read header information
        self._object_data_size = struct.unpack("!I", data[:4])[0]
        self.token = uuid.UUID(bytes=data[4:20])

        # Pass the rest into _receive
        self._receive(data[20:])


    def _receive(self, data: bytes):
        if(len(self._object_data) < self._object_data_size):
            # Figure how much more we need to read
            data_left = self._object_data_size - len(self._object_data)

            # Read up to that amount
            obj_data = data[:data_left]

            # Catch any leftovers
            leftovers = data[data_left:]

            # Add new data to buffer
            self._object_data += obj_data

            # Run any leftovers through this function
            if(len(leftovers) > 0):
                self._has_object = True
                return self._receive(leftovers)

        elif(not self._received_binary_size):
            # Get the binary size
            self._binary_data_size = struct.unpack("!Q", data[:8])[0]

            # Mark size as received
            self._received_binary_size = True

            # Get leftovers
            leftovers = data[8:]

            # Run any leftovers through this function
            if(len(leftovers) > 0):
                return self._receive(leftovers)
            
            elif(self._binary_data_size == 0):
                self._is_complete = True

        elif(self._binary_data_received < self._binary_data_size):
            # Figure how much more we need to read
            data_left = self._binary_data_size - self._binary_data_received

            # Read up to that amount
            bin_data = data[:data_left]

            # Catch any leftovers
            leftovers = data[data_left:]

            # Update received amount
            self._binary_data_received += len(bin_data)

            # Add to queue
            self._binary_data.put(bin_data)

            if(self._binary_data_size <= self._binary_data_received):
                self._is_complete = True

            # Return leftovers
            if(len(leftovers) > 0):
                return leftovers


    def get_object(self, encoding="utf-8"):
        """Returns the object sent in the reply"""
        return msgpack.unpackb(self._object_data, encoding=encoding)


    def read(self):
        """Reads all buffered data received so far"""
        # Hold data
        data = b""

        while self._binary_data.qsize() != 0:
            # Get data from fifo (exception if no data)
            hunk = self._binary_data.get_nowait()
            # Buffer data
            data += hunk

        self._binary_data_read += len(data)
        
        return data


    def read_all(self):
        """Reads all remaining data from the data part of the reply"""
        data = b""

        # Calculate the amount of data that has to be read before we are done reading
        expected_size = self._binary_data_size - self._binary_data_read

        while len(data) != expected_size:
            # Read more data
            data += self._binary_data.get()

        self._binary_data_read += len(data)
        return data


    @property
    def transfer_information(self):
        """Tuple containing information on the progress of the transfer of the binary data section of the reply.
        In order, it contains data size, data received, data read, fraction of data received, fraction of data read."""
        return (self._binary_data_size, self._binary_data_received, self._binary_data_read, self._binary_data_received / float(self._binary_data_size), self._binary_data_read / float(self._binary_data_size))