# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 OpenStack Foundation
# Copyright 2011 Piston Cloud Computing, Inc.
#
# Modified by: Brad P. Crochet <brad@redhat.com>
#
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
OpenStack Client factory.
"""

from oslo_utils import importutils

from ironicclient.common.i18n import _
from ironicclient import exceptions


def get_client_class(version):
    version_map = {
        '1': 'ironicclient.v1.client.Client',
        '1.5': 'ironicclient.v1.client.Client',
        '1.6': 'ironicclient.v1.client.Client',
        '1.9': 'ironicclient.v1.client.Client',
    }
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = _("Invalid client version '%(version)s'. must be one of: "
                "%(keys)s") % {'version': version,
                               'keys': ', '.join(version_map)}
        raise exceptions.UnsupportedVersion(msg)

    return importutils.import_class(client_path)


def Client(version, *args, **kwargs):
    client_class = get_client_class(version)
    return client_class(*args, **kwargs)
