/**
 * Document Intelligence – PageIndex  |  Frontend Application
 *
 * Vanilla JS SPA that talks to the FastAPI backend.
 */

const API = "/api/v1";

// ── DOM refs ────────────────────────────────────────────────────
const $  = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const dom = {
    // nav
    sidebar:      $("#sidebar"),
    menuToggle:   $("#menuToggle"),
    navBtns:      $$(".nav-btn"),
    pageTitle:    $("#pageTitle"),

    // upload
    dropZone:     $("#dropZone"),
    fileInput:    $("#fileInput"),
    uploadProgress: $("#uploadProgress"),
    uploadFileName: $("#uploadFileName"),
    progressFill:   $("#progressFill"),
    uploadStatus:   $("#uploadStatus"),
    uploadResult:   $("#uploadResult"),
    resultDocId:    $("#resultDocId"),
    btnUploadAnother: $("#btnUploadAnother"),
    btnGoQuery:     $("#btnGoQuery"),

    // documents
    docTableBody: $("#docTableBody"),
    btnRefreshDocs: $("#btnRefreshDocs"),

    // query
    queryDocId:   $("#queryDocId"),
    queryText:    $("#queryText"),
    btnQuery:     $("#btnQuery"),
    queryResults: $("#queryResults"),
    queryLoading: $("#queryLoading"),
    thinkingText: $("#thinkingText"),
    nodesList:    $("#nodesList"),
    contextText:  $("#contextText"),
    answerText:   $("#answerText"),

    // status
    apiStatus:    $("#apiStatus"),

    // toast
    toastContainer: $("#toastContainer"),
};

const VIEW_TITLES = {
    upload:    "Upload Document",
    documents: "Documents",
    query:     "Query Document",
};

// ── State ───────────────────────────────────────────────────────
let lastDocId = null;

// ── Navigation ──────────────────────────────────────────────────
function switchView(viewName) {
    $$(".view").forEach((v) => v.classList.remove("active"));
    $(`#view-${viewName}`)?.classList.add("active");

    dom.navBtns.forEach((b) => {
        b.classList.toggle("active", b.dataset.view === viewName);
    });

    dom.pageTitle.textContent = VIEW_TITLES[viewName] || "";

    if (viewName === "documents") loadDocuments();
    dom.sidebar.classList.remove("open");
}

dom.navBtns.forEach((btn) =>
    btn.addEventListener("click", () => switchView(btn.dataset.view))
);

dom.menuToggle.addEventListener("click", () =>
    dom.sidebar.classList.toggle("open")
);

// ── Toast ────────────────────────────────────────────────────────
function toast(message, type = "info", duration = 4000) {
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.textContent = message;
    dom.toastContainer.appendChild(el);
    setTimeout(() => {
        el.style.opacity = "0";
        setTimeout(() => el.remove(), 300);
    }, duration);
}

// ── API helpers ──────────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
    const res = await fetch(`${API}${path}`, opts);
    const data = await res.json();
    if (!res.ok) {
        const msg = data.detail || JSON.stringify(data);
        throw new Error(msg);
    }
    return data;
}

// ── Health check ─────────────────────────────────────────────────
async function checkHealth() {
    const dot  = dom.apiStatus.querySelector(".status-dot");
    const text = dom.apiStatus.querySelector(".status-text");
    try {
        await fetch("/");
        dot.className  = "status-dot online";
        text.textContent = "API Online";
    } catch {
        dot.className  = "status-dot offline";
        text.textContent = "API Offline";
    }
}

// ── Upload ───────────────────────────────────────────────────────
function resetUploadUI() {
    dom.dropZone.classList.remove("hidden");
    dom.uploadProgress.classList.add("hidden");
    dom.uploadResult.classList.add("hidden");
    dom.progressFill.style.width = "0%";
}

async function uploadFile(file) {
    if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
        toast("Please select a PDF file.", "error");
        return;
    }

    // Show progress
    dom.dropZone.classList.add("hidden");
    dom.uploadResult.classList.add("hidden");
    dom.uploadProgress.classList.remove("hidden");
    dom.uploadFileName.textContent = file.name;
    dom.uploadStatus.textContent = "Uploading…";
    dom.progressFill.style.width = "30%";

    try {
        const formData = new FormData();
        formData.append("file", file);

        dom.progressFill.style.width = "60%";
        dom.uploadStatus.textContent = "Submitting to PageIndex…";

        const data = await apiFetch("/documents/upload", {
            method: "POST",
            body: formData,
        });

        dom.progressFill.style.width = "100%";
        lastDocId = data.doc_id;

        // Show success
        setTimeout(() => {
            dom.uploadProgress.classList.add("hidden");
            dom.uploadResult.classList.remove("hidden");
            dom.resultDocId.textContent = data.doc_id;
        }, 400);

        toast("Document uploaded successfully!", "success");
    } catch (err) {
        resetUploadUI();
        toast(err.message, "error");
    }
}

