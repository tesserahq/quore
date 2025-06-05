# Understanding MCP Prompts vs Tools

# Understanding MCP Prompts vs Tools

## Overview

The Model Context Protocol (MCP) introduces the concepts of **prompts** and **tools** as part of its plugin system, enabling LLMs and agents to interact with external services in a standardized way. This guide breaks down the differences and the reasoning behind exposing prompts, clarifying how they should be used.

## What Are MCP Prompts?

In MCP, a `prompt` is a **declarative, user-facing capability** that a plugin/server exposes. While the term might suggest it's just a string prompt used by an LLM, it's more accurate to think of it as:

> A structured, callable instruction set that defines a task, its parameters, and optionally, how the LLM should fulfill it.

Prompts are:
- Publicly exposed by MCP servers via `prompts/list`
- Discoverable by orchestrators and LLM agents
- Often linked to internal tools and LLM logic
- Used to **guide external agents** on how to invoke functionality

### Why Expose Prompts?

You might ask: if the prompt is used internally by the plugin (e.g. a private string like “You are a weather bot…”), why expose it?

Answer: You’re **not exposing the LLM’s private instruction string**. You’re exposing the *interface* (name, description, arguments) that external systems can use to:
- **Discover what your plugin can do**
- **Call those capabilities with arguments**
- **Receive well-structured results**

This is analogous to OpenAPI/Function calling in OpenAI or plugin definitions in LangChain.

## Difference Between Tools and Prompts

| Aspect       | `tools`                                       | `prompts`                                          |
|--------------|-----------------------------------------------|----------------------------------------------------|
| Purpose      | Internal or low-level functionality           | Publicly exposed, intent-driven task wrappers      |
| LLM Involved?| Optional                                       | Often, yes (can contain internal LLM prompts)      |
| Visibility   | Not necessarily exposed                       | Exposed via `prompts/list` for discovery           |
| Use Case     | Compose internal logic, reusable primitives   | Callable units of work for agents/clients          |
| Analogy      | Functions or methods                          | Remote callable APIs or OpenAI Functions           |

## Example Scenario

You have 3 MCP servers:

- `calendar.mcp.local` with a prompt: `get_next_meeting`
- `weather.mcp.local` with a prompt: `get_forecast`
- `email.mcp.local` with a prompt: `send_email`

An agent receives a query:  
> "Do I need an umbrella for my next meeting?"

The orchestrator:
1. Calls the `get_next_meeting` prompt to get location & time
2. Uses `get_forecast` to fetch weather for that time/place
3. Uses `send_email` to notify attendees

Each of these was made discoverable via `prompts/list`. Without them, the agent wouldn't know what these services can do or how to interact with them.

## Final Takeaway

Think of MCP prompts as **declarative capability descriptors** — not just raw LLM prompt strings. They bridge the gap between low-level tools and agent-level intent, allowing systems to be dynamically introspected and composed.

## Resources and Resource Templates

In MCP, **resources** represent structured data objects that plugins can expose and share. These might include documents, events, files, tasks, or any domain-specific entities your server understands.

### What Are Resources?

Resources are:
- Publicly or privately scoped objects
- Discoverable via the `resources/list` API
- Referenced by prompts or tools
- Can be nested or hierarchical
- Typically include metadata (e.g. `id`, `type`, `title`, `created_at`)

Example:
```json
{
  "id": "doc-123",
  "type": "document",
  "title": "Quarterly Report",
  "created_at": "2025-01-01T10:00:00Z"
}
```

### Resource Templates

**Resource templates** define reusable data structures that prompts and tools can rely on. Think of them as schema blueprints for creating or referencing resources.

They help:
- Validate input/output data
- Enforce structure consistency
- Enable type-aware reasoning by LLMs or UIs

Example use cases:
- A `document` resource template ensures every doc has `title`, `content`, `author`.
- A `meeting` resource template includes `start_time`, `participants`, `location`.

Resource templates make it easier to design coherent, introspectable APIs and connect tools/prompts with real-world data.
