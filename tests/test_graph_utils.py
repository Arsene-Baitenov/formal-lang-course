import pytest
from typing import List, Any
from pathlib import Path
import networkx as nx

from project.graph_utils import get_graph, create_labeled_two_cycles_graph


@pytest.mark.parametrize(
    "name, num_nodes, num_edges, edge_labels",
    [
        ("bzip", 632, 556, ["d", "a"]),
        (
            "generations",
            129,
            273,
            [
                "type",
                "first",
                "rest",
                "onProperty",
                "intersectionOf",
                "equivalentClass",
                "someValuesFrom",
                "hasValue",
                "hasSex",
                "hasChild",
                "hasParent",
                "inverseOf",
                "sameAs",
                "hasSibling",
                "oneOf",
                "range",
                "versionInfo",
            ],
        ),
    ],
)
def test_get_graph(name: str, num_nodes: int, num_edges: int, edge_labels: List[Any]):
    graph = get_graph(name)
    assert graph.num_nodes == num_nodes
    assert graph.num_edges == num_edges
    assert graph.edge_labels == edge_labels


dir_name = Path(Path.cwd(), "labeled_two_cycles_graph_tmp")


@pytest.fixture()
def resource_setup(request):
    Path.mkdir(dir_name)

    def resource_teardown():
        for item in dir_name.iterdir():
            item.unlink()
        Path.rmdir(dir_name)

    request.addfinalizer(resource_teardown)


@pytest.mark.usefixtures("resource_setup")
def test_create_labeled_two_cycles_graph():
    path = str(Path(dir_name, "labeled_two_cycles_graph"))
    num_first_cycle_nodes = 2
    num_second_cycle_nodes = 3
    labels = ("a", "b")

    create_labeled_two_cycles_graph(
        num_first_cycle_nodes, num_second_cycle_nodes, labels, path
    )

    actual_graph = nx.nx_pydot.read_dot(path)

    expected_graph = nx.MultiDiGraph(
        [
            (0, 1, dict(label="a")),
            (1, 2, dict(label="a")),
            (2, 0, dict(label="a")),
            (0, 3, dict(label="b")),
            (3, 4, dict(label="b")),
            (4, 5, dict(label="b")),
            (5, 0, dict(label="b")),
        ]
    )

    assert nx.is_isomorphic(actual_graph, expected_graph)
