from pkgutil import walk_packages
from importlib import import_module
from PluginMount import JSCommand
'''
Recursively import all sub-packages in plugins.
Since all plugins are subclasses of JSCommand,
importing is enough to retrieve them via JSCommand.get_plugins()
For details refer to Marty Alchin's Simple plugin framework
http://martyalchin.com/2008/jan/10/simple-plugin-framework/
'''

__all__=['JSCommand']

for loader, modname, ispkg in  walk_packages(__path__):
    if ispkg: import_module("."+modname, __package__)
