@echo off
REM ============================================================
REM  Social Agent - Scheduler (double-click karo dekhne ke liye)
REM
REM  Yeh window khuli rehti hai aur har 5 min Sheet check karti hai.
REM  BAND karne ke liye: yeh window band kar do (ya Ctrl+C).
REM
REM  NOTE: Login pe agent KHUD (chup-chaap) chalu ho jata hai -
REM  Startup folder me shortcut laga hai. Yeh bat sirf tab chalao
REM  jab tum agent ko AANKHON se chalte hue dekhna chaho.
REM ============================================================

cd /d "%~dp0"
echo Social Agent chal raha hai... (band karne ke liye yeh window band karo)
echo.
"C:\Users\Muhammad Ali\AppData\Local\Python\pythoncore-3.14-64\python.exe" src\scheduler.py
pause
