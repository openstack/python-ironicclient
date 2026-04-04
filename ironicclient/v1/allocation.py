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

from collections.abc import Callable
import logging
from typing import Any

from ironicclient.common import base
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc


LOG: logging.Logger = logging.getLogger(__name__)


class Allocation(base.Resource):
    def __repr__(self) -> str:
        return "<Allocation %s>" % self._info


class AllocationManager(base.CreateManager[Allocation]):
    resource_class: type[Allocation] = Allocation
    _resource_name: str = 'allocations'
    _creation_attributes: list[str] = [
        'extra', 'name', 'resource_class', 'uuid',
        'traits', 'candidate_nodes', 'node', 'owner',
    ]

    def get(
        self,
        allocation_id: str,
        fields: list[str] | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource | None:
        """Get an allocation with the specified identifier.

        :param allocation_id: The UUID or name of an allocation.
        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned. Can not be used
                       when 'detail' is set.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: an :class:`Allocation` object.

        """
        return self._get(
            resource_id=allocation_id,
            fields=fields,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def delete(
        self,
        allocation_id: str,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> None:
        """Delete the Allocation.

        :param allocation_id: The UUID or name of an allocation.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        return self._delete(
            resource_id=allocation_id,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def wait(
        self,
        allocation_id: str,
        timeout: int | float = 0,
        poll_interval: int | float = 1,
        poll_delay_function: (
            Callable[[int | float], object] | None
        ) = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource | None:
        """Wait for the Allocation to become active.

        :param timeout: timeout in seconds, no timeout if 0.
        :param poll_interval: interval in seconds between polls.
        :param poll_delay_function: function to use to wait between polls
            (defaults to time.sleep). Should take one argument - delay time
            in seconds. Any exceptions raised inside it will abort the wait.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        :return: updated :class:`Allocation` object.
        :raises: StateTransitionFailed if allocation reaches the error state.
        :raises: StateTransitionTimeout on timeout.
        """
        timeout_msg = _(
            'Allocation %(allocation)s failed to become active '
            'in %(timeout)s seconds') % {
                'allocation': allocation_id,
                'timeout': timeout}
        for _count in utils.poll(
            timeout, poll_interval, poll_delay_function,
            timeout_msg,
        ):
            allocation = self.get(
                allocation_id,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
            if allocation is None:
                continue
            if allocation.state == 'error':
                raise exc.StateTransitionFailed(
                    _('Allocation %(allocation)s failed: '
                      '%(error)s') %
                    {'allocation': allocation_id,
                     'error': allocation.last_error})
            elif allocation.state == 'active':
                return allocation

            LOG.debug(
                'Still waiting for allocation %(allocation)s'
                ' to become active, the current state is'
                ' %(actual)s',
                {'allocation': allocation_id,
                 'actual': allocation.state})
        return None

    def update(
        self,
        allocation_id: str,
        patch: list[dict[str, Any]],
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> base.Resource | None:
        """Updates the Allocation. Only 'name' and 'extra' field are allowed.

        :param allocation_id: The UUID or name of an allocation.
        :param patch: a json PATCH document to apply to this allocation.
        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.
        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.
        """
        return self._update(
            resource_id=allocation_id,
            patch=patch,
            os_ironic_api_version=os_ironic_api_version,
            global_request_id=global_request_id,
        )

    def list(
        self,
        resource_class: str | None = None,
        state: str | None = None,
        node: str | None = None,
        limit: int | None = None,
        marker: str | None = None,
        sort_key: str | None = None,
        sort_dir: str | None = None,
        fields: list[str] | None = None,
        owner: str | None = None,
        os_ironic_api_version: str | None = None,
        global_request_id: str | None = None,
    ) -> list[Allocation]:
        """Retrieve a list of allocations.

        :param resource_class: Optional, get allocations with this resource
                               class.
        :param state: Optional, get allocations in this state. One of
                      ``allocating``, ``active`` or ``error``.
        :param node: UUID or name of the node of the allocation.
        :param marker: Optional, the UUID of an allocation, eg the last
                       allocation from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of allocations to return.
            2) limit == 0, return the entire list of allocations.
            3) limit == None, the number of items returned respect the
               maximum imposed by the Ironic API (see Ironic's
               api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param fields: Optional, a list with a specified set of fields
                       of the resource to be returned.
        :param owner: Optional, project that owns the allocation.

        :param os_ironic_api_version: String version (e.g. "1.35") to use for
            the request.  If not specified, the client's default is used.

        :param global_request_id: String containing global request ID header
            value (in form "req-<UUID>") to use for the request.

        :returns: A list of allocations.
        :raises: InvalidAttribute if a subset of fields is requested with
                 detail option set.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(
            marker, limit, sort_key, sort_dir, fields)
        for name, value in [('resource_class', resource_class),
                            ('state', state), ('node', node),
                            ('owner', owner)]:
            if value is not None:
                filters.append('%s=%s' % (name, value))

        if filters:
            path = '?' + '&'.join(filters)
        else:
            path = ''
        if limit is None:
            return self._list(
                self._path(path),
                "allocations",
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
        else:
            return self._list_pagination(
                self._path(path),
                "allocations",
                limit=limit,
                os_ironic_api_version=os_ironic_api_version,
                global_request_id=global_request_id,
            )
