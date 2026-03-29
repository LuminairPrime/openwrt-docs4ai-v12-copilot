$urls = @{
    'AbsolutelySkilled.md' = 'https://raw.githubusercontent.com/AbsolutelySkilled/AbsolutelySkilled/refs/heads/main/README.md'
    'product-manager-skills.md' = 'https://raw.githubusercontent.com/Digidai/product-manager-skills/refs/heads/main/README.md'
    'claude-code-tresor.md' = 'https://raw.githubusercontent.com/alirezarezvani/claude-code-tresor/refs/heads/main/README.md'
    'claude-skills.md' = 'https://raw.githubusercontent.com/alirezarezvani/claude-skills/refs/heads/main/README.md'
    'awesome-agent-skills.md' = 'https://raw.githubusercontent.com/VoltAgent/awesome-agent-skills/refs/heads/main/README.md'
    'awesome-claude-skills.md' = 'https://raw.githubusercontent.com/travisvn/awesome-claude-skills/refs/heads/main/README.md'
}

New-Item -ItemType Directory -Force -Path 'tools\agents-skills' | Out-Null
Move-Item -Path 'tools\install-claude-skills.ps1' -Destination 'tools\agents-skills\install-claude-skills.ps1' -Force

foreach ($file in $urls.Keys) {
    Write-Host "Downloading $file"
    Invoke-WebRequest -Uri $urls[$file] -OutFile (Join-Path 'tools\agents-skills' $file)
}
