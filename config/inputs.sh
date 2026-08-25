#!/usr/bin/env bash
# Defines how to run each benchmark in a reproducible way.
# Use: get_cmd <category> <algorithm> <language> <binary_or_java_dir>

get_cmd () {
  local cat="$1"
  local algo="$2"
  local lang="$3"
  local path="$4"   # for c/cpp/go/rust: path to ./benchmark ; for java: folder path

  case "$algo" in
    # CLBG-style: uses N as argv[1]
    fannkuch_redux)
      if [[ "$lang" == "java" ]]; then
        echo "cd \"$path\" && java Main 12"
      else
        echo "\"$path\" 12"
      fi
      ;;

    fasta)
      if [[ "$lang" == "java" ]]; then
        echo "cd \"$path\" && java Main 2500000"
      else
        echo "\"$path\" 2500000"
      fi
      ;;

    # Needs stdin (provide a fixed input file)
    reverse_complement)
      # Create input file if missing (small but valid)
      mkdir -p inputs
      if [[ ! -f inputs/revcomp_input.txt ]]; then
        cat > inputs/revcomp_input.txt <<'EOF'
>ONE
ACGTACGTACGTACGTACGTACGTACGTACGT
>TWO
GATTACAAGGTTCCGGAA
EOF
      fi
      if [[ "$lang" == "java" ]]; then
        echo "cd \"$path\" && java Main < \"$(pwd)/inputs/revcomp_input.txt\""
      else
        echo "\"$path\" < \"$(pwd)/inputs/revcomp_input.txt\""
      fi
      ;;

    # ⚠️ Your custom benchmarks: set safe args (avoid 0)
    binary_search)
      if [[ "$lang" == "java" ]]; then
        echo "cd \"$path\" && java Main 1000000"
      else
        echo "\"$path\" 1000000"
      fi
      ;;

    stream_merge)
      if [[ "$lang" == "java" ]]; then
        echo "cd \"$path\" && java Main 1000000"
      else
        echo "\"$path\" 1000000"
      fi
      ;;

    *)
      # Default: run without args
      if [[ "$lang" == "java" ]]; then
        echo "cd \"$path\" && java Main"
      else
        echo "\"$path\""
      fi
      ;;
  esac
}
