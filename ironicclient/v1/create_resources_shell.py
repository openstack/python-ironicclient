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

from ironicclient.common import cliutils
from ironicclient.v1 import create_resources


@cliutils.arg('resource_files', nargs='+', metavar='<file>', default=[],
              help='File (.yaml or .json) containing descriptions of the '
                   'resources to create. Can be specified multiple times.')
def do_create(cc, args):
    """Create baremetal resources (chassis, nodes, port groups and ports).

    The resources may be described in one or more JSON or YAML files. If any
    file cannot be validated, no resources are created. An attempt is made to
    create all the resources; those that could not be created are skipped
    (with a corresponding error message).
    """
    create_resources.create_resources(cc, args.resource_files)
