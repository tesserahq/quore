# Summarizing GitHub Issues with Local LLMs (Ollama + Llama3)

## Core idea
Use a **map → refine → reduce** pipeline to fit within context limits and scale across many issues.

## Steps

1. **Check context window**
   - Query Ollama for the model’s `context` (do not hardcode).
   - Example: `ollama show llama3 | grep context`.

2. **Define budgets**
   - Reserve tokens for prompt and output.
   - Formula:  
     `INPUT_BUDGET = (CTX - PROMPT_HEAD - OUTPUT_BUDGET) * 0.9`.

3. **Chunk issues (map stage)**
   - Split issue body into chunks under `INPUT_BUDGET`.
   - Summarize each chunk into strict JSON:  
     `{ tl_dr, key_points[], risks[], blockers[], owners[], labels[], severity }`.

4. **Merge per-issue summaries (refine stage)**
   - If multiple chunks per issue, merge partial JSONs into one compact summary.

5. **Batch issues (reduce stage)**
   - Estimate avg tokens per issue summary (~200).
   - Compute `max_issues_per_batch = INPUT_BUDGET / avg_issue_tokens`.
   - Reduce batches into rollups, then reduce rollups again if needed.
   - Output JSON:  
     `{ themes[], duplicates[], deps[], prioritized[], global_risks[], next_actions[] }`.

6. **Practical notes**
   - Run map stage concurrently, reduce sequentially.
   - Cache by content hash to avoid recomputation.
   - Strip or hash code blocks unless essential.
   - Validate JSON strictly, re-ask on parse errors.
   - Use `temperature=0` for deterministic outputs.

## Benefits
- Works with local models of varying context sizes (8k, 32k, etc.).
- Prevents overrunning context windows.
- Produces structured, composable summaries suitable for automation.