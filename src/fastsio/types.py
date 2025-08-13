from typing import NewType

# Public typing alias for better readability in handler annotations
SocketID = NewType("SocketID", str)
Environ = NewType("Environ", dict)
Auth = NewType("Auth", dict)
Data = NewType("Data", dict)
Reason = NewType("Reason", str)

__all__ = ["SocketID", "Environ", "Auth", "Reason", "Data"]


