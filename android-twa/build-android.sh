#!/usr/bin/env bash
# Build the நல்நாள் · NalNaal Android app from the live PWA.
# Usage: ./build-android.sh your-site.netlify.app
set -e

HOST="${1:-}"
if [ -z "$HOST" ]; then
  echo "Usage: ./build-android.sh <your-netlify-host>"
  echo "   e.g. ./build-android.sh nalnaal.netlify.app"
  exit 1
fi

echo "==> Pointing TWA config at https://$HOST"
sed -i '' "s/REPLACE_WITH_YOUR_NETLIFY_HOST/$HOST/g" twa-manifest.json

echo "==> Verifying the site is live and public..."
CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$HOST/manifest.json")
if [ "$CODE" != "200" ]; then
  echo "!! https://$HOST/manifest.json returned $CODE (need 200)."
  echo "   Make sure the site is claimed/public before building."
  exit 1
fi
echo "   OK (200)."

echo "==> Initializing Bubblewrap from the LIVE web manifest (most reliable)..."
echo "    (prompts for signing key; JDK/SDK already installed)"
npx @bubblewrap/cli@latest init --manifest "https://$HOST/manifest.json"

echo "==> Building..."
npx @bubblewrap/cli@latest build

echo ""
echo "==> Done. Artifacts in this folder:"
echo "     app-release-signed.apk   (install to test on a phone)"
echo "     app-release-bundle.aab   (upload to Google Play Console)"
echo ""
echo "==> Next: Bubblewrap printed an assetlinks.json. Save it to"
echo "     ../.well-known/assetlinks.json  then redeploy to Netlify"
echo "     so the app runs without a URL bar."
