from .bl import baseline
# from .bl import webBaseline, SOL
# from nmrpro.plugins. import JSinput as inp
# from nmrpro.plugins.PluginMount import JSCommand
    
# class ConstantBaselineCorrection(JSCommand):
#     menu_path = ['Processing', 'Baseline Correction', 'Constant Baseline Correction']
#     fun = staticmethod(webBaseline)
#     nd = [1,2]
#
# class AdvBaselineCorrection(JSCommand):
#     menu_path = ['Processing', 'Baseline Correction', 'Advanced baseline correction']
#     fun = staticmethod(webBaseline)
#     nd = [1]
#     title =  'Baseline correction methods'
#     args = {
#         'a':inp.select('Baseline correction algorithm', {
#             'cbf':inp.option('Constant',
#                 {'last':inp.num('Etimate from last %', val=10, _min=0, _max=100)}
#             ),
#             'med':inp.option('Median',
#                 {'mw':inp.num('Median window', val=50),
#                  'sf':inp.num('Smoothing window', val=24),
#                  'sigma':inp.num('sigma', val=5)
#                 }
#             ),
#             'polynom':inp.option('Polynomial', {'n':inp.num('Order', val=3)} ),
#             'cos':inp.option('Cosine series', {'n':inp.num('Order', val=3)} ),
#             'iter_polynom':inp.option('Iterative Polynomial', {'n':inp.num('Order', val=3)} ),
#             'airpls':inp.option('airPLS', {'n':inp.num('Order', val=1), 'lambda':inp.num('lambda', val=10)} ),
#             'th':inp.option('Tophat', {'size':inp.num('Structure element size', val=100, _min=1)} ),
#             #'bern':inp.option('Bernstein polynomials', {'n':inp.num('Order', val=3)} ),
#             #'als':inp.option('Asymmetric least squares', {} ),
#             #'fft':inp.option('Low FFT filter', {} ),
#         }),
#         'ret':inp.select('Show',
#             {'est':inp.option('Estimated baseline'),
#             'cor':inp.option('Corrected spectra'),}
#         ),
#     }
#
# class AdvBaselineCorrection2D(JSCommand):
#     menu_path = ['Processing', 'Baseline Correction', 'Advanced baseline correction (2D)']
#     fun = staticmethod(webBaseline)
#     nd = [2]
#     title =  'Baseline correction methods'
#     args = {
#         'a':inp.select('Baseline correction algorithm', {
#             'cbf':inp.option('Constant',
#                 {'last':inp.num('Etimate from last %', val=10, _min=0, _max=100)}
#             ),
#             'med':inp.option('Median',
#                 {'mw':inp.num('Median window', val=50),
#                  'sf':inp.num('Smoothing window', val=24),
#                  'sigma':inp.num('sigma', val=5)
#                 }
#             ),
#             'th':inp.option('Tophat', {'size':inp.num('Structure element size', val=100, _min=1)} ),
#             #'bern':inp.option('Bernstein polynomials', {'n':inp.num('Order', val=3)} ),
#             #'als':inp.option('Asymmetric least squares', {} ),
#             #'fft':inp.option('Low FFT filter', {} ),
#         }),
#     }
    
# class SolventFilter(JSCommand):
#     menu_path = ['Processing', 'Solvent Filter']
#     fun = staticmethod(SOL)
#     nd = [1,2]
#     title = 'Solvent filter'
#     args = {
#         'a':inp.select('Select filter:',
#             {'box':inp.option('Boxcar (rectangular)'),
#             'sine':inp.option('Sine-bell'),
#             'sine2':inp.option('Squared sine-bell'),
#             'gauss':inp.option('Squared Gaussian'),}
#         ),
#         'w':inp.num('Filter length', 16, unit='Points'),
#     }