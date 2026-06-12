from src.buffer_pool import BufferPool
from src.bplus_tree import BPlusTree


def buffer_demo() -> None:
    pages = [1, 2, 3, 1, 4, 2, 5]
    for policy in ["LRU", "LRU-2", "CLOCK", "2Q"]:
        pool = BufferPool(size=3, policy=policy)
        result = pool.simulate(pages)
        print(f"\n{policy}")
        print("Hits:", result["hits"], "Misses:", result["misses"], "Final:", result["final_buffer"])


def tree_demo() -> None:
    tree = BPlusTree(order=3)
    for key in [10, 20, 5, 15, 25, 30]:
        tree.insert(key)
    print("\nB+ Tree")
    print("\n".join(tree.display_lines()))
    print("Range [10, 25]:", tree.range_search(10, 25))


if __name__ == "__main__":
    buffer_demo()
    tree_demo()
