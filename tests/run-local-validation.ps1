<#
.SYNOPSIS
Run the preferred local maintainer validation sequence for openwrt-docs4ai.

.DESCRIPTION
This helper codifies the terminal testing discipline documented in DEVELOPMENT.md.
It is the one-command local maintainer validation path for this repository.

The script intentionally validates only local changes. Remote GitHub Actions
validation remains a separate step because CI can only validate a pushed commit,
not uncommitted local edits.

The default sequence is:
1. Focused pytest contract and regression suites
2. Deterministic fixture-backed smoke runner
3. Sequential local smoke runner

Each stage writes a dedicated log file under tmp/ci/local-validation/<timestamp>/,
and the script stops at the first failing stage.

.PARAMETER RunAi
Include the cache-backed AI stage in both smoke runners.

.PARAMETER KeepTemp
Preserve each smoke runner's temporary directory for inspection.

.PARAMETER SkipPytest
Skip the focused pytest stage.

.PARAMETER SkipFixtureSmoke
Skip tests/00-smoke-test.py.

.PARAMETER SkipSequentialSmoke
Skip tests/openwrt-docs4ai-00-smoke-test.py.

.PARAMETER ResultRoot
Override the root directory used for stage logs. Relative paths are resolved
from the repo root.

.EXAMPLE
pwsh -File tests/run-local-validation.ps1

.EXAMPLE
pwsh -File tests/run-local-validation.ps1 -RunAi -KeepTemp
#>

[CmdletBinding()]
param(
    [switch]$RunAi,
    [switch]$KeepTemp,
    [switch]$SkipPytest,
    [switch]$SkipFixtureSmoke,
    [switch]$SkipSequentialSmoke,
    [string]$ResultRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $pythonExe)) {
    throw "Repo virtual environment not found at $pythonExe. Create or refresh .venv before using this helper."
}

if ([string]::IsNullOrWhiteSpace($ResultRoot)) {
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $resolvedResultRoot = Join-Path $repoRoot "tmp\ci\local-validation\$timestamp"
}
elseif ([System.IO.Path]::IsPathRooted($ResultRoot)) {
    $resolvedResultRoot = $ResultRoot
}
else {
    $resolvedResultRoot = Join-Path $repoRoot $ResultRoot
}

$null = New-Item -ItemType Directory -Path $resolvedResultRoot -Force
$stageResults = [System.Collections.Generic.List[object]]::new()

function New-SmokeArguments {
    param(
        [Parameter(Mandatory)]
        [string]$ScriptPath
    )

    $arguments = @($ScriptPath)

    if ($RunAi) {
        $arguments += '--run-ai'
    }

    if ($KeepTemp) {
        $arguments += '--keep-temp'
    }

    return $arguments
}

function Invoke-ValidationStage {
    param(
        [Parameter(Mandatory)]
        [int]$Index,

        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [string[]]$Arguments,

        [Parameter(Mandatory)]
        [string]$LogFile
    )

    Write-Host ''
    Write-Host ("[{0}] {1}" -f $Index, $Name) -ForegroundColor Cyan
    Write-Host ("    Log: {0}" -f $LogFile)

    $global:LASTEXITCODE = 0
    $start = Get-Date

    & $pythonExe @Arguments 2>&1 | Tee-Object -FilePath $LogFile

    $exitCode = if ($null -ne $LASTEXITCODE) {
        [int]$LASTEXITCODE
    }
    else {
        0
    }

    $durationSeconds = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)
    $status = if ($exitCode -eq 0) { 'PASS' } else { 'FAIL' }

    $stageResults.Add(
        [pscustomobject]@{
            Index = $Index
            Name = $Name
            Status = $status
            ExitCode = $exitCode
            DurationSeconds = $durationSeconds
            LogFile = $LogFile
        }
    )

    if ($exitCode -ne 0) {
        throw "Stage '$Name' failed with exit code $exitCode. See $LogFile."
    }
}

$selectedStages = @()

if (-not $SkipPytest) {
    $selectedStages += [pscustomobject]@{
        Name = 'Focused pytest suites'
        Arguments = @(
            '-m',
            'pytest',
            'tests/test_00_pipeline_units.py',
            'tests/test_01_workflow_contract.py',
            'tests/test_02_fixture_pipeline_contract.py',
            'tests/test_03_wiki_corpus_sanity.py',
            'tests/test_wiki_scraper.py',
            '-q'
        )
        LogFile = Join-Path $resolvedResultRoot '01-focused-pytest.txt'
    }
}

if (-not $SkipFixtureSmoke) {
    $selectedStages += [pscustomobject]@{
        Name = 'Deterministic fixture smoke'
        Arguments = New-SmokeArguments -ScriptPath 'tests/00-smoke-test.py'
        LogFile = Join-Path $resolvedResultRoot '02-fixture-smoke.txt'
    }
}

if (-not $SkipSequentialSmoke) {
    $selectedStages += [pscustomobject]@{
        Name = 'Sequential local smoke runner'
        Arguments = New-SmokeArguments -ScriptPath 'tests/openwrt-docs4ai-00-smoke-test.py'
        LogFile = Join-Path $resolvedResultRoot '03-sequential-smoke.txt'
    }
}

if ($selectedStages.Count -eq 0) {
    throw 'Nothing to do. Leave at least one validation stage enabled.'
}

$contextPath = Join-Path $resolvedResultRoot 'run-context.json'
$summaryPath = Join-Path $resolvedResultRoot 'summary.json'
$failureMessage = $null

Push-Location $repoRoot
try {
    [pscustomobject]@{
        generatedAt = (Get-Date).ToString('o')
        repoRoot = $repoRoot
        pythonExe = $pythonExe
        runAi = [bool]$RunAi
        keepTemp = [bool]$KeepTemp
        stages = $selectedStages.Name
    } | ConvertTo-Json -Depth 3 | Set-Content -Path $contextPath -Encoding utf8

    Write-Host 'openwrt-docs4ai local validation helper' -ForegroundColor Green
    Write-Host ("Repo root: {0}" -f $repoRoot)
    Write-Host ("Python:    {0}" -f $pythonExe)
    Write-Host ("Logs:      {0}" -f $resolvedResultRoot)
    Write-Host ("Run AI:    {0}" -f [bool]$RunAi)
    Write-Host ("Keep temp: {0}" -f [bool]$KeepTemp)
    Write-Host 'Remote GitHub Actions validation is intentionally out of scope for this helper.'

    $index = 1
    foreach ($stage in $selectedStages) {
        Invoke-ValidationStage -Index $index -Name $stage.Name -Arguments $stage.Arguments -LogFile $stage.LogFile
        $index += 1
    }
}
catch {
    $failureMessage = $_.Exception.Message
}
finally {
    if ($stageResults.Count -gt 0) {
        $stageResults | ConvertTo-Json -Depth 3 | Set-Content -Path $summaryPath -Encoding utf8

        Write-Host ''
        Write-Host 'Validation summary' -ForegroundColor Cyan
        $stageResults | Format-Table -AutoSize
        Write-Host ("Summary JSON: {0}" -f $summaryPath)
    }

    Pop-Location
}

if ($null -ne $failureMessage) {
    throw $failureMessage
}

Write-Host ''
Write-Host 'Local validation completed successfully.' -ForegroundColor Green
Write-Host 'If you need remote proof next, push the commit and follow the CI Operations procedure in DEVELOPMENT.md.'
