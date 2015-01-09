#!/usr/bin/env python

import sys, os
from ParseGetPot import GPNode, ParseGetPot

globaloptions = {'includeparams'    : True,  # if False, parameters are not shown which reduces graph size considerably
                 'maxlen_value'     : 35,    # maximum length (characters) of values in param fields
                 'connection_ports' : True,  # if set to True, arrows point to entries in parameter tables. Otherwise, they point to the nodes
                 'showactive'       : False, # if set to False, node's "active" parameters are ignored for the output (usually they make output a bit messy but do not add much information)
                 }

styles = { 'Kernels'       : {'color' : '#5457b0', 'fontcolor' : '#5457b0' },
           'Variables'     : {'color' : '#000cff', 'fontcolor' : '#000cff' },
           'ScalarKernels' : {'color' : '#000077', 'fontcolor' : '#000077' },
           'AuxKernels'    : {'color' : '#b07854', 'fontcolor' : '#b07854' },
           'AuxVariables'  : {'color' : '#ff6500', 'fontcolor' : '#ff6500' },
           'BCs'           : {'color' : '#ff00b6', 'fontcolor' : '#ff00b6' },
           'ICs'           : {'color' : '#be409a', 'fontcolor' : '#be409a' },
           'Materials'     : {'color' : '#aad76e', 'fontcolor' : '#aad76e' },
           'Mesh'          : {'color' : '#0000ff', 'fontcolor' : '#0000ff' },
           'Transfers'     : {'color' : '#ff0000', 'fontcolor' : '#ff0000' },
           'Splits'        : {'color' : '#ff00ff', 'fontcolor' : '#ff00ff' },
         }


globalpars=['layout=dot;size="20,20";rankdir=LR;splines=true;pad="0";ranksep="1.5";nodesep="0.3"',
            'node[shape=box3d];'
            'edge[color="#808080";fontcolor="#808080"];']
            
# ports only work with splines... :-(
if globaloptions['connection_ports']:
  globalpars[0] += ';splines=true'
else:
  globalpars[0] += ';splines=ortho'
  
nodelist = []
edgelist = []
sub_list = {} # this list will be used to store the root nodes of all multiapps to simplify interconnection


def tr(s):
  return s.replace('/','_').replace('.','_').replace(':','_').replace('-','_')


def search_upwards(node, search_string):
  # we first search local trees and slowly traverse upwards until we found something
  # this looks inefficient but enforces matches to be as local as possible
  parent = node
  while parent != None:
    nd = parent.getNode(search_string)
    parent = parent.parent
    if nd != None:
      return nd, True
  return None, False


def add_edge(label, param, value, nd_from, nd_to, addedrow, style):
  # we revert all arrows for 'variable' parameters since this feels more logical
  revert = param == 'variable'

  if globaloptions['connection_ports']:
    if not addedrow: # avoid having multiple identical table rows in the case "displacements='dx dy dz'"
      if revert:
        label += ['<TR><TD>%s</TD><TD>=</TD><TD PORT="%s">%s</TD></TR>' % (param, param, value[0:globaloptions['maxlen_value']])]
      else:
        label += ['<TR><TD PORT="%s">%s</TD><TD>=</TD><TD>%s</TD></TR>' % (param, param, value[0:globaloptions['maxlen_value']])]
      addedrow = True
    if revert:
      edgelist.append('%s:%s -> %s[%s];' % (tr(nd_to.fullName()), param, tr(nd_from.fullName()), style ))
    else:
      edgelist.append('%s -> %s:%s[%s];' % (tr(nd_from.fullName()), tr(nd_to.fullName()), param, style ))
  else:
    if revert:
      edgelist.append('%s -> %s[taillabel="%s";%s];' % (tr(nd_to.fullName()), tr(nd_from.fullName()), param, style ))
    else:
      edgelist.append('%s -> %s[headlabel="%s";%s];' % (tr(nd_from.fullName()), tr(nd_to.fullName()), param, style ))
  return label, addedrow


