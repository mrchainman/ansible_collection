#!/usr/bin/python

import os

import hcl
from hvac.api.secrets_engines.pki import DEFAULT_MOUNT_POINT
from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_module import HashiVaultModule

from ..module_utils.utils import get_client, parse_ttl, is_params_subset


def main():
    argspec = HashiVaultModule.generate_argspec(
        state=dict(type='str',
                   choices=['present', 'absent'],
                   default='present'),
        name=dict(type='str', required=True),
        policy=dict(type='path'),
    )

    module = HashiVaultModule(
        argument_spec=argspec,
        supports_check_mode=True
    )

    state = module.params['state']
    name = module.params['name']
    policy_path = module.params['policy']

    if state == 'present':
        if not policy_path:
            module.fail_json(msg='Policy required when state is "present"')
        if not os.path.exists(policy_path):
            module.fail_json(msg=f'Policy {policy_path} not found')

    client = get_client(module)

    if name in client.sys.policy.list_policies()['data']['keys']:
        cur_policy_raw = client.sys.policy.read_policy(name)['data']['rules']
        cur_policy = hcl.loads(cur_policy_raw)
    else:
        cur_policy = None

    if state == 'absent':
        if cur_policy:
            client.sys.policy.delete_policy(name)
        module.exit_json(changed=bool(cur_policy))

    with open(policy_path) as infile:
        new_policy_raw = infile.read()
    new_policy = hcl.loads(new_policy_raw)

    if cur_policy == new_policy:
        module.exit_json(changed=False, policy=cur_policy)

    client.sys.policy.create_or_update_policy(name, new_policy_raw)

    module.exit_json(changed=True, policy=new_policy)


if __name__ == '__main__':
    main()
