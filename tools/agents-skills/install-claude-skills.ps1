<#
.SYNOPSIS
    Install curated agent skills from multiple community repos into three tool destinations.

.DESCRIPTION
    References and Inspiration:
      - https://www.reddit.com/r/ClaudeAI/comments/1rwzbcv/i_applied_my_skillwriting_principles_to_159/
      - https://github.com/AbsolutelySkilled/AbsolutelySkilled
      - https://raw.githubusercontent.com/AbsolutelySkilled/AbsolutelySkilled/refs/heads/main/README.md
      - https://raw.githubusercontent.com/Digidai/product-manager-skills/refs/heads/main/README.md
      - https://raw.githubusercontent.com/alirezarezvani/claude-code-tresor/refs/heads/main/README.md
      - https://raw.githubusercontent.com/alirezarezvani/claude-skills/refs/heads/main/README.md
      - https://raw.githubusercontent.com/VoltAgent/awesome-agent-skills/refs/heads/main/README.md
      - https://raw.githubusercontent.com/travisvn/awesome-claude-skills/refs/heads/main/README.md

    Clones/downloads skills from:
      - alirezarezvani/claude-skills       (https://github.com/alirezarezvani/claude-skills)
      - alirezarezvani/claude-code-tresor  (https://github.com/alirezarezvani/claude-code-tresor)
      - anthropics/skills                  (https://github.com/anthropics/skills)
      - obra/superpowers                   (https://github.com/obra/superpowers)
      - trailofbits/skills                 (https://github.com/trailofbits/skills)
      - openai/skills                      (https://github.com/openai/skills)
      - garrytan/gstack                    (https://github.com/garrytan/gstack)
      - massimodeluisa/recursive-decomp    (https://github.com/massimodeluisa/recursive-decomposition-skill)
      - AbsolutelySkilled/AbsolutelySkilled (Flagship: Second Brain, Super-Human, Brainstorm)
      - getsentry/skills                   (https://github.com/getsentry/skills)

    Installs into three destinations per skill:
      1. $HOME\.gemini\antigravity\skills\   - Antigravity (global)
      2. <project>\.claude\skills\           - Claude Code (project-level)
      3. <project>\.github\instructions\     - VS Code GitHub Copilot (path-scoped .instructions.md)

    Skill selection rationale (openwrt-docs4ai-pipeline):
      This is a Python documentation production pipeline with numbered stages, pytest/Ruff/Pyright
      quality gates, GitHub Actions CI, and a rich CLAUDE.md. Skills were chosen based on direct
      applicability to Python pipelines, CI/CD, debugging, and large-scale document refactoring.

    Idempotent: skips existing destinations unless -Force is passed.

.PARAMETER Force
    Overwrite existing skill directories in all destinations without prompting.

.PARAMETER SkipClone
    Reuse existing temp clones under $env:TEMP (useful for repeated testing).

.PARAMETER ProjectRoot
    Path to the project root (contains .claude\, .github\).
    Defaults to the parent of the tools\ directory (the repo root).

.EXAMPLE
    .\tools\install-claude-skills.ps1
    .\tools\install-claude-skills.ps1 -Force
    .\tools\install-claude-skills.ps1 -SkipClone -Force
#>
param(
    [switch]$Force,
    [switch]$SkipClone,
    [string]$ProjectRoot = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# =============================================================================
# SKILL MANIFEST
# =============================================================================

$SKILL_SOURCES = @(
    # -------------------------------------------------------------------------
    # 1. Alireza Rezvani Repos (Architecture, CI, Operations)
    # -------------------------------------------------------------------------
    @{
        Name     = "alirezarezvani/claude-skills"
        RepoUrl  = "https://github.com/alirezarezvani/claude-skills.git"
        TempDir  = "claude-skills"
        Skills   = @(
            @{ Path = "engineering-team/self-improving-agent"; Why = "Promotes CLAUDE.md patterns; closes memory→rules loop" },
            @{ Path = "engineering/ci-cd-pipeline-builder";    Why = "Audits/generates GitHub Actions configs" },
            @{ Path = "engineering/runbook-generator";         Why = "Formalises per-stage runbooks" },
            @{ Path = "engineering/codebase-onboarding";       Why = "Audience-aware onboarding" },
            @{ Path = "engineering/tech-debt-tracker";         Why = "Structured debt scanner" },
            @{ Path = "engineering/dependency-auditor";        Why = "Audits requirements.txt risk" },
            @{ Path = "engineering/pr-review-expert";          Why = "Blast-radius analysis on PRs into main" },
            @{ Path = "engineering/env-secrets-manager";       Why = "Leak detection across environments" },
            @{ Path = "engineering/changelog-generator";       Why = "Conventional commits → changelogs" },
            @{ Path = "engineering/skill-security-auditor";    Why = "Security gate: run on any new skill" }
        )
    },
    @{
        Name     = "alirezarezvani/claude-code-tresor"
        RepoUrl  = "https://github.com/alirezarezvani/claude-code-tresor.git"
        TempDir  = "claude-code-tresor"
        Skills   = @(
            @{ Path = "skills/development/code-reviewer";    Why = "Real-time code quality on file edits" },
            @{ Path = "skills/development/git-commit-helper"; Why = "Generates conventional commits from diff" },
            @{ Path = "skills/security/secret-scanner";      Why = "Blocks commits with exposed API keys" },
            @{ Path = "skills/documentation/readme-updater"; Why = "Keeps main docs current after refactors" }
        )
    },
    
    # -------------------------------------------------------------------------
    # 2. Trail of Bits & Sentry (Security, Modern Python, Bug Finding)
    # -------------------------------------------------------------------------
    @{
        Name     = "trailofbits/skills"
        RepoUrl  = "https://github.com/trailofbits/skills.git"
        TempDir  = "tob-skills"
        Skills   = @(
            @{ Path = "plugins/modern-python";       Why = "Modern Python tooling with ruff, pytest, and type hints" },
            @{ Path = "plugins/differential-review"; Why = "Security-focused diff review with git history analysis" },
            @{ Path = "plugins/static-analysis";     Why = "Static analysis execution patterns" }
        )
    },
    @{
        Name     = "getsentry/skills"
        RepoUrl  = "https://github.com/getsentry/skills.git"
        TempDir  = "sentry-skills"
        Skills   = @(
            @{ Path = "plugins/sentry-skills/skills/find-bugs"; Why = "Sentry's internal bug identification workflow" },
            @{ Path = "plugins/sentry-skills/skills/code-review"; Why = "Sentry's internal code review methodology" }
        )
    },

    # -------------------------------------------------------------------------
    # 3. OpenAI & GitHub CI Workflows
    # -------------------------------------------------------------------------
    @{
        Name     = "openai/skills"
        RepoUrl  = "https://github.com/openai/skills.git"
        TempDir  = "openai-skills"
        Skills   = @(
            @{ Path = "skills/.curated/gh-fix-ci";           Why = "Debug and fix failing GitHub Actions checks via CLI" },
            @{ Path = "skills/.curated/gh-address-comments"; Why = "Systematically address PR feedback" },
            @{ Path = "skills/.curated/yeet";                Why = "Stage, commit, and open PRs smoothly" }
        )
    },

    # -------------------------------------------------------------------------
    # 4. Advanced Workflows (TDD, Root Cause, Large Refactors)
    # -------------------------------------------------------------------------
    @{
        Name     = "garrytan/gstack"
        RepoUrl  = "https://github.com/garrytan/gstack.git"
        TempDir  = "gstack-skills"
        Skills   = @(
            @{ Path = "investigate"; Why = "Systematic root-cause debugging methodology" },
            @{ Path = "qa";          Why = "Test app, find bugs, generate regression tests" },
            @{ Path = "plan-eng-review"; Why = "Engineering Manager review: architecture, data flow, test edge cases" }
        )
    },
    @{
        Name     = "massimodeluisa/recursive-decomposition-skill"
        RepoUrl  = "https://github.com/massimodeluisa/recursive-decomposition-skill.git"
        TempDir  = "recursive-decomp-skill"
        Skills   = @(
            @{ Path = ""; DestName = "recursive-decomposition"; Why = "Handle long-context tasks (100+ files) and complex refactoring" }
        )
    },
    @{
        Name     = "obra/superpowers"
        RepoUrl  = "https://github.com/obra/superpowers.git"
        TempDir  = "superpowers"
        Skills   = @(
            @{ Path = "skills/tdd";       Why = "TDD workflow; strengthens pytest discipline" },
            @{ Path = "skills/debugging"; Why = "Systematic debugging patterns" }
        )
    },

    # -------------------------------------------------------------------------
    # 5. Planning, Architecture & Domain Driven Design
    # -------------------------------------------------------------------------
    @{
        Name     = "mattpocock/skills"
        RepoUrl  = "https://github.com/mattpocock/skills.git"
        TempDir  = "mattpocock-skills"
        Skills   = @(
            @{ Path = "skills/prd";              Why = "Write Product Requirements Documents covering edge cases" },
            @{ Path = "skills/architecture";     Why = "Document and plan codebase architecture" },
            @{ Path = "skills/refactoring-plan"; Why = "Plan structural refactoring smoothly" }
        )
    },
    @{
        Name     = "NeoLabHQ/context-engineering-kit"
        RepoUrl  = "https://github.com/NeoLabHQ/context-engineering-kit.git"
        TempDir  = "neolabhq-skills"
        Skills   = @(
            @{ Path = "plugins/sdd";          Why = "Spec-driven development workflow" },
            @{ Path = "plugins/ddd";          Why = "Domain-driven design, Clean Architecture, SOLID principles" },
            @{ Path = "plugins/code-review";  Why = "PR reviews with bug-hunter, security, and coverage angles" }
        )
    },

    # -------------------------------------------------------------------------
    # 6. Core Anthropic Skills
    # -------------------------------------------------------------------------
    @{
        Name     = "anthropics/skills"
        RepoUrl  = "https://github.com/anthropics/skills.git"
        TempDir  = "anthropics-skills"
        Skills   = @(
            @{ Path = "skills/skill-creator"; Why = "Interactive skill builder for creating project-specific skills" }
        )
    },

    # -------------------------------------------------------------------------
    # 7. AbsolutelySkilled (OpenWrt & Pipeline Essentials)
    # -------------------------------------------------------------------------
    @{
        Name     = "AbsolutelySkilled/AbsolutelySkilled"
        RepoUrl  = "https://github.com/AbsolutelySkilled/AbsolutelySkilled.git"
        TempDir  = "absolutely-skilled"
        Skills   = @(
            @{ Path = "skills/shell-scripting";   Why = "Strict POSIX/bash scripting patterns essential for OpenWrt init scripts" },
            @{ Path = "skills/technical-writing"; Why = "Advanced documentation structuring for the OpenWrt Docs AI pipeline" },
            @{ Path = "skills/system-design";     Why = "High-level architectural planning for ubus, LuCI, and embedded C system components" },
            @{ Path = "skills/api-design";        Why = "Designing robust boundaries and APIs for LuCI frontend integration" },
            @{ Path = "skills/clean-code";        Why = "Enforcing readable, maintainable code for C and JavaScript lifecycles" },
            @{ Path = "skills/super-human";       Why = "Autonomous SDLC: Decomposes features into DAG tasks, executes parallel waves, TDD verify, persistent board" },
            @{ Path = "skills/super-brainstorm";  Why = "Relentless Interview: Reads codebase to challenge assumptions; 1-question-at-a-time design spec" },
            @{ Path = "skills/second-brain";      Why = "Persistent Memory: Hierarchical ~/.memory/ store with tag-indexed retrieval and wiki-link traversal" },
            @{ Path = "skills/codedocs";          Why = "Agent-Friendly Docs: Generates OVERVIEW.md, Module/Pattern docs, and INDEX.md with coverage census" }
        )
    }
)

# =============================================================================
# DESTINATIONS
# =============================================================================

$DEST_ANTIGRAVITY  = Join-Path $HOME ".gemini\antigravity\skills"
$DEST_CLAUDE_CODE  = Join-Path $ProjectRoot ".claude\skills"
$DEST_COPILOT_DIR  = Join-Path $ProjectRoot ".github\instructions"

# =============================================================================
# HELPERS
# =============================================================================

function Write-Ok   { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green  }
function Write-Warn { param($msg) Write-Host "  [!!] $msg" -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host " [ERR] $msg" -ForegroundColor Red    }
function Write-Hdr  { param($msg) Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Sub  { param($msg) Write-Host "  --- $msg" -ForegroundColor DarkCyan }

function Ensure-Clone {
    param([string]$RepoUrl, [string]$TempDirName)
    $cloneDir = Join-Path $env:TEMP $TempDirName
    if ($SkipClone -and (Test-Path $cloneDir)) {
        Write-Warn "Reusing existing clone: $cloneDir"
        return $cloneDir
    }
    if (Test-Path $cloneDir) {
        Remove-Item -Recurse -Force $cloneDir
    }
    Write-Host "  Cloning $RepoUrl ..." -ForegroundColor DarkGray
    git clone --depth 1 --quiet $RepoUrl $cloneDir
    Write-Ok "Cloned -> $cloneDir"
    return $cloneDir
}

function Copy-Skill {
    param([string]$Src, [string]$Dst, [string]$SkillName)
    if (-not (Test-Path $Src)) {
        Write-Err "Source missing: $Src"
        return "failed"
    }
    if (Test-Path $Dst) {
        if ($Force) {
            Remove-Item -Recurse -Force $Dst
            Write-Warn "Overwriting: $SkillName"
        } else {
            Write-Warn "Already exists (skip): $SkillName"
            return "skipped"
        }
    }
    Copy-Item -Recurse $Src $Dst
    return "installed"
}

function Write-CopilotInstruction {
    param([string]$SkillDir, [string]$SkillName, [string]$DestDir, [string]$Why)

    $skillMd = Join-Path $SkillDir "SKILL.md"
    if (-not (Test-Path $skillMd)) {
        # Check if they named it README.md instead
        $skillMd = Join-Path $SkillDir "README.md"
        if (-not (Test-Path $skillMd)) {
            Write-Warn "No SKILL.md/README.md in $SkillDir - skipping Copilot instruction"
            return "skipped"
        }
    }

    $outFile = Join-Path $DestDir "$SkillName.instructions.md"
    if ((Test-Path $outFile) -and -not $Force) {
        Write-Warn "Already exists (skip): $SkillName.instructions.md"
        return "skipped"
    }

    $content = Get-Content $skillMd -Raw
    $body = $content -replace "(?s)^---.*?---\s*", ""

    $headerLines = @(
        "---",
        "applyTo: `"**`"",
        "---",
        "",
        "<!-- Source: $SkillName skill - auto-generated by install-claude-skills.ps1 -->",
        "<!-- Purpose: $Why -->",
        ""
    )
    
    Set-Content -Path $outFile -Value $headerLines -Encoding utf8 -Force
    Add-Content -Path $outFile -Value $body -Encoding utf8
    return "installed"
}

# =============================================================================
# MAIN
# =============================================================================

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "|          install-claude-skills.ps1                         |" -ForegroundColor Cyan
Write-Host "|  Destinations:                                             |" -ForegroundColor Cyan
Write-Host "|    1. Antigravity (global)                                 |" -ForegroundColor Cyan
Write-Host "|    2. Claude Code  (.claude\skills\)                       |" -ForegroundColor Cyan
Write-Host "|    3. VS Code Copilot (.github\instructions\)              |" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Where would you like to install the skills?" -ForegroundColor Yellow
$choice = Read-Host "Enter 1, 2, 3, or 'all' (default: all)"
if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "all" }

$installAntigravity = ($choice -match "1|all")
$installClaudeCode  = ($choice -match "2|all")
$installCopilot     = ($choice -match "3|all")

if (-not ($installAntigravity -or $installClaudeCode -or $installCopilot)) {
    Write-Warn "Invalid choice. Defaulting to all."
    $installAntigravity = $true; $installClaudeCode = $true; $installCopilot = $true
}

$activeDestinations = @()
if ($installAntigravity) { $activeDestinations += $DEST_ANTIGRAVITY }
if ($installClaudeCode)  { $activeDestinations += $DEST_CLAUDE_CODE }
if ($installCopilot)     { $activeDestinations += $DEST_COPILOT_DIR }

foreach ($d in $activeDestinations) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
        Write-Ok "Created: $d"
    }
}

$totals = @{
    antigravity = @{ installed=0; skipped=0; failed=0 }
    claude      = @{ installed=0; skipped=0; failed=0 }
    copilot     = @{ installed=0; skipped=0; failed=0 }
}

foreach ($source in $SKILL_SOURCES) {
    Write-Hdr "Repo: $($source.Name)"

    $cloneDir = Ensure-Clone -RepoUrl $source.RepoUrl -TempDirName $source.TempDir

    foreach ($skill in $source.Skills) {
        $skillPath = $skill.Path
        $skillName = if ($skill.Contains("DestName")) { $skill.DestName } else { Split-Path $skillPath -Leaf }
        $skillWhy  = $skill.Why
        
        # If Path is empty, we copy the root of the clone
        $skillSrc  = if ($skillPath -eq "") { $cloneDir } else { Join-Path $cloneDir $skillPath }

        Write-Sub "Skill: $skillName"

        # Special exclusions (e.g. drop .git if copying from repo root)
        if ($skillPath -eq "") {
            $gitDir = Join-Path $skillSrc ".git"
            if (Test-Path $gitDir) { Remove-Item -Recurse -Force $gitDir | Out-Null }
        }

        # 1. Antigravity
        if ($installAntigravity) {
            $dst = Join-Path $DEST_ANTIGRAVITY $skillName
            $r   = Copy-Skill -Src $skillSrc -Dst $dst -SkillName $skillName
            $totals.antigravity[$r]++
            if ($r -eq "installed") { Write-Ok "  -> Antigravity: $skillName" }
        }

        # 2. Claude Code
        if ($installClaudeCode) {
            $dst = Join-Path $DEST_CLAUDE_CODE $skillName
            $r   = Copy-Skill -Src $skillSrc -Dst $dst -SkillName $skillName
            $totals.claude[$r]++
            if ($r -eq "installed") { Write-Ok "  -> .claude/skills: $skillName" }
        }

        # 3. VS Code Copilot
        if ($installCopilot) {
            $r = Write-CopilotInstruction -SkillDir $skillSrc -SkillName $skillName `
                                          -DestDir $DEST_COPILOT_DIR -Why $skillWhy
            $totals.copilot[$r]++
            if ($r -eq "installed") { Write-Ok "  -> .github/instructions: $skillName.instructions.md" }
        }
    }
}

if (-not $SkipClone) {
    Write-Hdr "Cleanup"
    foreach ($source in $SKILL_SOURCES) {
        $cloneDir = Join-Path $env:TEMP $source.TempDir
        if (Test-Path $cloneDir) {
            Remove-Item -Recurse -Force $cloneDir
            Write-Ok "Removed: $($source.TempDir)"
        }
    }
}

Write-Hdr "Summary"
Write-Host ""

$rows = @(
    [PSCustomObject]@{ Destination="Antigravity (global)";               Path=$DEST_ANTIGRAVITY; Installed=$totals.antigravity["installed"]; Skipped=$totals.antigravity["skipped"]; Failed=$totals.antigravity["failed"] },
    [PSCustomObject]@{ Destination="Claude Code (.claude\skills)";        Path=$DEST_CLAUDE_CODE; Installed=$totals.claude["installed"];      Skipped=$totals.claude["skipped"];      Failed=$totals.claude["failed"] },
    [PSCustomObject]@{ Destination="VS Code Copilot (.github\instructions)"; Path=$DEST_COPILOT_DIR; Installed=$totals.copilot["installed"];  Skipped=$totals.copilot["skipped"];     Failed=$totals.copilot["failed"] }
)

foreach ($row in $rows) {
    $color = if ($row.Failed -gt 0) { "Red" } elseif ($row.Installed -gt 0) { "Green" } else { "Yellow" }
    Write-Host "  [$($row.Destination)]" -ForegroundColor $color
    Write-Host "    Path      : $($row.Path)"
    Write-Host "    Installed : $($row.Installed)"
    Write-Host "    Skipped   : $($row.Skipped)  (already present - use -Force to overwrite)"
    Write-Host "    Failed    : $($row.Failed)"
    Write-Host ""
}
