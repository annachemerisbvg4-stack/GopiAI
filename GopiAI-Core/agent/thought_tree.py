import json
from typing import Dict, List, Optional, Any


class ThoughtNode:
    """
    Represents a node in the thought tree.
    """

    def __init__(
        self,
        node_id: str,
        node_type: str,
        content: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.content = content
        self.parent_id = parent_id
        self.metadata = metadata or {}
        self.children: List[str] = []
        self.alternatives: List[str] = []


class ThoughtTree:
    """
    Represents a tree of thoughts for reasoning agent.
    """

    def __init__(self):
        self.nodes: Dict[str, ThoughtNode] = {}
        self.root: Optional[ThoughtNode] = None
        self.current_node_id: Optional[str] = None

    def to_json(self) -> str:
        """Serialize the thought tree to JSON."""
        tree_data = {
            "nodes": {
                node_id: {
                    "node_id": node.node_id,
                    "node_type": node.node_type,
                    "content": node.content,
                    "parent_id": node.parent_id,
                    "metadata": node.metadata,
                    "children": node.children,
                    "alternatives": node.alternatives,
                }
                for node_id, node in self.nodes.items()
            },
            "root_id": self.root.node_id if self.root else None,
            "current_node_id": self.current_node_id,
        }
        return json.dumps(tree_data, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_data: str) -> "ThoughtTree":
        """Create a thought tree from JSON data."""
        tree = cls()
        data = json.loads(json_data)

        # Recreate all nodes
        for node_id, node_data in data["nodes"].items():
            node = ThoughtNode(
                node_id=node_data["node_id"],
                node_type=node_data["node_type"],
                content=node_data["content"],
                parent_id=node_data["parent_id"],
                metadata=node_data["metadata"],
            )
            node.children = node_data["children"]
            node.alternatives = node_data["alternatives"]
            tree.nodes[node_id] = node

        # Set root and current node
        if data["root_id"] and data["root_id"] in tree.nodes:
            tree.root = tree.nodes[data["root_id"]]

        if data["current_node_id"] and data["current_node_id"] in tree.nodes:
            tree.current_node_id = data["current_node_id"]

        return tree
