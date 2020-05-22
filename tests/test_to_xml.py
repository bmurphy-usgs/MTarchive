# -*- coding: utf-8 -*-
"""
Created on Fri May 22 11:53:57 2020

@author: jpeacock
"""

from xml.etree import cElementTree as ET
from xml.dom import minidom
from mth5 import metadata
from collections import defaultdict, OrderedDict
from operator import itemgetter

s = metadata.Survey()
sd = s.to_dict(structured=True)

root = ET.Element(s.__class__.__name__)

for key, value in sd.items():
    element = ET.SubElement(root, key)
    if isinstance(value, dict):
        for k, v in value.items():
            sub_element = ET.SubElement(element, k)
            sub_element.text = str(v)
            units = s._attr_dict['{0}.{1}'.format(key, k)]['units']
            if units:
                sub_element.set('units', str(units)) 
    else:
        element.text = str(value)
print(minidom.parseString(ET.tostring(root).decode()).toprettyxml(indent='    '))    

## from xml

def etree_to_dict(element):
    meta_dict = {element.tag: {} if element.attrib else None}
    children = list(element)
    if children:
        child_dict = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                child_dict[k].append(v)
        meta_dict = {element.tag: {k:v[0] if len(v) == 1 else v 
                                   for k, v in child_dict.items()}}
    # going to skip attributes for now, later can check them against 
    # standards
    # if element.attrib:
    #     meta_dict[element.tag].update((k, v) 
    #                                   for k, v in element.attrib.items())
    
    if element.text:
        text = element.text.strip()
        # if children or element.attrib:
        #     if text:
        #       meta_dict[element.tag]['value'] = text
        # else:
        meta_dict[element.tag] = text
        
    return OrderedDict(sorted(meta_dict.items(), key=itemgetter(0)))

test_sd = etree_to_dict(root)

def dict_to_etree(meta_dict):
    def _to_etree(meta_dict, root):
        if not meta_dict:
            pass
        elif isinstance(meta_dict, str):
            root.text = meta_dict
        elif isinstance(meta_dict, dict):
            for k,v in meta_dict.items():
                assert isinstance(k, str)
                if k.startswith('#'):
                    assert k == '#text' and isinstance(v, str)
                    root.text = v
                elif k.startswith('@'):
                    assert isinstance(v, str)
                    root.set(k[1:], v)
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(e, ET.SubElement(root, k))
                else:
                    _to_etree(v, ET.SubElement(root, k))
        else:
            raise TypeError('invalid type: ' + str(type(meta_dict)))
    assert isinstance(meta_dict, dict) and len(meta_dict) == 1
    tag, body = next(iter(meta_dict.items()))
    node = ET.Element(tag)
    _to_etree(body, node)
    return ET.tostring(node)


# for level in root.iter(): 