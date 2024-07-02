from typing import Any, Dict, Iterator, Optional, Tuple, Union

import networkx as nx
import pandas as pd


class Node:
    def __init__(self, id: Union[int, str]) -> None:
        ...

    @property
    def id(self) -> Union[int, str]:
        ...

    def get_property(self, key: str) -> Any:
        ...

    def set_property(self, key: str, value: Any) -> None:
        ...

    def out_neighbours(self) -> Iterator["Node"]:
        ...

    def in_neighbours(self) -> Iterator["Node"]:
        ...


class Edge:
    def __init__(self, src: Union[int, str], dst: Union[int, str]) -> None:
        ...

    @property
    def src(self) -> Union[int, str]:
        ...

    @property
    def dst(self) -> Union[int, str]:
        ...

    def get_property(self, key: str) -> Any:
        ...

    def set_property(self, key: str, value: Any) -> None:
        ...


class Graph:
    def __init__(self) -> None:
        ...

    def add_node(
        self,
        id: Union[int, str],
        time: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...

    def add_edge(
        self,
        src: Union[int, str],
        dst: Union[int, str],
        time: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...

    def node_count(self) -> int:
        ...

    def edge_count(self) -> int:
        ...

    def nodes(self) -> Iterator[Node]:
        ...

    def edges(self) -> Iterator[Edge]:
        ...

    def to_pandas(self) -> pd.DataFrame:
        ...  # Returns a pandas DataFrame

    def to_networkx(self) -> nx.Graph:
        ...  # Returns a NetworkX graph


class GraphBuilder:
    def __init__(self) -> None:
        ...

    def add_node(
        self,
        id: Union[int, str],
        time: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> "GraphBuilder":
        ...

    def add_edge(
        self,
        src: Union[int, str],
        dst: Union[int, str],
        time: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> "GraphBuilder":
        ...

    def build(self) -> Graph:
        ...


class Algorithm:
    def __init__(self, graph: Graph) -> None:
        ...

    def run(self) -> Any:
        ...


class PageRank(Algorithm):
    def __init__(
        self,
        graph: Graph,
        damping_factor: float = 0.85,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> None:
        ...

    def run(self) -> Dict[Union[int, str], float]:
        ...


class ConnectedComponents(Algorithm):
    def __init__(self, graph: Graph) -> None:
        ...

    def run(self) -> Dict[Union[int, str], int]:
        ...


def load_graph(path: str) -> Graph:
    ...


def save_graph(graph: Graph, path: str) -> None:
    ...


# Constants
VERSION: str

# Type aliases
NodeID = Union[int, str]
EdgeID = Tuple[NodeID, NodeID]
PropertyDict = Dict[str, Any]


# Utility functions
def create_random_graph(num_nodes: int, num_edges: int) -> Graph:
    ...


def create_erdos_renyi_graph(num_nodes: int, probability: float) -> Graph:
    ...
