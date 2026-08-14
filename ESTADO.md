## ESTADO DEL PROYECTO (log de verificaciones)

### 2026-08-14 00:50 — correo Brevo: migración a API REST (revisado con code-verifier)

**NUEVO / LISTO (verificado)**

- **Notificaciones por email migradas de flask-mail/Gmail a la API REST de Brevo** (`brevo-python==5.0.2`, SDK v5 generado por Fern).
  - `send_notification()` (crear/editar/borrar tarea) y `send_email()` (botón de prueba, `task_list.html:98`) usan `client.transactional_emails.send_transac_email()` (`task_controller.py:14-47, 67-104`).
  - El SDK inyecta la clave como header `api-key` (vía `Brevo(api_key=...)` → `BaseClientWrapper.get_headers`); la API REST **no** acepta `x-api-key` ni la clave SMTP.
- **API key REST válida en `.env`**: `BREVO_API_KEY` con prefijo `xkeysib-...`. Verificada contra `GET /account` (org "Krypton Logic", `kryptonlogicpty@gmail.com`, plan free 300 créditos/día). La clave previa `xsmtpsib-...` era la contraseña del relay SMTP y devolvía `401 Key not found`.
- **Sender verificado en Brevo**: `BREVO_SENDER_EMAIL=kryptonlogicpty@gmail.com`, `BREVO_SENDER_NAME=Krypton Logic` — es el único sender de la cuenta (id=1, `GET /senders`). `a8966f001@smtp-brevo.com` es solo el login SMTP y NO sirve como sender para la API REST.
- **Flask-mail fuera del flujo de notificaciones**: el bloque Gmail quedó comentado en `send_notification` (`task_controller.py:50-65`).
- `send_email()` ahora redirige a `index` tras el envío (antes devolvía texto plano).
- **Los 4 procesos Flask que corrían `app.py` con la key vieja en memoria fueron detenidos** (hoy no hay proceso activo). `config.py:4` hace `load_dotenv()` solo al arrancar, así que un `.env` editado no se refleja en procesos ya corriendo — arrancar de nuevo para cargar la key correcta.

**PENDIENTE / A TENER EN CUENTA**

Crítico (seguridad):
- `task_controller.py:17,71` — `print(api_key)` imprime la API key de Brevo en consola/logs. No loguear secretos; eliminarlo o pasar a `logging` sin el valor.
- `task_controller.py:28-36` — El HTML del email interpola `{task.title}`, `{task.description}`, `{task.status}` con f-strings sin escapar → XSS en el correo del destinatario. Usar `html.escape()` o plantilla con autoescape.

Alto (robustez y bugs):
- `task_controller.py:182-184` — `delete_task` llama `send_notification(task_id, "Eliminada")` pasando el **id** (string `TSK-...`), pero la función accede a `task.id/title/status/description` → `AttributeError` tragado por el `try/except` (el correo de borrado nunca se envía). Pasar el objeto `Task` o capturar los datos antes de borrar.
- `task_controller.py:46-47,101-104` — Errores de envío solo se imprimen (`print`) y el flujo sigue igual (éxito y error redirigen a `index`): la UX no informa si el correo se envió y no hay registro. Usar `logging.exception()` y flash con resultado.
- `task_controller.py:14-47` — `send_notification()` sigue siendo síncrono tras el commit; si la API de Brevo falla tarda el timeout del SDK (60 s por defecto) antes de responder.
- `config.py:4` — `load_dotenv()` depende del CWD; usar ruta absoluta desde `BASE_DIR`. Recordar que los cambios de `.env` requieren reiniciar el proceso.

Medio:
- `config.py:26-39` — Configuración de mail mezclada: el bloque "Gmail" se sobreescribe con el "Brevo" (`MAIL_SERVER` queda `smtp.brevo.com`, puerto 587, TLS, `MAIL_PASSWORD` comentado). flask-mail ya no se usa para notificaciones pero `app/__init__.py` aún lo inicializa; conviene limpiar.
- `.env` — Hay espacios alrededor de `=` en `BREVO_API_KEY = ...`; dotenv los tolera, pero por convención quitarlos. La key de SMTP (`xsmtpsib-...`) quedó reemplazada por la REST (`xkeysib-...`); no reintroducir la antigua como API key.
- `AGENTS.md:23` queda desactualizado — ya no se envía a la dirección Gmail hardcodeada vía `send_notification()` (ahora va a `jorgeloy0276@gmail.com` por la API de Brevo).

---

### 2026-08-12 12:35 — verificación inicial (revisado con code-verifier)

**NUEVO / LISTO (verificado, revisado con code-verifier)**

