rem ** Example batch scripts to run python scripts from the command line (very manual approach)   :-(  **
rem      - manually edit this file to run the example lines you want
rem      - run directly on command line from root workspace...

@echo off

rem a tiny wrapper script to export .env into the current cmd session before running our main example application 
for /f "usebackq tokens=1* delims==" %%A in (".env") do set "%%A=%%B"
.venv\Scripts\python -m example.app

rem check list of available models on your github account
rem    (this script inputs the .env file directly)
rem python scripts\try_models.py

rem doesn't work?...
rem .venv\Scripts\python -c "from github_models.client import GitHubModelsClient, Config; c=GitHubModelsClient(Config.from_env()); print(c.list_models())"
