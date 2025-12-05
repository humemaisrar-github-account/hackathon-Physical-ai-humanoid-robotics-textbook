# Tasks: Physical AI & Humanoid Robotics Textbook

**Input**: Design documents from `specs/001-physical-ai-textbook/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Docusaurus project initialization and basic configuration.

- [x] T001 Initialize a new Docusaurus classic project in the `website/` directory.
- [x] T002 Configure `website/docusaurus.config.ts` with project title, tagline, author, and GitHub repository information.
- [x] T003 [P] Create initial `website/static/img` and `website/static/simulations` directories.
- [x] T004 [P] Remove default Docusaurus blog and docs content from `website/blog/` and `website/docs/`.

---

## Phase 2: Landing Page Implementation

**Purpose**: Create a professional landing page at the root URL (`/`).

- [x] T005 Create `website/src/pages/index.tsx` as the landing page component.
- [x] T006 Implement the landing page with title, description, hero section, and a call-to-action button linking to `/docs/index`.
- [x] T007 [P] Apply custom styles to the landing page in `website/src/css/custom.css` (or a dedicated component CSS module).
- [x] T008 Configure `website/docusaurus.config.ts` to ensure the landing page is the default route (`/`).
- [x] T009 Remove the `routes` redirect from `website/docusaurus.config.ts` if it exists.

---

## Phase 3: Foundational (Blocking Prerequisites)

**Purpose**: Core book structure and navigation.

- [x] T010 Create the main module directories within `website/docs/`: `module1-ros`, `module2-digital-twin`, `module3-isaac`, `module4-vla`, `capstone`.
- [x] T011 Configure the sidebar in `website/sidebars.ts` and `website/docusaurus.config.ts` to reflect the module structure and order (`modulesSidebar`).
- [x] T012 Create the main `website/docs/glossary.md` file.
- [x] T013 Create `website/docs/index.md` as the main documentation entry point.
- [x] T014 Ensure `website/docs/index.md` has `slug: /index` or is correctly configured to be accessible at `/docs/`.

**Checkpoint**: Foundation ready. The Docusaurus site should build with the correct sidebar structure but empty pages.

---

## Phase 4: User Story 1 - Master ROS 2 (Priority: P1) 🎯 MVP

**Goal**: Create the content for the first module, teaching students the fundamentals of ROS 2.

**Independent Test**: A user can navigate to Module 1, read the first chapter, and run the provided "Hello World" publisher/subscriber example.

### Implementation for User Story 1

- [x] T015 [US1] Create `_category_.json` to define the label for `website/docs/module1-ros/`.
- [x] T016 [P] [US1] Create placeholder Markdown file `website/docs/module1-ros/1-introduction-to-ros.md`.
- [x] T017 [P] [US1] Create placeholder Markdown file `website/docs/module1-ros/2-nodes-and-topics.md`.
- [x] T018 [US1] Add detailed content to `website/docs/module1-ros/1-introduction-to-ros.md` following the chapter contract.
- [x] T019 [US1] Add a "Hello World" ROS 2 publisher/subscriber code example to `website/docs/module1-ros/2-nodes-and-topics.md`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 5: User Story 2 - Build a Digital Twin (Priority: P2)

**Goal**: Create the content for the second module on simulation.

**Independent Test**: A user can navigate to Module 2 and see the placeholder chapters.

### Implementation for User Story 2

- [x] T020 [US2] Create `_category_.json` to define the label for `website/docs/module2-digital-twin/`.
- [x] T021 [P] [US2] Create placeholder Markdown file `website/docs/module2-digital-twin/1-understanding-simulation.md`.
- [x] T022 [P] [US2] Create placeholder Markdown file `website/docs/module2-digital-twin/2-gazebo-basics.md`.

---

## Phase 6: User Story 3 - Integrate an AI Brain (Priority: P3)

**Goal**: Create the content for the third module on NVIDIA Isaac.

**Independent Test**: A user can navigate to Module 3 and see the placeholder chapters.

### Implementation for User Story 3

- [x] T023 [US3] Create `_category_.json` to define the label for `website/docs/module3-isaac/`.
- [x] T024 [P] [US3] Create placeholder Markdown file `website/docs/module3-isaac/1-intro-to-isaac-sim.md`.

---

## Phase 7: Additional Content

**Purpose**: Scaffold the remaining content sections.

- [x] T025 [P] Create `_category_.json` to define the label for `website/docs/module4-vla/`.
- [x] T026 [P] Create `_category_.json` to define the label for `website/docs/capstone/`.
- [x] T027 [P] Create placeholder Markdown file `website/docs/module4-vla/1-vla-introduction.md`.
- [x] T028 [P] Create placeholder Markdown file `website/docs/capstone/1-capstone-overview.md`.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Final review, deployment preparation, and optional features.

- [x] T029 Review all generated content for consistency and adherence to the constitution.
- [x] T030 Configure and test the GitHub Actions workflow for deploying the Docusaurus site to GitHub Pages.
- [x] T031 [P] Add placeholder hooks for personalization features in a custom Docusaurus component (`website/src/components/PersonalizationHook.tsx`).
- [x] T032 [P] Add placeholder hooks for translation features in `website/docusaurus.config.ts`.

---

## Dependencies & Execution Order

- **Setup (Phase 1)** must complete before **Landing Page (Phase 2)** and **Foundational (Phase 3)**.
- **Landing Page (Phase 2)** and **Foundational (Phase 3)** can be done in parallel once Phase 1 is complete.
- User Story phases (4, 5, 6) and the Additional Content phase (7) can happen in parallel after Phase 3 is complete.
- **Polish (Phase N)** should be done last.

## Implementation Strategy

### MVP First (Landing Page + User Story 1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Landing Page
3. Complete Phase 3: Foundational
4. Complete Phase 4: User Story 1
5. **STOP and VALIDATE**: Build the Docusaurus site and verify that the landing page and the first module are complete and functional.

### Incremental Delivery

Each module (User Story) can be written and merged independently after the foundational setup is complete, allowing for incremental releases of the textbook.

---