- **SQL 100 % parametrizado**: `save()`, `get_by_id()` usan `%s` con tuplas en `app/models/task.py` — sin inyección SQL pese a no usar ORM.
- **Sin XSS en la web**: Jinja2 autoescapa `{{ }}` en todas las plantillas (título, descripción, búsqueda, filtros).
- **Invariante de estados respetada en la UI**: el `<select>` de `task_edit.html:33-39` y el matcheo en `task_list.html` usan exactamente los 5 valores ENUM; `summary` cuenta sobre `all_tasks`, por lo que el conteo es correcto aunque haya filtro activo.
- **Separación MVC limpia** con app factory `create_app()` en `app/__init__.py`; filtros de listado hechos en memoria, no concatenados a SQL.
- **Flujo feliz verificado**: crear/editar/detalle/listar funcionan con la DB local (localhost/root/task_manager) y Tailwind v4 vía CDN.

**PENDIENTE / A TENER EN CUENTA**

Crítico (seguridad):
- `run.py:6` — `app.run(debug=True, host='0.0.0.0', port=8082)` expone el debugger interactivo de Werkzeug a la red; cualquier excepción filtra el traceback completo. En despliegue usar `debug=False` y host `127.0.0.1`.
- `env`, `static/.env`, `.env` — credenciales reales (MySQL PythonAnywhere, app-password Gmail, SECRET_KEY) en texto plano dentro del workspace. No commitear, no compartir; rotar si se filtra.

Alto (robustez y bugs):
- `task.py:23-59` — Ningún acceso a MySQL tiene `try/except` ni cierre en `finally`: un fallo de DB → 500 con traceback y conexiones/cursors abiertos.
- `task_controller.py:13-21` — `title`, `description` y `status` se interpolan con f-string en el HTML del email sin escapar → XSS en el correo del destinatario. Usar `html.escape()` o plantillas con autoescape.
- `task_controller.py:67-69` — `closed_at` nunca se limpia al reabrir una tarea (status vuelve a `creada`/`en proceso`/`en espera`) → viola la invariante de dominio. Al guardar, si el status no es de cierre, asignar `closed_at = None`.
- `task_controller.py:60-78` — `Task.get_by_id()` puede devolver `None` (ID inexistente) → 500 en POST de edición, página vacía en detalle. Devolver `abort(404)`.
- `task_controller.py:56,70-72` — Email síncrono tras el commit sin `try/except`: si SMTP falla el usuario ve 500 aunque la tarea ya quedó guardada; el reintento duplica tareas. Capturar con `logging.exception()` o enviar en segundo plano.
- `task_add.html` / `task_edit.html` — Endpoints de escritura sin CSRF ni autenticación: cualquiera que alcance el servidor puede crear/editar tareas y disparar los correos.

Medio:
- `task.py:27-29` — ID `TSK-{count:04d}` desde `COUNT(*)`: race-prone entre requests concurrentes y colisiona si se borran filas → PrimaryKey Duplicate 500. Usar `MAX(id)` + reintento o AUTO_INCREMENT/UUID.
- `base.html:10` — `css/custom.css` no existe en `app/static/css/` → 404; el `custom.css` real está en la raíz `static/` (que Flask no sirve) y es un archivo fuente de Tailwind v4, no CSS compilado. La UI funciona solo gracias al CDN.
- `task_controller.py:48` — `search_query` no se pasa a `render_template`: el input de búsqueda queda vacío tras buscar y el mensaje «Mostrando todas las tareas» es incorrecto cuando hay búsqueda.
- `task_controller.py:63-66` — `status` y `title` sin validar contra el dominio: un status fuera del ENUM o título >100 chars → `DataError` → 500. Validar contra la lista canónica de estados.
- `task_controller.py:19` — El email de tarea nueva muestra `None` en «Fecha Creación» (`created_at` nunca se re-lee tras el INSERT).
- `config.py:11` — `SECRET_KEY` débil con fallback `'default'`; hoy no hay sesiones, pero comprometería cualquier uso futuro de session/CSRF.
- `env:1` — La clave `MYSQL_HOST` lleva un espacio inicial `" MYSQL_HOST=..."`; además el archivo no se carga en ningún lado.
- `task.py:15-21` — Conexiones sin pool y sin `charset` explícito.

Bajo:
- `task.py:45` — `get_all()` sin `ORDER BY` (orden físico de la tabla).
- `app/__init__.py:20-23` — No hay ruta `/` (el home responde 404); conviene un redirect a `/tasks`.
- `base.html:13` — Tailwind vía CDN sin SRI ni caché local.
- `config.py:4` — `load_dotenv()` depende del CWD; usar ruta absoluta desde el basedir.
- `task_controller.py:61-65` — `append_description` agrega un bloque de timestamp aunque la descripción nueva esté vacía.
- `task_list.html:89` — Clase CSS residual `x` (`gap-2 x space-x-4`).

---

*Formato: agregar nuevas entradas al inicio con fecha y hora (`### YYYY-MM-DD HH:MM — descripción`) y mover lo resuelto a la sección correspondiente.*
