from LibPeer.Application.Preferences import TransportPreferences
from LibPeer.Application.ApplicationBase import ApplicationBase
from LibPeer.Application.Reception import Reception
from LibPeer.Formats.BinaryAddress import BinaryAddress

class Interface:
    def __init__(self, app: ApplicationBase, channel: bytes, *transports):
        # Setup the channel for the interface to use
        self.channel = channel

        # Save transport preferences
        self.transport_prefs = TransportPreferences(*transports)

        # Select a transport protocol to use
        self.transport_prefs.select_transport(app)

        # Save the reference to the application
        self.application: ApplicationBase = app

        # Subscribe to incoming data
        self.application.incoming.subscribe(self.__receive)

    
    def __receive(self, reception: Reception):
        # Only forward onto the implementation if the message is of correct channel and transport
        if(reception.channel == self.channel and reception.transport == self.transport_prefs._tid):
            self._receive(reception.data, reception.peer)


    def _receive(self, data: bytes, peer: BinaryAddress):
        raise NotImplementedError


    def _send(self, data: bytes, peer: BinaryAddress):
        # Send data down the system
        self.application.send(data, self.transport_prefs, peer, self.channel)