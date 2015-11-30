#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Trigger
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of ansible-trigger nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


DOCUMENTATION = """
---
module: trigger_command
short_description: Sends arbitrary commands to devices via the Trigger framework
description:
  - The trigger_command module provides a module for sending arbitray
    commands to a network node and returns the ouput. 
  - Trigger is a toolkit used to connect to network devices. While Trigger can utilize a device's API, its main use with Ansible would be to interface with devices for which the only connection methods are telnet or ssh.
  - You can install trigger through pip or follow on github (http://github.com/trigger).
  - Read the docs: http://triggerproject.org/en/latest/
version_added: "1.9"
category: network
author: Mike Biancaniello (@chepazzo)
requirements:
  - trigger>=1.5.2
notes:
  - This module does not support idempotent operations.
  - This module does not support stateful configuration
options:
  command:
    description:
      - Specifies the command to execute on the node.
    required: true
  device:
    description:
      - Specifies the devicename on which to execute the commands.
    required: true
  username:
    description:
      - Specify the username. If omitted, Trigger will try to figure it out.
    required: false
    default: null
  password:
    description:
      - Specify the password. If omitted, Trigger will try to figure it out.
    required: false
    default: null
"""

EXAMPLES = """

  - name: show version
    trigger_command:
      device={{inventory_hostname}}
      command="show version"
      username="bob"
      password="ih8p@sswds"
    register: trigger_show_version

"""

try:
    from trigger.cmds import Commando
    TRIGGER_AVAILABLE = True
except ImportError:
    TRIGGER_AVAILABLE = False

TIMEOUT = 30
VERBOSE = True
DEBUG = True
## Whether or not to restrict devices to production.
## See Trigger documentation for netdevices.
PROD_ONLY = False
## Whether or not to force using the cli for Juniper devices.
## If False, then you have to write a handler to parse the xml output.
FORCE_CLI = True

class Do(Commando):
    '''
    A Commando subclass to instantiate the command(s) to be run.

    Args:
      commands (list): A list of commands (str) to be run on specified devices.
      devices (list): A list of devices on which to run specified commands.
      creds (Optional(tuple)): A tuple containing (username,password) for authenticating
        on the devices.
        | If omitted, Trigger will try to figure it out
        | See Trigger documentation for netdevices.
        | Default is None.
      timeout (Optional[int]): Timeout (in sec) to wait for a response from the device.
        | Default is 30.

    '''
    def __init__(self, commands=None, debug=False, timeout=TIMEOUT, **args):
        if commands is None:
            commands = []
        #print "\n\nDEBUG: "+str(debug)
        self.commands = commands
        self.data = {}
        self.debug = debug
        if 'args' in locals():
            args['timeout'] = timeout
        else:
            args = dict(timeout=timeout)
        Commando.__init__(self, **args)

def send_command(d,c,creds):
    '''
    Sends a command to a device.

    Args:
      d (str): Name of device on which to run specified command.
      c (str): Command to run on specified device.
      creds (tuple): A tuple containing (username,password) for authenticating
        on the devices.

    Returns:
        str: Text output from device.
    '''
    try:
        n = Do(devices=[d], commands=[c], creds=creds, verbose=VERBOSE, debug=DEBUG, timeout=TIMEOUT, production_only=PROD_ONLY,force_cli=FORCE_CLI)
    except Exception:
        return None
    ## run() will send the commands to the device.
    n.run()
    data = n.results[d]
    return data

def module_main(module):
    '''
    Main Ansible module function.
    This just does Ansible stuff like collect/format args and set 
    value of changed attribute.
    '''
    d = module.params['device']
    c = module.params['command']
    creds = None
    if 'username' in module.params and 'password' in module.params:
        u = module.params['username']
        p = module.params['password']
        creds = (u,p)
    data = send_command(d,c,creds)
    if data is None:
        module.fail_json(msg='Command failed.')
        return False
    module.exit_json(results=data)

def main():
    '''
    Main function for python module.
    '''
    argument_spec = dict(
        device=dict(required=True),
        command=dict(required=True),
        username=dict(required=False, default=None),
        password=dict(required=False, default=None)
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )
    if not TRIGGER_AVAILABLE:
        module.fail_json(msg='trigger is required for this module. Install from pip: pip install trigger.')
    module_main(module)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

