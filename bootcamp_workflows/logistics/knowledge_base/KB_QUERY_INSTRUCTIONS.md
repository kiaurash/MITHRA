# KB Query Instructions

## When to Use
✅ Information questions: "How/Who/When/What/Where..."
❌ Workflow execution, technical implementation, codebase search

## Workflow

### Step 0: Get syntax (first time in session)
```bash
./kb_query.sh --help
```
Read help output for exact command syntax, query modes, and options.

### Step 1: Introspect metadata (when needed)
```bash
./kb_query.sh --list-sources    # Discover available sources
./kb_query.sh --list-categories # Discover available categories
```

### Step 2: Query with --count first
Use discovered syntax/metadata to construct query. Always start with --count.

### Step 3: Adapt based on count
- **0-2**: Broaden term or try category listing
- **3-10**: Remove --count to get results
- **11+**: Add filters or --limit

### Step 4: Synthesize response
Answer naturally with specifics (names, links, dates). Never mention KB/script.

## Key Behaviors

1. **Run --help first** in each session to get current syntax
2. **Introspect metadata** before querying - don't guess
3. **Always --count first** to evaluate result volume
4. **Matching**: Source/search = partial match; category = exact match
