@echo off
echo.
echo [INFO] Activating virtual environment...
call myenv\Scripts\activate.bat

echo.
echo [INFO] Running the main program...
python app\main.py

echo.
echo [INFO] Program exited. Press any key to close.
pause