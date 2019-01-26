# LibPeer-Python
Work in process implementation of the LibPeer Standard Protocols for Python 3. This repo aims to be the first implementation of LibPeer based entirely from the [specification document](https://saltlamp.pcthingz.com/utdata/LibPeer/LibPeer_Standard_Protocols_v1.pdf). This project aims to be the reference implementation for both the LibPeer Standard Protocols, and the yet to be released LibPeer Unix Service specifications.

The prototype implementation will be kept up for historical and possibly experemental purposes, but already the two implementations differ slightly. The MsgPack library that the protoype implementation uses seems to run into utf-8 errors when decoding data that isn't supposed to be utf-8 encoded. As this implementation was developed from the document, this implementation is considered correct.

This implementation has the following dependancies:
 * [LibMedium](https://github.com/Tilo15/LibMedium)
 * RxPy
 * netifaces
 * psutil

 ## Progress

There is still a bit of work to be done, but with a well laid out specification, it shouldn't take long to get through the list

- [ ] Discoverers
  - [x] Samband
  - [ ] AMPP
- [ ] Networks
  - [x] IPv4
  - [ ] NARP
- [x] Muxer
- [x] Transports
  - [x] EDP
  - [x] DSTP
- [x] Modifiers
- [X] Interfaces
  - [X] DSI
  - [x] OMI
  - [X] SODI
- [x] Application Utilities
- [ ] Daemon/Server Configuration

Note that the "aplication" utilities will be a nice API for applications to use and will not be based on the LibPeer Standard Protocols specification. The specification states that how the application facing API is laid out can be defined by the implementation.