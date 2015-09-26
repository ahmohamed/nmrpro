from .apod import webApod
from .. import JSinput as inp
from ..PluginMount import SpecPlugin, JSCommand

class Apodization(SpecPlugin):
    __version__ = '0.1.0'
    __plugin_name__ = 'Apodization'
    __help__ = ''

    # TODO
    interface = {
    'Processing':{
        'Apodization':{
            'Expoenential line broadnening (auto)':{
                'fun':webApod,
                'args':None            
            },
            'Advanced apodization':{
                'fun':webApod,
                'title': 'Apodization',
                'args':{
                    'key':inp.multiselect('Select window function:', {
                        'em':inp.checkbox_option('Exponential', True,
                            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
                        ),
                        'sb':inp.checkbox_option('Sine-bell', False,
                            {'sboff':inp.num('Offset (0~1)', 0.5, 0, 1, step=0.01)}
                        ),
                        'sb2':inp.checkbox_option('Sine-bell', False,
                            {'sboff':inp.num('Offset (0~1)', 0.5, 0, 1, step=0.01)}
                        ),
                        'gauss':inp.checkbox_option('Gaussian', False,
                            {'gausslb':inp.num('Line broadening', 0.0, step=0.01, unit='Hz')}
                        ),
                        'sgauss':inp.checkbox_option('Shifted gaussian', False,
                            {'sgausslb':inp.num('Line broadening', 0.0, step=0.01, unit='Hz'),
                            'sgaussshift':inp.num('Shift', 0, unit='Points')},
                        ),
                        'gm':inp.checkbox_option('Lorentz-to-Gauss', False,
                            {'gmg1':inp.num('Inverse exponential width', 0.0, step=0.01, unit='Hz'),
                            'gmg2':inp.num('Gaussian broaden width', 0.0, step=0.01, unit='Hz'),
                            'gmg3':inp.num('Location of Gaussian maximum (0~1)', 0.0, 0, 1, step=0.01, unit='Hz')},
                        ),
                        'gmb':inp.checkbox_option('Modified gaussian', False,
                            {'gmblb':inp.num('Exponential term', 0.0, step=0.01, unit='Hz'),
                            'gmbgb':inp.num('Gaussian term', 0.0, step=0.01)},
                        ),
                        'jmod':inp.checkbox_option('Exponentially damped J-modulation', False,
                            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
                        ),
                        'sp':inp.checkbox_option('Custom Sine-bell', False,
                            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
                        ),
                        'tm':inp.checkbox_option('Trapezoid', False,
                            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
                        ),
                        'tri':inp.checkbox_option('Triangle', False,
                            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
                        ),
                    }),
                }
            },
        }
    }
    }

class Exp_Apod(JSCommand):
    menu_path = ['Processing', 'Apodization', 'Expoenential line broadnening (auto)']
    fun = staticmethod(webApod)
    nd = [1]

class Adv_Apod(JSCommand):
    menu_path = ['Processing', 'Apodization', 'Advanced apodization']
    fun = staticmethod(webApod)
    nd = [1,2]
    args = {
        'inv':inp.boolean('inverse apodization', False),
        'c':inp.num('Scale first point', 0.5, 0, 1, step=0.01),
        'em':inp.checkbox_option('Exponential', True,
            {'em_lb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
        ),
        'sb':inp.checkbox_option('Sine-bell', False,
            {'sb_off':inp.num('Offset (0~1)', 0.5, 0, 1, step=0.01)}
        ),
        'sb2':inp.checkbox_option('Sine-bell-Squared', False,
            {'sb2_off':inp.num('Offset (0~1)', 0.5, 0, 1, step=0.01)}
        ),
        'gauss':inp.checkbox_option('Gaussian', False,
            {'gauss_lb':inp.num('Line broadening', 0.0, step=0.01, unit='Hz')}
        ),
        'sgauss':inp.checkbox_option('Shifted gaussian', False,
            {'sgauss_lb':inp.num('Line broadening', 0.0, step=0.01, unit='Hz'),
            'sgauss_shift':inp.num('Shift', 0, unit='Points')},
        ),
        'gm':inp.checkbox_option('Lorentz-to-Gauss', False,
            {'gm_g1':inp.num('Inverse exponential width', 0.0, step=0.01, unit='Hz'),
            'gm_g2':inp.num('Gaussian broaden width', 0.0, step=0.01, unit='Hz'),
            'gm_g3':inp.num('Location of Gaussian maximum (0~1)', 0.0, 0, 1, step=0.01, unit='Hz')},
        ),
        'gmb':inp.checkbox_option('Modified gaussian', False,
            {'gmb_lb':inp.num('Exponential term', 0.0, step=0.01, unit='Hz'),
            'gmb_gb':inp.num('Gaussian term', 0.0, step=0.01)},
        ),
        'jmod':inp.checkbox_option('Exponentially damped J-modulation', False,
            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
        ),
        'sp':inp.checkbox_option('Custom Sine-bell', False,
            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
        ),
        'tm':inp.checkbox_option('Trapezoid', False,
            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
        ),
        'tri':inp.checkbox_option('Triangle', False,
            {'emlb':inp.num('Line broadening', 0.2, step=0.01, unit='Hz')}
        ),
    }


    