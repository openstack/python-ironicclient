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

from distutils.version import StrictVersion
import logging
import os
import re
import socket
import ssl
import textwrap
import time

from keystoneauth1 import adapter
from keystoneauth1 import exceptions as kexc
from oslo_serialization import jsonutils
import six
from six.moves import http_client
import six.moves.urllib.parse as urlparse

from ironicclient.common import filecache
from ironicclient.common.i18n import _
from ironicclient import exc


# NOTE(deva): Record the latest version that this client was tested with.
#             We still have a lot of work to do in the client to implement
#             microversion support in the client properly! See
#             http://specs.openstack.org/openstack/ironic-specs/specs/kilo/api-microversions.html # noqa
#             for full details.
DEFAULT_VER = '1.9'
LAST_KNOWN_API_VERSION = 58
LATEST_VERSION = '1.{}'.format(LAST_KNOWN_API_VERSION)

LOG = logging.getLogger(__name__)
USER_AGENT = 'python-ironicclient'
CHUNKSIZE = 1024 * 64  # 64kB

_MAJOR_VERSION = 1
API_VERSION = '/v%d' % _MAJOR_VERSION
API_VERSION_SELECTED_STATES = ('user', 'negotiated', 'cached', 'default')


DEFAULT_MAX_RETRIES = 5
DEFAULT_RETRY_INTERVAL = 2
SENSITIVE_HEADERS = ('X-Auth-Token',)


SUPPORTED_ENDPOINT_SCHEME = ('http', 'https')

_API_VERSION_RE = re.compile(r'/+(v%d)?/*$' % _MAJOR_VERSION)


def _trim_endpoint_api_version(url):
    """Trim API version and trailing slash from endpoint."""
    return re.sub(_API_VERSION_RE, '', url)


def _extract_error_json(body):
    """Return  error_message from the HTTP response body."""
    try:
        body_json = jsonutils.loads(body)
    except ValueError:
        return {}

    if 'error_message' not in body_json:
        return {}

    try:
        error_json = jsonutils.loads(body_json['error_message'])
    except ValueError:
        return body_json

    err_msg = (error_json.get('faultstring') or error_json.get('description'))
    if err_msg:
        body_json['error_message'] = err_msg

    return body_json


def get_server(url):
    """Extract and return the server & port."""
    if url is None:
        return None, None
    parts = urlparse.urlparse(url)
    return parts.hostname, str(parts.port)


