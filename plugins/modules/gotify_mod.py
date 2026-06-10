#!/usr/bin/python3
from ansible.module_utils.basic import AnsibleModule
# from gotify import Gotify
import requests
from bs4 import BeautifulSoup
import json

class Gotify():
    def __init__(self):
        self.module_args = dict(
                gotify_url=dict(type='str', required=True),
                gotify_auth=dict(type='dict', required=True),
                gotify_token=dict(type='str', required=False),
                gotify_clients=dict(type='list', elements='dict', required=False),
                gotify_apps=dict(type='list', elements='dict', required=False),
                )
        self.result = dict(
            changed=False,
            message=''
        )
        self.module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True
        )
        self.gotify_url = self.module.params['gotify_url']
        self.gotify_auth = self.module.params['gotify_auth']
        self.gotify_token = self.module.params['gotify_token']
        self.gotify_clients = self.module.params['gotify_clients']
        self.gotify_apps = self.module.params['gotify_apps']
        self.req_auth = ( self.gotify_auth["user"],self.gotify_auth["pass"] )

    def resp_wrapper(self,namespace=None,rtype=None,data=None,cid=None):
        if namespace == "client":
            if rtype == "get":
                request = requests.get(f"{self.gotify_url}/client", auth=self.req_auth)
            elif rtype == "post":
                request = requests.post(f"{self.gotify_url}/client", data=data, auth=self.req_auth)
            elif rtype == "delete":
                request = requests.delete(f"{self.gotify_url}/client/{cid}", auth=self.req_auth)
        elif namespace == "app":
            if rtype == "get":
                request = requests.get(f"{self.gotify_url}/application", auth=self.req_auth)
            elif rtype == "post":
                request = requests.post(f"{self.gotify_url}/application", data=data, auth=self.req_auth)
            elif rtype == "delete":
                request = requests.delete(f"{self.gotify_url}/application/{cid}", auth=self.req_auth)
        if rtype != "delete":
            r = json.loads(request._content.decode('utf-8'))
        else:
            r = "Delete does not return json"
        return r



















def resp_wrapper(url=None,namespace=None,rtype=None,auth=None,data=None,cid=None):
    if namespace == "client":
        if rtype == "get":
            request = requests.get(f"{url}/client", auth=auth)
        elif rtype == "post":
            request = requests.post(f"{url}/client", data=data, auth=auth)
        elif rtype == "delete":
            request = requests.delete(f"{url}/client/{cid}", auth=auth)
    elif namespace == "app":
        if rtype == "get":
            request = requests.get(f"{url}/application", auth=auth)
        elif rtype == "post":
            request = requests.post(f"{url}/application", data=data, auth=auth)
        elif rtype == "delete":
            request = requests.delete(f"{url}/application/{cid}", auth=auth)
    if rtype != "delete":
        r = json.loads(request._content.decode('utf-8'))
    else:
        r = "Delete does not return json"
    return r


def main():
    module_args = dict(
            gotify_url=dict(type='str', required=True),
            gotify_auth=dict(type='dict', required=True),
            gotify_token=dict(type='str', required=False),
            gotify_clients=dict(type='list', elements='dict', required=False),
            gotify_apps=dict(type='list', elements='dict', required=False),
            )

    result = dict(
        changed=False,
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )


    gotify_url = module.params['gotify_url']
    gotify_auth = module.params['gotify_auth']
    gotify_token = module.params['gotify_token']
    gotify_clients = module.params['gotify_clients']
    gotify_apps = module.params['gotify_apps']

    try:
        # Set username and password
        auth = ( gotify_auth["user"],gotify_auth["pass"] )
        # Get all clients
        resp = resp_wrapper(url = gotify_url, namespace="client", rtype="get", auth=auth)
        # Construct a usable dictionary
        existing_clients = {}
        for i in resp:
            existing_clients[i["name"]] = i["id"]
            
        for client in gotify_clients:
            if client["name"] in existing_clients.keys():
                if client["state"] == "absent":
                    deletion = resp_wrapper(url = gotify_url, namespace="client", rtype="delete", cid=existing_clients[client["name"]], auth=auth)
                    result['changed'] = True
                    result['message'] = f"{ client['name'] } has been deleted"
                else:
                    result['changed'] = False if not result['changed'] else True
                    result['message'] = f"{ client['name'] } is present"
            else:
                if client["state"] != "absent":
                    data = {
                            "name": client["name"]
                            }
                    creation = resp_wrapper(url = gotify_url, namespace="client", rtype="post", data=data, auth=auth)
                    result['changed'] = True
                    result['message'] = f"{ client['name'] } has been created"
                else:
                    pass

        # Get all clients
        resp = resp_wrapper(url = gotify_url, namespace="app", rtype="get", auth=auth)
        existing_apps = {}
        for i in resp:
            existing_apps[i["name"]] = i["id"]
            
        for app in gotify_apps:
            if app["name"] in existing_apps.keys():
                if app["state"] == "absent":
                    deletion = resp_wrapper(url = gotify_url, namespace="app", rtype="delete", cid=existing_apps[app["name"]], auth=auth)
                    result['changed'] = True
                    result['message'] = f"{ app['name'] } has been deleted"
                else:
                    result['changed'] = False if not result['changed'] else True
                    result['message'] = f"{ app['name'] } is present"
            else:
                if app["state"] != "absent":
                    data = {
                            "name": app["name"],
                            "description": app["description"],
                            # "image": app["icon"]
                            }
                    creation = resp_wrapper(url = gotify_url, namespace="app", rtype="post", data=data, auth=auth)
                    result['changed'] = True
                    result['message'] = f"{ app['name'] } has been created"
                else:
                    pass




    except Exception as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)

if __name__ == '__main__':
    main()







