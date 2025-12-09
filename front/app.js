// ==========================================
// CONFIGURATION
// ==========================================
const API_BASE_URL = "http://127.0.0.1:8000";

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

/**
 * Generic API request function
 * @param {string} method - HTTP method (GET, POST, etc.)
 * @param {string} path - API endpoint path
 * @param {object|null} body - Request body (for POST/PUT)
 * @returns {Promise<any>} - API response
 */
async function apiRequest(method, path, body = null) {
  const opts = {
    method: method.toUpperCase(),
    headers: { "Content-Type": "application/json" }
  };

  if (body !== null && body !== undefined) {
    opts.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(API_BASE_URL + path, opts);
    const text = await res.text();

    let json;
    try {
      json = JSON.parse(text);
    } catch {
      json = text;
    }

    if (!res.ok) {
      const msg = (json && json.detail) ? json.detail : (typeof json === "string" ? json : res.statusText);
      throw new Error(msg);
    }

    return json;
  } catch (error) {
    throw error;
  }
}

/**
 * POST request helper
 */
function apiPost(path, body) {
  return apiRequest("POST", path, body);
}

/**
 * GET request helper
 */
function apiGet(path) {
  return apiRequest("GET", path);
}

/**
 * Display status message
 * @param {HTMLElement} element - Status message element
 * @param {string} message - Message text
 * @param {string} type - Message type (success, error, info, loading)
 */
function showStatus(element, message, type = "info") {
  element.textContent = message;
  element.className = `status-message show ${type}`;
}

/**
 * Hide status message
 */
function hideStatus(element) {
  element.className = "status-message";
}

/**
 * Get value from object with fallback keys
 */
function getValue(obj, key1, key2) {
  return obj[key1] ?? obj[key2] ?? "";
}

// ==========================================
// NAVIGATION
// ==========================================
const pages = {
  import: document.getElementById("page-import"),
  search: document.getElementById("page-search"),
  stats: document.getElementById("page-stats"),
  visu: document.getElementById("page-visu")
};

function showPage(name) {
  // Hide all pages
  for (const key in pages) {
    pages[key].classList.toggle("active", key === name);
  }

  // Update nav buttons
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-page") === name);
  });
}

// Attach navigation event listeners
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const page = btn.getAttribute("data-page");
    showPage(page);
  });
});

// ==========================================
// PAGE IMPORT
// ==========================================
const importStatusEl = document.getElementById("import-status");
const importTableBody = document.querySelector("#import-table tbody");
const fileUpload = document.getElementById("file-upload");
const selectedFilename = document.getElementById("selected-filename");

// File upload handler
if (fileUpload) {
  fileUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    selectedFilename.textContent = `Fichier sélectionné : ${file.name}`;
    selectedFilename.classList.add("show");

    showStatus(importStatusEl, `Upload de ${file.name}...`, "loading");

    try {
      // Note: This sends the file name to the backend endpoint
      // You may need to adjust this depending on your backend implementation
      const body = await apiPost("/task1/load/" + encodeURIComponent(file.name), {});
      showStatus(importStatusEl, `✓ Succès : ${body.inserted} documents insérés`, "success");

      // Refresh data preview
      if (importTableBody) {
        await searchAllProteinsInto(importTableBody);
      }
    } catch (e) {
      showStatus(importStatusEl, `✗ Erreur : ${e.message}`, "error");
    }
  });
}

// Load default file
document.getElementById("btn-load-default").addEventListener("click", async () => {
  showStatus(importStatusEl, "Chargement du fichier par défaut...", "loading");
  try {
    const body = await apiPost("/task1/load", {});
    showStatus(importStatusEl, `✓ Succès : ${body.inserted} documents insérés dans MongoDB.`, "success");
  } catch (e) {
    showStatus(importStatusEl, `✗ Erreur : ${e.message}`, "error");
  }
});

// Load named file - Enter key support
document.getElementById("input-filename").addEventListener("keydown", e => {
  if (e.key === "Enter") {
    e.preventDefault();
    document.getElementById("btn-load-named").click();
  }
});

