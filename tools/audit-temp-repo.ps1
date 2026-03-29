$env:PYTHONIOENCODING="utf-8"
$auditor = "C:\Users\MC\Documents\AirSentinel\openwrt-docs4ai-pipeline\.claude\skills\skill-security-auditor\scripts\skill_security_auditor.py"
$targetDir = "C:\Users\MC\AppData\Local\Temp\absolutely-skilled\skills"
$outputFile = "C:\Users\MC\AppData\Local\Temp\audit_results.jsonl"

if (Test-Path $outputFile) { Remove-Item $outputFile }

Write-Host "Starting JSON audit of $targetDir..."
$dirs = Get-ChildItem -Directory $targetDir
$total = $dirs.Count
$idx = 0

foreach ($dir in $dirs) {
    if ($idx % 20 -eq 0) { Write-Host "[$idx/$total] Auditing..." }
    $idx++
    python $auditor $dir.FullName --json | Out-File -Append -FilePath $outputFile -Encoding utf8
}

Write-Host "Finished JSON batch audit."
