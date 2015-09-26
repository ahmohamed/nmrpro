from .fft import webFFT
from .. import JSinput as inp
from ..PluginMount import SpecPlugin, JSCommand

class FFTClass(SpecPlugin):
    __version__ = '0.1.0'
    __plugin_name__ = "Fourier transform"
    __help__ = ""

    interface = {
    "Processing":{
        "FFT":{
            "FFT":{
                "fun":webFFT,
                "args":None            
            },
        }
    }
    }


class FFTCommand(JSCommand):
    menu_path = ['Processing', 'FFT']
    fun = staticmethod(webFFT)
    nd = [1,2]
