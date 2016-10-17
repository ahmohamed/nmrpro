class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)

class JSCommand:
    __metaclass__ = PluginMount
    
    @staticmethod
    def shorten(name, dic):
        name = name.strip('_')
        if not dic.has_key(name[0:1]):
            return name[0:1]
        elif not dic.has_key(name[0:2]):
            return name[0:2]
        else:
            i=0
            while dic.has_key(name[0:2]+repr(i)):
                i = i+1
            return name[0:2]+repr(i)
    
    @classmethod
    def parse_plugin_input(cls, js_menu, funs, com):
        shortened_name = cls.shorten(com.fun.__name__, funs)
        funs[shortened_name] = com.fun
        com.fun = shortened_name
        
        js_menu.append({k: com.__dict__.get(k, None) for k in ('menu_path', 'fun', 'nd', 'args')})
    
    @classmethod
    def compile_menu(cls):
        js_menu = []
        plugin_funcs = {}
        
        for i in cls.plugins:
            cls.parse_plugin_input(js_menu, plugin_funcs, i)
        
        cls.menu = js_menu
        cls.fun = plugin_funcs
    
    @classmethod
    def get_menu(cls):
        if not hasattr(cls, 'menu'):
            cls.compile_menu()
        return cls.menu
    
    @classmethod
    def get_functions(cls):
        if not hasattr(cls, 'fun'):
            cls.compile_menu()
        return cls.fun
    