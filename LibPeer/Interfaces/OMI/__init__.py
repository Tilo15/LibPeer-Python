from LibPeer.Interfaces import Interface
from LibPeer.Application import ApplicationBase
from LibPeer.Interfaces.OMI.ObjectMessage import ObjectMessage
from LibPeer.Formats.BinaryAddress import BinaryAddress

import rx

class OMI(Interface):
    def __init__(self, application: ApplicationBase, channel: bytes = b"\x00"*16, transport: str = "DSTP"):
        # Initialise the interface
        super().__init__(application, channel, transport)

        # Set up subject for new Object Messages
        self.new_message = rx.subjects.Subject()

        # Setup dict for incoming messages
        self._incoming = {}


    def _receive(self, data: bytes, peer: BinaryAddress):
        # Do we have an incoming message from this peer?
        if(peer in self._incoming):
            # Get the existing message
            message: ObjectMessage = self._incoming[peer]

            # Feed the message more data
            leftovers = message._receive(data)

            # If there are leftovers, the message has been fully received
            if(message._ready):
                # Remove the message from the dict
                del self._incoming[peer]

                # Pass the message along to subscribers
                self.new_message.on_next((message, peer))

                if(len(leftovers) != 0):
                    # Process additional data
                    self._receive(leftovers, peer)

        # No existing message exists
        else:
            # Create new message using data as headers
            message = ObjectMessage.from_header(data[:21])

            # Save the message against the peer
            self._incoming[peer] = message

            # Handle rest of message normally
            self._receive(data[21:], peer)


    def send(self, obj, peer: BinaryAddress):
        # Is it a message object already?
        if(type(obj) == ObjectMessage):
            # Check it's ttl
            if(obj.ttl <= 0):
                raise IOError("Cannot send message with TTL <= 0")

            # Send the message
            self._send(obj.serialise(), peer)

        else:
            # Create the object message with a default TTL of 8
            message = ObjectMessage(obj, 8)

            # Send the message
            self._send(message.serialise(), peer)
