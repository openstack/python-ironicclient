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

from ironicclient.common import base
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc


class DeployTemplate(base.Resource):
    def __repr__(self):
        return "<DeployTemplate %s>" % self._info


class DeployTemplateManager(base.CreateManager):
    resource_class = DeployTemplate
    _creation_attributes = ['extra', 'name', 'steps', 'uuid']
    _resource_name = 'deploy_templates'

    def list(self, limit=None, marker=None, sort_key=None, sort_dir=None,
             detail=False, fields=None):
        """Retrieve a list of deploy templates.

        :param marker: Optional, the UUID of a deploy template, eg the last
                       template from a previous result set. Return the next
                       result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of deploy templates to return.
            2) limit == 0, return the entire list of deploy templates.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Ironic API
               (see Ironic's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about deploy templates.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :returns: A list of deploy templates.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(_("Can't fetch a subset of fields "
                                         "with 'detail' set"))

        filters = utils.common_filters(marker, limit, sort_key, sort_dir,
                                       fields, detail=detail)
        path = ''
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "deploy_templates")
        else:
            return self._list_pagination(self._path(path), "deploy_templates",
                                         limit=limit)

    def get(self, template_id, fields=None):
        return self._get(resource_id=template_id, fields=fields)

    def delete(self, template_id):
        return self._delete(resource_id=template_id)

    def update(self, template_id, patch):
        return self._update(resource_id=template_id, patch=patch)
