class SpecError(Exception):
    '''Base exception class for NMR Django app'''

class PluginNotFoundError(SpecError):
    '''Raised when an unavailbale plugin is requested'''

class SessionError(SpecError):
    '''Raised when session data is unavailable'''

class DomainError(SpecError):
    '''Raised when an incorrect domian (time, frequency) is provided.
        For example, because baseline correction works only on frquency
        domain, the function will raise an error if a time-domain is
        provided.
    '''