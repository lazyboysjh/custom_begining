param(
    [string]$RepoUrl = "https://github.com/lazyboysjh/custom_begining.git",
    [string]$Branch = "main",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$publishRoot = Join-Path $root "tmp\frontend-publish"
$distRoot = Join-Path $root "dist\shengtang\ui"
$expectedFiles = @(
    "dist/shengtang/ui/cover/index.html",
    "dist/shengtang/ui/status/index.html"
)

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )

    & git -C $WorkingDirectory @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
}

& node (Join-Path $root "scripts\copy_shengtang_static.mjs")
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build the Shengtang static frontend."
}

$actualDistFiles = @(
    Get-ChildItem -LiteralPath $distRoot -Recurse -File |
        ForEach-Object { $_.FullName.Substring($root.Length + 1).Replace("\", "/") } |
        Sort-Object
)
$missingDistFiles = @($expectedFiles | Where-Object { $_ -notin $actualDistFiles })
if ($missingDistFiles.Count -gt 0) {
    throw "Frontend publish files are missing: [$($missingDistFiles -join ', ')]"
}

$tmpParent = Split-Path $publishRoot -Parent
$resolvedTmpParent = (Resolve-Path $tmpParent).Path
if (-not $publishRoot.StartsWith($resolvedTmpParent + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to clean a publish directory outside $resolvedTmpParent"
}

if (Test-Path -LiteralPath $publishRoot) {
    Remove-Item -LiteralPath $publishRoot -Recurse -Force
}

try {
    New-Item -ItemType Directory -Path (Join-Path $publishRoot "dist\shengtang\ui\cover") -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $publishRoot "dist\shengtang\ui\status") -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $distRoot "cover\index.html") -Destination (Join-Path $publishRoot "dist\shengtang\ui\cover\index.html")
    Copy-Item -LiteralPath (Join-Path $distRoot "status\index.html") -Destination (Join-Path $publishRoot "dist\shengtang\ui\status\index.html")

    Invoke-Git $publishRoot init --initial-branch=$Branch
    Invoke-Git $publishRoot config user.name "lazyboysjh"
    Invoke-Git $publishRoot config user.email "73016304+lazyboysjh@users.noreply.github.com"
    Invoke-Git $publishRoot add --all

    $trackedFiles = @(& git -C $publishRoot ls-files | Sort-Object)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect the frontend-only publish index."
    }
    if (Compare-Object -ReferenceObject $expectedFiles -DifferenceObject $trackedFiles) {
        throw "Publish index contains files outside the frontend whitelist: $($trackedFiles -join ', ')"
    }

    Invoke-Git $publishRoot commit -m "Publish Shengtang frontend"
    $commit = (& git -C $publishRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $commit) {
        throw "Unable to resolve the frontend publish commit."
    }

    if ($DryRun) {
        Write-Host "DRY RUN OK: $commit"
        Write-Host "Tracked frontend files: $($trackedFiles -join ', ')"
        return
    }

    Invoke-Git $publishRoot push --force $RepoUrl "HEAD:refs/heads/$Branch"
    Invoke-Git $root fetch $RepoUrl "+refs/heads/${Branch}:refs/remotes/origin/${Branch}"

    $oldRef = $env:ST_CDN_REF
    $oldVersion = $env:ST_CDN_V
    try {
        $env:ST_CDN_REF = $commit
        $env:ST_CDN_V = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds().ToString()
        & python (Join-Path $root "build_shengtang_card.py")
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend published, but rebuilding the local card failed."
        }
    }
    finally {
        $env:ST_CDN_REF = $oldRef
        $env:ST_CDN_V = $oldVersion
    }

    Write-Host "PUBLISHED_FRONTEND_COMMIT=$commit"
    Write-Host "LOCAL_CARD_CDN_UPDATED=1"
}
finally {
    if (Test-Path -LiteralPath $publishRoot) {
        Remove-Item -LiteralPath $publishRoot -Recurse -Force
    }
}
