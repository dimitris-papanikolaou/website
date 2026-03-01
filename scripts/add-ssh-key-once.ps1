# Run this once in PowerShell (e.g. right-click -> Run with PowerShell, or in a terminal).
# When prompted "Enter passphrase for key...", press Enter (empty passphrase).
# Then you can use: ssh -T git@github.com  and push via SSH.

$keyPath = "$env:USERPROFILE\.ssh\id_ed25519"
if (-not (Test-Path $keyPath)) {
    Write-Host "Key not found: $keyPath" -ForegroundColor Red
    exit 1
}
Write-Host "Adding key. When asked for passphrase, press Enter (no passphrase)." -ForegroundColor Cyan
& ssh-add $keyPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "Key added. Testing GitHub..." -ForegroundColor Green
    ssh -T git@github.com
}
