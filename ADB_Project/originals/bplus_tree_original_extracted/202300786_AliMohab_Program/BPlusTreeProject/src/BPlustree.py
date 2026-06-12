from __future__ import annotations
from Bplustreenode import BPlusTreeNode


class BPlusTree:


    def __init__(self, order: int = 3) -> None:
        self.order = order          
        self.root = BPlusTreeNode(is_leaf=True)


    def insert(self, key: int, value: str) -> None:
        leaf = self._find_leaf(self.root, key)
        self._insert_into_leaf(leaf, key, value)

        if len(leaf.keys) > self.order:
            self._split_leaf(leaf)

    def range_search(self, start: int, end: int) -> list[tuple[int, str]]:

        results: list[tuple[int, str]] = []
        current = self._find_leaf(self.root, start)

        while current is not None:
            for i, key in enumerate(current.keys):
                if key > end:
                    return results
                if key >= start:
                    results.append((key, current.values[i]))
            current = current.next

        return results

    def display_tree(self) -> None:
        self._display(self.root, level=0)


    def _find_leaf(self, node: BPlusTreeNode, key: int) -> BPlusTreeNode:
        if node.is_leaf:
            return node

        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1

        return self._find_leaf(node.children[i], key)

    def _insert_into_leaf(self, leaf: BPlusTreeNode,
                          key: int, value: str) -> None:
        """Insert key/value in sorted order inside a leaf node."""
        i = 0
        while i < len(leaf.keys) and key > leaf.keys[i]:
            i += 1
        leaf.keys.insert(i, key)
        leaf.values.insert(i, value)


    def _split_leaf(self, leaf: BPlusTreeNode) -> None:

        mid = (self.order + 1) // 2

        new_leaf = BPlusTreeNode(is_leaf=True)
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        # Maintain the leaf linked list
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

    def _insert_into_parent(self, left: BPlusTreeNode,
                            separator: int,
                            right: BPlusTreeNode) -> None:
   
        parent = left.parent

        idx = parent.children.index(left)
        parent.keys.insert(idx, separator)
        parent.children.insert(idx + 1, right)
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


    def _display(self, node: BPlusTreeNode, level: int) -> None:
        print(f"  Level {level}: {node.keys}{'  [leaf]' if node.is_leaf else ''}")
        if not node.is_leaf:
            for child in node.children:
                self._display(child, level + 1)




