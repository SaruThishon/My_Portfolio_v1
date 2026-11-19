# Portfolio Database & Uploads Backup Script
# Usage: .\backup.ps1
# Creates timestamped backups in e:\MyPortfolio\backups\

$date = Get-Date -Format 'yyyy-MM-dd_HHmm'
$backupDir = "$PSScriptRoot\backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Host "Starting backup $date..." -ForegroundColor Cyan

# 1. SQL dump (plain text — readable, works with Supabase psql import)
$sqlFile = "$backupDir\portfolio_db_$date.sql"
docker exec -e PGPASSWORD=portfolio_pass portfolio_postgres `
    pg_dump -U portfolio_user portfolio_db | Out-File -Encoding UTF8 $sqlFile
Write-Host "SQL dump:    $sqlFile ($([math]::Round((Get-Item $sqlFile).Length/1KB, 1)) KB)" -ForegroundColor Green

# 2. Custom format dump (smaller, use pg_restore to restore)
docker exec -e PGPASSWORD=portfolio_pass portfolio_postgres `
    sh -c "PGPASSWORD=portfolio_pass pg_dump -U portfolio_user -Fc portfolio_db -f /tmp/pg_backup_$date.dump"
$dumpFile = "$backupDir\portfolio_db_$date.dump"
docker cp "portfolio_postgres:/tmp/pg_backup_$date.dump" $dumpFile
Write-Host "Custom dump: $dumpFile ($([math]::Round((Get-Item $dumpFile).Length/1KB, 1)) KB)" -ForegroundColor Green

# 3. Uploaded files zip
$zipFile = "$backupDir\uploads_$date.zip"
Compress-Archive -Path "$PSScriptRoot\backend\uploads" -DestinationPath $zipFile -Force
Write-Host "Uploads zip: $zipFile ($([math]::Round((Get-Item $zipFile).Length/1KB, 1)) KB)" -ForegroundColor Green

Write-Host ""
Write-Host "Backup complete! Files saved to: $backupDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To restore SQL dump to Supabase:" -ForegroundColor Yellow
Write-Host "  psql `"<supabase-connection-string>`" < $sqlFile"
Write-Host ""
Write-Host "To restore custom dump:" -ForegroundColor Yellow
Write-Host "  pg_restore -d `"<connection-string>`" $dumpFile"
