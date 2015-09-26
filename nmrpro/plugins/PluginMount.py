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
            
            
class SpecPlugin:
    """
    Mount point for plugins which refer to actions that can be performed.

    Plugins implementing this reference should provide the following attributes:

    ========  ========================================================
    title     The text to be displayed, describing the action

    url       The URL to the view where the action will be carried out

    selected  Boolean indicating whether the action is the one
              currently being performed
    ========  ========================================================
    """
    __metaclass__ = PluginMount

    @classmethod
    def get_plugin_interfaces(cls):
        return [p.interface for p in cls.plugins]
    
    @staticmethod
    def shorten(name, dic):
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
    def parse_plugin_input(cls, out, funs, dic):
        for k in dic:
            item = dic[k]
            #print(item.keys())
            if 'fun' in item.keys():
                if not out.get(k):
                    out[k] = {}
                shortened_name = cls.shorten(item['fun'].__name__, funs)
                funs[shortened_name]=item['fun']
                out[k] = {"fun": shortened_name, "args":item.get('args', None), "title": item.get("title", None)}
            else:
                if not out.get(k):
                    out[k] = {}
                cls.parse_plugin_input(out[k], funs, item)
        return out, funs
    
    @classmethod
    def compile_menu(cls):
        js_menu = {}
        plugin_funcs = {}
        
        for i in cls.get_plugin_interfaces():
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

class JSCommand:
    __metaclass__ = PluginMount
    
    @staticmethod
    def shorten(name, dic):
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
    