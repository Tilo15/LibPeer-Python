class NamespaceOccupiedError(Exception):
	pass

class NetworkError(Exception):
	pass

class DataError(Exception):
	pass

class UnboundError(Exception):
	pass

from LibMedium.Medium import RemoteCallException

ERROR_MAP = {
	1: NamespaceOccupiedError,
	2: NetworkError,
	3: DataError,
	4: UnboundError,
}


def throw(error: RemoteCallException):
	if(error.error_no in ERROR_MAP):
		raise ERROR_MAP[error.error_no](str(error))
	raise(error)

REV_ERROR_MAP = {
	NamespaceOccupiedError: 1,
	NetworkError: 2,
	DataError: 3,
	UnboundError: 4,
}


