# Carpeta de Respaldos de Base de Datos (MySQL)

En este directorio se almacenan los respaldos periódicos de la base de datos `monitor_asistencia_ia`.

### Generar respaldo:
```powershell
mysqldump -u root -p monitor_asistencia_ia > database/backup/backup_monitor_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

### Restaurar respaldo:
```powershell
mysql -u root -p monitor_asistencia_ia < database/backup/nombre_archivo.sql
```
