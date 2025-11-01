#!/bin/bash
# Knowledge Base Query Script
# Decompresses kb.json.gz in-memory and queries using jq
# Usage: ./kb_query.sh [OPTIONS]

set -euo pipefail

KB_DIR="$(cd "$(dirname "$0")" && pwd)"
KB_GZ="$KB_DIR/kb.json.gz"
KB_PLAIN="$KB_DIR/kb.json"

# Safety check: prevent uncompressed file from existing
if [ -f "$KB_PLAIN" ]; then
    echo "ERROR: Uncompressed kb.json found. This wastes tokens if accidentally read." >&2
    echo "Compress it first: cd $KB_DIR && gzip kb.json" >&2
    exit 1
fi

if [ ! -f "$KB_GZ" ]; then
    echo "ERROR: kb.json.gz not found at $KB_GZ" >&2
    exit 1
fi

# Parse arguments
QUERY_MODE="search"
QUERY_TERM=""
CATEGORY=""
SOURCE=""
TERM1=""
TERM2=""
LIMIT=10
COUNT_ONLY=false
FIELDS="id,question,answer,category"

show_usage() {
    cat << 'EOF'
Usage: ./kb_query.sh [OPTIONS]

Query modes:
  --search <term>              Search keyphrases and questions (default)
  --category <cat>             List all entries in category
  --source <source>            List all entries from source
  --multi <term1> <term2>      Search with AND logic (both terms must match)

Introspection:
  --list-sources               List all unique source values in metadata
  --list-categories            List all unique category values

Filters:
  --filter-category <cat>      Filter results by category
  --filter-source <source>     Filter results by metadata.source

Options:
  --count                      Show count of results only
  --limit <n>                  Limit results (default: 10)
  --fields <fields>            Comma-separated output fields
                              Default: id,question,answer,category
                              Available: id,questions,answer,keyphrases,category,metadata,links

Examples:
  ./kb_query.sh --list-sources
  ./kb_query.sh --list-categories
  ./kb_query.sh --search "stuck"
  ./kb_query.sh --search "langgraph" --filter-category "getting_help"
  ./kb_query.sh --source "week_1_standup_notes.txt"
  ./kb_query.sh --multi "mentor" "demo"
  ./kb_query.sh --category "deliverables"
  ./kb_query.sh --search "sprint" --count
  ./kb_query.sh --search "help" --limit 5
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --search)
            QUERY_MODE="search"
            QUERY_TERM="$2"
            shift 2
            ;;
        --category)
            QUERY_MODE="category"
            CATEGORY="$2"
            shift 2
            ;;
        --source)
            QUERY_MODE="source"
            SOURCE="$2"
            shift 2
            ;;
        --list-sources)
            QUERY_MODE="list-sources"
            shift
            ;;
        --list-categories)
            QUERY_MODE="list-categories"
            shift
            ;;
        --multi)
            QUERY_MODE="multi"
            TERM1="$2"
            TERM2="$3"
            shift 3
            ;;
        --filter-category)
            CATEGORY="$2"
            shift 2
            ;;
        --filter-source)
            SOURCE="$2"
            shift 2
            ;;
        --count)
            COUNT_ONLY=true
            shift
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --fields)
            FIELDS="$2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            show_usage
            exit 1
            ;;
    esac
done

# Build jq output based on requested fields
build_jq_output() {
    local field_spec="{"

    if [[ "$FIELDS" == *"id"* ]]; then
        field_spec="${field_spec}id, "
    fi
    if [[ "$FIELDS" == *"question"* ]] && [[ "$FIELDS" != *"questions"* ]]; then
        field_spec="${field_spec}question: .questions[0], "
    fi
    if [[ "$FIELDS" == *"questions"* ]]; then
        field_spec="${field_spec}questions, "
    fi
    if [[ "$FIELDS" == *"answer"* ]]; then
        field_spec="${field_spec}answer, "
    fi
    if [[ "$FIELDS" == *"keyphrases"* ]]; then
        field_spec="${field_spec}keyphrases, "
    fi
    if [[ "$FIELDS" == *"category"* ]]; then
        field_spec="${field_spec}category, "
    fi
    if [[ "$FIELDS" == *"metadata"* ]]; then
        field_spec="${field_spec}metadata, "
    fi
    if [[ "$FIELDS" == *"links"* ]]; then
        field_spec="${field_spec}links, "
    fi

    # Remove trailing comma and space
    field_spec="${field_spec%, }"
    field_spec="${field_spec}}"

    echo "$field_spec"
}

OUTPUT_SPEC=$(build_jq_output)

