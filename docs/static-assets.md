# Static Asset Workflow

This project uses hashed filenames and pre-compressed assets to enable long-term
caching and efficient delivery. The steps below outline the expected build and
deployment process.

1. **Build front end** – `npm run build` should produce files like
   `main.abcdef12.js` and `styles.deadbeef.css` inside `dist/` along with an
   `asset-manifest.json`.
2. **Compress assets** – After the build, run `brotli -q 11 dist/**/*.{js,css}`
   followed by `gzip -k dist/**/*.{js,css}` to create `.br` and `.gz` files.
3. **Collect static** – `./manage.py collectstatic` gathers the built files into
   `STATIC_ROOT` and generates the hashed manifest used by Django.
4. **Deploy** – Use `deploy_static.sh` (see below) to sync the contents of
   `STATIC_ROOT` to the configured storage location or CDN bucket.

## Expected HTTP Headers

Hashed assets are served with the following cache policy:

```
Cache-Control: public, max-age=31536000, immutable
Vary: Accept-Encoding
```

Requests with `Accept-Encoding: br` receive the Brotli compressed variant.
When Brotli is not supported, gzip is used instead.

HTML and API responses continue to include `Cache-Control: no-cache`.

## Deployment Script

`deploy_static.sh` is a simple helper that syncs the `staticfiles/` directory to
an S3 bucket and creates a CloudFront invalidation. Populate the `BUCKET` and
`DISTRIBUTION_ID` variables then run the script on each release.

```bash
#!/usr/bin/env bash
aws s3 sync staticfiles/ s3://$BUCKET/ --delete
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID \
  --paths '/*'
```

## Purging

Invalidate the CDN or remove files from the bucket whenever the build pipeline
changes hashing or compression settings.
