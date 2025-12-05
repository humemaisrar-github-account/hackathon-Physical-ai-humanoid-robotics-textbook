# Data Model: Physical AI & Humanoid Robotics Textbook

**Date**: 2025-12-04
**Status**: Draft

This document defines the core data entities for the textbook project. As this is a content-based project, the "data model" refers to the structure of the Markdown files and the relationships between them.

## Key Entities

### Textbook
- **Description**: The top-level container for all content. It is represented by the Docusaurus project itself.
- **Attributes**:
    - `title`: The title of the book.
    - `version`: The semantic version of the book.
- **Relationships**: Contains Modules.

### Module
- **Description**: A collection of chapters focused on a high-level topic (e.g., ROS 2). Represented as a directory within `/docs`.
- **Attributes**:
    - `title`: The title of the module (e.g., "ROS 2 — Robotic Nervous System").
    - `order`: A number determining its position in the sidebar.
- **Relationships**: Contains Chapters.

### Chapter
- **Description**: A detailed lesson with objectives, labs, and notes. Represented as a Markdown file within a module directory.
- **Attributes**:
    - `title`: The title of the chapter.
    - `learning_objectives`: A list of what the reader will learn.
- **Relationships**: Belongs to one Module. Contains Code Examples and Diagrams.

### Code Example
- **Description**: A standalone, executable piece of code demonstrating a concept. Embedded within a Chapter using Markdown code blocks.
- **Attributes**:
    - `language`: The programming language (e.g., `python`, `cpp`).
    - `code`: The code content.

### Diagram
- **Description**: A visual aid to explain a concept. Can be a static image or a Mermaid diagram embedded in a Chapter.
- **Attributes**:
    - `source_file`: Path to the image file (if static).
    - `mermaid_code`: The code for the Mermaid diagram.

### Glossary
- **Description**: A special chapter containing definitions for key terms used throughout the book.
- **Attributes**:
    - `term`: The word being defined.
    - `definition`: The explanation of the term.
