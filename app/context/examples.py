""" 
Módulo de contexto estático para la arquitectura CAG. 
Almacena estimaciones históricas que sirven como ejemplos ('few-shot')
para guiar al modelo de lenguaje en el formato y precisión de la respuesta. 
""" 
ESTIMATION_EXAMPLES = [
    {
    "meeting_summary": "El cliente necesita una plataforma web de gestión de inventario...",
    "estimation": 
    """
        ## Estimación: Plataforma de Gestión de Inventario
        
        ### Desglose de tareas:
        1. Diseño UI/UX: 40 horas
        2. Backend API (CRUD inventario): 60 horas
        3. Autenticación y roles: 20 horas
        4. Dashboard con métricas: 30 horas
        5. Testing y QA: 25 horas
        
        **Total estimado: 175 horas**
        **Equipo recomendado: 2 desarrolladores full-stack + 1 diseñador UX (part-time)**
        **Duración estimada: 6-8 semanas**
    """
    },
    {
    "meeting_summary": "Creación de una landing page promocional con formulario de contacto e integración a CRM vía API.", 
    "estimation": 
    """
        ## Estimación: Landing Page + Integración CRM 
            ### Desglose de tareas: 
            1. Maquetación y diseño responsivo: 15 horas 
            2. Formulario con validaciones: 10 horas 
            3. Integración con API de CRM: 15 horas 

            **Total estimado: 40 horas** 
            **Equipo recomendado: 1 desarrollador front-end + 1 diseñador UX (part-time)**
            **Duración estimada: 1-2 semanas**
    """
    }
]