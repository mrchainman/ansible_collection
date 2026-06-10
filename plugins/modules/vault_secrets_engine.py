#!/usr/bin/python

import re

from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_module import HashiVaultModule

from ..module_utils.utils import get_client, is_params_subset


def main():
    argspec = HashiVaultModule.generate_argspec(
        state=dict(type='str',
                   choices=['enabled', 'disabled'],
                   default='enabled'),
        backend_type=dict(type='str'),
        mount_point=dict(type='str'),
        description=dict(type='str'),
        config=dict(type='dict'),
        plugin_name=dict(type='str'),
        options=dict(type='dict'),
        local=dict(type='bool', default=False),
        seal_wrap=dict(type='bool', default=False),
    )

    module = HashiVaultModule(
        argument_spec=argspec,
        supports_check_mode=True
    )

    state = module.params['state']
    backend_type = module.params['backend_type']
    mount_point = module.params['mount_point'] or backend_type
    description = module.params['description']
    config = module.params['config'] or {}
    plugin_name = module.params['plugin_name']
    options = module.params['options']
    local = module.params['local']
    seal_wrap = module.params['seal_wrap']

    client = get_client(module)

    clean_mount_point = f"{re.sub(r'^/|/$', '', mount_point)}/"
    engine = client.sys.list_mounted_secrets_engines().get(clean_mount_point)

    if state == 'disabled':
        if engine:
            client.sys.disable_secrets_engine(path=mount_point)
        module.exit_json(changed=bool(engine))

    engine_path = f'sys/mounts/{mount_point}'
    engine_config_path = f'{engine_path}/tune'

    if not engine:
        client.sys.enable_secrets_engine(
            backend_type=backend_type,
            path=mount_point,
            description=description,
            config=config,
            plugin_name=plugin_name,
            options=options,
            local=local,
            seal_wrap=seal_wrap)
        module.exit_json(changed=True, engine=client.read(engine_path)['data'])

    cur_config = client.read(engine_config_path)['data']
    if is_params_subset(config, cur_config):
        module.exit_json(changed=False, engine=engine)

    client.write(engine_config_path, **config)

    module.exit_json(changed=True, engine=client.read(engine_path)['data'])


if __name__ == '__main__':
    main()
