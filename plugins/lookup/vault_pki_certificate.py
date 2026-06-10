DOCUMENTATION = """
  name: vault_pki_root
  author:
    - Modesto Mas (@mmas)
  short_description: Read PKI certificate
  requirements:
    - C(hvac) (L(Python library,https://hvac.readthedocs.io/en/stable/overview.html))
  description:
    - Read most-recent non-revoked PKI certificate issuer by common name
  seealso:
    - module: mmas.hashi_vault.vault_pki_certificate
  extends_documentation_fragment:
    - community.hashi_vault.connection
    - community.hashi_vault.connection.plugins
    - community.hashi_vault.auth
    - community.hashi_vault.auth.plugins
  options:
    _terms:
      description: Subject CN of the certificate.
      type: str
      required: true
    mount_point:
      description: PKI secrets engine mount point
      type: str
      default: pki_int
"""

EXAMPLES = """
- name: Download server certificate
  copy:
    dest: /tmp/homelab.local.crt
    content: "{{ lookup('mmas.hashi_vault.vault_pki_certificate', '*.homelab.local').certificate }}"
"""

RETURN = """
certificate:
  description:
    - Certificate of the root issuer.
issue_date:
  description:
    - Expiration datetime of the certificate.
expiration_date:
  description:
    - Expiration datetime of the certificate.
"""


from ansible_collections.community.hashi_vault.plugins.plugin_utils._hashi_vault_lookup_base import HashiVaultLookupBase
from ansible_collections.community.hashi_vault.plugins.module_utils._hashi_vault_common import HashiVaultValueError
import hvac

from ..module_utils.utils import get_client, get_certificate


class LookupModule(HashiVaultLookupBase):

    def run(self, terms, mount_point='pki_int', variables=None, **kwargs):
        self.set_options(direct=kwargs, var_options=variables)
        ret = []

        # TODO: remove process_deprecations() if backported fix is available
        #       (see method definition)
        self.process_deprecations()

        client = get_client(self)

        common_name = terms[0]
        try:
            issuer = get_certificate(client, mount_point, common_name)
        except hvac.exceptions.Forbidden:
            raise AnsibleError('Forbidden: Permission Denied')

        ret.append(issuer)

        return ret
