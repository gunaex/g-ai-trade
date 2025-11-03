# 🚨 SECURITY EMERGENCY - API KEYS EXPOSED

## CRITICAL ISSUE DISCOVERED

Your Binance API keys have been committed to git history and are **PUBLICLY VISIBLE** if this repository is on GitHub!

**Exposed Keys:**
- BINANCE_API_KEY: `42A2245C29AD75DC2900FE1E9BA660789E2102F812F3F08D5F4703997FC56E88`
- BINANCE_SECRET: `5460D0CB441096FD5D5AB14E69ED895D1D5AD44A37EEA26EC513167923EA241F`

**Commits containing keys:**
- `0836ca7` (Oct 30, 2025)
- `6384c66` (Oct 30, 2025)
- `27d9450` (Oct 30, 2025)

---

## ⚡ IMMEDIATE ACTIONS REQUIRED (DO THIS NOW!)

### 1. **REVOKE API KEYS IMMEDIATELY** (5 minutes)

Go to Binance TH and delete these API keys **RIGHT NOW**:

1. Visit: https://www.binance.th/en/my/settings/api-management
2. Find the API keys starting with `42A2245C...`
3. Click "Delete" and confirm
4. **DO NOT DELAY** - Anyone with access to your git history can use these keys!

### 2. **Generate NEW API Keys** (5 minutes)

After deleting the old keys:

1. Create new API keys on Binance TH
2. Set proper permissions: **Read + Trade ONLY** (NO Withdrawal!)
3. Enable IP whitelist (add your server's IP)
4. Copy the new keys (you'll need them in step 3)

### 3. **Update .env with NEW Keys** (1 minute)

```bash
# Edit .env file
notepad .env

# Replace with your NEW keys:
BINANCE_API_KEY=<your_new_api_key>
BINANCE_SECRET=<your_new_secret>
```

### 4. **Clean Git History** (10 minutes)

**Option A: If Repository is PRIVATE and you're the only contributor:**

```bash
# Remove .env from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push to remote (if already pushed)
git push origin --force --all
git push origin --force --tags
```

**Option B: If Repository is PUBLIC or has other contributors:**

⚠️ **NUCLEAR OPTION** - Delete and recreate repository:

1. Backup your code (copy to another folder)
2. Delete the GitHub repository
3. Create a new repository
4. Copy code back (WITHOUT .env file)
5. Ensure `.env` is in `.gitignore` before first commit
6. Commit and push clean code

### 5. **Verify Keys Are Revoked** (2 minutes)

Test if old keys still work:

```bash
# This should FAIL if keys are revoked
curl -H "X-MBX-APIKEY: 42A2245C29AD75DC2900FE1E9BA660789E2102F812F3F08D5F4703997FC56E88" \
  https://api.binance.th/api/v1/account
```

Expected: **401 Unauthorized** or **API key invalid**

---

## 📋 PREVENTION CHECKLIST

After fixing the immediate issue:

- [ ] Old API keys REVOKED on Binance TH
- [ ] New API keys generated with IP whitelist
- [ ] `.env` updated with new keys
- [ ] `.env` removed from git history
- [ ] Verified `.env` is in `.gitignore`
- [ ] Test with new keys: `python -c "from app.binance_client import get_binance_th_client; print(get_binance_th_client().get_server_time())"`

---

## 🛡️ LONG-TERM SECURITY MEASURES

### 1. **Use git-secrets** (Prevent future leaks)

```bash
# Install git-secrets
# Windows (with Chocolatey):
choco install git-secrets

# Add patterns to block
git secrets --add 'BINANCE_API_KEY=.*'
git secrets --add 'BINANCE_SECRET=.*'
git secrets --add 'SECRET_KEY=.*'

# Install hooks
git secrets --install
```

### 2. **Enable Branch Protection**

On GitHub:
- Settings → Branches → Add rule
- Require pull request reviews
- Require status checks to pass

### 3. **Add Pre-commit Hook**

Create `.git/hooks/pre-commit`:

```bash
#!/bin/sh
# Check for secrets before commit

if git diff --cached | grep -i "BINANCE_API_KEY\|BINANCE_SECRET"; then
    echo "ERROR: API keys detected in commit!"
    echo "Remove sensitive data before committing."
    exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 4. **Use Environment Variables in Production**

Never store production keys in files:

```bash
# On production server, set environment variables
export BINANCE_API_KEY="your_production_key"
export BINANCE_SECRET="your_production_secret"
export SECRET_KEY="your_64_char_secret"
```

---

## 📊 DAMAGE ASSESSMENT

### If Repository is PUBLIC on GitHub:

- ⚠️ **ASSUME KEYS ARE COMPROMISED**
- ⚠️ Anyone could have accessed them
- ⚠️ Keys may be in automated scrapers
- ⚠️ Check Binance account for unauthorized activity

### Actions:

1. Check Binance account history for suspicious trades
2. Check API usage logs
3. Change API keys immediately
4. Monitor account for 24-48 hours

### If Repository is PRIVATE:

- ✅ Lower risk (only collaborators have access)
- ✅ Still rotate keys as precaution
- ✅ Remove from git history anyway

---

## ✅ VERIFICATION STEPS

After completing all actions:

1. **Verify old keys don't work:**
   ```bash
   # Should fail
   curl -H "X-MBX-APIKEY: 42A2245C29AD75DC2900FE1E9BA660789E2102F812F3F08D5F4703997FC56E88" \
     https://api.binance.th/api/v1/account
   ```

2. **Verify .env is not in git:**
   ```bash
   git ls-files .env  # Should return nothing
   ```

3. **Verify .env not in history:**
   ```bash
   git log --all --full-history -- .env  # Should return nothing
   ```

4. **Test new keys work:**
   ```bash
   python -c "from app.binance_client import get_binance_th_client; print(get_binance_th_client().get_server_time())"
   ```

---

## 📞 SUPPORT

If you need help:

1. **Binance TH Support:** https://www.binance.th/en/support
2. **GitHub Support:** https://support.github.com/
3. **Git History Cleanup:** https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

---

## 🎯 FINAL CHECKLIST

Before deploying:

- [ ] Binance API keys rotated (old ones deleted)
- [ ] New keys have IP whitelist enabled
- [ ] New keys have Read+Trade only (NO withdrawal)
- [ ] .env file removed from git history
- [ ] .env file is in .gitignore
- [ ] Pre-commit hooks installed
- [ ] Tested with new keys
- [ ] Monitored Binance account for 24h

---

**DO NOT DEPLOY UNTIL ALL ITEMS ARE CHECKED OFF!**

**Last Updated:** 2025-11-03  
**Severity:** CRITICAL 🚨  
**Status:** ACTION REQUIRED NOW
