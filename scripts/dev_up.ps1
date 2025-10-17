$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $MyInvocation.MyCommand.Path)
cd ..\infra
docker compose up --build
Pop-Location
