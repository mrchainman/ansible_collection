#!/usr/bin/python

from hvac.api.secrets_engines.pki import DEFAULT_MOUNT_POINT
from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_module import HashiVaultModule

from ..module_utils.utils import get_client


def main():
    argspec = HashiVaultModule.generate_argspec(
        mount_point=dict(type='str', default=DEFAULT_MOUNT_POINT),
        issuing_certificates=dict(type='list', elements='str', default=[]),
        crl_distribution_points=dict(type='list', elements='str', default=[]),
        ocsp_servers=dict(type='list', elements='str', default=[]),
        enable_templating=dict(type='bool', default=False),
    )

    module = HashiVaultModule(
        argument_spec=argspec,
        supports_check_mode=True
    )

    mount_point = module.params['mount_point']
    issuing_certificates = module.params['issuing_certificates']
    crl_distribution_points = module.params['crl_distribution_points']
    ocsp_servers = module.params['ocsp_servers']
    enable_templating = module.params['enable_templating']

    client = get_client(module)

    data = client.secrets.pki.read_urls(mount_point=mount_point)['data']
    params = {'issuing_certificates': issuing_certificates,
              'crl_distribution_points': crl_distribution_points,
              'ocsp_servers': ocsp_servers,
              'enable_templating': enable_templating}

    if params == data:
        module.exit_json(changed=False)

    response = client.secrets.pki.set_urls(mount_point=mount_point,
                                           params=params)
    module.exit_json(changed=True, data=response['data'])


if __name__ == '__main__':
    main()
