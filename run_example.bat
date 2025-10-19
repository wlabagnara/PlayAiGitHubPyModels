rem a tiny wrapper script to export .env into the current cmd session before running (manual approach)
@echo off
for /f "usebackq tokens=1* delims==" %%A in (".env") do set "%%A=%%B"
.venv\Scripts\python -m example.app

rem extra scripts to run directly on command line from root workspace...
rem check list of available models on your github account

rem doesn't work?...
rem .venv\Scripts\python -c "from github_models.client import GitHubModelsClient, Config; c=GitHubModelsClient(Config.from_env()); print(c.list_models())"

rem this works... (this script inputs the .env file directly)
rem python scripts\try_models.py