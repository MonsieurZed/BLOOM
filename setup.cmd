@echo off
REM Get the current location
set "CURRENT_DIR=%cd%"

REM Check and extract ffmpeg.7z.001 and ffmpeg.7z.002 if ffmpeg folder does not exist
if not exist "%CURRENT_DIR%\binary\ffmpeg" (
    echo Extracting ffmpeg.7z.001 and ffmpeg.7z.002...
    copy /b "%CURRENT_DIR%\binary\ffmpeg.7z.001" + "%CURRENT_DIR%\binary\ffmpeg.7z.002" "%CURRENT_DIR%\binary\ffmpeg_combined.7z"
    tar -xf "%CURRENT_DIR%\binary\ffmpeg_combined.7z" -C "%CURRENT_DIR%\binary"
    del "%CURRENT_DIR%\binary\ffmpeg_combined.7z"
)

REM Check and extract ImageMagick.7z if ImageMagick folder does not exist
if not exist "%CURRENT_DIR%\binary\ImageMagick" (
    echo Extracting ImageMagick.7z...
    tar -xf "%CURRENT_DIR%\binary\ImageMagick.7z" -C "%CURRENT_DIR%\binary"
)

REM Locate the moviepy config_defaults.py file
set "MOVIEPY_CONFIG=%CURRENT_DIR%\.venv\Lib\site-packages\moviepy\config_defaults.py"

REM Backup the config_defaults.py file
if exist "%MOVIEPY_CONFIG%" (
    echo Backing up config_defaults.py...
    copy "%MOVIEPY_CONFIG%" "%CURRENT_DIR%\.venv\Lib\site-packages\moviepy\config_defaults_save.py"
) else (
    echo config_defaults.py not found. Exiting...
    pause
    exit /b 1
)

REM Edit the config_defaults.py file
echo Editing config_defaults.py...
(for /f "delims=" %%i in ('type "%MOVIEPY_CONFIG%"') do (
    echo %%i | findstr /c:"FFMPEG_BINARY = os.getenv('FFMPEG_BINARY', 'ffmpeg-imageio')" >nul && (
        echo FFMPEG_BINARY = r"%CURRENT_DIR%\binary\ffmpeg\bin\ffmpeg.exe"
    ) || echo %%i | findstr /c:"IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', 'auto-detect')" >nul && (
        echo IMAGEMAGICK_BINARY = r"%CURRENT_DIR%\binary\ImageMagick\magick.exe"
    ) || (
        echo %%i
    )
)) > "%MOVIEPY_CONFIG%.tmp"

move /y "%MOVIEPY_CONFIG%.tmp" "%MOVIEPY_CONFIG%"

REM Pause for user input
pause

REM Activate the virtual environment
call "%CURRENT_DIR%\.venv\scripts\activate"

REM Install pip requirements
pip install -r "%CURRENT_DIR%\requirements.txt"
