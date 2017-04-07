#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json 
import requests
from to import get_guest_data
import settings

middlewares = settings._middlewares
description_settings = settings._settings

def get_description(name, alias, middlewares, urls):
    import os
    to_manager = ToManager(name, alias, middlewares)
    description_dict = to_manager.transfer(urls)
    if not isinstance(name, basestring):
        name = name.decode("utf-8")
    if not isinstance(alias, basestring):
        alias = alias.decode("utf-8")
    description_dict["name"] = name 
    description_dict["alias"] = alias
    if not os.path.exists(os.path.join(os.getcwd(), "descriptions")):
        import  subprocess
        subprocess.call("mkdir descriptions", shell=True)
    with open("descriptions/" + alias + ".txt", "wt") as f:
        json.dump(description_dict, f)
        print "result has been written into %s" % f.name

class ToManager(object):
    def __init__(self, name, alias, middlewares=None):
        self.name = name
        self.alias = alias
        self.middlewares = []
        if middlewares is not None:
            if not isinstance(middlewares, list):
                raise TypeError("expected a list")
            self.middlewares.extend(middlewares)
        self._i = 0

    def transfer(self, urls=None):
        data = self.get_data(urls)
        if not data:
            raise ValueError("wrong data: %s" % data)
        self._data = data
        while self._i < len(self.middlewares):
            self.select_middleware(self._i)
        import os
        if not os.path.exists(os.path.join(os.getcwd(), "outputs")):
            import subprocess
            subprocess.call("mkdir outputs", shell=True)
        # 当前输出位置
        with open("output.txt", "wt") as f_:
            import json
            json.dump(self._data, f_)
        # 备份输出
        with open("outputs/" + self.alias + "_output.txt", "wt") as f:
            import json
            json.dump(self._data, f)
        return get_guest_data(self._data)

    def select_middleware(self, i):
        func = self.middlewares[self._i]
        self._data = func(self._data, self._i+1)
        self._i += 1

    def add_middleware(self, middleware):
        self.middlewares.append(middleware)

    def get_data(self, urls=None):
        if not urls:
            print "get local data from input.txt"
            local_data = self._get_local_data()
            return local_data
        else:
            print "get remote data from %s" % urls
            from collections import defaultdict
            remote_data = defaultdict(list)
            count = 1
            for u in urls:
                method = u.get("method")
                url = u.get("url")
                data = u.get("data")
                remote_data["data%s" % count].append(self._get_remote_data(method, url, data))
                count += 1
            return remote_data

    def _get_local_data(self):
        with open("input.txt", "rt") as f:
            data = json.load(f)
            return data

    def _get_remote_data(self, method, url, data):
        if method in ["post", "POST"]:
            res = requests.post(url, data=json.dumps(data))
        elif method in ["get", "GET"]:
            res = requests.get(url, params=data)
        if res and res.ok:
            return json.loads(res.content)
        else:
            raise Exception("HTTP Error: %s %s %s" % (url, data, res.content))

            
            
    
if __name__ == "__main__":
    name = description_settings.get("name", "default_name")
    alias = description_settings.get("alias", "default_alias")
    urls = description_settings.get("urls")
    get_description(name, alias, middlewares, urls)