// Drag & drop
dom.dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dom.dropZone.classList.add("drag-over");
});
dom.dropZone.addEventListener("dragleave", () =>
    dom.dropZone.classList.remove("drag-over")
);
dom.dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dom.dropZone.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    uploadFile(file);
});
dom.dropZone.addEventListener("click", () => dom.fileInput.click());
dom.fileInput.addEventListener("change", () => {
    if (dom.fileInput.files[0]) uploadFile(dom.fileInput.files[0]);
});

dom.btnUploadAnother.addEventListener("click", resetUploadUI);
dom.btnGoQuery.addEventListener("click", () => {
    dom.queryDocId.value = lastDocId || "";
    switchView("query");
});

// ── Documents ────────────────────────────────────────────────────
async function loadDocuments() {
    try {
        const docs = await apiFetch("/documents/");
        if (!docs.length) {
            dom.docTableBody.innerHTML =
                '<tr><td colspan="4" class="empty-state">No documents yet. Upload one to get started.</td></tr>';
            return;
        }

        dom.docTableBody.innerHTML = "";
        for (const doc of docs) {
            const tr = document.createElement("tr");

            // Check status
            let statusHTML = '<span class="badge badge-checking">Checking…</span>';
            try {
                const st = await apiFetch(`/documents/${doc.doc_id}/status`);
                statusHTML = st.ready
                    ? '<span class="badge badge-success">Ready</span>'
                    : '<span class="badge badge-warning">Processing</span>';
            } catch { /* keep "checking" */ }

            tr.innerHTML = `
                <td><code>${doc.doc_id}</code></td>
                <td>${doc.filename}</td>
                <td>${statusHTML}</td>
                <td>
                    <button class="btn btn-sm btn-secondary btn-query-doc" data-docid="${doc.doc_id}">
                        Query
                    </button>
                </td>
            `;
            dom.docTableBody.appendChild(tr);
        }

        // Attach query buttons
        $$(".btn-query-doc").forEach((btn) =>
            btn.addEventListener("click", () => {
                dom.queryDocId.value = btn.dataset.docid;
                switchView("query");
            })
        );
    } catch (err) {
        toast(err.message, "error");
    }
}

dom.btnRefreshDocs.addEventListener("click", loadDocuments);

// ── Query ────────────────────────────────────────────────────────
dom.btnQuery.addEventListener("click", async () => {
    const docId = dom.queryDocId.value.trim();
    const query = dom.queryText.value.trim();

    if (!docId) { toast("Enter a Document ID.", "error"); return; }
    if (!query) { toast("Enter a question.", "error"); return; }

    dom.btnQuery.disabled = true;
    dom.queryResults.classList.add("hidden");
    dom.queryLoading.classList.remove("hidden");

    try {
        const data = await apiFetch("/inference/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ doc_id: docId, query }),
        });

        // Populate results
        dom.thinkingText.textContent = data.tree_search.thinking;

        // Nodes
        dom.nodesList.innerHTML = "";
        data.tree_search.retrieved_nodes.forEach((node) => {
            const chip = document.createElement("div");
            chip.className = "node-chip";
            chip.innerHTML = `
                <span class="node-title">${node.title || node.node_id}</span>
                <span class="node-meta">Page ${node.page_index ?? "—"}  ·  ${node.node_id}</span>
            `;
            dom.nodesList.appendChild(chip);
        });

        dom.contextText.textContent = data.context_preview;
        dom.answerText.textContent = data.answer;

        dom.queryLoading.classList.add("hidden");
        dom.queryResults.classList.remove("hidden");

        toast("Answer generated!", "success");
    } catch (err) {
        dom.queryLoading.classList.add("hidden");
        toast(err.message, "error");
    } finally {
        dom.btnQuery.disabled = false;
    }
});

// ── Collapsible sections ─────────────────────────────────────────
$$(".result-card-header[data-toggle]").forEach((header) => {
    header.addEventListener("click", () => {
        const body = $(`#${header.dataset.toggle}`);
        body.classList.toggle("collapsed");
        const chevron = header.querySelector(".chevron");
        if (chevron) {
            chevron.style.transform = body.classList.contains("collapsed")
                ? "rotate(-90deg)"
                : "rotate(0deg)";
        }
    });
});

// ── Init ─────────────────────────────────────────────────────────
checkHealth();
setInterval(checkHealth, 30_000);