# Execute query based on mode
case $QUERY_MODE in
    search)
        if [ -z "$QUERY_TERM" ]; then
            echo "ERROR: --search requires a search term" >&2
            show_usage
            exit 1
        fi

        # Build filter conditions
        FILTER_CONDITIONS='((.keyphrases[] | ascii_downcase | contains($query | ascii_downcase)) or (.questions[] | ascii_downcase | contains($query | ascii_downcase)))'

        if [ -n "$CATEGORY" ]; then
            FILTER_CONDITIONS=".category == \$cat and $FILTER_CONDITIONS"
        fi

        if [ -n "$SOURCE" ]; then
            FILTER_CONDITIONS="$FILTER_CONDITIONS and (.metadata.source | ascii_downcase | contains(\$src | ascii_downcase))"
        fi

        JQ_FILTER="[.qa_entries[] | select($FILTER_CONDITIONS)] | unique_by(.id)"

        if [ "$COUNT_ONLY" = true ]; then
            if [ -n "$CATEGORY" ] && [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" --arg cat "$CATEGORY" --arg src "$SOURCE" "$JQ_FILTER | length"
            elif [ -n "$CATEGORY" ]; then
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" --arg cat "$CATEGORY" "$JQ_FILTER | length"
            elif [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" --arg src "$SOURCE" "$JQ_FILTER | length"
            else
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" "$JQ_FILTER | length"
            fi
        else
            if [ -n "$CATEGORY" ] && [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" --arg cat "$CATEGORY" --arg src "$SOURCE" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            elif [ -n "$CATEGORY" ]; then
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" --arg cat "$CATEGORY" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            elif [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" --arg src "$SOURCE" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            else
                zcat "$KB_GZ" | jq --arg query "$QUERY_TERM" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            fi
        fi
        ;;

    category)
        if [ -z "$CATEGORY" ]; then
            echo "ERROR: --category requires a category name" >&2
            show_usage
            exit 1
        fi

        if [ -n "$SOURCE" ]; then
            JQ_FILTER='[.qa_entries[] | select(.category == $cat and (.metadata.source | ascii_downcase | contains($src | ascii_downcase)))]'
            if [ "$COUNT_ONLY" = true ]; then
                zcat "$KB_GZ" | jq --arg cat "$CATEGORY" --arg src "$SOURCE" "$JQ_FILTER | length"
            else
                zcat "$KB_GZ" | jq --arg cat "$CATEGORY" --arg src "$SOURCE" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            fi
        else
            JQ_FILTER='[.qa_entries[] | select(.category == $cat)]'
            if [ "$COUNT_ONLY" = true ]; then
                zcat "$KB_GZ" | jq --arg cat "$CATEGORY" "$JQ_FILTER | length"
            else
                zcat "$KB_GZ" | jq --arg cat "$CATEGORY" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            fi
        fi
        ;;

    source)
        if [ -z "$SOURCE" ]; then
            echo "ERROR: --source requires a source name" >&2
            show_usage
            exit 1
        fi

        if [ -n "$CATEGORY" ]; then
            JQ_FILTER='[.qa_entries[] | select((.metadata.source | ascii_downcase | contains($src | ascii_downcase)) and .category == $cat)]'
            if [ "$COUNT_ONLY" = true ]; then
                zcat "$KB_GZ" | jq --arg src "$SOURCE" --arg cat "$CATEGORY" "$JQ_FILTER | length"
            else
                zcat "$KB_GZ" | jq --arg src "$SOURCE" --arg cat "$CATEGORY" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            fi
        else
            JQ_FILTER='[.qa_entries[] | select(.metadata.source | ascii_downcase | contains($src | ascii_downcase))]'
            if [ "$COUNT_ONLY" = true ]; then
                zcat "$KB_GZ" | jq --arg src "$SOURCE" "$JQ_FILTER | length"
            else
                zcat "$KB_GZ" | jq --arg src "$SOURCE" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            fi
        fi
        ;;

    multi)
        if [ -z "$TERM1" ] || [ -z "$TERM2" ]; then
            echo "ERROR: --multi requires two search terms" >&2
            show_usage
            exit 1
        fi

        # Build filter conditions for multi-term
        FILTER_CONDITIONS='((.keyphrases[] | ascii_downcase | contains($q1 | ascii_downcase)) or (.questions[] | ascii_downcase | contains($q1 | ascii_downcase))) and ((.keyphrases[] | ascii_downcase | contains($q2 | ascii_downcase)) or (.questions[] | ascii_downcase | contains($q2 | ascii_downcase)))'

        if [ -n "$CATEGORY" ]; then
            FILTER_CONDITIONS=".category == \$cat and ($FILTER_CONDITIONS)"
        fi

        if [ -n "$SOURCE" ]; then
            FILTER_CONDITIONS="($FILTER_CONDITIONS) and (.metadata.source | ascii_downcase | contains(\$src | ascii_downcase))"
        fi

        JQ_FILTER="[.qa_entries[] | select($FILTER_CONDITIONS)] | unique_by(.id)"

        if [ "$COUNT_ONLY" = true ]; then
            if [ -n "$CATEGORY" ] && [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" --arg cat "$CATEGORY" --arg src "$SOURCE" "$JQ_FILTER | length"
            elif [ -n "$CATEGORY" ]; then
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" --arg cat "$CATEGORY" "$JQ_FILTER | length"
            elif [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" --arg src "$SOURCE" "$JQ_FILTER | length"
            else
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" "$JQ_FILTER | length"
            fi
        else
            if [ -n "$CATEGORY" ] && [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" --arg cat "$CATEGORY" --arg src "$SOURCE" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            elif [ -n "$CATEGORY" ]; then
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" --arg cat "$CATEGORY" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            elif [ -n "$SOURCE" ]; then
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" --arg src "$SOURCE" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            else
                zcat "$KB_GZ" | jq --arg q1 "$TERM1" --arg q2 "$TERM2" --argjson limit "$LIMIT" "$JQ_FILTER | .[:\$limit] | .[] | $OUTPUT_SPEC"
            fi
        fi
        ;;

    list-sources)
        # List all unique source values from metadata
        zcat "$KB_GZ" | jq -r '[.qa_entries[].metadata.source] | unique | .[]' | sort
        ;;

    list-categories)
        # List all unique category values
        zcat "$KB_GZ" | jq -r '[.qa_entries[].category] | unique | .[]' | sort
        ;;
esac
