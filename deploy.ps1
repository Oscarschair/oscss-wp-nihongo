# deploy.ps1
# Automated deploy script for oscss-wp-nihongo to Lolipop via Python Paramiko

Write-Host "=== oscss-wp-nihongo Deployment to Lolipop ===" -ForegroundColor Cyan

python scripts/core/deploy_theme_and_purge.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n--------------------------------------------------" -ForegroundColor Green
    Write-Host " SUCCESS: Theme deployed and cache purged!" -ForegroundColor Green
    Write-Host "--------------------------------------------------" -ForegroundColor Green
} else {
    Write-Host "`n--------------------------------------------------" -ForegroundColor Red
    Write-Host " ERROR: Deployment failed." -ForegroundColor Red
    Write-Host "--------------------------------------------------" -ForegroundColor Red
}
