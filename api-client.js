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
  const cleanBase = value => value.trim().replace(/\/+$/, "");
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
    if (!/^https?:\/\//i.test(base)) {
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
      if (/^https?:\/\//i.test(item.source_url || "")) {
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

  // Wiki-style knowledge base: AI creates refreshed, source-linked, versioned topic pages.
  const wikiSection = document.createElement("section");
  wikiSection.id = "knowledge-wiki";
  wikiSection.className = "section-shell wiki-section";
  wikiSection.innerHTML = [
    '<div class="section-heading"><div><div class="eyebrow">03 / LIVING KNOWLEDGE BASE</div><h2>Research that <span class="muted-holo">keeps evolving.</span></h2></div><p>Ask AI to research a topic using current web sources. Each refresh creates a saved revision with source links.</p></div>',
    '<div class="api-console wiki-console"><div class="api-console-head"><span class="status-dot"></span><span>AI KNOWLEDGE EDITOR</span><span>VERSIONED · SOURCE-LINKED</span></div>',
    '<form id="wiki-update-form" class="wiki-update-form"><label for="wiki-topic">Topic to create or refresh</label><input id="wiki-topic" maxlength="180" minlength="3" required placeholder="e.g. Sri Lanka inflation, tourism, public debt"><label for="wiki-focus">What should be updated?</label><input id="wiki-focus" maxlength="400" placeholder="Latest official figures, context, trends and risks"><button id="wiki-update-button" class="button button-primary" type="submit">Research &amp; update page ↗</button></form>',
    '<p class="api-help">AI-written content is a draft, not an official publication. Verify important claims against primary sources. Refreshing uses the server configured AI provider.</p>',
    '<div class="wiki-search-row"><label for="wiki-search">Search saved pages</label><div><input id="wiki-search" type="search" placeholder="Search topics in the knowledge base"><button id="wiki-search-button" class="button button-quiet" type="button">Search</button></div></div>',
    '<div id="wiki-page-list" class="wiki-page-list" aria-live="polite"><p>Connect the API above to browse saved knowledge pages.</p></div><article id="wiki-page-view" class="wiki-page-view" aria-live="polite"><p>Select a saved page or research a new topic.</p></article></div>'
  ].join("");
  const sourcesSection = byId("sources");
  if (sourcesSection) sourcesSection.parentNode.insertBefore(wikiSection, sourcesSection);
  const wikiList = byId("wiki-page-list");
  const wikiView = byId("wiki-page-view");
  const safeText = value => String(value == null ? "" : value);
  function renderWikiPage(page) {
    wikiView.replaceChildren();
    wikiView.append(make("div", "REVISION " + page.revision + " · UPDATED " + safeText(page.updated_at || "just now"), "wiki-meta"));
    wikiView.append(make("h3", page.title, "wiki-page-title"));
    wikiView.append(make("pre", page.content, "wiki-page-content"));
    if (page.sources && page.sources.length) {
      wikiView.append(make("h4", "Source links", "wiki-sources-title"));
      const list = make("ul", undefined, "wiki-sources");
      page.sources.forEach(url => {
        if (!/^https?:\/\//i.test(url)) return;
        const li = make("li");
        const link = make("a", url);
        link.href = url; link.target = "_blank"; link.rel = "noopener noreferrer";
        li.append(link); list.append(li);
      });
      wikiView.append(list);
    }
    if (page.history && page.history.length > 1) {
      wikiView.append(make("h4", "Recent revision history", "wiki-sources-title"));
      const history = make("ol", undefined, "wiki-history");
      page.history.forEach(item => history.append(make("li", safeText(item.created_at) + " — " + safeText(item.title))));
      wikiView.append(history);
    }
  }
  async function loadWikiPages() {
    try {
      const data = await fetchJson("/api/knowledge/pages?q=" + encodeURIComponent(byId("wiki-search").value.trim()));
      wikiList.replaceChildren();
      if (!data.data.length) { wikiList.append(make("p", "No saved pages yet. Research a topic above to create one.")); return; }
      data.data.forEach(page => {
        const button = make("button", undefined, "wiki-page-card");
        button.type = "button";
        button.append(make("strong", page.title));
        button.append(make("span", "Revision " + page.revision + " · " + safeText(page.updated_at)));
        button.append(make("p", page.excerpt));
        button.addEventListener("click", async () => {
          try { renderWikiPage(await fetchJson("/api/knowledge/pages/" + encodeURIComponent(page.slug))); }
          catch (error) { wikiView.replaceChildren(make("p", error.message)); }
        });
        wikiList.append(button);
      });
    } catch (error) {
      wikiList.replaceChildren(make("p", error.message + " Connect the API and configure its server-side AI key."));
    }
  }
  byId("wiki-search-button").addEventListener("click", loadWikiPages);
  byId("wiki-search").addEventListener("keydown", event => {
    if (event.key === "Enter") { event.preventDefault(); loadWikiPages(); }
  });
  byId("wiki-update-form").addEventListener("submit", async event => {
    event.preventDefault();
    const button = byId("wiki-update-button");
    const topic = byId("wiki-topic").value.trim();
    button.disabled = true;
    button.textContent = "Researching current sources…";
    wikiView.replaceChildren(make("p", "Checking current web sources and saving a new page revision…"));
    try {
      const page = await fetchJson("/api/knowledge/update", {
        method: "POST",
        body: JSON.stringify({ topic, focus: byId("wiki-focus").value.trim() || "latest official facts, context, trends and risks" })
      });
      renderWikiPage(page);
      await loadWikiPages();
    } catch (error) {
      wikiView.replaceChildren(make("p", error.message + " AI updates require OPENAI_API_KEY on the API server."));
    } finally {
      button.disabled = false;
      button.textContent = "Research & update page ↗";
    }
  });

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