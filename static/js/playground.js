const editor = document.getElementById("codeEditor");
const output = document.getElementById("output");
const status = document.getElementById("status");
const runBtn = document.getElementById("runBtn");
const clearBtn = document.getElementById("clearBtn");
const saveBtn = document.getElementById("saveBtn");
const exampleBar = document.getElementById("exampleBar");
const snippetList = document.getElementById("snippetList");

const exampleNames = [
    { id: "hello", label: "Hello" },
    { id: "variables", label: "Variables" },
    { id: "conditionals", label: "Conditionals" },
    { id: "functions", label: "Functions" },
    { id: "loops", label: "Loops" },
    { id: "lists", label: "Lists" },
    { id: "vault", label: "Vault" },
    { id: "classes", label: "Classes" },
    { id: "ai", label: "AI Demo" }
];

let examples = {};

async function loadExamples() {
    try {
        const res = await fetch("/api/examples");
        examples = await res.json();
        exampleBar.innerHTML = "";
        exampleNames.forEach(ex => {
            const btn = document.createElement("button");
            btn.className = "example-btn";
            btn.textContent = ex.label;
            btn.onclick = () => {
                if (examples[ex.id]) {
                    editor.value = examples[ex.id];
                    output.textContent = "Example loaded. Click Run.";
                    output.className = "output-area";
                    status.textContent = "Ready";
                    status.className = "status";
                }
            };
            exampleBar.appendChild(btn);
        });
    } catch (e) {
        console.error("Failed to load examples", e);
    }
}

async function runCode() {
    const code = editor.value;
    status.textContent = "Running...";
    status.className = "status running";
    output.textContent = "";
    output.className = "output-area";
    runBtn.disabled = true;

    try {
        const res = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code })
        });
        const data = await res.json();

        if (data.success) {
            output.textContent = data.output || "(no output)";
            output.className = "output-area success";
            status.textContent = "Success";
            status.className = "status ok";
        } else {
            output.textContent = data.error || data.output || "Unknown error";
            output.className = "output-area error";
            status.textContent = "Error";
            status.className = "status fail";
        }
    } catch (err) {
        output.textContent = "Network error: " + err.message;
        output.className = "output-area error";
        status.textContent = "Failed";
        status.className = "status fail";
    }

    runBtn.disabled = false;
}

async function saveSnippet() {
    const code = editor.value;
    if (!code.trim()) {
        alert("Nothing to save");
        return;
    }
    const title = prompt("Snippet title:", "My WanX Code");
    if (title === null) return;

    try {
        const res = await fetch("/api/snippets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, code })
        });
        const data = await res.json();
        if (data.id) {
            alert("Saved successfully!");
            loadSnippets();
        } else {
            alert(data.error || "Failed to save");
        }
    } catch (e) {
        alert("Error saving: " + e.message);
    }
}

async function loadSnippets() {
    try {
        const res = await fetch("/api/snippets");
        const list = await res.json();
        if (!list.length) {
            snippetList.innerHTML = "<em>No saved snippets yet</em>";
            return;
        }
        snippetList.innerHTML = list.map(s => `
            <div style="margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
                <span style="cursor:pointer; color:var(--accent);" onclick="loadSnippet(\( {s.id})"> \){s.title}</span>
                <button onclick="deleteSnippet(${s.id})" style="background:none;border:none;color:#ff6b6b;cursor:pointer;font-size:0.8rem;">✕</button>
            </div>
        `).join("");
    } catch (e) {
        snippetList.innerHTML = "Could not load snippets";
    }
}

async function loadSnippet(id) {
    try {
        const res = await fetch(`/api/snippets/${id}`);
        const data = await res.json();
        if (data.code) {
            editor.value = data.code;
            output.textContent = `Loaded: ${data.title}`;
            output.className = "output-area";
            status.textContent = "Ready";
            status.className = "status";
        }
    } catch (e) {
        alert("Failed to load snippet");
    }
}

async function deleteSnippet(id) {
    if (!confirm("Delete this snippet?")) return;
    await fetch(`/api/snippets/${id}`, { method: "DELETE" });
    loadSnippets();
}

// Make functions available to onclick
window.loadSnippet = loadSnippet;
window.deleteSnippet = deleteSnippet;

runBtn.addEventListener("click", runCode);
clearBtn.addEventListener("click", () => {
    editor.value = "";
    output.textContent = "Editor cleared.";
    output.className = "output-area";
    status.textContent = "Ready";
    status.className = "status";
});
saveBtn.addEventListener("click", saveSnippet);

editor.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        runCode();
    }
});

loadExamples();
loadSnippets();