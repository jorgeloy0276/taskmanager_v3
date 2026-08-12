## ESTADO DEL PROYECTO (log de verificaciones)

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
