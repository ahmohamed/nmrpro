from pkgutil import walk_packages
from importlib import import_module
from PluginMount import SpecPlugin, JSCommand
'''
Recursively import all sub-packages in plugins.
Since all plugins are subclasses of SpecPlugin,
importing is enough to retrieve them via SpecPlugin.get_plugins()
For details refer to Marty Alchin's Simple plugin framework
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
'''

__all__=['SpecPlugin', 'JSCommand']

for loader, modname, ispkg in  walk_packages(__path__):
    if ispkg: import_module("."+modname, __package__)