def ParseNodes(nodes, global_root, parentstyle):
  for node in nodes:
    label = ['<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">',
             '<TR><TD COLSPAN="3" BGCOLOR="#cccccc"><B>%s&nbsp;</B>' % tr(node.name)]
    # if there is a type attribute, we add it to the label line
    if 'type' in node.params_list:
      label[-1] += ':&nbsp;%s' % node.params['type']
    label[-1] += '</TD></TR>'
    
    # parse parameters, we count how much we found to avoid showing empty tables for clusters
    foundparams = 0
    for param, value in node.params.iteritems():
      if param == 'active' and not globaloptions['showactive']:
        continue
      found = False
      addedrow = False
      foundparams += 1
      for valpart in value.split(' '): # treat "displacements='dx dy dz'" separately

        if node.fullName().find('Transfers') >= 0:
          # special handling for Transfers since they interconnect different multiapps
          if (node.params['direction'] == 'to_multiapp'   and param == 'variable' ) or \
             (node.params['direction'] == 'from_multiapp' and param == 'source_variable' ):
            for nd_multi in sub_list[node.params['multi_app']]:
              nd, found = search_upwards(nd_multi, valpart)
              if found:
                label, addedrow = add_edge(label, param, value, nd, node, addedrow, 'color="%s"' % styles['Transfers']['color'])
                break
            continue
          else:
            if (node.params['direction'] == 'to_multiapp'   and param == 'source_variable' ) or \
               (node.params['direction'] == 'from_multiapp' and param == 'variable' ):
              nd, found = search_upwards(node, valpart)
              if found:
                label, addedrow = add_edge(label, param, value, nd, node, addedrow, 'color="%s"' % styles['Transfers']['color'])
          
        # regular parameter inside or outside a Transfer block
        # we first search local trees and slowly traverse upwards until we found something
        # this looks inefficient but enforces matches to be as local as possible
        nd, found = search_upwards(node, valpart)
        if found:
          label, addedrow = add_edge(label, param, value, nd, node, addedrow, '')

      if globaloptions['includeparams'] and not found and param != 'type':
          label += ['<TR><TD>%s</TD><TD>=</TD><TD>%s</TD></TR>' % (param, value[0:globaloptions['maxlen_value']])]
          
    label += ['</TABLE>']
  
    if len(node.children) > 0:
      if node.name != 'global_root': # no frame around global root node
        nodelist.append("subgraph cluster_%s" % node.name)
      nodelist.append('{  label=<<B>%s</B>>;' % node.name)
      style=''
      if node.name in styles.keys():
        for key, val in styles[node.name].iteritems():
          style += '%s="%s";' % (key, val)
        nodelist.append(style)
      if foundparams > 0: # only add tables that contain content
        nodelist.append('%s[label=<%s>, shape=plaintext];' % (tr(node.fullName()), '\n'.join(label)))
      # parse this node's children
      ParseNodes(node.children.values(), global_root, style)
      nodelist.append("}")
    else:
      nodelist.append('%s[label=<%s>;%sfontcolor="black"];' % (tr(node.fullName()), '\n'.join(label), parentstyle))


def ParseFiles(global_root, sub_apps, basepath):
  new_sub_apps={}
  
  for sub, filenames in sub_apps.iteritems():
    sub_list[sub] = []
    for filename in filenames:
      if not os.path.isabs(filename):
        filename = os.path.join(basepath,filename)
      
      if os.path.isfile(filename):
        file_root = ParseGetPot(filename).root_node
        sub_list[sub].append(file_root)
        file_root.name = tr(os.path.basename(filename))
        file_root.parent = global_root
    
        global_root.children[filename] = file_root
        global_root.children_list.append(filename)

        nd_sub = file_root.getNode('MultiApps')
        if nd_sub != None:
          for nd_multi in nd_sub.children.values():
            new_sub_apps[nd_multi.name] = nd_multi.params['input_files'].split(' ')

  return new_sub_apps


if __name__ == '__main__':
  if (len(sys.argv) > 1):
    filename = os.path.abspath(sys.argv[1])
    basepath = os.path.dirname(filename)

    # we will attach all multi-apps below this root node
    global_root = GPNode('global_root', None)
    sub_apps = {'main' : [filename]}

    while len(sub_apps) > 0:
      sub_apps = ParseFiles(global_root, sub_apps, basepath)
    
    ParseNodes(global_root.children.values(), global_root, '')

    print 'strict digraph "%s" {' % sys.argv[1]
    print '\n'.join(globalpars)
    print '\n'.join(nodelist)
    print '\n'.join(edgelist)

    print '}'
    
    #print 'Printing tree'
    #pgp.root_node.Print()
  else:
    print 'Usage %s filename' % sys.argv[0]