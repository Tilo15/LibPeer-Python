from LibPeer.Muxer import Muxer
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Formats.Chunk import Chunk
from LibPeer.Logging import log
from LibPeer.Transports.DSTP.ChunkTracker import ChunkTracker

import time
import struct
import rx
import threading
import uuid
import queue

CHUNK_SIZE = 4096

class Connection:
    def __init__(self, muxer: Muxer, channel: bytes, address: BinaryAddress):
        self.muxer = muxer
        self.channel = channel
        self.address = address

        # Metrics
        self.in_flight = 0
        self.window_size = 16
        self.last_packet_delay = 0
        self.last_packet_sent = 0

        # States
        self.connected = False
        self.last_pong = 0
        self.ping_retries = 0

        # Message type map
        self.message_map = {
            b"\x05": self.recv_connect_request,
            b"\x0D": self.recv_connect_accept,
            b"\x18": self.recv_disconnect,
            b"\x10": self.recv_connect_reset,
            b"\x50": self.recv_ping,
            b"\x70": self.recv_pong,
            b"\x02": self.recv_chunk,
            b"\x06": self.recv_chunk_ack,
            b"\x15": self.recv_chunk_nak
        }

        self.in_flight_chunks = {}
        self.last_queued_chunk = b"\x00"*16
        self.tx_lock = threading.Lock()
        self.chunk_trackers = set()
        self.chunk_queue = queue.Queue()

        self.received_chunk_ids = set()
        self.received_chunks = {}
        self.current_chunk = b"\x00"*16

        self.data_ready = rx.subjects.Subject()


    def calculate_window_size(self):
        delay_factor = 1 - self.last_packet_delay * 10
        window_factor = self.in_flight / self.window_size
        gain = delay_factor * window_factor

        self.window_size += gain

        if(self.window_size < 5):
            self.window_size = 5


    def kill(self, reason: str):
        # Stop the connection
        self.connected = False
        
        # Log out the reason
        log.debug("Connection killed: %s" % reason)

        # Notify trackers
        for tracker in self.chunk_trackers:
            tracker.canceled(reason)

        # Clean up
        self.in_flight = 0
        self.window_size = 16
        self.last_packet_delay = 0
        self.last_packet_sent = 0
        self.last_pong = 0
        self.in_flight_chunks = {}
        self.last_queued_chunk = b"\x00"*16
        self.tx_lock = threading.Lock()
        self.chunk_trackers = set()
        self.chunk_queue = queue.Queue()
        self.received_chunk_ids = set()
        self.received_chunks = {}
        self.current_chunk = b"\x00"*16


    def connect(self):
        # Only connect if not already connected
        if(not self.connected):
            # Send connection request
            self._send(b"\x05")

        # If not connected in 10 seconds, kill
        self.timeout(10, lambda: not self.connected, lambda: self.kill("Connection request timed out"))


    def send(self, data: bytes):
        # Don't allow threads to break the sequence!
        with self.tx_lock:
            # Break the data up into chunks
            chunks = []

            while len(data) != 0:
                # Generate an ID
                chunk_id = uuid.uuid4().bytes

                # Create and add the chunk
                chunks.append(Chunk(chunk_id, self.last_queued_chunk, data[:CHUNK_SIZE]))

                # Update last queued
                self.last_queued_chunk = chunk_id

                # Update the data left
                data = data[CHUNK_SIZE:]

            # Create a chunk tracker for this transaction
            tracker = ChunkTracker([c.id for c in chunks])

            # Add the chunk tracker to the list
            self.chunk_trackers.add(tracker)

            # Add the chunks to the queue to be sent
            for chunk in chunks:
                self.chunk_queue.put(chunk)

            if(self.connected):
                # Start sending chunks
                self.send_chunks()

            else:
                # Not connected, connect first
                self.connect()

            # Return the subject
            return tracker.sent


    def timeout(self, duration: int, condition, action, else_action = None):
        # Do something after a timeout if a condition is met
        def timer():
            time.sleep(duration)
            if(condition()):
                action()
            elif(else_action):
                else_action()

        threading.Thread(target=timer).start()


    def _send(self, data: bytes):
        # Send data to the muxer (0x06 is the byte for DSTP)
        self.muxer.send(data, self.channel, b"\x06", self.address).subscribe(lambda x: x)


    def send_chunk(self, chunk: Chunk):
        # Send the chunk
        self._send(b"\x02%s" % chunk.serialise())


    def send_chunks(self):
        # Calculate a new window size
        self.calculate_window_size()

        # Figure out how many packets we can send to fill the window
        available = round(self.window_size - self.in_flight)

        # Store how many chunks we resent
        resent_chunks = 0

        # Loop over sent but not acknowledged chunks
        for chunk in self.in_flight_chunks.values():
            # If the cunk was sent over (5 seconds + last packet delay) ago, resend it
            if(chunk.time_sent < time.time() - (self.last_packet_delay + 5)):
                # Resend
                self.send_chunk(chunk)

                # Increment resent chunks
                resent_chunks += 1

            if(resent_chunks > available):
                # Stop sending chunks
                break

        # Recalculate the window space we have left
        available -= resent_chunks

        # Send the next chunks
        try:
            for i in range(available):
                # Get next chunk from queue
                chunk = self.chunk_queue.get_nowait()

                # Add to in flight chunks list
                self.in_flight_chunks[chunk.id] = chunk

                # Increment in flight chunks counter
                self.in_flight += 1

                # Send the chunk
                self.send_chunk(chunk)

        except queue.Empty:
            log.debug("Connection window underrun")    


    def send_ping(self):
        # Only ping if the connection is active
        if(self.connected):
            # Send the ping request
            self._send(b"\x50")

            # Mark this point in time
            time_sent = time.time()

            # Set a timeout
            self.timeout(5, lambda t=time_sent: self.last_pong < t, self.ping_failure, self.send_ping)


    def ping_failure(self):
        # Tried more than 10 times?
        if(self.ping_retries > 10):
            # The connection is dead
            self.kill("Remote peer stopped responding")
            return

        # Increment ping retries
        self.ping_retries += 1

        # Try again
        self.send_ping()


    def receive(self, data: bytes):
        # Slice off the message type
        message_type = data[:1]

        # Do we have a handler?
        if(message_type in self.message_map):
            # Call the handler
            self.message_map[message_type](data[1:])

        else:
            log.warn("Could not handle packet with message type of %i" % data[0])


    def notify_trackers(self, chunk_id: bytes):
        # Save list of complete trackers
        complete = set()

        # Loop over ever chunk tracker
        for tracker in self.chunk_trackers:
            # Notify the tracker with the id
            tracker.chunk_acked(chunk_id)

            # If the tracker is complete, mark for deletion
            if(tracker.complete):
                complete.add(tracker)

        # Remove all complete trackers
        for tracker in complete:
            self.chunk_trackers.remove(tracker)


    def recv_connect_request(self, data: bytes):
        # If not already connected
        if(not self.connected):
            # Mark as connected
            self.connected = True

            # Acknowledge
            self._send(b"\x0D")

            # Start pinging
            self.send_ping()

        else:
            # Sent in error
            self.kill("Connection reset by local peer")

            # Send connection reset
            self._send(b"\x10")


    def recv_connect_accept(self, data: bytes):
        # Mark as connected
        self.connected = True

        # Start pinging
        self.send_ping()
        
        # Start sending chunks
        self.send_chunks()


    def recv_disconnect(self, data: bytes):
        # Stop the connection
        self.kill("The remote peer closed the connection")


    def recv_connect_reset(self, data: bytes):
        # Kill the connection
        self.kill("Connection reset by remote peer")

        # Attempt again to connect
        self.connect()


    def recv_ping(self, data: bytes):
        # If the connection is alive
        if(self.connected):
            # Repy with pong
            self._send(b"\x70")

        else:
            # Send a disconnect, someone is obviously confused
            self._send(b"\x18")


    def recv_pong(self, data: bytes):
        # Only care if its active
        if(self.connected):
            # Record the time it was received
            self.last_pong = time.time()

            # Clear retries
            self.ping_retries = 0

            # Transmit any chunks waiting
            self.send_chunks()


    def recv_chunk(self, data: bytes):
        # If not connected send disconnect
        if(not self.connected):
            self._send(b"\x18")
            return

        # Deserialise the chunk
        chunk, valid, timestamp = Chunk.deserialise(data)

        # If the chunk is valid
        if(valid):
            # Send a chunk acknowledgement
            self._send(b"\x06%s%s" % (chunk.id, struct.pack("!d", timestamp)))

            # Handle the chunk
            self.handle_chunk(chunk)

        # Chunk got broken on the way
        else:
            # Send nack
            self._send(b"\x15%s" % chunk.id)


    def recv_chunk_ack(self, data: bytes):
        # Get information
        chunk_id = data[:16]
        time_sent = struct.unpack("!d", data[16:])[0]

        # Is this chunk still in flight?
        if(chunk_id in self.in_flight_chunks):
            # Notify trackers
            self.notify_trackers(chunk_id)

            # Remove from flight list
            del self.in_flight_chunks[chunk_id]

            # Decrement in flight count
            self.in_flight -= 1

            # Set last packet delay
            self.last_packet_delay = time.time() - time_sent

        # Continue to send chunks
        self.send_chunks()


    def recv_chunk_nak(self, data: bytes):
        # Is this chunk still in flight?
        if(data in self.in_flight_chunks):
            # Resend the chunk immediately
            self.send_chunk(self.in_flight_chunks[data])


    def handle_chunk(self, chunk: Chunk):
        # Have we received this chunk before?
        if(chunk.id in self.received_chunk_ids):
            return

        # Add the chunk id to a list of received ids
        self.received_chunk_ids.add(chunk.id)

        # Add the chunk to the received dict using the prev id
        self.received_chunks[chunk.prev_id] = chunk

        # Collect the largest possible amount of data from the received chunks
        # while still preserving order
        data = b""

        # See if any complete message can be passed to the application yet
        while(self.current_chunk in self.received_chunks):
            # Get the next chunk in the cronological sequence
            next_chunk: Chunk = self.received_chunks[self.current_chunk]

            # Store the data from the chunk
            data += next_chunk.payload

            # Update the current chunk
            self.current_chunk = next_chunk.id

            # Remove the chunk from memory
            del self.received_chunks[next_chunk.prev_id]
            del next_chunk

        # We we managed to collect some data, notify the application
        if(len(data) > 0):
            self.data_ready.on_next((data, self.channel, self.address))


            
