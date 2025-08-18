# 🤖 CatchAI Copilot - Copiloto Conversacional sobre Documentos

Una aplicación de inteligencia artificial que permite a los usuarios subir documentos PDF y realizar consultas en lenguaje natural sobre su contenido.

## 🚀 Instrucciones para levantar el entorno

### Prerrequisitos
- Docker y Docker Compose instalados
- Clave API de Google Gemini

### Pasos de instalación

1. **Configurar variables de entorno**
\`\`\`bash
# Editar el archivo .env y agregar tu GOOGLE_API_KEY
GOOGLE_API_KEY=tu_clave_api_aqui
\`\`\`

2. **Levantar el entorno**
\`\`\`bash
docker-compose up
\`\`\`

3. **Acceder a la aplicación**
- URL: `http://localhost:8501`

## 🏗️ Arquitectura del sistema

### Patrón: Arquitectura por Capas (Layered Architecture)

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                     │
│                      (Streamlit UI)                         │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE LÓGICA DE NEGOCIO                │
│                 (Conversation Manager)                      │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE SERVICIOS                       │
│           (Document Processor + AI Services)               │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PERSISTENCIA                     │
│                      (ChromaDB)                             │
└─────────────────────────────────────────────────────────────┘
\`\`\`

## 🔧 Justificación de elecciones técnicas

**Streamlit**: Elegido para crear interfaces web rápidas con Python, ideal para prototipos de ML.

**Google Gemini API**: Seleccionado por su buen rendimiento en comprensión de texto en español y API estable.

**ChromaDB**: Implementado por su simplicidad para búsquedas vectoriales y fácil configuración.

**LangChain**: Utilizado para estructurar el flujo conversacional entre componentes de IA.

**Docker**: Garantiza consistencia entre entornos y simplifica el despliegue.

## 💬 Explicación del flujo conversacional

### Procesamiento de documentos:
1. Usuario sube archivos PDF
2. PyPDF extrae el texto
3. El texto se divide en fragmentos
4. Se generan embeddings con sentence-transformers
5. Los vectores se almacenan en ChromaDB

### Flujo de consulta:
1. Usuario hace una pregunta
2. Se vectoriza la consulta
3. ChromaDB busca fragmentos relevantes
4. Se construye un prompt con contexto
5. Gemini API genera la respuesta
6. Se muestra la respuesta al usuario

## 🚧 Limitaciones actuales y mejoras futuras

### Limitaciones actuales:
- Solo soporta archivos PDF
- Diseñado para un usuario por sesión
- No mantiene historial entre sesiones
- Limitado por la RAM disponible

### Mejoras futuras:
- **Corto plazo**: Soporte para DOCX y TXT, mejorar UI
- **Mediano plazo**: Múltiples usuarios, persistencia de sesiones
- **Largo plazo**: Procesamiento de imágenes, integración con cloud storage
