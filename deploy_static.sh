#!/usr/bin/env bash
# Sync static assets to a CDN bucket and invalidate the cache.

set -euo pipefail

BUCKET="example-bucket"
DISTRIBUTION_ID="ABCDEFG12345"

aws s3 sync staticfiles/ s3://$BUCKET/ --delete
aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" \
  --paths '/*'

