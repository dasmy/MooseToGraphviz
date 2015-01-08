A GraphViz generator for MOOSE input files
==========================================

This script generates [GraphViz](http://www.graphviz.org) input files (known from the callgraph/dependency graph output of Doxygen) from input files for [MOOSE](http://mooseframework.org) applications.

Currently, due to limitations of the HTML parser of GraphViz, only svg output can make use of all features.
However, you can convert svg-files to any other graphics file format, e.g. using [Inkscape](http://www.inkscape.org).

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
An example output for MOOSEs [https://github.com/idaholab/moose/blob/devel/examples/ex20_user_objects/ex20.i](`ex20.i`) file reads

![ex20.i.svg](https://github.com/dasmy/MooseToGraphviz/raw/master/ex20.i.svg "ex20.i.svg")

Customization
-------------
There are not many customization options available, yet.
However, some parameters, default values, etc. can already be tuned by modifying `globaloptions` and `globalpars` in `ParseToGV.py`.
Available options are documented there.

Advanced Usage
--------------
### MOOSE example files
For getting an overview of all MOOSE example files, you might want to call (this version using `open` is for MacOS, changing it for Linux is trivial)

    for file in ~/workspace/moose/examples/*/*.i; do ./ParseToGV.py $file | dot -Tsvg > ${file}.svg && open -a firefox ${file}.svg; done
