from LibPeer.Networks import Network
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Logging import log

import socket
import threading
import rx
import traceback

class Ipv4(Network):
    identifier = b"IPv4"

    def __init__(self, options: dict):
        super().__init__(options)
        self._socket = None


    def go_up(self) -> bool:
        """Attempt to get the network ready to used. Returns true on success"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.bind((self.options["address"], self.options["port"]))
            self.up = True

            threading.Thread(target=self._listen).start()
            return True

        except:
            return False

    
    def _listen(self):
        while self.up:
            try:
                data, addr = self._socket.recvfrom(65536)
                address = BinaryAddress(self.identifier, addr[0].encode("utf-8"), str(addr[1]).encode("utf-8"))
                self.incoming.on_next((data, address))

            except Exception as e:
                log.error("Exception on listener thread: " + str(e))
                tb = traceback.format_exc()
                for line in tb.split("\n"):
                    log.error(line)
        
        log.info("Listening stopped.")


    def go_down(self,):
        """Shut down the network interface"""
        self.up = False
        self._socket.close()


    def send(self, data: bytes, address: BinaryAddress) -> rx.Observable:
        """Send the specified data to the specified address"""
        def send_it():
            self._socket.sendto(data, (address.network_address, int(address.network_port)))

        return rx.Observable.from_callable(send_it)
