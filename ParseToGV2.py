#!/usr/bin/env python

import sys, os
from ParseGetPot import GPNode, ParseGetPot

# GraphViz global parameters (default node shape and size, edge type, etc.)
gv_globalpars=['layout=dot;size="20,20";rankdir=LR;splines=true;pad="0";ranksep="1.5";nodesep="0.3"',
               'node[shape=box3d];'
               'edge[color="#808080";fontcolor="#808080"];']
               
globaloptions={'table_heading_style': 'BGCOLOR="#dddddd"', # HTML style for the parameter table headings
               'maxlen_param': 20, # maximum length (number of characters) for parameter names in parameter tables
               'maxlen_value': 35, # maximum length (number of characters) for parameter names in parameter tables
               'connection_ports' : True,  # if set to True, arrows point to entries in parameter tables. Otherwise, they point to the nodes
               'use_splines' : True # if True, splines are used for the edges. otherwise orthogonal connectors
              }

styles = { 'Kernels'       : {'color' : '#5457b0', 'fontcolor' : '#5457b0' },
           'Variables'     : {'color' : '#000cff', 'fontcolor' : '#000cff' },
           'ScalarKernels' : {'color' : '#000077', 'fontcolor' : '#000077' },
           'AuxKernels'    : {'color' : '#b07854', 'fontcolor' : '#b07854' },
           'AuxVariables'  : {'color' : '#ff6500', 'fontcolor' : '#ff6500' },
           'BCs'           : {'color' : '#ff00b6', 'fontcolor' : '#ff00b6' },
           'ICs'           : {'color' : '#be409a', 'fontcolor' : '#be409a' },
           'Materials'     : {'color' : '#4d9302', 'fontcolor' : '#4d9302' },
           'Mesh'          : {'color' : '#0000ff', 'fontcolor' : '#0000ff' },
           'Transfers'     : {'color' : '#ff0000', 'fontcolor' : '#ff0000' },
           'Splits'        : {'color' : '#ff00ff', 'fontcolor' : '#ff00ff' },
         }


# ports only work with splines...
if globaloptions['use_splines'] or globaloptions['connection_ports']:
  gv_globalpars[0] += ';splines=true'
else:
  gv_globalpars[0] += ';splines=ortho'
 

nodelist = []
edgelist = []
multiapp_nodes = {}


def tr(s):
  return s.replace('/','_').replace('.','_').replace(':','_').replace('-','_')


def attach_child(nd_parent, nd_child):
  nd_child.parent = nd_parent
  nd_parent.children[nd_child.name] = nd_child
  nd_parent.children_list.append(nd_child.name)


def getNode(search_root, name, **kwargs):
  if name in search_root.children:
    if 'excludenodes' in kwargs.keys():
      for excludenode in kwargs['excludenodes']:
        if excludenode == search_root.children[name].fullName():
          return None
    return search_root.children[name]
  else:
    for key, value in search_root.children.iteritems():
      node = getNode(value, name, **kwargs)
      if node != None:
        return node
  return None


# TODO: add preferrednodenames to start searching at Variables and AuxVariables
def search_upwards(node, search_string, **kwargs):
  # we first search local trees and slowly traverse upwards until we found something
  # this looks inefficient but enforces matches to be as local as possible
  parent = node
  while parent != None:
    nd = getNode(parent, search_string, **kwargs)
    parent = parent.parent
    if nd != None:
      return nd, True
  return None, False


def ParseFile(filename, basepath):
  nodes_found = []

  if not os.path.isabs(filename):
    filename = os.path.join(basepath,filename)
  
  if not os.path.isfile(filename):
    sys.stderr.write('Could not find sub-app input file %s. Ignoring.' % filename)
    return None
  else:
    # read the file into a GPNode object
    nd_file = ParseGetPot(filename).root_node
    nd_file.name = tr(os.path.basename(filename))
    nd_file.parent = None
    
    nodes_found.append(nd_file)
    # search it for any MultiApps
    nd_multiapp = getNode(nd_file, 'MultiApps')
    if nd_multiapp != None:
      # traverse over all possible sub-apps
      for nd_sub in nd_multiapp.children.values():
        # traverse over all entries in their 'input_files' parameter
        multiapp_nodes[nd_sub.name] = []
        for filename_sub in nd_sub.params['input_files'].split(' '):
          nodes_subfile = ParseFile(filename_sub, basepath)
          # we store references to the multiapp_nodes for simpler interconnection code in Transfer objects
          multiapp_nodes[nd_sub.name] += nodes_subfile
          nodes_found += nodes_subfile
          
    return nodes_found


