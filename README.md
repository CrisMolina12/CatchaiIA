# CatchAI Copilot - Copiloto Conversacional sobre Documentos

Una aplicación de inteligencia artificial que permite a los usuarios subir documentos PDF y realizar consultas en lenguaje natural sobre su contenido.

## Instrucciones para levantar el entorno

1. **Editar el archivo .env y agregar tu GOOGLE_API_KEY**
\`\`\`
GOOGLE_API_KEY=tu_clave_api_aqui
\`\`\`

2. **Levantar el entorno**
\`\`\`bash
docker-compose up
\`\`\`

3. **Acceder a la aplicación**
- URL: http://localhost:8501

## Arquitectura del sistema

El sistema utiliza una **Arquitectura por Capas** que separa las responsabilidades en cuatro niveles:

**Capa de Presentación**: Streamlit maneja la interfaz web donde los usuarios suben PDFs y hacen preguntas. Incluye formularios de carga y visualización de respuestas.

**Capa de Lógica de Negocio**: El Conversation Manager coordina todo el flujo entre componentes, gestiona las sesiones de usuario y mantiene el contexto de las conversaciones.

**Capa de Servicios**: Tres servicios principales trabajan aquí - Document Processor extrae texto de PDFs con PyPDF, los embeddings se generan con sentence-transformers, y Gemini API procesa las consultas para generar respuestas inteligentes.

**Capa de Persistencia**: ChromaDB almacena los vectores de los documentos procesados, permitiendo búsquedas semánticas rápidas cuando el usuario hace preguntas.

## Justificación de elecciones técnicas

**Streamlit**: Elegido para crear interfaces web rápidas con Python, ideal para prototipos de ML.

**Google Gemini API**: Seleccionado por su buen rendimiento en comprensión de texto en español y API estable.

**ChromaDB**: Implementado por su simplicidad para búsquedas vectoriales y fácil configuración.

**LangChain**: Utilizado para estructurar el flujo conversacional entre componentes de IA.

**Docker**: Garantiza consistencia entre entornos y simplifica el despliegue.

## Explicación del flujo conversacional

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

## Limitaciones actuales y mejoras futuras

### Limitaciones actuales:
- Solo soporta archivos PDF
- No mantiene historial entre sesiones

### Mejoras futuras:
- Soporte para DOCX y TXT, mejorar UI
