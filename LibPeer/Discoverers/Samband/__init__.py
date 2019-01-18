from LibPeer.Formats.Samband import SambandPacket
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Discoverers import Discoverer
from LibPeer.Logging import log
from LibPeer.Networks.Ipv4 import Ipv4

from netifaces import interfaces, ifaddresses, AF_INET

import socket
import struct
import threading
import uuid

class Samband(Discoverer):
    def __init__(self, networks: list):
        super().__init__(networks)

        self.applications = set()

        # Find IPv4 network (required for this discoverer)
        self.ipv4: Ipv4 = None
        for network in networks:
            if(network.identifier == b"IPv4"):
                self.ipv4 = network
                break
        
        if(self.ipv4 == None):
            raise TypeError("An IPv4 network is required to run this discoverer")

        self._received_ids = set()

        # Setup the multicast channel
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("224.0.0.63", 1944))
        mreq = struct.pack("=4sl", socket.inet_aton("224.0.0.63"), socket.INADDR_ANY)
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.listening = True
        threading.Thread(target=self._listener).start()



    def _listener(self):
        log.debug("Started listening for local applications")
        while(self.listening):
            data = self._socket.recv(65536)
            
            try:
                packet, valid = SambandPacket.deserialise(data)

                # Drop if checksum invalid
                if(not valid):
                    log.debug("Dropped packet with invalid checksum")
                    continue
                    
                # Ignore any duplicates
                if(packet.id.bytes in self._received_ids):
                    continue

                if(packet.address.application in self.applications):
                    self.discovered.on_next(packet.address)

            except Exception as e:
                log.warn("Encountered exception on listener thread: %s" % str(e))
                # TODO remove
                import traceback
                print(traceback.format_exc())


    def advertise(self, address: BinaryAddress) -> int:
        packet = SambandPacket(uuid.uuid4(), address)
        # Send the packet
        self._socket.sendto(packet.serialise(), ('224.0.0.63', 1944))

        # Recommend re-advertising in 5 seconds
        return 5


    def add_application(self, namespace: bytes):
        self.applications.add(namespace)


    def remove_aplication(self, namespace: bytes):
        self.applications.remove(namespace)

    def get_addresses(self) -> list:
        addrs = []
        for interface in interfaces():
            addresses = ifaddresses(interface)
            if(AF_INET in addresses):
                for link in addresses[AF_INET]:
                    if(link['addr'] != '127.0.0.1'):
                        addrs.append(BinaryAddress(b"IPv4", link['addr'].encode('utf-8','ignore'), str(self.ipv4.options["port"]).encode("utf-8")))

        return addrs
    

    def stop(self):
        self.listening = False