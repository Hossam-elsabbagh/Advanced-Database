from __future__ import annotations
from typing import Optional


class BPlusTreeNode:


    def __init__(self, is_leaf: bool) -> None:
        self.is_leaf: bool = is_leaf
        self.keys: list[int] = []
        self.children: list["BPlusTreeNode"] = []   
        self.values: list[str] = []                  
        self.next: Optional["BPlusTreeNode"] = None  
        self.parent: Optional["BPlusTreeNode"] = None 

    def __repr__(self) -> str:
        kind = "Leaf" if self.is_leaf else "Internal"
        return f"BPlusTreeNode({kind}, keys={self.keys})"