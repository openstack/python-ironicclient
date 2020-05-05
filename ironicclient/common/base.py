# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Base utilities to build API operation managers and objects on top of.
"""

import abc
import copy
from urllib import parse as urlparse

from ironicclient.common.apiclient import base
from ironicclient import exc


def getid(obj):
    """Wrapper to get  object's ID.

    Abstracts the common pattern of allowing both an object or an
    object's ID (UUID) as a parameter when dealing with relationships.
    """
    try:
        return obj.id
    except AttributeError:
        return obj


class Manager(object, metaclass=abc.ABCMeta):
    """Provides  CRUD operations with a particular API."""

    def __init__(self, api):
        self.api = api

    def _path(self, resource_id=None):
        """Returns a request path for a given resource identifier.

        :param resource_id: Identifier of the resource to generate the request
                            path.
        """
        return ('/v1/%s/%s' % (self._resource_name, resource_id)
                if resource_id else '/v1/%s' % self._resource_name)

    @property
    @abc.abstractmethod
    def resource_class(self):
        """The resource class

        """

    @property
    @abc.abstractmethod
    def _resource_name(self):
        """The resource name.

        """

    def _get(self, resource_id, fields=None, os_ironic_api_version=None,
             global_request_id=None):
        """Retrieve a resource.

        :param resource_id: Identifier of the resource.
        :param fields: List of specific fields to be returned.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :raises exc.ValidationError: For invalid resource_id arg value.
        """

        if not resource_id:
            raise exc.ValidationError(
                "The identifier argument is invalid. "
                "Value provided: {!r}".format(resource_id))

        if fields is not None:
            resource_id = '%s?fields=' % resource_id
            resource_id += ','.join(fields)

        try:
            return self._list(
                self._path(resource_id),
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id)[0]
        except IndexError:
            return None

    def _get_as_dict(self, resource_id, fields=None,
                     os_ironic_api_version=None, global_request_id=None):
        """Retrieve a resource as a dictionary

        :param resource_id: Identifier of the resource.
        :param fields: List of specific fields to be returned.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :returns: a dictionary representing the resource; may be empty
        """

        resource = self._get(resource_id, fields=fields,
                             os_ironic_api_version=os_ironic_api_version,
                             global_request_id=global_request_id)
        if resource:
            return resource.to_dict()
        else:
            return {}

    def _format_body_data(self, body, response_key):
        if response_key:
            try:
                data = body[response_key]
            except KeyError:
                return []
        else:
            data = body

        if not isinstance(data, list):
            data = [data]

        return data

    def _list_pagination(self, url, response_key=None, obj_class=None,
                         limit=None, os_ironic_api_version=None,
                         global_request_id=None):
        """Retrieve a list of items.

        The Ironic API is configured to return a maximum number of
        items per request, (see Ironic's api.max_limit option). This
        iterates over the 'next' link (pagination) in the responses,
        to get the number of items specified by 'limit'. If 'limit'
        is None this function will continue pagination until there are
        no more values to be returned.

        :param url: a partial URL, e.g. '/nodes'
        :param response_key: the key to be looked up in response
            dictionary, e.g. 'nodes'
        :param obj_class: class for constructing the returned objects.
        :param limit: maximum number of items to return. If None returns
            everything.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        if obj_class is None:
            obj_class = self.resource_class

        if limit is not None:
            limit = int(limit)
        kwargs = {"headers": {}}
        if os_ironic_api_version is not None:
            kwargs['headers'][
                'X-OpenStack-Ironic-API-Version'] = os_ironic_api_version
        if global_request_id is not None:
            kwargs["headers"]["X-Openstack-Request-Id"] = global_request_id

        # NOTE(jroll)
        # endpoint_trimmed is what is prepended if we only pass a path
        # to json_request. This might be something like
        # https://example.com:4443/baremetal
        # The code below which parses the 'next' URL keeps any path prefix
        # we're using, so it ends up calling json_request() with e.g.
        # /baremetal/v1/nodes. When this is appended to endpoint_trimmed,
        # we end up with a full URL of e.g.
        # https://example.com:4443/baremetal/baremetal/v1/nodes.
        # Parse out the prefix from the base endpoint here, so we can strip
        # it below and make sure we're passing a correct path.
        endpoint_parts = urlparse.urlparse(self.api.endpoint_trimmed)
        url_path_prefix = endpoint_parts[2]

        object_list = []
        object_count = 0
        limit_reached = False
        while url:
            resp, body = self.api.json_request('GET', url, **kwargs)
            data = self._format_body_data(body, response_key)
            for obj in data:
                object_list.append(obj_class(self, obj, loaded=True))
                object_count += 1
                if limit and object_count >= limit:
                    # break the for loop
                    limit_reached = True
                    break

            # break the while loop and return
            if limit_reached:
                break

            url = body.get('next')
            if url:
                # NOTE(lucasagomes): We need to edit the URL to remove
                # the scheme and netloc
                url_parts = list(urlparse.urlparse(url))
                url_parts[0] = url_parts[1] = ''
                if url_path_prefix:
                    url_parts[2] = url_parts[2].replace(
                        url_path_prefix, '', 1)
                url = urlparse.urlunparse(url_parts)

        return object_list

    def __list(self, url, response_key=None, body=None,
               os_ironic_api_version=None, global_request_id=None):
        kwargs = {"headers": {}}

        if os_ironic_api_version is not None:
            kwargs['headers'][
                'X-OpenStack-Ironic-API-Version'] = os_ironic_api_version
        if global_request_id is not None:
            kwargs["headers"]["X-Openstack-Request-Id"] = global_request_id

        resp, body = self.api.json_request('GET', url, **kwargs)

        data = self._format_body_data(body, response_key)
        return data

    def _list(self, url, response_key=None, obj_class=None, body=None,
              os_ironic_api_version=None, global_request_id=None):
        if obj_class is None:
            obj_class = self.resource_class

        data = self.__list(url, response_key=response_key, body=body,
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)
        return [obj_class(self, res, loaded=True) for res in data if res]

    def _list_primitives(self, url, response_key=None,
                         os_ironic_api_version=None, global_request_id=None):
        return self.__list(url, response_key=response_key,
                           os_ironic_api_version=os_ironic_api_version,
                           global_request_id=global_request_id)

    def _update(self, resource_id, patch, method='PATCH',
                os_ironic_api_version=None, global_request_id=None,
                params=None):
        """Update a resource.

        :param resource_id: Resource identifier.
        :param patch: New version of a given resource, a dictionary or None.
        :param method: Name of the method for the request.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :param params: query parameters to pass.
        """

        url = self._path(resource_id)
        kwargs = {"headers": {}}
        if patch is not None:
            kwargs['body'] = patch
        if os_ironic_api_version is not None:
            kwargs['headers'][
                'X-OpenStack-Ironic-API-Version'] = os_ironic_api_version
        if global_request_id is not None:
            kwargs["headers"]["X-Openstack-Request-Id"] = global_request_id
        if params:
            kwargs['params'] = params
        resp, body = self.api.json_request(method, url, **kwargs)
        # PATCH/PUT requests may not return a body
        if body:
            return self.resource_class(self, body)

    def _delete(self, resource_id,
                os_ironic_api_version=None, global_request_id=None):
        """Delete a resource.

        :param resource_id: Resource identifier.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        headers = {}
        if os_ironic_api_version is not None:
            headers["X-OpenStack-Ironic-API-Version"] = os_ironic_api_version
        if global_request_id is not None:
            headers["X-Openstack-Request-Id"] = global_request_id
        self.api.raw_request('DELETE', self._path(resource_id),
                             headers=headers)


class CreateManager(Manager, metaclass=abc.ABCMeta):
    """Provides creation operations with a particular API."""

    @property
    @abc.abstractmethod
    def _creation_attributes(self):
        """A list of required creation attributes for a resource type.

        """

    def create(self, os_ironic_api_version=None, global_request_id=None,
               **kwargs):
        """Create a resource based on a kwargs dictionary of attributes.

        :param kwargs: A dictionary containing the attributes of the resource
                       that will be created.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :raises exc.InvalidAttribute: For invalid attributes that are not
                                      needed to create the resource.
        """

        new = {}
        invalid = []
        for (key, value) in kwargs.items():
            if key in self._creation_attributes:
                new[key] = value
            else:
                invalid.append(key)
        if invalid:
            raise exc.InvalidAttribute(
                'The attribute(s) "%(attrs)s" are invalid; they are not '
                'needed to create %(resource)s.' %
                {'resource': self._resource_name,
                 'attrs': '","'.join(invalid)})
        headers = {}
        if os_ironic_api_version is not None:
            headers['X-OpenStack-Ironic-API-Version'] = os_ironic_api_version
        if global_request_id is not None:
            headers["X-Openstack-Request-Id"] = global_request_id
        url = self._path()
        resp, body = self.api.json_request('POST', url, body=new,
                                           headers=headers)
        if body:
            return self.resource_class(self, body)


class Resource(base.Resource):
    """Represents a particular instance of an object (tenant, user, etc).

    This is pretty much just a bag for attributes.
    """

    def to_dict(self):
        return copy.deepcopy(self._info)
