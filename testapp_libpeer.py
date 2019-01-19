from LibPeer.Networks.Ipv4 import Ipv4
from LibPeer.Muxer import Muxer
from LibPeer.Transports.EDP import EDP
from LibPeer.Discoverers.Samband import Samband

from LibPeer.Formats.BinaryAddress import BinaryAddress

import struct

from LibPeer.Logging import log

log.settings(True, 0)

def recv(info):
    data = info[0]
    chan = info[1]
    addr = info[2]

    print("Got message from peer %s over channel %s: %s" % (str(addr), str(chan), data.decode("utf-8")))

peers = set()

def new_peer(address):
    print("Found peer %s" % str(address))
    peers.add(address)


app = b"helloworld"

net = Ipv4({"address": "192.168.1.224", "port": 3001})
net.go_up()

muxer = Muxer([net])
muxer.add_application(app)

disc = Samband([net])
disc.add_application(app)
disc.discovered.subscribe(new_peer)

trans = EDP(muxer, {})
trans.incoming.subscribe(recv)

while True:
    # chan = int(input("Channel: "))
    mesg = input("Message: ").encode("utf-8")

    for peer in peers:    
        print("************" * 4)
        trans.send(mesg, struct.pack("!QQ", 0, 0), app, peer).subscribe(lambda x: print("Sent to %s" % peer))

    for address in disc.get_addresses():
        address.application = app
        disc.advertise(address)
    
    print("Advertised")