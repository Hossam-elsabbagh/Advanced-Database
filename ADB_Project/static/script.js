async function postJSON(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!result.ok) {
        throw new Error(result.error || "Unknown error");
    }
    return result.data;
}

function showError(id, message) {
    document.getElementById(id).textContent = message || "";
}

function renderBufferSummary(data) {
    const summary = document.getElementById("buffer-summary");
    summary.innerHTML = "";
    const items = [
        `Policy: ${data.policy}`,
        `Buffer Size: ${data.buffer_size}`,
        `Hits: ${data.hits}`,
        `Misses: ${data.misses}`,
        `Hit Rate: ${(data.hit_rate * 100).toFixed(2)}%`,
        `Final Buffer: [${data.final_buffer.join(", ")}]`,
    ];
    for (const item of items) {
        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = item;
        summary.appendChild(badge);
    }
}

function renderBufferTable(data) {
    const table = document.getElementById("buffer-table");
    table.innerHTML = `
        <thead>
            <tr>
                <th>Step</th>
                <th>Page</th>
                <th>Status</th>
                <th>Evicted</th>
                <th>Buffer</th>
                <th>Extra State</th>
                <th>Explanation</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;
    const tbody = table.querySelector("tbody");
    for (const step of data.steps) {
        let extra = "-";
        if (data.policy === "2Q") {
            extra = `A1in: [${step.a1in.join(", ")}] | Am: [${step.am.join(", ")}]`;
        } else if (data.policy === "CLOCK") {
            extra = `Reference bits: ${JSON.stringify(step.clock_reference_bits)}`;
        }
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${step.step}</td>
            <td>${step.page}</td>
            <td>${step.status}</td>
            <td>${step.evicted ?? "-"}</td>
            <td>[${step.buffer.join(", ")}]</td>
            <td>${extra}</td>
            <td>${step.message}</td>
        `;
        tbody.appendChild(row);
    }
}

document.getElementById("run-buffer").addEventListener("click", async () => {
    showError("buffer-error", "");
    try {
        const data = await postJSON("/api/buffer/simulate", {
            policy: document.getElementById("buffer-policy").value,
            size: document.getElementById("buffer-size").value,
            pages: document.getElementById("buffer-pages").value,
        });
        renderBufferSummary(data);
        renderBufferTable(data);
    } catch (error) {
        showError("buffer-error", error.message);
    }
});

function renderTree(data) {
    const treeView = document.getElementById("tree-view");
    treeView.innerHTML = "";

    data.levels.forEach((level, index) => {
        const levelDiv = document.createElement("div");
        levelDiv.className = "level";
        const title = document.createElement("div");
        title.className = "level-title";
        title.textContent = `Level ${index}`;
        const row = document.createElement("div");
        row.className = "node-row";

        level.forEach((node) => {
            const nodeDiv = document.createElement("div");
            nodeDiv.className = `node ${node.type}`;
            nodeDiv.innerHTML = `<span class="node-type">${node.type}</span>[${node.keys.join(" | ")}]`;
            row.appendChild(nodeDiv);
        });

        levelDiv.appendChild(title);
        levelDiv.appendChild(row);
        treeView.appendChild(levelDiv);
    });
}

function renderLeafChain(data) {
    const chain = document.getElementById("leaf-chain");
    chain.innerHTML = "<strong>Leaf Chain</strong><br>";
    data.leaf_chain.forEach((leaf, index) => {
        const item = document.createElement("span");
        item.className = "chain-item";
        item.textContent = `[${leaf.keys.join(", ")}]`;
        chain.appendChild(item);
        if (index < data.leaf_chain.length - 1) {
            chain.append(" -> ");
        }
    });
}

function renderRange(data) {
    const rangeDiv = document.getElementById("range-results");
    if (!data.range) {
        rangeDiv.innerHTML = "<strong>Range Search</strong><br>No range entered.";
        return;
    }
    const results = data.range.results.map(item => `${item.key} -> ${item.value}`).join("<br>") || "No records found.";
    rangeDiv.innerHTML = `<strong>Range Search [${data.range.start}, ${data.range.end}]</strong><br>${results}`;
}

document.getElementById("build-tree").addEventListener("click", async () => {
    showError("tree-error", "");
    try {
        const data = await postJSON("/api/bplustree/build", {
            order: document.getElementById("tree-order").value,
            keys: document.getElementById("tree-keys").value,
            value_prefix: document.getElementById("value-prefix").value,
            range_start: document.getElementById("range-start").value,
            range_end: document.getElementById("range-end").value,
        });
        renderTree(data);
        renderLeafChain(data);
        renderRange(data);
    } catch (error) {
        showError("tree-error", error.message);
    }
});

window.addEventListener("load", () => {
    document.getElementById("run-buffer").click();
    document.getElementById("build-tree").click();
});