// Load named file
document.getElementById("btn-load-named").addEventListener("click", async () => {
  const filename = document.getElementById("input-filename").value.trim();
  if (!filename) {
    showStatus(importStatusEl, "⚠ Veuillez saisir un nom de fichier (ex: data_sample.tsv)", "error");
    return;
  }

  showStatus(importStatusEl, `Chargement de ${filename}...`, "loading");
  try {
    const body = await apiPost("/task1/load/" + encodeURIComponent(filename), {});
    showStatus(importStatusEl, `✓ Succès : ${body.inserted} documents insérés depuis ${body.file}`, "success");
  } catch (e) {
    showStatus(importStatusEl, `✗ Erreur : ${e.message}`, "error");
  }
});

// Preview data
const btnPreviewData = document.getElementById("btn-preview-data");
if (btnPreviewData) {
  btnPreviewData.addEventListener("click", async () => {
    showStatus(importStatusEl, "Chargement de la prévisualisation...", "loading");
    try {
      await searchAllProteinsInto(importTableBody);
      showStatus(importStatusEl, "✓ Données chargées avec succès", "success");
    } catch (e) {
      showStatus(importStatusEl, `✗ Erreur : ${e.message}`, "error");
    }
  });
}

/**
 * Search all proteins and display in table
 */
async function searchAllProteinsInto(tbody) {
  tbody.innerHTML = "<tr><td colspan='7' class='text-center'>Chargement...</td></tr>";

  try {
    const list = await apiPost("/proteins/search", {
      entry: "",
      protein_name: "",
      entry_name: "",
      organism: "",
      sequence: "",
      ec_number: "",
      interpro: ""
    });

    tbody.innerHTML = "";

    if (!Array.isArray(list) || !list.length) {
      tbody.innerHTML = "<tr><td colspan='7' class='text-center'><em>Aucune donnée trouvée. Veuillez d'abord importer des données.</em></td></tr>";
      return;
    }

    list.forEach(p => {
      const tr = document.createElement("tr");
      const cells = [
        getValue(p, "Entry", "entry"),
        getValue(p, "Protein names", "protein_name"),
        getValue(p, "Entry name", "entry_name") || getValue(p, "Entry Name", "entry_name"),
        getValue(p, "Organism", "organism"),
        getValue(p, "Sequence", "sequence"),
        getValue(p, "EC number", "ec_number"),
        getValue(p, "InterPro", "interpro")
      ];

      cells.forEach(txt => {
        const td = document.createElement("td");
        td.textContent = txt || "-";
        tr.appendChild(td);
      });

      tbody.appendChild(tr);
    });
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center">Erreur lors du chargement : ${e.message}</td></tr>`;
    throw e;
  }
}

// ==========================================
// PAGE SEARCH / INFORMATIONS
// ==========================================
const searchForm = document.getElementById("search-form");
const searchStatus = document.getElementById("search-status");
const resultsBody = document.querySelector("#results-table tbody");
const searchResultsCard = document.getElementById("search-results-card");

