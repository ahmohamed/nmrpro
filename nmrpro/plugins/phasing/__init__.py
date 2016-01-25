from .ps import *

__all__ = ['ps', 'autops']
#
# class Autophase(JSCommand):
#     menu_path = ['Processing', 'Phase Correction', 'Automatic phase correction']
#     fun = staticmethod(webPhase)
#     nd = [1,2]
#
#
# class AdvPhase(JSCommand):
#     menu_path = ['Processing', 'Phase Correction', 'Advanced phase correction']
#     fun = staticmethod(webPhase)
#     nd = [1,2]
#     args = {
#         'a':inp.select('Phase correction method', {
#             'man':inp.option('Manual phase correction',
#                 {'p0':inp.num('Zero-order', val=0),
#                 'p1':inp.num('First-order', val=0),}
#             ),
#             'atan':inp.option('Autmatic using arctan',
#                 {'p0only':inp.boolean('Zero-order phase only', val=False),}
#             ),
#             'opt':inp.option('Automatic using optimization function',{
#                 'optfn':inp.select('Optimization method', {
#                     'autosim':inp.option('Simultaneous optimization of 0 & 1st order phases'),
#                     'auto':inp.option('Sequential optimization of 0 & 1st order phases'),
#                     'auto0':inp.option('Optimization of 0 order phase only'),
#                 }),
#                 'objfn':inp.select('Automatic phasing method (objective function)', {
#                     'entropy':inp.option('Entropy minization'),
#                     'integ':inp.option('Intrgration maximization'),
#                     'minpoint':inp.option('Minimum point maximization'),
#                     'peakmin':inp.option('Peak minima maximization'),
#                     'whiten':inp.option('Whitening'),
#                 }),
#             }),
#         }),
#     }