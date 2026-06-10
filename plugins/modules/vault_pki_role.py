#!/usr/bin/python

from hvac.api.secrets_engines.pki import DEFAULT_MOUNT_POINT
from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_module import HashiVaultModule

from ..module_utils.utils import get_client, is_params_subset


def main():
    argspec = HashiVaultModule.generate_argspec(
        state=dict(type='str',
                   choices=['present', 'absent'],
                   default='present'),
        mount_point=dict(type='str', default=DEFAULT_MOUNT_POINT),
        name=dict(type='str', required=True),
        allowed_domains=dict(type='list', elements='str', default=[]),
        allowed_other_sans=dict(type='list', elements='str', default=[]),
        allowed_serial_numbers=dict(type='list', elements='str', default=[]),
        allowed_uri_sans=dict(type='list', elements='str', default=[]),
        allowed_user_ids=dict(type='list', elements='str', default=[]),
        allow_any_name=dict(type='bool', default=False),
        allow_bare_domains=dict(type='bool', default=False),
        allow_glob_domains=dict(type='bool', default=False),
        allow_ip_sans=dict(type='bool', default=True),
        allow_localhost=dict(type='bool', default=True),
        allow_subdomains=dict(type='bool', default=False),
        allow_token_displayname=dict(type='bool', default=False),
        allow_wildcard_certificates=dict(type='bool', default=True),
        allowed_domains_template=dict(type='bool', default=False),
        allowed_uri_sans_template=dict(type='bool', default=False),
        ttl=dict(type='str', default='0'),
        max_ttl=dict(type='str', default='0'),
        issuer_ref=dict(type='str', default='default'),
    )

    module = HashiVaultModule(
        argument_spec=argspec,
        supports_check_mode=True
    )

    state = module.params['state']
    mount_point = module.params['mount_point']
    name = module.params['name']
    allowed_domains = module.params['allowed_domains']
    allowed_other_sans = module.params['allowed_other_sans']
    allowed_serial_numbers = module.params['allowed_serial_numbers']
    allowed_uri_sans = module.params['allowed_uri_sans']
    allowed_user_ids = module.params['allowed_user_ids']
    allow_any_name = module.params['allow_any_name']
    allow_bare_domains = module.params['allow_bare_domains']
    allow_glob_domains = module.params['allow_glob_domains']
    allow_ip_sans = module.params['allow_ip_sans']
    allow_localhost = module.params['allow_localhost']
    allow_subdomains = module.params['allow_subdomains']
    allow_token_displayname = module.params['allow_token_displayname']
    allow_wildcard_certificates = module.params['allow_wildcard_certificates']
    allowed_domains_template = module.params['allowed_domains_template']
    allowed_uri_sans_template = module.params['allowed_uri_sans_template']
    ttl = module.params['ttl']
    max_ttl = module.params['max_ttl']
    issuer_ref = module.params['issuer_ref']

    client = get_client(module)
    path = f'{mount_point}/roles/{name}'
    response = client.read(path)
    role = response['data'] if response else None


    if state == 'absent':
        if role:
            client.delete(path)
            module.exit_json(changed=True)
        module.exit_json(changed=False)

    params = {
        'allowed_domains': allowed_domains,
        'allowed_other_sans': allowed_other_sans,
        'allowed_serial_numbers': allowed_serial_numbers,
        'allowed_uri_sans': allowed_uri_sans,
        'allowed_user_ids': allowed_user_ids,
        'allow_any_name': allow_any_name,
        'allow_bare_domains': allow_bare_domains,
        'allow_glob_domains': allow_glob_domains,
        'allow_ip_sans': allow_ip_sans,
        'allow_localhost': allow_localhost,
        'allow_subdomains': allow_subdomains,
        'allow_token_displayname': allow_token_displayname,
        'allow_wildcard_certificates': allow_wildcard_certificates,
        'allowed_domains_template': allowed_domains_template,
        'allowed_uri_sans_template': allowed_uri_sans_template,
        'ttl': ttl,
        'max_ttl': max_ttl,
        'issuer_ref': issuer_ref,
    }
    params = {k: v for k, v in params.items() if v is not None}

    if state == 'present' and not role:
        client.write(path, **params)
        module.exit_json(changed=True, role=role)

    changed = not is_params_subset(params, role)
    if changed:
        response = client.write(path, **params)
        role = response['data']
    module.exit_json(changed=changed, role=role)


if __name__ == '__main__':
    main()
