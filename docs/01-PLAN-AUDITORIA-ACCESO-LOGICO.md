# Plan de ejecución v3 — Auditoría técnica de Control de Acceso Lógico sobre AppNotify
> Parcial II · NTC-ISO/IEC 27001:2022 · 9 controles · exposición de 60 minutos
> Base: `docs/00-TRANSCRIPCION-ORGANIZADA.md` · v3 incorpora el giro metodológico de **prueba de fuego**

---

## 0. Correcciones de la v1 (leídas antes de continuar)

| # | Error de la v1 | Corrección aplicada |
|---|---|---|
| 1 | A.5.16 y A.8.2 estaban redactados como desviaciones (= NC según la profesora), no como ineficiencias | Los dos controles **cumplen 100 %** de su criterio; la ineficiencia se traslada al mecanismo de **mantenimiento** (barrido manual, ticket manual). Ver §2 |
| 2 | Población de A.8.4 = "2 repositorios" | Hay **1 solo repositorio** (`frontend/` es un directorio, no un repo). La población se redefine como **105 archivos versionados**, muestra 12 |
| 3 | CORS con `allow_credentials=True` presentado como brecha autonomous | No se sostiene solo: con token Bearer el navegador no filtra la lectura. Se corrige CORS en la preparación; queda como **endurecimiento**, no como hallazgo |
| 4 | "Mongo local sin TLS" contradecía la evidencia TLS de A.5.17 | Topología decided: `mongod` en Docker **con TLS y CA propia**; el defecto es `tlsAllowInvalidCertificates=True`. Tiempo máximo 30 min, es evidencia de apoyo, no la base principal |
| 5 | `localStorage` podía contaminar A.8.5 y hundir un CONFORME | **Partición explícita de alcance**: A.5.17 = "protección de la información de autenticación" (incluye almacenamiento del secreto de sesión); A.8.5 = "método de autenticación" (MFA, bloqueo, emisión, expiración, revocación). Pivot predefinido en §10 |
| 6 | Faltaba el ciclo PHVA para 7 de 9 controles | Se agrega **Ficha PHVA por control** como entregable (§5, F1) |
| 7 | No existía tabla de debilidades originales (arregladas / reportadas / retenidas) | Se agrega §6 |
| 8 | Secretos del laboratorio en un repositorio **público** | Política de secretos: se generan en runtime, `.env` gitignored, `.env.example` versionado, evidencia redactada, `gitleaks` se corre en F0/F1 y no en F6 |
| 9 | Sesión JWT con expiración y revocación | Sesión **opaque en Mongo**: revocación = borrar el documento; sin crypto, sin dependencia nueva, sin secreto JWT que proteger |
| 10 | Poblaciones inconsistentes entre controles | **Una sola tabla de laboratorio** (§3) de la que se derivan todas las poblaciones y muestras |
| 11 | `backend/Dockerfile` con `--workers 4` → 4 planificadores | En el laboratorio se usa `--workers 1` |
| 12 | Fecha 27 de octubre asumida | Fecha oficial: **jueves 29**. El 27 es el casoDfavorable si el acceso lógico expone primero |
| 13 | *(v3)* Las verificaciones eran **revisiones** de configuración, no **pruebas** de resistencia | **Giro metodológico**: cada control se demuestra con una **prueba de fuego** — un intento real de eludirlo, ejecutado en vivo. Ver §1 bis, §2.1 y §2.4 |
| 14 | *(v3)* Los scripts solo reportaban; no ejecutaban el ataque | Los 7 scripts `pf_*.py` **ejecutan el ataque** y emiten un veredicto por caso. El reporte *es* la evidencia de la columna S |
| 15 | *(v3)* No había forma de demostrar que un control **aguanta bajo operación real** | **Prueba con dos actores concurrentes** (§2.4): el análogo del "guardia distraído" — usuarios legítimos operando mientras el atacante actúa |

---

## 1. Objetivo, entregables y la regla que gobierna todo

**Objetivo.** Auditar el control de acceso lógico de AppNotify (RemindSender) contra 9 controles de NTC-ISO/IEC 27001:2022 por muestreo, con hallazgos **conforme / no conforme / oportunidad de mejora**, y defenderlo en 60 minutos con evidencia objetiva, verificable y reproducible.

**Entregables del parcial:**

| # | Entregable | Dónde |
|---|---|---|
| E1 | **Registro de lista de chequeo diligenciada** — 18 columnas, 16-20 filas | `docs/2. Lista Chequeo.xlsx` |
| E2 | **Presentación y sustentación práctica** — modalidad C (mixta) | Exposición + evidencias |

**Entregables de soporte** (obligatorios para sostener E1, no son notas extra): matriz de riesgos con trazabilidad · normas y políticas propias (criterios de aceptación) · **fichas PHVA por control** · índice de evidencias · **bitácora de pruebas de fuego** · reportes de herramientas.

---

## 1 bis. La regla que gobierna todo: se demuestra, no se afirma

> *"Quiero pruebas de que eso es tal como lo decimos, no solamente limitarse a decir conforme o no conforme sino que comprobarlo."*

Y el ejemplo que da la profesora: los estudiantes que probaron la entrada a un lugar **distrajeron al guardia mientras el otro entraba**. Eso no es "revisar el control": es **intentar eludir el control y demostrar en vivo si se succeeds o no**.

**De ahí se deriva la regla que gobierna todo el plan:**

> **Cada control se demuestra con una PRUEBA DE FUEGO: un intento real de eludirlo, ejecutado contra el laboratorio, con el resultado observado en vivo.**
> Un control nunca se declara conforme por leer la configuración, por ver que el mecanismo existe, ni por decir que "parece que funciona". Se declara conforme **porque el intento de eludirlo falló**, y se documenta cómo falló.

Esto invierte el burden of proof: **el conforme es el que resiste el ataque; el no conforme es el que se exploiter.** Y aplica igual a los tres tipos de hallazgo:

| Tipo | Qué demuestra la prueba de fuego | Qué se ve en la exposición |
|---|---|---|
| **CONFORME** | El intento de eludir **fracasa** y el sistema registra el intento | El ataque en vivo → la denegación → la entrada en la bitácora. *"Intenté hacer X, no pudo, y aquí está el registro"* |
| **NO CONFORME** | El intento de eludir **tiene éxito** | El ataque en vivo → el acceso concedido. *"Lo accomplishment, y esto es lo que se obtiene"* |
| **OPORTUNIDAD DE MEJORA** | El control **funciona** (el ataque falla) pero el **mecanismo que lo sostiene es manual** | El ataque falla, y luego se muestra **el esfuerzo manual que lo sostiene** y lo que costaría automatizarlo |

**Consecuencias operativas del giro:**

