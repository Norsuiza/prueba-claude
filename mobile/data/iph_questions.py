# Tipos de pregunta:
# 'text'        → campo de texto libre
# 'date'        → fecha DD/MM/AAAA
# 'time'        → hora HH:MM
# 'yes_no'      → botones Sí / No
# 'choice'      → una opción de lista
# 'multiselect' → varias opciones
# 'long_text'   → texto largo (narrativa)

INSTITUTIONS = [
    'Policía Municipal',
    'Policía Estatal',
    'Guardia Nacional',
    'Policía Ministerial',
    'Policía Federal Ministerial',
    'Policía Mando Único',
    'Otra autoridad',
]

CONOCIMIENTO_OPCIONES = [
    'Denuncia',
    'Flagrancia',
    'Localización',
    'Mandamiento judicial',
    'Llamada de emergencia (911)',
    'Descubrimiento',
    'Aportación',
]

ANEXOS_OPCIONES = [
    'Anexo A - Detención(es)',
    'Anexo B - Uso de la fuerza',
    'Anexo C - Inspección de vehículo',
    'Anexo D - Inventario de armas/objetos',
    'Anexo E - Entrevistas',
    'Anexo F - Entrega-recepción del lugar',
    'Anexo G - Continuación narrativa',
]

PREGUNTAS_SECCION1 = [
    {
        'id': 'fecha_puesta',
        'seccion': 'Sección 1 - Puesta a Disposición',
        'texto': '¿Cuál es la fecha de la puesta a disposición?',
        'tipo': 'date',
        'campo': 'fecha_puesta_disposicion',
    },
    {
        'id': 'hora_puesta',
        'seccion': 'Sección 1 - Puesta a Disposición',
        'texto': '¿Cuál es la hora de la puesta a disposición? (formato 24 hrs)',
        'tipo': 'time',
        'campo': 'hora_puesta_disposicion',
    },
    {
        'id': 'no_expediente',
        'seccion': 'Sección 1 - Puesta a Disposición',
        'texto': '¿Cuál es el número de expediente? (si no aplica, escribe N/A)',
        'tipo': 'text',
        'campo': 'no_expediente',
    },
    {
        'id': 'anexos_usados',
        'seccion': 'Sección 1 - Puesta a Disposición',
        'texto': '¿Cuáles Anexos se entregarán? Selecciona todos los que apliquen.',
        'tipo': 'multiselect',
        'opciones': ANEXOS_OPCIONES,
        'campo': 'anexos_usados',
    },
    {
        'id': 'doc_complementaria',
        'seccion': 'Sección 1 - Puesta a Disposición',
        'texto': '¿Se anexa documentación complementaria?',
        'tipo': 'yes_no',
        'campo': 'doc_complementaria',
    },
    {
        'id': 'tipo_doc',
        'seccion': 'Sección 1 - Puesta a Disposición',
        'texto': '¿Qué tipo de documentación? Selecciona los que apliquen.',
        'tipo': 'multiselect',
        'opciones': ['Fotografías', 'Audio', 'Videos', 'Certificados médicos', 'Otra'],
        'campo': 'tipo_doc_complementaria',
        'condicion': lambda data: data.get('doc_complementaria') == 'Sí',
    },
    {
        'id': 'oficial_primer_apellido',
        'seccion': 'Sección 1 - Datos del Oficial',
        'texto': '¿Cuál es tu primer apellido? (quien realiza la puesta a disposición)',
        'tipo': 'text',
        'campo': 'oficial_primer_apellido',
        'prefill': 'primer_apellido',
    },
    {
        'id': 'oficial_segundo_apellido',
        'seccion': 'Sección 1 - Datos del Oficial',
        'texto': '¿Cuál es tu segundo apellido?',
        'tipo': 'text',
        'campo': 'oficial_segundo_apellido',
        'prefill': 'segundo_apellido',
    },
    {
        'id': 'oficial_nombre',
        'seccion': 'Sección 1 - Datos del Oficial',
        'texto': '¿Cuál es tu nombre(s)?',
        'tipo': 'text',
        'campo': 'oficial_nombre',
        'prefill': 'nombre',
    },
    {
        'id': 'oficial_adscripcion',
        'seccion': 'Sección 1 - Datos del Oficial',
        'texto': '¿Cuál es tu adscripción?',
        'tipo': 'text',
        'campo': 'oficial_adscripcion',
        'prefill': 'adscripcion',
    },
    {
        'id': 'oficial_cargo',
        'seccion': 'Sección 1 - Datos del Oficial',
        'texto': '¿Cuál es tu cargo/grado?',
        'tipo': 'text',
        'campo': 'oficial_cargo',
        'prefill': 'cargo_grado',
    },
    {
        'id': 'fiscal_primer_apellido',
        'seccion': 'Sección 1 - Fiscal que Recibe',
        'texto': 'Primer apellido del Fiscal/Autoridad que recibe la puesta a disposición:',
        'tipo': 'text',
        'campo': 'fiscal_primer_apellido',
    },
    {
        'id': 'fiscal_segundo_apellido',
        'seccion': 'Sección 1 - Fiscal que Recibe',
        'texto': 'Segundo apellido del Fiscal/Autoridad:',
        'tipo': 'text',
        'campo': 'fiscal_segundo_apellido',
    },
    {
        'id': 'fiscal_nombre',
        'seccion': 'Sección 1 - Fiscal que Recibe',
        'texto': 'Nombre(s) del Fiscal/Autoridad:',
        'tipo': 'text',
        'campo': 'fiscal_nombre',
    },
    {
        'id': 'fiscal_autoridad',
        'seccion': 'Sección 1 - Fiscal que Recibe',
        'texto': '¿A qué Fiscalía/Autoridad pertenece?',
        'tipo': 'text',
        'campo': 'fiscal_autoridad',
    },
    {
        'id': 'fiscal_cargo',
        'seccion': 'Sección 1 - Fiscal que Recibe',
        'texto': '¿Cuál es el cargo del Fiscal/Autoridad?',
        'tipo': 'text',
        'campo': 'fiscal_cargo',
    },
]

