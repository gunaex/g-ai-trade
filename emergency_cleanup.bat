@echo off
REM Emergency Script to Clean .env from Git History
REM Run this AFTER revoking old API keys on Binance

echo ========================================
echo EMERGENCY: Removing .env from Git History
echo ========================================
echo.
echo WARNING: This will rewrite git history!
echo Make sure you have:
echo   1. REVOKED old API keys on Binance TH
echo   2. Generated NEW API keys
echo   3. Updated .env with NEW keys locally
echo.
pause

echo.
echo Step 1: Creating backup...
git branch backup-before-cleanup

echo.
echo Step 2: Removing .env from ALL commits...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all

echo.
echo Step 3: Cleaning up refs...
git for-each-ref --format="delete %%(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo.
echo ========================================
echo SUCCESS! .env removed from git history
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Verify .env is gone:
echo    git log --all --full-history -- .env
echo    (should show nothing)
echo.
echo 2. Force push to GitHub:
echo    git push origin --force --all
echo    git push origin --force --tags
echo.
echo 3. Verify on GitHub that .env is not visible
echo.
echo 4. Delete old API keys on Binance TH!
echo.
pause