def add_edge(nd_from, nd_to, **kwargs):
  name_to = tr(nd_to.fullName())
  name_from = tr(nd_from.fullName())

  if globaloptions['connection_ports']:
    if 'port_to' in kwargs.keys():
      name_to += ':%s' % kwargs['port_to']
    if 'port_from' in kwargs.keys():
      name_from += ':%s' % kwargs['port_from']

    edgelist.append('%s -> %s[];' % (name_from, name_to))
  else:
    edgelist.append('%s -> %s[%s="%s"];' % (name_from, name_to, kwargs['labeltype'], kwargs['label']))
    


def ParseConnections(node):
  for param, value in node.params.iteritems():
    # Try to connect regular parameters to respective blocks.
    # We first search local trees and traverse upwards until we found something
    # this looks inefficient but enforces matches to be as local as possible
    # * we prevent pointing to ourselves because no block will ever reference itself (I assume)
    # * we prefer starting our search in a Variables or AuxVariables block
    # * special handling for Transfer blocks (search the respective file first, redirect arrows appropriately)
    #   better reflect the data flow directions
    search_start_list = [node]
    if node.parent != None: # TODO: highlight transfer arrows
      if node.parent.name == 'Transfers':
        if (node.params['direction'] == 'to_multiapp'   and param == 'variable' ) or \
           (node.params['direction'] == 'from_multiapp' and param == 'source_variable' ):
          search_start_list = multiapp_nodes[node.params['multi_app']] + search_start_list
    
    for search_start in search_start_list:
      nd_connected, found = search_upwards(search_start, value, excludenodes=[node.fullName()], prefernodenames=['Variables', 'AuxVariables'])
      if found:
        if param == 'variable':
          # revert edge since this feels more natural
          add_edge(node, nd_connected, port_from='%s_VALUE' % tr(param), labeltype='taillabel', label=param)
        else:
          add_edge(nd_connected, node, port_to='%s_PARAM' % tr(param), labeltype='headlabel', label=param)
      break


def CreateParamTable(node):
  # add node name (and type if available) in a heading line with colored background
  table = ['<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">']
  table += ['<TR><TD COLSPAN="3" %s><B>%s&nbsp;</B>' % (globaloptions['table_heading_style'], tr(node.name))]
  if 'type' in node.params_list:
    table[-1] += ':&nbsp;%s' % node.params['type']
  table[-1] += '</TD></TR>'

  # create the tables for all parameters except 'type' (because this is in the headline already)
  for param, value in node.params.iteritems():
    if param != 'type':
      table += ['<TR><TD PORT="%s_PARAM">%s</TD><TD>=</TD><TD PORT="%s_VALUE">%s</TD></TR>' % (tr(param), param[0:globaloptions['maxlen_param']], tr(param), value[0:globaloptions['maxlen_value']])]

  table += ['</TABLE>']
  
  return table


def getStyle(nodename):
  style = ''
  if nodename in styles.keys():
    for key, val in styles[nodename].iteritems():
      style += '%s="%s"' % (key, val)
  return style


def ParseTree(node, parentstyle):
  global nodelist
  style = parentstyle + getStyle(node.name)
  table = CreateParamTable(node)
  
  if len(node.children) > 0:
    # we have to produce a cluster for this node
    nodelist.append("subgraph cluster_%s{label=<%s>;%s" % (tr(node.fullName()), '\n'.join(table), style))
    # include this node's children
    for nd_child in node.children.values():
      ParseTree(nd_child, style)
    nodelist.append('}')
  else:
    # no child nodes --> no cluster
    nodelist.append('%s[label=<%s>;%s];' % (tr(node.fullName()), '\n'.join(table), style))

  # connect parameter values etc. to respective tree nodes if we can find them
  ParseConnections(node)


if __name__ == '__main__':
  if (len(sys.argv) > 1):
    filename = os.path.abspath(sys.argv[1])
    basepath = os.path.dirname(filename)
    # since we also want to draw connections between different files
    # (for sub-apps), we first have to read them completely...
    global_root = GPNode('global_root', None)
    nodes_found = ParseFile(filename, basepath)
    for node in nodes_found:
      attach_child(global_root, node)
    # ...before we parse their connections
    for node in global_root.children.values():
      ParseTree(node,'')
    

    print 'strict digraph "%s" {' % sys.argv[1]
    print '\n'.join(gv_globalpars)
    print '\n'.join(nodelist)
    print '\n'.join(edgelist)

    print '}'
  else:
    print 'Usage %s filename' % sys.argv[0]