from LibPeer.Networks.Ipv4 import Ipv4
from LibPeer.Discoverers.AMPP import AMPP
from LibPeer.Logging import log

import sys
import time

if(len(sys.argv) != 2):
    print("Usage:\n\tAMPP_Server <port>\n\t<port>\tThe UDP port to listen on")
    exit(1)

log.settings(True, 0)

nets = [Ipv4({"address": "", "port": int(sys.argv[1])}),]
nets[0].go_up()

ampp = AMPP(nets)

try:
    while True:
        addrs = ampp.get_addresses()
        delay = 1
        for address in addrs:
            # Set app
            address.application = b"AMPP"
            delay = ampp.advertise(address)

        time.sleep(delay)

except:
    ampp.stop()

exit(0)

        