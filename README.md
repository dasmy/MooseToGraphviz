A GraphViz generator for MOOSE input files
==========================================

Input files for the [Multiphysics Object Oriented Simulation Environment (MOOSE)](http://mooseframework.org) tend to become more and more complex as simulated systems are converging towards realistic scales.
Especially when dealing with Multiapps, which are one of MOOSE's unique features, the rapidly become a mess.
This makes dealing with them rather difficult and - in particular for beginners - getting an overview over the employed relationships between kernels, materials, variables, aux-objects, etc. is cumbersome.

This script generates [GraphViz](http://www.graphviz.org) input files (known from the callgraph/dependency graph output of Doxygen) from input files for MOOSE applications.
These graphs are particularly suitable for getting a quick overview on what goes on inside an input file.

Since the script has been hacked together in only few hours, it is still rather incomplete but already functional.
For parsing the input file it makes use of the Python parser `ParseGetPot.py` from the MOOSE project that is also employed in the Peacock GUI.

Currently, due to limitations of the HTML parser of GraphViz, only svg output can make use of all features.
However, you can convert svg-files to any other graphics file format, e.g. using [Inkscape](http://www.inkscape.org) or (even simpler) [CairoSVG](http://cairosvg.org).

Usage
-----

Usage of the tool is pretty simple.
Just give the filename of your MOOSE input file on the command line, e.g.

    ./ParseToGV.py ~/workspace/moose/examples/ex03_coupling/ex03.i

The resulting GraphViz script is then printed to `stdout`.
An online conversion can be performed by redirecting the output to GraphViz via

    ./ParseToGV.py ~/workspace/moose/examples/ex03_coupling/ex03.i | dot -Tsvg > file.svg

Then, `file.svg` contains the produced graph.

Example
-------
An example output for MOOSEs [`ex10.i`](examples/ex10.i) file reads

![examples/ex20.i.svg](https://rawgit.com/dasmy/MooseToGraphviz/master/examples/ex10.i.svg)

For [`ex20.i`](examples/ex20.i), the output reads

![examples/ex20.i.svg](https://rawgit.com/dasmy/MooseToGraphviz/master/examples/ex20.i.svg)

Customization
-------------
There are not many customization options available, yet.
However, some parameters, default values, etc. can already be tuned by modifying `globaloptions`, `gv_globalpars`, `nodestyles`, and `edgestyles` in `ParseToGV.py`.
  * `gv_globalpars` contains the global GraphViz declarations such as default node and edge type, etc.
  * `nodestyles` and `edgestyles` declare colors and other style options for specific node types such as `[Variables]`, `[Kernels]`, etc. and their connecting edges.
  * `globaloptions` contains several knobs for fine-tuning the graph:
      * `table_heading_style`: HTML style for the parameter table headings.
      * `maxlen_param`, `maxlen_value`: Maximum length (number of characters) for parameter names/values in parameter tables.
      * `connection_ports` : If set to True, arrows point to entries in parameter tables. Otherwise, they point to the nodes.
      * `use_splines`      : If True, splines are used for the edges. Otherwise orthogonal connectors.
      * `includeparams`    : If False, parameter tables are not shown which reduces graph size considerably but also omits information.
      * `showactive`       : If set to False, node's `active` parameters are ignored for the output (usually they make output a bit messy but do not add much information).
      * `clusterstyle`     : Special style attributes for clusters (i.e. the large rectangles), in particular the position and formatting of the label.

Available options are documented there.

Advanced Usage
--------------
### MOOSE example files
For getting an overview of all MOOSE example files, you might want to call (this version using `open` is for MacOS, changing it for Linux is trivial)

    for file in ~/workspace/moose/examples/*/*.i; do ./ParseToGV.py $file | dot -Tsvg > ${file}.svg && open -a firefox ${file}.svg; done

### MultiApps
MultiApps are also supported, the sub-App input files are parsed automatically (if they can be found by the script).
You still only have to use

    ./ParseToGV.py master_app.i

A rather complex example is composed of [`delta_real_parameters.i`](examples/delta_real_parameters.i) and [`delta_real_parameters_sub.i`](examples/delta_real_parameters_sub.i) and yields

![examples/ex20.i.svg](https://rawgit.com/dasmy/MooseToGraphviz/master/examples/delta_real_parameters.i.svg)

Known Issues
------------
* Comments are currently completely ignored.
* Found another problem? - Please report an [Issue](https://github.com/dasmy/MooseToGraphviz/issues) - ideally with a minimal example of the offending input file. :smile:
