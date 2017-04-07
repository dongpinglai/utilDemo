#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from bson import ObjectId


fields = []
inner = {}


def guest_base(key, value):
    info = {
        "isarray": False,
        "index": False,
        "required": False,
        "unique": False,
        "description": "",
        "datatype": type(value).__name__,
        "alias": key,
        "name": key,
    }

    if info['datatype'] == 'unicode':
        info['datatype'] = 'str'

    if isinstance(value, (list, dict)):
        info['datatype_embed_type'] = str(ObjectId())
        info['datatype_embed'] = 'complex'

    return info


def guest(datas, inner_obj=None):
    """
    :data: TODO
    :returns: TODO
    """

    if isinstance(datas, list):
        new_datas = {}
        #datas = datas[0]
        for data in datas:
            for key, val in data.iteritems():
                if key not in new_datas:
                    new_datas[key] = val
        datas = new_datas

    for k, v in datas.iteritems():
        if isinstance(v, (dict, list)):
            item = guest_base(k, v)
            inner_obj_id = str(item['datatype_embed_type'])
            inner[inner_obj_id] = {'fields': []}
            guest(v, inner_obj=inner_obj_id)
        else:
            item = guest_base(k, v)

        if inner_obj:
            inner[inner_obj]['fields'].append(item)
        else:
            fields.append(item)
            
def get_guest_data(data):
    guest(data)
    result = {'fields': fields, 'datas': inner}
    return result
    

if __name__ == "__main__":
    import datetime
    import json
    import requests
    import sys
    import os

    test_data = {}
    with open(os.path.expanduser("input.txt"), "rt") as f:
        test_data = json.loads(f.read())

    if len(sys.argv) > 1:
        method = "get-fetch datas"
        url = sys.argv[1]
        data  = {}
        data_items = sys.argv[2:]
        for item in data_items:
            key, val = item.split(":")
            data[key] = val
        print type(data), data
        res = requests.get(url, params=json.dumps(data), timeout=500) # default get 
        if res.ok:
            print res.text
            datas = json.loads(res.text)
            guest(datas)
        else: # plan B post
            res = requests.post(url, data=json.dumps(data), timeout=500)
            if res.ok:
                method = "post-send requests"
                print res.content
                datas = json.loads(res.content)
                guest(datas)
            else:
                raise ValueError("Both get and post all failed")
                
        result = {'fields': fields, 'datas': inner}
        result = json.dumps(result)

        with open('output.txt', 'wb') as fp:
            fp.write(result)
        print 'Done and result has been written into ', fp.name, " Method:", method
    elif test_data:
        guest(test_data)
        result = {'fields': fields, 'datas': inner}
        result = json.dumps(result)
        with open("output.txt", 'wb') as fp:
            fp.write(result)
        print 'Done and result has been written into', fp.name
    else:
        print "need URL argument"
