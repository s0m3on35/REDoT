// REDoT Web Console - main.js
// Handles dynamic UI, module execution, and WebSocket streaming

const API_BASE = "/api";
const terminal = document.getElementById("termBox");
let socket = null;
let execId = null;

// Initialize system
window.onload = () => {
  fetchModules();
  document.getElementById("runBtn").addEventListener("click", runSelectedModule);
  document.getElementById("clearBtn").addEventListener("click", () => { terminal.textContent = ""; });
  document.getElementById("refreshMods").addEventListener("click", fetchModules);
  document.getElementById("moduleSelect").addEventListener("change", updateFormInputs);
};

// Fetch available modules
function fetchModules() {
  fetch(`${API_BASE}/modules`)
    .then(res => res.json())
    .then(data => {
      const select = document.getElementById("moduleSelect");
      select.innerHTML = "";
      data.forEach(mod => {
        const option = document.createElement("option");
        option.value = mod.path;
        option.textContent = mod.name;
        option.dataset.inputs = JSON.stringify(mod.inputs || []);
        select.appendChild(option);
      });
      updateFormInputs(); // Trigger initial input generation
    })
    .catch(err => {
      terminal.textContent = `Error loading modules: ${err}`;
    });
}

// Generate inputs for selected module
function updateFormInputs() {
  const select = document.getElementById("moduleSelect");
  const selected = select.options[select.selectedIndex];
  const inputs = JSON.parse(selected.dataset.inputs || "[]");

  const form = document.getElementById("paramForm");
  form.innerHTML = "";

  inputs.forEach(input => {
    const row = document.createElement("div");
    row.className = "row";

    const label = document.createElement("label");
    label.textContent = `--${input.name}`;

    const field = document.createElement("input");
    field.type = input.type === "number" ? "number" : "text";
    field.name = input.name;
    field.placeholder = input.description || "";

    row.appendChild(label);
    row.appendChild(field);
    form.appendChild(row);
  });
}

// Run selected module
function runSelectedModule() {
  const select = document.getElementById("moduleSelect");
  const path = select.value;

  const formData = new FormData(document.getElementById("paramForm"));
  const inputs = {};
  formData.forEach((value, key) => {
    inputs[key] = value;
  });

  fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, inputs })
  })
  .then(res => res.json())
  .then(data => {
    execId = data.exec_id;
    terminal.textContent = "";
    openSocketStream(execId);
  })
  .catch(err => {
    terminal.textContent = `Error running module: ${err}`;
  });
}

// WebSocket stream output from backend
function openSocketStream(execId) {
  if (socket) socket.close();

  socket = new WebSocket(`ws://${window.location.hostname}:8765/ws/${execId}`);

  socket.onopen = () => {
    console.log(`WebSocket connected to exec_id: ${execId}`);
  };

  socket.onmessage = (event) => {
    terminal.textContent += event.data;
    terminal.scrollTop = terminal.scrollHeight;
  };

  socket.onerror = (err) => {
    terminal.textContent += `\n[!] WebSocket error: ${err.message}`;
  };

  socket.onclose = () => {
    console.log(`WebSocket closed for exec_id: ${execId}`);
  };
}
