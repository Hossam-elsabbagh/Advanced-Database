from flask import Flask, jsonify, render_template, request

from src.buffer_pool import BufferPool, parse_page_sequence
from src.bplus_tree import BPlusTree, parse_key_sequence

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/buffer/simulate", methods=["POST"])
def simulate_buffer():
    try:
        payload = request.get_json(force=True)
        size = int(payload.get("size", 3))
        policy = payload.get("policy", "LRU")
        pages = parse_page_sequence(payload.get("pages", ""))
        pool = BufferPool(size=size, policy=policy)
        return jsonify({"ok": True, "data": pool.simulate(pages)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.route("/api/bplustree/build", methods=["POST"])
def build_bplus_tree():
    try:
        payload = request.get_json(force=True)
        order = int(payload.get("order", 3))
        keys = parse_key_sequence(payload.get("keys", ""))
        value_prefix = payload.get("value_prefix", "Record") or "Record"
        range_start_raw = payload.get("range_start", "")
        range_end_raw = payload.get("range_end", "")

        tree = BPlusTree(order=order)
        tree.bulk_insert(keys, value_prefix=value_prefix)
        data = tree.to_dict()
        data["inserted_keys"] = keys
        data["display_lines"] = tree.display_lines()

        if str(range_start_raw).strip() and str(range_end_raw).strip():
            range_start = int(range_start_raw)
            range_end = int(range_end_raw)
            data["range"] = {
                "start": range_start,
                "end": range_end,
                "results": [{"key": k, "value": v} for k, v in tree.range_search(range_start, range_end)],
            }
        else:
            data["range"] = None

        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)
