DOCUMENTATION = """
  name: vault_pki_root
  author:
    - Modesto Mas (@mmas)
  short_description: Read PKI intermediate issuer
  requirements:
    - C(hvac) (L(Python library,https://hvac.readthedocs.io/en/stable/overview.html))
  description:
    - Read most-recent non-revoked PKI intermediate issuer by common name
  seealso:
    - module: mmas.hashi_vault.vault_pki_intermediate
  extends_documentation_fragment:
    - community.hashi_vault.connection
    - community.hashi_vault.connection.plugins
    - community.hashi_vault.auth
    - community.hashi_vault.auth.plugins
  options:
    _terms:
      description: Subject CN of the intermediate issuer.
      type: str
      required: true
    mount_point:
      description: PKI secrets engine mount point
      type: str
      default: pki_int
"""

EXAMPLES = """
- name: Download intermediate certificate
  copy:
    dest: /tmp/intermediate.crt
    content: "{{ lookup('mmas.hashi_vault.vault_pki_intermediate', 'Vault Intermediate').certificate }}"
"""

RETURN = """
certificate:
  description:
    - Certificate of the root issuer.
common_name:
  description:
    - Subject CN of the root issuer certificate.
issuer_id:
  description:
    - Issuer ID of the root issuer.
issuer_name:
  description:
    - Issuer name of the root issuer.
key_id:
  description:
    - Key ID of the root issuer.
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

from ..module_utils.utils import get_client, get_issuer


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
            issuer = get_issuer(client, mount_point, common_name)
        except hvac.exceptions.Forbidden:
            raise AnsibleError('Forbidden: Permission Denied')

        ret.append(issuer)

        return ret
