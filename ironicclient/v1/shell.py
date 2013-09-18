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

from ironicclient.common import utils
from ironicclient import exc


@utils.arg('chassis', metavar='<chassis>', help="ID of chassis")
def do_chassis_show(self, args):
    """Show a chassis."""
    try:
        chassis = self.chassis.get(args.chassis)
    except exc.HTTPNotFound:
        raise exc.CommandError('Chassis not found: %s' % args.chassis)
    else:
        fields = ['uuid', 'description', 'extra']
        data = dict([(f, getattr(chassis, f, '')) for f in fields])
        utils.print_dict(data, wrap=72)
