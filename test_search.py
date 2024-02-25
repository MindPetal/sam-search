"""
    Tests for search.py 
"""
import sys
import pytest
from pytest_mock import mocker
import urllib3
import client
import search

@pytest.fixture
def api_client():
    api_config = search.client.Configuration()
    api_config.access_token = 'abcd'
    api_config.host = 'https://www.example.com'

    return client.ApiClient(api_config)

def test_load_config(mocker):
    mocker.patch('builtins.open', mocker.mock_open(read_data='foo'))
    assert 'foo' == search.load_config()
    
def test_search(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfRoleDto()
    role_dto = swagger_client.RoleDto()
    role_dto.name = 'Robot'
    role_dto.id = 1566107
    api_response.value = [role_dto]

    mocker.patch('search.client.SamApi.search', 
                  return_value=api_response)
    assert api_response.to_dict()['value'] == search.search(api_client, 
                                                            api_key, 
                                                            from_date,
                                                            to_date, 
                                                            limit, 
                                                            naics)

def test_format_date():
    pass

def test_format_results():
    pass

def test_process_search():
    pass

def test_teams_post():
    pass

def test_get_roles(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfRoleDto()
    role_dto = swagger_client.RoleDto()
    role_dto.name = 'Robot'
    role_dto.id = 1566107
    api_response.value = [role_dto]

    mocker.patch('uipath_config.swagger_client.RolesApi.roles_get', 
                  return_value=api_response)
    assert api_response.to_dict() == uipath_config.get_roles(api_client)

def test_compare_role_match():
    role_dto = swagger_client.RoleDto()
    role_dto.name = 'Robot'
    role_dto.id = 1566107
    orch_roles = [{'name': 'Robot', 'id': 1566107}]

    assert role_dto == uipath_config.compare_role('Robot', orch_roles)

def test_compare_role_no_match():
    role_dto = swagger_client.RoleDto()
    role_dto.name = 'Robot'
    role_dto.id = 1566107
    orch_roles = [{'name': 'Foo', 'id': 1566108}]

    assert role_dto is not uipath_config.compare_role('Robot', orch_roles)

def test_create_role(mocker):
    role = {'role': 'Tenant-Role-Test',
            'type': 'Tenant',
            'perms': [{'perm': 'Roles.View',
                       'scope': 'Global'}]}
    role_dto = swagger_client.RoleDto()
    role_dto.name = role['role']
    role_dto.display_name = role['role']
    role_dto.type = role['type']
    role_dto.is_static = False
    role_dto.is_editable = True

    perm_dto = swagger_client.PermissionDto()
    perm_dto.name = role['perms'][0]['perm']
    perm_dto.is_granted = True
    perm_dto.role_id = 0
    perm_dto.scope = role['perms'][0]['scope']
    role_dto.permissions = [perm_dto]

    mock_roles_post = mocker.patch('uipath_config.swagger_client.RolesApi.roles_post')
    uipath_config.create_role(api_client, role)
    mock_roles_post.assert_called_once_with(body=role_dto)

def test_process_create_roles_match(mocker):
    git_roles = [{'role': 'Tenant-Role-Test',
                  'type': 'Tenant',
                  'perms': [{'perm': 'Roles.View',
                             'scope': 'Global'}]}]
    orch_roles = {'value': [{'name': 'Tenant-Role-Test', 
                             'display_name': 'Tenant-Role-Test', 
                             'type': 'Tenant', 
                             'groups': None, 
                             'is_static': False, 
                             'is_editable': True, 
                             'permissions': None, 
                             'id': 6799364}]}

    mocker.patch('uipath_config.get_roles', return_value=orch_roles)
    mock_create_role = mocker.patch('uipath_config.create_role')
    uipath_config.process_create_roles(api_client, git_roles)
    mock_create_role.assert_not_called()

def test_process_create_roles_no_match(mocker):
    git_roles = [{'role': 'Tenant-Role-Test',
                  'type': 'Tenant',
                  'perms': [{'perm': 'Roles.View',
                             'scope': 'Global'}]}]
    orch_roles = {'value': [{'name': 'Blah', 
                             'display_name': 'Blah', 
                             'type': 'Tenant', 
                             'groups': None, 
                             'is_static': False, 
                             'is_editable': True, 
                             'permissions': None, 
                             'id': 6799364}]}

    mocker.patch('uipath_config.get_roles', return_value=orch_roles)
    mock_create_role = mocker.patch('uipath_config.create_role')
    uipath_config.process_create_roles(api_client, git_roles)
    mock_create_role.assert_called_once_with(api_client, git_roles[0])

def test_get_folders(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-folder')
    folder_dto.id = 1566107
    api_response.value = [folder_dto]

    mocker.patch('uipath_config.swagger_client.FoldersApi.folders_get', 
                  return_value=api_response)
    assert api_response.to_dict() == uipath_config.get_folders(api_client)

def test_compare_folder_match():
    folder_dto = swagger_client.FolderDto(display_name='test-folder')
    folder_dto.id = 1566107
    folder_dto.key = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    folder_dto.parent_id = 1111
    folder_dto.parent_key = 'abcd'
    orch_folders = [{'display_name': 'test-folder',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 1111,
                     'parent_key': 'abcd'}]

    assert folder_dto == uipath_config.compare_folder('test-folder', orch_folders)

def test_compare_folder_no_match():
    folder_dto = swagger_client.FolderDto(display_name='test-folder')
    folder_dto.id = 1566107
    folder_dto.key = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    folder_dto.parent_id = 1111
    folder_dto.parent_key = 'abcd'
    orch_folders = [{'display_name': 'foo',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 1111,
                     'parent_key': 'abcd'}]

    assert folder_dto is not uipath_config.compare_folder('test-folder', orch_folders)

def test_create_parent_folder(mocker):
    folder_dto = swagger_client.FolderDto(display_name='test-folder')
    folder_dto.key = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    folder_dto.fully_qualified_name = 'test-folder'
    folder_dto.provision_type = 'Automatic'
    folder_dto.permission_model = 'FineGrained'
    folder_dto.parent_id = None
    folder_dto.parent_key = None
    folder_dto.feed_type = 'Processes'

    mock_folders_post = mocker.patch('uipath_config.swagger_client.FoldersApi.folders_post')
    uipath_config.create_folder(api_client, 'test-folder')
    mock_folders_post.assert_called_once_with(body=folder_dto)

def test_create_subfolder(mocker):
    folder_dto = swagger_client.FolderDto(display_name='test-folder')
    folder_dto.key = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    folder_dto.fully_qualified_name = 'test-folder'
    folder_dto.provision_type = 'Automatic'
    folder_dto.permission_model = 'FineGrained'
    folder_dto.parent_id = 1234
    folder_dto.parent_key = 'dddd'
    folder_dto.feed_type = 'Processes'

    mock_folders_post = mocker.patch('uipath_config.swagger_client.FoldersApi.folders_post')
    uipath_config.create_folder(api_client, 'test-folder', 
                                parent_id=1234, parent_key='dddd')
    mock_folders_post.assert_called_once_with(body=folder_dto)

def test_process_create_folder_match(mocker):
    orch_folders = [{'display_name': 'test-folder',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': None,
                     'parent_key': None}]

    mock_create_folder = mocker.patch('uipath_config.create_folder')
    uipath_config.process_create_folder(api_client, 'test-folder', orch_folders)
    mock_create_folder.assert_not_called()

def test_process_create_folder_no_match(mocker):
    orch_folders = [{'display_name': 'test-folder',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': None,
                     'parent_key': None}]

    mock_create_folder = mocker.patch('uipath_config.create_folder')
    uipath_config.process_create_folder(api_client, 'foo', orch_folders)
    mock_create_folder.assert_called_once_with(api_client, 'foo')

def test_process_create_subfolders_match(mocker):
    git_subfolders = [{'subfolder': 'test-sub-1',
                       'sub_subfolders': [{'sub_subfolder': 'test-sub-sub-1'}]}]
    parent_dto = swagger_client.FolderDto(display_name='test-folder')
    parent_dto.key = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    parent_dto.id = 1111
    orch_folders = [{'display_name': 'test-sub-1',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 1111,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
                    {'display_name': 'test-sub-sub-1',
                     'id': 1566108,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 1111,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}]

    mock_create_subfolder = mocker.patch('uipath_config.create_folder')
    uipath_config.process_create_subfolders(api_client, git_subfolders, 
                                            parent_dto, orch_folders)
    mock_create_subfolder.assert_not_called()

def test_process_create_subfolders_no_subfolder_match(mocker):
    git_subfolders = [{'subfolder': 'test-sub-1'}]
    parent_dto = swagger_client.FolderDto(display_name='test-folder')
    parent_dto.key = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    parent_dto.id = 1111
    orch_folders = []

    mock_create_subfolder = mocker.patch('uipath_config.create_folder')
    uipath_config.process_create_subfolders(api_client, git_subfolders, 
                                            parent_dto, orch_folders)
    mock_create_subfolder.assert_called_once_with(api_client, 'test-sub-1', 
                                                  parent_dto.id, parent_dto.key)

def test_process_create_subfolders_no_sub_subfolder_match(mocker):
    git_subfolders = [{'subfolder': 'test-sub-1',
                       'sub_subfolders': [{'sub_subfolder': 'foo'}]}]
    parent_dto = swagger_client.FolderDto(display_name='test-folder')
    parent_dto.key = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    parent_dto.id = 1111
    orch_folders = [{'display_name': 'test-sub-1',
                     'id': 2222,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 1111,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'},
                    {'display_name': 'test-sub-sub-1',
                     'id': 1566108,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 2222,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}]

    mock_create_subfolder = mocker.patch('uipath_config.create_folder')
    uipath_config.process_create_subfolders(api_client, git_subfolders, 
                                            parent_dto, orch_folders)
    mock_create_subfolder.assert_called_once_with(api_client, 'foo', 
                                                  orch_folders[0]['id'], 
                                                  orch_folders[0]['key'])

def test_get_assets(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'desc'
    api_response.value = [asset_dto]

    mocker.patch('uipath_config.swagger_client.AssetsApi.assets_get_filtered', 
                  return_value=api_response)
    assert api_response.to_dict() == uipath_config.get_assets(api_client, 1234)

def test_compare_asset_match():
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'desc'
    orch_assets = [{'name': 'test-asset', 'value_scope': 'Global', 
                    'value': 'test-value', 'description': 'desc',
                    'id': 1111}]

    assert asset_dto == uipath_config.compare_asset('test-asset', orch_assets)

def test_compare_asset_no_match():
    asset_dto = swagger_client.AssetDto(name='foo', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'desc'
    orch_assets = [{'name': 'test-asset', 'value_scope': 'Global', 
                    'value': 'test-value', 'description': 'desc',
                    'id': 1111}]

    assert asset_dto is not uipath_config.compare_asset('test-asset', orch_assets)

def test_compare_asset_to_delete_match():
    git_assets = [{'asset': 'test-asset', 'value': 'test', 'desc': 'test'}]
    assert uipath_config.compare_asset_to_delete('test-asset', git_assets)

def test_compare_asset_to_delete_no_match():
    git_assets = [{'asset': 'test-asset', 'value': 'test', 'desc': 'test'}]
    assert not uipath_config.compare_asset_to_delete('foo', git_assets)

def test_create_asset_text(mocker):
    git_asset = {'asset': 'test-asset', 'value': 'text', 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = 'text'
    asset_dto.value_type = 'Text'
    asset_dto.string_value = 'text'
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1

    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_post')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset)
    mock_assets_post.assert_called_once_with(body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)

def test_create_asset_bool(mocker):
    git_asset = {'asset': 'test-asset', 'type': 'Bool', 
                 'value': False, 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = 'False'
    asset_dto.value_type = 'Bool'
    asset_dto.bool_value = False
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1

    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_post')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset)
    mock_assets_post.assert_called_once_with(body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)

def test_create_asset_int(mocker):
    git_asset = {'asset': 'test-asset', 'type': 'Integer', 
                 'value': 6789, 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = '6789'
    asset_dto.value_type = 'Integer'
    asset_dto.int_value = 6789
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1

    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_post')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset)
    mock_assets_post.assert_called_once_with(body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)

def test_create_asset_cred(mocker):
    git_asset = {'asset': 'test-asset', 'type': 'Credential', 
                 'value': 'username: ', 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = 'username: '
    asset_dto.value_type = 'Credential'
    asset_dto.credential_username = 'username: '
    asset_dto.credential_password = 'placeholder'
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1

    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_post')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset)
    mock_assets_post.assert_called_once_with(body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)
    
def test_update_asset_text(mocker):
    git_asset = {'asset': 'test-asset', 'value': 'text', 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = 'text'
    asset_dto.value_type = 'Text'
    asset_dto.string_value = 'text'
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1
    asset_dto.id = 8888

    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_put_by_id')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset, 8888)
    mock_assets_post.assert_called_once_with(8888, body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)

def test_update_asset_bool(mocker):
    git_asset = {'asset': 'test-asset', 'type': 'Bool', 
                 'value': False, 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = 'False'
    asset_dto.value_type = 'Bool'
    asset_dto.bool_value = False
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1
    asset_dto.id = 8888
    
    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_put_by_id')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset, 8888)
    mock_assets_post.assert_called_once_with(8888, body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)

def test_update_asset_int(mocker):
    git_asset = {'asset': 'test-asset', 'type': 'Integer', 
                 'value': 6789, 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = '6789'
    asset_dto.value_type = 'Integer'
    asset_dto.int_value = 6789
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1
    asset_dto.id = 8888
    
    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_put_by_id')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset, 8888)
    mock_assets_post.assert_called_once_with(8888, body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)

def test_update_asset_cred(mocker):
    git_asset = {'asset': 'test-asset', 'type': 'Credential', 
                 'value': 'username: ', 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.can_be_deleted = True
    asset_dto.value = 'username: '
    asset_dto.value_type = 'Credential'
    asset_dto.credential_username = 'username: '
    asset_dto.credential_password = 'placeholder'
    asset_dto.key_value_list = []
    asset_dto.has_default_value = True
    asset_dto.description = 'test'
    asset_dto.robot_values = []
    asset_dto.user_values = []
    asset_dto.tags = []
    asset_dto.folders_count = 1
    asset_dto.id = 8888
    
    mock_assets_post = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_put_by_id')
    uipath_config.create_or_update_asset(api_client, 1234, git_asset, 8888)
    mock_assets_post.assert_called_once_with(8888, body=asset_dto, 
                                             x_uipath_organization_unit_id=1234)

def test_delete_asset(mocker):
    mock_asset_delete = mocker.patch('uipath_config.swagger_client.AssetsApi.assets_delete_by_id')
    uipath_config.delete_asset(api_client, 1234, 5678)
    mock_asset_delete.assert_called_once_with(key=1234,
                                              x_uipath_organization_unit_id=5678)

def test_git_asset_updated_true():
    git_asset = {'asset': 'test-asset', 'value': 'updated', 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.value = 'text'
    asset_dto.description = 'test'

    assert uipath_config.git_asset_updated(git_asset, asset_dto)

def test_git_asset_updated_false():
    git_asset = {'asset': 'test-asset', 'value': 'text', 'desc': 'test'}
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.value = 'text'
    asset_dto.description = 'test'

    assert not uipath_config.git_asset_updated(git_asset, asset_dto)

def test_process_parent_folder_assets_match_no_update(mocker):
    git_parent_folder = {'name': 'test-parent-folder',
                         'assets': [{'asset': 'test-asset',
                                     'value': 'test-value',
                                     'desc': 'test-desc'}]}
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_or_update_asset')
    uipath_config.process_parent_folder_assets(api_client, git_parent_folder, 
                                               1234)
    mock_call.assert_not_called()

def test_process_parent_folder_assets_match_update(mocker):
    git_asset = {'asset': 'test-asset', 
                 'value': 'test-value-updated',
                 'desc': 'test-desc'}
    git_parent_folder = {'name': 'test-parent-folder', 'assets': [git_asset]}
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_or_update_asset')
    uipath_config.process_parent_folder_assets(api_client, git_parent_folder, 
                                               1234)
    mock_call.assert_called_once_with(api_client, 1234, git_asset, 1111)

def test_process_parent_folder_assets_no_match(mocker):
    git_asset = {'asset': 'test-asset', 
                 'value': 'test-value',
                 'desc': 'test-desc'}
    git_parent_folder = {'name': 'test-parent-folder', 'assets': [git_asset]}
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='foo', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_or_update_asset')
    uipath_config.process_parent_folder_assets(api_client, git_parent_folder, 
                                               1234)
    mock_call.assert_called_once_with(api_client, 1234, git_asset)

def test_process_subfolder_assets_match_no_update(mocker):
    git_subfolders = [{'subfolder': 'test-subfolder',
                       'assets': [{'asset': 'test-asset',
                                   'value': 'test-value',
                                   'desc': 'test-desc'}]}]
    orch_folders = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-subfolder')
    folder_dto.id = 1566107
    orch_folders.value = [folder_dto]

    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_or_update_asset')
    uipath_config.process_subfolder_assets(api_client, git_subfolders, 
                                           orch_folders.to_dict()['value'])                        
    mock_call.assert_not_called()

def test_process_subfolder_assets_match_update(mocker):
    git_asset = {'asset': 'test-asset',
                 'value': 'test-value-updated',
                 'desc': 'test-desc'}
    git_subfolders = [{'subfolder': 'test-subfolder',
                       'assets': [git_asset]}]
    orch_folders = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-subfolder')
    folder_dto.id = 1234
    orch_folders.value = [folder_dto]

    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_or_update_asset')
    uipath_config.process_subfolder_assets(api_client, git_subfolders, 
                                           orch_folders.to_dict()['value'])                        
    mock_call.assert_called_once_with(api_client, 1234, git_asset, 1111)

def test_process_subfolder_assets_no_match(mocker):
    git_asset = {'asset': 'test-asset',
                 'value': 'test-value-updated',
                 'desc': 'test-desc'}
    git_subfolders = [{'subfolder': 'test-subfolder',
                       'assets': [git_asset]}]
    orch_folders = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-subfolder')
    folder_dto.id = 1234
    orch_folders.value = [folder_dto]

    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='foo', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_or_update_asset')
    uipath_config.process_subfolder_assets(api_client, git_subfolders, 
                                           orch_folders.to_dict()['value'])                        
    mock_call.assert_called_once_with(api_client, 1234, git_asset)

def test_process_parent_folder_asset_deletions_match(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    git_asset = {'asset': 'test-asset',
                 'value': 'test-value',
                 'desc': 'test-desc'}
    git_parent_folder = {'name': 'test-parent-folder', 'assets': [git_asset]}

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_asset')
    uipath_config.process_parent_folder_asset_deletions(api_client, git_parent_folder,
                                                        5678)
    mock_call.assert_not_called()

def test_process_parent_folder_asset_deletions_no_match(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='foo', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    git_asset = {'asset': 'test-asset',
                 'value': 'test-value',
                 'desc': 'test-desc'}
    git_parent_folder = {'name': 'test-parent-folder', 'assets': [git_asset]}

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_asset')
    uipath_config.process_parent_folder_asset_deletions(api_client, git_parent_folder,
                                                        5678)
    mock_call.assert_called_once_with(api_client, 1111, 5678)

def test_process_subfolder_asset_deletions_match(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='test-asset', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    git_asset = {'asset': 'test-asset',
                 'value': 'test-value',
                 'desc': 'test-desc'}
    git_subfolders = [{'subfolder': 'test-subfolder', 
                       'assets': [git_asset]}]

    orch_folders = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-subfolder')
    folder_dto.id = 1234
    orch_folders.value = [folder_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_asset')
    uipath_config.process_subfolder_asset_deletions(api_client, git_subfolders,
                                                    orch_folders.to_dict()['value'])
    mock_call.assert_not_called()

def test_process_subfolder_asset_deletions_no_match(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfAssetDto()
    asset_dto = swagger_client.AssetDto(name='foo', value_scope='Global')
    asset_dto.id = 1111
    asset_dto.value = 'test-value'
    asset_dto.description = 'test-desc'
    api_response.value = [asset_dto]

    git_asset = {'asset': 'test-asset',
                 'value': 'test-value',
                 'desc': 'test-desc'}
    git_subfolders = [{'subfolder': 'test-subfolder', 
                       'assets': [git_asset]}]

    orch_folders = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-subfolder')
    folder_dto.id = 1234
    orch_folders.value = [folder_dto]

    mocker.patch('uipath_config.get_assets', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_asset')
    uipath_config.process_subfolder_asset_deletions(api_client, git_subfolders,
                                                    orch_folders.to_dict()['value'])
    mock_call.assert_called_once_with(api_client, 1111, 1234)

def test_get_group_id(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfUserDto()
    user_dto = swagger_client.UserDto()
    user_dto.id = 1111
    api_response.value = [user_dto]

    mocker.patch('uipath_config.swagger_client.UsersApi.users_get', 
                  return_value=api_response)
    assert api_response.to_dict()['value'][0]['id'] == uipath_config.get_group_id(api_client, 'test-group')

def test_prepare_assign_groups_roles_one_role():
    group = {'group': 'Automation Developers',
             'roles': [{'role': 'Tenant-Role-Test'}]}
    orch_roles = [{'name': 'Tenant-Role-Test', 
                    'display_name': 'Tenant-Role-Test', 
                    'type': 'Tenant', 
                    'groups': None, 
                    'is_static': False, 
                    'is_editable': True, 
                    'permissions': None, 
                    'id': 6799364}]
    folder_roles_dto = swagger_client.FolderRolesDto()
    folder_roles_dto.folder_id = 1234
    folder_roles_dto.role_ids = [6799364]
    folder_roles_dtos = [folder_roles_dto]

    assert folder_roles_dtos == uipath_config.prepare_assign_groups_roles(group, 1234, orch_roles)

def test_prepare_assign_groups_roles_two_role():
    group = {'group': 'Automation Developers',
             'roles': [{'role': 'Tenant-Role-Test'},
                       {'role': 'Tenant-Role-Test2'}]}
    orch_roles = [{'name': 'Tenant-Role-Test', 
                    'display_name': 'Tenant-Role-Test', 
                    'type': 'Tenant', 
                    'groups': None, 
                    'is_static': False, 
                    'is_editable': True, 
                    'permissions': None, 
                    'id': 6799364}]
    folder_roles_dto = swagger_client.FolderRolesDto()
    folder_roles_dto.folder_id = 1234
    folder_roles_dto.role_ids = [6799364, None]
    folder_roles_dtos = [folder_roles_dto]

    assert folder_roles_dtos == uipath_config.prepare_assign_groups_roles(group, 1234, orch_roles)

def test_assign_groups_roles(mocker):
    body_assign = swagger_client.UserAssignmentsDto()
    body_assign.user_ids = [1111]
    folder_roles_dto = swagger_client.FolderRolesDto()
    folder_roles_dto.folder_id = 2222
    folder_roles_dto.role_ids = [3333]
    folder_roles_dtos = [folder_roles_dto]
    body_assign.roles_per_folder = [folder_roles_dto]
    body = swagger_client.FolderAssignUsersRequest(assignments=body_assign)

    mock_call = mocker.patch('uipath_config.swagger_client.FoldersApi.folders_assign_users')
    uipath_config.assign_groups_roles(api_client, 1111, folder_roles_dtos)
    mock_call.assert_called_once_with(body=body)

def test_process_folder_assign_groups_roles(mocker):
    groups = [{'group': 'Automation Developers',
               'roles': [{'role': 'Tenant-Role-Test'},
                         {'role': 'Tenant-Role-Test2'}]}]
    orch_roles = [{'name': 'Tenant-Role-Test', 
                   'display_name': 'Tenant-Role-Test', 
                   'type': 'Tenant', 
                   'groups': None, 
                   'is_static': False, 
                   'is_editable': True, 
                   'permissions': None, 
                   'id': 6799364}]
    folder_roles_dto = swagger_client.FolderRolesDto()
    folder_roles_dto.folder_id = 2222
    folder_roles_dto.role_ids = [6799364, None]
    folder_roles_dtos = [folder_roles_dto]

    mocker.patch('uipath_config.get_group_id', return_value=1111)
    mock_call = mocker.patch('uipath_config.assign_groups_roles')
    uipath_config.process_folder_assign_groups_roles(api_client, groups, 
                                                     2222, orch_roles)
    mock_call.assert_called_once_with(api_client, 1111, folder_roles_dtos)

def test_process_subfolder_assign_groups_roles(mocker):
    git_subfolders = [{'subfolder': 'test-sub-1',
                       'groups': [{'group': 'Automation Developers',
                                   'roles': [{'role': 'Tenant-Role-Test'},
                                             {'role': 'Automation User'}]}]}]
    orch_folders = [{'display_name': 'test-sub-1',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 9999,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}]
    orch_roles = [{'name': 'Tenant-Role-Test', 
                   'display_name': 'Tenant-Role-Test', 
                   'type': 'Tenant', 
                   'groups': None, 
                   'is_static': False, 
                   'is_editable': True, 
                   'permissions': None, 
                   'id': 6799364}]
    folder_roles_dto = swagger_client.FolderRolesDto()
    folder_roles_dto.folder_id = 1566107
    folder_roles_dto.role_ids = [6799364, None]
    folder_roles_dtos = [folder_roles_dto]

    mocker.patch('uipath_config.get_group_id', return_value=1111)
    mock_call = mocker.patch('uipath_config.assign_groups_roles')
    uipath_config.process_subfolder_assign_groups_roles(api_client, 
                                                        git_subfolders, 
                                                        orch_folders, 
                                                        orch_roles)
    mock_call.assert_called_once_with(api_client, 1111, folder_roles_dtos)

def test_get_queues(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    queue_dto = swagger_client.QueueDefinitionDto(name='test-queue')
    queue_dto.id = 4444
    api_response.value = [queue_dto]

    mocker.patch('uipath_config.swagger_client.QueueDefinitionsApi.queue_definitions_get', 
                  return_value=api_response)
    assert api_response.to_dict() == uipath_config.get_queues(api_client, 1566107)

def test_compare_queue_match():
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    queue_dto = swagger_client.QueueDefinitionDto(name='test-queue')
    queue_dto.id = 4444
    api_response.value = [queue_dto]
    
    assert queue_dto == uipath_config.compare_queue('test-queue', 
                                                     api_response.to_dict()['value'])

def test_compare_queue_no_match():
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    queue_dto = swagger_client.QueueDefinitionDto(name='test-queue')
    queue_dto.id = 4444
    api_response.value = [queue_dto]
    
    assert queue_dto is not uipath_config.compare_queue('test-foo', 
                                                     api_response.to_dict()['value'])

def test_compare_queue_to_delete_match():
    git_queues = [{'queue': 'test-queue', 'desc': 'test'}]
    assert uipath_config.compare_queue_to_delete('test-queue', git_queues)

def test_compare_queue_to_delete_no_match():
    git_queues = [{'queue': 'test-queue', 'desc': 'test'}]
    assert not uipath_config.compare_queue_to_delete('foo', git_queues)

def test_create_queue(mocker):
    queue = {'queue': 'test-queue', 'desc': 'testing'}
    body = swagger_client.QueueDefinitionDto(name='test-queue')
    body.description = 'testing'
    body.enforce_unique_reference = True

    mock_call = mocker.patch('uipath_config.swagger_client.QueueDefinitionsApi.queue_definitions_post')
    uipath_config.create_queue(api_client, queue, 1111)
    mock_call.assert_called_once_with(body=body, 
                                      x_uipath_organization_unit_id=1111)

def test_delete_queue(mocker):
    mock_queue_delete = mocker.patch('uipath_config.swagger_client.QueueDefinitionsApi.queue_definitions_delete_by_id')
    uipath_config.delete_queue(api_client, 1234, 5678)
    mock_queue_delete.assert_called_once_with(key=1234,
                                              x_uipath_organization_unit_id=5678)

def test_process_queues_match(mocker):
    git_subfolders = [{'subfolder': 'test-sub-1',
                       'queues': [{'queue': 'test-queue',
                                   'desc': 'test'}]}]
    orch_folders = [{'display_name': 'test-sub-1',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 9999,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}]
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    queue_dto = swagger_client.QueueDefinitionDto(name='test-queue')
    queue_dto.id = 4444
    api_response.value = [queue_dto]

    mocker.patch('uipath_config.get_queues', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_queue')
    uipath_config.process_queues(api_client, git_subfolders, orch_folders)
    mock_call.assert_not_called()

def test_process_queues_no_match(mocker):
    git_subfolders = [{'subfolder': 'test-sub-1',
                       'queues': [{'queue': 'test-queue',
                                   'desc': 'test'}]}]
    queue = {'queue': 'test-queue', 'desc': 'test'}
    orch_folders = [{'display_name': 'test-sub-1',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 9999,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}]
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    queue_dto = swagger_client.QueueDefinitionDto(name='test-foo')
    queue_dto.id = 4444
    api_response.value = [queue_dto]

    mocker.patch('uipath_config.get_queues', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_queue')
    uipath_config.process_queues(api_client, git_subfolders, orch_folders)
    mock_call.assert_called_once_with(api_client, queue, 1566107)

def test_process_queues_no_queues(mocker):
    git_subfolders = [{'subfolder': 'test-sub-1',
                       'queues': [{'queue': 'test-queue',
                                   'desc': 'test'}]}]
    queue = {'queue': 'test-queue', 'desc': 'test'}
    orch_folders = [{'display_name': 'test-sub-1',
                     'id': 1566107,
                     'key': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                     'parent_id': 9999,
                     'parent_key': '3fa85f64-5717-4562-b3fc-2c963f66afa6'}]
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    api_response.value = []

    mocker.patch('uipath_config.get_queues', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_queue')
    uipath_config.process_queues(api_client, git_subfolders, orch_folders)
    mock_call.assert_called_once_with(api_client, queue, 1566107)

def test_process_queue_deletions_match(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    queue_dto = swagger_client.QueueDefinitionDto(name='test-queue')
    queue_dto.id = 1111
    queue_dto.description = 'test-desc'
    queue_dto.enforce_unique_reference = True
    api_response.value = [queue_dto]

    git_queue = {'queue': 'test-queue', 'desc': 'test-desc'}
    git_subfolders = [{'subfolder': 'test-subfolder', 
                       'queues': [git_queue]}]

    orch_folders = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-subfolder')
    folder_dto.id = 1234
    orch_folders.value = [folder_dto]

    mocker.patch('uipath_config.get_queues', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_queue')
    uipath_config.process_queue_deletions(api_client, git_subfolders,
                                          orch_folders.to_dict()['value'])
    mock_call.assert_not_called()

def test_process_queue_deletions_no_match(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfQueueDefinitionDto()
    queue_dto = swagger_client.QueueDefinitionDto(name='foo')
    queue_dto.id = 1111
    queue_dto.description = 'test-desc'
    queue_dto.enforce_unique_reference = True
    api_response.value = [queue_dto]

    git_queue = {'queue': 'test-queue', 'desc': 'test-desc'}
    git_subfolders = [{'subfolder': 'test-subfolder', 
                       'queues': [git_queue]}]

    orch_folders = swagger_client.ODataValueOfIEnumerableOfFolderDto()
    folder_dto = swagger_client.FolderDto(display_name='test-subfolder')
    folder_dto.id = 1234
    orch_folders.value = [folder_dto]

    mocker.patch('uipath_config.get_queues', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_queue')
    uipath_config.process_queue_deletions(api_client, git_subfolders,
                                          orch_folders.to_dict()['value'])
    mock_call.assert_called_once_with(api_client, 1111, 1234)

def test_get_machines(mocker):
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    machine_dto = swagger_client.ExtendedMachineDto(name='test-machine')
    machine_dto.description = 'test'
    machine_dto.id = 1111
    api_response.value = [machine_dto]

    mocker.patch('uipath_config.swagger_client.MachinesApi.machines_get', 
                  return_value=api_response)
    assert api_response.to_dict() == uipath_config.get_machines(api_client)

def test_compare_machine_match():
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    machine_dto = swagger_client.MachineDto(name='test-machine')
    machine_dto.id = 1111
    api_response.value = [machine_dto]
    
    assert machine_dto == uipath_config.compare_machine('test-machine', 
                                                         api_response.to_dict()['value'])

def test_compare_machine_no_match():
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    machine_dto = swagger_client.MachineDto(name='test-machine')
    machine_dto.id = 1111
    api_response.value = [machine_dto]
    
    assert machine_dto is not uipath_config.compare_machine('test-foo', 
                                                             api_response.to_dict()['value'])

def test_compare_machine_to_delete_no_match():
    git_machines = [{'machine': 'test-machine', 'desc': 'test'}]
    assert not uipath_config.compare_machine_to_delete('foo', git_machines)

def test_compare_machine_to_delete_match():
    git_machines = [{'machine': 'test-machine', 'desc': 'test'}]
    assert uipath_config.compare_machine_to_delete('test-machine', git_machines)

def test_create_machine(mocker):
    machine = {'machine': 'test-machine', 'desc': 'test'}
    body = swagger_client.MachineDto(name='test-machine')
    body.description = 'test'
    body.type = 'Template'

    mock_call = mocker.patch('uipath_config.swagger_client.MachinesApi.machines_post')
    uipath_config.create_machine(api_client, machine)
    mock_call.assert_called_once_with(body=body)

def test_delete_machine(mocker):
    mock_call = mocker.patch('uipath_config.swagger_client.MachinesApi.machines_delete_by_id')
    uipath_config.delete_machine(api_client, 1234)
    mock_call.assert_called_once_with(key=1234)

def test_process_machines_match(mocker):
    git_machines = [{'machine': 'test-machine', 'desc': 'test'}]
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    machine_dto = swagger_client.ExtendedMachineDto(name='test-machine')
    machine_dto.description = 'test'
    machine_dto.id = 1111
    api_response.value = [machine_dto]

    mocker.patch('uipath_config.get_machines', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_machine')
    uipath_config.process_machines(api_client, git_machines)
    mock_call.assert_not_called()

def test_process_machines_no_match(mocker):
    git_machines = [{'machine': 'test-machine', 'desc': 'test'}]
    machine = {'machine': 'test-machine', 'desc': 'test'}
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    machine_dto = swagger_client.ExtendedMachineDto(name='test-foo')
    machine_dto.description = 'test'
    machine_dto.id = 1111
    api_response.value = [machine_dto]

    mocker.patch('uipath_config.get_machines', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_machine')
    uipath_config.process_machines(api_client, git_machines)
    mock_call.assert_called_once_with(api_client, machine)

def test_process_machines_no_machine(mocker):
    git_machines = [{'machine': 'test-machine', 'desc': 'test'}]
    machine = {'machine': 'test-machine', 'desc': 'test'}
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    api_response.value = []

    mocker.patch('uipath_config.get_machines', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.create_machine')
    uipath_config.process_machines(api_client, git_machines)
    mock_call.assert_called_once_with(api_client, machine)

def test_process_machine_deletions_match(mocker):
    git_machines = {'machines': [{'machine': 'test-machine', 'desc': 'test'}]}
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    machine_dto = swagger_client.ExtendedMachineDto(name='test-machine')
    machine_dto.description = 'test'
    machine_dto.id = 1111
    api_response.value = [machine_dto]

    mocker.patch('uipath_config.get_machines', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_machine')
    uipath_config.process_machine_deletions(api_client, git_machines)
    mock_call.assert_not_called()

def test_process_machine_deletions_no_match(mocker):
    git_machines = {'machines': [{'machine': 'test-machine', 'desc': 'test'}]}
    api_response = swagger_client.ODataValueOfIEnumerableOfExtendedMachineDto()
    machine_dto = swagger_client.ExtendedMachineDto(name='foo')
    machine_dto.description = 'test'
    machine_dto.id = 1111
    api_response.value = [machine_dto]

    mocker.patch('uipath_config.get_machines', return_value=api_response.to_dict())
    mock_call = mocker.patch('uipath_config.delete_machine')
    uipath_config.process_machine_deletions(api_client, git_machines)
    mock_call.assert_called_once_with(api_client, 1111)