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
        self.config.begin()
    
    def tearDown(self):
        self.config.end()
        del self.config
    
    def test_basic_resources(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages')
        
        assert route_path('messages', testing.DummyRequest()) == '/messages'
        assert route_path('formatted_messages', testing.DummyRequest(), format='html') == '/messages.html'
        assert route_path('new_message', testing.DummyRequest()) == '/messages/new'
        assert route_path('formatted_new_message', testing.DummyRequest(), format='html') == '/messages/new.html'
        
        assert route_path('formatted_message', testing.DummyRequest(), id=1, format='html') == '/messages/1.html'
        assert route_path('message', testing.DummyRequest(), id=1) == '/messages/1'
        assert route_path('formatted_edit_message', testing.DummyRequest(), id=1, format='html') == '/messages/1/edit.html'
        assert route_path('edit_message', testing.DummyRequest(), id=1) == '/messages/1/edit'
    
    def test_resources_with_path_prefix(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', path_prefix='/category/:category_id')
        
        assert route_path('messages', testing.DummyRequest(), category_id=2) == '/category/2/messages'
        assert route_path('formatted_messages', testing.DummyRequest(), format='html', category_id=2) == '/category/2/messages.html'
        assert route_path('new_message', testing.DummyRequest(), category_id=2) == '/category/2/messages/new'
        assert route_path('formatted_new_message', testing.DummyRequest(), format='html', category_id=2) == '/category/2/messages/new.html'
        
        assert route_path('formatted_message', testing.DummyRequest(), id=1, format='html', category_id=2) == '/category/2/messages/1.html'
        assert route_path('message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1'
        assert route_path('formatted_edit_message', testing.DummyRequest(), id=1, format='html', category_id=2) == '/category/2/messages/1/edit.html'
        assert route_path('edit_message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1/edit'
    
    def test_resources_with_path_prefix_with_trailing_slash(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', path_prefix='/category/:category_id/')
        
        assert route_path('messages', testing.DummyRequest(), category_id=2) == '/category/2/messages'
        assert route_path('formatted_messages', testing.DummyRequest(), format='html', category_id=2) == '/category/2/messages.html'
        assert route_path('new_message', testing.DummyRequest(), category_id=2) == '/category/2/messages/new'
        assert route_path('formatted_new_message', testing.DummyRequest(), format='html', category_id=2) == '/category/2/messages/new.html'
        
        assert route_path('formatted_message', testing.DummyRequest(), id=1, format='html', category_id=2) == '/category/2/messages/1.html'
        assert route_path('message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1'
        assert route_path('formatted_edit_message', testing.DummyRequest(), id=1, format='html', category_id=2) == '/category/2/messages/1/edit.html'
        assert route_path('edit_message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1/edit'
    
    def test_resources_with_collection_action(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', collection=dict(sorted='GET'))
        
        assert route_path('sorted_messages', testing.DummyRequest()) == '/messages/sorted'
    
    def test_resources_with_member_action(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', member=dict(comment='GET'))
        
        assert route_path('comment_message', testing.DummyRequest(), id=1) == '/messages/1/comment'
    
    def test_resources_with_new_action(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', new=dict(preview='GET'))
        
        assert route_path('preview_new_message', testing.DummyRequest(), id=1) == '/messages/new/preview'
    
    def test_resources_with_name_prefix(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', name_prefix="special_")
        
        assert route_path('special_message', testing.DummyRequest(), id=1) == '/messages/1'
    
    def test_resources_with_parent_resource(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler',
                                 'message', 'messages',
                                 parent_resource = dict(member_name='category', collection_name='categories'))
        
        assert route_path('category_messages', testing.DummyRequest(), category_id=2) == '/categories/2/messages'
        assert route_path('category_message', testing.DummyRequest(), category_id=2, id=1) == '/categories/2/messages/1'
    
    def test_resources_with_parent_resource_override_path_prefix(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler',
                                 'message', 'messages',
                                 parent_resource = dict(member_name='category', collection_name='categories'),
                                 path_prefix = 'folders/:folder_id')
        
        assert route_path('category_messages', testing.DummyRequest(), folder_id=2) == '/folders/2/messages'
        assert route_path('category_message', testing.DummyRequest(), folder_id=2, id=1) == '/folders/2/messages/1'
    
    def test_resources_with_parent_resource_override_name_prefix(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler',
                                 'message', 'messages',
                                 parent_resource = dict(member_name='category', collection_name='categories'),
                                 name_prefix = '')
        
        assert route_path('messages', testing.DummyRequest(), category_id=2) == '/categories/2/messages'
        assert route_path('message', testing.DummyRequest(), category_id=2, id=1) == '/categories/2/messages/1'

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
