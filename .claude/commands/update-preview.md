# Update Preview Command

Updates the UI preview pages and deploys to Vercel.

## Usage
`/update-preview` - Update and deploy all preview pages

## What This Command Does

### 1. Update checks-overview.html

For any check that has `status: "completed"` in release-plan.json but shows as `status: 'planned'` in the HTML:
- Change `status: 'planned'` to `status: 'implemented'`

### 2. Update index.html

For completed checks:
- Ensure they appear with the "NEW" badge (green) instead of "PLANNED" badge (orange)

### 3. Update Statistics

In both HTML files, update:
- Progress bar percentage
- Completed/In Progress/Not Started counts
- Phase completion counts

### 4. Deploy to Vercel

```bash
cd ui-preview && vercel --yes --prod
```

### 5. Verify Deployment

- Check the deployment URL is accessible
- Verify mobile responsiveness
- Display the new URLs

## Output

```
╔══════════════════════════════════════════════════════════════════════╗
║                    UI Preview Updated                                 ║
╚══════════════════════════════════════════════════════════════════════╝

Changes Made:
  ✓ checks-overview.html - Updated X check(s) to implemented
  ✓ index.html - Updated progress stats
  ✓ Deployed to Vercel

URLs:
  UI Preview: https://...vercel.app/
  Checks Overview: https://...vercel.app/checks-overview.html

Mobile: Verified responsive ✓
```

## When to Use

- After completing a check with /finish
- When statistics need updating
- Before sharing links with others
