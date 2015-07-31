Trigger
=======

The Trigger role allows Ansible to connect to network devices using the Trigger framework.

http://trigger.readthedocs.org/en/latest/

Requirements
------------

This role requires that Trigger be installed on the same machine with Ansible.

Role Variables
--------------

There are no role variables used.

Dependencies
------------

There are no role dependencies.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    ---
    - name: Show Version on routers
      hosts: routers
      connection: local
      gather_facts: no

      roles:
      - trigger
    
      - name: show version
        trigger_command:
          device={{inventory_hostname}}
          command="show version"
          username="bob"
          password="ih8p@sswds"
        register: show_version

      - name: Show Data
        debug: msg="{{ show_version.results }}"

License
-------

BSD

Author Information
------------------

Mike Biancaniello (@chepazzo)
