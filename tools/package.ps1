param(
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [string]$UpstreamRef = "unknown"
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$packageRoot = Join-Path $SourceRoot "x64\Release\a"
if (-not (Test-Path $packageRoot)) {
    throw "Official Release package directory not found: $packageRoot"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Copy-Item (Join-Path $repo "Localization\OptiScalerCN.ini") (Join-Path $packageRoot "OptiScalerCN.ini") -Force
Copy-Item (Join-Path $repo "README.zh-CN.md") (Join-Path $packageRoot "README.OptiScaler-CN.zh-CN.md") -Force
Copy-Item (Join-Path $repo "UPSTREAM.md") (Join-Path $packageRoot "UPSTREAM.OptiScaler-CN.md") -Force
$sha = (git -C $SourceRoot rev-parse --short=12 HEAD).Trim()
$name = "OptiScaler-CN-$UpstreamRef-$sha.zip" -replace '[^A-Za-z0-9._-]','-'
$zip = Join-Path $OutputDir $name
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $packageRoot '*') -DestinationPath $zip -CompressionLevel Optimal
$hash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant()
@{
    upstream_ref = $UpstreamRef
    upstream_commit = (git -C $SourceRoot rev-parse HEAD).Trim()
    package = (Split-Path -Leaf $zip)
    sha256 = $hash
    built_at_utc = (Get-Date).ToUniversalTime().ToString('o')
} | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $OutputDir "build-metadata.json")
Write-Host "PACKAGE=$zip"
Write-Host "SHA256=$hash"
