$ErrorActionPreference = "Continue"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$dockerConfig = Join-Path $projectRoot ".docker-config"

New-Item -ItemType Directory -Force -Path $dockerConfig | Out-Null

$env:DOCKER_CONFIG = $dockerConfig

Set-Location $projectRoot

function Test-DockerReady {
    docker info *> $null
    return $LASTEXITCODE -eq 0
}

if (-not (Test-DockerReady)) {
    $dockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

    if (Test-Path $dockerDesktop) {
        Write-Host "Starting Docker Desktop..."
        Start-Process -FilePath $dockerDesktop -WindowStyle Hidden

        for ($attempt = 1; $attempt -le 12; $attempt++) {
            Start-Sleep -Seconds 5
            if (Test-DockerReady) {
                break
            }
        }
    }
}

if (-not (Test-DockerReady)) {
    Write-Host "Docker is not running yet. Open Docker Desktop, wait until it says the engine is running, then run this script again."
    exit 1
}

docker compose up --build
exit $LASTEXITCODE
