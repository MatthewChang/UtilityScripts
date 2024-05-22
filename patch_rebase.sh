#!/bin/bash

# Check if the correct number of arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 branch_A branch_B"
    exit 1
fi

# Assign the arguments to variables
branch_A=$1
branch_B=$2

# Fetch the latest data from the remote repository
git fetch

# Check if branch B is merged into branch A
if git branch --merged "$branch_A" | grep -q "$branch_B"; then
    echo "Branch $branch_B is merged into $branch_A"
    patch_file="/tmp/$branch_B-to-$branch_A.patch"
    # Create a patch file of the differences between the two branches
    git diff "$branch_B" "$branch_A" > "$patch_file"

    # Checkout branch B and create a new branch named "branch_A_squashed"
    new_name="$branch_A"_squashed
    git checkout -b "$new_name" "$branch_B"

    # Apply the patch to the new branch
    git apply "$patch_file"

    echo "Patch applied to new branch: $new_name"
    # Remove the patch file
    rm "$patch_file"
else
    echo "Branch $branch_B is not merged into $branch_A"
fi