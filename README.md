# Web Video Downloader

A small self-hosted web app you can use from your iPhone's Safari browser.
Deploy it for free on Render.com — no credit card, no local install needed.

## 1. Put these files in a GitHub repository

Create a free account at github.com, make a new repository, and upload every
file in this folder (including the `templates` folder) using "Add file" →
"Upload files" in the GitHub web UI. No command line needed.

## 2. Deploy on Render (free tier)

1. Create a free account at render.com (sign up with GitHub for a one-click link)
2. Click "New" → "Web Service"
3. Select your repository
4. Render detects the `Dockerfile` automatically — leave settings as default
5. Click "Create Web Service" and wait a couple of minutes for the build

Render gives you a permanent public URL like
`https://your-app-name.onrender.com`.

Note: on the free tier, the app "sleeps" after 15 minutes of no traffic and
takes 30–60 seconds to wake up on the next visit. That's expected — just
wait for the page to load.

## 3. Make it feel like an app on iPhone

1. Open the site in Safari
2. Tap the Share icon (square with an arrow)
3. Tap "Add to Home Screen"

It'll now launch full-screen from your home screen like a native app.

## Notes

- Downloaded files are saved to the `downloads/` folder on the server, and
  served to your phone via a "Save to Files" button, which uses iOS's normal
  Safari download flow.
- Only download content you own, have explicit permission to save, or that's
  licensed for reuse. Downloading other people's videos may violate the
  platform's Terms of Service and copyright law depending on your use case.