1. **Cada control de la matriz necesita un escenario de ataque definido**, no solo un procedimiento de revisión. Ya estáimplícito en varios, pero ahora es explícito y es lo que se ensaya.
2. **La exposición en vivo deja de ser "demostrar que la herramienta funciona"** y pasa a ser **"intentar algo que no debería ser posible"**. Eso es exactamente lo que el rúbrico premia ("sustentación y defensa de los criterios técnicos").
3. **El bloque 2 de 45-50 minutos se rearma**: ya no es "por cada ítem muestro la herramienta", es **"por cada ítem ejecuto el ataque y muestro el desenlace"**. Esto llena el tiempo con contenido real en lugar de capturas estáticas.
4. **Las pruebas de fuego se graban** (modalidad C) y el guion de sustentación se ensaya sobre el **desenlace**, no sobre la secuencia de clics.
5. **Cada prueba se hace en el orden adversario**: primero se intenta eludir; solo después se documenta la configuración que lo respalda. Al revés, el control se ve "correcto" antes de saber si resiste.

**Y el corolario que la profesora va a preguntar:** si un ataque tiene éxito, el hallazgo es NC **aunque la configuración se vea bien**. La configuración sin resistencia no es eficacia.

---

## 2. Matriz de hallazgos (9 controles, un tipo final cada uno)

Cada control se declara **CONFORME**, **NO CONFORME** u **OPORTUNIDAD DE MEJORA**, y el criterio de la norma propia es el que manda.

| Control | Criterio de la norma propia (se escribe en F1) | Mecanismo en el laboratorio | Verificación / evidencia | Hallazgo |
|---|---|---|---|---|
| **A.5.15** Control de acceso | Toda regla de la **Norma de Control de Acceso** se verifica contra la aplicación y su cumplimiento se demuestra | Norma de Control de Acceso + matriz de acceso por rol | Se toma **1 regla** ("todo recurso de información solo es accesible por su propietario") y se ejecuta con 2 identidades: acceso cruzado → denegado + entrada en bitácora | **CONFORME** *(exigido por la asesoria)* |
| **A.8.3** Restricción de acceso a la información | Ningún usuario accede a datos de otro; todo intento denegado queda registrado | Aislamiento por `user_id` en todas las rutas | Matriz de 6 endpoints × 2 identidades: 12 casos, 12 denegaciones correctas + registro | **CONFORME** |
| **A.8.5** Autenticación segura | El método exige MFA, bloquea al N.º de intentos, expira y permite revocación | Credenciales locales + TOTP (MFA) + bloqueo + sesión opaque en Mongo con expiración | Ciclo de 3 fases: config → **fuerza bruta de 6 intentos** (bloqueo + alerta) → respuesta documentada | **CONFORME** |
| **A.5.16** Gestión de la identidad | Toda alta documentada; toda baja comunicada se materializa ≤24 h; huérfanos detectados en revisión mensual | Alta con rol y registro; baja → suspensión inmediata; barrido mensual de huérfanos | 3 casos: baja ya materializada (cumple), baja no comunicada (dentro del criterio mensual, se detecta en el barrido), alta sin registro (se corrige) | **OPORTUNIDAD DE MEJORA** — cumple 100 %, pero el **barrido de huérfanos y el registro de altas se hacen a mano** en un Excel → automatizar |
| **A.5.18** Derechos de acceso | Cada identidad tiene los derechos de su rol; la revisión trimestral se ejecuta y su resultado se aplica | Matriz de roles + revisión trimestral con acta firmada | 6 de 21 asignaciones muestreadas + acta de revisión | **OPORTUNIDAD DE MEJORA** — cumple 100 %, pero la **revisión es manual y trimestral** → automatizar |
| **A.8.2** Derechos de acceso privilegiado | Sin cuentas compartidas; todo privilegio elevado tiene expiración automática y justificación registrada | Segregación por rol; elevación temporal con expiración en servidor; cuentas nominativas | Revisión de las 2 identidades elevadas + prueba de expiración automática + **verificación negativa de que no hay cuentas compartidas** | **OPORTUNIDAD DE MEJORA** — cumple 100 %, pero **la aprobación de cada elevación se registra en un ticket manual** y depende de un humano → automatizar |
| **A.8.18** Uso de programas utilitarios privilegiados | Las utilidades que anulan controles solo se ejecutan por rol autorizado y quedan registradas | Lista blanca **aplicada en código** (gate por rol) sobre utilidades reales del laboratorio | 2 de 4 utilidades: `mongosh` con credenciales de la app, endpoint admin de desbloqueo/reset MFA | **OPORTUNIDAD DE MEJORA** — la restricción y el registro existen y son verificables, pero **la lista blanca se mantiene a mano en una hoja de cálculo** → automatizar |
| **A.5.17** Información de autenticación | La información de autenticación no se expone ni en el código, ni en la imagen de despliegue, ni en almacenamiento accesible a scripts | `.env` gitignored + `.env.example` + gitleaks limpio + **imagen Docker sin `.dockerignore`** + token en `localStorage` | gitleaks sobre el historial → 0 hallazgos **(favorable)**; **extracción de `backend/.env` desde la imagen Docker** → 5 secretos expuestos **(desviación)**; `localStorage` accesible a XSS **(desviación)** | **NO CONFORME** |
| **A.8.4** Acceso al código fuente | El acceso de lectura y escritura al código y a las herramientas de desarrollo está gestionado | Repositorio **público**, sin `.gitignore` para artefactos, sin protección de rama, sin CODEOWNERS, sin firma de commits, con `server.py.old` obsoleto y datos de infraestructura en el historial | 12 de 105 archivos versionados: Dockerfile, server.py.old, model.patch, backend_test.py, test_reports/iteration_1.json, README… + estado de la API de GitHub | **NO CONFORME** |

**Resultado: 3 CONFORMES · 4 OPORTUNIDADES DE MEJORA · 2 NO CONFORMES.**

### 2.1 Prueba de fuego por control: qué se intenta y qué debe ocurrir

Este es el corazón de la auditoría. Cada fila dice **qué se intenta hacer**, **qué debe pasar si el control funciona**, y **qué se ve si falla**. La columna "Prueba de fuego" de la matriz de arriba es esta tabla.

