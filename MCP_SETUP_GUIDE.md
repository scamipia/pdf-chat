# Guía de Preparación para Filesystem MCP

## 📋 Pasos Previos (Sin modificar código aún)

### 1. Instalar dependencias de MCP

Necesitarás agregar estas dependencias a tu `requirements.txt`:

```txt
# MCP Client para Filesystem
mcp

# Para manejo asíncrono de archivos
aiofiles
```

**Comando para instalar:**
```bash
pip install mcp aiofiles
```

O usando `uv` (recomendado según la documentación oficial):
```bash
uv add mcp aiofiles
```

O si prefieres agregarlo al `requirements.txt` primero:
```bash
pip install -r requirements.txt
```

---

### 2. Configurar archivo de variables de entorno

Crea un archivo `.env` en la raíz del proyecto con:

```env
# Filesystem MCP Configuration
# Rutas permitidas separadas por comas (sin espacios después de las comas)
# Ejemplo para Windows:
FILESYSTEM_ALLOWED_PATHS=C:\Users\Camila\Documents,C:\Users\Camila\Desktop\pdf-chat\src\data

# Ruta raíz por defecto para operaciones de archivos
# Esta será la carpeta base desde donde se pueden acceder archivos
FILESYSTEM_ROOT_PATH=C:\Users\Camila\Documents

# Habilitar Filesystem MCP
MCP_FILESYSTEM_ENABLED=true
```

**⚠️ IMPORTANTE:**
- Ajusta las rutas según tus necesidades
- El archivo `.env` ya está en `.gitignore`, así que está seguro
- Para Windows, puedes usar rutas con barras invertidas (`\`) o barras normales (`/`) - Python las maneja ambas
- **NO** incluyas espacios después de las comas en `FILESYSTEM_ALLOWED_PATHS`

**Ejemplos de rutas permitidas:**
```env
# Opción 1: Rutas absolutas de Windows
FILESYSTEM_ALLOWED_PATHS=C:\Users\Camila\Documents,C:\Users\Camila\Desktop\MisPDFs

# Opción 2: Rutas con barras normales (también funciona en Windows)
FILESYSTEM_ALLOWED_PATHS=C:/Users/Camila/Documents,C:/Users/Camila/Desktop/MisPDFs

# Opción 3: Incluir la carpeta del proyecto
FILESYSTEM_ALLOWED_PATHS=C:\Users\Camila\Documents,C:\Users\Camila\Desktop\pdf-chat\src\data
```

---

### 3. Estructura de carpetas recomendada

Crea estas carpetas si no existen:

```
pdf-chat/
├── src/
│   ├── app_pdfchat.py
│   ├── data/
│   │   ├── uploads/
│   │   └── chroma_store/
│   └── mcp/              # Nueva carpeta para módulos MCP
│       ├── __init__.py
│       └── filesystem_mcp.py
├── .env                 # Variables de entorno (ya en .gitignore)
└── requirements.txt
```

**Comando para crear la carpeta:**
```bash
mkdir src\mcp
```

O desde PowerShell:
```powershell
New-Item -ItemType Directory -Path "src\mcp"
```

---

### 4. Permisos del sistema (Windows)

#### Verificar permisos:
- Asegúrate de tener permisos de **lectura** en las carpetas que quieras acceder
- Si usas rutas de red, verifica conectividad
- Para verificar permisos, intenta abrir la carpeta en el Explorador de Windows

#### Consideraciones de seguridad:
- **NO** configures rutas que incluyan carpetas del sistema críticas como:
  - `C:\Windows\`
  - `C:\Program Files\`
  - `C:\Program Files (x86)\`
  - `C:\System32\`
- Limita el acceso a carpetas específicas que necesites
- Considera usar rutas relativas cuando sea posible
- Si compartes el código, usa rutas relativas o variables de entorno

**Rutas recomendadas para incluir:**
- ✅ `C:\Users\TuUsuario\Documents`
- ✅ `C:\Users\TuUsuario\Desktop`
- ✅ `C:\Users\TuUsuario\Downloads`
- ✅ La carpeta del proyecto: `C:\Users\Camila\Desktop\pdf-chat\src\data`

**Rutas a evitar:**
- ❌ `C:\Windows\`
- ❌ `C:\Program Files\`
- ❌ `C:\` (raíz del sistema)

---

### 5. Verificar instalación

Antes de modificar el código, verifica que todo esté listo:

```bash
# Verificar que MCP está instalado
python -c "import mcp; print('MCP instalado correctamente')"

# Verificar aiofiles
python -c "import aiofiles; print('aiofiles instalado correctamente')"

# Verificar que el archivo .env existe y se puede leer
python -c "from decouple import config; print('Variables de entorno cargadas')"
```

Si alguno de estos comandos falla, instala las dependencias faltantes.

---

## 📝 Checklist de Preparación

Antes de empezar a modificar el código, asegúrate de tener:

- [ ] Dependencias instaladas (`mcp` y `aiofiles`)
- [ ] Archivo `.env` creado con las variables de configuración
- [ ] Rutas permitidas definidas en `FILESYSTEM_ALLOWED_PATHS`
- [ ] Ruta raíz configurada en `FILESYSTEM_ROOT_PATH`
- [ ] Permisos de lectura verificados en las carpetas configuradas
- [ ] Estructura de carpetas `src/mcp/` creada
- [ ] Verificación de instalación completada exitosamente

---

## 🔐 Seguridad

**Archivos que NO debes subir a Git:**
- `.env` (ya está protegido en `.gitignore` ✅)

**Consideraciones importantes:**
- El `.gitignore` ya protege el archivo `.env`
- No incluyas rutas sensibles en el código
- Usa variables de entorno para todas las configuraciones
- Si compartes el proyecto, documenta qué rutas necesita configurar cada usuario

---

## 📚 Recursos útiles

- [Documentación MCP](https://modelcontextprotocol.io/)
- [MCP Filesystem Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [Python aiofiles Documentation](https://github.com/Tinche/aiofiles)

---

## 🎯 Funcionalidades que tendrás con Filesystem MCP

Una vez implementado, podrás:

1. **Listar archivos** en carpetas específicas
2. **Leer archivos** de texto, PDFs, etc. desde rutas locales
3. **Buscar archivos** por nombre o patrón
4. **Obtener información** de archivos (tamaño, fecha de modificación, etc.)
5. **Cargar documentos** directamente desde tu sistema de archivos sin necesidad de subirlos manualmente

---

## ⏭️ Siguiente paso

Una vez completados estos pasos, podremos modificar el código para integrar el Filesystem MCP.

**Resumen rápido:**
1. ✅ Instalar `mcp` y `aiofiles`
2. ✅ Crear archivo `.env` con las rutas permitidas
3. ✅ Crear carpeta `src/mcp/`
4. ✅ Verificar permisos en las carpetas
5. ✅ Verificar instalación con los comandos de prueba
