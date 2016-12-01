import sys
import json
import numpy as np
import random

def read_json_file(file_path):
    content = ""
    with open(file_path, 'r') as f:
        for line in f:
            content += line
    return content

def sidewalk_dist(way, node1, node2):
    # 0.00006
    return np.random.normal(0.00006, 0.00002)

def rotate_vec(vec, theta):
    rotMatrix = np.array([[np.cos(theta), -np.sin(theta)], 
                         [np.sin(theta),  np.cos(theta)]])
    return vec.dot(theta)


def add_sidewalk(output, way, sidewalk_nodes):
    
    for i in range(2):
        nodes = []
        for node in sidewalk_nodes:        
            next_node_id = int(random.random() * 100000000000)
            nodes += [next_node_id]
            output["elements"] += [{
                "type": "node",
                "id": next_node_id,
                "lat": node[i][0],
                "lon": node[i][1]
            }]
        next_way_id = int(random.random() * 100000000000)
        output["elements"] += [{
                "type": "way",
                "id": next_way_id,
                "nodes": nodes,
                "tags": { "highway": "sidewalk" }
            }]


def generate_sidewalks(osm_json_file):
    osm_content = read_json_file(osm_json_file)
    osm_json = json.loads(osm_content)
    
    sidewalk_json = {
        "version": 0.6,
        "generator": "Overpass API",
        "osm3s": {
            "timestamp_osm_base": "2016-11-29T06:59:03Z",
            "copyright": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL."
        },
        "elements": []
    }
    

    nodes = {}  # maps from node id to (lat, lon) vector
    ways = []   # list of way elements

    for element in osm_json["elements"]:
        if element["type"] == "node":
            nodes[element["id"]] = np.array([element["lat"], element["lon"]])
        elif element["type"] == "way":
            ways += [element]

    for way in ways:
        num_nodes = len(way["nodes"])
        if num_nodes > 1:
            n1 = nodes[way["nodes"][0]]
            n2 = nodes[way["nodes"][1]]
            # unit vector of center line direction
            direction = (n2 - n1) / np.linalg.norm(n2 - n1)
            orth_direction = np.array([-direction[1], direction[0]])

            # expected distance from centerline
            d = sidewalk_dist(way, n1, n2)

            # list of sidewalk waypoint pairs (left, right)
            sidewalk_nodes = [tuple([n1 - orth_direction * d, n1 + orth_direction * d])]
            prev_direction = direction

            print num_nodes
            for i in range(2, num_nodes):
                n1 = nodes[way["nodes"][i - 1]]
                n2 = nodes[way["nodes"][i]]
                d = sidewalk_dist(way, n1, n2)
                direction = (n2 - n1) / np.linalg.norm(n2 - n1)
                orth_direction = np.array([-direction[1], direction[0]])

                # print np.linalg.norm(direction)
                # print np.linalg.norm(prev_direction)

                # theta = np.arccos(prev_direction.dot(direction))
                # intersec_direction = np.array([1, 0])
                # intersec_direction = rotate_vec(direction, (np.pi - theta) / 2)

                sidewalk_nodes += [tuple([n1 - orth_direction * d, n1 + orth_direction * d])]    
                prev_direction = direction

            # last node

            n1 = nodes[way["nodes"][num_nodes - 2]]
            n2 = nodes[way["nodes"][num_nodes - 1]]
            direction = (n2 - n1) / np.linalg.norm(n2 - n1)
            orth_direction = np.array([-direction[1], direction[0]])
            print np.linalg.norm(orth_direction)

            # expected distance from centerline
            d = sidewalk_dist(way, n1, n2)
            print d
            sidewalk_nodes += [tuple([n2 - orth_direction * d, n2 + orth_direction * d])]

            add_sidewalk(sidewalk_json, way, sidewalk_nodes)
    
    print sidewalk_nodes
    pretty_json =  json.dumps(sidewalk_json, indent=2, separators=(',', ': '))

    output_file = open('output.json', 'w')
    output_file.write(pretty_json)

    return sidewalk_json


if __name__ == "__main__":
    generate_sidewalks("downtown_osm.json")
 # http://tyrasd.github.io/osmtogeojson/