PREGUNTAS_SECCION2 = [
    {
        'id': 'respondiente_primer_apellido',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': 'Primer apellido del primer respondiente:',
        'tipo': 'text',
        'campo': 'respondiente_primer_apellido',
        'prefill': 'primer_apellido',
    },
    {
        'id': 'respondiente_segundo_apellido',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': 'Segundo apellido del primer respondiente:',
        'tipo': 'text',
        'campo': 'respondiente_segundo_apellido',
        'prefill': 'segundo_apellido',
    },
    {
        'id': 'respondiente_nombre',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': 'Nombre(s) del primer respondiente:',
        'tipo': 'text',
        'campo': 'respondiente_nombre',
        'prefill': 'nombre',
    },
    {
        'id': 'respondiente_institucion',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': '¿A qué institución pertenece el primer respondiente?',
        'tipo': 'choice',
        'opciones': INSTITUTIONS,
        'campo': 'respondiente_institucion',
        'prefill': 'institucion',
    },
    {
        'id': 'respondiente_cargo',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': '¿Cuál es su grado o cargo?',
        'tipo': 'text',
        'campo': 'respondiente_cargo',
        'prefill': 'cargo_grado',
    },
    {
        'id': 'respondiente_unidad',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': '¿En qué unidad llegó al lugar? (Número de patrulla, moto, etc.)',
        'tipo': 'text',
        'campo': 'respondiente_unidad',
    },
    {
        'id': 'mas_elementos',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': '¿Llegó más de un elemento al lugar?',
        'tipo': 'yes_no',
        'campo': 'mas_elementos',
    },
    {
        'id': 'cuantos_elementos',
        'seccion': 'Sección 2 - Primer Respondiente',
        'texto': '¿Cuántos elementos llegaron al lugar?',
        'tipo': 'text',
        'campo': 'cuantos_elementos',
        'condicion': lambda data: data.get('mas_elementos') == 'Sí',
    },
]

