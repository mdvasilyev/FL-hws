import project.task1 as task1
from tempfile import NamedTemporaryFile
from textwrap import dedent


def test_graph_info():
    info = task1.get_graph_info("skos")
    assert 144 == info.number_of_nodes
    assert 252 == info.number_of_edges


def test_graph_save():
    path = ""
    with NamedTemporaryFile(delete=False) as f:
        path = f.name
    task1.two_cycle_graph(path, 2, 3, ("first", "second"))
    with open(path) as f:
        contents = "".join(f.readlines())
        expected = """\
            digraph  {
            1;
            2;
            0;
            3;
            4;
            5;
            1 -> 2  [key=0, label=first];
            2 -> 0  [key=0, label=first];
            0 -> 1  [key=0, label=first];
            0 -> 3  [key=0, label=second];
            3 -> 4  [key=0, label=second];
            4 -> 5  [key=0, label=second];
            5 -> 0  [key=0, label=second];
            }
            """
        expected = dedent(expected)
        contents = dedent(contents)
        assert expected == contents
