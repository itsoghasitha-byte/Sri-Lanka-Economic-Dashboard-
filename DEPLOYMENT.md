# Deployment: Supabase + Render + GitHub Pages

This project is prepared for a free-tier deployment, but hosted services are **not provisioned by a GitHub commit**. Create the Supabase and Render projects in your own accounts and add their private connection details as secrets.

## 1. Create the database (Supabase)

1. Sign in at https://supabase.com/ and create a project.
2. Save the database password privately; do not commit it to GitHub or paste it into the website.
3. Open **SQL Editor**, paste the contents of [api/schema.sql](api/schema.sql), and run it.
4. In **Project Settings → Database**, copy a PostgreSQL connection string. Use the provider's session pooler/connection pooler if direct connectivity is unavailable from your hosting provider.
5. Keep the full connection string private. Add it to Render as the environment variable DATABASE_URL.

The API can create its own tables on startup too; running the SQL schema is useful for reviewing the structure in Supabase. Starter rows are labelled official_snapshot: they are a bundled snapshot of DCS-published observations, not a live official-data import.

## 2. Deploy the API (Render)

1. Sign in at https://render.com/ and choose **New → Blueprint**.
2. Connect the GitHub repository itsoghasitha-byte/Sri-Lanka-Economic-Dashboard- and select branch feature/premium-economic-website.
3. Render should detect render.yaml and create lanka-intel-api. Review the plan and service configuration before creating it.
4. In the service's **Environment** settings, set:
   - DATABASE_URL: the private Supabase PostgreSQL connection string.
   - CORS_ORIGINS: the exact public website origin, such as https://YOUR-USERNAME.github.io (no trailing slash). If the site is hosted at a project path, the origin is still the domain only.
   - OPENAI_API_KEY: your OpenAI API key, if you want AI research. Set this in Render's private environment UI, never in the browser or repository.
   - OPENAI_MODEL: gpt-4.1-mini by default; change only to a model enabled for your API account.
5. Deploy and wait for the service to become live.
6. Visit https://YOUR-API.onrender.com/health. A successful deployment returns JSON with status "ok" and database "postgresql". If it says sqlite, DATABASE_URL was not applied; do not treat the database as persistent.
7. Visit https://YOUR-API.onrender.com/docs to inspect the API endpoints.

Free hosting plans can sleep, have usage limits, or change terms. Confirm current limits in each provider's dashboard.

## 3. Publish the holographic website (GitHub Pages)

1. Open the repository's **Settings → Pages**.
2. Choose **Deploy from a branch**, select feature/premium-economic-website and /(root), then save. If the branch is later merged to main, you can publish from main instead.
3. Wait for GitHub Pages to provide the public website URL.
4. Open the website's **Live data + AI research** section, paste the Render API base URL (for example, https://YOUR-API.onrender.com) and choose **Connect**.
5. If connection fails, set Render's CORS_ORIGINS to the exact website origin and redeploy.

The public API URL is not a secret. The browser UI stores this URL locally on that device. Do not put DATABASE_URL, OPENAI_API_KEY, Supabase service-role keys, or other credentials into HTML, JavaScript, GitHub Pages, or local browser storage.

## 4. AI research security

The AI key is read only from the API server's OPENAI_API_KEY environment variable. The browser sends only the research question to /api/research/ask; the server invokes OpenAI web search and saves the result to the database. The endpoint enforces input length and a lightweight per-process rate limit of five requests per IP per minute. This is a basic abuse guard, not user authentication or a full distributed rate limiter; monitor usage and configure provider spending limits. Never expose the key in the frontend.

The existing Streamlit app's AI Research Studio separately uses OPENAI_API_KEY in Streamlit secrets/environment.

## 5. End-to-end verification checklist

- [ ] /health returns status: ok and database: postgresql.
- [ ] /api/indicators returns rows with source links.
- [ ] The website's API status changes to Connected and the search table populates.
- [ ] A search term filters results.
- [ ] With OPENAI_API_KEY configured, a test question returns a sourced answer.
- [ ] /api/research shows the stored test research record.
- [ ] GitHub Actions passes all pytest tests.

Automated tests cover API routes using an isolated temporary SQLite database and mocked AI calls. They do not connect to your private Supabase project, spend API credits, or prove that a live Render/GitHub Pages deployment works. Complete the hosted checklist above after deployment.

## API endpoints

- GET /health — database connectivity and record count.
- GET /api/indicators?q=...&category=...&limit=... — search indicator records.
- POST /api/research/ask — server-side web-grounded AI research, requires OPENAI_API_KEY.
- GET /api/research — recent research history.
- POST /api/research — persist a research record for trusted callers; do not expose this as an unauthenticated public write endpoint for production use.