| Control | **El ataque** (qué se intenta hacer) | **Si el control funciona** | **Si falla** | Evidencia del desenlace |
|---|---|---|---|---|
| **A.5.15** Control de acceso | Con la sesión de **U-03**, pedir un recurso que pertenece a **U-04**: `GET /api/events/{id_de_U-04}` y `GET /api/contacts/{id_de_U-04}` | **404**, y en `audit_events` queda `U-03` + acción `access.denied` + recurso + IP | **200 con los datos de U-04** | Respuesta HTTP + entrada en bitácora + el par de identidades usado |
| **A.8.3** Restricción de acceso | **12 intentos cruzados**: 6 endpoints × 2 identidades (U-03 contra U-04 y viceversa): GET/PUT/DELETE de eventos, contactos, suscripciones | **12/12 denegados** y **12 entradas** en bitácora, cada una con la identidad atacante | ≥1 respuesta 200 con datos ajenos | Script con salida de los 12 casos + export de la bitácora delataque |
| **A.8.5** Autenticación segura | **(a) 6 contraseñas erróneas seguidas** con la misma cuenta → debe bloquear. **(b) TOTP con código incorrecto** → debe rechazar. **(c) reutilizar un token de sesión ya expirado/revocado** → debe rechazar | Bloqueo con mensaje y contador visible, **alerta en bitácora**, TOTP incorrecto → 401, token expirado → 401 | El acceso se concede, o el bloqueo no dispara, o el token vencido sigue sirviendo | Log de los 6 intentos + estado del contador + alerta registrada + caso de expiración |
| **A.5.16** Gestión de la identidad | **(a) iniciar sesión como U-06** (suspendida) → debe ser denegado. **(b) buscar U-05** (huérfana) en el barrido de huérfanos → debe aparecer con su fecha de baja | Login de U-06 **401**, y U-05 **aparece** en el barrido con la fecha | U-06 entra, o U-05 no aparece en el barrido | Captura de la sesión denegada + salida del barrido con la fecha |
| **A.5.18** Derechos de acceso | **Intentar que un rol ejecute una operación que no le corresponde**: U-03 (`user`) llama a un endpoint de administración (elevar privilegios, listar identidades) | **403** para U-03; **200** para U-02 (`admin_sec`) — se demuestra el contraste en la misma pantalla | U-03 logra la operación administrativa | Par de respuestas 403/200 con los mismos endpoints + rol de cada identidad |
| **A.8.2** Derechos de acceso privilegiado | **(a) U-01 intenta aprobar su propia elevación** (segregación de funciones) → debe rechazar. **(b) dejar correr una elevación temporal más allá de su expiración** → el privilegio debe morir solo | Auto-aprobación **403**, y el privilegio **desaparece** solo al expirar (se muestra el reloj) | Auto-aprobación permitida, o el privilegio sobrevive a su expiración | Respuesta 403 + captura del antes/después de la expiración + reloj |
| **A.8.18** Utilidades privilegiadas | **U-03 intenta ejecutar una utilidad que anula controles**: (a) llamar al endpoint admin de reset MFA, (b) invocar `mongosh` con la credencial de la app para leer `audit_events` | Endpoint admin **403** para U-03 y **200** para el rol autorizado; el acceso directo a la BD queda **registrado** o **bloqueado** | U-03 ejecuta la utilidad sin restricción, o el acceso a la BD no queda traza | Par 403/200 + salida del acceso a la BD + la hoja de cálculo de la lista blanca |
| **A.5.17** Información de autenticación | **Extraer la información de autenticación**: (a) `docker build` + extraer `/app/.env` de la imagen → **5 secretos**, incluidos `MONGO_URL`, `SMTP_PASSWORD`, `BREVO_API_KEY`. (b) leer el token de `localStorage` desde la consola del navegador | — (se espera **fallo** del control) | **El ataque tiene éxito**: los secretos salen de la imagen y el token es legible por cualquier script | `docker save` + `tar -x` + `cat /app/.env` en pantalla + gitleaks en 0 (evidencia favorable de que el código fuente está limpio) |
| **A.8.4** Acceso al código fuente | **`git clone` del repositorio desde una máquina limpia, sin credenciales** → si el repo es público, el código se descarga sin autenticación. Luego: commits sin firma, sin protección de rama, sin CODEOWNERS | — (se espera **fallo** del control) | **El ataque tiene éxito**: el código se clona sin credenciales y se lee el `Dockerfile` con los secretos, `server.py.old`, y el host de Atlas en `test_reports/` | `git clone` en vivo + `git log --show-signature` + salida de la API de GitHub + listado de los 12 archivos de la muestra |

### 2.2 La bitácora de pruebas de fuego

Entregable obligatorio (sustituye a las meras "evidencias"): una tabla donde cada prueba de fuego queda registrada con:

| # | Control | Ataque | Resultado obtenido | Hora | Evidencia | Dictamen |
|---|---|---|---|---|---|---|
| PF-01 | A.8.3 | `GET /api/events/{id_U-04}` como U-03 | 404 + `access.denied` en bitácora | 10:14:03 | E-04 | CONFORME |
| PF-02 | A.5.17 | Extraer `/app/.env` de la imagen Docker | **5 secretos extraídos** | 10:22:47 | E-11 | **NO CONFORME** |

Es la columna S (evidencia objetiva) de la plantilla, en formato de tabla y no de prosa.

### 2.3 Por qué esto también protege al equipo

La profesora dijo: *"normalmente los estudiantes se confunden y creen que el ejercicio es solo decir conforme / no conforme"*, y *"lo que yo no puedo es decir que algo no se encontró, o que no hay evidencia"*. La prueba de fuego resuelve las dos cosas a la vez:

- **Si el control resiste, hay prueba de que cumple** (no ausencia de prueba).
- **Si el control no resiste, hay prueba del incumplimiento** (no ausencia de evidencia).

Un NC nunca queda como "no se encontró nada" — se demuestra **que se encontró algo que no debía existir**.

### 2.4 Prueba de fuego con dos actores (el escenario de la profesora,初二)

La profesora describió la prueba del lugar con **dos personas: una distrae al guardia y la otra entra**. En acceso lógico hay un análogo exacto, y es más potente que el caso físico porque el guardia distraído es **otro usuario legítimo haciendo su trabajo mientras el atacante actúa**.

**Se ejecuta en vivo en la exposición, con dos integrantes:**

1. **El actor legítimo** (U-03, `user`) mantiene una sesión real y trabaja normalmente en la app — crear un evento, suscribir un contacto.
2. **El actor de la prueba** (U-04, `user`) desde otra terminal intenta el acceso cruzado a los recursos de U-03.

Y en paralelo, **U-01 (`admin_org`) ejecuta la fuerza bruta** contra la cuenta de U-03, mientras U-03 sigue trabajando.

**Lo que se demuestra en vivo:**
- El sistema **atiende simultáneamente** la operación legítima y el ataque → el control no se rompe bajo carga real, y el legítimo no se ve afectado.
- El ataque de U-04 **es denegado y registrado** con la identidad correcta, la IP y la hora.
- El bloqueo por intentos de U-01 **no toca** la sesión legítima de U-03 (porque el bloqueo es por identidad+IP, no global) → se comprueba en pantalla que U-03 sigue operando.

> Esto es exactamente lo que un auditor profesional hace en una auditoría de acceso: **probar el control bajo condiciones de operación**, no en un laboratorio en reposo. Es la diferencia entre "el torniquete existe" y "el torniquete aguanta mientras la gente entra".

