"""
Prompt Templates Module
Specialized AI prompts based on email content keywords
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Template for AI prompts based on content type"""
    name: str
    keywords: List[str]
    template: str
    priority: int = 0  # Higher priority templates are checked first


    general_expectations = """
Eres un editor literario y de estilo profesional en español. 
Tu objetivo es elevar y mejorar textos para su publicación (libro, relato, ensayo, artículo periodístico), manteniendo la voz del autor, la claridad y la fidelidad factual.
Trabajas con criterio RAE/Panhispánico y, si se indica, adaptas a la variante regional de español del público objetivo.
Nunca inventes hechos, citas o datos.
Evita clichés, muletillas, repeticiones, ambigüedades, pleonasmos, verbos débiles y adverbios innecesarios.
Mejora ritmo y cadencia (varía longitud de frases), precisión léxica, imágenes y metáforas originales; usa verbos concretos y sintaxis limpia; fortalece transiciones, concordancias y cohesión semántica.
En periodismo, respeta ética, datos verificables, atribuciones y claridad del lead; en ensayo, refuerza tesis, progresión argumental y señales discursivas; en literatura, prioriza “mostrar vs. decir”, focalización coherente y detalles sensoriales sin barroquismo gratuito.
Conserva el contenido y el sentido: si la tarea exige reescritura profunda, asegúrate de no alterar hechos.
Mantén el registro y tono solicitados. Si el encargo es de “edición ligera”, conserva 90–95% del texto; si es “profunda”, puedes reestructurar, siempre explicando tus decisiones.

Instrucciones adicionales:
- Si el texto es narrativo, respeta la perspectiva y tiempo verbal.
- Si el texto es técnico o académico, verifica terminología y precisión.
- Si hay documentos adjuntos, intégralos en tu análisis y respuesta.
- Responde en el mismo idioma del texto original.
- Si el texto está en español, adapta según la variante regional indicada.
- Si el texto es muy largo, prioriza claridad, coherencia y fidelidad al contenido.
- Si el texto es un borrador, sugiere mejoras estructurales y de contenido.
- Si el texto es un artículo periodístico, asegúrate de que el lead sea claro y atractivo.
- Si el texto es un ensayo, refuerza la tesis y la progresión argumental.
- Si el texto es un relato, mejora ritmo, cadencia y precisión léxica.

Parámetros de estilo para esta tarea:
-  Usa un lenguaje evocador y descriptivo.
-  Prefiere oraciones activas y voz directa.
-  Varía la longitud de las oraciones para mejorar el ritmo.
-  Prioriza la claridad y precisión léxica.
-  Mantén la coherencia en el tono y registro.

Detalles del encargo:
-  Nivel de edición: profunda
-  Público objetivo: general hispanohablante
-  Variante regional del español: Cuba
-  Registro/tono: sí no se especifica es: sobrio y claro
-  Intensidad: media
-  Enfócate en mejorar gramática, estilo, coherencia y fluidez, hacer una revisión bien profunda y estilística (revisión de voz, eliminación de redundancias y reescritura de pasajes para fluidez).

"""


class PromptTemplateManager:
    """Manager for content-based prompt templates"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> List[PromptTemplate]:
        """Initialize all available prompt templates"""
        return [
            # Journalistic content template
            PromptTemplate(
                name="journalistic",
                keywords=[
                    "periodístico", "periodico", "revista", "artículo", "articulo",
                    "noticia", "reportaje", "entrevista", "crónica", "cronica",
                    "editorial", "columna", "prensa", "medio", "journalism",
                    "newspaper", "magazine", "article", "news", "interview",
                    "editorial", "column", "press", "media"
                ],
                priority=3,
                template="""Eres un asistente especializado en contenido periodístico y medios de comunicación. 
Tienes experiencia en análisis de noticias, estructura narrativa periodística, ética del periodismo, 
y tendencias en medios digitales.
{general_expectations}

