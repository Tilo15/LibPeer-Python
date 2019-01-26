from LibPeer.Discoverers.AMPP.Bootstrappers import Bootstrapper
from LibPeer.Formats.BinaryAddress import BinaryAddress
from LibPeer.Networks.Ipv4 import Ipv4
from LibPeer.Logging import log

import dns.resolver
import rx

DOMAINS = ["libpeer.pcthingz.com", "libpeer.unitatem.net", "libpeer.mooo.com"]

class DNS(Bootstrapper):
    def __init__(self, networks):
        super().__init__(networks)

        # Store the results in a ReplaySubject
        self.discovered = rx.subjects.ReplaySubject()

        log.debug("Looking up TXT records")

        for entry in DOMAINS:
            # Query
            try:
                log.debug("Querying domain: %s" % entry)
                answers = dns.resolver.query(entry, "TXT")
            except:
                log.warn("Unable to lookup TXT records for %s" % entry)
                continue

            # Read the text data
            for answer in answers:
                for txt in answer.strings:
                    # Does it start with 'LP:'?
                    if(txt.startswith(b"LP:")):
                        # Valid LibPeer entry!
                        entry_type = txt[3:7]

                        if(entry_type == b"MOTD"):
                            # Message of the day
                            log.info("%s says: %s" % (entry, txt[8:].replace(b"::", b":").decode("utf-8")))

                        elif(entry_type == b"ADDR"):
                            # IPv4 Address
                            info = txt[8:].split(b":")

                            # Add peers
                            self.discovered.on_next(BinaryAddress(Ipv4.identifier, info[0], info[1], b"AMPP"))

                        elif(entry_type == b"NAME"):
                            # DNS Name
                            info = txt[8:].split(b":")

                            # Query for address(es)
                            try:
                                response = dns.resolver.query(info[0].decode("utf-8"))
                            except:
                                log.warn("Unable to lookup name %s as suggested by DNS seed %s" % (info[0].decode("utf-8"), entry))
                                continue

                            # Add each response
                            for result in response:
                                self.discovered.on_next(BinaryAddress(Ipv4.identifier, result.address.encode("utf-8"), info[1], b"AMPP"))
                            

                        else:
                            log.debug("Encountered invalid LibPeer DNS TXT entry")

        # Done!
        log.debug("Completed DNS lookups")


    def stop(self):
        pass
