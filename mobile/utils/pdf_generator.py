"""
Generador de PDF: sobrepone los datos del formulario sobre el IPH-DELITOS.pdf original.
Usa PyMuPDF (fitz) para insertar texto en las coordenadas exactas de cada campo.
"""
import os
import sys

try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'formatos', 'IPH-DELITOS.pdf'
)

BLACK = (0, 0, 0)
FONT = 'helv'
FS = 8      # font size normal
FS_SM = 7  # font size pequeño


def _val(data, key, default=''):
    v = data.get(key, default)
    if isinstance(v, list):
        return ', '.join(v) if v else default
    return str(v).strip() if v else default


def _put(page, x, y, text, fontsize=FS):
    """Inserta texto en coordenadas absolutas (x, y = baseline)."""
    if text:
        page.insert_text((x, y), text, fontname=FONT, fontsize=fontsize, color=BLACK)


def _put_after(page, label, text, occurrence=0, dx=5, dy=0, fontsize=FS):
    """Busca la etiqueta y coloca texto justo después (a la derecha)."""
    if not text:
        return
    hits = page.search_for(label)
    if len(hits) > occurrence:
        r = hits[occurrence]
        page.insert_text(
            (r.x1 + dx, r.y1 + dy),
            text, fontname=FONT, fontsize=fontsize, color=BLACK
        )


def _put_below(page, label, text, occurrence=0, dx=0, dy=2, fontsize=FS, max_width=None):
    """Busca la etiqueta y coloca texto abajo de ella."""
    if not text:
        return
    hits = page.search_for(label)
    if len(hits) > occurrence:
        r = hits[occurrence]
        _insert_wrapped(page, text, r.x0 + dx, r.y1 + dy + fontsize, fontsize, max_width or 500)


def _insert_wrapped(page, text, x, y, fontsize=FS, max_width=480, line_height=11):
    """Inserta texto con saltos de línea automáticos."""
    words = str(text).split()
    line = ''
    cur_y = y
    char_width = fontsize * 0.5  # aproximado
    max_chars = int(max_width / char_width)

    for word in words:
        test = (line + ' ' + word).strip()
        if len(test) > max_chars and line:
            page.insert_text((x, cur_y), line, fontname=FONT, fontsize=fontsize, color=BLACK)
            cur_y += line_height
            line = word
        else:
            line = test
    if line:
        page.insert_text((x, cur_y), line, fontname=FONT, fontsize=fontsize, color=BLACK)


def _fill_page1(page, data):
    """Sección 1: Puesta a Disposición."""
    # Fecha, Hora, No. Expediente
    _put(page, 70,  200, _val(data, 'fecha_puesta_disposicion'))
    _put(page, 228, 200, _val(data, 'hora_puesta_disposicion'))
    _put(page, 400, 200, _val(data, 'no_expediente'))

    # Datos de quien realiza la puesta a disposición (occurrence 0)
    _put(page, 100, 382, _val(data, 'oficial_primer_apellido'))
    _put(page, 100, 397, _val(data, 'oficial_segundo_apellido'))
    _put(page, 100, 412, _val(data, 'oficial_nombre'))
    _put(page, 100, 427, _val(data, 'oficial_adscripcion'))
    _put(page, 100, 442, _val(data, 'oficial_cargo'))

    # Fiscal/Autoridad que recibe (occurrence 1)
    _put(page, 100, 487, _val(data, 'fiscal_primer_apellido'))
    _put(page, 100, 501, _val(data, 'fiscal_segundo_apellido'))
    _put(page, 100, 516, _val(data, 'fiscal_nombre'))
    _put(page, 110, 531, _val(data, 'fiscal_autoridad'))
    _put(page, 100, 546, _val(data, 'fiscal_adscripcion') or _val(data, 'oficial_adscripcion'))
    _put(page, 70,  561, _val(data, 'fiscal_cargo'))


def _fill_page2(page, data):
    """Sección 2: Primer Respondiente | Sección 3: Conocimiento | Sección 4: Lugar."""
    # Sección 2 - nombres en columnas (y=73 es la línea de escritura bajo los headers)
    _put(page, 97,  78, _val(data, 'respondiente_primer_apellido'))
    _put(page, 266, 78, _val(data, 'respondiente_segundo_apellido'))
    _put(page, 430, 78, _val(data, 'respondiente_nombre'))

    # Grado/cargo y unidad
    _put(page, 103, 186, _val(data, 'respondiente_cargo'))
    _put(page, 95,  203, _val(data, 'respondiente_unidad'))

    # Sección 3 - fechas/horas (col izquierda: conocimiento, col derecha: arribo)
    _put(page, 130, 385, _val(data, 'fecha_conocimiento'))
    _put(page, 130, 412, _val(data, 'hora_conocimiento'))
    _put(page, 393, 385, _val(data, 'fecha_arribo'))
    _put(page, 393, 412, _val(data, 'hora_arribo'))

    # Sección 4 - Ubicación
    _put(page, 118, 504, _val(data, 'calle'))
    _put(page, 80,  521, _val(data, 'no_exterior'))
    _put(page, 104, 538, _val(data, 'colonia'))
    _put(page, 72,  556, _val(data, 'municipio'))
    _put(page, 105, 574, _val(data, 'entidad_federativa'))
    _put(page, 84,  590, _val(data, 'referencias'))

    # Coordenadas GPS
    coords = _val(data, 'coordenadas')
    if coords and ',' in coords:
        parts = coords.split(',', 1)
        _put(page, 65,  622, parts[0].strip(), fontsize=FS_SM)
        _put(page, 290, 622, parts[1].strip(), fontsize=FS_SM)


