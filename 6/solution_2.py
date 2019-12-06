#!/usr/bin/env python

import sys
import anytree

nodes = {}

def add_node(node_id, parent_id):
    node = nodes.get(node_id, anytree.Node(node_id))
    parent = nodes.get(parent_id, anytree.Node(parent_id))
    node.parent = parent
    nodes[node_id], nodes[parent_id] = node, parent
    return node

def count_transfers(source, dest):
    path_diff = set(source.parent.path) ^ set(dest.parent.path)
    return len(path_diff)

if __name__ == '__main__':
    last_node = None
    with open('input', 'r') as input_data:
        for line in input_data:
            parent_id, child_id = line.strip().split(')')
            last_node = add_node(child_id, parent_id)

    print(count_transfers(nodes['YOU'], nodes['SAN']))

