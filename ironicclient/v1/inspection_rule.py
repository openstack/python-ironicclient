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

from __future__ import annotations

from typing import Any

from ironicclient.common import base
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc


class InspectionRule(base.Resource):
    def __repr__(self) -> str:
        return "<InspectionRule %s>" % self._info


class InspectionRuleManager(base.CreateManager):
    resource_class: type[InspectionRule] = InspectionRule
    _creation_attributes: list[str] = [
        'uuid', 'description', 'priority', 'sensitive',
        'phase', 'conditions', 'actions',
    ]
    _resource_name: str = 'inspection_rules'

    def get(
        self,
        rule_id: str,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource | None:
        return self._get(
            resource_id=rule_id,
            fields=fields,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def delete(
        self,
        rule_id: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        return self._delete(
            resource_id=rule_id,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def update(
        self,
        rule_id: str,
        patch: list[dict[str, Any]],
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource | None:
        return self._update(
            resource_id=rule_id,
            patch=patch,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def list(
        self,
        limit: int | None = None,
        marker: str | None = None,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        detail: bool = False,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[base.Resource]:
        """Retrieve a list of rules.

        :param marker: Optional, the UUID of a deploy template, eg the last
                       template from a previous result set. Return the next
                       result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of rules to return.
            2) limit == 0, return the entire list of rules.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Ironic API
               (see Ironic's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about rules.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of rules.

        """
        if limit is not None:
            limit = int(limit)

        if detail and fields:
            raise exc.InvalidAttribute(
                _("Can't fetch a subset of fields "
                  "with 'detail' set"))

        filters = utils.common_filters(
            marker, limit, sort_key, sort_dir,
            fields, detail=detail)
        path = ''
        if filters:
            path += '?' + '&'.join(filters)
        if limit is None:
            return self._list(
                self._path(path),
                "inspection_rules",
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path),
                "inspection_rules",
                limit=limit,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
