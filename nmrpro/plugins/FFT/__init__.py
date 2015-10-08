from .fft import webFFT
from .fft import *
from .. import JSinput as inp
from ..PluginMount import JSCommand

__all__ = ['fft', 'fft_positive', 'fft_norm']

class FFTCommand(JSCommand):
    menu_path = ['Processing', 'FFT']
    fun = staticmethod(webFFT)
    nd = [1,2]
