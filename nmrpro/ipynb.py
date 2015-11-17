try:
    _ip = get_ipython()
except:
    _ip = None
if _ip and _ip.__module__.lower().startswith('ipy'):
    #_ip.user_module._specdraw_version = False
    def initialize_specdraw():
        try:
            if _ip.user_module._d3_version:
                print ('d3 already initialized. Version: ', _ip.user_module._d3_version)
                return
        except Exception as e:
            _ip.user_module._d3_version = False
        
        from IPython.display import display, Javascript, HTML
        print ('Initilizing SpecDrawJS ...')
        
        specdraw_css = "files/specdraw.css"
        d3_js = "https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"
        specdraw_js = "files/specdraw.js"
        
        display(HTML('''<link media="all" href="%s" type="text/css"
                        rel="stylesheet"/>''' % (specdraw_css)))
        
        display(HTML('''<div id='specdraw_results'></div>'''))
        
        display(Javascript('''
        require(["%s"], function(d3){
            require(["%s"], function(specdraw) {
                window.d3 = d3
                window.specdraw = specdraw
    
                var kernel = Jupyter.notebook.kernel;
                kernel.execute("_d3_version = '"+ d3.version + "'", {output:function(){}});
                kernel.execute("_specdraw_version = '"+ specdraw.version + "'", {output:function(){}});
                d3.select('div#specdraw_results').text(
                    'Using D3 version: '+ d3.version +
                    ', SpecdrawJS version: '+ specdraw.version
                );
            })
        });
        ''' %(d3_js, specdraw_js) ))

    def plotSpectra(s):
        if not hasattr(_ip.user_module, '_d3_version') or not _ip.user_module._d3_version:
            initialize_specdraw()
            import time
            time.sleep(5)
        
        if s.ndim > 1:
            raise TypeError('Interactive plotting is currently available only to 1D spectra')
            
        import json
        from IPython.display import display, Javascript, HTML
        json_spec = json.dumps({'x':s.uc[0].ppm_scale().tolist(), 'y':s.tolist()})
        
        display(Javascript(
        "var pre_data = JSON.parse('"+json_spec+"');"+
        '''
        var data = pre_data.x.map(function(d,i){ return {x:d, y:pre_data.y[i]}; });
        var spec_data = {data_type:'spectrum', nd:1, x_label:'13C',data:data};
        var spec_app = specdraw.App()
            .width(960)
            .height(500)
            .config(2)
            .appendSlide(spec_data);

        d3.select(element[0]).call(spec_app);
        '''))
    
    def jsTester(panel):
        from nmrpro.plugins import JSCommand
        from IPython.display import display, Javascript, HTML
        import json
        
        if isinstance(panel, JSCommand):
            panel = panel.args
        
        panel = json.dumps(panel)
        display(Javascript('''
        <script>'''
        +"var panel = JSON.parse('"+panel+"');"+
        '''
        var inp = specdraw.hooks.input;
        d3.select(element).append(inp.div(panel));
        </script>
        '''))