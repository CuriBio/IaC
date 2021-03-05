#!/bin/bash
source_path=${1:-.}
file_hashes=$(cd "$source_path" && find ./src -type f -not -name '*.pyc' | sort | xargs md5sum)
hash=$(echo "$file_hashes" | md5sum | cut -d' ' -f1)
echo '{"hash": "'"$hash"'"}'
