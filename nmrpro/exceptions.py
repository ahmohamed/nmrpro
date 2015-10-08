class SpecError(Exception):
    '''Base exception class for NMR Django app'''

class NoNMRDataError(SpecError):
    '''Raised when path provided does not contain NMR files.'''

class DomainError(SpecError):
    '''Raised when an incorrect domian (time, frequency) is provided.
        For example, because baseline correction works only on frquency
        domain, the function will raise an error if a time-domain is
        provided.
    '''
