from flask import Flask, request, jsonify, send_file
from io import BytesIO
import sys
import tempfile
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

app = Flask(__name__)
CORS(app)

import secrets as _secrets

_SECRET_KEY     = os.environ.get('SECRET_KEY')
_JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

if not _SECRET_KEY:
    _SECRET_KEY = _secrets.token_hex(32)

if not _JWT_SECRET_KEY:
    _JWT_SECRET_KEY = _secrets.token_hex(32)

app.config['SECRET_KEY'] = _SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iph_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = _JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

db = SQLAlchemy(app)
jwt = JWTManager(app)


class Report(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expediente  = db.Column(db.String(100), default='')
    fecha       = db.Column(db.String(20),  default='')
    detenido    = db.Column(db.String(200), default='')
    created_at  = db.Column(db.String(30),  default='')
    form_json   = db.Column(db.Text,        default='{}')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    primer_apellido = db.Column(db.String(100), default='')
    segundo_apellido = db.Column(db.String(100), default='')
    nombre = db.Column(db.String(100), default='')
    adscripcion = db.Column(db.String(200), default='')
    cargo_grado = db.Column(db.String(100), default='')
    institucion = db.Column(db.String(100), default='Policía Municipal')
    no_placa = db.Column(db.String(50), default='')


def user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'primer_apellido': user.primer_apellido,
        'segundo_apellido': user.segundo_apellido,
        'nombre': user.nombre,
        'adscripcion': user.adscripcion,
        'cargo_grado': user.cargo_grado,
        'institucion': user.institucion,
        'no_placa': user.no_placa,
    }


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Servidor IPH activo'})


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'El usuario ya existe'}), 400
    user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        primer_apellido=data.get('primer_apellido', ''),
        segundo_apellido=data.get('segundo_apellido', ''),
        nombre=data.get('nombre', ''),
        adscripcion=data.get('adscripcion', ''),
        cargo_grado=data.get('cargo_grado', ''),
        institucion=data.get('institucion', 'Policía Municipal'),
        no_placa=data.get('no_placa', ''),
    )
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=user.id)
    return jsonify({'token': token, 'user': user_to_dict(user)}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not check_password_hash(user.password_hash, data.get('password', '')):
        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
    token = create_access_token(identity=user.id)
    return jsonify({'token': token, 'user': user_to_dict(user)})


@app.route('/api/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(user_to_dict(user))


@app.route('/api/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    data = request.get_json()
    fields = ['primer_apellido', 'segundo_apellido', 'nombre',
              'adscripcion', 'cargo_grado', 'institucion', 'no_placa']
    for field in fields:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify(user_to_dict(user))


@app.route('/api/reports', methods=['POST'])
@jwt_required()
def save_report():
    import json as _json
    from datetime import datetime as _dt
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    form = data.get('form_data', {})
    detenido = ' '.join(filter(None, [
        form.get('detenido_nombre', ''),
        form.get('detenido_primer_apellido', ''),
        form.get('detenido_segundo_apellido', ''),
    ])).strip() or 'Sin detenido'
    report = Report(
        user_id    = user_id,
        expediente = form.get('no_expediente', 'N/A'),
        fecha      = form.get('fecha_puesta_disposicion', ''),
        detenido   = detenido,
        created_at = _dt.now().strftime('%d/%m/%Y %H:%M'),
        form_json  = _json.dumps(form, ensure_ascii=False),
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'id': report.id, 'message': 'Reporte guardado'}), 201


@app.route('/api/reports', methods=['GET'])
@jwt_required()
def list_reports():
    import json as _json
    user_id = get_jwt_identity()
    reports = Report.query.filter_by(user_id=user_id).order_by(Report.id.desc()).all()
    return jsonify([{
        'id':         r.id,
        'expediente': r.expediente,
        'fecha':      r.fecha,
        'detenido':   r.detenido,
        'created_at': r.created_at,
    } for r in reports])


@app.route('/api/reports/<int:report_id>/pdf', methods=['GET'])
@jwt_required()
def report_pdf(report_id):
    import json as _json
    user_id = get_jwt_identity()
    report = Report.query.filter_by(id=report_id, user_id=user_id).first()
    if not report:
        return jsonify({'error': 'Reporte no encontrado'}), 404

    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mobile_dir = os.path.join(proj_root, 'mobile')
    if mobile_dir not in sys.path:
        sys.path.insert(0, mobile_dir)

    try:
        from utils.pdf_generator import generate_iph_pdf
    except ImportError as e:
        return jsonify({'error': f'pdf_generator no disponible: {e}'}), 500

    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    tmp_path = tmp.name
    tmp.close()
    try:
        form_data = _json.loads(report.form_json)
        generate_iph_pdf(form_data, {}, tmp_path)
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        filename = f'IPH_{report.expediente}_{report.id}.pdf'
        return send_file(BytesIO(pdf_bytes), mimetype='application/pdf',
                         as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.route('/api/generate_pdf', methods=['POST'])
@jwt_required()
def generate_pdf_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    form_data = data.get('form_data', {})
    user_data = data.get('user_data', {})

    # Importar pdf_generator desde mobile/utils (mismo repo)
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mobile_dir = os.path.join(proj_root, 'mobile')
    if mobile_dir not in sys.path:
        sys.path.insert(0, mobile_dir)

    try:
        from utils.pdf_generator import generate_iph_pdf
    except ImportError as e:
        return jsonify({'error': f'pdf_generator no disponible: {e}'}), 500

    tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    tmp_path = tmp.name
    tmp.close()

    try:
        generate_iph_pdf(form_data, user_data, tmp_path)
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        filename = f'IPH_{user_data.get("no_placa", "reporte")}.pdf'
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos lista.")
    print("Servidor iniciado en http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