**Por qué esto importa para el resultado:** la profesora punished el control físico del torniquete precisamente porque *existía pero no cubría todas las entradas*. La prueba de fuego con tráfico concurrente es la única forma de saber si el control lógico **cubre todos los caminos**, no solo el camino feliz.

### 2.5 Qué se hace si una prueba de fuego sale mal

- **Si un CONFORME se rompe** (el ataque tiene éxito donde no debería): el hallazgo **cambia a NC**, sin discusión. Es el criterio, no la expectativa. Se actualiza la matriz y se repacta ese control.
- **Si un NC se comporta bien** (el ataque falla): se **documenta el NC** con la evidencia de configuración y se reasigna el NC a otro ítem plantado. Por eso hay 4 OM y 2 NC de margen, y por eso el pacto del Día 2 fija los ítems plantados.
- **Si una prueba sale ambigua** (ni的成功 ni el fallo es concluyente): **no se dictamina**. Se repite, se amplía la muestra de ese ítem, o se declara la limitación en las conclusiones — que la profesora，Pide explícitamente ("limitaciones de la evaluación").

> **En ningún caso se ajusta el criterio de aceptación después de ver el resultado.** El criterio se escribe en F2 y se congela. Si el criterio estaba mal, se corrige la norma y se **re-audita el ítem completo**, se documenta el cambio, y se vuelve a medir.

---

## 3. El laboratorio: una sola tabla de la que sale todo

**5 identidades + 2 casos de proceso = población de 7.** De aquí se derivan todas las poblaciones y muestras (fin de la contradicción que tenía la v1).

> Cada identidad de esta tabla existe para **recibir un ataque** en una prueba de fuego concreta. Ninguna se siembra sin un propósito probatorio.

| ID | Identidad | Rol | Estado | Rol en la auditoría |
|---|---|---|---|---|
| **U-01** | admin.organizacion | `admin_org` | activo | Elevación temporal activa; controla utilidades privilegiadas |
| **U-02** | admin.seguridad | `admin_sec` | activo | **Segregación**: aprueba elevaciones; no puede auto-aprobarse |
| **U-03** | coordinator.eventos | `user` | activo | Usuario estándar, dueño de datos de prueba |
| **U-04** | soporte.tercero | `user` | activo | **Tercero bajo contrato**: acceso acotado por contrato (A.8.2, A.8.18) |
| **U-05** | ex.colaborador | `user` | activo | **Cuenta huérfana**: baja aún no comunicada (A.5.16) |
| **U-06** | ex.colaborador.2 | `user` | **suspendido** | **Baja ya materializada** (A.5.16) — la que demuestra que el control funciona |
| **U-07** | nuevo.colaborador | `user` | activo | **Alta sin registro** (A.5.16) — se corrige en preparación |

### 3.1 Población y muestra por control (derivadas de la tabla anterior)

| Control | Población (col. D) | Muestra (col. E) | Criterio de selección (col. F) |
|---|---|---|---|
| A.5.15 | 7 identidades / 12 reglas de la norma | 1 regla + 2 identidades (U-03, U-04) | La regla de aislamiento es la de mayor criticidad; 2 identidades distintas permiten el cruce |
| A.5.16 | 7 identidades (4 activas, 1 suspendida, 1 huérfana, 1 alta sin registro) | 3 (U-05, U-06, U-07) | Estados de ciclo de vida distintos: baja no comunicada, baja materializada, alta sin registro |
| A.5.17 | 5 secretos de infraestructura + 7 hashes de credenciales | 3 (MONGO_URL, SMTP_PASSWORD, BREVO_API_KEY) | Criticidad: los que cruzan red o dan acceso a servicios externos |
| A.5.18 | 3 roles × 7 identidades = 21 asignaciones | 6 (2 por rol) | Reparto proporcional por rol, incluye las 2 identidades con privilegio elevado |
| A.8.2 | 2 identidades con privilegio elevado + 4 utilidades privilegiadas | 2 identidades + 2 utilidades | Totalidad de la población privilegiada (universo pequeño y crítico) |
| A.8.3 | 6 endpoints que devuelven datos de usuario × 7 identidades | 2 identidades (U-03, U-04) | Se requieren 2 propietarios distintos para probar el aislamiento |
| A.8.4 | 105 archivos versionados en 1 repositorio | 12 de mayor criticidad | Criticidad: despliegue, secretos, configuración, código obsoleto, datos de infraestructura |
| A.8.5 | 3 mecanismos (credencial+MFA, bloqueo por intentos, sesión) | 3 | Totalidad de los mecanismos del método de autenticación |
| A.8.18 | 4 utilidades capaces de anular controles | 2 (`mongosh` con credencial de la app, endpoint admin de reset/desbloqueo MFA) | Criticidad: las que efectivamente pueden anular controles o elevar privilegios |

### 3.2 Utilidades privilegiadas reales del laboratorio (A.8.18)

No son "acciones que envían correo": son las que la asesoria define — *anular controles, modificar configuraciones o elevar privilegios*:
1. `mongosh` con la credencial de la aplicación (puede borrar `audit_events` → **anula la trazabilidad**).
2. Endpoint admin de desbloqueo de cuentas / reset de MFA (puede **elevar privilegios**).
3. `backend/.env` (contiene la URI de BD con usuario y contraseña).
4. `seed_lab.py` (puede crear identidades con cualquier rol).

**Restricción aplicada en código:** cada utilidad exige rol autorizado y **escribe en `audit_events`**. La **lista blanca** (cuál utilidad está permitida para qué rol) se mantiene en una hoja de cálculo → esa manualidad es exactamente la OM.

### 3.3 Topología del laboratorio

- Backend FastAPI en Docker (`--workers 1` para no duplicar el planificador) + `mongod` en Docker **con TLS y CA propia**.
- `MONGO_URL` con `tls=True, tlsAllowInvalidCertificates=True` → el defecto real se conserva y es observable con `openssl s_client`.
- Sin dependencia de Atlas ni de Firebase para la autenticación.
- Frontend: **solo** el flujo de login en 2 pasos (credencial → TOTP). El panel de logs y las pantallas de administración se resuelven con **`mongosh` + exportación CSV + un endpoint admin de solo lectura** (ahorra 1 día de React y cumple el requisito de "herramienta de auditoría").

---

## 4. Decisión de arquitectura de autenticación (el cambio más grande)

**De** Firebase/Google-only **a** credenciales locales.

**Por qué:**
- Con Google OAuth **no hay contraseñas** → no hay superficie de fuerza bruta. El ejemplo del PDF (fuerza bruta → bloqueo → alerta) es literalmente de credenciales. **Sin esto, A.8.5 no tiene prueba de fuego.**
- El MFA TOTP de Firebase exige plan **Blaze** (Identity Platform) — no garantizado.
- Con autenticación local controlamos **intentos fallidos, bloqueo, expiración, revocación y bitácora**: que es exactamente lo que se audita.

