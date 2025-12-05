# Chapter Structure Contract

**Date**: 2025-12-04
**Status**: Defined

This document defines the "contract" or required structure for every chapter's Markdown file in the textbook. Adherence to this structure is mandatory for all contributions to ensure consistency.

## Chapter Template

Each chapter `.md` file MUST follow this structure:

```markdown
---
title: "Chapter Title"
---

## Learning Objectives

- Objective 1
- Objective 2
- Objective 3

## [Concept 1 Title]

Explanation of the first concept.

### Code Example: [Title of Example]

```python
# Code block for the concept
print("Hello, World!")
```

## [Concept 2 Title]

Explanation of the second concept.

### Diagram: [Title of Diagram]

```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```

## Practical Lab

A step-by-step tutorial for the reader to apply what they've learned.

1.  **Step 1**: ...
2.  **Step 2**: ...

## Safety and Ethics Notes

A dedicated section to discuss the safety and ethical implications of the chapter's topic, in accordance with the project constitution.

## Summary

A brief summary of the key takeaways from the chapter.
```
