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

from keystoneauth1 import loading as kaloading
from oslo_utils import importutils

from ironicclient.common.i18n import _
from ironicclient import exc


def get_client(api_version, os_auth_token=None, ironic_url=None,
               os_username=None, os_password=None, os_auth_url=None,
               os_project_id=None, os_project_name=None, os_tenant_id=None,
               os_tenant_name=None, os_region_name=None,
               os_user_domain_id=None, os_user_domain_name=None,
               os_project_domain_id=None, os_project_domain_name=None,
               os_service_type=None, os_endpoint_type=None,
               insecure=None, timeout=None, os_cacert=None, ca_file=None,
               os_cert=None, cert_file=None, os_key=None, key_file=None,
               os_ironic_api_version=None, max_retries=None,
               retry_interval=None, session=None, **ignored_kwargs):
    """Get an authenticated client, based on the credentials.

    :param api_version: the API version to use. Valid value: '1'.
    :param os_auth_token: pre-existing token to re-use
    :param ironic_url: ironic API endpoint
    :param os_username: name of a user
    :param os_password: user's password
    :param os_auth_url: endpoint to authenticate against
    :param os_tenant_name: name of a tenant (deprecated in favour of
        os_project_name)
    :param os_tenant_id: ID of a tenant (deprecated in favour of
        os_project_id)
    :param os_project_name: name of a project
    :param os_project_id: ID of a project
    :param os_region_name: name of a keystone region
    :param os_user_domain_name: name of a domain the user belongs to
    :param os_user_domain_id: ID of a domain the user belongs to
    :param os_project_domain_name: name of a domain the project belongs to
    :param os_project_domain_id: ID of a domain the project belongs to
    :param os_service_type: the type of service to lookup the endpoint for
    :param os_endpoint_type: the type (exposure) of the endpoint
    :param insecure: allow insecure SSL (no cert verification)
    :param timeout: allows customization of the timeout for client HTTP
        requests
    :param os_cacert: path to cacert file
    :param ca_file: path to cacert file, deprecated in favour of os_cacert
    :param os_cert: path to cert file
    :param cert_file: path to cert file, deprecated in favour of os_cert
    :param os_key: path to key file
    :param key_file: path to key file, deprecated in favour of os_key
    :param os_ironic_api_version: ironic API version to use
    :param max_retries: Maximum number of retries in case of conflict error
    :param retry_interval: Amount of time (in seconds) between retries in case
        of conflict error
    :param session: Keystone session to use
    :param ignored_kwargs: all the other params that are passed. Left for
        backwards compatibility. They are ignored.
    """
    os_service_type = os_service_type or 'baremetal'
    os_endpoint_type = os_endpoint_type or 'publicURL'
    project_id = (os_project_id or os_tenant_id)
    project_name = (os_project_name or os_tenant_name)
    kwargs = {
        'os_ironic_api_version': os_ironic_api_version,
        'max_retries': max_retries,
        'retry_interval': retry_interval,
    }
    endpoint = ironic_url
    cacert = os_cacert or ca_file
    cert = os_cert or cert_file
    key = os_key or key_file
    if os_auth_token and endpoint:
        kwargs.update({
            'token': os_auth_token,
            'insecure': insecure,
            'ca_file': cacert,
            'cert_file': cert,
            'key_file': key,
            'timeout': timeout,
        })
    elif os_auth_url:
        auth_type = 'password'
        auth_kwargs = {
            'auth_url': os_auth_url,
            'project_id': project_id,
            'project_name': project_name,
            'user_domain_id': os_user_domain_id,
            'user_domain_name': os_user_domain_name,
            'project_domain_id': os_project_domain_id,
            'project_domain_name': os_project_domain_name,
        }
        if os_username and os_password:
            auth_kwargs.update({
                'username': os_username,
                'password': os_password,
            })
        elif os_auth_token:
            auth_type = 'token'
            auth_kwargs.update({
                'token': os_auth_token,
            })
        # Create new session only if it was not passed in
        if not session:
            loader = kaloading.get_plugin_loader(auth_type)
            auth_plugin = loader.load_from_options(**auth_kwargs)
            # Let keystoneauth do the necessary parameter conversions
            session = kaloading.session.Session().load_from_options(
                auth=auth_plugin, insecure=insecure, cacert=cacert,
                cert=cert, key=key, timeout=timeout,
            )

    exception_msg = _('Must provide Keystone credentials or user-defined '
                      'endpoint and token')
    if not endpoint:
        if session:
            try:
                # Pass the endpoint, it will be used to get hostname
                # and port that will be used for API version caching. It will
                # be also set as endpoint_override.
                endpoint = session.get_endpoint(
                    service_type=os_service_type,
                    interface=os_endpoint_type,
                    region_name=os_region_name
                )
            except Exception as e:
                raise exc.AmbiguousAuthSystem(
                    _('%(message)s, error was: %(error)s') %
                    {'message': exception_msg, 'error': e})
        else:
            # Neither session, nor valid auth parameters provided
            raise exc.AmbiguousAuthSystem(exception_msg)

    # Always pass the session
    kwargs['session'] = session

    return Client(api_version, endpoint, **kwargs)


def Client(version, *args, **kwargs):
    module = importutils.import_versioned_module('ironicclient',
                                                 version, 'client')
    client_class = getattr(module, 'Client')
    return client_class(*args, **kwargs)