class VersionNegotiationMixin(object):
    def negotiate_version(self, conn, resp):
        """Negotiate the server version

        Assumption: Called after receiving a 406 error when doing a request.

        :param conn: A connection object
        :param resp: The response object from http request
        """
        def _query_server(conn):
            if (self.os_ironic_api_version and
                    not isinstance(self.os_ironic_api_version, list) and
                    self.os_ironic_api_version != 'latest'):
                base_version = ("/v%s" %
                                str(self.os_ironic_api_version).split('.')[0])
            else:
                base_version = API_VERSION
            return self._make_simple_request(conn, 'GET', base_version)

        version_overridden = False

        if (resp and hasattr(resp, 'request') and
                hasattr(resp.request, 'headers')):
            orig_hdr = resp.request.headers
            # Get the version of the client's last request and fallback
            # to the default for things like unit tests to not cause
            # migraines.
            req_api_ver = orig_hdr.get('X-OpenStack-Ironic-API-Version',
                                       self.os_ironic_api_version)
        else:
            req_api_ver = self.os_ironic_api_version
        if (resp and req_api_ver != self.os_ironic_api_version and
                self.api_version_select_state == 'negotiated'):
            # If we have a non-standard api version on the request,
            # but we think we've negotiated, then the call was overridden.
            # We should report the error with the called version
            requested_version = req_api_ver
            # And then we shouldn't save the newly negotiated
            # version of this negotiation because we have been
            # overridden a request.
            version_overridden = True
        else:
            requested_version = self.os_ironic_api_version

        if not resp:
            resp = _query_server(conn)
        if self.api_version_select_state not in API_VERSION_SELECTED_STATES:
            raise RuntimeError(
                _('Error: self.api_version_select_state should be one of the '
                  'values in: "%(valid)s" but had the value: "%(value)s"') %
                {'valid': ', '.join(API_VERSION_SELECTED_STATES),
                 'value': self.api_version_select_state})
        min_ver, max_ver = self._parse_version_headers(resp)
        # NOTE: servers before commit 32fb6e99 did not return version headers
        # on error, so we need to perform a GET to determine
        # the supported version range
        if not max_ver:
            LOG.debug('No version header in response, requesting from server')
            resp = _query_server(conn)
            min_ver, max_ver = self._parse_version_headers(resp)
        # Reset the maximum version that we permit
        if StrictVersion(max_ver) > StrictVersion(LATEST_VERSION):
            LOG.debug("Remote API version %(max_ver)s is greater than the "
                      "version supported by ironicclient. Maximum available "
                      "version is %(client_ver)s",
                      {'max_ver': max_ver,
                       'client_ver': LATEST_VERSION})
            max_ver = LATEST_VERSION

        # If the user requested an explicit version or we have negotiated a
        # version and still failing then error now.  The server could
        # support the version requested but the requested operation may not
        # be supported by the requested version.
        # TODO(TheJulia): We should break this method into several parts,
        # such as a sanity check/error method.
        if ((self.api_version_select_state == 'user' and
                not self._must_negotiate_version()) or
                (self.api_version_select_state == 'negotiated' and
                    version_overridden)):
            raise exc.UnsupportedVersion(textwrap.fill(
                _("Requested API version %(req)s is not supported by the "
                  "server, client, or the requested operation is not "
                  "supported by the requested version. "
                  "Supported version range is %(min)s to "
                  "%(max)s")
                % {'req': requested_version,
                   'min': min_ver, 'max': max_ver}))
        if (self.api_version_select_state == 'negotiated'):
            raise exc.UnsupportedVersion(textwrap.fill(
                _("No API version was specified or the requested operation "
                  "was not supported by the client's negotiated API version "
                  "%(req)s.  Supported version range is: %(min)s to %(max)s")
                % {'req': requested_version,
                   'min': min_ver, 'max': max_ver}))

        if isinstance(requested_version, six.string_types):
            if requested_version == 'latest':
                negotiated_ver = max_ver
            else:
                negotiated_ver = str(
                    min(StrictVersion(requested_version),
                        StrictVersion(max_ver)))

        elif isinstance(requested_version, list):
            if 'latest' in requested_version:
                raise ValueError(textwrap.fill(
                    _("The 'latest' API version can not be requested "
                      "in a list of versions. Please explicitly request "
                      "'latest' or request only versios between "
                      "%(min)s to %(max)s")
                    % {'min': min_ver, 'max': max_ver}))

            versions = []
            for version in requested_version:
                if min_ver <= StrictVersion(version) <= max_ver:
                    versions.append(StrictVersion(version))
            if versions:
                negotiated_ver = str(max(versions))
            else:
                raise exc.UnsupportedVersion(textwrap.fill(
                    _("Requested API version specified and the requested "
                      "operation was not supported by the client's "
                      "requested API version %(req)s.  Supported "
                      "version range is: %(min)s to %(max)s")
                    % {'req': requested_version,
                       'min': min_ver, 'max': max_ver}))

        else:
            raise ValueError(textwrap.fill(
                _("Requested API version %(req)s type is unsupported. "
                  "Valid types are Strings such as '1.1', 'latest' "
                  "or a list of string values representing API versions.")
                % {'req': requested_version}))

        if StrictVersion(negotiated_ver) < StrictVersion(min_ver):
            negotiated_ver = min_ver
        # server handles microversions, but doesn't support
        # the requested version, so try a negotiated version
        self.api_version_select_state = 'negotiated'
        self.os_ironic_api_version = negotiated_ver
        LOG.debug('Negotiated API version is %s', negotiated_ver)

        # Cache the negotiated version for this server
        endpoint_override = getattr(self, 'endpoint_override', None)
        host, port = get_server(endpoint_override)
        filecache.save_data(host=host, port=port, data=negotiated_ver)

        return negotiated_ver

    def _generic_parse_version_headers(self, accessor_func):
        min_ver = accessor_func('X-OpenStack-Ironic-API-Minimum-Version',
                                None)
        max_ver = accessor_func('X-OpenStack-Ironic-API-Maximum-Version',
                                None)
        return min_ver, max_ver

    def _parse_version_headers(self, accessor_func):
        # NOTE(jlvillal): Declared for unit testing purposes
        raise NotImplementedError()

    def _make_simple_request(self, conn, method, url):
        # NOTE(jlvillal): Declared for unit testing purposes
        raise NotImplementedError()

    def _must_negotiate_version(self):
        return (self.api_version_select_state == 'user' and
                (self.os_ironic_api_version == 'latest' or
                 isinstance(self.os_ironic_api_version, list)))

