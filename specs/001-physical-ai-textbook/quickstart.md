# Quickstart Guide: Contributing to the Textbook

**Date**: 2025-12-04
**Status**: Draft

This guide provides a quick overview for new contributors, both human and agent, on how to get started with adding or editing content for the "Physical AI & Humanoid Robotics" textbook.

## 1. Prerequisites

- You must have `git` installed.
- You must have `node` and `npm` (or `yarn`) installed to run Docusaurus.
- Familiarize yourself with the [Project Constitution](../.specify/memory/constitution.md) and the [Feature Specification](./spec.md).

## 2. Getting Started

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Install dependencies**:
    Navigate to the `website` directory and install the necessary packages.
    ```bash
    cd website
    npm install
    ```

3.  **Run the development server**:
    To see a live preview of the Docusaurus site:
    ```bash
    npm start
    ```
    The site will be available at `http://localhost:3000`.

## 3. Contribution Workflow

1.  **Create a new feature branch**:
    Use the `/sp.specify` command to define a new feature (e.g., a new chapter). This will create a new branch for you.

2.  **Add your content**:
    - Add new `.md` files in the appropriate `docs/module-name/` directory.
    - Ensure your chapter follows the [Chapter Structure Contract](./contracts/chapter-structure.md).
    - Add any images to the `static/img` directory.

3.  **Preview your changes**:
    Run `npm start` in the `website` directory to ensure your changes render correctly.

4.  **Commit and Push**:
    Commit your changes and push them to the remote repository.

5.  **Create a Pull Request**:
    Open a pull request against the `main` branch. Your contribution will be reviewed for compliance with the project constitution.
