A GraphViz generator for MOOSE input files
==========================================

This script generates [GraphViz](http://www.graphviz.org) input files (known from the callgraph/dependency graph output of Doxygen) from input files for [MOOSE](http://mooseframework.org) applications.
Since it has been hacked together in only few hours, it is still rather incomplete but already functional.

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
However, some parameters, default values, etc. can already be tuned by modifying `globaloptions` and `globalpars` in `ParseToGV.py`.
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

TODO
----
* Avoid pointing to self, e.g. in file:///Users/mathias/workspace/moose/modules/tensor_mechanics/tests/crystal_plasticity/crysp_user_object.i.svg .
  There, a kernel/BC has the same name as the variable. Maybe always start the search at variables?
* Think about how to deal with comments