_RETRY_EXCEPTIONS = (exc.Conflict, exc.ServiceUnavailable,
                     exc.ConnectionRefused, kexc.RetriableConnectionFailure)


def with_retries(func):
    """Wrapper for _http_request adding support for retries."""
    @six.wraps(func)
    def wrapper(self, url, method, **kwargs):
        if self.conflict_max_retries is None:
            self.conflict_max_retries = DEFAULT_MAX_RETRIES
        if self.conflict_retry_interval is None:
            self.conflict_retry_interval = DEFAULT_RETRY_INTERVAL

        num_attempts = self.conflict_max_retries + 1
        for attempt in range(1, num_attempts + 1):
            try:
                return func(self, url, method, **kwargs)
            except _RETRY_EXCEPTIONS as error:
                msg = ("Error contacting Ironic server: %(error)s. "
                       "Attempt %(attempt)d of %(total)d" %
                       {'attempt': attempt,
                        'total': num_attempts,
                        'error': error})
                if attempt == num_attempts:
                    LOG.error(msg)
                    raise
                else:
                    LOG.debug(msg)
                    time.sleep(self.conflict_retry_interval)

    return wrapper


class VerifiedHTTPSConnection(six.moves.http_client.HTTPSConnection):
    """httplib-compatible connection using client-side SSL authentication

    :see http://code.activestate.com/recipes/
            577548-https-httplib-client-connection-with-certificate-v/
    """

    def __init__(self, host, port, key_file=None, cert_file=None,
                 ca_file=None, timeout=None, insecure=False):
        six.moves.http_client.HTTPSConnection.__init__(self, host, port,
                                                       key_file=key_file,
                                                       cert_file=cert_file)
        self.key_file = key_file
        self.cert_file = cert_file
        if ca_file is not None:
            self.ca_file = ca_file
        else:
            self.ca_file = self.get_system_ca_file()
        self.timeout = timeout
        self.insecure = insecure

    def connect(self):
        """Connect to a host on a given (SSL) port.

        If ca_file is pointing somewhere, use it to check Server Certificate.

        Redefined/copied and extended from httplib.py:1105 (Python 2.6.x).
        This is needed to pass cert_reqs=ssl.CERT_REQUIRED as parameter to
        ssl.wrap_socket(), which forces SSL to check server certificate against
        our client certificate.
        """
        sock = socket.create_connection((self.host, self.port), self.timeout)

        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        if self.insecure is True:
            kwargs = {'cert_reqs': ssl.CERT_NONE}
        else:
            kwargs = {'cert_reqs': ssl.CERT_REQUIRED, 'ca_certs': self.ca_file}

        if self.cert_file:
            kwargs['certfile'] = self.cert_file
            if self.key_file:
                kwargs['keyfile'] = self.key_file

        self.sock = ssl.wrap_socket(sock, **kwargs)

    @staticmethod
    def get_system_ca_file():
        """Return path to system default CA file."""
        # Standard CA file locations for Debian/Ubuntu, RedHat/Fedora,
        # Suse, FreeBSD/OpenBSD
        ca_path = ['/etc/ssl/certs/ca-certificates.crt',
                   '/etc/pki/tls/certs/ca-bundle.crt',
                   '/etc/ssl/ca-bundle.pem',
                   '/etc/ssl/cert.pem']
        for ca in ca_path:
            if os.path.exists(ca):
                return ca
        return None


