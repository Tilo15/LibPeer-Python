from LibPeer.Networks.Ipv4 import Ipv4
from LibPeer.Muxer import Muxer
from LibPeer.Transports.EDP import EDP

from LibPeer.Formats.BinaryAddress import BinaryAddress

import struct

def recv(info):
    data = info[0]
    chan = info[1]
    addr = info[2]

    print("Got message from peer %s over channel %s: %s" % (str(addr), str(chan), data.decode("utf-8")))

app = b"quickmessage"

net = Ipv4({"address": "", "port": 3001})
net.go_up()

muxer = Muxer([net])
muxer.add_application(app)

trans = EDP(muxer, {})
trans.incoming.subscribe(recv)

while True:
    addr = input("Dest: ").encode("utf-8").split(b":")
    chan = int(input("Channel: "))
    mesg = input("Message: ").encode("utf-8")

    trans.send(mesg, struct.pack("!QQ", 0, chan), app, BinaryAddress(net.identifier, addr[0], addr[1])).subscribe(lambda x: print("Sent!"))