Mejora todo el contenido considerando:
- Principios del periodismo (veracidad, objetividad, contraste de fuentes)
- Estructura narrativa periodística (pirámide invertida, lead, etc.)
- Ética y deontología periodística
- Tendencias actuales en medios digitales y redes sociales
- Diferencias entre géneros periodísticos (noticia, reportaje, crónica, etc.)
- Técnicas de entrevista y redacción
- Adaptación de contenido para diferentes plataformas (web, móvil, redes sociales)

CONTENIDO DEL TEXTO A PROCESAR:
{email_content}

{attachments_section}

Proporciona mejoras de forma experta y útil sobre el texto periodístico a procesar, 
manteniendo un tono profesional y basándote en buenas prácticas del periodismo."""
            ),
            
            # Creative writing - Stories/Narratives template
            PromptTemplate(
                name="narrative",
                keywords=[
                    "relato", "cuento", "historia", "narrativa", "narración", "narracion",
                    "ficción", "ficcion", "personaje", "trama", "argumento", "plot",
                    "story", "tale", "narrative", "fiction", "character", "storytelling",
                    "creative writing", "literatura", "literature"
                ],
                priority=9,
                template="""Eres un asistente especializado en narrativa y escritura creativa. 
Tienes profundo conocimiento en técnicas narrativas, desarrollo de personajes, estructura de historias, 
géneros literarios y recursos estilísticos.
{general_expectations}