class SessionClient(VersionNegotiationMixin, adapter.LegacyJsonAdapter):
    """HTTP client based on Keystone client session."""

    def __init__(self,
                 os_ironic_api_version,
                 api_version_select_state,
                 max_retries,
                 retry_interval,
                 **kwargs):
        self.os_ironic_api_version = os_ironic_api_version
        self.api_version_select_state = api_version_select_state
        self.conflict_max_retries = max_retries
        self.conflict_retry_interval = retry_interval
        if isinstance(kwargs.get('endpoint_override'), six.string_types):
            kwargs['endpoint_override'] = _trim_endpoint_api_version(
                kwargs['endpoint_override'])

        super(SessionClient, self).__init__(**kwargs)

        endpoint_filter = self._get_endpoint_filter()
        endpoint = self.get_endpoint(**endpoint_filter)
        if endpoint is None:
            raise exc.EndpointNotFound(
                _('The Bare Metal API endpoint cannot be detected and was '
                  'not provided explicitly'))
        self.endpoint_trimmed = _trim_endpoint_api_version(endpoint)

    def _parse_version_headers(self, resp):
        return self._generic_parse_version_headers(resp.headers.get)

    def _get_endpoint_filter(self):
        return {
            'interface': self.interface,
            'service_type': self.service_type,
            'region_name': self.region_name
        }

    def _make_simple_request(self, conn, method, url):
        # NOTE: conn is self.session for this class
        return conn.request(url, method, raise_exc=False,
                            user_agent=USER_AGENT,
                            endpoint_filter=self._get_endpoint_filter(),
                            endpoint_override=self.endpoint_override)

    @with_retries
    def _http_request(self, url, method, **kwargs):

        # NOTE(TheJulia): self.os_ironic_api_version is reset in
        # the self.negotiate_version() call if negotiation occurs.
        if self.os_ironic_api_version and self._must_negotiate_version():
            self.negotiate_version(self.session, None)

        kwargs.setdefault('user_agent', USER_AGENT)
        kwargs.setdefault('auth', self.auth)
        if isinstance(self.endpoint_override, six.string_types):
            kwargs.setdefault('endpoint_override', self.endpoint_override)

        if getattr(self, 'os_ironic_api_version', None):
            kwargs['headers'].setdefault('X-OpenStack-Ironic-API-Version',
                                         self.os_ironic_api_version)

        endpoint_filter = kwargs.setdefault('endpoint_filter', {})
        endpoint_filter.setdefault('interface', self.interface)
        endpoint_filter.setdefault('service_type', self.service_type)
        endpoint_filter.setdefault('region_name', self.region_name)

        resp = self.session.request(url, method,
                                    raise_exc=False, **kwargs)
        if resp.status_code == http_client.NOT_ACCEPTABLE:
            negotiated_ver = self.negotiate_version(self.session, resp)
            kwargs['headers']['X-OpenStack-Ironic-API-Version'] = (
                negotiated_ver)
            return self._http_request(url, method, **kwargs)
        if resp.status_code >= http_client.BAD_REQUEST:
            error_json = _extract_error_json(resp.content)
            raise exc.from_response(resp, error_json.get('error_message'),
                                    error_json.get('debuginfo'), method, url)
        elif resp.status_code in (http_client.MOVED_PERMANENTLY,
                                  http_client.FOUND, http_client.USE_PROXY):
            # Redirected. Reissue the request to the new location.
            location = resp.headers.get('location')
            resp = self._http_request(location, method, **kwargs)
        elif resp.status_code == http_client.MULTIPLE_CHOICES:
            raise exc.from_response(resp, method=method, url=url)
        return resp

    def json_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', 'application/json')
        kwargs['headers'].setdefault('Accept', 'application/json')

        if 'body' in kwargs:
            kwargs['data'] = jsonutils.dump_as_bytes(kwargs.pop('body'))

        resp = self._http_request(url, method, **kwargs)
        body = resp.content
        content_type = resp.headers.get('content-type', None)
        status = resp.status_code
        if (status in (http_client.NO_CONTENT, http_client.RESET_CONTENT) or
                content_type is None):
            return resp, list()
        if 'application/json' in content_type:
            try:
                body = resp.json()
            except ValueError:
                LOG.error('Could not decode response body as JSON')
        else:
            body = None

        return resp, body

    def raw_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type',
                                     'application/octet-stream')
        return self._http_request(url, method, **kwargs)


def _construct_http_client(session,
                           token=None,
                           auth_ref=None,
                           os_ironic_api_version=DEFAULT_VER,
                           api_version_select_state='default',
                           max_retries=DEFAULT_MAX_RETRIES,
                           retry_interval=DEFAULT_RETRY_INTERVAL,
                           timeout=600,
                           ca_file=None,
                           cert_file=None,
                           key_file=None,
                           insecure=None,
                           **kwargs):

    kwargs.setdefault('service_type', 'baremetal')
    kwargs.setdefault('user_agent', 'python-ironicclient')
    kwargs.setdefault('interface', kwargs.pop('endpoint_type',
                                              'publicURL'))

    ignored = {'token': token,
               'auth_ref': auth_ref,
               'timeout': timeout != 600,
               'ca_file': ca_file,
               'cert_file': cert_file,
               'key_file': key_file,
               'insecure': insecure}

    dvars = [k for k, v in ignored.items() if v]

    if dvars:
        LOG.warning('The following arguments are ignored when using '
                    'the session to construct a client: %s',
                    ', '.join(dvars))

    return SessionClient(session=session,
                         os_ironic_api_version=os_ironic_api_version,
                         api_version_select_state=api_version_select_state,
                         max_retries=max_retries,
                         retry_interval=retry_interval,
                         **kwargs)