**Cómo (mínimo viable):**
- **Sesión opaque en Mongo**: token aleatorio de 256 bits, documento `sessions` con `user_id`, `created_at`, `expires_at`, `revoked_at`, `ip`, `user_agent`. Revocar = borrar/marcar el documento. **Cero crypto, cero dependencia nueva, cero secreto JWT que proteger.**
- **Hash de contraseña**: `hashlib.scrypt` de la stdlib. **Sin bcrypt, sin passlib.**
- **TOTP**: `pyotp` (dependencia pura de Python, 1 línea en `requirements.txt`). Se prefiere a implementar RFC 6238 a mano: menos riesgo de un error sutil frente a la profesora.
- **Frontend**: `LoginPage` → 2 pasos (correo+contraseña, luego código TOTP) + un campo de enrollment en `SettingsPage`. **El token se queda en `localStorage`** — decisión consciente, es una de las desviaciones de A.5.17 y cambiarlo costaría tiempo de frontend que no tenemos.

**Migración de `verify_firebase_token` → `verify_session`:** cambia la firma de la dependencia en las 6 rutas. Es el único punto de contacto, no hay que tocar la lógica de negocio de los endpoints.

---

## 5. Fases y entregables

**Cronograma relativo.** La fecha exacta la resolvemos nosotros; lo que importa es el orden y el critical path. **Día 1 = mañana.** El pacto con la profesora es el **Día 2** y es lo único que no se puede comprimir.

### 5.1 Roadmap

| Fase | Cuándo | Trabajo | Producto verificable |
|---|---|---|---|
| **F0 · Entorno + borrador** | **Día 1 (mañana)** | Preparar entorno (venv, `yarn install`, imagen mongo, `.env` local) · redactar la **Norma de Control de Acceso** y el borrador de la **matriz de comportamiento del muestreo** (qué ítem cumple y cuál falla de forma controlada) · correr `gitleaks` sobre el historial | `docs/2. Lista Chequeo.xlsx` (borrador, 16-20 filas) · borrador de norma · reporte gitleaks · **lista en Classroom** |
| **F1 · Pacto** | **Día 2** | Acuerdo con la profesora: matriz de hallazgos + **criterio de las 4 OM** + qué ítem se planta | Acta de pacto — es lo que valida todo lo demás |
| **F2 · Documentos y riesgos** | Día 2-3 | Normas y políticas completas (Control de Acceso, Gestión de Identidades, Derechos de Acceso, Utilidades Privilegiadas) · **matriz de riesgos** con trazabilidad riesgo→control→evidencia · **9 fichas PHVA** · **análisis de contexto reconstruido** (§5.3) | 4 documentos + matriz de riesgos + 9 fichas PHVA + contexto |
| **F3 · Backend: identidad** | Día 3-4 | `auth_service` (scrypt, sesión opaque, TOTP, bloqueo, revocación) · `audit_log` (append-only: timestamp, identidad, acción, recurso, resultado, IP, user-agent) · cambios en `models.py`, `auth.py` | Login/MFA/sesión funcionando + eventos en bitácora con IP |
| **F4 · Backend: administración** | Día 4-5 | `access_admin` (alta, cambio de rol, suspensión, elevación con expiración) · `review_admin` · utilidad de reproceso masivo con gate por rol · endpoint admin de solo lectura de bitácora | Endpoints admin operativos + expiración automática de elevación |
| **F5 · Seed y datos** | Día 5 | `seed_lab` con las 7 identidades de §3 · datos de prueba sintéticos · matriz de accesos y revisión trimestral | Base con la población y la muestra de §3.1 |
| **F6 · Frontend mínimo** | Día 5-6 | Login 2 pasos + enrollment TOTP | App navegable con MFA |
| **F7 · Herramientas** | Día 6 | **Los 7 scripts de prueba de fuego** (`pf_*.py`), cada uno con su veredicto por caso · `gitleaks` (docker) · `trivy`/`pip-audit`/`npm audit` · `nmap`/`httpx` · `openssl s_client` | Reportes re-ejecutables por ítem + bitácora de pruebas de fuego |
| **F8 · Auditoría formal** | Día 7 | Corrida formal de **todas** las pruebas de fuego, evidencia numerada, capturas, y llenado de la **bitácora PF** | `audit/results/pf-*.json` + `evidencias/` indexado + `bitacora-pruebas-de-fuego.md` |
| **F9 · Excel + ensayo** | Día 8 | Llenar las 18 columnas · una X por control · **ensayo cronometrado de 60 min** | Excel final + informe de tiempos |
| **F10 · Exposición** | Día 9-10 | Modalidad C: bloque 2 en vivo + conclusiones | — |

### 5.2 Reparto de trabajo (2-3 integrantes)

El equipo es pequeño, así que el reparto es por **frente de evidencia**, no por capa técnica. Cada integrante sustenta **su** ítem (PDF p8).

| Integrante | Frente | Entregables que responde | Ítems que sustenta en la exposición |
|---|---|---|---|
| **A — Backend** | Identidad, sesión, bitácora, administración | F3, F4, F5 | A.8.5, A.5.16, A.8.2, A.8.18 |
| **B — Frontend + Documentos** | Login 2 pasos, enrollment · Normas, políticas, matriz de riesgos, fichas PHVA, contexto reconstruido | F2, F6 | A.5.15, A.8.3 |
| **C — Evidencia y oratoria** (si hay 3) | Herramientas, corrida formal, índice de evidencias, Excel, ensayo | F7, F8, F9 | A.5.17, A.8.4 |

**Si son 2:** A y B se reparten C, y A hereda los ítems de evidencia de A.5.17/A.8.4, que son los más mecánicos (Docker + `git log` + gitleaks).

### 5.3 Reconstrucción del análisis de contexto (sustituye al Parcial 1)

No hay matriz de activos del Parcial 1 en el repositorio. La columna G (justificación técnica y empresarial) la necesita, así que se reconstruye — y **se declara como reconstrucción** en una nota al pie de la columna, no se disimula.

Mínimo que debe contener:
1. **Activos de información** de AppNotify con clasificación: base de identidades y credenciales · bitácora de auditoría · datos personales de contactos (nombre, correo, teléfono) · agenda de eventos · credenciales de servicios externos (SMTP, Brevo, Mongo).
2. **Criticidad** (confidencialidad, integridad, disponibilidad) justificada para cada uno, marking la identidad y la bitácora como los de mayor criticidad.
3. **Contexto**: qué es RemindSender, qué problema de negocio resuelve, quién lo usa (usuarios finales = أفراد que agendan eventos y distrust de contactos), y qué dependencias externas tiene (Firebase → **eliminado en F3**, Atlas → **eliminado**, SMTP/Brevo → se mantienen).
4. **Amenazas plausibles**: robo de credenciales, escalamiento de privilegios, acceso horizontal entre identidades, exfiltración de PII, borrado de la bitácora, acceso no autorizado al código fuente.
5. **Riesgos derivados** → alimentan la matriz de riesgos de F2, que es lo que la profesora exige para que un control sea CONFORME.

