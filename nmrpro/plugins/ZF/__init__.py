from .zf import ZF
from .. import JSinput as inp
from ..PluginMount import SpecPlugin, JSCommand

class ZFDouble(JSCommand):
    menu_path = ['Processing', 'Zero Filling', 'Zero fill to double size']
    fun = staticmethod(ZF)
    nd = [1,2]

class CustomZF(JSCommand):
    menu_path = ['Processing', 'Zero Filling', 'Custom size zero filling']
    fun = staticmethod(ZF)
    nd = [1,2]
    args = {
        "size":inp.select("Zero fill to (points):", {
            "1024":inp.option("1K"),
            "2048":inp.option("2K"),
            "4096":inp.option("4K"),
            "8192":inp.option("8K"),
            "16384":inp.option("16K"),
            "32768":inp.option("32K"),
            "65536":inp.option("64K"),
            "131072":inp.option("128K"),
        }),
    }
    