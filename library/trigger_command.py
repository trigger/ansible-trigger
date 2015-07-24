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
version_added: 0.0.0
category: System
author: Mike Biancaniello (@chepazzo)
requirements:
  - trigger>=1.5.2
notes:
  - This module does not support idempotent operations.
  - This module does not support stateful configuration
options:
  command:
    description:
      - Specifies the command to send to the node and execute
        in the configured mode.
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
    register: trigger

"""

try:
    from trigger.cmds import Commando
    TRIGGER_AVAILABLE = True
except ImportError:
    TRIGGER_AVAILABLE = False

PROD_ONLY = False
TIMEOUT = 30
VERBOSE = True
DEBUG = True

class Do(Commando):
    def __init__(self, commands=[], debug=False, timeout=TIMEOUT, **args):
        '''
        adding files,debug to allowed arguments
        '''
        #print "\n\nDEBUG: "+str(debug)
        self.commands = commands
        self.data = {}
        self.debug = debug
        if 'args' in locals():
            args['timeout'] = timeout
        else:
            args = dict(timeout=timeout)
        Commando.__init__(self, **args)

def send_command(module):
    d = module.params['device']
    c = module.params['command']
    creds = None
    if 'username' in module.params and 'password' in module.params:
        u = module.params['username']
        p = module.params['password']
        creds = (u,p)
    try:
        n = Do(devices=[d], commands=[c], creds=creds, verbose=VERBOSE, debug=DEBUG, timeout=TIMEOUT, production_only=PROD_ONLY)
    except Exception:
        module.fail_json(msg=str(e))
        return False
    ## run() will send the commands to the device.
    n.run()
    data = n.results[d]
    module.exit_json(changed=True,changes=data)

def main():
    argument_spec = dict(
        device=dict(required=True),
        command=dict(required=True),
        username=dict(required=False, default=None),
        password=dict(required=False, default=None)
    )
    module = AnsibleModule(argument_spec=argument_spec)
    if not TRIGGER_AVAILABLE:
        module.fail_json(msg='trigger is required for this module. Install from pip: pip install trigger.')
    send_command(module)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

