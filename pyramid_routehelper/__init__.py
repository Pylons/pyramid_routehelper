from pyramid_handlers import add_handler
from pyramid.config import ConfigurationError

__all__ = ['includeme', 'add_resource']

def includeme(config):
    if getattr(config, 'add_handler', None):
        config.add_directive('add_resource', add_resource)
    else:
        raise ConfigurationError("add_handler needs to be added before add_resource can be used")
    

def strip_slashes(name):
    """Remove slashes from the beginning and end of a part/URL."""
    if name.startswith('/'):
        name = name[1:]
    if name.endswith('/'):
        name = name[:-1]
    return name

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

            >>> from pyramid.url import resource_url
            >>> config.add_resource('myproject.handlers:LocationHandler', 'location', 'locations', 
            ...            parent_resource=dict(member_name='region', 
            ...                                 collection_name='regions'))
            >>> # path_prefix is "regions/:region_id" 
            >>> # name prefix is "region_"  
            >>> resource_url('region_locations', region_id=13) 
            '/regions/13/locations'
            >>> resource_url('region_new_location', region_id=13) 
            '/regions/13/locations/new'
            >>> resource_url('region_location', region_id=13, id=60) 
            '/regions/13/locations/60'
            >>> resource_url('region_edit_location', region_id=13, id=60) 
            '/regions/13/locations/60/edit'

        Overriding generated ``path_prefix``::

            >>> config.add_resource('myproject.handlers:LocationHandler', 'location', 'locations', 
            ...            parent_resource=dict(member_name='region',
            ...                                 collection_name='regions'),
            ...            path_prefix='areas/:area_id')
            >>> # name prefix is "region_"
            >>> url_for('region_locations', area_id=51)
            '/areas/51/locations'

        Overriding generated ``name_prefix``::

            >>> m = Mapper()
            >>> m.resource('location', 'locations',
            ...            parent_resource=dict(member_name='region',
            ...                                 collection_name='regions'),
            ...            name_prefix='')
            >>> # path_prefix is "regions/:region_id" 
            >>> url_for('locations', region_id=51)
            '/regions/51/locations'
    """
    
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
    
    options = dict(
        handler = handler
    )
    
    def requirements_for(meth):
        opts = options.copy()
        if method != 'any':
            opts['request_method'] = meth.upper()
        return opts
    
    for method, lst in collection_methods.iteritems():
        primary = (method != 'GET' and lst.pop(0)) or None
        route_options = requirements_for(method)
        for action in lst:
            route_options['action'] = action
            route_name = "%s%s_%s" % (name_prefix, action, collection_name)

            # Connect paths
            self.add_handler("formatted_" + route_name,
                             "%s/%s.:format" % (collection_path, action),
                             **route_options)
            self.add_handler(route_name,
                             "%s/%s" % (collection_path, action),
                             **route_options)
        
        if primary:
            route_options['action'] = primary
            self.add_handler("formatted_%s" % collection_name, "%s.:format" % collection_path, **route_options)
            self.add_handler(collection_name, collection_path, **route_options)
        
    self.add_handler("formatted_" + name_prefix + collection_name,
                     collection_path + ".:format",
                     handler,
                     action='index',
                     request_method='GET')
    self.add_handler(name_prefix + collection_name,
                     collection_path,
                     handler,
                     action='index',
                     request_method='GET')
    
    for method, lst in new_methods.iteritems():
        route_options = requirements_for(method)
        for action in lst:
            path = (action == 'new' and new_path) or "%s/%s" % (new_path, action)
            name = "new_" + member_name
            if action != 'new':
                name = action + "_" + name
            route_options['action'] = action
            formatted_path = (action == 'new' and new_path + '.:format') or "%s/%s.:format" % (new_path, action)
            self.add_handler('formatted_' + name_prefix + name, formatted_path, **route_options)
            self.add_handler(name_prefix + name, path, **route_options)
    
    requirements_regexp = '[^\/]+'
    
    for method, lst in member_methods.iteritems():
        route_options = requirements_for(method)
        if method not in ['POST', 'GET', 'any']:
            primary = lst.pop(0)
        else:
            primary = None
        for action in lst:
            route_options['action'] = action
            self.add_handler('formatted_%s%s_%s' % (name_prefix, action, member_name),
                             '%s/%s.:format' % (member_path, action), **route_options)
            self.add_handler('%s%s_%s' % (name_prefix, action, member_name),
                             '%s/%s' % (member_path, action), **route_options)
        
        if primary:
            route_options['action'] = primary
            self.add_handler("formatted_" + member_name,
                             "%s.:format"  % member_path, **route_options)
            self.add_handler(member_name, member_path, **route_options)
    
    route_options = requirements_for('GET')
    route_options['action'] = 'show'
    self.add_handler('formatted_' + name_prefix + member_name,
                     member_path + ".:format", **route_options)
    self.add_handler(name_prefix + member_name, member_path, **route_options)

# Submapper support


# Sub_domain option


# Converters??