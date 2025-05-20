## Labeling System for Metadata at Ingestion

To make the vector data more searchable and filterable, we use a flexible **labeling system** for metadata. Labels are stored as simple **key–value pairs** attached to each vector (similar to Kubernetes labels on resources) and are applied at ingestion time. These metadata labels allow us to encode **contextual information** about each chunk in a structured way, beyond just the vector embedding itself.

Each vector entry will have an associated set of labels (metadata). In practice, this is stored as a JSONB column in Postgres to allow arbitrary keys. Using JSONB for metadata is convenient, as it can store multiple key–value pairs and be indexed for querying. For example, in our schema we might have a metadata JSONB column to hold labels . A given chunk could have labels like:

- dataset: "ProductDocs" – indicating which dataset the chunk belongs to (if we don’t have a separate column for dataset, we ensure it as a label).
- document_id: "doc_456" – an identifier for the source document or item the chunk came from.
- user_id: "123" – if the data is associated with a specific end-user or entity within the project.
- vm_status: "active" – dynamic status info (in the example of VM data).
- region: "us-west-2" – any other relevant attribute from the external source.
- source: "external_api" or other flags denoting origin, sensitivity, etc.

These labels are **attached at ingestion time** by whatever pipeline is adding the data. For static documents, some labels might be automatically added (e.g. a label for dataset name, document title, or document type). For dynamic data, the ingestion code can tag each vector with relevant metadata from the external service (as in the VM example, we tag the user ID it belongs to, the status, region, etc.). The system could also allow _custom labels_ from users – for instance, a user could tag certain documents as “confidential: true” or “category: finance”, which then get stored as labels on each chunk of those docs.

The **labeling system design** is inspired by Kubernetes labels: essentially free-form key/value metadata that can later be used to select subsets of data. By keeping it schema-flexible (using JSON), we avoid needing to alter the database schema for every new type of attribute. It also allows external integrations to consistently annotate data as it’s ingested without needing to coordinate on a rigid schema. We do, however, define some conventions: keys and values are strings, certain keys might be reserved (e.g. user_id, dataset, etc. used by our platform), and all labels are inherently scoped to the project (so we don’t need a global uniqueness on keys; different projects can use similar label keys without conflict).

**Storage and Performance:** All labels are stored in a JSONB column (metadata), which provides schema flexibility and supports user-defined labels at ingestion time. To support efficient querying, we will maintain a general-purpose GIN index on the full metadata column. This enables broad filtering via JSON containment queries like metadata @> '{"vm_status": "active"}'. However, since this index covers all keys, it can grow large and be less selective for high-cardinality queries.

To improve performance on common access patterns, we will also create dedicated expression indexes on a curated set of system-wide labels, such as user_id, vm_status, dataset, or document_id. These are labels that the platform defines and expects to be used frequently across projects and queries. By creating explicit indexes on expressions like (metadata->>'user_id'), we can speed up equality filters (user_id = '123') and reduce query latency for common filters.

We will not dynamically index user-defined labels to avoid index bloat, write amplification, and operational complexity. Instead, all user-specific filters will fall back to the general GIN index. This strikes a balance between flexibility and performance, ensuring predictable performance for core platform features without limiting extensibility.

**Query-Time Filtering with Labels**

One of the key advantages of labeling each vector chunk is the ability to **filter search results at query time** using these labels. In a multi-tenant scenario, this is crucial for enforcing data isolation and context-based querying. All vector searches in our platform will inherently be scoped to a project (so we **always filter by project** or use a project-specific table). Beyond that, we can apply fine-grained filters within the project’s data using any of the label key/values.

For example, consider a query where we only want to retrieve chunks that belong to a specific end-user and relate to active virtual machines. We could attach a filter like user_id = 123 AND vm_status = 'active' to the vector search. In SQL with PGVector, this would look like adding a WHERE clause on the metadata, for instance:

```
SELECT content, embedding, metadata
FROM vectors
WHERE project_id = &lt;project-id&gt;
AND metadata->>'user_id' = '123'
AND metadata->>'vm_status' = 'active'
ORDER BY embedding &lt;-&gt; \[query_embedding\]
LIMIT 5;
```

This ensures that the similarity search (the ORDER BY embedding &lt;-&gt; query) only considers vectors that satisfy those label conditions. As a result, the retrieved chunks will all be tagged with user_id=123 and vm_status=active, effectively **scoping the semantic search** to the active VMs of that user. This mechanism can enforce multi-tenant isolation (e.g. ensure one customer’s query doesn’t retrieve another customer’s data) by always filtering on a tenant or project ID label . In our design, the project_id itself is a column (and/or label) that is always used as a filter either via a WHERE clause or via row-level security policies, so cross-project leakage is prevented by design. (In a self-managed Postgres setup, one could enable row-level security and attach a policy that project_id = current_project on the vectors table , adding an extra safety net enforced in the database.)

At query time, the application or API layer will determine which filters to apply based on context. For a normal user query, it might automatically inject user_id = &lt;their id&gt; to ensure they only search their own data. If the query is meant to only search a particular dataset or data source, it can add dataset = X as a filter. These filters correspond to how data was labeled at ingestion. Essentially, **labels let us slice the vector index on demand**. Instead of searching the entire project’s vectors, we can narrow it down: e.g. “only vectors from dataset = SupportTickets and ticket_status = open” for a query asking about open support issues.

PGVector (and Postgres) will handle these conditions as part of the SQL query. Under the hood, **metadata filtering in PGVector is implemented as a regular SQL filter on the table** . This means that the vector similarity search (especially if using an approximate index like HNSW) does not inherently know about the filter – it finds nearest neighbors and then Postgres applies the WHERE clause to filter out any that don’t match. For _moderately sized_ data sets or common filters, this post-filtering is efficient enough: the database will fetch the top N similar vectors and discard those not matching, possibly fetching a few more until it has the desired number of results that pass the filter. However, if the label filter is very selective in a very large corpus, we need to ensure this remains performant. One way is to use the aforementioned GIN index on metadata, which can quickly pre-select the subset of rows matching the label condition. In practice, we might combine approaches: for example, use a **subquery** or indexed selection to get candidate IDs with the label, then apply vector distance ordering among those. Another approach is **partitioning or sharding by certain labels** so that the vector index itself is inherently smaller per partition (for instance, one could partition the table by project or by dataset). PGVector currently does not support using a single HNSW index with an internal metadata filter, so these workarounds (filter first or partition) are used when needed . In our context, project isolation is handled at a higher level (one project’s data isn’t even queried with another’s), so the primary use of filters is for within-project queries like the user or status examples.

**Example:** If vm_status has values “active” and “inactive”, one could even maintain two separate indexes or partitions (one for active, one for inactive) to optimize queries that always target active items. But since status can change, it may be simpler to keep one index and use label filtering. The label filtering in the query is flexible: we could even allow range queries or set-membership (though with simple key–value labels, it’s typically equality checks). The system could expose query syntax akin to Kubernetes label selectors (e.g. vm_status=active AND user_id in (123,124)) which it translates to the SQL conditions.

To summarize, **label filters at query time** allow targeted semantic searches. They are implemented via WHERE clauses on the vector table query, which Postgres applies either by post-filtering the similarity results or by using a JSON index to narrow the search space. This design gives us a powerful way to combine symbolic filtering with vector similarity – improving relevance and enforcing data scope. It enables multi-tenant isolation as well as functional segmentation of data (by type, by user, by status, etc.) during retrieval.
