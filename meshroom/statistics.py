#!/usr/bin/env python3
import argparse
import os
from pprint import pprint
from collections import Iterable

from meshroom.processGraph import graph as pg

parser = argparse.ArgumentParser(description='Query the status of nodes in a Graph of processes.')
parser.add_argument('graphFile', metavar='GRAPHFILE.mg', type=str,
                    help='Filepath to a graph file.')
parser.add_argument('--node', metavar='NODE_NAME', type=str,
                    help='Process the node alone.')
parser.add_argument('--graph', metavar='NODE_NAME', type=str,
                    help='Process the node and all previous nodes needed.')
parser.add_argument('--exportHtml', metavar='FILE', type=str,
                    help='Filepath to the output html file.')
parser.add_argument("--verbose", help="Print full status information",
                    action="store_true")

args = parser.parse_args()

if not os.path.exists(args.graphFile):
    print('ERROR: No graph file "{}".'.format(args.node, args.graphFile))
    exit(-1)

graph = pg.loadGraph(args.graphFile)

graph.update()
graph.updateStatisticsFromCache()

nodes = []
if args.node:
    if args.node not in graph.nodes:
        print('ERROR: node "{}" does not exist in file "{}".'.format(args.node, args.graphFile))
        exit(-1)
    nodes = [graph.nodes[args.node]]
else:
    startNodes = None
    if args.graph:
        startNodes = [graph.nodes[args.graph]]
    nodes = graph.dfsNodesOnFinish(startNodes=startNodes)

for node in nodes:
    print('{}: {}'.format(node.name, node.statistics.toDict()))

if args.exportHtml:
    import matplotlib.pyplot as plt, mpld3
    import numpy as np

    with open(args.exportHtml, 'w') as fileObj:
        for node in nodes:
            plt.title(node.name)
            s = node.statistics
            for k in ('cpuUsage', 'ramUsage', 'swapUsage', 'vramUsage'):
                allData = s.__dict__[k]
                fig = plt.figure()
                ax = fig.add_subplot(111, axisbg='#EEEEEE')
                ax.grid(color='white', linestyle='solid')

                # if multiple values per time
                if allData and isinstance(allData[0], Iterable):
                    # transpose the list of list
                    allData = list(map(list, zip(*allData)))
                else:
                    allData = [allData]

                for data in allData:
                    y = data
                    x = np.arange(len(y))
                    ax.plot(x, y)
                plt.ylim(0, 100)
                plt.title(k)

                mpld3.save_html(fig, fileObj)
