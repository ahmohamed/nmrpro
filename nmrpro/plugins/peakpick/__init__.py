from .peakpick import *
# from nmrpro.plugins. import JSinput as inp
# from nmrpro.plugins.PluginMount import JSCommand
#
# pick_t = lambda data, args: pick(data,{'a':'t', 'thresh':float(args.get('thresh'))})

# class PickCWT(JSCommand):
#     menu_path = ['Analysis', 'Peak Picking', 'Automatically using CTW']
#     fun = staticmethod(pick)
#     nd = [1]
#
# class PickThreshold(JSCommand):
#     menu_path = ['Analysis', 'Peak Picking', 'Peaks below a Threshold']
#     fun = staticmethod(pick_t)
#     nd = [1]
#     args = {'thresh':inp.threshold('Peak Threshold', 'y')}

# class AdvPick(JSCommand):
#     menu_path = ['Analysis', 'Peak Picking', 'Custom Peak Picking']
#     fun = staticmethod(pick)
#     nd = [1]
#     args = {
#         'a':inp.select('Peak Picking algorithm', {
#             't':inp.option('Threshold',
#             {
#                 'thresh': inp.threshold('Peak Threshold', 'y'),
#                 'msep': inp.num('Minimum sepration between peaks', 0.001, step=0.001, unit='ppm'),
#             }),
#             'c':inp.option('Connected segments',
#                 {'thresh': inp.threshold('Peak Threshold', 'y')}
#             ),
#             'cwt':inp.option('Continuous wavelet transform',
#             {
#                 'w':inp.text('Wavelet widths'), #TODO: inp.num
#                 'snr':inp.num('Minimum Signal-to-noise ratio', 16, step=0.01),
#             }),
#         }),
#     }