// REDoT Operator Console - Enhanced Version
const API = "/api";
const terminal = document.getElementById("terminalOutput");
const moduleSelect = document.getElementById("moduleSelect");
const paramForm = document.getElementById("inputs");
const agentSelect = document.getElementById("agentSelect");
const historyPanel = document.getElementById("historyLog");

let currentExecId = null;
let pollingInterval = null;

window.onload = () => {
  loadModules();
  document.getElementById("runBtn").addEventListener("click", runModule);
  document.getElementById("clearBtn").addEventListener("click", () => terminal.textContent = "");
  document.getElementById("downloadBtn").addEventListener("click", downloadLog);
  moduleSelect.addEventListener("change", buildFormInputs);
};

// Load modules with categories
async function loadModules() {
  const res = await fetch(`${API}/modules`);
  const modules = await res.json();

  moduleSelect.innerHTML = "";
  const categories = {};

  modules.forEach(mod => {
    const category = mod.category || "uncategorized";
    if (!categories[category]) {
      const optgroup = document.createElement("optgroup");
      optgroup.label = category;
      categories[category] = optgroup;
    }

    const opt = document.createElement("option");
    opt.value = mod.path;
    opt.textContent = mod.name;
    opt.dataset.inputs = JSON.stringify(mod.inputs || []);
    opt.dataset.output = mod.output || "";
    categories[category].appendChild(opt);
  });

  Object.values(categories).forEach(group => moduleSelect.appendChild(group));
  buildFormInputs();
}

// Generate form inputs with support for text, number, dropdown, checkbox
function buildFormInputs() {
  const selected = moduleSelect.options[moduleSelect.selectedIndex];
  const inputs = JSON.parse(selected.dataset.inputs || "[]");
  paramForm.innerHTML = "";

  inputs.forEach(input => {
    const label = document.createElement("label");
    label.className = "param-label";
    label.textContent = `--${input.name}`;

    let field;
    switch (input.ui_type) {
      case "select":
        field = document.createElement("select");
        field.name = input.name;
        input.options.forEach(opt => {
          const option = document.createElement("option");
          option.value = opt;
          option.textContent = opt;
          field.appendChild(option);
        });
        break;
      case "checkbox":
        field = document.createElement("input");
        field.type = "checkbox";
        field.name = input.name;
        break;
      default:
        field = document.createElement("input");
        field.type = input.type === "number" ? "number" : "text";
        field.name = input.name;
        field.placeholder = input.description || "";
    }

    paramForm.appendChild(label);
    paramForm.appendChild(field);
  });
}

// Run module with chaining output injection
async function runModule() {
  const selected = moduleSelect.options[moduleSelect.selectedIndex];
  const path = selected.value;

  const inputs = {};
  const fields = paramForm.querySelectorAll("input, select");
  fields.forEach(input => {
    if (input.type === "checkbox") {
      inputs[input.name] = input.checked;
    } else if (input.value.trim() !== "") {
      inputs[input.name] = input.value;
    }
  });

  const res = await fetch(`${API}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, inputs })
  });

  const data = await res.json();
  currentExecId = data.exec_id;
  terminal.textContent = "";
  appendToHistory(selected.textContent, inputs);

  startPollingOutput(currentExecId, selected.dataset.output);
}

// Poll output and auto-chain to next if applicable
function startPollingOutput(execId, expectedOutput) {
  clearInterval(pollingInterval);

  pollingInterval = setInterval(async () => {
    try {
      const res = await fetch(`${API}/output/${execId}`);
      const data = await res.json();

      if (data.log) {
        terminal.textContent = data.log;
        terminal.scrollTop = terminal.scrollHeight;
      }

      if (data.log && (data.log.includes("return code") || data.log.includes("completed") || data.log.includes("exited"))) {
        clearInterval(pollingInterval);
        tryChaining(expectedOutput, data.log);
      }
    } catch (err) {
      clearInterval(pollingInterval);
      terminal.textContent += "\n[!] Output polling failed.";
    }
  }, 2000);
}

// Attempt to chain to next module if chaining tag detected
function tryChaining(expectedKey, log) {
  if (!expectedKey) return;
  const match = log.match(new RegExp(`${expectedKey}: (.+)`));
  if (match && match[1]) {
    const value = match[1].trim();
    const nextField = paramForm.querySelector(`[name="${expectedKey}"]`);
    if (nextField && nextField.tagName === "INPUT") {
      nextField.value = value;
    }
    terminal.textContent += `\n[>] Auto-filled ${expectedKey} from previous output.`;
  }
}

// Add to command history
function appendToHistory(name, inputs) {
  const entry = document.createElement("div");
  entry.className = "history-entry";

  const meta = document.createElement("div");
  meta.className = "history-meta";
  meta.innerHTML = `<span class="command-name">${name}</span><br/><span class="command-target">${Object.values(inputs).join(" ")}</span>`;

  const time = document.createElement("div");
  time.className = "history-time";
  time.textContent = new Date().toLocaleTimeString();

  entry.appendChild(meta);
  entry.appendChild(time);
  historyPanel.prepend(entry);
}

// Download output as TXT
function downloadLog() {
  const blob = new Blob([terminal.textContent], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "redot_log.txt";
  a.click();
  URL.revokeObjectURL(url);
}
