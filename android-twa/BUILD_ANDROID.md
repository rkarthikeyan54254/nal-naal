# Building the நல்நாள் · NalNaal Android app (TWA)

This turns the live PWA into a real Android app (`.apk` for testing, `.aab` for the Play Store) using **Bubblewrap** — Google's official tool for wrapping a PWA as a Trusted Web Activity (TWA).

## Prerequisites (already checked on this Mac)

- ✅ Java 17 (installed: Zulu17)
- ✅ Node.js 24 + npx
- The app deployed to a **public HTTPS URL** (your Netlify site)

You'll also need the **Android SDK** — Bubblewrap can download it for you on first run, or install Android Studio.

## Step 1 — Get your permanent public URL

The app is deployed. If you used the anonymous deploy, **claim it** to your Netlify account so it's permanent:
- Open the "Claim on Netlify" link that was printed after deploy, OR
- Re-deploy under your account:
  ```bash
  cd tamil-nal-app
  npx netlify-cli login          # opens browser, log in once
  npx netlify-cli deploy --dir=. --prod
  ```
Note your final host, e.g. `nalnaal.netlify.app` (you can rename the site in Netlify settings to something memorable).

## Step 2 — Point the TWA config at your URL

Edit `android-twa/twa-manifest.json` and replace every `REPLACE_WITH_YOUR_NETLIFY_HOST` with your host (e.g. `nalnaal.netlify.app`).

Or run this one-liner from the repo root (replace the host):
```bash
sed -i '' 's/REPLACE_WITH_YOUR_NETLIFY_HOST/nalnaal.netlify.app/g' android-twa/twa-manifest.json
```

## Step 3 — Build the Android app

```bash
cd android-twa
npx @bubblewrap/cli@latest init --manifest ./twa-manifest.json
# Bubblewrap will:
#  - offer to download the Android SDK & JDK if missing (say yes)
#  - ask for a signing key — create a new one, SAVE the password & keystore safely
npx @bubblewrap/cli@latest build
```

This produces:
- `app-release-signed.apk` — install on any Android phone to test (`adb install app-release-signed.apk`, or copy to the phone and tap it)
- `app-release-bundle.aab` — upload this to the Google Play Console

## Step 4 — Digital Asset Links (removes the browser URL bar)

For the app to run full-screen without a URL bar, the website must verify it trusts the app. Bubblewrap prints an `assetlinks.json` after building. Place it on your site at:
```
/.well-known/assetlinks.json
```
Add it to the repo under `.well-known/assetlinks.json`, redeploy to Netlify, and the TWA will run chrome-less.

(Bubblewrap generates the exact file contents including your app's SHA-256 fingerprint — copy it verbatim.)

## Step 5 — Publish to Google Play

1. Create a Google Play Developer account ($25 one-time): https://play.google.com/console
2. Create a new app → upload the `.aab`
3. Fill in store listing (use the icon at `icons/icon-512.png`, screenshots from the app)
4. Complete content rating, privacy policy, and data-safety forms
5. Submit for review

## Updating the app later

When you change the PWA, just redeploy to Netlify — installed TWAs load the live site, so users get updates instantly **without** a Play Store update. You only rebuild/re-upload the `.aab` if you change the app icon, name, or Android-level config.

---

## Quick reference — what each file is

- `twa-manifest.json` — Bubblewrap's config (package id `app.nalnaal.twa`, name, colors, icon, URL)
- After `init`: an Android project is generated here you can also open in Android Studio
- Keep your **signing keystore + password** safe — you need the same key for every future Play update
