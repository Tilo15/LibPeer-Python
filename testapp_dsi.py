from LibPeer.Application import Application
from LibPeer.Interfaces.DSI import DSI
from LibPeer.Interfaces.DSI.Connection import Connection

import sys
import threading
import time

app = Application("dsistreamer")

dsi = DSI(app)

def pipe(connection: Connection):
    while connection.connected:
        sys.stdout.buffer.write(connection.read(1024))
        sys.stdout.buffer.flush()


connections = []

def new_connection(connection: Connection):
    sys.stderr.write("New connection from %s\n" % connection.peer)
    threading.Thread(target=pipe, args=(connection))
    connections.append(connection)




dsi.new_connection.subscribe(new_connection)
app.set_discoverable(True)

# Wait 10 seconds and attempt connection to all peers
time.sleep(10)

sys.stderr.write("Finding peers...\n")
for discovery in app.find_peers():
    try:
        sys.stderr.write("Attempting connection with %s\n" % str(discovery.peer))
        conn = dsi.connect(discovery.peer)
        connections.append(conn)
        threading.Thread(target=pipe, args=(conn))
        sys.stderr.write("Established connection with %s\n" % str(discovery.peer))
    
    except Exception as e:
        sys.stderr.write("Failed to establish connection with %s, %s\n" % (str(discovery.peer), str(e)))

sys.stderr.write("Now piping...\n")


while True:
    data = sys.stdin.buffer.read(8192)
    
    # Send to each subscribed peer
    for connection in connections:
        if(connection.connected):
            connection.send(data)



