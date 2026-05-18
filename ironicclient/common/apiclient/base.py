# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack Foundation
# Copyright 2012 Grid Dynamics
# Copyright 2013 OpenStack Foundation
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

from __future__ import annotations

# E1102: %s is not callable
# pylint: disable=E1102

import copy
from typing import Any, Callable, Protocol

from oslo_utils import strutils


class ManagerProtocol(Protocol):
    """Minimal protocol for Resource's manager dependency."""

    client: Any


class Resource(object):
    """Base class for OpenStack resources (tenant, user, etc.).

    This is pretty much just a bag for attributes.
    """

    HUMAN_ID: bool = False
    NAME_ATTR: str = "name"

    def __init__(
        self,
        manager: ManagerProtocol,
        info: dict[str, Any],
        loaded: bool = False,
    ) -> None:
        """Populate and bind to a manager.

        :param manager: BaseManager object
        :param info: dictionary representing resource attributes
        :param loaded: prevent lazy-loading if set to True
        """
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    def __repr__(self) -> str:
        reprkeys = sorted(
            k for k in self.__dict__.keys() if k[0] != "_" and k != "manager"
        )
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)

    @property
    def human_id(self) -> str | None:
        """Human-readable ID which can be used for bash completion."""
        if self.HUMAN_ID:
            name = getattr(self, self.NAME_ATTR, None)
            if name is not None:
                return str(strutils.to_slug(name))
        return None

    def _add_details(self, info: dict[str, Any]) -> None:
        for k, v in info.items():
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass

    def __getattr__(self, k: str) -> Any:
        if k not in self.__dict__:
            # NOTE(bcwaldon): disallow lazy-loading if already loaded once
            if not self.is_loaded():
                self.get()
                return self.__getattr__(k)

            raise AttributeError(k)
        else:
            return self.__dict__[k]

    def get(self) -> None:
        """Support for lazy loading details.

        Some clients, such as novaclient have the option to lazy load the
        details, details which can be loaded with this function.
        """
        # set_loaded() first ... so if we have to bail, we know we tried.
        self.set_loaded(True)
        get_fn: Callable[..., Resource] | None = getattr(
            self.manager, "get", None,
        )
        if get_fn is None:
            return

        new = get_fn(self.id)
        if new:
            self._add_details(new._info)
            self._add_details(
                {"x_request_id": self.manager.client.last_request_id}
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Resource):
            return NotImplemented
        # two resources of different types are not equal
        if not isinstance(other, self.__class__):
            return False
        return self._info == other._info

    def is_loaded(self) -> bool:
        return self._loaded

    def set_loaded(self, val: bool) -> None:
        self._loaded = val

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._info)
