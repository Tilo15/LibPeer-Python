from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Formats.Parcel import Parcel
from LibPeer.Logging import log

import uuid
import rx

class Muxer:

    def __init__(self, networks: list):
        self.networks = {}
        self.incoming = rx.subjects.Subject()

        self.applications = set()

        for network in networks:
            # Add network to map
            self.networks[network.identifier] = network

            # Subscribe to incoming data
            network.incoming.subscribe(self._receive)


    def _receive(self, info):
        # Get the data
        data = info[0]
        address: BinaryAddress = info[1]

        try:
            # Deserialise and pass along to subscribers
            parcel = Parcel.deserialise(data)

            # Update the address to include more information
            address.application = parcel.application_protocol

            try:
                # Pass along the parcel and address
                self.incoming.on_next((parcel, address))

            except Exception as e:
                log.warn("Error during receive callback: %s" % str(e))

        except:
            pass


    def send(self, data: bytes, channel: bytes, transport: bytes, address: BinaryAddress) -> rx.Observable:
        # Create the parcel
        parcel = Parcel(uuid.uuid4(), channel, transport, address.application, data)

        # Send over network
        return self.networks[address.network_type].send(parcel.serialise(), address)

    
    def add_application(self, protocol: bytes):
        self.applications.add(protocol)
        

    def remove_application(self, protocol: bytes):
        self.applications.remove(protocol)