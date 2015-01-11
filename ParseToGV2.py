#!/usr/bin/env python

import sys, os
from ParseGetPot import GPNode, ParseGetPot

# GraphViz global parameters (default node shape and size, edge type, etc.)
gv_globalpars=['layout=dot;size="20,20";rankdir=LR;splines=true;pad="0";ranksep="1.5";nodesep="0.3"',
               'node[shape=box3d];'
               'edge[color="#808080";fontcolor="#808080"];']


nodelist = []
edgelist = []


def tr(s):
  return s.replace('/','_').replace('.','_').replace(':','_').replace('-','_')


def attach_child(nd_parent, nd_child):
  nd_child.parent = nd_parent
  nd_parent.children.append(nd_child)


def ParseFile(filename, basepath):
  if not os.path.isabs(filename):
    filename = os.path.join(basepath,filename)
  
  if not os.path.isfile(filename):
    sys.stderr.write('Could not find sub-app input file %s. Ignoring.' % filename)
  else:
    # read the file into a GPNode object
    nd_file = ParseGetPot(filename).root_node
    nd_file.name = tr(os.path.basename(filename))
    nd_file.parent = None
    # search it for any MultiApps
    nd_multiapp = nd_file.getNode('MultiApps')
    if nd_multiapp != None:
      # traverse over all possible sub-apps
      for nd_sub in nd_multiapp.children.values():
        # traverse over all entries in their 'input_files' parameter
        for filename_sub in nd_multi.params['input_files'].split(' '):
          nd_subfile = ParseFile(filename_sub, basepath)
          attach_child(nd_sub, nd_subfile)
          
    return nd_file


def ParseNodeConnections(node):
  node.Print()


if __name__ == '__main__':
  if (len(sys.argv) > 1):
    filename = os.path.abspath(sys.argv[1])
    basepath = os.path.dirname(filename)

    global_root = ParseFile(filename, basepath)
    ParseNodeConnections(global_root)
    

    print 'strict digraph "%s" {' % sys.argv[1]
    print '\n'.join(gv_globalpars)
    print '\n'.join(nodelist)
    print '\n'.join(edgelist)

    print '}'
  else:
    print 'Usage %s filename' % sys.argv[0]