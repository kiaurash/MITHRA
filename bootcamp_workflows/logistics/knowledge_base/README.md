# Knowledge Base System

## Overview

Token-efficient Q&A knowledge base for bootcamp logistics using compressed storage and query script.

## Architecture

```
knowledge_base/
├── README.md                    # This file
├── kb_schema.json              # Schema definition
├── kb.json.gz                  # Compressed Q&A data (DO NOT READ DIRECTLY)
├── kb_query.sh                 # Query script (use this!)
└── KB_QUERY_INSTRUCTIONS.md    # Query strategy guide for LLMs
```

## Key Features

✅ **Fool-proof design:** Compressed storage prevents accidental reads
✅ **In-memory decompression:** No disk traces, ~5-45ms latency overhead
✅ **Flexible queries:** Search, multi-term AND, category filtering, count
✅ **Token efficient:** 75-85% reduction vs loading full files
✅ **Safety checks:** Script errors if uncompressed kb.json exists
✅ **Scalable:** Can grow to 10K+ lines without risk

## Usage

### For LLMs

When user asks information questions:

1. Read `KB_QUERY_INSTRUCTIONS.md` for strategy
2. Use `kb_query.sh` script to query (never read kb.json.gz directly)
3. Synthesize answer naturally from results

**Example:**
```bash
./kb_query.sh --search "stuck"
./kb_query.sh --multi "mentor" "evaluation"
./kb_query.sh --category "deliverables"
```

### For Humans (Editing KB)

**To add/edit entries:**

```bash
# 1. Decompress
cd knowledge_base/
gunzip kb.json.gz

# 2. Edit kb.json (add Q&A entries following kb_schema.json)

# 3. Validate JSON syntax
jq empty kb.json

# 4. Recompress
gzip kb.json

# The script will error if you forget step 4
```

**Schema reference:** See `kb_schema.json` for mandatory/optional fields

## Current Statistics

- **Entries:** 30 Q&A pairs
- **Categories:** 7 (getting_help, program_structure, deliverables, timeline, technical, mentorship, community)
- **Sources:** getting_help.txt, program_information.txt, sprint_deliverables.txt
- **File size:** ~20KB uncompressed, ~5KB compressed
- **Query latency:** ~15-55ms

## Query Modes

| Mode | Usage | Example |
|------|-------|---------|
| Search | Find by keyword/phrase | `--search "stuck"` |
| Multi-term | AND logic (both must match) | `--multi "mentor" "demo"` |
| Category | List all in category | `--category "deliverables"` |
| Filtered | Search within category | `--search "submit" --filter-category "deliverables"` |
| Count | Get result count only | `--search "demo" --count` |

## Design Principles

1. **Script = Mechanism** - All jq logic, query patterns in script
2. **Instructions = Strategy** - When/what to query, adaptive decision-making
3. **Compressed storage** - Forces script usage, prevents accidental reads
4. **No redundancy** - Script handles mechanics, instructions guide strategy
5. **Fool-proof** - Multiple safety layers prevent token waste

## Token Comparison

| Approach | Tokens | Notes |
|----------|--------|-------|
| Load 3 logistics files | ~5,400 | getting_help.txt + program_info.txt + sprint_deliverables.txt |
| KB query (3-10 results) | ~200-400 | 75-85% savings |
| KB query (count only) | ~10 | Just a number |

## Future Expansion

Planned additions:
- FAQ entries from Slack
- Q&A summaries from lectures
- Common troubleshooting scenarios
- Technical how-to guides

Can scale to 300+ entries without performance issues.

## Safety Features

1. **Compressed storage** - Read tool fails on .gz files
2. **Uncompressed check** - Script errors if kb.json exists
3. **In-memory only** - zcat pipes to jq, no disk writes
4. **Clear instructions** - CLAUDE.md emphasizes using script only
5. **Audit capability** - Can log queries in script if needed

## Maintenance

**Weekly checks:**
- Verify kb.json.gz exists and kb.json does not
- Monitor query latency as KB grows
- Review common queries for optimization opportunities

**When adding entries:**
- Follow schema strictly (see kb_schema.json)
- Use 3-5 diverse question phrasings
- Include 10-20 keyphrases with semantic variations
- Test queries after adding new content

## Technical Details

**Compression:**
- Algorithm: gzip (standard)
- Ratio: ~4:1 (20KB → 5KB)
- Decompression: zcat streams to stdout

**Query pipeline:**
```
zcat kb.json.gz → jq (filter/select) → unique_by(id) → format → stdout
```

**Memory usage:**
- zcat buffer: ~32KB
- jq processing: ~500KB-1MB (depends on KB size)
- Total: < 2MB peak

**No persistent state:**
- Everything in pipe memory
- Freed on process exit
- Zero disk traces

## Contact

Questions or issues? See CLAUDE.md for bootcamp support channels.