PREGUNTAS_SECCION3 = [
    {
        'id': 'como_entero',
        'seccion': 'Sección 3 - Conocimiento del Hecho',
        'texto': '¿Cómo se enteró del hecho?',
        'tipo': 'choice',
        'opciones': CONOCIMIENTO_OPCIONES,
        'campo': 'como_entero_hecho',
    },
    {
        'id': 'numero_911',
        'seccion': 'Sección 3 - Conocimiento del Hecho',
        'texto': '¿Tienes número de reporte del 911? Si no, escribe N/A.',
        'tipo': 'text',
        'campo': 'numero_911',
        'condicion': lambda data: data.get('como_entero_hecho') == 'Llamada de emergencia (911)',
    },
    {
        'id': 'fecha_conocimiento',
        'seccion': 'Sección 3 - Conocimiento del Hecho',
        'texto': '¿Cuál es la fecha en que se enteró del hecho?',
        'tipo': 'date',
        'campo': 'fecha_conocimiento',
    },
    {
        'id': 'hora_conocimiento',
        'seccion': 'Sección 3 - Conocimiento del Hecho',
        'texto': '¿A qué hora se enteró del hecho? (24 hrs)',
        'tipo': 'time',
        'campo': 'hora_conocimiento',
    },
    {
        'id': 'fecha_arribo',
        'seccion': 'Sección 3 - Conocimiento del Hecho',
        'texto': '¿Cuál es la fecha en que llegó al lugar?',
        'tipo': 'date',
        'campo': 'fecha_arribo',
    },
    {
        'id': 'hora_arribo',
        'seccion': 'Sección 3 - Conocimiento del Hecho',
        'texto': '¿A qué hora llegó al lugar? (24 hrs)',
        'tipo': 'time',
        'campo': 'hora_arribo',
    },
]

PREGUNTAS_SECCION4 = [
    {
        'id': 'calle',
        'seccion': 'Sección 4 - Lugar de la Intervención',
        'texto': '¿Cuál es la calle o tramo carretero del lugar?',
        'tipo': 'text',
        'campo': 'calle',
    },
    {
        'id': 'no_exterior',
        'seccion': 'Sección 4 - Lugar de la Intervención',
        'texto': 'Número exterior (si no aplica, escribe S/N):',
        'tipo': 'text',
        'campo': 'no_exterior',
    },
    {
        'id': 'colonia',
        'seccion': 'Sección 4 - Lugar de la Intervención',
        'texto': '¿Colonia o localidad?',
        'tipo': 'text',
        'campo': 'colonia',
    },
    {
        'id': 'municipio',
        'seccion': 'Sección 4 - Lugar de la Intervención',
        'texto': '¿Municipio o demarcación territorial?',
        'tipo': 'text',
        'campo': 'municipio',
    },
    {
        'id': 'entidad',
        'seccion': 'Sección 4 - Lugar de la Intervención',
        'texto': '¿Entidad federativa?',
        'tipo': 'text',
        'campo': 'entidad_federativa',
    },
    {
        'id': 'referencias',
        'seccion': 'Sección 4 - Lugar de la Intervención',
        'texto': 'Referencias del lugar (entre qué calles, landmarks, etc.):',
        'tipo': 'text',
        'campo': 'referencias',
    },
    {
        'id': 'coordenadas',
        'seccion': 'Sección 4 - Lugar de la Intervención',
        'texto': '¿Tienes las coordenadas GPS del lugar? (escribe "Latitud,Longitud" o N/A)',
        'tipo': 'text',
        'campo': 'coordenadas',
    },
    {
        'id': 'inspeccion_lugar',
        'seccion': 'Sección 4 - Inspección del Lugar',
        'texto': '¿Realizó la inspección del lugar?',
        'tipo': 'yes_no',
        'campo': 'inspeccion_lugar',
    },
    {
        'id': 'objetos_hallados',
        'seccion': 'Sección 4 - Inspección del Lugar',
        'texto': '¿Encontró objetos relacionados con los hechos?',
        'tipo': 'yes_no',
        'campo': 'objetos_hallados',
    },
    {
        'id': 'preservo_lugar',
        'seccion': 'Sección 4 - Inspección del Lugar',
        'texto': '¿Preservó el lugar de la intervención?',
        'tipo': 'yes_no',
        'campo': 'preservo_lugar',
    },
    {
        'id': 'priorizacion',
        'seccion': 'Sección 4 - Inspección del Lugar',
        'texto': '¿Llevó a cabo la priorización en el lugar?',
        'tipo': 'yes_no',
        'campo': 'priorizacion',
    },
    {
        'id': 'tipo_riesgo',
        'seccion': 'Sección 4 - Inspección del Lugar',
        'texto': '¿Qué tipo de riesgo se presentó?',
        'tipo': 'choice',
        'opciones': ['Sociales', 'Naturales'],
        'campo': 'tipo_riesgo',
        'condicion': lambda data: data.get('priorizacion') == 'Sí',
    },
    {
        'id': 'especifique_riesgo',
        'seccion': 'Sección 4 - Inspección del Lugar',
        'texto': 'Especifique el tipo de riesgo:',
        'tipo': 'text',
        'campo': 'especifique_riesgo',
        'condicion': lambda data: data.get('priorizacion') == 'Sí',
    },
]

