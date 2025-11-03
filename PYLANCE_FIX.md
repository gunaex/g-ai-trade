# Pylance Import Error Fix Guide

## Issue
Pylance shows error: `Import "nest_asyncio" could not be resolved`

## Root Cause
VS Code/Pylance is using a different Python interpreter than the one where `nest-asyncio` is installed.

## Solution

### Option 1: Select Correct Python Interpreter (Recommended)

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type: `Python: Select Interpreter`
3. Choose the interpreter from your `.venv` folder:
   - Windows: `.venv\Scripts\python.exe`
   - Linux/Mac: `.venv/bin/python`

### Option 2: Reinstall Package in Current Environment

```bash
# Activate virtual environment first
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Then install
pip install nest-asyncio==1.5.8
```

### Option 3: Install All Requirements

```bash
pip install -r requirements.txt
```

## Verification

Run this command to verify installation:
```bash
python -c "import nest_asyncio; print('nest-asyncio is installed'); nest_asyncio.apply()"
```

Expected output: `nest-asyncio is installed`

## Still Having Issues?

1. **Reload VS Code Window**
   - Press `Ctrl+Shift+P` → `Developer: Reload Window`

2. **Check Python Path in VS Code**
   - Look at bottom-left corner of VS Code
   - Should show: `Python 3.11.x ('.venv': venv)`

3. **Verify Package Location**
   ```bash
   python -c "import nest_asyncio; print(nest_asyncio.__file__)"
   ```
   Should show path inside `.venv` folder

## Note

The import error is a **Pylance/IDE issue only**. The code will run fine because:
- ✅ `nest-asyncio==1.5.8` is in `requirements.txt`
- ✅ Package is actually installed (verified by terminal test)
- ✅ Import is now at top of `backtesting_engine.py`

You can safely ignore the Pylance warning if the code runs successfully.
