import unittest
from pyramid import testing
from pyramid.config import Configurator
from pyramid_routehelper import includeme, add_resource, action, ConfigurationError
from pyramid.url import route_path


class TestResourceGeneration_add_resource(unittest.TestCase):
    def _create_config(self, autocommit=True):
        config = Configurator(autocommit=autocommit)
        includeme(config)
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
        assert route_path('json_formatted_messages', testing.DummyRequest()) == '/messages.json'
        assert route_path('new_message', testing.DummyRequest()) == '/messages/new'
        assert route_path('json_formatted_new_message', testing.DummyRequest()) == '/messages/new.json'
        
        assert route_path('json_formatted_message', testing.DummyRequest(), id=1) == '/messages/1.json'
        assert route_path('message', testing.DummyRequest(), id=1) == '/messages/1'
        assert route_path('json_formatted_edit_message', testing.DummyRequest(), id=1) == '/messages/1/edit.json'
        assert route_path('edit_message', testing.DummyRequest(), id=1) == '/messages/1/edit'
    
    def test_resources_with_path_prefix(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', path_prefix='/category/:category_id')
        
        assert route_path('messages', testing.DummyRequest(), category_id=2) == '/category/2/messages'
        assert route_path('json_formatted_messages', testing.DummyRequest(), category_id=2) == '/category/2/messages.json'
        assert route_path('new_message', testing.DummyRequest(), category_id=2) == '/category/2/messages/new'
        assert route_path('json_formatted_new_message', testing.DummyRequest(), category_id=2) == '/category/2/messages/new.json'
        
        assert route_path('json_formatted_message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1.json'
        assert route_path('message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1'
        assert route_path('json_formatted_edit_message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1/edit.json'
        assert route_path('edit_message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1/edit'
    
    def test_resources_with_path_prefix_with_trailing_slash(self):
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages', path_prefix='/category/:category_id/')
        
        assert route_path('messages', testing.DummyRequest(), category_id=2) == '/category/2/messages'
        assert route_path('json_formatted_messages', testing.DummyRequest(), category_id=2) == '/category/2/messages.json'
        assert route_path('new_message', testing.DummyRequest(), category_id=2) == '/category/2/messages/new'
        assert route_path('json_formatted_new_message', testing.DummyRequest(), category_id=2) == '/category/2/messages/new.json'
        
        assert route_path('json_formatted_message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1.json'
        assert route_path('message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1'
        assert route_path('json_formatted_edit_message', testing.DummyRequest(), id=1, category_id=2) == '/category/2/messages/1/edit.json'
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
    
    def test_resources_with_double_default_views(self):
        class MessedUpHandler(object):
            @action(renderer='json')
            @action(renderer='template.mak')
            def index(self):
                return {}
        
        try:
            self.config.add_resource(MessedUpHandler, 'message', 'messages')
        except ConfigurationError, e:
            assert str(e) == "Two methods have been decorated without specifying a format."

class TestResourceRecognition(unittest.TestCase):
    def _create_config(self, autocommit=True):
        config = Configurator(autocommit=autocommit)
        includeme(config)
        return config
    
    def setUp(self):
        self.config = self._create_config()
        self.config.add_resource('pyramid_routehelper.tests:DummyCrudHandler', 'message', 'messages')
        self.config.begin()
        
        self.wsgi_app = self.config.make_wsgi_app()

        self.collection_path = '/messages'
        self.collection_name = 'messages'
        self.member_path     = '/messages/:id'
        self.member_name     = 'message'
    
    def tearDown(self):
        self.config.end()
        del self.config
    
    def _get(self, path):
        return self._makeRequest(path, 'GET')
    
    def _post(self, path):
        return self._makeRequest(path, 'POST')
    
    def _put(self, path):
        return self._makeRequest(path, 'PUT')
    
    def _delete(self, path):
        return self._makeRequest(path, 'DELETE')
    
    def _makeRequest(self, path, request_method = 'GET'):
        wsgi_environ = dict(
            PATH_INFO = path,
            REQUEST_METHOD = request_method
        )
        resp_body = self.wsgi_app(wsgi_environ, lambda status,headers: None)[0]
        return resp_body
    
    def test_get_collection(self):
        result = self._get('/messages')
        assert result == '"index"'
    
    def test_get_formatted_collection(self):
        result = self._get('/messages.json')
        assert result == '{"format": "json"}'
    
    def test_post_collection(self):
        result = self._post('/messages')
        assert result == '"create"'
    
    def test_get_member(self):
        result = self._get('/messages/1')
        assert result == '"show"'
    
    def test_put_member(self):
        result = self._put('/messages/1')
        assert result == '"update"'
    
    def test_delete_member(self):
        result = self._delete('/messages/1')
        assert result == '"delete"'
    
    def test_new_member(self):
        result = self._get('/messages/new')
        assert result == '"new"'
    
    def test_edit_member(self):
        result = self._get('/messages/1/edit')
        assert result == '"edit"'

class Test_includeme(unittest.TestCase):
    def test_includme(self):
        config = Configurator(autocommit=True)
        includeme(config)
        assert config.add_resource.im_func.__docobj__ is add_resource

class DummyCrudHandler(object):
    def __init__(self, request):
        self.request = request
    
    @action(renderer='json')
    def index(self):
        return "index"
    
    @action(alt_for='index', renderer='xml', xhr=True, format='xml')
    @action(alt_for='index', renderer='json', format='json')
    def api_index(self):
        return {'format':'json'}
    
    @action(renderer='json')
    def create(self):
        return "create"
    
    @action(renderer='json', format='json')
    @action(renderer='json')
    def show(self):
        return "show"
    
    @action(renderer='json')
    def update(self):
        return "update"
    
    @action(renderer='json')
    def delete(self):
        return "delete"
    
    @action(renderer='json', format='json')
    @action(renderer='json')
    def new(self):
        return "new"
    
    @action(renderer='json', format='json')
    @action(renderer='json')
    def edit(self):
        return "edit"
    
    @action(renderer='json')
    def sorted(self):
        return "sorted"