@echo off
"C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe" -u root -pMySQL2026! --default-character-set=utf8mb4 < "C:\Users\jesus\Desktop\monitor_asistencia_ia_INTEGRADO\database\setup_all.sql"
echo Exit code: %ERRORLEVEL%