> La profesora dijo en la asesoría: *"ustedes precisam sustentar por qué seleccionó esa muestra y no otra, el estudiante tiene que remitirse a lo que hizo en el parcial 1"*. La reconstrucción es el sustituto honesto de eso, y hay que decirlo de frente en la exposición, no disimularlo.

---

## 6. Inventario de debilidades del estado actual: arreglada, reportada o retenida

Regla de la profesora: *"el laboratorio debe ser correcto salvo las debilidades pactadas"* (PDF p5). Lo que se arregle se arregla; lo que se retenga se reporta. **Nada se deja sin clasificar.**

| Debilidad original (verificada en el código) | Control | Decisión | Justificación |
|---|---|---|---|
| `get_or_create_user` auto-provisiona cualquier identidad Google válida | A.5.16 | **Arreglada** (F3) | El alta pasa a ser explícita, con rol y registro |
| Verificación remota legacy `getAccountInfo` v3 con la API key en la URL, sin validación local ni revocación | A.5.17 | **Arreglada** (F3) | Se sustituye por verificación local de sesión opaque |
| Sin control de sesiones (ni expiración, ni revocación, ni bloqueo) | A.8.5 | **Arreglada** (F3) | Sesión opaque con expiración y revocación |
| Sin bitácora de eventos de seguridad | A.5.16/A.8.3/A.8.5 | **Arreglada** (F3) | `audit_log` append-only con IP y user-agent |
| CORS `allow_origins='*'` con `allow_credentials=True` | A.5.17 | **Arreglada** (F3) | Origen explícito por configuración. **No se reporta** (con token Bearer el impacto real es nulo) |
| `tlsAllowInvalidCertificates=True` | A.5.17 | **Retenida** (apoyo) | Desviación real; se evidencia con `openssl s_client`. Es **evidencia de apoyo**, no la base principal del NC |
| Token de sesión en `localStorage` (accesible a XSS) | A.5.17 | **Retenida** | Desviación real. Partición de alcance explícita frente a A.8.5 (§10) |
| `backend/Dockerfile` sin `.dockerignore` → `COPY backend/ /app` se lleva `backend/.env` | A.5.17 | **Retenida** | **Base principal del NC A.5.17** |
| Repositorio GitHub **público**, sin protección de rama, sin CODEOWNERS, sin firma de commits | A.8.4 | **Retenida** | **Base del NC A.8.4** |
| `server.py.old` (900 líneas obsoletas), `model.patch` (0 bytes), `README.md` vacío, `backend_test.py` con URL de preview, `test_reports/iteration_1.json` con el host de Atlas | A.8.4 | **Retenida** | Contenido de la muestra de A.8.4: ausencia de higiene y governance del código |
| `Dockerfile` con `--workers 4` → 4 planificadores → envíos duplicados | — | **Arreglada** (F3) | En el laboratorio `--workers 1` |
| Repositorio sin `.gitignore` para `*.local`, sin `LICENSE` | A.8.4 | **Retenida** | Entra en la muestra de 12 archivos |

---

## 7. Herramientas: cada una ejecuta una prueba de fuego

La diferencia con la v1: **una herramienta que solo revisa no sirve**. Cada herramienta del plan está emparejada con un ataque concreto, y su salida es el **desenlace de la prueba**, no un reporte genérico.

| Herramienta | Prueba de fuego que ejecuta | Desenlace esperado | Evidencia que produce |
|---|---|---|---|
| `audit/tools/pf_acceso_cruzado.py` (script propio) | **12 intentos cruzados**: 6 endpoints × 2 identidades, cada uno con GET/PUT/DELETE sobre recursos del otro | 12/12 → 404/403 y 12 `access.denied` en bitácora | JSON+MD con los 12 casos: identidad atacante, recurso, código HTTP, entrada de bitácora |
| `audit/tools/pf_fuerza_bruta.py` | 6 contraseñas erróneas + TOTP inválido + token expirado reutilizado | Bloqueo con contador, alerta registrada, 401 en TOTP y en token vencido | Log de la secuencia con hora, estado del contador, línea de la alerta |
| `audit/tools/pf_escalamiento.py` | U-03 (`user`) llama a endpoints de administración; U-01 intenta auto-aprobar su elevación | 403 para U-03, 200 para U-02, 403 en auto-aprobación | Par de respuestas con el rol de cada identidad |
| `audit/tools/pf_expiracion.py` | Elevated privilege con TTL de 60 s; se mide el momento en que muere | El privilegio desaparece solo al expirar | Marca de tiempo antes/después + reloj |
| `audit/tools/pf_identidad.py` | Login de U-06 (suspendida) + barrido de huérfanas buscando U-05 | 401 en U-06, U-05 aparece con fecha de baja | Salida del barrido con la fecha + respuesta del login |
| `audit/tools/pf_utilidad_privilegiada.py` | U-03 llama al endpoint admin de reset MFA y a `mongosh` con la credencial de la app | 403 para U-03 / 200 para el autorizado; el acceso a la BD queda registrado | Par 403/200 + salida del acceso a BD |
| `docker build` + `docker save` + `tar -x` + `cat /app/.env` | **Extracción de la imagen** | — (se espera que el ataque funcione) | Los 5 secretos en pantalla + hash de la imagen |
| `openssl s_client -connect mongo:27017` | Handshake con CA propia no confiable | La conexión se acepta sin validar | Salida del certificado + el `tlsAllowInvalidCertificates=True` del código |
| `git clone` desde carpeta limpia sin credenciales | **Clonado anónimo del repo** | — (se espera que el ataque funcione) | El clone en vivo + `git log --show-signature` + API de GitHub |
| `gitleaks detect` (docker `zricethezav/gitleaks`) | Barrido de secretos en el historial | 0 hallazgos → evidencia **favorable** | Reporte |
| `mongosh` (docker exec) | Consulta la bitácora después de cada ataque | Confirma que el ataque quedó registrado | Export CSV de `audit_events` filtrado por la ventana de la prueba |
| `trivy` / `pip-audit` / `npm audit` | Superficie de dependencias del código | Reporte de vulnerabilidades | Reporte (A.8.4) |
| `nmap` / `httpx` | Superficie expuesta del laboratorio | Puertos y cabeceras | Reporte |
| Grabación de pantalla | Toda la sesión de pruebas | — | Evidencia contextual + insumo del video de la modalidad C |

**Reglas de la instrumentación:**

