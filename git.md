# Guía de Git + GitHub (Windows)

Guía práctica para trabajar con Git y GitHub en esta máquina. Comandos, flujo diario y solución de problemas (troubleshooting) basados en casos reales ya resueltos.

---

## 1. Configuración inicial (una sola vez)

Identidad global (se aplica a todos los repos):

```powershell
git config --global user.name "jorgeloy0276"
git config --global user.email "jorgeloy0276@gmail.com"
```

Editor y salto de línea (opcional pero recomendado en Windows):

```powershell
git config --global core.editor "code --wait"
git config --global core.autocrlf true
```

> No hace falta repetir esto por cada proyecto: es configuración global.

---

## 2. Autenticación por SSH (GitHub)

Las llaves SSH **son por máquina y por cuenta de GitHub, no por repositorio**. Se configuran una sola vez y sirven para todos los proyectos.

### 2.1 Generar una llave (si no existe)

```powershell
ssh-keygen -t ed25519 -C "jorgeloy0276@gmail.com" -f "$env:USERPROFILE\.ssh\key_jorgeloy0276"
```

Crea dos archivos en `C:\Users\Jorge Eloy\.ssh\`:
- `key_jorgeloy0276` → llave **privada** (no se comparte jamás).
- `key_jorgeloy0276.pub` → llave **pública** (se registra en GitHub).

> Si pones una passphrase, la llave queda protegida con contraseña. Eso es lo recomendado, pero exige el paso 2.3 para no sufrir prompts.

### 2.2 Registrar la llave pública en GitHub

1. Copia el contenido de la llave pública:

   ```powershell
   Get-Content "$env:USERPROFILE\.ssh\key_jorgeloy0276.pub"
   ```

2. En GitHub: **Settings → SSH and GPG keys → New SSH key**. Pega el contenido (empieza con `ssh-ed25519 AAAA...`).

### 2.3 Archivo de configuración `~/.ssh/config`

La llave tiene un nombre no estándar (`key_jorgeloy0276`). Sin configuración, SSH busca llaves con nombres por defecto (`id_rsa`, `id_ed25519`) y **nunca ofrecerá la tuya**. Crea/edita `C:\Users\Jorge Eloy\.ssh\config`:

```
Host github.com
HostName github.com
User git
IdentityFile ~/.ssh/key_jorgeloy0276
IdentitiesOnly yes
```

### 2.4 Agente SSH (para llaves con passphrase)

El "OpenSSH Authentication Agent" de Windows guarda la llave desbloqueada para no escribir la passphrase cada vez.

1. Habilita el servicio (una vez, como administrador):

   ```powershell
   Get-Service ssh-agent | Set-Service -StartupType Automatic
   Start-Service ssh-agent
   ```

2. Carga la llave en el agente (tras cada reinicio):

   ```powershell
   ssh-add "$env:USERPROFILE\.ssh\key_jorgeloy0276"
   ```

3. Verifica qué llaves tiene cargadas el agente:

   ```powershell
   ssh-add -l
   ```

### 2.5 Decirle a Git que use el OpenSSH de Windows

**Problema real:** Git para Windows trae su propio `ssh.exe` (MSYS), que no habla con el agente de Windows. Eso causa `Permission denied (publickey)` intermitente. Solución (una vez):

```powershell
git config --global core.sshCommand "C:/Windows/System32/OpenSSH/ssh.exe"
```

> Ojo: usar **barras normales** (`/`), no `\`. Git interpreta el valor como comando de shell y con `\` rompe la ruta (`C:WindowsSystem32...`).

### 2.6 Verificar la conexión

```powershell
ssh -T git@github.com
# Debe responder: Hi jorgeloy0276! You've successfully authenticated...
```

El exit code `1` es normal en este comando; lo importante es que aparezca tu usuario.

---

## 3. Flujo diario (subir cambios)

```powershell
git status                        # ver qué cambió
git diff                          # ver cambios sin agregar (sin stage)
git add <archivo>                 # agregar un archivo al stage
git add .                         # agregar todos los cambios
git commit -m "Descripción del cambio"
git push                          # subir commits locales al remoto
```

Flujo completo en una sola tanda:

```powershell
git status
git add .
git commit -m "Mensaje del cambio"
git push
```

Ver historial:

```powershell
git log --oneline --graph        # historial compacto con grafo
git log --oneline -5             # últimos 5 commits
```

Traer cambios del remoto:

```powershell
git pull                          # fetch + merge (por defecto)
git pull --rebase                 # fetch + rebase (historial lineal)
```

---

## 4. Crear un proyecto nuevo y subirlo a GitHub

El SSH ya está configurado (sección 2), así que **no se repite nada**. Solo:

1. En GitHub: **New repository** (mismo nombre que tu carpeta). **No** marques "Add a README" si ya tienes commits locales.
2. En tu proyecto:

   ```powershell
   git init
   git add .
   git commit -m "Commit inicial"
   git remote add origin git@github.com:jorgeloy0276/<repo>.git
   git push -u origin main
   ```

3. Verificar:

   ```powershell
   git ls-remote origin
   ```

> Si ya tenías el repo creado en GitHub **con** un README inicial, ver la sección 7.2 (non-fast-forward).

---

## 5. Ramas

```powershell
git branch                          # listar ramas
git branch <nombre>                 # crear rama
git checkout <nombre>               # cambiar de rama
git checkout -b <nombre>            # crear y cambiar en un paso
git merge <nombre>                  # fusionar otra rama en la actual
git branch -d <nombre>              # borrar rama local
git push origin <nombre>            # subir una rama nueva
git push origin --delete <nombre>   # borrar rama en el remoto
```

---

## 6. Deshacer cambios

```powershell
git restore <archivo>               # descartar cambios SIN commitear (working tree)
git restore --staged <archivo>      # sacar del stage (lo mantiene modificado)
git reset --soft HEAD~1             # deshacer el último commit, deja cambios en stage
git reset --hard HEAD~1             # deshacer el último commit y perder sus cambios
git commit --amend -m "Nuevo msg"   # corregir el mensaje del último commit
```

> `reset --hard` **borra** trabajo. Úsalo solo si estás seguro.

---

## 7. Troubleshooting (problemas reales y su solución)

### 7.1 `git@github.com: Permission denied (publickey)`

**Síntoma:** el push falla aunque "otros proyectos funcionan".

**Causas posibles y solución (en orden):**

1. **La llave no está registrada en GitHub.** Verifica con `ssh -T git@github.com`. Si GitHub la acepta pero luego dice `Permission denied`, la pública no está en tu cuenta → añadirla (sección 2.2).
2. **No hay `~/.ssh/config`** y la llave tiene nombre no estándar → crearlo (sección 2.3).
3. **La llave tiene passphrase y el agente no la tiene cargada.** Git para Windows (ssh MSYS) no puede pedirla sin terminal interactivo. Log típico:

   ```
   debug1: read_passphrase: can't open /dev/tty: No such device or address
   debug2: no passphrase given, try next key
   ```

   Solución: cargar la llave en el agente (`ssh-add`) y fijar `core.sshCommand` al OpenSSH nativo (secciones 2.4 y 2.5).

4. **Hay llaves viejas/duplicadas en el agente.** Revisar con `ssh-add -l` y limpiar: `ssh-add -d` (quita una) o `ssh-add -D` (quita todas).

Diagnóstico detallado:

```powershell
ssh -vvT git@github.com
```

### 7.2 `! [rejected] main -> main (non-fast-forward)`

**Síntoma:** el push falla porque el remoto tiene commits que tu local no tiene. Pasa típicamente cuando el repo en GitHub se creó con un README inicial, o se subieron archivos por la web ("Add files via upload").

**Diagnóstico (antes de tocar nada):**

```powershell
git ls-remote origin                # ver a qué apunta el remoto
git log --oneline --all             # comparar historias locales y remotas
```

**Opción A — Forzar push (reemplaza el historial remoto con el local):**

Solo si el remoto no tiene nada que quieras conservar (proyecto nuevo).

```powershell
git push --force-with-lease origin main
```

> `--force-with-lease` es más seguro que `-f`: falla si el remoto cambió mientras tanto.

**Opción B — Integrar los cambios del remoto (conserva su historial):**

```powershell
git pull --rebase origin main
git push
```

### 7.3 `fatal: remote origin already exists`

Ya existe un remoto llamado `origin`. Verlo / cambiarlo:

```powershell
git remote -v                                   # ver remotos
git remote set-url origin git@github.com:usuario/repo.git
git remote remove origin                        # borrar y volver a añadir
```

### 7.4 Subí archivos que no debía (`.pyc`, credenciales, `.env`)

Quitar del **tracking** (los archivos se quedan en disco, solo salen de Git):

```powershell
git rm -r --cached __pycache__
git rm --cached Variables_env.txt
git rm --cached env
git add .gitignore
git commit -m "Quitar archivos de cache y credenciales del repositorio"
git push
```

Y evitar que vuelvan, añadiendo al `.gitignore`:

```
__pycache__/
*.py[cod]
Variables_env.txt
env
.env
```

> Si ya habías subido credenciales a un repo **público**, además de quitarlas del tracking debes rotarlas/cambiarlas en el servicio afectado: Git conserva el historial.

### 7.5 `HEAD is now at ...` / estado "detached HEAD"

Estás en un commit suelto, no en una rama. Vuelve a tu rama:

```powershell
git switch main
```

### 7.6 `The following paths are ignored by one of your .gitignore files`

`git add` rechaza archivos ignorados. Forzar (poco recomendado) o revisar `.gitignore`:

```powershell
git add -f archivo.txt    # forzar
```

### 7.7 `Git is not recognized` / `no se reconoce el término 'git'`

Git no está en el PATH. Reinstalar Git for Windows o añadir su carpeta `cmd` al PATH.

---

## 8. Referencia rápida de comandos

| Comando | Qué hace |
|---|---|
| `git status` | Estado de la copia de trabajo |
| `git add .` | Agregar todos los cambios al stage |
| `git commit -m "msg"` | Crear commit con los cambios en stage |
| `git push` | Subir commits al remoto |
| `git pull` | Traer cambios del remoto y fusionar |
| `git log --oneline --graph` | Historial compacto |
| `git branch` | Listar ramas |
| `git checkout -b <r>` | Crear y saltar a una rama |
| `git merge <r>` | Fusionar rama en la actual |
| `git remote -v` | Ver remotos configurados |
| `git ls-remote origin` | Ver a qué commit apunta el remoto |
| `ssh -T git@github.com` | Probar autenticación SSH con GitHub |
| `ssh-add -l` | Listar llaves cargadas en el agente |

---

## Resumen de "no hay que repetir nada"

- Identidad de git → global, una vez.
- Llaves SSH + `~/.ssh/config` → por máquina, una vez.
- Agente SSH + `core.sshCommand` → una vez (persiste entre proyectos).
- Por cada proyecto nuevo solo: `git init`, `git add .`, `git commit`, `git remote add origin ...`, `git push -u origin main`.
