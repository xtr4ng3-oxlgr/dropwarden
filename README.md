# DROPWARDEN

**DROPWARDEN** es una consola defensiva para revisar archivos descargados, instaladores, scripts, ZIPs, entradas de inicio y salud básica de instalación antes de ejecutar o instalar cosas en Windows.

Creado por **xtr4ng3**.

```text
Before you run it, make it answer.
```

---

## Propósito

DROPWARDEN responde una pregunta simple:

```text
¿Esto que descargué o tengo en mi PC conviene ejecutarlo, instalarlo o revisarlo primero?
```

No es antivirus.  
No elimina archivos.  
No ejecuta muestras.  
No sube datos a internet.  
No promete detectar malware.

Es una herramienta local de decisión pre-ejecución.

---

## Funciones

- Consola brutal con menú.
- Análisis de archivo individual.
- Análisis de carpeta Descargas.
- Auditor de PC / Install Advisor.
- Revisión de archivos recientes en Descargas.
- Hash SHA256 y MD5.
- Entropía.
- Doble extensión sospechosa.
- Nombre sospechoso.
- Zone.Identifier de Windows.
- Firma digital Authenticode.
- Análisis básico PE con `pefile`.
- Inspección ZIP.
- Revisión de scripts `.bat`, `.cmd`, `.ps1`, `.vbs`, `.js`, `.sh`.
- Inventario de programas instalados.
- Auditoría de elementos de inicio.
- Reportes HTML / JSON / TXT.
- PowerShell para metadatos de Windows.
- Helper C opcional para entropía.

---

## Instalación

Ejecutar una vez:

```bat
INSTALAR_DEPENDENCIAS.bat
```

Dependencias:

```text
rich
pefile
psutil
```

---

## Uso

Abrir menú:

```bat
ABRIR_DROPWARDEN.bat
```

CLI directa:

```bash
python dropwarden.py analyze "C:\Users\User\Downloads\setup.exe"
python dropwarden.py downloads --deep
python dropwarden.py system --deep-downloads
```

---

## Veredictos

```text
0-25    BAJO
26-50   MODERADO
51-75   REVISAR
76-100  ALTO RIESGO
```

Los veredictos son señales para revisión manual, no sentencia absoluta.

---

## Para PCs de recursos medios

DROPWARDEN está pensado para funcionar bien en equipos modestos:

- consola pura,
- sin GUI pesada,
- sin base de datos,
- sin escaneos eternos,
- dependencias mínimas,
- análisis de Descargas limitado,
- reportes locales.

---

## Seguridad

DROPWARDEN no hace acciones destructivas.

No ejecuta archivos analizados.  
No borra archivos.  
No desinfecta.  
No modifica el sistema.  
No transmite datos.

---

## Licencia

MIT.

**xtr4ng3**
