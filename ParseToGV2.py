#!/usr/bin/env python

import sys, os
from ParseGetPot import GPNode, ParseGetPot

# GraphViz global parameters (default node shape and size, edge type, etc.)
gv_globalpars=['layout=dot;size="20,20";rankdir=LR;splines=true;pad="0";ranksep="1.5";nodesep="0.3"',
               'node[shape=box3d];'
               'edge[color="#808080";fontcolor="#808080"];']
               
globaloptions={'node_table_heading_style': 'BGCOLOR="#dddddd"', # HTML style for the parameter table headings for regular nodes
               'cluster_table_heading_style': '', # HTML style for the parameter table headings for clusters
               'maxlen_param': 20, # maximum length (number of characters) for parameter names in parameter tables
               'maxlen_value': 35, # maximum length (number of characters) for parameter names in parameter tables
              }


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


def ParseConnections(node):
  # TODO
  print ''

def CreateParamTable(node, heading):
  # add node name (and type if available) in a heading line with colored background
  table = ['<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">']
  if heading:
    table += ['<TR><TD COLSPAN="3" %s><B>%s&nbsp;</B>' % (globaloptions['node_table_heading_style'], tr(node.name))]
    if 'type' in node.params_list:
      table[-1] += ':&nbsp;%s' % node.params['type']
    table[-1] += '</TD></TR>'
  else:
    # add node type if available in a heading line with no
    if 'type' in node.params_list:
      table += ['<TR><TD COLSPAN="3" %s><B>%s&nbsp;</B></TD></TR>' % tr(globaloptions['cluster_table_heading_style'], node.params['type'])]

  # create the tables for all parameters except 'type' (because this is in the headline already)
  # TODO: add ports everywhere !
  for param, value in node.params.iteritems():
    if param != 'type':
      table += ['<TR><TD PORT="%s_PARAM">%s</TD><TD>=</TD><TD PORT="%s_VALUE">%s</TD></TR>' % (param, param[0:globaloptions['maxlen_param']], param, value[0:globaloptions['maxlen_value']])]

  table += ['</TABLE>']

  # do not add an empty table
  if len(node.params) > 0 or heading:
    if heading:
      nodelist.append('%s[label=<%s>];' % (tr(node.fullName()), '\n'.join(table)))
    else:
      # no heading --> simple plaintext node style
      nodelist.append('%s[label=<%s>, shape=plaintext];' % (tr(node.fullName()), '\n'.join(table)))
    
  # connect parameter values etc. to respective tree nodes if we can find them
  ParseConnections(node)


def ParseTree(node):
  if len(node.children) > 0:
    # we have to produce a cluster for this node
    nodelist.append("subgraph cluster_%s" % tr(node.fullName()))
    nodelist.append('{  label=<<B>%s</B>>;' % node.name)
    CreateParamTable(node, False)
    for nd_child in node.children.values():
      ParseTree(nd_child)
    nodelist.append('}')
  else:
    # no child nodes --> no cluster
    CreateParamTable(node, True)


if __name__ == '__main__':
  if (len(sys.argv) > 1):
    filename = os.path.abspath(sys.argv[1])
    basepath = os.path.dirname(filename)
    # since we also want to draw connections between different files
    # (for sub-apps), we first have to read them completely...
    global_root = ParseFile(filename, basepath)
    # ...before we parse their connections
    ParseTree(global_root)
    

    print 'strict digraph "%s" {' % sys.argv[1]
    print '\n'.join(gv_globalpars)
    print '\n'.join(nodelist)
    print '\n'.join(edgelist)

    print '}'
  else:
    print 'Usage %s filename' % sys.argv[0]