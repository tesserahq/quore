<p align="center">
  <img width="140px" src="assets/logo.png">
  
  <p align="center">
    A modular, multi-tenant AI platform designed to power intelligent agents through extensible plugins, vector search, and modern language model tooling. Built with FastAPI, PGVector, LangChain, and LlamaIndex, Quore provides a flexible foundation for building and deploying contextual AI experiences across projects and organizations.
  </p>
</p>

## ✨ Features

- **Workspaces & Projects**  
  Organize data, users, and configurations in isolated environments with full multi-tenancy support.

- **Pluggable Tooling via MCP**  
  Support for user-defined and community-developed agent tools using the [Model Context Protocol (MCP)](https://modelcontext.org/). Quore can discover, register, and interact with tools from remote repositories.

- **Vector Search with PGVector**  
  High-performance similarity search using PostgreSQL and PGVector. Supports project-scoped embeddings, metadata filtering, and customizable retrieval strategies.

- **LlamaIndex + LangChain Integration**  
  Native support for structured document ingestion, chunking, embedding, and retrieval using LlamaIndex’s modular data pipeline and LangChain’s agent framework.

- **Flexible Metadata & Labeling**  
  JSON-based labels on vector entries for dynamic filtering (e.g. user-level scoping, status flags, content tags).

- **Future-Proof Embedding Versioning**  
  Designed with extensibility in mind — supports future embedding model upgrades, A/B testing, and re-indexing workflows.

## 🧠 How It Works

1. **Create a Workspace**  
   Group related projects under a shared organization.

2. **Add a Project**  
   Each project has its own configuration, document sources, and embedding model.

3. **Ingest Data**  
   Upload documents or integrate with external systems. Quore uses LlamaIndex to chunk and embed content.

4. **Register Plugins**  
   Add MCP-compatible agent tools from GitHub or custom sources. Quore discovers available tools and makes them available to agents.

5. **Query the System**  
   Ask natural language questions. Quore performs vector retrieval and invokes the appropriate tools or agents to respond.

## 🧩 Plugin Architecture

Quore supports agent tools defined as [MCP](https://modelcontext.org/) servers. These can be:

- Downloaded from public GitHub repositories
- Discovered dynamically using a manifest or MCP handshake
- Registered per workspace or project, and enabled selectively

Each plugin exposes one or more tools that agents can use — such as `get_invoice_status`, `create_support_ticket`, or `search_logs`.

## 📦 Tech Stack

- **Python + FastAPI** — REST API and plugin lifecycle management
- **PostgreSQL + PGVector** — Scalable, production-grade vector search
- **LlamaIndex** — Document ingestion and indexing
- **LangChain** — Agent reasoning and orchestration
- **MCP** — Plugin communication protocol (via stdio or HTTP)

## 🚧 Status

> Quore is currently in **active development**.  
> We’re focusing on core infrastructure, plugin management, and vector indexing. Contributions, feedback, and early collaborators are welcome!

## 📖 License

[MIT](LICENSE)

## 🙌 Acknowledgments

Inspired by the work of [LangChain](https://github.com/langchain-ai/langchain), [LlamaIndex](https://github.com/jerryjliu/llama_index), and the [MCP community](https://modelcontext.org/).
