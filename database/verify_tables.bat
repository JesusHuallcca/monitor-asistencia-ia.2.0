@echo off
"C:\Program Files\MySQL\MySQL Server 9.7\bin\mysql.exe" -u root -pMySQL2026! -e "USE monitor_asistencia_ia; SHOW TABLES; SELECT COUNT(*) as total_usuarios FROM usuarios;"
echo Exit code: %ERRORLEVEL%