// Search form submission
searchForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(searchForm);
  const payload = {};

  for (const [k, v] of formData.entries()) {
    const value = v.trim();
    if (value !== "") {
      payload[k] = value;
    }
  }

  if (Object.keys(payload).length === 0) {
    showStatus(searchStatus, "⚠ Veuillez remplir au moins un champ de recherche.", "error");
    searchResultsCard.style.display = "none";
    return;
  }

  showStatus(searchStatus, "Recherche en cours...", "loading");
  resultsBody.innerHTML = "<tr><td colspan='7' class='text-center'>Chargement...</td></tr>";
  searchResultsCard.style.display = "block";

  try {
    const list = await apiPost("/proteins/search", payload);

    resultsBody.innerHTML = "";

    if (!list.length) {
      showStatus(searchStatus, "ℹ Aucun résultat trouvé pour ces critères.", "info");
      resultsBody.innerHTML = "<tr><td colspan='7' class='text-center'><em>Aucun résultat</em></td></tr>";
      return;
    }

    showStatus(searchStatus, `✓ ${list.length} résultat(s) trouvé(s).`, "success");

    list.forEach(p => {
      const tr = document.createElement("tr");
      const cells = [
        getValue(p, "Entry", "entry"),
        getValue(p, "Protein names", "protein_name"),
        getValue(p, "Entry name", "entry_name") || getValue(p, "Entry Name", "entry_name"),
        getValue(p, "Organism", "organism"),
        getValue(p, "Sequence", "sequence"),
        getValue(p, "EC number", "ec_number"),
        getValue(p, "InterPro", "interpro")
      ];

      cells.forEach(txt => {
        const td = document.createElement("td");
        td.textContent = txt || "-";
        tr.appendChild(td);
      });

      resultsBody.appendChild(tr);
    });
  } catch (e) {
    showStatus(searchStatus, `✗ Erreur : ${e.message}`, "error");
    resultsBody.innerHTML = `<tr><td colspan="7" class="text-center">Erreur : ${e.message}</td></tr>`;
  }
});

// Reset search form
document.getElementById("btn-reset-search").addEventListener("click", () => {
  searchForm.reset();
  hideStatus(searchStatus);
  resultsBody.innerHTML = "";
  searchResultsCard.style.display = "none";
});

// ==========================================
// PAGE STATISTICS
// ==========================================
const statsStatus = document.getElementById("stats-status");

// Refresh statistics
document.getElementById("btn-refresh-stats").addEventListener("click", async () => {
  showStatus(statsStatus, "Chargement des statistiques...", "loading");

  // Reset all stat values
  document.getElementById("stat-total").textContent = "-";
  document.getElementById("stat-with-domain").textContent = "-";
  document.getElementById("stat-without-domain").textContent = "-";
  document.getElementById("stat-with-fct").textContent = "-";
  document.getElementById("stat-without-fct").textContent = "-";

  try {
    const stats = await apiGet("/stats");

    document.getElementById("stat-total").textContent = stats.totalProt.toLocaleString();
    document.getElementById("stat-with-domain").textContent = stats.protWithDomain.toLocaleString();
    document.getElementById("stat-without-domain").textContent = stats.protWithoutDomain.toLocaleString();
    document.getElementById("stat-with-fct").textContent = stats.protWithFct.toLocaleString();
    document.getElementById("stat-without-fct").textContent = stats.protWithoutFct.toLocaleString();

    showStatus(statsStatus, "✓ Statistiques mises à jour avec succès.", "success");
  } catch (e) {
    showStatus(statsStatus, `✗ Erreur : ${e.message}. Vérifiez que l'endpoint GET /stats existe dans le backend.`, "error");
  }
});

// ==========================================
// PAGE VISUALIZATION
// ==========================================
const visuForm = document.getElementById("visu-form");
const visuStatus = document.getElementById("visu-status");
const visuCenter = document.getElementById("visu-center");
const visuSummary = document.getElementById("visu-summary");
const visuNeighbors = document.getElementById("visu-neighbors");
const visuResults = document.getElementById("visu-results");

// Variable globale pour le graphe 3D
let graph3D = null;

