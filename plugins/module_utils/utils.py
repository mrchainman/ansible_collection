import datetime
from OpenSSL import crypto
import re
import traceback

from ansible.errors import AnsibleError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_common import HashiVaultValueError


def get_client(module):
    module.connection_options.process_connection_options()
    client_args = module.connection_options.get_hvac_connection_options()
    client = module.helper.get_vault_client(**client_args)

    try:
        module.authenticator.validate()
        module.authenticator.authenticate(client)
    except (NotImplementedError, HashiVaultValueError) as e:
        if isinstance(module, AnsibleModule):
            module.fail_json(msg=to_native(e),
                             exception=traceback.format_exc())
        else:
            raise AnsibleError(e)

    return client


def get_issuer(client, mount_point, common_name):
    response = client.list(f'{mount_point}/issuers')
    if not response:
        return None
    issuers = []
    for key in response['data']['keys']:
        data = client.read(f'{mount_point}/issuer/{key}')['data']
        certificate = data['certificate'].strip()
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        subject_common_name = x509.get_subject().CN
        if common_name == subject_common_name and data['revoked'] is False:
            issuers.append({
                'certificate': certificate,
                'issuer_id': data['issuer_id'],
                'issuer_name': data['issuer_name'],
                'common_name': common_name,
                'key_id': data['key_id'],
                'issue_date': parse_x509_datetime(x509.get_notBefore()),
                'expiration_date': parse_x509_datetime(x509.get_notAfter()),
            })
    if not issuers:
        return None
    return max(issuers, key=lambda x: x['issue_date'])


def get_certificate(client, mount_point, common_name):
    response = client.list(f'{mount_point}/certs')
    if not response:
        return None
    certificates = []
    for key in response['data']['keys']:
        data = client.read(f'{mount_point}/cert/{key}')['data']
        if data['revocation_time']:
            continue
        certificate = data['certificate'].strip()
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        if common_name != x509.get_subject().CN :
            continue
        certificates.append({
            'certificate': certificate,
            'issue_date': parse_x509_datetime(x509.get_notBefore()),
            'expiration_date': parse_x509_datetime(x509.get_notAfter()),
        })
    if not certificates:
        return None
    return max(certificates, key=lambda x: x['issue_date'])


def parse_ttl(ttl):
    if isinstance(ttl, int):
        return ttl
    if not re.match(r'\d+[hms]?$', ttl):
        raise HashiVaultValueError(f'InvalidTTL: {ttl}')
    if ttl.endswith('h'):
        return int(ttl[:-1])*60*60
    if ttl.endswith('m'):
        return int(ttl[:-1])*60
    if ttl.endswith('s'):
        ttl = ttl[:-1]
    return int(ttl)


def parse_x509_datetime(x509_datetime):
    return datetime.datetime.strptime(x509_datetime.decode(), '%Y%m%d%H%M%SZ')


def list_certificates(client, mount_point, common_name):
    response = client.list(f'{mount_point}/certs')
    if not response:
        return []
    certificates = []
    for serial_number in response['data']['keys']:
        data = client.read(f'{mount_point}/cert/{serial_number}')['data']
        if data['revocation_time']:
            continue
        certificate = data['certificate']
        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        if common_name != x509.get_subject().CN:
            continue
        certificates.append({
            'certificate': certificate,
            'serial_number': serial_number,
            'issue_date': x509.get_notBefore(),
            # 'issue_date': datetime.datetime.strptime(x509.get_notBefore().decode(), '%Y%m%d%H%M%SZ'),
            'issuer_common_name': x509.get_issuer().CN,
            'common_name': common_name,
        })
    return certificates


def is_params_subset(new_params, cur_params):
    for key, new_value in new_params.items():
        cur_value = cur_params.get(key)
        null_count = sum(1 for i in [cur_value, new_value] if i is not None)
        if null_count == 1:
            return False
        elif isinstance(cur_value, list):
            if not isinstance(new_value, list):
                new_value = [new_value]
            cur_value, new_value = set(cur_value), set(new_value)
        elif key.endswith('ttl'):
            new_value = parse_ttl(new_value)
            cur_value = parse_ttl(cur_value)
        if cur_value != new_value:
            return False
    return True