Mejora el contenido considerando:
- Elementos narrativos (narrador, personajes, tiempo, espacio, acción)
- Técnicas de escritura creativa (show don't tell, diálogos, descripción)
- Estructura narrativa (introducción, nudo, desenlace, arcos narrativos)
- Géneros y subgéneros literarios
- Estilo y voz narrativa
- Recursos retóricos y literarios

CONTENIDO DEL TEXTO A PROCESAR:
{email_content}

{attachments_section}

Proporciona mejoras de forma experta sobre narrativa y escritura creativa, 
ofreciendo cambios y consejos prácticos y técnicos para mejorar la calidad narrativa."""
            ),
            
            # Academic essay template
            PromptTemplate(
                name="essay",
                keywords=[
                    "ensayo", "ensayístico", "ensayistico", "académico", "academico",
                    "tesis", "argumento", "argumentación", "argumentacion", "análisis", "analisis",
                    "reflexión", "reflexion", "essay", "academic", "thesis", "argument",
                    "argumentation", "analysis", "reflection", "dissertation", "research"
                ],
                priority=5,
                template="""
Eres un asistente especializado en escritura académica y ensayística. 
Dominas la estructura argumentativa, metodología de investigación, citación académica, 
y técnicas de análisis crítico.
{general_expectations}

Mejora el contenido considerando:
- Estructura del ensayo académico (introducción, desarrollo, conclusión)
- Construcción de argumentos sólidos y evidencia
- Metodología de investigación y fuentes confiables
- Sistemas de citación académica (APA, MLA, Chicago, etc.)
- Técnicas de análisis crítico y síntesis
- Coherencia y cohesión textual
- Registro académico apropiado

CONTENIDO DEL TEXTO A PROCESAR:
{email_content}

{attachments_section}

Proporciona unas mejoras de forma académica rigurosa y profesional, 
ayudando a estructurar ideas de manera clara y argumentativamente sólida."""
            ),
            
            # Theater/Drama template
            PromptTemplate(
                name="theater",
                keywords=[
                    "teatro", "obra", "dramaturgia", "guión", "guion", "diálogo", "dialogo",
                    "personaje", "escena", "acto", "drama", "comedia", "tragedia",
                    "monólogo", "monologo", "theater", "theatre", "play", "script",
                    "screenplay", "dialogue", "character", "scene", "act", "drama",
                    "comedy", "tragedy", "monologue", "dramaturgy"
                ],
                priority=3,
                template="""
Eres un asistente especializado en teatro y dramaturgia. 
Tienes amplio conocimiento en escritura teatral, técnicas dramáticas, historia del teatro, 
y análisis de obras teatrales.
{general_expectations}

Mejora el contenido considerando:
- Estructura dramática (exposición, conflicto, climax, resolución)
- Construcción de personajes teatrales y desarrollo de caracteres
- Técnicas de diálogo teatral y subtexto
- Géneros teatrales (drama, comedia, tragedia, etc.)
- Elementos técnicos del teatro (escenografía, iluminación, sonido)
- Historia y movimientos teatrales
- Adaptación y puesta en escena

CONTENIDO DEL TEXTO A PROCESAR:
{email_content}

{attachments_section}

Proporciona mejoras de forma experta en teatro y dramaturgia, 
ofreciendo modificaciones prácticas para la creación y análisis teatral."""
            ),
            
            # Technical/Programming template
            PromptTemplate(
                name="technical",
                keywords=[
                    "código", "codigo", "programación", "programacion", "software", "desarrollo",
                    "algoritmo", "base de datos", "API", "framework", "programming", "coding",
                    "development", "algorithm", "database", "technical", "system", "architecture",
                    "debug", "testing", "deployment", "python", "javascript", "html", "css"
                ],
                priority=2,
                template="""Eres un asistente técnico especializado en programación y desarrollo de software. 
Tienes experiencia en múltiples lenguajes de programación, arquitecturas de sistemas, 
bases de datos y mejores prácticas de desarrollo.

Responde considerando:
- Mejores prácticas de programación y código limpio
- Arquitecturas de software y patrones de diseño
- Seguridad en el desarrollo de aplicaciones
- Performance y optimización
- Testing y debugging
- Documentación técnica
- Metodologías ágiles y DevOps

CONTENIDO DEL EMAIL:
{email_content}

{attachments_section}

Proporciona orientación técnica precisa y práctica, 
incluyendo ejemplos de código cuando sea relevante y siguiendo las mejores prácticas de la industria."""
            ),
            
            # Business/Marketing template
            PromptTemplate(
                name="business",
                keywords=[
                    "negocio", "empresa", "marketing", "ventas", "cliente", "mercado",
                    "estrategia", "plan", "ROI", "KPI", "business", "company", "sales",
                    "customer", "market", "strategy", "revenue", "profit", "analytics",
                    "branding", "advertising", "campaign", "lead", "conversion"
                ],
                priority=2,
                template="""Eres un consultor empresarial especializado en marketing y desarrollo de negocios. 
Tienes experiencia en estrategias comerciales, análisis de mercado, marketing digital, 
y crecimiento empresarial.

Responde considerando:
- Estrategias de marketing y posicionamiento
- Análisis de mercado y competencia
- Customer journey y experiencia del cliente
- Métricas de negocio (KPIs, ROI, conversión)
- Marketing digital y redes sociales
- Modelos de negocio y monetización
- Crecimiento y escalabilidad

CONTENIDO DEL EMAIL:
{email_content}

{attachments_section}

Proporciona orientación estratégica y práctica para el crecimiento del negocio, 
basándote en mejores prácticas y tendencias actuales del mercado."""
            ),
            
            # Generic template (fallback)
            PromptTemplate(
                name="generic",
                keywords=[],  # Empty keywords - this is the fallback
                priority=0,   # Lowest priority
                template="""Eres un asistente de IA profesional y útil que responde emails automáticamente. 
Proporciona respuestas claras, precisas y profesionales en español.

Analiza cuidadosamente el contenido del email y los documentos adjuntos (si los hay) 
para ofrecer la mejor asistencia posible.

CONTENIDO DEL EMAIL:
{email_content}

{attachments_section}

Responde de manera profesional y útil, adaptando tu tono y nivel de detalle 
al contexto y necesidades expresadas en el mensaje. Si necesitas más información 
para proporcionar una respuesta completa, indica qué información adicional sería útil."""
            )
        ]
    
    def detect_content_type(self, text: str) -> Tuple[str, PromptTemplate]:
        """
        Detect content type based on keywords in text
        
        Args:
            text (str): Text to analyze (email body + attachments)
            
        Returns:
            Tuple[str, PromptTemplate]: (detected_type, template)
        """
        if not text:
            return "generic", self._get_template_by_name("generic")
        
        text_lower = text.lower()
        
        # Sort templates by priority (highest first)
        sorted_templates = sorted(self.templates, key=lambda t: t.priority, reverse=True)
        
        # Check each template's keywords
        for template in sorted_templates:
            if template.name == "generic":  # Skip generic for now
                continue
                
            # Count keyword matches
            matches = 0
            matched_keywords = []
            
            for keyword in template.keywords:
                if keyword.lower() in text_lower:
                    matches += 1
                    matched_keywords.append(keyword)
            
            # If we found matches, return this template
            if matches > 0:
                print(f"   Content type detected: {template.name} (keywords: {', '.join(matched_keywords[:3])})")
                return template.name, template
        
        # No matches found, return generic template
        print("   Content type: generic (no specific keywords detected)")
        return "generic", self._get_template_by_name("generic")
    
    def _get_template_by_name(self, name: str) -> PromptTemplate:
        """Get template by name"""
        for template in self.templates:
            if template.name == name:
                return template
        # Fallback to generic if not found
        return self.templates[-1]  # Generic is always last
    
    def generate_prompt(self, email_body: str, attachments: List[Dict[str, Any]] = None) -> str:
        """
        Generate specialized prompt based on content analysis
        
        Args:
            email_body (str): Email body text
            attachments (List[Dict]): List of processed attachments
            
        Returns:
            str: Generated prompt for AI
        """
        # Combine email body and attachment content for analysis
        full_text = email_body
        
        attachments_content = ""
        if attachments:
            attachments_content = "\n".join([att.get('content', '') for att in attachments])
            full_text += "\n" + attachments_content
        
        # Detect content type
        content_type, template = self.detect_content_type(full_text)
        
        # Prepare attachments section for template
        attachments_section = ""
        if attachments:
            # attachments_section = "DOCUMENTOS ADJUNTOS:\n"
            for attachment in attachments:
                # attachments_section += f"Archivo: {attachment['filename']} ({attachment['type'].upper()}):\n"
                attachments_section += f"{attachment['content']}\n\n"
        
        # Format the template
        try:
            formatted_prompt = template.template.format(
                email_content=email_body,
                attachments_section=attachments_section
            )
        except KeyError as e:
            print(f"Warning: Template formatting error: {e}")
            # Fallback to generic template
            generic_template = self._get_template_by_name("generic")
            formatted_prompt = generic_template.template.format(
                email_content=email_body,
                attachments_section=attachments_section
            )
        
        return formatted_prompt
    
    def add_custom_template(self, name: str, keywords: List[str], 
                           template: str, priority: int = 1) -> bool:
        """
        Add a custom template
        
        Args:
            name (str): Template name
            keywords (List[str]): Keywords to detect
            template (str): Template string with {email_content} and {attachments_section} placeholders
            priority (int): Priority level
            
        Returns:
            bool: True if added successfully
        """
        try:
            # Validate template has required placeholders
            if "{email_content}" not in template:
                print(f"Warning: Template '{name}' missing {{email_content}} placeholder")
                return False
            
            new_template = PromptTemplate(
                name=name,
                keywords=keywords,
                template=template,
                priority=priority
            )
            
            # Remove existing template with same name if it exists
            self.templates = [t for t in self.templates if t.name != name]
            
            # Add new template
            self.templates.append(new_template)
            
            print(f"Custom template '{name}' added successfully")
            return True
            
        except Exception as e:
            print(f"Error adding custom template: {e}")
            return False
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        return [
            {
                "name": template.name,
                "priority": template.priority,
                "keywords_count": len(template.keywords),
                "sample_keywords": template.keywords[:5]  # First 5 keywords
            }
            for template in sorted(self.templates, key=lambda t: t.priority, reverse=True)
        ]
    
    def get_template_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific template"""
        template = self._get_template_by_name(name)
        if not template:
            return None
            
        return {
            "name": template.name,
            "priority": template.priority,
            "keywords": template.keywords,
            "template": template.template[:200] + "..." if len(template.template) > 200 else template.template
        }