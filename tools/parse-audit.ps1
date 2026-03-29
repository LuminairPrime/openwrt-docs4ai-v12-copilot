$lines = Get-Content -Path "C:\Users\MC\AppData\Local\Temp\audit_results.jsonl" -Encoding utf8 | Where-Object { $_.Trim().StartsWith('{') }
$json = $lines | ConvertFrom-Json

Write-Host "Total Audits: $($json.Count)"
$json | Group-Object verdict | Select-Object Name, Count | Format-Table

$fails = $json | Where-Object verdict -eq "FAIL"
if ($fails) {
    Write-Host "`n--- FAILED SKILLS ---"
    foreach ($f in $fails) { Write-Host $f.skill_name }
}

$warns = $json | Where-Object verdict -eq "WARN"
if ($warns) {
    Write-Host "`n--- WARNED SKILLS ---"
    foreach ($w in $warns) { Write-Host $w.skill_name }
}