PREGUNTAS_SECCION5 = [
    {
        'id': 'narrativa',
        'seccion': 'Sección 5 - Narrativa de los Hechos',
        'texto': (
            'Relate cronológicamente los hechos desde el conocimiento '
            'hasta la puesta a disposición.\n'
            '(¿Quién? ¿Qué? ¿Cómo? ¿Cuándo? ¿Dónde?)'
        ),
        'tipo': 'long_text',
        'campo': 'narrativa_hechos',
    },
]

PREGUNTAS_ANEXO_A = [
    {
        'id': 'detenido_primer_apellido',
        'seccion': 'Anexo A - Detención',
        'texto': 'Primer apellido de la persona detenida:',
        'tipo': 'text',
        'campo': 'detenido_primer_apellido',
    },
    {
        'id': 'detenido_segundo_apellido',
        'seccion': 'Anexo A - Detención',
        'texto': 'Segundo apellido de la persona detenida:',
        'tipo': 'text',
        'campo': 'detenido_segundo_apellido',
    },
    {
        'id': 'detenido_nombre',
        'seccion': 'Anexo A - Detención',
        'texto': 'Nombre(s) de la persona detenida:',
        'tipo': 'text',
        'campo': 'detenido_nombre',
    },
    {
        'id': 'detenido_apodo',
        'seccion': 'Anexo A - Detención',
        'texto': 'Apodo o alias (si no tiene, escribe N/A):',
        'tipo': 'text',
        'campo': 'detenido_apodo',
    },
    {
        'id': 'detenido_sexo',
        'seccion': 'Anexo A - Detención',
        'texto': '¿Sexo de la persona detenida?',
        'tipo': 'choice',
        'opciones': ['Mujer', 'Hombre'],
        'campo': 'detenido_sexo',
    },
    {
        'id': 'detenido_nacionalidad',
        'seccion': 'Anexo A - Detención',
        'texto': '¿Nacionalidad de la persona detenida?',
        'tipo': 'choice',
        'opciones': ['Mexicana', 'Extranjera'],
        'campo': 'detenido_nacionalidad',
    },
    {
        'id': 'detenido_fecha_nac',
        'seccion': 'Anexo A - Detención',
        'texto': '¿Fecha de nacimiento de la persona detenida?',
        'tipo': 'date',
        'campo': 'detenido_fecha_nacimiento',
    },
    {
        'id': 'detenido_identificacion',
        'seccion': 'Anexo A - Detención',
        'texto': '¿Con qué documento se identificó?',
        'tipo': 'choice',
        'opciones': ['Credencial INE', 'Licencia', 'Pasaporte', 'Otro', 'No se identificó'],
        'campo': 'detenido_identificacion',
    },
    {
        'id': 'detenido_fecha_detencion',
        'seccion': 'Anexo A - Detención',
        'texto': '¿Cuál es la fecha de la detención?',
        'tipo': 'date',
        'campo': 'detenido_fecha_detencion',
    },
    {
        'id': 'detenido_hora_detencion',
        'seccion': 'Anexo A - Detención',
        'texto': '¿A qué hora se realizó la detención? (24 hrs)',
        'tipo': 'time',
        'campo': 'detenido_hora_detencion',
    },
    {
        'id': 'detenido_calle',
        'seccion': 'Anexo A - Domicilio del Detenido',
        'texto': 'Calle del domicilio de la persona detenida:',
        'tipo': 'text',
        'campo': 'detenido_calle',
    },
    {
        'id': 'detenido_colonia',
        'seccion': 'Anexo A - Domicilio del Detenido',
        'texto': 'Colonia del domicilio de la persona detenida:',
        'tipo': 'text',
        'campo': 'detenido_colonia',
    },
    {
        'id': 'detenido_descripcion',
        'seccion': 'Anexo A - Descripción Física',
        'texto': 'Describa brevemente a la persona detenida (vestimenta, rasgos visibles, tatuajes, etc.):',
        'tipo': 'long_text',
        'campo': 'detenido_descripcion',
    },
    {
        'id': 'detenido_lesiones',
        'seccion': 'Anexo A - Condición del Detenido',
        'texto': '¿La persona detenida presenta lesiones visibles?',
        'tipo': 'yes_no',
        'campo': 'detenido_lesiones',
    },
    {
        'id': 'detenido_padecimiento',
        'seccion': 'Anexo A - Condición del Detenido',
        'texto': '¿Manifiesta tener algún padecimiento?',
        'tipo': 'yes_no',
        'campo': 'detenido_padecimiento',
    },
    {
        'id': 'detenido_grupo_vulnerable',
        'seccion': 'Anexo A - Condición del Detenido',
        'texto': '¿Se identificó como miembro de algún grupo vulnerable?',
        'tipo': 'yes_no',
        'campo': 'detenido_grupo_vulnerable',
    },
    {
        'id': 'detenido_grupo_delictivo',
        'seccion': 'Anexo A - Condición del Detenido',
        'texto': '¿Se identificó como integrante de algún grupo delictivo?',
        'tipo': 'yes_no',
        'campo': 'detenido_grupo_delictivo',
    },
    {
        'id': 'familiar_nombre',
        'seccion': 'Anexo A - Familiar o Persona de Confianza',
        'texto': 'Nombre del familiar o persona de confianza señalado por el detenido (o N/A):',
        'tipo': 'text',
        'campo': 'familiar_nombre',
    },
    {
        'id': 'familiar_telefono',
        'seccion': 'Anexo A - Familiar o Persona de Confianza',
        'texto': 'Número telefónico del familiar (o N/A):',
        'tipo': 'text',
        'campo': 'familiar_telefono',
    },
    {
        'id': 'derechos_informados',
        'seccion': 'Anexo A - Derechos',
        'texto': '¿Le informó sus derechos a la persona detenida?',
        'tipo': 'yes_no',
        'campo': 'derechos_informados',
    },
    {
        'id': 'lugar_traslado',
        'seccion': 'Anexo A - Traslado',
        'texto': '¿A dónde se trasladó a la persona detenida?',
        'tipo': 'choice',
        'opciones': ['Fiscalía/Agencia', 'Hospital', 'Otra dependencia'],
        'campo': 'lugar_traslado',
    },
    {
        'id': 'obs_detencion',
        'seccion': 'Anexo A - Traslado',
        'texto': 'Observaciones del traslado (ruta, medio, demoras). Si no hay, escribe N/A:',
        'tipo': 'long_text',
        'campo': 'obs_detencion',
    },
]

