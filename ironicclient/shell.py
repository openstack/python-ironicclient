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
import sys

from cliff import app
from cliff import commandmanager
try:
    import ironic_inspector_client
except ImportError:
    ironic_inspector_client = None
import openstack
from openstack import config as os_config
from osc_lib import utils
import pbr.version

from ironicclient.common import http
from ironicclient.common.i18n import _
from ironicclient import exc
from ironicclient.v1 import client


_DEFAULTS = {
    'auth_type': 'none',
}
_TYPE = 'baremetal'
_INSPECTOR_TYPE = 'baremetal-introspection'
_DESCRIPTION = 'Bare Metal service (ironic) client'
_NAMESPACE = 'openstack.baremetal.v1'
_INSPECTOR_NAMESPACE = 'openstack.baremetal_introspection.v1'
_HELP = _("%(err)s.\n* Use --os-endpoint for standalone %(project)s.\n"
          "* Use --os-auth-url and credentials for authentication.\n"
          "* Use --os-cloud to load configuration from clouds.yaml\n"
          "* See `%(cmd)s --help` for more details")

LOG = logging.getLogger(__name__)


class ClientManager(object):

    def __init__(self, cloud_region, options):
        self.cloud_region = cloud_region
        self.options = options
        self._ironic = None
        self._inspector = None

    @property
    def baremetal(self):
        if self._ironic is None:
            self._ironic = self._create_ironic_client()
        return self._ironic

    @property
    def baremetal_introspection(self):
        if self._inspector is None:
            self._inspector = self._create_inspector_client()
        return self._inspector

    def _create_ironic_client(self):
        api_version = self.options.os_baremetal_api_version
        allow_api_version_downgrade = False
        if not api_version:
            api_version = self.cloud_region.get_default_microversion(_TYPE)
            if not api_version:
                api_version = http.LATEST_VERSION
                allow_api_version_downgrade = True
        LOG.debug(
            'Using bare metal API version %s, downgrade %s', api_version,
            'allowed' if allow_api_version_downgrade else 'disallowed')

        # NOTE(dtantsur): endpoint_override is required to respect settings in
        # clouds.yaml, such as baremetal_endpoint_override.
        endpoint_override = self.cloud_region.get_endpoint(_TYPE)
        try:
            return client.Client(
                os_ironic_api_version=api_version,
                allow_api_version_downgrade=allow_api_version_downgrade,
                session=self.cloud_region.get_session(),
                region_name=self.cloud_region.get_region_name(_TYPE),
                endpoint_override=endpoint_override,
                max_retries=self.options.max_retries,
                retry_interval=self.options.retry_interval,
            )
        except exc.EndpointNotFound as e:
            # Re-raise with a more obvious message.
            raise exc.EndpointNotFound(_HELP % {'err': e, 'cmd': sys.argv[0],
                                                'project': 'ironic'})

    def _create_inspector_client(self):
        assert ironic_inspector_client is not None, \
            'BUG: _create_inspector_client called without inspector client'
        # NOTE(dtantsur): endpoint_override is required to respect settings in
        # clouds.yaml, such as baremetal_introspection_endpoint_override.
        endpoint_override = self.cloud_region.get_endpoint(_INSPECTOR_TYPE)
        try:
            return ironic_inspector_client.ClientV1(
                inspector_url=endpoint_override,
                session=self.cloud_region.get_session(),
                region_name=self.cloud_region.get_region_name(_INSPECTOR_TYPE),
            )
        except ironic_inspector_client.EndpointNotFound as e:
            # Re-raise with a more obvious message.
            raise exc.EndpointNotFound(_HELP % {'err': e, 'cmd': sys.argv[0],
                                                'project': 'ironic-inspector'})


class CommandManager(commandmanager.CommandManager):

    def load_commands(self, namespace):
        super(CommandManager, self).load_commands(namespace)
        if ironic_inspector_client is not None:
            super(CommandManager, self).load_commands(_INSPECTOR_NAMESPACE)
        # Strip the 'baremetal' prefix used in OSC
        prefix = 'baremetal '
        prefix_len = len(prefix)
        self.commands = dict(
            (cmd[prefix_len:] if cmd.startswith(prefix) else cmd, ep)
            for (cmd, ep) in self.commands.items()
        )


class App(app.App):

    def __init__(self):
        version_info = pbr.version.VersionInfo('python-ironicclient')
        mgr = CommandManager(_NAMESPACE)
        self.config = os_config.OpenStackConfig(override_defaults=_DEFAULTS)
        super(App, self).__init__(description=_DESCRIPTION,
                                  version=str(version_info),
                                  command_manager=mgr,
                                  deferred_help=True)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(App, self).build_option_parser(
            description, version, argparse_kwargs=argparse_kwargs)
        self.config.register_argparse_arguments(parser, sys.argv[1:])

        parser.add_argument(
            '--os-baremetal-api-version',
            metavar='<baremetal-api-version>',
            default=utils.env('OS_BAREMETAL_API_VERSION'),
            help='Bare metal API version, default="latest" (the maximum '
                 'version supported by both the client and the server). '
                 '(Env: OS_BAREMETAL_API_VERSION)',
        )
        parser.add_argument(
            '--max-retries',
            metavar='<max-retries-number>',
            default=http.DEFAULT_MAX_RETRIES,
            type=int,
            help='Maximum number of retries on connection problems and '
                 'resource state conflicts'
        )
        parser.add_argument(
            '--retry-interval',
            metavar='<retry-interval-seconds>',
            default=http.DEFAULT_RETRY_INTERVAL,
            type=int,
            help='Interval in seconds between two retries'
        )
        return parser

    # This is the openstacksdk default value
    _STREAM_FORMAT = '%(asctime)s %(levelname)s: %(name)s %(message)s'

    def _configure_ironic_logging(self):
        debug_enabled = self.options.debug or self.options.verbose_level > 1

        openstack.enable_logging(debug=debug_enabled, stream=sys.stderr,
                                 format_template=self._STREAM_FORMAT,
                                 # No fancy formatting if debug is off
                                 format_stream=debug_enabled)
        # NOTE(dtantsur): prevent openstack logging from appearing again in the
        # cliff handlers
        for name in ('openstack', 'keystoneauth'):
            logger = logging.getLogger(name)
            logger.propagate = False

        # NOTE(dtantsur): I wish logging.basicConfig worked, but at this point
        # cliff has already started configuring logging.
        for name in ('ironicclient', 'ironic_inspector_client'):
            logger = logging.getLogger(name)
            logger.setLevel(
                logging.DEBUG if debug_enabled else logging.WARNING)
            # warnings are already configured by cliff, only configure
            # debug logging for ironic.
            if not logger.handlers and debug_enabled:
                handler = logging.StreamHandler(stream=sys.stderr)
                handler.setFormatter(logging.Formatter(self._STREAM_FORMAT))
                logger.addHandler(handler)
                logger.propagate = False

    def initialize_app(self, argv):
        super(App, self).initialize_app(argv)
        self._configure_ironic_logging()
        self.cloud_region = self.config.get_one(argparse=self.options)
        # Compatibility with OSC
        self.client_manager = ClientManager(self.cloud_region, self.options)


def main(argv=sys.argv[1:]):
    return App().run(argv)
