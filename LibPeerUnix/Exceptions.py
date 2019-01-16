class NamespaceOccupiedError(Exception):
	pass

class TransportError(Exception):
	pass

class NetworkError(Exception):
	pass

class DataError(Exception):
	pass

from LibMedium.Medium import RemoteCallException

ERROR_MAP = {
	1: NamespaceOccupiedError
	2: TransportError
	3: NetworkError
	4: DataError
}


def throw(error: RemoteCallException):
	if(error.error_no in ERROR_MAP):
		raise ERROR_MAP[error.error_no](str(error))
	raise(error)

REV_ERROR_MAP = {
	NamespaceOccupiedError: 1
	TransportError: 2
	NetworkError: 3
	DataError: 4
}


