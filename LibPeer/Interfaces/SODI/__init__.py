from LibPeer.Application.Preferences import TransportPreferences
from LibPeer.Application.ApplicationBase import ApplicationBase
from LibPeer.Application.Reception import Reception
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Interfaces import Interface
from LibPeer.Interfaces.SODI.Reply import Reply
from LibPeer.Interfaces.SODI.Solicitation import Solicitation

import rx

class SODI(Interface):
    def __init__(self, app: ApplicationBase, channel: bytes = b"\x00"*16, transport: str = "DSTP"):
        super().__init__(app, channel, transport)
        self._replies = {}
        self._tokens = {}
        self._solicitations = {}

        self.solicited = rx.subjects.Subject()


    def _receive(self, data: bytes, peer: BinaryAddress):
        # If a reply already exists, pass data into it
        if(peer in self._replies):
            reply = self._replies[peer]

            # Get the object state before passing in data
            obj_state = reply._has_object

            # Pass in data
            leftovers = self._replies[peer]._receive(data)

            # Handle events for this reply
            self._check_complete(reply, peer, obj_state)


        elif(peer in self._tokens):
            # Create a reply object
            reply = Reply(peer, data)

            # If the token matches, save it
            if(reply.token.bytes == self._tokens[peer]):
                self._replies[peer] = reply

                # Handle events for this reply
                self._check_complete(reply, peer)


        else:
            try:
                # Must be a solicitation!
                solic = Solicitation.deserialise(data, peer, self)

                # Notify app
                self.solicited.on_next(solic)
            except:
                pass



    def _check_complete(self, reply: Reply, peer: BinaryAddress, prior_has_object_state = False):
        # If done, forget about it all!
        if(reply._is_complete):
            del self._tokens[peer]
            del self._replies[peer]

        # If that changed, notify app
        if(prior_has_object_state != reply._has_object):
            self._solicitations[reply.token.bytes].on_next(reply)
            self._solicitations[reply.token.bytes].on_completed()
            del self._solicitations[reply.token.bytes]


    def solicit(self, peer: BinaryAddress, query: str) -> rx.Observable:
        solic = Solicitation(self, peer, query)

        # Create and store the observable
        observable = rx.subjects.Subject()
        self._solicitations[solic.token.bytes] = observable

        # Store the token so we can accept the response
        self._tokens[peer] = solic.token.bytes

        # Send the solicitation
        self._send(solic.serialise(), peer)

        # Return observable
        return observable


            


        
