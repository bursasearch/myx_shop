#!/bin/bash
# Sync local repo with upstream (bursasearch) and push to origin (your fork)

# Exit immediately if a command fails
set -e

# Fetch latest changes from upstream
git fetch upstream

# Checkout your main branch
git checkout main

# Merge upstream changes into your local main
git merge upstream/main

# Push the updated main branch to your origin repo
git push origin main

echo "✅ Sync complete: upstream merged and pushed to origin."
