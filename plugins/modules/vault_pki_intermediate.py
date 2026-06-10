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
        mount_point=dict(type='str', default='pki_int'),
        root_mount_point=dict(type='str', default=DEFAULT_MOUNT_POINT),
        common_name=dict(type='str', required=True),
        format=dict(type='str',
                    choices=['pem', 'der', 'pem_bundle'],
                    default='pem'),
        ttl=dict(type='str'),
    )

    module = HashiVaultModule(
        argument_spec=argspec,
        supports_check_mode=True
    )

    state = module.params['state']
    type_ = module.params['type']
    mount_point = module.params['mount_point']
    root_mount_point = module.params['root_mount_point']
    common_name = module.params['common_name']
    format_ = module.params['format']
    ttl = module.params['ttl']

    client = get_client(module)
    issuer = get_issuer(client, mount_point, common_name)

    if state == 'absent':
        if issuer:
            client.delete(f'{mount_point}/issuer/{issuer["issuer_id"]}')
            client.delete(f'{mount_point}/key/{issuer["key_id"]}')
            module.exit_json(changed=True)
        module.exit_json(changed=False, issuer=issuer)

    if state == 'present' and issuer:
        module.exit_json(changed=False, issuer=issuer)

    response = client.secrets.pki.generate_intermediate(
        type=type_,
        common_name=common_name,
        mount_point=mount_point)

    key_id = response['data']['key_id']

    extra_params = {'ttl': ttl, 'format': format_}
    extra_params = {k: v for k, v in extra_params.items() if v is not None}
    response = client.secrets.pki.sign_intermediate(
        csr=response['data']['csr'],
        common_name=common_name,
        mount_point=root_mount_point,
        extra_params=extra_params)

    certificate = response['data']['certificate']

    response = client.secrets.pki.set_signed_intermediate(
        mount_point=mount_point,
        certificate=certificate)

    issuer_id = response['data']['imported_issuers'][0]

    issuer = {'issuer_id': issuer_id,
              'issuer_name': '',
              'common_name': common_name,
              'key_id': key_id,
              'certificate': certificate}

    module.exit_json(changed=True, issuer=issuer)


if __name__ == '__main__':
    main()
