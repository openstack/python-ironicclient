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
import six

import six.moves.urllib.parse as urlparse

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


@six.add_metaclass(abc.ABCMeta)
class Manager(object):
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

    @abc.abstractproperty
    def resource_class(self):
        """The resource class

        """

    @abc.abstractproperty
    def _resource_name(self):
        """The resource name.

        """

    def _get(self, resource_id, fields=None):
        """Retrieve a resource.

        :param resource_id: Identifier of the resource.
        :param fields: List of specific fields to be returned.
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
            return self._list(self._path(resource_id))[0]
        except IndexError:
            return None

    def _get_as_dict(self, resource_id, fields=None):
        """Retrieve a resource as a dictionary

        :param resource_id: Identifier of the resource.
        :param fields: List of specific fields to be returned.
        :returns: a dictionary representing the resource; may be empty
        """

        resource = self._get(resource_id, fields=fields)
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
                         limit=None):
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

        """
        if obj_class is None:
            obj_class = self.resource_class

        if limit is not None:
            limit = int(limit)

        object_list = []
        object_count = 0
        limit_reached = False
        while url:
            resp, body = self.api.json_request('GET', url)
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
                url = urlparse.urlunparse(url_parts)

        return object_list

    def _list(self, url, response_key=None, obj_class=None, body=None):
        resp, body = self.api.json_request('GET', url)

        if obj_class is None:
            obj_class = self.resource_class

        data = self._format_body_data(body, response_key)
        return [obj_class(self, res, loaded=True) for res in data if res]

    def _update(self, resource_id, patch, method='PATCH'):
        """Update a resource.

        :param resource_id: Resource identifier.
        :param patch: New version of a given resource.
        :param method: Name of the method for the request.
        """

        url = self._path(resource_id)
        resp, body = self.api.json_request(method, url, body=patch)
        # PATCH/PUT requests may not return a body
        if body:
            return self.resource_class(self, body)

    def _delete(self, resource_id):
        """Delete a resource.

        :param resource_id: Resource identifier.
        """
        self.api.raw_request('DELETE', self._path(resource_id))


@six.add_metaclass(abc.ABCMeta)
class CreateManager(Manager):
    """Provides creation operations with a particular API."""

    @abc.abstractproperty
    def _creation_attributes(self):
        """A list of required creation attributes for a resource type.

        """

    def create(self, **kwargs):
        """Create a resource based on a kwargs dictionary of attributes.

        :param kwargs: A dictionary containing the attributes of the resource
                       that will be created.
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
        url = self._path()
        resp, body = self.api.json_request('POST', url, body=new)
        if body:
            return self.resource_class(self, body)


class Resource(base.Resource):
    """Represents a particular instance of an object (tenant, user, etc).

    This is pretty much just a bag for attributes.
    """

    def to_dict(self):
        return copy.deepcopy(self._info)
