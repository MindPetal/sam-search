
from __future__ import absolute_import

import re

import six

from client.api_client import ApiClient


class MsApi(object):

    def __init__(self, api_client=None):

        if api_client is None:
            api_client = ApiClient()

        self.api_client = api_client

    def teams_post(self, **kwargs):
        """Posts data to Teams channel.

        Makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, pass async_req=True
        >>> thread = api.teams_post(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str body
        :return: MsChannelDto
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True

        if kwargs.get('async_req'):
            return self.teams_post_with_http_info(**kwargs)
        else:
            (data) = self.teams_post_with_http_info(**kwargs)
            return data

    def teams_post_with_http_info(self, **kwargs):
        """Posts data to Teams channel.

        Makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, pass async_req=True
        >>> thread = api.teams_post(async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str body
        :return: MsChannelDto
                 If the method is called asynchronously,
                 returns the request thread.
        """
        all_params = ['body']
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()

        for key, val in six.iteritems(params['kwargs']):

            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method assets_post" % key)

            params[key] = val

        del params['kwargs']
        collection_formats = {}
        path_params = {}
        query_params = []
        header_params = {}
        form_params = []
        local_var_files = {}
        body_params = None

        if 'body' in params:
            body_params = params['body']
        
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])

        header_params['Content-Type'] = self.api_client.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.api_client.call_api(
            '', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type=str,
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)