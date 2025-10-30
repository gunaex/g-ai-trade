@echo off
:: Create root-level files
type nul > .gitignore
type nul > requirements.txt
type nul > .env
type nul > run.bat

:: Create app folder and files
mkdir app\repo
mkdir app\ai
mkdir app\security

type nul > app\__init__.py
type nul > app\main.py
type nul > app\db.py
type nul > app\models.py
type nul > app\repo\orders.py
type nul > app\ai\decision.py

:: Create ui/src structure
mkdir ui\src\pages
mkdir ui\src\components
mkdir ui\src\lib

type nul > ui\src\pages\Trade.tsx
type nul > ui\src\pages\Monitoring.tsx
type nul > ui\src\pages\Settings.tsx
type nul > ui\src\components\Navbar.tsx
type nul > ui\src\lib\api.ts
type nul > ui\src\App.tsx
type nul > ui\src\index.css

:: Create ui config files
type nul > ui\vite.config.ts
type nul > ui\package.json

:: Create dist folder
mkdir dist