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

import logging

from keystoneauth1 import loading as kaloading
from oslo_utils import importutils

from ironicclient.common.i18n import _
from ironicclient import exc

LOG = logging.getLogger(__name__)


def get_client(api_version, auth_type=None, os_ironic_api_version=None,
               max_retries=None, retry_interval=None, **kwargs):
    """Get an authenticated client, based on the credentials.

    :param api_version: the API version to use. Valid value: '1'.
    :param auth_type: type of keystoneauth auth plugin loader to use.
    :param os_ironic_api_version: ironic API version to use.
    :param max_retries: Maximum number of retries in case of conflict error
    :param retry_interval: Amount of time (in seconds) between retries in case
        of conflict error.
    :param kwargs: all the other params that are passed to keystoneauth.
    """
    # TODO(TheJulia): At some point, we should consider possibly noting
    # the "latest" flag for os_ironic_api_version to cause the client to
    # auto-negotiate to the greatest available version, however we do not
    # have the ability yet for a caller to cap the version, and will hold
    # off doing so until then.
    if auth_type is None:
        if 'endpoint' in kwargs:
            if 'token' in kwargs:
                auth_type = 'admin_token'
            else:
                auth_type = 'none'
        elif 'token' in kwargs and 'auth_url' in kwargs:
            auth_type = 'token'
        else:
            auth_type = 'password'
    session = kwargs.get('session')
    if not session:
        loader = kaloading.get_plugin_loader(auth_type)
        loader_options = loader.get_options()
        # option.name looks like 'project-name', while dest will be the actual
        # argument name to which the value will be passed to (project_name)
        auth_options = [o.dest for o in loader_options]
        # Include deprecated names as well
        auth_options.extend([d.dest for o in loader_options
                             for d in o.deprecated])
        auth_kwargs = {k: v for (k, v) in kwargs.items() if k in auth_options}
        auth_plugin = loader.load_from_options(**auth_kwargs)
        # Let keystoneauth do the necessary parameter conversions
        session_loader = kaloading.session.Session()
        session_opts = {k: v for (k, v) in kwargs.items() if k in
                        [o.dest for o in session_loader.get_conf_options()]}
        session = session_loader.load_from_options(auth=auth_plugin,
                                                   **session_opts)

    # Make sure we also pass the endpoint interface to the HTTP client.
    # NOTE(gyee/efried): 'interface' in ksa config is deprecated in favor of
    # 'valid_interfaces'. So, since the caller may be deriving kwargs from
    # conf, accept 'valid_interfaces' first. But keep support for 'interface',
    # in case the caller is deriving kwargs from, say, an existing Adapter.
    interface = kwargs.get('valid_interfaces', kwargs.get('interface'))

    endpoint = kwargs.get('endpoint')
    if not endpoint:
        try:
            # endpoint will be used to get hostname
            # and port that will be used for API version caching.
            # NOTE(gyee): KSA defaults interface to 'public' if it is
            # empty or None so there's no need to set it to publicURL
            # explicitly.
            endpoint = session.get_endpoint(
                service_type=kwargs.get('service_type') or 'baremetal',
                interface=interface,
                region_name=kwargs.get('region_name')
            )
        except Exception as e:
            raise exc.AmbiguousAuthSystem(
                _('Must provide Keystone credentials or user-defined '
                  'endpoint, error was: %s') % e)

    ironicclient_kwargs = {
        'os_ironic_api_version': os_ironic_api_version,
        'max_retries': max_retries,
        'retry_interval': retry_interval,
        'session': session,
        'endpoint_override': endpoint,
        'interface': interface
    }

    return Client(api_version, **ironicclient_kwargs)


def Client(version, *args, **kwargs):
    module = importutils.import_versioned_module('ironicclient',
                                                 version, 'client')
    client_class = getattr(module, 'Client')
    return client_class(*args, **kwargs)
