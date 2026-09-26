# GitHub Push

From this project folder in PowerShell:

```powershell
git init
git add .
git status
git commit -m "Initial commit - AI Library Book Recommendation System"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Before `git add .`, check `git status` and make sure no `.env` or secret files are listed.
