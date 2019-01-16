from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class Network:
	def __init__(self, protocol: bytes, name: str, active: str):
		self.protocol: bytes = protocol
		self.name: str = name
		self.active: str = active
	
	
	def serialise(self):
		items = [
			Primitives.type_binary.serialise(self.protocol),
			Primitives.type_string.serialise(self.name),
			Primitives.type_string.serialise(self.active),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return Network(
			Primitives.type_binary.deserialise(items[0]),
			Primitives.type_string.deserialise(items[1]),
			Primitives.type_string.deserialise(items[2])
		)

from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class Transport:
	def __init__(self, protocol: bytes, name: str):
		self.protocol: bytes = protocol
		self.name: str = name
	
	
	def serialise(self):
		items = [
			Primitives.type_binary.serialise(self.protocol),
			Primitives.type_string.serialise(self.name),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return Transport(
			Primitives.type_binary.deserialise(items[0]),
			Primitives.type_string.deserialise(items[1])
		)

from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class Address:
	def __init__(self, protocol: bytes, address: bytes, port: bytes, label: bytes):
		self.protocol: bytes = protocol
		self.address: bytes = address
		self.port: bytes = port
		self.label: bytes = label
	
	
	def serialise(self):
		items = [
			Primitives.type_binary.serialise(self.protocol),
			Primitives.type_binary.serialise(self.address),
			Primitives.type_binary.serialise(self.port),
			Primitives.type_binary.serialise(self.label),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return Address(
			Primitives.type_binary.deserialise(items[0]),
			Primitives.type_binary.deserialise(items[1]),
			Primitives.type_binary.deserialise(items[2]),
			Primitives.type_binary.deserialise(items[3])
		)

from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class Message:
	def __init__(self, address: Address, payload: bytes, channel: bytes, transport: bytes):
		self.address: Address = address
		self.payload: bytes = payload
		self.channel: bytes = channel
		self.transport: bytes = transport
	
	
	def serialise(self):
		items = [
			self.address.serialise(),
			Primitives.type_binary.serialise(self.payload),
			Primitives.type_binary.serialise(self.channel),
			Primitives.type_binary.serialise(self.transport),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return Message(
			Address.deserialise(items[0]),
			Primitives.type_binary.deserialise(items[1]),
			Primitives.type_binary.deserialise(items[2]),
			Primitives.type_binary.deserialise(items[3])
		)

from LibMedium.Specification.Item import Primitives
import LibMedium.Util

class Peer:
	def __init__(self, administrative_distance: int, last_seen: float, address: Address):
		self.administrative_distance: int = administrative_distance
		self.last_seen: float = last_seen
		self.address: Address = address
	
	
	def serialise(self):
		items = [
			Primitives.type_uint16.serialise(self.administrative_distance),
			Primitives.type_double.serialise(self.last_seen),
			self.address.serialise(),
		]
		return LibMedium.Util.pack_list(items)
	
	@staticmethod
	def deserialise(data: bytes):
		items = LibMedium.Util.unpack_list(data)
		return Peer(
			Primitives.type_uint16.deserialise(items[0]),
			Primitives.type_double.deserialise(items[1]),
			Address.deserialise(items[2])
		)

