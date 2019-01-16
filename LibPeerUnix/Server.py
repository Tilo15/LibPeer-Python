from LibMedium.Daemon import Daemon
from LibMedium.Medium.Listener import Listener
from LibMedium.Medium.Listener.Application import InvocationEvent
from LibMedium.Medium.Listener.Application import Application
from LibMedium.Messages.Event import Event
from LibMedium.Util.Defer import Defer
from LibMedium.Specification.Item import Primitives

import LibPeerUnix.Exceptions
import LibPeerUnix.Models

class LibPeerUnixServerBase:
	def __init__(self):
		self.applications = set()
		self._daemon = Daemon('net.unitatem.libpeer')
		self._listener = Listener(self._daemon)
		
		self._listener.invoked.subscribe(self._handle_invocation)
		self._listener.new_connection.subscribe(self._handle_connection)
		
		self._invocation_handlers = {
			b'available_discoverers': self._handle_available_discoverers_invocation,
			b'available_networks': self._handle_available_networks_invocation,
			b'available_transports': self._handle_available_transports_invocation,
			b'bind': self._handle_bind_invocation,
			b'set_discoverable': self._handle_set_discoverable_invocation,
			b'add_label': self._handle_add_label_invocation,
			b'remove_label': self._handle_remove_label_invocation,
			b'clear_labels': self._handle_clear_labels_invocation,
			b'get_peers': self._handle_get_peers_invocation,
			b'get_labelled_peers': self._handle_get_labelled_peers_invocation,
			b'send': self._handle_send_invocation,
			b'close': self._handle_close_invocation
		}
		
		self.run()
	
	def _handle_invocation(self, event):
		if(event.invocation.function in self._invocation_handlers):
			self._invocation_handlers[event.invocation.function](event)
		else:
			event.error('The invoked method does not exist on this service')
	
	def _handle_connection(self, application):
		self.applications.add(application)
	
	def _broadcast_event(self, event):
		for app in self.applications:
			if(app.alive):
				try:
					app.send_event(event)
				except:
					pass
	
	def _convert_exception(self, e: Exception):
		error_num = 0
		if(type(e) in LibPeerUnix.Exceptions.REV_ERROR_MAP):
			error_num = LibPeerUnix.Exceptions.REV_ERROR_MAP[type(e)]
		return (str(e), error_num)
	
	def _handle_available_discoverers_invocation(self, event):
		values = []
		try:
			result = self.available_discoverers(event.app, *values)
			serialise_result = lambda x: Primitives.type_array.serialise([Primitives.type_string.serialise(x) for x in x])
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_available_networks_invocation(self, event):
		values = []
		try:
			result = self.available_networks(event.app, *values)
			serialise_result = lambda x: Primitives.type_array.serialise([x.serialise() for x in x])
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_available_transports_invocation(self, event):
		values = []
		try:
			result = self.available_transports(event.app, *values)
			serialise_result = lambda x: Primitives.type_array.serialise([x.serialise() for x in x])
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_bind_invocation(self, event):
		values = [
			Primitives.type_binary.deserialise(event.invocation.args[0]),
			Primitives.type_boolean.deserialise(event.invocation.args[1])
		]
		
		try:
			result = self.bind(event.app, *values)
			serialise_result = lambda x: b''
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_set_discoverable_invocation(self, event):
		values = [
			Primitives.type_boolean.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.set_discoverable(event.app, *values)
			serialise_result = lambda x: b''
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_add_label_invocation(self, event):
		values = [
			Primitives.type_binary.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.add_label(event.app, *values)
			serialise_result = lambda x: b''
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_remove_label_invocation(self, event):
		values = [
			Primitives.type_binary.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.remove_label(event.app, *values)
			serialise_result = lambda x: b''
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_clear_labels_invocation(self, event):
		values = []
		try:
			result = self.clear_labels(event.app, *values)
			serialise_result = lambda x: b''
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_get_peers_invocation(self, event):
		values = []
		try:
			result = self.get_peers(event.app, *values)
			serialise_result = lambda x: Primitives.type_array.serialise([x.serialise() for x in x])
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_get_labelled_peers_invocation(self, event):
		values = [
			Primitives.type_binary.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.get_labelled_peers(event.app, *values)
			serialise_result = lambda x: Primitives.type_array.serialise([x.serialise() for x in x])
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_send_invocation(self, event):
		values = [
			LibPeerUnix.Models.Message.deserialise(event.invocation.args[0])
		]
		
		try:
			result = self.send(event.app, *values)
			serialise_result = lambda x: b''
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	
	def _handle_close_invocation(self, event):
		values = []
		try:
			result = self.close(event.app, *values)
			serialise_result = lambda x: b''
			if(type(result) is Defer):
				result._attach(event, serialise_result, self._convert_exception)
			else:
				event.complete(serialise_result(result))
		
		except Exception as e:
			event.error(*self._convert_exception(e))
	

	
	def new_peer(self, peer: LibPeerUnix.Models.Peer, application: Application = None):
		event = Event(b'new_peer',
			peer.serialise())
		
		if(application):
			application.send_event(event)
		else:
			self._broadcast_event(event)
	
	def receive(self, message: LibPeerUnix.Models.Message, application: Application = None):
		event = Event(b'receive',
			message.serialise())
		
		if(application):
			application.send_event(event)
		else:
			self._broadcast_event(event)
	

	
	def available_discoverers(self, caller: Application) -> list:
		raise NotImplementedError
	
	def available_networks(self, caller: Application) -> list:
		raise NotImplementedError
	
	def available_transports(self, caller: Application) -> list:
		raise NotImplementedError
	
	def bind(self, caller: Application, application: bytes, local: bool):
		raise NotImplementedError
	
	def set_discoverable(self, caller: Application, discoverable: bool):
		raise NotImplementedError
	
	def add_label(self, caller: Application, label: bytes):
		raise NotImplementedError
	
	def remove_label(self, caller: Application, label: bytes):
		raise NotImplementedError
	
	def clear_labels(self, caller: Application):
		raise NotImplementedError
	
	def get_peers(self, caller: Application) -> list:
		raise NotImplementedError
	
	def get_labelled_peers(self, caller: Application, label: bytes) -> list:
		raise NotImplementedError
	
	def send(self, caller: Application, message: LibPeerUnix.Models.Message):
		raise NotImplementedError
	
	def close(self, caller: Application):
		raise NotImplementedError
	
	def run(self):
		raise NotImplementedError
	
