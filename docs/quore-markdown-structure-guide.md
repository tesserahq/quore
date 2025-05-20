---
title: "How to Structure Markdown Files for Ingestion into Quore"
version: "1.0"
tags: ["rag", "llamaindex", "markdown", "embedding", "semantic-chunking"]
---

# How to Structure Markdown Files for Ingestion into Quore

This guide explains how to format and structure your `.md` files for optimal ingestion in LlamaIndex, enabling high-quality retrieval-augmented generation (RAG) performance.

## Why Structure Matters

LlamaIndex transforms Markdown into semantic nodes. Clean structure improves:

- Chunking logic
- Semantic embedding quality
- Retrieval relevance

## 1. Use Clear, Consistent Headings

LlamaIndex uses headings to split content logically.

### Good Example

```markdown
# Installation Guide

## Requirements

## Installation Steps

### Step 1: Download

### Step 2: Install
```

### Bad Example

```markdown
# Guide

### Step1

### Info
```

## Keep Sections Short and Focused

````markdown
## API Authentication

You must use a Bearer token for every request. Tokens can be generated from the settings dashboard.

Example:

```bash
curl -H "Authorization: Bearer $TOKEN" https://api.foo.com/data
```
````

## Use Metadata (Frontmatter)

Use YAML frontmatter to add context like tags or versioning.

```yaml
---
title: "FooApp API Guide"
version: "2.1"
tags: ["api", "authentication", "fooapp"]
---
```

This metadata can be indexed and used to filter or boost relevance.

## Favor Semantic Content

Avoid filler and generic intros in every section.

Do:

```markdown
## Deleting a Resource

Use `DELETE /resources/:id` to permanently remove a resource.
```

Don’t:

```
## Overview

In this section, we will explain how to delete a resource.
```

## Use Lists and Tables Appropriately

Flat lists and clean tables enhance comprehension and retrieval.

## Plan Comparison

| Feature    | Free  | Pro   |
| ---------- | ----- | ----- |
| API Access | Yes   | Yes   |
| Rate Limit | 100/d | 10k/d |

## Organize Files Logically

Store files in semantic directories and use meaningful filenames.

```markdown
docs/
├── getting-started/
│ └── install.md
├── api/
│ └── authentication.md
└── guides/
└── troubleshooting.md
```

## Optional: Add Anchors for Direct Linking

```markdown
LlamaIndex can use anchor references in advanced retrieval logic.

## Using Anchors

You can add custom anchors like this:

<a name="generate-token"></a>

### Generating a Token
```

## Filename Best Practices

When ingesting Markdown files into Quore, filenames become part of the document’s metadata. This affects how documents are grouped, filtered, and referenced during retrieval.

### ✅ Best Practices

| Practice                                | Why It Matters                                              |
|-----------------------------------------|--------------------------------------------------------------|
| **Use kebab-case names**                | Improves readability and avoids issues with whitespace       |
| **Make filenames descriptive**          | Helps identify document purpose quickly                      |
| **Keep names concise**                  | Easier to parse and manage in code and UIs                   |
| **Avoid spaces or special characters**  | Prevents path issues in cross-platform environments          |
| **Use semantic folders if possible**    | Encodes hierarchy and domain context into the path           |

**Examples:**

```bash
# Good
docs/api/authentication-guide.md
guides/install-steps.md

# Bad
docs/api/guide1.md
docs/My Guide.md
```
