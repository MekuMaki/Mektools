#!/bin/bash

MANIFEST_FILE="mektools/manifest.json"
INIT_FILE="mektools/__init__.py"
TOML_FILE="mektools/blender_manifest.toml"

# Ensure required files exist
if [ ! -f "$MANIFEST_FILE" ]; then
    echo "Error: $MANIFEST_FILE not found!"
    exit 1
fi

if [ ! -f "$INIT_FILE" ]; then
    echo "Error: $INIT_FILE not found!"
    exit 1
fi

if [ ! -f "$TOML_FILE" ]; then
    echo "Error: $TOML_FILE not found!"
    exit 1
fi

# Function to safely parse JSON fields (supports both strings & numbers)
parse_json_field() {
    local key=$1
    grep "\"$key\":" "$MANIFEST_FILE" | sed -E 's/.*: "?([^",]+)"?,?/\1/'
}

# Parse manifest.json
NAME=$(parse_json_field "name")
AUTHOR=$(parse_json_field "author")
VERSION=$(grep '"version":' "$MANIFEST_FILE" | sed -E 's/.*: \[(.*)\],?/\1/' | tr -d ' ')
VERSION_BUT_WITHDOTS=$(grep '"version":' "$MANIFEST_FILE" | sed -E 's/.*: \[(.*)\],?/\1/' | tr -d ' ' | tr ',' '.')
FEATURE_NAME=$(parse_json_field "feature_name")
FEATURE_PATCH=$(parse_json_field "feature_patch") 
BLENDER_VERSION=$(grep '"blender":' "$MANIFEST_FILE" | sed -E 's/.*: "(.*)"/\1/')
BLENDER_VERSION_BUT_WITHDOTS=$(grep '"blender":' "$MANIFEST_FILE" | sed -E 's/.*: \[(.*)\],?/\1/' | tr -d ' '| tr ',' '.')
DESCRIPTION=$(parse_json_field "description")
CATEGORY=$(parse_json_field "category")
LOCATION=$(parse_json_field "location")

# Construct new bl_info dictionary
NEW_BL_INFO=$(cat <<EOF
bl_info = {
    "name": "$NAME",
    "author": "$AUTHOR",
    "version": (${VERSION// /,}),
    "blender": (${BLENDER_VERSION//./,}),
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

# ---------------------------------------
# Update blender_manifest.toml
# ---------------------------------------

# Function to replace a key's value in a TOML file
update_toml_field() {
    local key="$1"
    local value="$2"
    local file="$3"

    # If the key exists, replace its value. Otherwise, append it.
    if grep -q "^$key\s*=" "$file"; then
        sed -i -E "s|^$key\s*=.*|$key = \"$value\"|" "$file"
    else
        echo "$key = \"$value\"" >> "$file"
    fi
}

# Update fields in blender_manifest.toml
update_toml_field "name" "$NAME" "$TOML_FILE"
update_toml_field "version" "$VERSION_BUT_WITHDOTS" "$TOML_FILE"
update_toml_field "feature_name" "$FEATURE_NAME" "$TOML_FILE"
update_toml_field "feature_patch" "$FEATURE_PATCH" "$TOML_FILE" 
update_toml_field "blender_version_min" "$BLENDER_VERSION_BUT_WITHDOTS" "$TOML_FILE"

echo "Updated version in $TOML_FILE:"
grep "version" "$TOML_FILE"