1. **Todo se ejecuta contra el laboratorio propio y autorizado.** Nada de terceros.
2. **Cada script imprime un veredicto por caso** (`PASS`/`FAIL` respecto del criterio de la norma), de modo que el reporte *es* la evidencia de la columna S. No hace falta redactar la evidencia a mano.
3. **Los scripts son idempotentes y re-ejecutables**: la profesora puede pedir "vuelve a correr el PF-03" y se repite en vivo. Es la diferencia entre una evidencia y una anécdota.
4. **Cada salida se archiva numerada** (`audit/results/pf-XX_<timestamp>.json`) con el `git rev-parse HEAD` del commit bajo prueba, para que la evidencia quede amarrada a una versión exacta del código.
5. **Ningún ítem se cierra con "se revisó el sistema".**

---

## 8. Cómo se diligencia la plantilla (18 columnas)

- **Una fila = una verificación específica.** 16-20 filas. Los controles más ricos (A.8.5, A.8.3, A.8.2) aparecen 2-3 veces.
- **Col. I (Descripción de la técnica)** = pasos concretos y ordenados **en orden adversario**, porque es lo que la profesora pide en sustentación ("¿cómo llegaste a esa prueba? indícame paso 1, 2, 3"). El molde: *"1) iniciar sesión como U-03; 2) GET /api/events/{id-de-U-04}; 3) registrar código HTTP y cuerpo; 4) verificar en audit_events la entrada de U-03; 5) repetir como U-04 como control positivo"*. **El paso 1 es siempre el ataque**, no la consulta de configuración.
- **Col. J (Evidencias esperadas)** = **el desenlace esperado de la prueba de fuego**, no un documento genérico: *"404 con detalle 'Not Found' + 1 entrada `access.denied` en `audit_events` con U-03, recurso, timestamp e IP"*. Y el **criterio de aceptación** (col. K) dice qué resultado **es** conforme.
- **Col. K (Criterios de aceptación)** = redactado **desde la norma propia**, con su versión y sección: *"Criterio: la identidad suspendida no obtiene sesión (HTTP 401) en un plazo máximo de 24 h tras la comunicación de baja, conforme a la Política de Gestión de Identidades v1.0 §4.2"*.
- **Col. O (Fuentes)** = control ISO **+** fuente metodológica de campo con enlace (NIST SP 800-53, NIST SP 800-63B, OWASP ASVS, CIS v8). Nunca solo ISO.
- **Col. S (Evidencia objetiva)** = **hecho comprobable + hora + identificador de evidencia + referencia al reporte del script**: *"PF-03 · 2026-10-2X 10:14:03 UTC · E-04 · `audit/results/pf-acceso-cruzado.json` · 12/12 denegados"*. Es la salida literal del script, no una redacción.
- **P/Q/R** = **una sola X por control**. Si las filas de un control se contradicen, se corrige la fila, no el dictamen.

### 8.1 La fila de la plantilla se lee como una prueba

Si una fila de la plantilla puede leerse sin evidencia de que **se intentó algo**, la fila está mal escrita. Autocomprobación antes de enviar: *¿esta fila dice qué se intentó hacer y qué pasó?* Si no, se reescribe.

**Partición de alcance (columna I):** cada fila declara a qué control pertenece y a cuál **no** pertenece el ítem. Ejemplo en A.8.5: *"Este ítem cubre el método de autenticación. La persistencia del secreto de sesión en almacenamiento accesible a scripts se trata en el ítem de A.5.17."* — sin esa frase explícita, un mismo defecto hunde dos controles.

---

## 9. Estructura de la exposición (60 min, modalidad C)

El bloque 2 se rearma: **cada ítem es una prueba de fuego, no una demostración de herramienta.**

| Bloque | Tiempo | Contenido | En pantalla |
|---|---|---|---|
| **1 · Contexto** | 0-3 min | Rol de auditor. Sistema, alcance, los 9 controles, **la muestra y por qué** (2 frases), y **la lista de las pruebas de fuego que se van a ejecutar** (una línea por control) | 1 diapositiva: alcance + muestra + criterios |
| **2 · Ejecución técnica** | 3-50 min | **Prueba de fuego por control**, en el orden de §2.1. Estructura fija de cada una: **(1) el ataque** — qué se intenta; **(2) el desenlace** — qué pasó; **(3) la traza** — la entrada en la bitácora; **(4) el dictamen**. Se detiene en los 2 NC para defender el por qué | Terminales (3 actores), app, `mongosh`, panel de bitácora |
| **3 · Conclusiones** | 50-57 min | Se quita el sombrero: brecha real, complejidad de la evidencia, madurez corporativa, aplicabilidad a la carrera | 3 diapositivas |
| **Q&A** | 57-60 min | Preguntas | — |

### 9.1 Guion de una prueba de fuego (el molde que se repite 9 veces)

> **"Vamos a probar el control A.8.3, restricción de acceso a la información. El criterio de la norma dice: _ningún usuario accede a datos de otro, y todo intento denegado queda registrado_.
> **El intento:** con la sesión de U-03, que es un usuario estándar, voy a pedir un evento, un contacto y una suscripción que son de U-04. Son 12 intentos en total, sobre 6 endpoints y las dos identidades cruzadas.
> **El resultado:** [ejecuta] los 12 devolvieron 404. Ninguno devolvió datos de U-04.
> **La traza:** en `audit_events` hay 12 entradas `access.denied`, con U-03, el recurso, la hora y la IP de origen.
> **El dictamen:** conforme. El control no solo existe, **resistió el intento** de un usuario legítimo de alcanzar datos de otro, y dejó rastro."**

Ese molde es lo que la profesora pidió: **no decir "es conforme", sino mostrar que se intentó y no se pudo.**

### 9.2 La prueba de fuego con dos actores va dentro del bloque 2

Se ejecuta con **dos integrantes en dos terminales** (y el tercero en la app):

- **Terminal 1 — U-03**: sesión legítima, creando un evento y suscribiendo un contacto.
- **Terminal 2 — U-04**: ejecuta el acceso cruzado a los recursos de U-03 → denegado.
- **Terminal 3 — U-01**: fuerza bruta contra la cuenta de U-03 → bloqueo, mientras U-03 **sigue trabajando**.

**Lo que se demuestra y se dice:** *"El control no se probó en un sistema en reposo: se probó con usuarios legítimos operando. El ataque fue denegado, el bloqueo por fuerza bruta noMCscream la sesión legítima, y todo quedó registrado."*

### 9.3 Reglas de ensayo

- El bloque 1 no pasa de 3 min (cronometrado).
- Cada integrante sustenta **su** ítem sin leer, y puede **volver a ejecutar su script en vivo** si le piden más detalle.
- Los 2 NC se muestran **sin eufemismo**: se ve el ataque funcionar. Es el momento de mayor valor de la exposición y no debe suavizarse.
- **Plan B grabado** (P2 L288): el video de las 9 pruebas de fuego es también el seguro si falla la red el día de la exposición.

---

## 10. Riesgos y pivotes predefinidos