PREGUNTAS_ANEXO_B = [
    {
        'id': 'lesionados_autoridad',
        'seccion': 'Anexo B - Uso de la Fuerza',
        'texto': '¿Cuántos lesionados de la autoridad? (número)',
        'tipo': 'text',
        'campo': 'lesionados_autoridad',
    },
    {
        'id': 'lesionados_persona',
        'seccion': 'Anexo B - Uso de la Fuerza',
        'texto': '¿Cuántos lesionados civiles? (número)',
        'tipo': 'text',
        'campo': 'lesionados_persona',
    },
    {
        'id': 'nivel_fuerza',
        'seccion': 'Anexo B - Uso de la Fuerza',
        'texto': '¿Qué nivel de fuerza se utilizó?',
        'tipo': 'choice',
        'opciones': [
            'Reducción física de movimientos',
            'Armas incapacitantes menos letales',
            'Armas de fuego / fuerza letal',
        ],
        'campo': 'nivel_fuerza',
    },
    {
        'id': 'conductas_fuerza',
        'seccion': 'Anexo B - Uso de la Fuerza',
        'texto': 'Describa las conductas que motivaron el uso de la fuerza:',
        'tipo': 'long_text',
        'campo': 'conductas_fuerza',
    },
    {
        'id': 'asistencia_medica',
        'seccion': 'Anexo B - Uso de la Fuerza',
        'texto': '¿Se brindó o solicitó asistencia médica?',
        'tipo': 'yes_no',
        'campo': 'asistencia_medica',
    },
]

