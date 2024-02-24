import cfpq_data as cfpq
import networkx as nx
from collections import namedtuple


Info = namedtuple("Info", ["number_of_nodes", "number_of_edges", "edges"])


def get_graph_info(name):
    graph = cfpq.graph_from_csv(cfpq.download(name))
    return Info(
        graph.number_of_nodes(), graph.number_of_edges(), graph.edges(data=True)
    )


def two_cycle_graph(path, n, m, labels=("a", "b")):
    g = cfpq.labeled_two_cycles_graph(n=n, m=m, labels=labels)
    dot = nx.drawing.nx_pydot.to_pydot(g)
    dot.write_raw(path)