// Ego graph form submission
visuForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const entry = document.getElementById("visu-entry").value.trim();
  const thrStr = document.getElementById("visu-threshold").value.trim();

  if (!entry) {
    showStatus(visuStatus, "⚠ Veuillez saisir un Entry.", "error");
    return;
  }

  const threshold = parseFloat(thrStr || "0");
  if (Number.isNaN(threshold) || threshold < 0 || threshold > 1) {
    showStatus(visuStatus, "⚠ Le seuil Jaccard doit être un nombre entre 0 et 1.", "error");
    return;
  }

  showStatus(visuStatus, "Chargement du graphe...", "loading");
  visuCenter.textContent = "";
  visuSummary.textContent = "";
  visuNeighbors.innerHTML = "";
  visuResults.style.display = "none";

  try {
    const body = await apiPost("/task2/ego_graph", {
      entry: entry,
      jaccard_threshold: threshold
    });

    hideStatus(visuStatus);
    visuResults.style.display = "block";

    const center = body.center || {};
    const neighbors = body.neighbors || [];
    const summary = body.summary || {};

    const centerEntry = center.entry || center.Entry || entry;
    const centerName = center.name || center["Protein names"] || "N/A";
    const centerOrg = center.organism || center["Organism"] || "N/A";

    visuCenter.innerHTML = `
      <p><strong>Entry :</strong> ${centerEntry}</p>
      <p><strong>Nom :</strong> ${centerName}</p>
      <p><strong>Organisme :</strong> ${centerOrg}</p>
    `;

    const numNeighbors = summary.num_neighbors ?? neighbors.length;
    visuSummary.innerHTML = `
      ℹ️ Cette protéine possède <strong>${numNeighbors}</strong> voisin(s) avec un seuil Jaccard ≥ ${threshold}
    `;

    if (!neighbors.length) {
      visuNeighbors.innerHTML = "<li>Aucun voisin trouvé pour ce seuil.</li>";
      // Clear 3D graph
      if (graph3D) {
        const graphContainer = document.getElementById("3d-graph");
        graphContainer.innerHTML = "";
        graph3D = null;
      }
      return;
    }

    // Display neighbors list
    neighbors.forEach(n => {
      const li = document.createElement("li");
      const e = n.entry || n.Entry || "?";
      const name = n.name || n["Protein names"] || "N/A";
      const org = n.organism || n["Organism"] || "N/A";
      const weight = n.weight != null ? n.weight.toFixed(3) : "N/A";

      li.innerHTML = `
        <strong>${e}</strong> - ${name}<br>
        <small>Organisme: ${org} | Jaccard: ${weight}</small>
      `;

      visuNeighbors.appendChild(li);
    });

    // Create 3D graph data
    const graphData = {
      nodes: [],
      links: []
    };

    // Add center node (red, large)
    graphData.nodes.push({
      id: centerEntry,
      name: centerName,
      val: 10,
      color: '#ff0000'
    });

    // Add neighbor nodes (blue, medium)
    neighbors.forEach(n => {
      const neighborEntry = n.entry || n.Entry || "?";
      const neighborName = n.name || n["Protein names"] || "N/A";
      const weight = n.weight || 0;

      graphData.nodes.push({
        id: neighborEntry,
        name: neighborName,
        val: 5,
        color: '#0000ff'
      });

      // Add link from center to neighbor
      graphData.links.push({
        source: centerEntry,
        target: neighborEntry,
        color: '#ff0000',
        value: weight
      });
    });

    // Create or update 3D graph
    const graphContainer = document.getElementById("3d-graph");

    // Clear existing graph
    graphContainer.innerHTML = "";

    // Check if ForceGraph3D is available
    if (typeof ForceGraph3D !== 'undefined') {
      graph3D = ForceGraph3D()(graphContainer)
        .graphData(graphData)
        .nodeLabel(node => `${node.id} - ${node.name}`)
        .nodeColor(node => node.color)
        .nodeVal(node => node.val)
        .linkColor(link => link.color)
        .linkWidth(2)
        .backgroundColor('#000000')
        .width(graphContainer.clientWidth || 1200)
        .height(500);
    } else {
      // Fallback if library not loaded
      graphContainer.innerHTML = `
        <div style="color: white; padding: 2rem; text-align: center;">
          <p>Visualisation 3D non disponible</p>
          <p>La bibliothèque ForceGraph3D n'a pas pu être chargée.</p>
        </div>
      `;
    }

  } catch (e) {
    showStatus(visuStatus, `✗ Erreur : ${e.message}`, "error");
    visuResults.style.display = "none";
  }
});

// ==========================================
// INITIALIZATION
// ==========================================
console.log("NoSQL Proteins Explorer initialized");
console.log("API Base URL:", API_BASE_URL);
console.log("Ready to use!");
