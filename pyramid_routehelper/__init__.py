from pyramid.config import ConfigurationError
import inspect

__all__ = ['includeme', 'add_resource', 'action']

def includeme(config):
    config.add_directive('add_resource', add_resource)

def strip_slashes(name):
    """Remove slashes from the beginning and end of a part/URL."""
    if name.startswith('/'):
        name = name[1:]
    if name.endswith('/'):
        name = name[:-1]
    return name

class action(object):
    """Decorate a method for registration by 
    :func:`~pyramid_routehelper.add_resource`.
    
    Keyword arguments are identical to :class:`~pyramid.view.view_config`, with
    the exception to how the ``name`` argument is used.
    
    ``alt_for``
        Designate a method as another view for the specified action if
        the decorated method is not the desired action name instead of registering
        the method with an action of the same name.
    
    ``format``
        Specify a format for the view that this decorator describes.
    """
    def __init__(self, **kw):
        self.kw = kw

    def __call__(self, wrapped):
        if hasattr(wrapped, '__exposed__'):
            wrapped.__exposed__.append(self.kw)
        else:
            wrapped.__exposed__ = [self.kw]
        return wrapped

# map.resource port
def add_resource(self, handler, member_name, collection_name, **kwargs):
    """ Add some RESTful routes for a resource handler.
    
    This function should never be called directly; instead the
    ``pyramid_routehelper.includeme`` function should be used to include this
    function into an application; the function will thereafter be available
    as a method of the resulting configurator.

    The concept of a web resource maps somewhat directly to 'CRUD' 
    operations. The overlying things to keep in mind is that
    adding a resource handler is about handling creating, viewing, and
    editing that resource.
    
    ``handler`` is a dotted name of (or direct reference to) a
    Python handler class,
    e.g. ``'my.package.handlers.MyHandler'``.
    
    ``member_name`` should be the appropriate singular version of the resource
    given your locale and used with members of the collection.
    
    ``collection_name`` will be used to refer to the resource collection methods
    and should be a plural version of the member_name argument.
    
    All keyword arguments are optional.
    
    ``collection``
        Additional action mappings used to manipulate/view the
        entire set of resources provided by the handler.
        
        Example::
            
            config.add_resource('myproject.handlers:MessageHandler', 'message', 'messages', collection={'rss':'GET'})
            # GET /messages/rss (maps to the rss action)
            # also adds named route "rss_message"
    
    ``member``
        Additional action mappings used to access an individual
        'member' of this handler's resources.
        
        Example::
            
            config.add_resource('myproject.handlers:MessageHandler', 'message', 'messages', member={'mark':'POST'})
            # POST /messages/1/mark (maps to the mark action)
            # also adds named route "mark_message"
    
    ``new``
        Action mappings that involve dealing with a new member in
        the controller resources.
        
        Example::
            
            config.add_resource('myproject.handlers:MessageHandler', 'message', 'messages',  new={'preview':'POST'})
            # POST /messages/new/preview (maps to the preview action)
            # also adds a url named "preview_new_message"
    
    ``path_prefix``
        Prepends the URL path for the Route with the path_prefix
        given. This is most useful for cases where you want to mix
        resources or relations between resources.
    
    ``name_prefix``
        Perpends the route names that are generated with the
        name_prefix given. Combined with the path_prefix option,
        it's easy to generate route names and paths that represent
        resources that are in relations.
        
        Example::
            
            config.add_resource('myproject.handlers:CategoryHandler', 'message', 'messages',
                path_prefix='/category/:category_id', 
                name_prefix="category_")
            # GET /category/7/messages/1
            # has named route "category_message"
            
    ``parent_resource`` 
        A ``dict`` containing information about the parent
        resource, for creating a nested resource. It should contain
        the ``member_name`` and ``collection_name`` of the parent
        resource.

        If ``parent_resource`` is supplied and ``path_prefix``
        isn't, ``path_prefix`` will be generated from
        ``parent_resource`` as
        "<parent collection name>/:<parent member name>_id". 

        If ``parent_resource`` is supplied and ``name_prefix``
        isn't, ``name_prefix`` will be generated from
        ``parent_resource`` as  "<parent member name>_". 

        Example:: 

            >>> from pyramid.url import route_path
            >>> config.add_resource('myproject.handlers:LocationHandler', 'location', 'locations', 
            ...            parent_resource=dict(member_name='region', 
            ...                                 collection_name='regions'))
            >>> # path_prefix is "regions/:region_id" 
            >>> # name prefix is "region_"  
            >>> route_path('region_locations', region_id=13) 
            '/regions/13/locations'
            >>> route_path('region_new_location', region_id=13) 
            '/regions/13/locations/new'
            >>> route_path('region_location', region_id=13, id=60) 
            '/regions/13/locations/60'
            >>> route_path('region_edit_location', region_id=13, id=60) 
            '/regions/13/locations/60/edit'

        Overriding generated ``path_prefix``::

            >>> config.add_resource('myproject.handlers:LocationHandler', 'location', 'locations', 
            ...            parent_resource=dict(member_name='region',
            ...                                 collection_name='regions'),
            ...            path_prefix='areas/:area_id')
            >>> # name prefix is "region_"
            >>> route_path('region_locations', area_id=51)
            '/areas/51/locations'

        Overriding generated ``name_prefix``::

            >>> config.add_resource('myproject.handlers:LocationHandler', 'location', 'locations', 
            ...            parent_resource=dict(member_name='region',
            ...                                 collection_name='regions'),
            ...            name_prefix='')
            >>> # path_prefix is "regions/:region_id" 
            >>> route_path('locations', region_id=51)
            '/regions/51/locations'
    """
    handler = self.maybe_dotted(handler)
    
    action_kwargs = {}
    for name,meth in inspect.getmembers(handler, inspect.ismethod):
        if hasattr(meth, '__exposed__'):
            for settings in meth.__exposed__:
                config_settings = settings.copy()
                action_name = config_settings.pop('alt_for', name)

                # If format is not set, use the route that doesn't specify a format
                if 'format' not in config_settings:
                    if 'default' in action_kwargs.get(action_name,{}):
                        raise ConfigurationError("Two methods have been decorated without specifying a format.")
                    else:
                        action_kwargs.setdefault(action_name, {})['default'] = config_settings
                # Otherwise, append to the list of view config settings for formatted views
                else:
                    config_settings['attr'] = name
                    action_kwargs.setdefault(action_name, {}).setdefault('formatted',[]).append(config_settings)
                
    collection = kwargs.pop('collection', {})
    member = kwargs.pop('member', {})
    new = kwargs.pop('new', {})
    path_prefix = kwargs.pop('path_prefix', None)
    name_prefix = kwargs.pop('name_prefix', None)
    parent_resource = kwargs.pop('parent_resource', None)
    
    if parent_resource is not None:
        if path_prefix is None:
            path_prefix = '%s/:%s_id' % (parent_resource['collection_name'], parent_resource['member_name'])
        if name_prefix is None:
            name_prefix = '%s_' % parent_resource['member_name']
    else:
        if path_prefix is None: path_prefix = ''
        if name_prefix is None: name_prefix = ''
    
    member['edit'] = 'GET'
    new['new'] = 'GET'
    
    def swap(dct, newdct):
        map(lambda (key,value): newdct.setdefault(value.upper(), []).append(key), dct.items())
        return newdct
    
    collection_methods = swap(collection, {})
    member_methods = swap(member, {})
    new_methods = swap(new, {})
    
    collection_methods.setdefault('POST', []).insert(0, 'create')
    member_methods.setdefault('PUT', []).insert(0, 'update')
    member_methods.setdefault('DELETE', []).insert(0, 'delete')
    
    # Continue porting code
    controller = strip_slashes(collection_name)
    path_prefix = strip_slashes(path_prefix)
    path_prefix = '/' + path_prefix
    if path_prefix and path_prefix != '/':
        path = path_prefix + '/' + controller
    else:
        path = '/' + controller
    collection_path = path
    new_path = path + '/new'
    member_path = path + '/:id'

    def add_route_and_view(self, action, route_name, path, request_method='any'):
        if request_method != 'any':
            request_method = request_method.upper()
        else:
            request_method = None
        
        self.add_route(route_name, path, **kwargs)
        self.add_view(view=handler, attr=action, route_name=route_name, request_method=request_method, **action_kwargs.get(action, {}).get('default', {}))
        
        for format_kwargs in action_kwargs.get(action, {}).get('formatted', []):
            format = format_kwargs.pop('format')
            self.add_route("%s_formatted_%s" % (format, route_name),
                           "%s.%s" % (path, format), **kwargs)
            self.add_view(view=handler, attr=format_kwargs.pop('attr'), request_method=request_method,
                          route_name = "%s_formatted_%s" % (format, route_name), **format_kwargs)
    
    for method, lst in collection_methods.iteritems():
        primary = (method != 'GET' and lst.pop(0)) or None
        for action in lst:
            add_route_and_view(self, action, "%s%s_%s" % (name_prefix, action, collection_name), "%s/%s" % (collection_path,action))
        
        if primary:
            add_route_and_view(self, primary, name_prefix + collection_name, collection_path, method)
    
    # Add route and view for collection
    add_route_and_view(self, 'index', name_prefix + collection_name, collection_path, 'GET')
    
    for method, lst in new_methods.iteritems():
        for action in lst:
            path = (action == 'new' and new_path) or "%s/%s" % (new_path, action)
            name = "new_" + member_name
            if action != 'new':
                name = action + "_" + name
            formatted_path = (action == 'new' and new_path + '.:format') or "%s/%s.:format" % (new_path, action)
            add_route_and_view(self, action, name_prefix + name, path, method)
    
    for method, lst in member_methods.iteritems():
        if method not in ['POST', 'GET', 'any']:
            primary = lst.pop(0)
        else:
            primary = None
        for action in lst:
            add_route_and_view(self, action, '%s%s_%s' % (name_prefix, action, member_name), '%s/%s' % (member_path, action))
        
        if primary:
            add_route_and_view(self, primary, name_prefix + member_name, member_path, method)
    
    add_route_and_view(self, 'show', name_prefix + member_name, member_path, method)

# Submapper support


# Sub_domain option


# Converters??