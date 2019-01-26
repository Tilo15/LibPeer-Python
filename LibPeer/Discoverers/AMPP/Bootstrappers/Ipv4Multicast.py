from LibPeer.Discoverers.AMPP.Bootstrappers import Bootstrapper
from LibPeer.Discoverers.Samband import Samband
from LibPeer.Networks.Ipv4 import Ipv4

import threading
import time

class Ipv4Multicast(Bootstrapper):
    def __init__(self, networks):
        super().__init__(networks)

        self.running = True

        # Create Samband instance (it doesn't use the network, just checks it's id)
        self.samband = Samband(networks)

        # Forward messages from the Samband instance
        self.samband.discovered.on_next(lambda x: self.discovered.on_next(x))

        # Add AMPP to the list to listen for
        self.samband.add_application(b"AMPP")

        # Run advertiser
        threading.Thread(target=self.advertiser).start()


    def advertiser(self):
        # Advertise the AMPP instance
        while self.running:
            addresses = self.samband.get_addresses()

            delay = 0

            for address in addresses:
                address.application = b"AMPP"
                delay = self.samband.advertise(address)

            time.sleep(delay)


    def stop(self):
        self.running = False
