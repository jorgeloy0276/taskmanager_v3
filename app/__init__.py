from flask import Flask
from flask_mail import Mail
from config import Config

# Instancia global de mail
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializamos mail con la app
    mail.init_app(app)

    # Importamos los controladores después de inicializar la app
    from app.controllers.task_controller import index, add_task, edit_task, task_detail

    # Registramos las rutas
    app.route('/')(index)
    app.route('/tasks')(index)
    app.route('/add', methods=['GET', 'POST'])(add_task)
    app.route('/edit/<task_id>', methods=['GET', 'POST'])(edit_task)
    app.route('/detail/<task_id>')(task_detail)

    return app