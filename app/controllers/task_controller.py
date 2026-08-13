from flask import render_template, request, redirect, url_for
from app.models.task import Task
from flask_mail import Message
from config import Config
from app import mail  # Importamos mail desde __init__.py
import datetime

def send_notification(task, action):
    msg = Message(
        subject=f"Tarea {action}: {task.id}",
        sender=Config.MAIL_USERNAME,
        recipients=['jorgeloy0276@gmail.com'],
        html=f"""
        <h2>Tarea {action}</h2>
        <p><strong>ID:</strong> {task.id}</p>
        <p><strong>Título:</strong> {task.title}</p>
        <p><strong>Estado:</strong> {task.status}</p>
        <p><strong>Descripción:</strong><pre>{task.description}</pre></p>
        <p><strong>Fecha Creación:</strong> {task.created_at}</p>
        <p><strong>Fecha Cierre:</strong> {task.closed_at or 'N/A'}</p>
        """
    )
    mail.send(msg)

def send_email():
   print("Enviando correo...")
  
   msg = Message(
       subject="Correo de prueba",
       sender="admin@example.com",
       recipients=['jorgeloy0276@gmail.com'],
       html="Esto es un correo de prueba."
   )

   try:
    mail.send(msg)
    print("Correo enviado correctamente.")
   except Exception as e:
       print(f"Error al enviar el correo: {str(e)}")
       return "Error al enviar el correo", 500

   return "Correo enviado correctamente", 200
   

def index():
    # Obtenemos el filtro de estado y la búsqueda desde los parámetros de la URL
    status_filter = request.args.get('status', None)
    search_query = request.args.get('search', None)

    # Obtenemos todas las tareas
    all_tasks = Task.get_all()

    # Filtramos las tareas si hay un filtro de estado
    if status_filter:
        tasks = [task for task in all_tasks if task.status == status_filter]
    else:
        tasks = all_tasks

    # Filtramos por búsqueda si aplica
    if search_query:
        tasks = [task for task in tasks if search_query.lower() in task.title.lower()]

    # Calculamos el resumen
    summary = {'creada': 0, 'en proceso': 0, 'en espera': 0, 'cancelado': 0, 'terminado': 0}
    for task in all_tasks:  # Usamos all_tasks para el resumen, no las filtradas
        summary[task.status] += 1

    return render_template('task_list.html', tasks=tasks, summary=summary, status_filter=status_filter)

def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        task = Task(None, title, None, description)
        task.save()
        send_notification(task, "Creada")
        return redirect(url_for('index'))
    return render_template('task_add.html')

def edit_task(task_id):
    task = Task.get_by_id(task_id)
    if request.method == 'POST':
        task.title = request.form['title']
        new_desc = request.form['description']
        task.append_description(new_desc)
        task.status = request.form['status']
        if task.status in ['cancelado', 'terminado']:
          
            task.closed_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task.save()
        str_status = task.status
        send_notification(task,str_status)
        return redirect(url_for('index'))
    return render_template('task_edit.html', task=task)

def task_detail(task_id):
    task = Task.get_by_id(task_id)
    return render_template('task_detail.html', task=task)


def delete_task(task_id):
    Task.delete(task_id)
    send_notification(task_id, "Eliminada")
    return redirect(url_for('index'))