from LibMedium.Medium.Listener.Application import Application
from LibMedium.Util.Defer import Defer
from LibPeerUnix.Server import LibPeerUnixServerBase
import LibPeerUnix.Exceptions
import LibPeerUnix.Models
from LibPeerUnix.Utilities import LabelCollection, PeerCollection, TransmitItem
from LibPeer.Discoverers import Discoverer
from LibPeer.Discoverers.Samband import Samband
from LibPeer.Networks import Network
from LibPeer.Networks.Ipv4 import Ipv4
from LibPeer.Muxer import Muxer
from LibPeer.Transports import Transport
from LibPeer.Transports.EDP import EDP
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Logging import log

import threading
import time
import queue

class LibPeerUnixServer(LibPeerUnixServerBase):
    
    def run(self):
        # This is called when the daemon is ready to communicate. Do your background tasks in here.
        # Communication is managed in a different thread, so feel free to place your infinate loop here.
        # A set of application connections can be found at 'self.applications'.
        # All your events are available to fire off at any time using 'self.event_name(*params)'.
        # To fire an event to a single application instance, pass in the application as the last
        # paramater in the event call, eg. 'self.event_name(param1, param2, application)'
        
        # Setup networks (TODO needs system config)
        self.networks = [
            Ipv4({"address": "", "port": 3000}),
        ] # TODO put up

        # Setup muxer (TODO needs system config)
        self.muxer = Muxer(self.networks)

        # Setup transports (TODO needs system config)
        self.transports = [
            EDP(self.muxer, {})
        ] # TODO attach listeners

        # Setup discoverers (TODO needs system config)
        self.discoverers = [
            Samband(self.networks)
        ] # TODO attach listeners

        # Setup priority map (TODO needs system config)
        self.namespace_priorities = {

        }

        # Setup maps
        self.app_namespace = {}
        self.namespace_app = {}
        self.application_labels = {}
        self.applications_advertised = set()
        self.discoveries = {}
        self.transport_map = {} # TODO set up

        self.tx_queue = queue.PriorityQueue()


    def ensure_bound(self, application: Application):
        if(application not in self.app_namespace):
            raise LibPeerUnix.Exceptions.UnboundError("That method cannot be called before bind(nameapce) is called.")

    
    def peer_discovered(self, peer: BinaryAddress, distance_mul: int):
        # Determine administrative distance
        distance = 1

        # Change AD to 0 if this is the local machine
        for discoverer in self.discoverers:
            if(peer in discoverer.get_addresses()):
                distance = 0
                break

        # Get the PeerCollection for this namespace
        collection: PeerCollection = self.discoveries[peer.application]

        # Tell it of our find, and get the model to notify the application with
        model = collection.found_peer(peer, distance).get_model()

        # Notify the relevent application
        app = self.namespace_app[peer.application]
        self.new_peer(model, app)

        

    def advertiser(self, app: Application, discoverer: Discoverer):
        # Get the application's namespace
        namespace = self.app_namespace[app]

        while(app in self.applications_advertised):
            # Get peer's address
            addresses = discoverer.get_addresses()

            # Get the label lock
            with self.application_labels[app].lock:
                # Loop over each address
                for address in addresses:
                    # Give the address application information
                    address.application = namespace

                    # Loop over each label
                    for label in self.application_labels[app].labels:
                        # Add label info to the address
                        address.label = label

                        # Advertise with the label info
                        discoverer.advertise(address)
            
            # Get ready to store time to wait after advertising
            wait = 0

            # Now advertise the application with no label
            for address in addresses:
                # Clear the label
                address.label = None

                # Advertise
                wait = discoverer.advertise(address)

            # Wait before advertising again
            time.sleep(wait)
        
    
    
    # Below are all the method calls you will need to handle.
    def available_discoverers(self, caller: Application) -> list:
        return [d.__class__.__name__ for d in self.discoverers]
    
    
    def available_networks(self, caller: Application) -> list:
        return [LibPeerUnix.Models.Network(n.identifier, n.__class__.__name__, n.up) for n in self.networks]
    
    
    def available_transports(self, caller: Application) -> list:
        return [LibPeerUnix.Models.Transport(t.identifier, n.__class__.__name__) for t in self.transports]
    
    
    def bind(self, caller: Application, application: bytes):
        # Make sure no other application is currently bound
        if(application in self.namespace_app):
            raise LibPeerUnix.Exceptions.NamespaceOccupiedError("Can not bind to the namespace '%s' as it is already in use" % application.decode("utf-8"))

        # Set the namespace's app to be the caller
        self.namespace_app[application] = caller

        # Now set the application's namespace 
        self.app_namespace[caller] = application

        # Give the application a label collection
        self.application_labels[caller] = LabelCollection()

        # Create a new collection for our discoveries dict
        self.discoveries[application] = PeerCollection()

        # Start listening for data addressed to this namespace
        self.muxer.add_application(application)

        # Start listening for advertisments with this namespace
        for discoverer in self.discoverers:
            discoverer.add_application(application)
    
    
    def set_discoverable(self, caller: Application, discoverable: bool):
        # Make sure the application has bound to a namespace
        self.ensure_bound(caller)

        if(caller in self.applications_advertised and not discoverable):
            self.applications_advertised.remove(caller)

        else:
            # Add the app to the advertised list
            self.applications_advertised.add(caller)

            # Create an advertiser thread for each discoverer
            for discoverer in self.discoverers:
                threading.Thread(target=self.advertiser, args=(caller, discoverer)).start()
    
    
    def add_label(self, caller: Application, label: bytes):
        # Make sure the application has bound to a namespace
        self.ensure_bound(caller)

        # Add the label
        self.application_labels[caller].add_label(label)
    
    
    def remove_label(self, caller: Application, label: bytes):
        # Make sure the application has bound to a namespace
        self.ensure_bound(caller)

        # Remove the label
        self.application_labels[caller].remove_label(label)
    
    
    def clear_labels(self, caller: Application):
        # Make sure the application has bound to a namespace
        self.ensure_bound(caller)

        # Clear the labes
        self.application_labels[caller].clear_labels()
    
    
    def get_peers(self, caller: Application) -> list:
        # Make sure the application has bound to a namespace
        self.ensure_bound(caller)

        # Get all peers under the namespace
        return self.discoveries[self.app_namespace[caller]].get_peer_models()
    
    
    def get_labelled_peers(self, caller: Application, label: bytes) -> list:
        # Make sure the application has bound to a namespace
        self.ensure_bound(caller)

        # Get all peers under the namespace with a label
        return self.discoveries[self.app_namespace[caller]].get_peer_models_with_label(label)
    
    
    def send(self, caller: Application, message: LibPeerUnix.Models.Message):
        # Make sure the application has bound to a namespace
        self.ensure_bound(caller)

        # Get the transport to send the message with
        transport: Transport = self.transport_map[message.transport]

        # Create the BinaryAddress to send the message with
        address = BinaryAddress(message.address.protocol, message.address.address, message.address.port, self.app_namespace[caller])

        # Defer the result until the sending has completed
        defer = Defer()

        # Send the data using the transport
        transport.send(message.payload, message.channel, address)

        pass
    
    
    def close(self, caller: Application):
        pass



    # Create a thread for outgoing network traffic
    def transmitter(self):
        # TODO add proper shutdown
        while True:
            # Queue of TransmitItems
            self.tx_queue.get().execute()



    
    
# If you run this module, it will run your daemon class above
if __name__ == '__main__':
    daemon = LibPeerUnixServer()

