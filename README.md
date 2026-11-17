# Tennis Trip

Who to contact and what to send for the Philippines and Japan trip, plus the flight and tournament plan. Static site and installable PWA.

- `src/curated.json`: hand-checked contacts, drafts and the plan.
- `src/import_outreach.py`: adds the newest contacts and drafts from `../philippines-outreach-2026-11-17.md` and `../japan-outreach-2026-11-17.md` and writes `src/data.json`, the only data the page renders.
- `src/build.py`: inlines `data.json` into `public/index.html`, writes the manifest, icons and a versioned service worker.

Rebuild and deploy:

    python3 src/import_outreach.py && python3 src/build.py
    vercel --prod --yes --scope jerryshi042003s-projects

Images in `public/img` are Instagram profile pictures saved locally from each public profile (Nov 17, 2026); a contact without a saved picture shows its city instead.

Privacy: the page is public. No private phone numbers, personal emails or home addresses. Hosts appear by first name only.
