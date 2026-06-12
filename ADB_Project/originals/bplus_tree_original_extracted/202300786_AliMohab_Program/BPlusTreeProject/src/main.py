from BPlustree import BPlusTree


def main() -> None:
    tree = BPlusTree(order=3)

    tree.insert(10, "Record10")
    tree.insert(20, "Record20")
    tree.insert(5,  "Record5")
    tree.insert(15, "Record15")
    tree.insert(25, "Record25")
    tree.insert(30, "Record30")

    print("===== B+ Tree Structure =====")
    tree.display_tree()

    print()

    print("===== Range Search [10, 25] =====")
    results = tree.range_search(10, 25)
    for key, value in results:
        print(f"  {key} -> {value}")

    print()
    print("===== Extended Test: insert keys 1-50 =====")
    tree2 = BPlusTree(order=3)
    for k in range(1, 51):
        tree2.insert(k, f"Rec{k}")

    tree2.display_tree()

    print()
    print("===== Range Search [20, 30] =====")
    for key, value in tree2.range_search(20, 30):
        print(f"  {key} -> {value}")


if __name__ == "__main__":
    main()