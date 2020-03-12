from pathlib import Path
from typing import Iterator, Sequence

import networkx as nx
from networkx.algorithms.dag import lexicographical_topological_sort
from WDL import Call, Conditional, Decl, Scatter, WorkflowNode, load
from WDL.CLI import read_source


HEAD_ID = "__HEAD__"
NODE_TYPE_ORDERING = {
    Decl: 1,
    Call: 2,
    Conditional: 3,
    Scatter: 4,
}


class WorkflowBodyGraph(nx.DiGraph):
    def __init__(self, *nodes: WorkflowNode):
        super().__init__()
        self.add_node(HEAD_ID, key=(0, 0))
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
            for dep in node.workflow_node_dependencies or [HEAD_ID]:
                if not self.has_node(dep):
                    self.add_node(dep, index=self._index)
                    self._index += 1

                self.add_edge(dep, node.workflow_node_id)

            node_attrs = {
                "workflow_node": node,
                "key": (NODE_TYPE_ORDERING[type(node)], self._index),
            }

            if not self.has_node(node.workflow_node_id):
                self.add_node(node.workflow_node_id, index=self._index, **node_attrs)
                self._index += 1
            else:
                attrs = self.nodes[node.workflow_node_id]

                if "workflow_node" in attrs:
                    raise ValueError("Graph has cycle or duplicate node")

                self.nodes[node.workflow_node_id].update(node_attrs)

                if "index" not in attrs:
                    attrs["index"] = self._index
                    self._index += 1

    def dependency_order(self) -> Iterator[WorkflowNode]:
        """
        Sorts nodes in topological order, with ties broken by 1. the type of node, and
        2. the order in which the node was added.

        Returns:
            An `Iterator` over the `WorkflowNode`s in the graph.
        """
        prune = [key for (key, value) in self.nodes.items() if "key" not in value]

        if prune:
            graph = self.copy()

            for nid in prune:
                graph.remove_node(nid)
        else:
            graph = self

        itr = iter(
            lexicographical_topological_sort(
                graph, key=lambda nid: self.nodes[nid]["key"]
            )
        )
        first = next(itr)

        if first != HEAD_ID:
            raise ValueError(f"Expected first node to be HEAD, instead got {first}")

        for node_id in itr:
            yield self.nodes[node_id]["workflow_node"]


def load_document(uri: str, import_dir: Sequence[Path] = ()):
    return load(uri, path=import_dir, read_source=read_source, check_quant=False)
