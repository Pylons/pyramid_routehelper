import unittest
from pyramid import testing
from pyramid_handlers import includeme as handlers_includeme, action
from pyramid.config import Configurator
from pyramid_routehelper import includeme as routehelper_includeme, add_resource
from pyramid.url import route_path


class Test_add_resource(unittest.TestCase):
    def _create_config(self, autocommit=True):
        config = Configurator(autocommit=autocommit)
        handlers_includeme(config)
        routehelper_includeme(config)
        return config
    
    def setUp(self):
        self.config = self._create_config()
    
    def tearDown(self):
        del self.config
    
    def test_basic_resources(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages')
    
    def test_resources_with_path_prefix(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', path_prefix='/category/:category_id')
    
    def test_resources_with_path_prefix_with_trailing_slash(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', path_prefix='/category/:category_id/')
    
    def test_resources_with_collection_action(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', collection=dict(sorted='GET'))
    
    def test_resources_with_member_action(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', member=dict(comment='GET'))
    
    def test_resources_with_new_action(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', new=dict(preview='GET'))
    
    def test_resources_with_name_prefix(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', name_prefix="special_")
    
    def test_resources_with_parent_resource(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler',
                                 'message', 'messages',
                                 parent_resource = dict(member_name='category', collection_name='categories'))

class Test_includeme(unittest.TestCase):
    def test_includme(self):
        config = Configurator(autocommit=True)
        handlers_includeme(config)
        routehelper_includeme(config)
        assert config.add_resource.im_func.__docobj__ is add_resource

class DummyCrudHandler(object):
    def __init__(self, request):
        self.request = request
    
    @action(renderer='json')
    def index(self):
        return "index"
    
    @action(renderer='json')
    def create(self):
        return "create"
    
    @action(renderer='json')
    def read(self):
        return "read"
    
    @action(renderer='json')
    def update(self):
        return "update"
    
    @action(renderer='json')
    def delete(self):
        return "delete"
    
    @action(renderer='json')
    def new(self):
        return "new"
    
    @action(renderer='json')
    def edit(self):
        return "edit"