def _fill_page4(page, data):
    """Sección 5: Narrativa de los hechos."""
    narrativa = _val(data, 'narrativa_hechos')
    if narrativa:
        _insert_wrapped(page, narrativa, x=37, y=90, fontsize=FS, max_width=520, line_height=12)


def _fill_page5_6_7(doc, data):
    """Anexo A: Detención(es) - páginas 5 y 6 (índices 4 y 5)."""
    if not _val(data, 'detenido_primer_apellido'):
        return

    p = doc[4]  # Página 5

    # Fecha y hora detención
    _put(p, 80,  120, _val(data, 'detenido_fecha_detencion'))
    _put(p, 200, 120, _val(data, 'detenido_hora_detencion'))

    # Nombres en columnas
    _put(p, 97,  142, _val(data, 'detenido_primer_apellido'))
    _put(p, 266, 142, _val(data, 'detenido_segundo_apellido'))
    _put(p, 430, 142, _val(data, 'detenido_nombre'))

    # Apodo
    _put(p, 90,  158, _val(data, 'detenido_apodo'))

    # Fecha nacimiento y edad
    _put(p, 115, 208, _val(data, 'detenido_fecha_nacimiento'))
    _put(p, 370, 208, _val(data, 'detenido_edad', ''))

    # No. identificación
    _put(p, 112, 254, _val(data, 'detenido_identificacion_num', ''))

    # Domicilio
    _put(p, 118, 286, _val(data, 'detenido_calle'))
    _put(p, 82,  303, _val(data, 'detenido_no_exterior', 'S/N'))
    _put(p, 104, 320, _val(data, 'detenido_colonia'))
    _put(p, 72,  337, _val(data, 'detenido_municipio', 'Culiacán'))
    _put(p, 105, 354, _val(data, 'detenido_entidad', 'Sinaloa'))

    # Descripción física (área de texto libre)
    _insert_wrapped(p, _val(data, 'detenido_descripcion'), x=37, y=395, fontsize=FS_SM, max_width=520)

    # Familiar
    _put(p, 97,  590, _val(data, 'familiar_primer_apellido', ''))
    _put(p, 266, 590, _val(data, 'familiar_segundo_apellido', ''))
    _put(p, 430, 590, _val(data, 'familiar_nombre'))
    _put(p, 80,  608, _val(data, 'familiar_telefono'))


def _fill_page9(page, data):
    """Anexo C: Inspección de Vehículo."""
    if not _val(data, 'vehiculo_marca'):
        return

    _put(page, 80,  120, _val(data, 'vehiculo_fecha_inspeccion', ''))
    _put(page, 200, 120, _val(data, 'vehiculo_hora_inspeccion', ''))

    _put(page, 220, 173, _val(data, 'vehiculo_marca'))
    _put(page, 220, 173, '')  # submarca va después
    _put_after(page, 'Submarca:', _val(data, 'vehiculo_submarca'), dx=5)
    _put(page, 380, 173, _val(data, 'vehiculo_modelo', ''))
    _put(page, 505, 173, _val(data, 'vehiculo_color'))

    _put(page, 112, 222, _val(data, 'vehiculo_placa'))
    _put(page, 332, 222, _val(data, 'vehiculo_serie', ''))

    _insert_wrapped(page, _val(data, 'vehiculo_observaciones', 'Sin observaciones.'),
                    x=37, y=284, fontsize=FS_SM, max_width=520)
    _insert_wrapped(page, _val(data, 'vehiculo_destino'),
                    x=37, y=343, fontsize=FS_SM, max_width=520)


def generate_iph_pdf(form_data, user_data, output_path):
    if not PYMUPDF_AVAILABLE:
        raise ImportError('PyMuPDF no está instalado. Ejecuta: pip install pymupdf')

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f'Plantilla no encontrada: {TEMPLATE_PATH}')

    doc = fitz.open(TEMPLATE_PATH)

    _fill_page1(doc[0], form_data)
    _fill_page2(doc[1], form_data)
    _fill_page4(doc[3], form_data)

    anexos = form_data.get('anexos_usados', [])
    if 'Anexo A - Detención(es)' in anexos:
        _fill_page5_6_7(doc, form_data)
    if 'Anexo C - Inspección de vehículo' in anexos:
        _fill_page9(doc[8], form_data)

    doc.save(output_path)
    doc.close()
    return output_path
