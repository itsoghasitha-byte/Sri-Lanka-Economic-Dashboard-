(() => {
  const byId = id => document.getElementById(id);
  const input = byId("api-base-url");
  const status = byId("api-connection-status");
  const results = byId("api-results");
  const search = byId("api-search");
  const queryForm = byId("api-search-form");
  const researchForm = byId("ai-research-form");
  const researchOutput = byId("ai-research-output");
  const savedKey = "lankaIntelPublicApiBase";
  const cleanBase = value => value.trim().replace(/\\/+$/, "");
  const baseUrl = () => cleanBase(input.value);
  const setStatus = (message, good = false) => {
    status.textContent = message;
    status.dataset.state = good ? "online" : "offline";
  };
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const fetchJson = async (path, options = {}) => {
    const base = baseUrl();
    if (!base) throw new Error("Enter your deployed API URL first.");
    const response = await fetch(base + path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.detail || ("API returned HTTP " + response.status));
    return body;
  };
  async function connect() {
    const base = baseUrl();
    if (!/^https?:\\/\\//i.test(base)) {
      setStatus("Enter a valid http(s) API URL.");
      return;
    }
    localStorage.setItem(savedKey, base);
    setStatus("Connecting…");
    try {
      const health = await fetchJson("/health");
      setStatus("Connected · " + health.database + " · " + health.indicator_rows + " records", true);
      await loadIndicators();
    } catch (error) {
      setStatus(error.message + " Check deployment and CORS settings.");
      results.replaceChildren(make("p", "No live results yet. The API must be deployed and allow this website's origin."));
    }
  }
  async function loadIndicators() {
    const term = search.value.trim();
    const data = await fetchJson("/api/indicators?q=" + encodeURIComponent(term));
    results.replaceChildren();
    if (!data.data.length) {
      results.append(make("p", "No matching indicators found."));
      return;
    }
    const table = make("table", undefined, "live-data-table");
    const thead = make("thead");
    const tr = make("tr");
    ["Period", "Indicator", "Value", "Source"].forEach(label => tr.append(make("th", label)));
    thead.append(tr);
    const tbody = make("tbody");
    data.data.forEach(item => {
      const row = make("tr");
      row.append(make("td", String(item.period)));
      row.append(make("td", String(item.indicator)));
      row.append(make("td", Number(item.value).toLocaleString(undefined, { maximumFractionDigits: 2 }) + " " + item.unit));
      const sourceCell = make("td");
      const link = make("a", String(item.source));
      if (/^https?:\\/\\//i.test(item.source_url || "")) {
        link.href = item.source_url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      }
      sourceCell.append(link);
      row.append(sourceCell);
      tbody.append(row);
    });
    table.append(thead, tbody);
    results.append(table);
  }
  byId("api-connect-button").addEventListener("click", connect);
  queryForm.addEventListener("submit", async event => {
    event.preventDefault();
    try { await loadIndicators(); }
    catch (error) { setStatus(error.message); }
  });
  researchForm.addEventListener("submit", async event => {
    event.preventDefault();
    const question = byId("ai-research-question").value.trim();
    if (question.length < 5) return;
    const button = byId("ai-research-button");
    button.disabled = true;
    researchOutput.textContent = "Researching current sources…";
    try {
      const data = await fetchJson("/api/research/ask", { method: "POST", body: JSON.stringify({ question }) });
      researchOutput.textContent = data.answer;
    } catch (error) {
      researchOutput.textContent = error.message + " AI requires OPENAI_API_KEY on the API host; the key is never entered in this browser.";
    } finally {
      button.disabled = false;
    }
  });
  const existing = localStorage.getItem(savedKey);
  if (existing) input.value = existing;
  if (existing) connect();
  else setStatus("API not connected · deploy the backend to enable live queries");
})();