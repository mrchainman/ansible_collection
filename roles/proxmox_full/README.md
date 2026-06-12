Role Name
=========

This role sets up proxmox via terraform.
Currently it downloads isos/disks and creates vms, more to come.

Requirements
------------

Terraform or opentofu installed.
An existing proxmox server.

Role Variables
--------------
The following variables are genearl and should be set at the role or group level:

| Variablename | Required | Default | Description |
---------------------------------------------------
|terraform_project_path | yes | "" | Path to the folder where terraform files will be created |
|terraform_binary_path | no | "/usr/bin/terraform" | Path to the terraform/opentofu executable |
|terraform_pmx_endpoint | yes | "http://localhost:8006/" | Where proxmox can be reached |
|terraform_pmx_api_token | yes | "<user>@<pam/pve>!<tokenname>=<tokensecret>" | Token used to authenticate |
|terraform_parallelism | no | 50 | Parallelism option for Terraform



Each VM has specific settings which are set by the following variables. This should be set in either group_vars or host_vars

| Variablename | Required | Default | Description |
---------------------------------------------------
|pmx_name | no | "{{ inventory_hostname }}" | The name of the VM |
| existing_node_id | no |   | VM ID, can be used to import the vm into state
|pmx_node| yes | "pmx01" | Name of the Porxmox Node |
|pmx_import_image | no | "debian_cloud_image" | The base image to import |
|pmx_memory | no | 1024 | VM Memory |
|pmx_balloon | no | true | VM Memory Balooning |
|pmx_bios_type | no | "seabios" | VM Bios |
|pmx_machine | no | "q35" | VM Machinetype |
|pmx_description | no | "" | VM Description |
|pmx_cpu_arch | no | "x86_64" | VM CPU Architecture |
|pmx_cpu_type | no | "x86-64-v2-AES" | VM CPU Type |
|pmx_cpuunits | no | 1 | VM CPU Units |
|pmx_cores | no | "2" | VM CPU Cores |
|pmx_vcpus | no | "2" | VM VCPUS |
|pmx_nw_bridge | no | "vmbr2" | Name of the network bridge to attach the vm to |
|pmx_ip_address | no | "{{ ansible_host }}" | The IP Address to assign to the vm |
|nw_mask | no | 24 | The networkmask of the IP |
|pmx_ip_address_net | no | "{{ ansible_host }}/{{ nw_mask }}" | Full CIDR notation of the ip |
|pmx_gw_address | no | "192.168.11.1" | Gatwayaddress |
|pmx_dns | no | "{{ pmx_gw_address }}" | DNS Server |
|pmx_root_storage | no | "local-zfs" | Where to store the rootdisk |
|pmx_root_size | no | 30 | Size of the rootdisk |
|pmx_data_storage | no | "encset" | Where to store the data disk |
|pmx_ostype | no | "l26" | Type of the OS |
|pmx_scsihw | no | virtio-scsi-single | SCSI Hardware |
|pmx_vga | no | std | VGA Attachment |
|pmx_ssh_key | yes | "changeme" | Public SSH Key set during cloud init |

To define the boot order use this syntax

pmx_boot:
  - scsi0
  - ide2

To define extra data disks the following syntax can be user:

pmx_extra_disks:
  - mountpoint: /mnt
    size: 50
    storage: "{{ pmx_data_storage }}"
    backup: false
    replicate: true
    ssd: false

Images can be defined as follows:

terraform_images:
  - name: debian_cloud_image
    imagestore: local
    filename: debian-13-generic-amd64.qcow2
    url: "https://cloud.debian.org/images/cloud/trixie/latest/debian-13-generic-amd64.qcow2"

Example Playbook
----------------

- name: Run Terraform
  become: false
  hosts: all
  gather_facts: false
  tags:
    - "never"
    - "terraform"
  vars:
    terraform_project_path: ./terraform/proxmox
    terraform_binary_path: ~/.data/Administration/ansible/bin/tofu
    pmx_node: "hv02"
  roles:
    - { role: mrchainman.custom.proxmox_full }

License
-------

GPLv2

Author Information
------------------

MrChainman <mrchainman@chainman.xyz>