| Riesgo | Mitigación / pivot |
|---|---|
| **La profesora no acepta la matriz de hallazgos** | Se presenta en el pacto (F1) **antes** de construir. Si rechaza una OM → esa fila pasa a NC y se reasigna: hay 4 OM y 2 NC de margen. Si rechaza un NC → se cambia el ítem plantado, no se maquilla el dictamen |
| **A.5.17 y A.8.5 se contaminan** por el token en `localStorage` | Partición de alcance explícita en la columna I. **Pivot:** si ella insiste en que el almacenamiento del token pertenece a A.8.5, se mueve el ítem a A.8.5 → A.8.5 pasa a NC y el CONFORME se reasigna a otro control (A.8.3 o A.5.15). Decidido en el pacto, no en la exposición |
| **El NC de A.5.17 depende del `.env` dentro de la imagen** | `backend/.env` es local y **gitignored**: nunca se versiona. La imagen se construye en local y se destruye. La evidencia es la **extracción**, no la publicación de la imagen |
| **Repositorio público + paquete de evidencias** | Los secretos del laboratorio se generan en runtime desde `.env` local; `.env.example` versionado con placeholders; evidencia **redactada** (mascarar contraseñas y connection strings en capturas). `gitleaks` se corre en **F0**, no en F6: el hallazgo favorable no puede ser una sorpresa el día 6 |
| **No hay red / corte de internet** | Plan B: grabar el bloque 2. Backend y Mongo en Docker local, sin Atlas ni Firebase |
| **Falta de tiempo** (7 días) | La palanca es **recortar superficie del laboratorio**, no functionality: el panel de logs se resuelve con `mongosh` + CSV + endpoint de solo lectura; el frontend solo hace el login en 2 pasos. Si hay que recortar ítems, se recortan filas de la lista, nunca las 3 fases de un CONFORME |
| **El entorno no está listo** (sin venv, sin `node_modules`, sin imagen de mongo, sin `.env`) | **F0 incluye la preparación del entorno**, hoy por la noche. `yarn install` de CRA 5 + React 19 necesita red: se lanza primero |
| **Falta la matriz de activos del Parcial 1** | La columna G (justificación) la necesita. Si no existe, se reconstruye desde el contexto de AppNotify y se declara como reconstrucción |
| **Confundir desviación parcial con OM** (error #5 de la profesora) | Regla dura: cualquier desviación medida contra el criterio ⇒ NC. Solo es OM si el criterio se cumple **al 100 %** y la ineficiencia está en el **mantenimiento** |
| **Un NC en un ítem hunde el control completo** | Regla de la profesora. Por eso cada NC está **en un control con un solo ítem**, y no hay ítems compartidos entre controles sin declarar el dueño |
| **Un CONFORME se rompe en la prueba de fuego** | El hallazgo cambia a NC y se repacta. Es el criterio, no la expectativa. §2.5 |
| **Un NC se comporta bien** | Se documenta con la evidencia de configuración y se reasigna el NC a otro ítem plantado (hay margen: 4 OM, 2 NC) |
| **Una prueba de fuego sale ambigua** | No se dictamina: se repite, se amplía la muestra del ítem, o se declara la limitación en las conclusiones |
| **El script falla en vivo el día de la exposición** | Los scripts son re-ejecutables y hay video de respaldo (modalidad C). Un re-run fallido **es** evidencia válida y se explica en vivo |
| **Se ajusta el criterio después de ver el resultado** | Prohibido. El criterio se congela en F2. Si estaba mal, se corrige la norma y se **re-audita el ítem completo**, documentando el cambio |
| **El ataque de la exposición toca datos reales** | El laboratorio usa datos sintéticos. Los correos de prueba van al buzón del equipo |

---

## 11. Lo que NO vamos a hacer

- **No** construir un SIEM, un IdP empresarial ni un IAM completo: 4 módulos y una app navegable, no una plataforma.
- **No** escanear terceros ni ejecutar exploits fuera del laboratorio.
- **No** corregir los dos NC **antes** de la exposición: son la evidencia.
- **No** presentar teoría de la norma en el bloque 1: el marco conceptual va en las notas del orador.
- **No** proponer soluciones a los NC: se dictamina y se documenta.
- **No** construir panel de logs en React: `mongosh` + CSV + endpoint de solo lectura cumplen el requisito.

---

## 12. Decisiones tomadas

| # | Decisión | Estado |
|---|---|---|
| 1 | Fecha de exposición | **Se resuelve internamente.** El plan usa días relativos (Día 1 = mañana) y el pacto queda en Día 2 |
| 2 | Reescribir la autenticación a credenciales locales | **Autorizado.** `scrypt` + TOTP (`pyotp`) + sesión opaque en Mongo; se tocan `LoginPage`, `AuthContext`, `api.js`, `auth.py`, `models.py` |
| 3 | Repositorio GitHub | **Se mantiene público** durante la exposición → es la evidencia del NC de A.8.4. Se corrige en el plan de acción del Parcial 3 |
| 4 | Matriz de activos del Parcial 1 | **No existe** → se reconstruye en F2 y **se declara como reconstrucción** (§5.3) |
| 5 | Integrantes | **2-3**, reparto por frente de evidencia (§5.2) |
| 6 | Credenciales de Firebase/Atlas | **No se usan.** Laboratorio autocontenido: `mongod` en Docker, cero dependencia externa |

---

## 13. Los primeros 60 minutos (lo que haces al abrir esto mañana)

1. `yarn install` en `frontend/` (necesita red; es lo más lento del entorno).
2. `python -m venv .venv` + `pip install -r backend/requirements.txt` + `pip install pyotp`.
3. `docker pull mongo:8` y levantar `mongod` con TLS (CA propia) — §3.3.
4. `gitleaks detect --source .` sobre el historial → es evidencia **favorable** de A.5.17 y tiene que estar resuelta antes, no el día 6.
5. Redactar la **Norma de Control de Acceso** y la **matriz de comportamiento del muestreo** → subir el borrador de la lista de chequeo a Classroom.
6. Mandar el borrador. **Sin el borrador en Classroom, la reunión de pacto del Día 2 no produce nada y todo el cronograma se cae.**

**Y un paso más, que es el que define el nivel de la exposición:**

7. Escribir el **ataque de cada una de las 9 pruebas de fuego** en una sola hoja (`audit/templates/pruebas-de-fuego.md`): qué se intenta, con qué identidad, contra qué recurso, qué debería pasar y qué evidencia lo demuestra. **Esa hoja es el guion del bloque 2**, y se escribe *antes* de construir, porque es lo que se pacta con la profesora.

> Con eso, la exposición deja de ser "revisar 9 controles" y pasa a ser **"intentar 9 veces hacer algo que no debería ser posible, y demostrar qué pasó"**. Ahí es donde se gana el 70 % de la rúbrica.
