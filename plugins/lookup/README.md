# mmas.hashi_vault lookups

## vault_pki_certificate

### Sinopsis

  - Read most-recent non-revoked PKI certificate issuer by common name

### Requirements

  - [`hvac`](https://hvac.readthedocs.io/en/stable/overview.html)

### Parameters

```yaml
_terms:
  description: Subject CN of the certificate.
  type: str
  required: true
mount_point:
  description: PKI secrets engine mount point
  type: str
  default: pki_int
```

### See also

  - [`module: vault_pki_certificate`](https://github.com/mmas/hashi_vault-ansible-collection/tree/master/plugins/modules#vault_pki_certificate)


### Examples

```yaml
- name: Download server certificate
  copy:
    dest: /tmp/homelab.local.crt
    content: "{{ lookup('mmas.hashi_vault.vault_pki_certificate', '*.homelab.local').certificate }}"
```

### Return values

```yaml
certificate:
  description:
    - Certificate of the root issuer.
issue_date:
  description:
    - Expiration datetime of the certificate.
expiration_date:
  description:
    - Expiration datetime of the certificate.
```



## vault_pki_intermediate

### Sinopsis

  - Read most-recent non-revoked PKI intermediate issuer by common name

### Requirements

  - [`hvac`](https://hvac.readthedocs.io/en/stable/overview.html)

### Parameters

```yaml
_terms:
  description: Subject CN of the certificate.
  type: str
  required: true
mount_point:
  description: PKI secrets engine mount point
  type: str
  default: pki_int
```

### See also

  - [`module: vault_pki_intermediate`](https://github.com/mmas/hashi_vault-ansible-collection/tree/master/plugins/modules#vault_pki_intermediate)


### Examples

```yaml
- name: Download intermediate certificate
  copy:
    dest: /tmp/intermediate.crt
    content: "{{ lookup('mmas.hashi_vault.vault_pki_intermediate', 'Vault Intermediate').certificate }}"
```

### Return values

```yaml
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
```




## vault_pki_root

### Sinopsis

  - Read most-recent non-revoked PKI root issuer by common name

### Requirements

  - [`hvac`](https://hvac.readthedocs.io/en/stable/overview.html)

### Parameters

```yaml
_terms:
  description: Subject CN of the root issuer.
  type: str
  required: true
mount_point:
  description: PKI secrets engine mount point
  type: str
  default: pki
```

### See also

  - [`module: vault_pki_root`](https://github.com/mmas/hashi_vault-ansible-collection/tree/master/plugins/modules#vault_pki_root)

### Examples

```yaml
- name: Download root certificate
  copy:
    dest: /tmp/root.crt
    content: "{{ lookup('mmas.hashi_vault.vault_pki_root', 'Vault Root').certificate }}"
```

### Return values

```yaml
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
```
