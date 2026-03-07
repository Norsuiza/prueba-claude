import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


GOLD = colors.HexColor('#B8860B')
DARK = colors.HexColor('#1a1a2e')
LIGHT_GRAY = colors.HexColor('#f5f5f5')
WHITE = colors.white
BLACK = colors.black


def _section_header(text, styles):
    style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=WHITE,
        backColor=DARK,
        spaceAfter=4,
        spaceBefore=10,
        leftIndent=6,
        rightIndent=6,
        leading=16,
        fontName='Helvetica-Bold',
    )
    return Paragraph(text, style)


def _field_row(label, value):
    return [
        Paragraph(f'<b>{label}:</b>', ParagraphStyle(
            'Label', fontSize=8, fontName='Helvetica-Bold', textColor=DARK
        )),
        Paragraph(str(value) if value else '—', ParagraphStyle(
            'Value', fontSize=8, fontName='Helvetica', textColor=BLACK
        )),
    ]


def _val(data, key, default='—'):
    v = data.get(key, default)
    if isinstance(v, list):
        return ', '.join(v) if v else default
    return str(v) if v else default


def generate_iph_pdf(form_data, user_data, output_path):
    if not REPORTLAB_AVAILABLE:
        raise ImportError('reportlab no está instalado. Ejecuta: pip install reportlab')

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontSize=13, textColor=DARK, fontName='Helvetica-Bold',
        spaceAfter=4, alignment=1,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=10, textColor=GOLD, fontName='Helvetica-Bold',
        spaceAfter=2, alignment=1,
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontSize=8, textColor=colors.gray,
        spaceAfter=8, alignment=1,
    )

    story.append(Paragraph('SISTEMA NACIONAL DE SEGURIDAD PÚBLICA', title_style))
    story.append(Paragraph('INFORME POLICIAL HOMOLOGADO (IPH2019)', title_style))
    story.append(Paragraph('HECHO PROBABLEMENTE DELICTIVO', subtitle_style))
    story.append(Paragraph(
        f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")} | '
        f'No. Expediente: {_val(form_data, "no_expediente")}',
        meta_style
    ))
    story.append(HRFlowable(width='100%', thickness=2, color=GOLD))
    story.append(Spacer(1, 0.3 * cm))

    def add_table(rows):
        t = Table(rows, colWidths=[5 * cm, 12 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2 * cm))

    # SECCIÓN 1
    story.append(_section_header('SECCIÓN 1. PUESTA A DISPOSICIÓN', styles))
    add_table([
        _field_row('Fecha de puesta a disposición', _val(form_data, 'fecha_puesta_disposicion')),
        _field_row('Hora', _val(form_data, 'hora_puesta_disposicion')),
        _field_row('No. Expediente', _val(form_data, 'no_expediente')),
        _field_row('Anexos entregados', _val(form_data, 'anexos_usados')),
        _field_row('Documentación complementaria', _val(form_data, 'doc_complementaria')),
        _field_row('Tipo de documentación', _val(form_data, 'tipo_doc_complementaria')),
    ])

    story.append(_section_header('DATOS DE QUIEN REALIZA LA PUESTA A DISPOSICIÓN', styles))
    add_table([
        _field_row('Primer apellido', _val(form_data, 'oficial_primer_apellido')),
        _field_row('Segundo apellido', _val(form_data, 'oficial_segundo_apellido')),
        _field_row('Nombre(s)', _val(form_data, 'oficial_nombre')),
        _field_row('Adscripción', _val(form_data, 'oficial_adscripcion')),
        _field_row('Cargo/Grado', _val(form_data, 'oficial_cargo')),
    ])

    story.append(_section_header('FISCAL/AUTORIDAD QUE RECIBE', styles))
    add_table([
        _field_row('Primer apellido', _val(form_data, 'fiscal_primer_apellido')),
        _field_row('Segundo apellido', _val(form_data, 'fiscal_segundo_apellido')),
        _field_row('Nombre(s)', _val(form_data, 'fiscal_nombre')),
        _field_row('Fiscalía/Autoridad', _val(form_data, 'fiscal_autoridad')),
        _field_row('Cargo', _val(form_data, 'fiscal_cargo')),
    ])

    # SECCIÓN 2
    story.append(_section_header('SECCIÓN 2. PRIMER RESPONDIENTE', styles))
    add_table([
        _field_row('Primer apellido', _val(form_data, 'respondiente_primer_apellido')),
        _field_row('Segundo apellido', _val(form_data, 'respondiente_segundo_apellido')),
        _field_row('Nombre(s)', _val(form_data, 'respondiente_nombre')),
        _field_row('Institución', _val(form_data, 'respondiente_institucion')),
        _field_row('Cargo/Grado', _val(form_data, 'respondiente_cargo')),
        _field_row('Unidad', _val(form_data, 'respondiente_unidad')),
        _field_row('Más de un elemento', _val(form_data, 'mas_elementos')),
        _field_row('Cuántos elementos', _val(form_data, 'cuantos_elementos')),
    ])

    # SECCIÓN 3
    story.append(_section_header('SECCIÓN 3. CONOCIMIENTO DEL HECHO', styles))
    add_table([
        _field_row('¿Cómo se enteró?', _val(form_data, 'como_entero_hecho')),
        _field_row('No. 911', _val(form_data, 'numero_911')),
        _field_row('Fecha conocimiento', _val(form_data, 'fecha_conocimiento')),
        _field_row('Hora conocimiento', _val(form_data, 'hora_conocimiento')),
        _field_row('Fecha arribo', _val(form_data, 'fecha_arribo')),
        _field_row('Hora arribo', _val(form_data, 'hora_arribo')),
    ])

    # SECCIÓN 4
    story.append(_section_header('SECCIÓN 4. LUGAR DE LA INTERVENCIÓN', styles))
    add_table([
        _field_row('Calle/Tramo carretero', _val(form_data, 'calle')),
        _field_row('No. Exterior', _val(form_data, 'no_exterior')),
        _field_row('Colonia/Localidad', _val(form_data, 'colonia')),
        _field_row('Municipio', _val(form_data, 'municipio')),
        _field_row('Entidad federativa', _val(form_data, 'entidad_federativa')),
        _field_row('Referencias', _val(form_data, 'referencias')),
        _field_row('Coordenadas GPS', _val(form_data, 'coordenadas')),
        _field_row('Inspección del lugar', _val(form_data, 'inspeccion_lugar')),
        _field_row('Objetos hallados', _val(form_data, 'objetos_hallados')),
        _field_row('Preservó el lugar', _val(form_data, 'preservo_lugar')),
        _field_row('Priorización', _val(form_data, 'priorizacion')),
        _field_row('Tipo de riesgo', _val(form_data, 'tipo_riesgo')),
        _field_row('Especifique riesgo', _val(form_data, 'especifique_riesgo')),
    ])

    # SECCIÓN 5
    story.append(_section_header('SECCIÓN 5. NARRATIVA DE LOS HECHOS', styles))
    narr_style = ParagraphStyle(
        'Narr', fontSize=9, fontName='Helvetica',
        leading=14, spaceAfter=8, leftIndent=6, rightIndent=6
    )
    narrativa = form_data.get('narrativa_hechos', '—')
    story.append(Paragraph(str(narrativa), narr_style))
    story.append(Spacer(1, 0.2 * cm))

    # ANEXO A
    if form_data.get('detenido_primer_apellido'):
        story.append(_section_header('ANEXO A. DETENCIÓN(ES)', styles))
        add_table([
            _field_row('Primer apellido', _val(form_data, 'detenido_primer_apellido')),
            _field_row('Segundo apellido', _val(form_data, 'detenido_segundo_apellido')),
            _field_row('Nombre(s)', _val(form_data, 'detenido_nombre')),
            _field_row('Apodo/alias', _val(form_data, 'detenido_apodo')),
            _field_row('Sexo', _val(form_data, 'detenido_sexo')),
            _field_row('Nacionalidad', _val(form_data, 'detenido_nacionalidad')),
            _field_row('Fecha de nacimiento', _val(form_data, 'detenido_fecha_nacimiento')),
            _field_row('Identificación', _val(form_data, 'detenido_identificacion')),
            _field_row('Fecha de detención', _val(form_data, 'detenido_fecha_detencion')),
            _field_row('Hora de detención', _val(form_data, 'detenido_hora_detencion')),
            _field_row('Domicilio - Calle', _val(form_data, 'detenido_calle')),
            _field_row('Domicilio - Colonia', _val(form_data, 'detenido_colonia')),
            _field_row('Lesiones visibles', _val(form_data, 'detenido_lesiones')),
            _field_row('Padecimiento', _val(form_data, 'detenido_padecimiento')),
            _field_row('Grupo vulnerable', _val(form_data, 'detenido_grupo_vulnerable')),
            _field_row('Grupo delictivo', _val(form_data, 'detenido_grupo_delictivo')),
            _field_row('Familiar/confianza', _val(form_data, 'familiar_nombre')),
            _field_row('Tel. familiar', _val(form_data, 'familiar_telefono')),
            _field_row('Derechos informados', _val(form_data, 'derechos_informados')),
            _field_row('Lugar de traslado', _val(form_data, 'lugar_traslado')),
        ])
        story.append(Paragraph(
            f"<b>Descripción física:</b> {_val(form_data, 'detenido_descripcion')}",
            ParagraphStyle('Desc', fontSize=9, fontName='Helvetica', leading=13, leftIndent=6)
        ))
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(
            f"<b>Observaciones del traslado:</b> {_val(form_data, 'obs_detencion')}",
            ParagraphStyle('Obs', fontSize=9, fontName='Helvetica', leading=13, leftIndent=6)
        ))
        story.append(Spacer(1, 0.2 * cm))

    # ANEXO B
    if form_data.get('nivel_fuerza'):
        story.append(_section_header('ANEXO B. INFORME DEL USO DE LA FUERZA', styles))
        add_table([
            _field_row('Lesionados autoridad', _val(form_data, 'lesionados_autoridad')),
            _field_row('Lesionados civiles', _val(form_data, 'lesionados_persona')),
            _field_row('Nivel de fuerza', _val(form_data, 'nivel_fuerza')),
            _field_row('Asistencia médica', _val(form_data, 'asistencia_medica')),
        ])
        story.append(Paragraph(
            f"<b>Conductas que motivaron el uso de la fuerza:</b><br/>{_val(form_data, 'conductas_fuerza')}",
            ParagraphStyle('Cond', fontSize=9, fontName='Helvetica', leading=13, leftIndent=6)
        ))
        story.append(Spacer(1, 0.2 * cm))

    # ANEXO C
    if form_data.get('vehiculo_marca'):
        story.append(_section_header('ANEXO C. INSPECCIÓN DE VEHÍCULO', styles))
        add_table([
            _field_row('Tipo', _val(form_data, 'vehiculo_tipo')),
            _field_row('Procedencia', _val(form_data, 'vehiculo_procedencia')),
            _field_row('Marca', _val(form_data, 'vehiculo_marca')),
            _field_row('Submarca/Modelo', _val(form_data, 'vehiculo_submarca')),
            _field_row('Color', _val(form_data, 'vehiculo_color')),
            _field_row('Uso', _val(form_data, 'vehiculo_uso')),
            _field_row('Placa/Matrícula', _val(form_data, 'vehiculo_placa')),
            _field_row('Situación', _val(form_data, 'vehiculo_situacion')),
            _field_row('Objetos relacionados', _val(form_data, 'vehiculo_objetos')),
            _field_row('Destino del vehículo', _val(form_data, 'vehiculo_destino')),
        ])

    # ANEXO E
    if form_data.get('entrevistado_primer_apellido'):
        story.append(_section_header('ANEXO E. ENTREVISTAS', styles))
        add_table([
            _field_row('Primer apellido', _val(form_data, 'entrevistado_primer_apellido')),
            _field_row('Segundo apellido', _val(form_data, 'entrevistado_segundo_apellido')),
            _field_row('Nombre(s)', _val(form_data, 'entrevistado_nombre')),
            _field_row('Calidad', _val(form_data, 'entrevistado_calidad')),
            _field_row('Sexo', _val(form_data, 'entrevistado_sexo')),
            _field_row('Teléfono', _val(form_data, 'entrevistado_telefono')),
        ])
        story.append(Paragraph(
            f"<b>Relato:</b> {_val(form_data, 'entrevistado_relato')}",
            ParagraphStyle('Relato', fontSize=9, fontName='Helvetica', leading=13, leftIndent=6)
        ))
        story.append(Spacer(1, 0.2 * cm))

    doc.build(story)
    return output_path
