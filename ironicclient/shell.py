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
Command-line interface to the OpenStack Bare Metal Provisioning API.
"""

from __future__ import print_function

import argparse
import getpass
import logging
import os
import pkgutil
import re
import sys

from keystoneauth1.loading import session as kasession
from oslo_utils import encodeutils
from oslo_utils import importutils
import six

import ironicclient
from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common import http
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient import exc


LAST_KNOWN_API_VERSION = 34
LATEST_VERSION = '1.{}'.format(LAST_KNOWN_API_VERSION)


class IronicShell(object):

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='ironic',
            description=__doc__.strip(),
            epilog=_('See "ironic help COMMAND" '
                     'for help on a specific command.'),
            add_help=False,
            formatter_class=HelpFormatter,
        )

        # Register global Keystone args first so their defaults are respected.
        # See https://bugs.launchpad.net/python-ironicclient/+bug/1463581
        kasession.register_argparse_arguments(parser)

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS,
                            )

        parser.add_argument('--version',
                            action='version',
                            version=ironicclient.__version__)

        parser.add_argument('--debug',
                            default=bool(cliutils.env('IRONICCLIENT_DEBUG')),
                            action='store_true',
                            help=_('Defaults to env[IRONICCLIENT_DEBUG]'))

        parser.add_argument('--json',
                            default=False,
                            action='store_true',
                            help=_('Print JSON response without formatting.'))

        parser.add_argument('-v', '--verbose',
                            default=False, action="store_true",
                            help=_('Print more verbose output'))

        # for backward compatibility only
        parser.add_argument('--cert-file',
                            dest='os_cert',
                            help=_('DEPRECATED! Use --os-cert.'))

        # for backward compatibility only
        parser.add_argument('--key-file',
                            dest='os_key',
                            help=_('DEPRECATED! Use --os-key.'))

        # for backward compatibility only
        parser.add_argument('--ca-file',
                            dest='os_cacert',
                            help=_('DEPRECATED! Use --os-cacert.'))

        parser.add_argument('--os-username',
                            dest='username',
                            default=cliutils.env('OS_USERNAME'),
                            help=_('Defaults to env[OS_USERNAME]'))

        parser.add_argument('--os_username',
                            dest='username',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-password',
                            dest='password',
                            default=cliutils.env('OS_PASSWORD'),
                            help=_('Defaults to env[OS_PASSWORD]'))

        parser.add_argument('--os_password',
                            dest='password',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-tenant-id',
                            dest='tenant_id',
                            default=cliutils.env('OS_TENANT_ID'),
                            help=_('Defaults to env[OS_TENANT_ID]'))

        parser.add_argument('--os_tenant_id',
                            dest='tenant_id',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-tenant-name',
                            dest='tenant_name',
                            default=cliutils.env('OS_TENANT_NAME'),
                            help=_('Defaults to env[OS_TENANT_NAME]'))

        parser.add_argument('--os_tenant_name',
                            dest='tenant_name',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-auth-url',
                            dest='auth_url',
                            default=cliutils.env('OS_AUTH_URL'),
                            help=_('Defaults to env[OS_AUTH_URL]'))

        parser.add_argument('--os_auth_url',
                            dest='auth_url',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-region-name',
                            dest='region_name',
                            default=cliutils.env('OS_REGION_NAME'),
                            help=_('Defaults to env[OS_REGION_NAME]'))

        parser.add_argument('--os_region_name',
                            dest='region_name',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-auth-token',
                            dest='token',
                            default=cliutils.env('OS_AUTH_TOKEN'),
                            help=_('Defaults to env[OS_AUTH_TOKEN]'))

        parser.add_argument('--os_auth_token',
                            dest='token',
                            help=argparse.SUPPRESS)

        parser.add_argument('--ironic-url',
                            dest='endpoint',
                            default=cliutils.env('IRONIC_URL'),
                            help=_('Defaults to env[IRONIC_URL]'))

        parser.add_argument('--ironic_url',
                            dest='endpoint',
                            help=argparse.SUPPRESS)

        parser.add_argument('--ironic-api-version',
                            default=cliutils.env('IRONIC_API_VERSION',
                                                 default="latest"),
                            help=_('Accepts 1.x (where "x" is microversion), '
                                   '1 or "latest". Defaults to '
                                   'env[IRONIC_API_VERSION] or "latest".'))

        parser.add_argument('--ironic_api_version',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-service-type',
                            dest='service_type',
                            default=cliutils.env('OS_SERVICE_TYPE'),
                            help=_('Defaults to env[OS_SERVICE_TYPE] or '
                                   '"baremetal"'))

        parser.add_argument('--os_service_type',
                            dest='service_type',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-endpoint',
                            dest='endpoint',
                            default=cliutils.env('OS_SERVICE_ENDPOINT'),
                            help=_('Specify an endpoint to use instead of '
                                   'retrieving one from the service catalog '
                                   '(via authentication). '
                                   'Defaults to env[OS_SERVICE_ENDPOINT].'))

        parser.add_argument('--os_endpoint',
                            dest='endpoint',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-endpoint-type',
                            dest='interface',
                            default=cliutils.env('OS_ENDPOINT_TYPE'),
                            help=_('Defaults to env[OS_ENDPOINT_TYPE] or '
                                   '"publicURL"'))

        parser.add_argument('--os_endpoint_type',
                            dest='interface',
                            help=argparse.SUPPRESS)

        parser.add_argument('--os-user-domain-id',
                            dest='user_domain_id',
                            default=cliutils.env('OS_USER_DOMAIN_ID'),
                            help=_('Defaults to env[OS_USER_DOMAIN_ID].'))

        parser.add_argument('--os-user-domain-name',
                            dest='user_domain_name',
                            default=cliutils.env('OS_USER_DOMAIN_NAME'),
                            help=_('Defaults to env[OS_USER_DOMAIN_NAME].'))

        parser.add_argument('--os-project-id',
                            dest='project_id',
                            default=cliutils.env('OS_PROJECT_ID'),
                            help=_('Another way to specify tenant ID. '
                                   'This option is mutually exclusive with '
                                   ' --os-tenant-id. '
                                   'Defaults to env[OS_PROJECT_ID].'))

        parser.add_argument('--os-project-name',
                            dest='project_name',
                            default=cliutils.env('OS_PROJECT_NAME'),
                            help=_('Another way to specify tenant name. '
                                   'This option is mutually exclusive with '
                                   ' --os-tenant-name. '
                                   'Defaults to env[OS_PROJECT_NAME].'))

        parser.add_argument('--os-project-domain-id',
                            dest='project_domain_id',
                            default=cliutils.env('OS_PROJECT_DOMAIN_ID'),
                            help=_('Defaults to env[OS_PROJECT_DOMAIN_ID].'))

        parser.add_argument('--os-project-domain-name',
                            dest='project_domain_name',
                            default=cliutils.env('OS_PROJECT_DOMAIN_NAME'),
                            help=_('Defaults to env[OS_PROJECT_DOMAIN_NAME].'))

        msg = _('Maximum number of retries in case of conflict error '
                '(HTTP 409). Defaults to env[IRONIC_MAX_RETRIES] or %d. '
                'Use 0 to disable retrying.') % http.DEFAULT_MAX_RETRIES
        parser.add_argument('--max-retries', type=int, help=msg,
                            default=cliutils.env(
                                'IRONIC_MAX_RETRIES',
                                default=str(http.DEFAULT_MAX_RETRIES)))

        msg = _('Amount of time (in seconds) between retries '
                'in case of conflict error (HTTP 409). '
                'Defaults to env[IRONIC_RETRY_INTERVAL] '
                'or %d.') % http.DEFAULT_RETRY_INTERVAL
        parser.add_argument('--retry-interval', type=int, help=msg,
                            default=cliutils.env(
                                'IRONIC_RETRY_INTERVAL',
                                default=str(http.DEFAULT_RETRY_INTERVAL)))

        return parser

    def get_available_major_versions(self):
        matcher = re.compile(r"^v[0-9]+$")
        submodules = pkgutil.iter_modules([os.path.dirname(__file__)])
        available_versions = [name[1:] for loader, name, ispkg in submodules
                              if matcher.search(name)]

        return available_versions

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>',
                                           dest='subparser_name')
        try:
            submodule = importutils.import_versioned_module('ironicclient',
                                                            version, 'shell')
        except ImportError as e:
            msg = _("Invalid client version '%(version)s'. "
                    "Major part must be one of: '%(major)s'") % {
                "version": version,
                "major": ", ".join(self.get_available_major_versions())}
            raise exceptions.UnsupportedVersion(
                _('%(message)s, error was: %(error)s') %
                {'message': msg, 'error': e})
        submodule.enhance_parser(parser, subparsers, self.subcommands)
        utils.define_commands_from_module(subparsers, self, self.subcommands)
        return parser

    def _setup_debugging(self, debug):
        if debug:
            logging.basicConfig(
                format="%(levelname)s (%(module)s:%(lineno)d) %(message)s",
                level=logging.DEBUG)
        else:
            logging.basicConfig(
                format="%(levelname)s %(message)s",
                level=logging.CRITICAL)

    def do_bash_completion(self):
        """Prints all of the commands and options for bash-completion."""
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        print(' '.join(commands | options))

    def _check_version(self, api_version):
        """Validate the supplied API (micro)version.

        :param api_version: API version as a string ("1", "1.x" or "latest")
        :returns: tuple (major version, version string)
        """
        if api_version in ('1', 'latest'):
            return (1, LATEST_VERSION)
        else:
            try:
                versions = tuple(int(i) for i in api_version.split('.'))
            except ValueError:
                versions = ()

            if not versions or len(versions) > 2:
                msg = _("The requested API version %(ver)s is an unexpected "
                        "format. Acceptable formats are 'X', 'X.Y', or the "
                        "literal string 'latest'."
                        ) % {'ver': api_version}
                raise exc.CommandError(msg)

            if versions == (1, 0):
                os_ironic_api_version = None
            else:
                os_ironic_api_version = api_version

            api_major_version = versions[0]
            return (api_major_version, os_ironic_api_version)

    def main(self, argv):
        # TODO(rloo): delete the ironic CLI in the S* cycle.
        print('The "ironic" CLI is deprecated and will be removed in the '
              'S* release. Please use the "openstack baremetal" CLI instead.',
              file=sys.stderr)
        # Parse args once to find version
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self._setup_debugging(options.debug)

        # build available subcommands based on version
        (api_major_version, os_ironic_api_version) = (
            self._check_version(options.ironic_api_version))

        subcommand_parser = self.get_subcommand_parser(api_major_version)
        self.parser = subcommand_parser

        # Handle top-level --help/-h before attempting to parse
        # a command off the command line
        if options.help or not argv:
            self.do_help(options)
            return 0

        # Parse args again and call whatever callback was selected
        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with these commands right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion()
            return 0

        # Assume password auth if it does not seem like none, admin_token or
        # token auth
        if not args.endpoint and not (args.token and args.auth_url):
            if not args.username:
                raise exc.CommandError(_("You must provide a username via "
                                         "either --os-username or via "
                                         "env[OS_USERNAME]"))

            if not args.password:
                # No password, If we've got a tty, try prompting for it
                if hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
                    # Check for Ctl-D
                    try:
                        args.password = getpass.getpass(
                            'OpenStack Password: ')
                    except EOFError:
                        pass
            # No password because we didn't have a tty or the
            # user Ctl-D when prompted.
            if not args.password:
                raise exc.CommandError(_("You must provide a password via "
                                         "either --os-password, "
                                         "env[OS_PASSWORD], "
                                         "or prompted response"))

            if not (args.tenant_id or args.tenant_name or
                    args.project_id or args.project_name):
                raise exc.CommandError(
                    _("You must provide a project name or"
                      " project id via --os-project-name, --os-project-id,"
                      " env[OS_PROJECT_ID] or env[OS_PROJECT_NAME]."))

            if not args.auth_url:
                raise exc.CommandError(_("You must provide an auth url via "
                                         "either --os-auth-url or via "
                                         "env[OS_AUTH_URL]"))

        if args.max_retries < 0:
            raise exc.CommandError(_("You must provide value >= 0 for "
                                     "--max-retries"))
        if args.retry_interval < 1:
            raise exc.CommandError(_("You must provide value >= 1 for "
                                     "--retry-interval"))
        client_args = (
            'token', 'endpoint', 'username', 'password', 'auth_url',
            'project_id', 'project_name', 'tenant_id', 'tenant_name',
            'region_name', 'user_domain_id', 'user_domain_name',
            'project_domain_id', 'project_domain_name', 'service_type',
            'interface', 'max_retries', 'retry_interval', 'timeout', 'insecure'
        )
        kwargs = {}
        for key in client_args:
            value = getattr(args, key)
            # NOTE(vdrok): check for both None and ''. If the default value
            # for option is set using cliutils.env function, default empty
            # value is ''. If the default is not set explicitly, it is None.
            if value not in (None, ''):
                kwargs[key] = value
        # NOTE(vdrok): this is to workaround the fact that these options are
        # named differently in keystoneauth, depending on whether they are
        # provided through CLI or loaded from conf options, here we unify them.
        for cli_ssl_opt, conf_ssl_opt in [
                ('os_cacert', 'cafile'), ('os_cert', 'certfile'),
                ('os_key', 'keyfile')]:
            value = getattr(args, cli_ssl_opt)
            if value not in (None, ''):
                kwargs[conf_ssl_opt] = value
        kwargs['os_ironic_api_version'] = os_ironic_api_version
        client = ironicclient.client.get_client(api_major_version, **kwargs)
        if options.ironic_api_version in ('1', 'latest'):
            # Allow negotiating a lower version, if the latest version
            # supported by the client is higher than the latest version
            # supported by the server.
            client.http_client.api_version_select_state = 'default'

        try:
            args.func(client, args)
        except exc.Unauthorized:
            raise exc.CommandError(_("Invalid OpenStack Identity credentials"))
        except exc.CommandError as e:
            subcommand_parser = self.subcommands[args.subparser_name]
            subcommand_parser.error(e)

    @cliutils.arg('command', metavar='<subcommand>', nargs='?',
                  help=_('Display help for <subcommand>'))
    def do_help(self, args):
        """Display help about this program or one of its subcommands."""
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError(_("'%s' is not a valid subcommand") %
                                       args.command)
        else:
            self.parser.print_help()


class HelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        super(HelpFormatter, self).start_section(heading.capitalize())


def main():
    try:
        IronicShell().main(sys.argv[1:])
    except KeyboardInterrupt:
        print(_("... terminating ironic client"), file=sys.stderr)
        return 130
    except Exception as e:
        print(encodeutils.safe_encode(six.text_type(e)), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
