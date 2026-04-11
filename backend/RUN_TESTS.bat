@echo off
echo.
echo ========================================
echo   VOICEFORWARD TEST MENU
echo ========================================
echo.
echo Choose a test:
echo.
echo 1. Live Transcription (speak into mic)
echo 2. Speed Test (no mic needed)
echo 3. Basic API Test
echo 4. Microphone Test
echo 5. AI Analyzer Test (mock data)
echo 6. Full Pipeline Test (mic + AI)
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting live transcription test...
    python test_live_transcription.py
) else if "%choice%"=="2" (
    echo.
    echo Starting speed test...
    python test_sarvam_speed.py
) else if "%choice%"=="3" (
    echo.
    echo Starting basic API test...
    python test_sarvam.py
) else if "%choice%"=="4" (
    echo.
    echo Starting microphone test...
    python test_mic.py
) else if "%choice%"=="5" (
    echo.
    echo Starting AI analyzer test...
    python test_analyzer.py
) else if "%choice%"=="6" (
    echo.
    echo Starting full pipeline test...
    python test_full_pipeline.py
) else (
    echo Invalid choice!
)

echo.
pause