PREGUNTAS_ANEXO_C = [
    {
        'id': 'vehiculo_tipo',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Tipo de vehículo?',
        'tipo': 'choice',
        'opciones': ['Terrestre', 'Acuático', 'Aéreo'],
        'campo': 'vehiculo_tipo',
    },
    {
        'id': 'vehiculo_procedencia',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Procedencia del vehículo?',
        'tipo': 'choice',
        'opciones': ['Nacional', 'Extranjero'],
        'campo': 'vehiculo_procedencia',
    },
    {
        'id': 'vehiculo_marca',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Marca del vehículo?',
        'tipo': 'text',
        'campo': 'vehiculo_marca',
    },
    {
        'id': 'vehiculo_submarca',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Submarca/Modelo del vehículo?',
        'tipo': 'text',
        'campo': 'vehiculo_submarca',
    },
    {
        'id': 'vehiculo_color',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Color del vehículo?',
        'tipo': 'text',
        'campo': 'vehiculo_color',
    },
    {
        'id': 'vehiculo_uso',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Uso del vehículo?',
        'tipo': 'choice',
        'opciones': ['Particular', 'Transporte público', 'Carga'],
        'campo': 'vehiculo_uso',
    },
    {
        'id': 'vehiculo_placa',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Placa/Matrícula? (si no tiene, escribe S/P)',
        'tipo': 'text',
        'campo': 'vehiculo_placa',
    },
    {
        'id': 'vehiculo_situacion',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Situación del vehículo?',
        'tipo': 'choice',
        'opciones': ['Con reporte de robo', 'Sin reporte de robo', 'No es posible saberlo'],
        'campo': 'vehiculo_situacion',
    },
    {
        'id': 'vehiculo_objetos',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Se encontraron objetos relacionados con los hechos en el vehículo?',
        'tipo': 'yes_no',
        'campo': 'vehiculo_objetos',
    },
    {
        'id': 'vehiculo_destino',
        'seccion': 'Anexo C - Inspección de Vehículo',
        'texto': '¿Destino que se le dio al vehículo?',
        'tipo': 'text',
        'campo': 'vehiculo_destino',
    },
]

PREGUNTAS_ANEXO_E = [
    {
        'id': 'entrevistado_primer_apellido',
        'seccion': 'Anexo E - Entrevista',
        'texto': 'Primer apellido de la persona entrevistada:',
        'tipo': 'text',
        'campo': 'entrevistado_primer_apellido',
    },
    {
        'id': 'entrevistado_segundo_apellido',
        'seccion': 'Anexo E - Entrevista',
        'texto': 'Segundo apellido de la persona entrevistada:',
        'tipo': 'text',
        'campo': 'entrevistado_segundo_apellido',
    },
    {
        'id': 'entrevistado_nombre',
        'seccion': 'Anexo E - Entrevista',
        'texto': 'Nombre(s) de la persona entrevistada:',
        'tipo': 'text',
        'campo': 'entrevistado_nombre',
    },
    {
        'id': 'entrevistado_calidad',
        'seccion': 'Anexo E - Entrevista',
        'texto': '¿Calidad de la persona entrevistada?',
        'tipo': 'choice',
        'opciones': ['Víctima u ofendido', 'Denunciante', 'Testigo'],
        'campo': 'entrevistado_calidad',
    },
    {
        'id': 'entrevistado_sexo',
        'seccion': 'Anexo E - Entrevista',
        'texto': '¿Sexo de la persona entrevistada?',
        'tipo': 'choice',
        'opciones': ['Mujer', 'Hombre'],
        'campo': 'entrevistado_sexo',
    },
    {
        'id': 'entrevistado_telefono',
        'seccion': 'Anexo E - Entrevista',
        'texto': 'Teléfono de la persona entrevistada (o N/A):',
        'tipo': 'text',
        'campo': 'entrevistado_telefono',
    },
    {
        'id': 'entrevistado_relato',
        'seccion': 'Anexo E - Entrevista',
        'texto': 'Relato de la entrevista:',
        'tipo': 'long_text',
        'campo': 'entrevistado_relato',
    },
]


def get_question_list(data=None):
    """Retorna la lista de preguntas activas según los datos ya capturados."""
    if data is None:
        data = {}

    all_q = (
        PREGUNTAS_SECCION1
        + PREGUNTAS_SECCION2
        + PREGUNTAS_SECCION3
        + PREGUNTAS_SECCION4
        + PREGUNTAS_SECCION5
    )

    anexos = data.get('anexos_usados', [])

    if 'Anexo A - Detención(es)' in anexos:
        all_q += PREGUNTAS_ANEXO_A
    if 'Anexo B - Uso de la fuerza' in anexos:
        all_q += PREGUNTAS_ANEXO_B
    if 'Anexo C - Inspección de vehículo' in anexos:
        all_q += PREGUNTAS_ANEXO_C
    if 'Anexo E - Entrevistas' in anexos:
        all_q += PREGUNTAS_ANEXO_E

    active = []
    for q in all_q:
        condicion = q.get('condicion')
        if condicion is None or condicion(data):
            active.append(q)

    return active
