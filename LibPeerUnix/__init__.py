from LibMedium.Daemon import Daemon
from LibMedium.Medium import RemoteCallException
from LibMedium.Specification.Item import Primitives

import rx

import LibPeerUnix.Exceptions
import LibPeerUnix.Models

class LibPeerUnixConnection:
	def __init__(self):
		self.new_peer: rx.subjects.Subject = rx.subjects.Subject()
		self.receive: rx.subjects.Subject = rx.subjects.Subject()
		
		self._event_map = {
			b'new_peer': self._handle_new_peer_event,
			b'receive': self._handle_receive_event,
		}
		
		self._daemon = Daemon('net.unitatem.libpeer')
		self._medium = self._daemon.summon()
		self._medium.event_received.subscribe(self._handle_event)
	
	def available_discoverers(self) -> list:
		try:
			return [Primitives.type_string.deserialise(x) for x in Primitives.type_array.deserialise(self._medium.invoke(b'available_discoverers').response)]
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def available_networks(self) -> list:
		try:
			return [LibPeerUnix.Models.Network.deserialise(x) for x in Primitives.type_array.deserialise(self._medium.invoke(b'available_networks').response)]
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def available_transports(self) -> list:
		try:
			return [LibPeerUnix.Models.Transport.deserialise(x) for x in Primitives.type_array.deserialise(self._medium.invoke(b'available_transports').response)]
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def bind(self, application: bytes, local: bool):
		try:
			self._medium.invoke(b'bind', Primitives.type_binary.serialise(application), Primitives.type_boolean.serialise(local)).response
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def set_discoverable(self, discoverable: bool):
		try:
			self._medium.invoke(b'set_discoverable', Primitives.type_boolean.serialise(discoverable)).response
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def add_label(self, label: bytes):
		try:
			self._medium.invoke(b'add_label', Primitives.type_binary.serialise(label)).response
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def remove_label(self, label: bytes):
		try:
			self._medium.invoke(b'remove_label', Primitives.type_binary.serialise(label)).response
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def clear_labels(self):
		try:
			self._medium.invoke(b'clear_labels').response
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def get_peers(self) -> list:
		try:
			return [LibPeerUnix.Models.Peer.deserialise(x) for x in Primitives.type_array.deserialise(self._medium.invoke(b'get_peers').response)]
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def get_labelled_peers(self, label: bytes) -> list:
		try:
			return [LibPeerUnix.Models.Peer.deserialise(x) for x in Primitives.type_array.deserialise(self._medium.invoke(b'get_labelled_peers', Primitives.type_binary.serialise(label)).response)]
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def send(self, message: LibPeerUnix.Models.Message):
		try:
			self._medium.invoke(b'send', message.serialise()).response
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def close(self):
		try:
			self._medium.invoke(b'close').response
		except RemoteCallException as e:
			LibPeerUnix.Exceptions.throw(e)
	
	def _handle_new_peer_event(self, params):
		args = [
			LibPeerUnix.Models.Peer.deserialise(params[0]),
		]
		
		self.new_peer.on_next(args)
	
	def _handle_receive_event(self, params):
		args = [
			LibPeerUnix.Models.Message.deserialise(params[0]),
		]
		
		self.receive.on_next(args)
	
	def _handle_event(self, event):
		self._event_map[event.name](event.args)
	

