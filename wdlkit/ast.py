from functools import total_ordering
from pathlib import Path
from typing import Iterable, Sequence, Type

import networkx as nx
from networkx.algorithms.dag import lexicographical_topological_sort
from WDL import Call, Conditional, Decl, Scatter, WorkflowNode, load
from WDL.CLI import read_source


HEAD = object()
NODE_TYPE_ORDERING = {
    Decl: 0,
    Call: 1,
    Conditional: 2,
    Scatter: 3,
}


@total_ordering
class WorkflowBodyGraphNode:
    def __init__(self, node: WorkflowNode, index: int):
        self.node = node
        self.index = index
        self._tuple = None

    def _as_tuple(self) -> [Type[WorkflowNode], int]:
        if self._tuple is None:
            self._tuple = (type(self.node), self.index)

        return self._tuple

    def __eq__(self, other: "WorkflowBodyGraphNode"):
        return self._as_tuple() == other._as_tuple()

    def __lt__(self, other: "WorkflowBodyGraphNode"):
        return self._as_tuple() < other._as_tuple()


class WorkflowBodyGraph(nx.DiGraph):
    def __init__(self, *nodes: WorkflowNode):
        super().__init__()
        self.add_node(HEAD, index=0)
        self._index = 1

        if nodes:
            self.add_workflow_nodes(*nodes)

    def add_workflow_nodes(self, *nodes: WorkflowNode):
        """
        Adds `WorkflowNode`s to the graph.

        Args:
            nodes: `WorkflowNode`s
        """
        for node in nodes:
            if not self.has_node(node.workflow_node_id):
                self.add_node(
                    node.workflow_node_id,
                    workflow_node=WorkflowBodyGraphNode(node, self._index)
                )
            elif "workflow_node" not in self[node.workflow_node_id]:
                self[node.workflow_node_id]["workflow_node"] = WorkflowBodyGraphNode(
                    node, self._index
                )
            else:
                raise ValueError("Graph has cycle or duplicate node")

            self._index += 1

            for dep in (node.workflow_node_dependencies or [HEAD]):
                self.add_edge(dep, node.workflow_node_id)

    def dependency_order(self) -> Iterable[WorkflowBodyGraphNode]:
        """
        Sorts nodes in topological order, with ties broken by 1. the type of node, and
        2. the order in which the node was added.

        Returns:
            An `Iterable` over the `WorkflowNode`s in the graph.
        """
        return lexicographical_topological_sort(self)


def load_document(uri: str, import_dir: Sequence[Path] = ()):
    return load(uri, path=import_dir, read_source=read_source, check_quant=False)
