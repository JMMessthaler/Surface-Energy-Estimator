import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Literal, Union, Self

import networkx as nx
from matplotlib.pyplot import show
from networkx import Graph
from pydantic import BaseModel, RootModel, Field

import messthaler_wulff.mylog as mylog
from messthaler_wulff.math.bravais import CommonBravais, Bravais, plot_bravais
from messthaler_wulff.parsing.bravais import BravaisModel
from messthaler_wulff.parsing.common import NodeModel, list2vec


class FiniteGraphModel(BaseModel):
    type: Literal["finite"]
    nodes: list[NodeModel]
    edges: list[tuple[NodeModel, NodeModel]]

    def graph(self):
        graph = Graph()
        graph.add_nodes_from(list(map(list2vec, self.nodes)))
        graph.add_edges_from([(list2vec(a), list2vec(b), {"weight": -1}) for a, b in self.edges])
        for n in graph:
            graph.nodes[n]["weight"] = graph.degree(n)
        return graph


class GraphModel(RootModel):
    root: Union[BravaisModel, FiniteGraphModel] = Field(discriminator="type")


class GraphType:
    builtin: dict[Path, Self] = {}

    def __init__(self, value):
        self.value = value

    def bravais(self):
        assert isinstance(self.value, Bravais)
        return self.value

    def graph(self, args):
        match self.value:
            case Graph():
                assert len(args) == 0  # TODO
                return self.value
            case Bravais():
                assert len(args) == 1  # TODO
                return self.value.graph(int(args[0]))

        raise NotImplementedError(f"Function not implemented for type {type(self.value)}")

    def plot(self, args):
        match self.value:
            case Graph():
                nx.draw(self.graph(args))
                show()
                return
            case Bravais():
                g = self.graph(args)
                plot_bravais(self.value, g)
                show()
                return
        raise NotImplementedError(f"Function not implemented for type {type(self.value)}")

    @classmethod
    def from_model(cls, model) -> Self:
        match model:
            case GraphModel():
                return cls.from_model(model.root)
            case FiniteGraphModel():
                return cls(model.graph())
            case BravaisModel():
                return cls(model.bravais())
        raise NotImplementedError(f"Function not implemented for type {type(model)}")

    @classmethod
    def from_string(cls, string: str) -> Self:
        return cls.from_model(GraphModel.model_validate_json(string))

    @classmethod
    def from_path(cls, path: Path) -> Self:
        path = Path(path)

        if path in cls.builtin:
            return cls.builtin[path]

        if path == Path("-"):
            string = input("Enter graph/bravais json here: ")
        else:
            if not path.exists():
                mylog.log.error(f"File {path} does not exist")
                sys.exit()
            string = path.read_text()

        return cls.from_string(string)

    @classmethod
    def add_args(cls, parser: ArgumentParser):
        parser.add_argument("graph", type=GraphType.from_path)

    @classmethod
    def from_args(cls, args: Namespace) -> Self:
        return args.graph

    @classmethod
    def add_args_graph(cls, parser: ArgumentParser):
        cls.add_args(parser)
        parser.add_argument("-p", "--graph-parameter", type=int, default=None)

    @classmethod
    def graph_from_args(cls, args: Namespace) -> Graph:
        graph_type = cls.from_args(args)
        graph_params = [] if args.graph_parameter is None else [args.graph_parameter]

        return graph_type.graph(graph_params)


for bravais in CommonBravais:
    GraphType.builtin[Path(bravais.name)] = GraphType(bravais.value)
