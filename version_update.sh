#!/bin/bash

MANIFEST_FILE="mektools/manifest.json"
INIT_FILE="mektools/__init__.py"

# Ensure the manifest file exists
if [ ! -f "$MANIFEST_FILE" ]; then
    echo "Error: $MANIFEST_FILE not found!"
    exit 1
fi

# Ensure the __init__.py file exists
if [ ! -f "$INIT_FILE" ]; then
    echo "Error: $INIT_FILE not found!"
    exit 1
fi

# Function to safely parse JSON fields
parse_json_field() {
    local key=$1
    grep "\"$key\":" "$MANIFEST_FILE" | sed -E 's/.*: "(.*)",?/\1/'
}

# Parse the manifest.json
NAME=$(parse_json_field "name")
AUTHOR=$(parse_json_field "author")
VERSION=$(grep '"version":' "$MANIFEST_FILE" | sed -E 's/.*: \[(.*)\],?/\1/' | tr -d ' ')
BLENDER_VERSION=$(grep '"min_version":' "$MANIFEST_FILE" | sed -E 's/.*: "(.*)"/\1/' | tr '.' ',')
DESCRIPTION=$(parse_json_field "description")
CATEGORY=$(parse_json_field "category")
LOCATION=$(parse_json_field "location")

# Construct the new bl_info dictionary
NEW_BL_INFO=$(cat <<EOF
bl_info = {
    "name": "$NAME",
    "author": "$AUTHOR",
    "version": (${VERSION// /}),
    "blender": (${BLENDER_VERSION}),
    "description": "$DESCRIPTION",
    "category": "$CATEGORY",
    "location": "$LOCATION",
}
EOF
)

# Update __init__.py using awk
awk -v new_bl_info="$NEW_BL_INFO" '
BEGIN { added = 0 }
/bl_info =/ { 
    added = 1 
    print new_bl_info
    while (getline && !/\}/) {} 
    next 
}
{ print }
END {
    if (added == 0) {
        print new_bl_info
    }
}' "$INIT_FILE" > "$INIT_FILE.tmp" && mv "$INIT_FILE.tmp" "$INIT_FILE"

echo "Updated bl_info in $INIT_FILE:"
echo "$NEW_BL_INFO"




