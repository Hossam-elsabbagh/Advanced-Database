from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(eq=False)
class BPlusTreeNode:
    is_leaf: bool

    def __post_init__(self) -> None:
        self.keys: list[int] = []
        self.children: list[BPlusTreeNode] = []
        self.values: list[str] = []
        self.next: BPlusTreeNode | None = None
        self.parent: BPlusTreeNode | None = None

    def __repr__(self) -> str:
        node_type = "Leaf" if self.is_leaf else "Internal"
        return f"BPlusTreeNode({node_type}, keys={self.keys})"


class BPlusTree:
    """Simple B+ Tree with insertion, range search, and JSON-friendly visualization."""

    def __init__(self, order: int = 3) -> None:
        if order < 2:
            raise ValueError("Order must be at least 2.")
        self.order = order
        self.root = BPlusTreeNode(is_leaf=True)

    def insert(self, key: int, value: str | None = None) -> None:
        if value is None:
            value = f"Record{key}"
        leaf = self._find_leaf(self.root, key)
        self._insert_into_leaf(leaf, key, value)
        if len(leaf.keys) > self.order:
            self._split_leaf(leaf)

    def bulk_insert(self, keys: list[int], value_prefix: str = "Record") -> None:
        for key in keys:
            self.insert(key, f"{value_prefix}{key}")

    def search(self, key: int) -> str | None:
        leaf = self._find_leaf(self.root, key)
        for index, existing_key in enumerate(leaf.keys):
            if existing_key == key:
                return leaf.values[index]
        return None

    def range_search(self, start: int, end: int) -> list[tuple[int, str]]:
        if start > end:
            start, end = end, start
        results: list[tuple[int, str]] = []
        current = self._find_leaf(self.root, start)

        while current is not None:
            for index, key in enumerate(current.keys):
                if key > end:
                    return results
                if key >= start:
                    results.append((key, current.values[index]))
            current = current.next
        return results

    def levels(self) -> list[list[dict[str, Any]]]:
        output: list[list[dict[str, Any]]] = []
        queue: list[tuple[BPlusTreeNode, int]] = [(self.root, 0)]
        while queue:
            node, level = queue.pop(0)
            if len(output) <= level:
                output.append([])
            output[level].append({
                "type": "leaf" if node.is_leaf else "internal",
                "keys": list(node.keys),
                "values": list(node.values) if node.is_leaf else [],
            })
            if not node.is_leaf:
                for child in node.children:
                    queue.append((child, level + 1))
        return output

    def leaf_chain(self) -> list[dict[str, Any]]:
        current = self.root
        while not current.is_leaf:
            current = current.children[0]
        leaves: list[dict[str, Any]] = []
        while current:
            leaves.append({"keys": list(current.keys), "values": list(current.values)})
            current = current.next
        return leaves

    def to_dict(self) -> dict[str, Any]:
        return {
            "order": self.order,
            "levels": self.levels(),
            "leaf_chain": self.leaf_chain(),
        }

    def display_lines(self) -> list[str]:
        lines: list[str] = []
        self._display(self.root, 0, lines)
        return lines

    def _find_leaf(self, node: BPlusTreeNode, key: int) -> BPlusTreeNode:
        if node.is_leaf:
            return node
        index = 0
        while index < len(node.keys) and key >= node.keys[index]:
            index += 1
        return self._find_leaf(node.children[index], key)

    def _insert_into_leaf(self, leaf: BPlusTreeNode, key: int, value: str) -> None:
        index = 0
        while index < len(leaf.keys) and key > leaf.keys[index]:
            index += 1
        if index < len(leaf.keys) and leaf.keys[index] == key:
            leaf.values[index] = value
            return
        leaf.keys.insert(index, key)
        leaf.values.insert(index, value)

    def _split_leaf(self, leaf: BPlusTreeNode) -> None:
        mid = (self.order + 1) // 2
        new_leaf = BPlusTreeNode(is_leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        new_leaf.next = leaf.next
        leaf.next = new_leaf
        separator = new_leaf.keys[0]

        if leaf is self.root:
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.keys = [separator]
            new_root.children = [leaf, new_leaf]
            leaf.parent = new_root
            new_leaf.parent = new_root
            self.root = new_root
        else:
            new_leaf.parent = leaf.parent
            self._insert_into_parent(leaf, separator, new_leaf)

    def _insert_into_parent(self, left: BPlusTreeNode, separator: int, right: BPlusTreeNode) -> None:
        parent = left.parent
        if parent is None:
            raise RuntimeError("Cannot insert into a missing parent.")
        index = parent.children.index(left)
        parent.keys.insert(index, separator)
        parent.children.insert(index + 1, right)
        right.parent = parent
        if len(parent.keys) > self.order:
            self._split_internal(parent)

    def _split_internal(self, node: BPlusTreeNode) -> None:
        mid = len(node.keys) // 2
        median = node.keys[mid]
        right = BPlusTreeNode(is_leaf=False)
        right.keys = node.keys[mid + 1:]
        right.children = node.children[mid + 1:]
        for child in right.children:
            child.parent = right

        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]

        if node is self.root:
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.keys = [median]
            new_root.children = [node, right]
            node.parent = new_root
            right.parent = new_root
            self.root = new_root
        else:
            right.parent = node.parent
            self._insert_into_parent(node, median, right)

    def _display(self, node: BPlusTreeNode, level: int, lines: list[str]) -> None:
        suffix = " [leaf]" if node.is_leaf else ""
        lines.append(f"Level {level}: {node.keys}{suffix}")
        if not node.is_leaf:
            for child in node.children:
                self._display(child, level + 1, lines)


def parse_key_sequence(text: str) -> list[int]:
    if not text or not text.strip():
        raise ValueError("Enter at least one key.")
    parts = text.replace("\n", ",").replace(";", ",").split(",")
    keys: list[int] = []
    for part in parts:
        stripped = part.strip()
        if not stripped:
            continue
        try:
            keys.append(int(stripped))
        except ValueError as exc:
            raise ValueError(f"Invalid key: {stripped}") from exc
    if not keys:
        raise ValueError("Enter at least one key.")
    return keys
