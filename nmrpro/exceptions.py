class SpecError(Exception):
    '''Base exception class for NMR Django app'''

class NoNMRDataError(SpecError):
    '''Raised when path provided does not contain NMR files.'''

class DomainError(SpecError):
    '''
    Raised when an incorrect domian (time, frequency) is provided.

    For example, because baseline correction works only on frquency
    domain, the function will raise an error if a time-domain is
    provided.
    '''

class NMRTypeError(SpecError):
    '''
    Raised when an incorrect type is provided.
    
    Examples include passing a single spectrum when a dataset is expected,
    Incorrect number of dimnesions (2D to a function supporting 1D only).
    '''
    
class NMRShapeError(SpecError):
    '''
    Raised when an incorrect shape is provided.
    
    Examples include passing apodization window with different shape than the spectrum.
    '''


class ArgumentError(SpecError):
    '''Raised when an incompatible argument is passed to a function.'''