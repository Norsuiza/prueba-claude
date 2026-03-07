from flask import Flask, request, jsonify
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

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-iph-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iph_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-iph-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

db = SQLAlchemy(app)
jwt = JWTManager(app)


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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos lista.")
    print("Servidor iniciado en http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
