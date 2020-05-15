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

from openstack import config
from oslo_utils import importutils

from ironicclient.common.i18n import _
from ironicclient import exc

LOG = logging.getLogger(__name__)


def get_client(api_version, auth_type=None, os_ironic_api_version=None,
               max_retries=None, retry_interval=None, session=None,
               valid_interfaces=None, interface=None, service_type=None,
               region_name=None, additional_headers=None,
               global_request_id=None, **kwargs):
    """Get an authenticated client, based on the credentials.

    :param api_version: the API version to use. Valid value: '1'.
    :param auth_type: type of keystoneauth auth plugin loader to use.
    :param os_ironic_api_version: ironic API version to use.
    :param max_retries: Maximum number of retries in case of conflict error
    :param retry_interval: Amount of time (in seconds) between retries in case
        of conflict error.
    :param session: An existing keystoneauth session. Will be created from
        kwargs if not provided.
    :param valid_interfaces: List of valid endpoint interfaces to use if
        the bare metal endpoint is not provided.
    :param interface: An alias for valid_interfaces.
    :param service_type: Bare metal endpoint service type.
    :param region_name: Name of the region to use when searching the bare metal
        endpoint.
    :param additional_headers: Additional headers that should be attached
        to every request passing through the client. Headers of the same name
        specified per request will take priority.
    :param global_request_id: A header (in the form of ``req-$uuid``) that will
        be passed on all requests. Enables cross project request id tracking.
    :param kwargs: all the other params that are passed to keystoneauth for
        session construction.
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

    if not session:
        # TODO(dtantsur): consider flipping load_yaml_config to True to support
        # the clouds.yaml format.
        region = config.get_cloud_region(load_yaml_config=False,
                                         load_envvars=False,
                                         auth_type=auth_type,
                                         **kwargs)
        session = region.get_session()

    # Make sure we also pass the endpoint interface to the HTTP client.
    # NOTE(gyee/efried): 'interface' in ksa config is deprecated in favor of
    # 'valid_interfaces'. So, since the caller may be deriving kwargs from
    # conf, accept 'valid_interfaces' first. But keep support for 'interface',
    # in case the caller is deriving kwargs from, say, an existing Adapter.
    interface = valid_interfaces or interface

    endpoint = kwargs.get('endpoint')
    if not endpoint:
        try:
            # endpoint will be used to get hostname
            # and port that will be used for API version caching.
            # NOTE(gyee): KSA defaults interface to 'public' if it is
            # empty or None so there's no need to set it to publicURL
            # explicitly.
            endpoint = session.get_endpoint(
                service_type=service_type or 'baremetal',
                interface=interface,
                region_name=region_name,
            )
        except Exception as e:
            raise exc.AmbiguousAuthSystem(
                _('Must provide Keystone credentials or user-defined '
                  'endpoint, error was: %s') % e)

    ironicclient_kwargs = {
        'os_ironic_api_version': os_ironic_api_version,
        'additional_headers': additional_headers,
        'global_request_id': global_request_id,
        'max_retries': max_retries,
        'retry_interval': retry_interval,
        'session': session,
        'endpoint_override': endpoint,
        'interface': interface
    }

    return Client(api_version, **ironicclient_kwargs)


def Client(version, endpoint_override=None, session=None, *args, **kwargs):
    """Create a client of an appropriate version.

    This call requires a session. If you want it to be created, use
    ``get_client`` instead.

    :param endpoint_override: A bare metal endpoint to use.
    :param session: A keystoneauth session to use. This argument is actually
        required and is marked optional only for backward compatibility.
    :param args: Other arguments to pass to the HTTP client. Not recommended,
        use kwargs instead.
    :param kwargs: Other keyword arguments to pass to the HTTP client (e.g.
        ``insecure``).
    """
    module = importutils.import_versioned_module('ironicclient',
                                                 version, 'client')
    client_class = getattr(module, 'Client')
    return client_class(endpoint_override=endpoint_override, session=session,
                        *args, **kwargs)
