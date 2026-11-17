#!/usr/bin/env bash
# Usage: ./new-post.sh "My Post Title"
set -e
title="${1:?Usage: ./new-post.sh \"My Post Title\"}"
slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g')
[ -z "$slug" ] && slug="post-$(date +%H%M%S)"
file="_posts/$(date +%Y-%m-%d)-$slug.md"
cat > "$file" <<EOF
---
layout: post
title: "$title"
date: $(date '+%Y-%m-%d %H:%M:%S %z')
categories: []
---

Write here...
EOF
echo "Created $file"
${EDITOR:-nano} "$file"
