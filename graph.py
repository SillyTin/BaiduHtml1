from graphviz import Digraph

g = Digraph('graph')
g.node('a')
g.node('b')
g.edge('a','b')
g.view()