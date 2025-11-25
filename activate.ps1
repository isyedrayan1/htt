# Activation script for Antigravity project
# Run this with: .\activate.ps1

Write-Host "🚀 Activating Antigravity Driver Intelligence Platform..." -ForegroundColor Cyan

# Activate virtual environment
.\venv\Scripts\Activate.ps1

Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  2. Test file discovery: python src/ingestion/file_detector.py" -ForegroundColor White
Write-Host "  3. Run ingestion: python src/ingest_cota.py" -ForegroundColor White
Write-Host ""
