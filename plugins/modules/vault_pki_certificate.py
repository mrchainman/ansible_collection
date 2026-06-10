#!/usr/bin/python

from hvac.api.secrets_engines.pki import DEFAULT_MOUNT_POINT
from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_module import HashiVaultModule

from ..module_utils.utils import get_client, list_certificates

# If state=created or state=present and does not exist, the output will be
# certificate {ca_chain, certificate, expiration, issuing_ca, private_key, private_key_type, serial_number}


def main():
    argspec = HashiVaultModule.generate_argspec(
        state=dict(type='str',
                   choices=['present', 'created', 'revoked'],
                   default='present'),
        mount_point=dict(type='str', default=DEFAULT_MOUNT_POINT),
        role_name=dict(type='str', required=True),
        common_name=dict(type='str', required=True),
        alt_names=dict(type='list', elements='str', default=[]),
        ip_sans=dict(type='list', elements='str', default=[]),
        uri_sans=dict(type='list', elements='str', default=[]),
        other_sans=dict(type='list', elements='str', default=[]),
        ttl=dict(type='str', default=None),
        format=dict(type='str',
                    choices=['pem', 'der', 'pem_bundle'],
                    default='pem'),
        private_key_format=dict(type='str',
                                choices=['der', 'pkcs8'],
                                default='der'),
        exclude_cn_from_sans=dict(type='bool', default=False),
    )

    module = HashiVaultModule(
        argument_spec=argspec,
        supports_check_mode=True
    )

    state = module.params['state']
    mount_point = module.params['mount_point']
    role_name = module.params['role_name']
    common_name = module.params['common_name']
    alt_names = module.params['alt_names']
    ip_sans = module.params['ip_sans']
    uri_sans = module.params['uri_sans']
    other_sans = module.params['other_sans']
    ttl = module.params['ttl']
    format_ = module.params['format']
    private_key_format = module.params['private_key_format']
    exclude_cn_from_sans = module.params['exclude_cn_from_sans']

    client = get_client(module)
    certificates = list_certificates(client, mount_point, common_name)

    if state == 'revoked':
        changed = False
        for certificate in certificates:
            client.write(f'{mount_point}/revoke',
                         serial_number=certificate['serial_number'])
            changed = True
        module.exit_json(changed=changed)

    if state == 'present' and certificates:
        module.exit_json(changed=False)

    response = client.write(f'{mount_point}/issue/{role_name}',
        common_name=common_name,
        alt_names=','.join(alt_names),
        ip_sans=','.join(ip_sans),
        uri_sans=','.join(uri_sans),
        other_sans=','.join(other_sans),
        ttl=ttl,
        format_=format_,
        private_key_format=private_key_format,
        exclude_cn_from_sans=exclude_cn_from_sans)
    module.exit_json(changed=True, certificate=response['data'])


if __name__ == '__main__':
    main()
