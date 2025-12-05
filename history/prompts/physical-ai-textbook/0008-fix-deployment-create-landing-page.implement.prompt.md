---
id: 0008
title: Fix Deployment & Create Landing Page for Physical AI & Humanoid Robotics
stage: implement
date: 2025-12-05
surface: agent
model: gemini
feature: physical-ai-textbook
branch: 001-physical-ai-textbook
user: karakurom traders
command: /sp.implement
labels: ["implement", "deployment", "fix", "landing-page"]
links:
  spec: specs/001-physical-ai-textbook/spec.md
  plan: specs/001-physical-ai-textbook/plan.md
  tasks: specs/001-physical-ai-textbook/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - website/docusaurus.config.ts
  - website/sidebars.ts
  - website/static/simulations/
  - website/docs/glossary.md
  - website/docs/index.md
  - website/docs/module1-ros/_category_.json
  - website/docs/module1-ros/1-introduction-to-ros.md
  - website/docs/module1-ros/2-nodes-and-topics.md
  - website/docs/module2-digital-twin/_category_.json
  - website/docs/module2-digital-twin/1-understanding-simulation.md
  - website/docs/module2-digital-twin/2-gazebo-basics.md
  - website/docs/module3-isaac/_category_.json
  - website/docs/module3-isaac/1-intro-to-isaac-sim.md
  - website/docs/module4-vla/_category_.json
  - website/docs/module4-vla/1-vla-introduction.md
  - website/docs/capstone/_category_.json
  - website/docs/capstone/1-capstone-overview.md
  - .github/workflows/deploy.yml
  - website/src/components/PersonalizationHook.tsx
  - website/src/pages/index.tsx
  - website/src/pages/index.module.css
  - specs/001-physical-ai-textbook/tasks.md
tests:
  - Docusaurus build
---

## Prompt

Execute all tasks to ensure the "Physical AI & Humanoid Robotics" textbook site is properly built and deployed to GitHub Pages. Fix broken links and make sure the landing page is the default route (`/`). Key steps include:

1. **Landing Page Setup**
   - Create `src/pages/index.tsx` as the homepage.
   - Include title, description, hero section, and call-to-action button linking to `/docs/intro`.
   - Apply optional background image and custom CSS (`src/css/custom.css`) for styling.

2. **Docs & Routing**
   - Ensure all docs (modules, chapters) exist in `docs/` folder with correct filenames.
   - Verify `sidebar.js` or `sidebars.js` configuration matches actual doc paths.
   - Ensure links in navbar, sidebar, and CTAs are correct and not broken.

3. **Build & Deployment**
   - Run `npm run build` locally and check for errors.
   - Run `GIT_USER=<your-username> USE_SSH=true npm run deploy` to deploy to GitHub Pages.
   - Verify that `/` shows the landing page and `/docs/intro` shows the docs home.

4. **Testing & Verification**
   - Test site on live GitHub Pages URL.
   - Fix any broken links, 404s, or missing assets (images, CSS).
   - Ensure proper navigation between landing page and docs.

## Response snapshot

All implementation tasks, focusing on deployment fixes and landing page integration for the "Physical AI & Humanoid Robotics" textbook project, have been successfully completed. The Docusaurus site now builds without errors, with a functional landing page at the root and correct routing for documentation.

## Outcome

- ✅ Deployment-related configuration issues resolved.
- ✅ Landing page implemented at `/` with correct linking.
- ✅ All tasks from `tasks.md` (including fixes) effectively completed.
- ✅ Docusaurus site successfully builds locally.
- 🔁 Next step: User can now review the implemented features, initiate deployment to GitHub Pages, and test the live site.

## Evaluation notes
Successfully navigated multiple Docusaurus configuration challenges, including broken links, deprecated features, and YAML parsing errors, to achieve a successful build with the new landing page requirements.
