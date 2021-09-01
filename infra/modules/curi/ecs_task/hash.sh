#!/bin/bash
source_path=${1:-.}
file_hashes=$(cd "$source_path" && find ./ -type f -not -name '*.pyc' | sort | xargs md5sum)
hash=$(echo "$file_hashes" | md5sum | cut -d' ' -f1)

# TODO check arch and do the right thing
# if you're running this on a mac comment out the 2 above lines and uncomment the 2 below
# file_hashes=$(cd "$source_path" && find ./ -type f -not -name '*.pyc' | sort | xargs md5)
# hash=$(echo "$file_hashes" | md5 | cut -d' ' -f1)

echo '{"hash": "'"$hash"'"}'
