#!/usr/bin/python

from hvac.api.secrets_engines.pki import DEFAULT_MOUNT_POINT
from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_module import HashiVaultModule

from ..module_utils.utils import get_client, get_issuer


def main():
    argspec = HashiVaultModule.generate_argspec(
        state=dict(type='str',
                   choices=['present', 'absent'],
                   default='present'),
        type=dict(type='str',
                  choices=['internal', 'exported'],
                  default='internal'),
        mount_point=dict(type='str', default=DEFAULT_MOUNT_POINT),
        common_name=dict(type='str', required=True),
        ttl=dict(type='str'),
    )

    module = HashiVaultModule(
        argument_spec=argspec,
        supports_check_mode=True
    )

    state = module.params['state']
    type_ = module.params['type']
    mount_point = module.params['mount_point']
    common_name = module.params['common_name']
    ttl = module.params['ttl']

    client = get_client(module)
    issuer = get_issuer(client, mount_point, common_name)

    if state == 'absent':
        if issuer:
            client.delete(f'{mount_point}/issuer/{issuer["issuer_id"]}')
            client.delete(f'{mount_point}/key/{issuer["key_id"]}')
            module.exit_json(changed=True)
        module.exit_json(changed=False)

    if state == 'present' and issuer:
        module.exit_json(changed=False, issuer=issuer)

    extra_params = {}
    if ttl:
        extra_params['ttl'] = ttl
    response = client.secrets.pki.generate_root(type=type_,
                                                common_name=common_name,
                                                extra_params=extra_params,
                                                mount_point=mount_point)
    issuer = {'issuer_id': response['data']['issuer_id'],
              'issuer_name': response['data']['issuer_name'],
              'common_name': common_name,
              'key_id': response['data']['key_id'],
              'certificate': response['data']['certificate']}

    module.exit_json(changed=True, issuer=issuer)


if __name__ == '__main__':
    main()
