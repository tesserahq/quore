# Datum Engineering Onboarding Guide

Welcome to Datum! This guide is designed to help new software engineers understand how we build, ship, and collaborate.

---

## About Datum

### Vision & mission

Datum is building the world’s first open network cloud — a neutral place where [Alt Clouds](https://link.datum.net/alt-clouds), tech incumbents, and digital leaders can programmatically interact with their unique ecosystem. Run workloads on our global infrastructure, in any of the public clouds, or on your private infrastructure, then leverage Datum’s global “fast path” network to deterministically route and observe traffic, privately connect with partners, and interact with customers. 

- **Mission**: To make 1k new hyperscalers by providing an internet built for AI: open, programmable, and designed for what’s next.
- **Vision**: To be the most trusted way for digital ecosystems to interact, with millions of intelligent connections to prove it.

Datum has a strong belief in transparency and building developer trust. Core components are released under the [AGPLv3 license](https://www.gnu.org/licenses/agpl-3.0.html), giving users full visibility and audit capability, the ability to adapt and self-host if needed, and long-term confidence without vendor lock-in.

---

### Why lean in to Datum?

Great question! You should chat with us if you're an...

- **Alt cloud provider** that needs networking super powers to service customers without building your own network and network teams. 
- **ISV or SaaS provider** that wants to embed networking capabilities in your offerings to accelerate adoption, meet requirements, etc. 
- **Enterprise customer** that needs telco-style capabilities to manage diverse connectivity for routing, security, privacy and cost issues.

| Challenge | How Datum Helps |
|----------|------------------|
| Connecting with clouds, partners, and customers globally | Datum acts as your connective tissue — one API, many ecosystems |
| Managing network complexity and interconnect | Use our fast path network and routing policies |
| Creating private, secure partner experiences | Build virtual “meet-me” environments with identity-aware routing |
| Observing and managing policy across providers | Inject policy, visibility, and control without building from scratch |
| Building AI-native workflows that reason about infrastructure | Agent-friendly, programmatic interfaces make this native |

If you'd like to learn more, please visit [our website](https://www.datum.net). 

### Our main projects

We're currently investing in two main areas:

- [Datum Cloud](https://github.com/datum-cloud/datum) is an open network cloud that you can run anywhere, backed by open source.
- [Milo](https://github.com/datum-cloud/milo) is an open source business OS that helps you grow and scale your Alt Cloud.

### Get involved

If you choose to contribute to any of our projects, we would love to work with you to ensure a great experience.

- Follow [us on LinkedIn](https://www.linkedin.com/company/datum-cloud/).
- Read and subscribe to the [Datum blog](https://www.datum.net/blog/).
- For general discussions, join us on the [Datum Community Slack](https://slack.datum.net) team.
- [Website](https://www.datum.net)



---

## Core Projects & Repositories

> Here are our key repositories and what they do. Each repo has its own README and setup instructions, but this is your map.

| Repo | Purpose | Maintainers | Stack |
|------|---------|-------------|-------|
| `datum-platform` | Main monorepo for the platform | @emiliano, @jessica | FastAPI, PGVector, LangChain |
| `datum-ui` | Frontend client | @jessica | React (Remix), Tailwind |
| `datum-agents` | Agent infrastructure + MCP tooling | @guillermo | Python, LangGraph, LlamaIndex |
| `datum-docs` | Developer documentation & tutorials | @geronimo | Markdown, MkDocs |
| `datum-infra` | Kubernetes + CI/CD infra (k3s, ArgoCD, Flux) | @emiliano | Pulumi, Helm, GitOps |

---

## Teams & Structure

### Founders

- **Zac Smith** – He started his first business at the age of 10 mowing lawns with his brother, Jacob. For the past 20 years, he has been focused on using software to build automated infrastructure platforms, helping to grow Voxel, a Linux-based hosting platform that was sold to Internap in 2011, into one of the early leading cloud hosting companies.

  In 2014, he co-founded Packet to empower technology-enabled Enterprises with automated bare metal infrastructure no matter where it was, what it was or who owned it. Backed by SoftBank, Dell Technologies, Third Point and Battery Ventures, Packet became the leader in bare metal compute automation and was acquired by Equinix in March 2020. 

  Until June 2023, he served as the Head of Edge Infrastructure at Equinix, leading the strategy, product and go to market for Equinix's bare metal compute and edge services platform.

  He lives in Manhattan with his wife and two children, invests in mission and community-driven founders via [www.hoti.vc](http://www.hoti.vc) and plays the double bass in local community orchestras.
- **Jacob Smith** – His professional experience involves digital infrastructure, internet marketing, sales, arts management, and classical music.

  A love of entrepreneurship inspired the co-founding of digital infrastructure startup Packet with his brother Zac in 2014. Packet — backed by SoftBank, Dell Capital, Samsung, Third Point, and others — was acquired by Equinix in 2020, and he was proud to help integrate and then scale what became Equinix Metal in the years that followed. 

  During the pandemic, he helped lead various aspects of GTM strategy and marketing for Equinix, focusing primarily on customer success, product-led growth, startups, developers, and open source. Before departing Equinix in 2023, he spent a year as part of the CRO leadership team, helping to roll out its first specialist sales organization and augment a scaled $8B sales-led revenue engine with PLG and self-service. 

  A professional bassoonist by training, he played principal bassoonist with the Academy of Vocal Arts Opera Orchestra, Opera Philadelphia, and others for many years. From 2007 until 2016 he held fundraising and marketing roles at the Philadelphia Chamber Music Society and Marlboro Music Festival.

  A native of California, he lives in Southern Vermont.

### Core Team

- **Chris Berridge** – UX, UI and Product designer with a track record of crafting impactful and intuitive digital experiences for brands worldwide.
  He has worked at the forefront of the design industry for over 15 years; creating award-winning work, partnering with and shaping successful design teams, and crafting digital products and services for the likes of Google, Adidas, and M&C Saatchi.

- **Steve Smyser** – Financial and business operations leader ensuring organizational efficiency.

- **Alex Benik** – Trusted advisor and longtime investor at Battery, now associated with Encoded.vc.

- **Joshua Reese** – Industry veteran with experience across the stack at The Planet, SoftLayer, and StackPath.

- **Scot Wells** – Platform engineering expert who contributed to scaling infrastructure and systems at Highwinds and StackPath.

- **Jose Szychowski** – Backend developer passionate about creating innovative solutions and addressing complex challenges.

- **Felix Widjaja** – Brings 25 years of experience with websites, currently focused on Customer Experience.

- **Yahya Fakhroji** – Frontend Developer dedicated to crafting engaging web experiences and transforming ideas into impactful solutions.

- **Dodik Gaghan** - Building, Automating, and Scaling | Full-Stack x DevOps / K8s x Cloud-Native
 
- **Emiliano Jankowski** – He has been building Enterprise-grade software for the last 20 years. He started his first project using QuickBasic at the age of 15, and since then he hasn't stopped. He has worked at advanced levels with a variety of languages including ASP.NET (C#), Java, PHP, Ruby, Go, Elixir, and Python. In addition to programming fundamentals, he has taken dozens of projects from zero to 100%, including architecting, client and stakeholder interfacing, and infrastructure, CI/CD, and monitoring. He prides himself on being both hardworking and collaborative and has built & led cross-functional remote teams with over 20 members.

- **Brandon Burciaga** – As a polyglot full stack principal engineer and cloud solutions architect with nearly a decade in the software industry, Brandon is incredibly passionate about his craft. A dedicated student, engineer, scientist, and researcher, he thrives on solving challenging, complex problems across scale and context.

  Brandon has led organization-wide digital transformations and helped define technical vision for both startups and large enterprises across sectors like Healthcare, eCommerce, Enterprise Banking, and FinTech. He sets a high bar for operational excellence, beginning with himself and leading by example.

  Deeply committed to diversity, equity, and inclusion, Brandon actively cultivates healthy, accessible, and safe environments. He believes people always come first and lives to give back and serve others, continuing the cycle of support he's experienced in his own journey.


---

## Your First Week

- [ ] Clone and run the main platform repo
- [ ] Read the `CONTRIBUTING.md` and `README.md` in `datum-platform`
- [ ] Join Slack channels: `#platform`, `#agents`, `#design`, `#infra`
- [ ] Schedule onboarding 1:1 with your team lead
- [ ] Ask Worktron (our Slack AI) any question you have!
- [ ] Check out open "good first issues" in GitHub

---

## Project History

Datum was conceived from the realization that modern, data-intensive workloads—particularly those driven by AI and intelligence—demand more agile and programmable networking solutions. The founders, after their experience with Packet and its integration into Equinix, identified a persistent gap: while compute and storage had become highly programmable, networking remained complex and less accessible to software developers. ￼

Recognizing that businesses increasingly operate across multiple clouds, handle vast amounts of data, and collaborate with numerous partners, Datum aims to provide a network cloud that offers:

* Programmable network superpowers that can run anywhere.
* A global platform for seamless interaction with diverse ecosystems.
* Federation as a core concept, allowing workloads to run on shared infrastructure or other environments as needed. ￼

Early prototypes focused on integrating OpenAI and pgvector. As the platform evolved, features like a plugin registry (via MCP), multi-tenant support, and an agent runtime inspired by LangGraph were added. Datum continues to build upon this foundation, striving to make networking as flexible and developer-friendly as other areas of cloud infrastructure.

---

## Tools & Integrations

### Slack Channel Guide

Datum uses naming conventions to organize Slack channels. Here's how to navigate them:

#### Project Channels (`proj-*`)
| Channel              | Description                    | Activity Level |
|----------------------|--------------------------------|----------------|
| `proj-cloud-portal`  | Manages the Cloud Portal UI    | 🔥 High        |
| `proj-aim`           | AI/ML infrastructure modules    | 🚀 Medium      |

#### Team Channels (`team-*`)
...

#### Most Active Public Channels
| Channel      | Description                  |
|--------------|------------------------------|
| `engineering`| General engineering chatter  |
| `team-infra` | Infra discussions + support  |
| `proj-automation-hub`  | Automation tips and hacks    |

### Development Tools

#### GitHub
- **Purpose**: Code repository, issue tracking, and CI/CD pipeline management
- **Access Process**: 
  - Request access through: tech-access@datum.net
  - Required info: GitHub username
  - Access level: Based on team (Developer/Admin)
- **Setup Steps**:
  1. Enable 2FA on your GitHub account
  2. Install GitHub CLI: `brew install gh`
  3. Configure SSO with your @datum.net email
- **Primary Repos**: datum-platform, datum-ui, datum-agents

#### Cursor
- **Purpose**: Primary IDE for development with AI assistance
- **Access Process**: Self-service installation
- **Setup Steps**:
  1. Download from: https://cursor.sh
  2. Install via: `brew install --cask cursor`
  3. Request API key from: dev-tools@datum.net

### Communication & Collaboration

#### Slack
- **Purpose**: Primary communication platform
- **Access Process**:
  - Auto-provisioned with @datum.net email
  - Workspace: datum-team.slack.com
- **Required Channels**:
  - #platform
  - #engineering
  - #team-announcements
  - #support
- **Setup Steps**:
  1. Accept invitation from HR
  2. Install desktop & mobile apps
  3. Configure notifications

#### Linear
- **Purpose**: Project management and sprint planning
- **Access Process**: 
  - Request access through: pm-tools@datum.net
  - SSO enabled with @datum.net email
- **Setup Steps**:
  1. Accept email invitation
  2. Join your team's workspace
  3. Install desktop app

### Infrastructure & Monitoring

#### Zitadel
- **Purpose**: Authentication and user management
- **Access Process**:
  - URL: auth.datum.net
  - Auto-provisioned with company email
- **Setup Steps**:
  1. Complete initial login
  2. Configure MFA
  3. Generate development API keys

#### Grafana/Prometheus Stack
- **Purpose**: Metrics, logging, and system monitoring
- **Access Process**:
  - URL: monitoring.datum.net
  - Request access: infra@datum.net
- **Required Dashboards**:
  - Platform Overview
  - Service Health
  - Error Rates
- **Setup Steps**:
  1. Login with SSO
  2. Install Grafana CLI tools
  3. Configure local monitoring

### Development Infrastructure

#### n8n
- **Purpose**: Workflow automation
- **Access Process**:
  - URL: workflows.datum.net
  - Request through: automation@datum.net
- **Setup Steps**:
  1. Accept invitation
  2. Configure personal API tokens
  3. Review common workflows

#### Local Development Environment
- **Required Tools**:
  ```bash
  # Install core tools
  brew install kubectl helm k9s
  brew install --cask docker
  
  # Install language-specific tools
  brew install python@3.11 node@18 go@1.21
  
  # Install monitoring tools
  brew install prometheus grafana loki
  ```

### Access Request Template
```json
{
  "employee": {
    "name": "",
    "email": "",
    "github_username": "",
    "start_date": "",
    "team": "",
    "role": ""
  },
  "access_levels": {
    "github": "developer|admin",
    "linear": "member|admin",
    "grafana": "viewer|editor",
    "zitadel": "developer|admin"
  },
  "additional_tools": []
}
```

> Note: All access requests are automatically processed through our onboarding workflow. Submit requests at least 3 days before start date.

---

## Knowledge Base Highlights

```md
### How to deploy a new environment
1. Fork `datum-infra`
2. Configure your env in `environments/dev`
3. Push and let ArgoCD sync it
```

```md
### Common Lingo
- MCP: Model Context Protocol
- RAG: Retrieval Augmented Generation
- PGVector: PostgreSQL + Vector Search
```

---

## Developer Tips

- Use `make run-dev` to start local envs
- Prefer async workflows for LLM responses
- Use `docs/DECISIONS.md` to track major tech choices
- Every commit should be AI-explainable — write great PR descriptions
