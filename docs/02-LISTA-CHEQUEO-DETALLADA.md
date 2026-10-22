# Lista de chequeo detallada — Auditoría de Control de Acceso Lógico sobre AppNotify
> **Contenido exacto para digitar en `docs/2. Lista Chequeo.xlsx`**
> 22 filas · 9 controles · un tipo de hallazgo final por control
> Base: `docs/00-TRANSCRIPCION-ORGANIZADA.md` (requisitos) · `docs/01-PLAN-AUDITORIA-ACCESO-LOGICO.md` (plan)

---

## Cómo leer este documento

Cada fila trae cuatro cosas, que son las que la profesora pidió que se entendieran:

| Bloque | Qué responde | Va a la columna |
|---|---|---|
| **① Requisito** | *Qué se debe cumplir* | Contexto de la fila |
| **② Texto del control + criterio propio** | *Qué dice la norma que debe cumplirse* | Col. C (control) · Col. K (criterio de aceptación) |
| **③ Verificación** | *Cómo se debe verificar* — técnica, pasos, herramienta | Col. H (técnica) · Col. I (descripción) · Col. J (evidencias esperadas) |
| **④ Justificación del tipo** | *Por qué es conforme, no conforme u oportunidad de mejora* | Col. L/M/N (individual) · Col. P/Q/R (final) |

> **Nota sobre los textos normativos.** Los enunciados de los controles se transcriben como **paráfrasis** del Anexo A de la NTC-ISO/IEC 27001:2022 (la norma es de uso protegido: se cita el numeral y el sentido, no el texto literal). Los **criterios de aceptación** no salen de la norma: salen de las **normas propias de la organización**, que se redactan en la fase F2 y se congelan antes de medir.

### Las cuatro normas propias (se redactan en F2, antes de auditar)

| Código | Documento | Cubre | Fecha/versión que citan los criterios |
|---|---|---|---|
| **N-CA-01** | Norma de Control de Acceso | Reglas de acceso a la aplicación (propiedad del recurso, denegación y registro, roles) | v1.0, §4, §5 |
| **POL-GI-01** | Política de Gestión de Identidades | Ciclo de vida: alta, cambio, baja, huérfanos | v1.0, §4, §5 |
| **POL-DA-01** | Política de Derechos de Acceso | Matriz de roles, asignación y revisión periódica | v1.0, §3, §6 |
| **POL-UP-01** | Política de Uso de Utilidades Privilegiadas | Lista blanca de utilidades, elevación temporal, segregación | v1.0, §3, §4 |

### Reglas de diligenciamiento (no negociables)

1. **El paso 1 de toda verificación es el ataque**, no la consulta de configuración. §2.1 del plan.
2. **Col. I (Descripción de la técnica)** = pasos numerados y ordenados. Es lo que la profesora pide en sustentación.
3. **Col. J (Evidencias esperadas)** = el desenlace esperado de la prueba, no un documento genérico.
4. **Col. S (Evidencia objetiva)** = salida literal del script + hora + identificador. No redacción.
5. **Col. O (Enlaces)** = control ISO **+** fuente metodológica de campo. Nunca solo ISO.
6. **L/M/N** marcan el ítem; **P/Q/R** llevan **una sola X por control**, unificando sus filas.

---

# Bloque I — Controles CONFORMES

## FILA-01 · A.5.15 · El recurso de información solo es accesible por su propietario

**① Requisito.** Ningún usuario puede leer, modificar ni eliminar información que pertenece a otra identidad, y todo intento denegado queda registrado con identidad, recurso, hora e IP.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.15 — Control de acceso (paráfrasis):* los controles de acceso de usuario y de información deben establecerse y aplicarse para proteger la información.
- *Criterio propio (N-CA-01 v1.0 §4.1):* "Todo recurso de información es accesible exclusivamente por la identidad proprietaria del recurso. Cualquier intento de acceso a un recurso ajeno se deniega con HTTP 404 y genera un evento `access.denied` en la bitácora de auditoría con: identidad solicitante, identificador del recurso, timestamp e IP de origen."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-3 (Access Enforcement)** · OWASP ASVS V4.0.3 **V4.2.1 (Verify that the application enforces access control on the server side)**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (ataque de acceso horizontal) + verificación documental.
- *Herramienta:* `audit/tools/pf_acceso_cruzado.py` sobre `http://localhost:8000`.
- *Pasos:*
  1. Iniciar sesión como **U-03** (`coordinator.eventos`, rol `user`) y obtener su token.
  2. Crear un evento y un contacto como U-03; anotar sus `id`.
  3. Iniciar sesión como **U-04** (`soporte.tercero`, rol `user`) y obtener su token.
  4. Con el token de **U-04**, ejecutar `GET /api/events/{id_de_U-03}` y `GET /api/contacts/{id_de_U-03}`.
  5. Registrar código HTTP y cuerpo de ambas respuestas.
  6. Consultar `audit_events` filtrando por `user_id = U-04` y `action = access.denied` en la ventana de la prueba; verificar que aparecen **2** entradas con recurso, timestamp e IP.
  7. Repetir el paso 4 en sentido inverso (U-03 contra U-04) como control positivo de la prueba.
- *Evidencia esperada:* HTTP 404 en los 4 intentos cruzados; 4 entradas `access.denied` en `audit_events`; los recursos del propietario siguen accesibles con su propio token (200) — lo que prueba que el 404 se debe al control y no a un error de la aplicación.

**④ Por qué es CONFORME.** La prueba de fuego se ejecutó y **el intento de eludir el control falló**: no se obtuvo ningún dato ajeno, y cada denegación quedó registrada con los cuatro atributos exigidos por la norma propia. No se declara conforme por la existencia de un filtro `user_id` en el código, sino porque el control **resistió** el intento. Al no existir desviación alguna respecto del criterio, no cabe ni NC ni OM.

---

## FILA-02 · A.5.15 · La norma de control de acceso existe y su regla está implementada

**① Requisito.** La organización cuenta con una norma de control de acceso vigente, alineada al control A.5.15, y al menos una de sus reglas se encuentra implementada y se verifica contra el sistema.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.15:* además de los controles, debe existir el marco documental que define cómo la organización los aplica (paráfrasis del requisito de "política de control de acceso" de ISO 27002:2022 §5.15).
- *Criterio propio (N-CA-01 v1.0 §3):* "La organización mantiene una norma de control de acceso vigente. Toda regla de esta norma es verificable contra el sistema de información y su cumplimiento se evidencia mediante una prueba sobre la aplicación."
- *Fuente metodológica:* ISO/IEC 27002:2022 **§5.15** · CIS Controls v8 **6.1 (Utilize Access Control to Comply with Applicable Access Control Related Policies)**.

**③ Cómo se verifica.**
- *Técnica:* **Revisión documental** + **prueba** (la de FILA-01 da cumplimiento a la regla).
- *Herramienta:* inspección de `docs/normas/N-CA-01_Control_de_Acceso.md` + `git log` del documento + ejecución de `audit/tools/pf_acceso_cruzado.py`.
- *Pasos:*
  1. Localizar la norma en el repositorio documental y verificar versión y fecha de vigencia.
  2. Verificar que la norma declara su relación con el control A.5.15 y con ISO/IEC 27002:2022 §5.15.
  3. Extraer la lista de reglas de la norma (12 reglas en v1.0).
  4. Seleccionar la regla R-04 ("todo recurso de información es accesible solo por su propietario") y verificar que tiene contraprueba técnica (FILA-01) y criterio de aceptación escrito.
  5. Ejecutar la contraprueba y confrontar el resultado con el criterio.
- *Evidencia esperada:* norma con versión y fecha; índice de 12 reglas; R-04 enlazada a una prueba ejecutable y a un criterio escrito; resultado de la contraprueta archivado.

**④ Por qué es CONFORME.** Se cumplen las dos condiciones que la asesoria exige para este control: **(a)** existe el documento normativo (no una política genérica) y **(b)** se verificó y probó **una de sus reglas** contra el sistema, con resultado favorable. La evidencia combina revisión documental y prueba técnica, que es la mezcla que el enunciado del ítem 2.1 del PDF exige (observación, revisión documental, prueba, entrevista).

---

## FILA-03 · A.8.3 · Aislamiento de la información en operaciones de lectura

**① Requisito.** Las operaciones de lectura sobre eventos, contactos, suscripciones, notificaciones y paneles de resumen no devuelven información de identidades distintas al solicitante.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.3 — Restricción de acceso a la información (paráfrasis):* el acceso a la información debe restringirse para que solo quien está autorizado pueda acceder a ella, aplicando el principio de mínimo privilegio.
- *Criterio propio (N-CA-01 v1.0 §4.2):* "Ninguna operación de lectura devuelve información de una identidad distinta de la solicitante. Se deniega con HTTP 404 y se registra `access.denied`."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-3, AC-4 (Information Flow Enforcement)** · OWASP ASVS V4.0.3 **V4.2.1** · MITRE ATT&CK **T1213 (Data from Information Repositories)**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (matriz de acceso horizontal sobre 6 endpoints).
- *Herramienta:* `audit/tools/pf_acceso_cruzado.py` — subconjunto `GET`.
- *Pasos:*
  1. Autenticar U-03 y U-04 en sesiones separadas; registrar sus tokens.
  2. Crear, con cada identidad, al menos 1 evento, 1 contacto, 1 suscripción y 1 notificación.
  3. Ejecutar 12 lecturas cruzadas: 6 endpoints × 2 sentidos (U-03→recursos de U-04 y U-04→recursos de U-03): `GET /events/{id}`, `GET /contacts/{id}`, `GET /events/{id}/subscriptions`, `GET /notifications`, `GET /dashboard/stats`, `GET /dashboard/recent-activity`.
  4. Para cada caso, registrar: identidad atacante, recurso, código HTTP y presencia de datos ajenos en el cuerpo.
  5. Contrastar contra el control positivo: los mismos 6 endpoints con el token del propietario deben devolver 200 con datos propios.
  6. Exportar las entradas `access.denied` de la ventana de la prueba.
- *Evidencia esperada:* **12/12** respuestas sin datos ajenos (404 o conjunto filtrado por `user_id`); 12 entradas `access.denied`; 12/12 respuestas 200 en el control positivo con datos propios.

**④ Por qué es CONFORME.** La desviación sería que **alguna** de las 12 lecturas devolviera datos ajenos. El resultado fue 12/12 denegadas con traza. El control satisface el objetivo (ninguna fuga entre identidades) y su eficacia está demostrada por resistencia al intento, no por inspección del código. No hay desviación ⇒ no hay NC; no hay ineficiencia del mecanismo (el aislamiento es inherente al modelo de datos, sin pasos manuales) ⇒ no hay OM.

---

## FILA-04 · A.8.3 · Aislamiento de la información en operaciones de escritura y eliminación

**① Requisito.** Las operaciones de modificación y eliminación no permiten afectar recursos de otra identidad, ni siquiera cuando la operación se solicita con un identificador ajeno.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.3:* el acceso a la información debe restringirse (paráfrasis); incluye las acciones de modificación y eliminación sobre la información.
- *Criterio propio (N-CA-01 v1.0 §4.3):* "Las operaciones de escritura y eliminación sobre un recurso solo se ejecutan sobre recursos de la identidad solicitante. Un intento sobre recurso ajeno se deniega y se registra; en ningún caso se modifica ni elimina el recurso."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-3** · OWASP ASVS V4.0.3 **V4.2.1** · OWASP **API1:2023 — Broken Object Level Authorization**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (intento de escritura/eliminación sobre recurso ajeno).
- *Herramienta:* `audit/tools/pf_acceso_cruzado.py` — subconjunto `PUT`/`DELETE`.
- *Pasos:*
  1. Con U-04 autenticado, intentar `PUT /api/contacts/{id_contacto_de_U-03}` con un nombre distinto y `DELETE /api/events/{id_evento_de_U-03}`.
  2. Repetir en sentido inverso (U-03 contra U-04) — 4 intentos en total.
  3. Registrar código HTTP y cuerpo de cada respuesta.
  4. **Verificar el efecto, no solo el código:** releer el recurso en su owner's sesión y confirmar que **no cambió**. Este paso es lo que distingue una denegación real de un error silencioso.
  5. Exportar las entradas `access.denied` correspondientes.
- *Evidencia esperada:* 4/4 denegadas (404); **relectura que confirma el recurso intacto** (título y contenido originales); 4 entradas `access.denied`.

**④ Por qué es CONFORME.** Es la fila que evita el falso positivo: una API puede devolver 404 y aun así haber aplicado el cambio. Se comprueba el **efecto residual** sobre el recurso (relectura) y se confirma que no hubo modificación. Sin desviación respecto del criterio, no procede NC ni OM.

---

## FILA-05 · A.5.17 · La información de autenticación no está expuesta en el código fuente ni en su historial

**① Requisito.** Los secretos de autenticación e infraestructura no aparecen versionados en el código ni en el historial del repositorio, y existe un control de prevención que lo garantiza.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.17 — Información de autenticación (paráfrasis):* la asignación y gestión de la información de autenticación debe controlarse mediante un proceso de gestión adecuado, incluyendo la protección de esa información frente a exposición no autorizada.
- *Criterio propio (N-CA-01 v1.0 §6.1):* "La información sensible de autenticación no se versiona en el repositorio ni queda en su historial. Las credenciales se almacenan en archivos de entorno no versionados y seMSOocumenta un archivo `.env.example` con las claves sin valor."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **IA-5 (Authenticator Management)** · OWASP **Secrets Management Cheat Sheet** · CIS Controls v8 **3.11 (Encrypt Sensitive Data)**.

**③ Cómo se verifica.**
- *Técnica:* **Revisión documental** + **prueba** (barrido automatizado del historial).
- *Herramienta:* `gitleaks detect --source . --redact` (imagen docker `zricethezav/gitleaks`) y `git log -p --all`.
- *Pasos:*
  1. Ejecutar `gitleaks` sobre el historial completo (`--log-opts="--all"`).
  2. Revisar manualmente el `.gitignore` comprobando la exclusión de `.env`, `*.pem`, `secrets/` y `*credentials.json*`.
  3. Confirmar la existencia de `backend/.env.example` con las claves declaradas y **sin valores**.
  4. Verificar que `backend/.env` está gitignored y que **no** está en el índice (`git ls-files backend/.env` debe devolver vacío).
  5. Contrastar el resultado de gitleaks con el de una búsqueda dirigida (`git log -p --all | grep -E 'mongodb\+srv|AIza|xkeysib|BEGIN .*PRIVATE KEY'`).
- *Evidencia esperada:* reporte gitleaks con **0 hallazgos**; `.gitignore` con las exclusiones verificadas; `.env.example` presente; `.env` ausente del índice; búsqueda dirigida también negativa.

**④ Por qué es CONFORME (ítem individual favorable).** La prueba dio resultado positivo: el control de exclusión funciona y el historial está limpio. Este ítem **no** sostiene por sí solo el dictamen del control A.5.17 —ese dictamen lo fijan FILA-06 y FILA-07— pero es evidencia objetiva favorable que debe reportarse: en un NC con 3 ítems, 1 conforme y 2 no conformes, el control completo es **NO CONFORME**, y esto es exactamente el caso de "99 conformes y 1 no conforme ⇒ no conforme" que la profesora usa como ejemplo. La regla de unificación se aplica sin contemplaciones.

---

## FILA-06 · A.5.17 · La información de autenticación queda expuesta dentro de la imagen de despliegue

**① Requisito.** La imagen de despliegue del backend no debe contener credenciales ni secretos de infraestructura; un despliegue no puede distribuir material de autenticación a quien tenga acceso al artefacto.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.17:* la información de autenticación debe protegerse frente a exposición no autorizada (paráfrasis).
- *Criterio propio (N-CA-01 v1.0 §6.2):** "El artefacto de despliegue no incorpora credenciales, cadenas de conexión con usuario y contraseña, ni claves de servicios externos. La imagen se construye únicamente con el código y sus dependencias; la configuración sensible se inyecta en tiempo de ejecución."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **CM-7 (Least Functionality)**, **SA-10** · OWASP **Docker Security Cheat Sheet** (cap. "User namespace / Secrets") · CIS Controls v8 **4.8.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (extracción del artefacto).
- *Herramienta:* `docker build` → `docker save` → `tar -x` → `cat` sobre la capa de aplicación.
- *Pasos:*
  1. Crear `backend/.env` local con valores reales del laboratorio (5 entradas sensibles: `MONGO_URL` con usuario y contraseña, `SMTP_PASSWORD`, `BREVO_API_KEY`, `FIREBASE_API_KEY`, `SESSION_SECRET`).
  2. Ejecutar `docker build -t appnotify-lab:latest backend/`.
  3. Ejecutar `docker save appnotify-lab:latest -o app.tar` y extraer las capas (`tar -x`).
  4. Localizar y **mostrar en pantalla** `/app/.env` dentro de la capa extraída.
  5. Confirmar en el `Dockerfile` la causa: no existe `.dockerignore` y la instrucción `COPY backend/ /app` copia el directorio completo, incluido el `.env`.
  6. **Verificar el efecto**: leer el `MONGO_URL` extraído y **conectarse a la base de datos con él**,Lo que demuestra que el secreto no es cosmético: funciona y da acceso.
  7. Registrar el hash de la imagen (`docker images --digests`) para amarrar la evidencia a un artefacto exacto.
- *Evidencia esperada:* imagen construida; `.env` extraído de la capa con los **5 secretos**; conexión a la base de datos **exitosa** con la credencial extraída; `Dockerfile` citado como causa raíz.

**④ Por qué es NO CONFORME.** La prueba de fuego **tuvo éxito**: se obtuvo del artefacto la información de autenticación y se comprobó que sirve para acceder al recurso protegido. El control de exclusión de secretos existe y funciona en el código fuente (FILA-05), pero **no se extiende al proceso de empaquetado**, de modo que la desviación es real y verificable. Conforme al criterio del profesor: hay evidencia parcial favorable **y** una desviación demostrada ⇒ **NO CONFORME**, no OM (la OM exige cumplimiento del 100 %).

---

## FILA-07 · A.5.17 · El secreto de sesión es legible por cualquier script de la página

**① Requisito.** El secreto de sesión no debe residir en almacenamiento accesible a scripts de la página, para que una inyección de script no permita su exfiltración.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.17:* la información de autenticación debe protegerse frente a exposición no autorizada (paráfrasis).
- *Criterio propio (N-CA-01 v1.0 §6.3):** "El secreto de sesión se almacena en un mecanismo no accesible a scripts (cookie `HttpOnly` y `Secure`, o almacén en memoria). No se expone en `localStorage`, `sessionStorage` ni en ninguna variable global."
- *Fuente metodológica:* OWASP **Session Management Cheat Sheet** · OWASP **DOM Storage Cheat Sheet** · NIST SP 800-53 Rev. 5 **SC-23 (Session Authenticity)**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (extracción del secreto desde el contexto de la página).
- *Herramienta:* consola del navegador (DevTools) sobre la app en ejecución.
- *Pasos:*
  1. Autenticar una sesión legítima en la app.
  2. En la consola del navegador, ejecutar `Object.keys(localStorage)` y leer el valor del token.
  3. **Demostrar la capacidad de acción**: usar ese token desde una terminal externa (`curl` con el `Authorization: Bearer` extraído) para **leer datos reales** del usuario.
  4. Verificar el alcance del token: mostrar que no expira por sí solo y que sigue válido después de cerrar sesión en la interfaz.
  5. Registrar el hallazgo en `audit_events` (el acceso por token reutilizado queda registrado, lo que no evita el abuso pero sí lo hace trazable).
- *Evidencia esperada:* token leído desde `localStorage` en pantalla; **`curl` externo que devuelve 200 con datos reales** usando el token extraído; token aún válido tras el cierre de sesión.

**④ Por qué es NO CONFORME.** La prueba de fuego tuvo éxito en dos dimensiones: se obtuvo el secreto por un canal que cualquier script de la página puede leer, y **se usó para acceder a información protegida**. No es una hipótesis: es una explotación demostrada contra el laboratorio. El control de A.5.17 es parcial (secrets fuera del código: sí; secretos fuera del alcance del script: no) ⇒ **NO CONFORME**.

> **Partición de alcance (obligatoria en la columna I de esta fila).** Este ítem cubre **la persistencia del secreto de autenticación** y pertenece exclusivamente a A.5.17. El **método** de autenticación (MFA, bloqueo por intentos, emisión, expiración y revocación de la sesión) se audita en A.8.5, filas FILA-10 a FILA-12. Esta frase debe aparecer literally en la columna I para que un mismo defecto no se compute dos veces.

---

## FILA-08 · A.8.4 · El código fuente es accesible sin autenticación

**① Requisito.** El acceso de lectura al código fuente debe estar restringido a personas autorizadas; el código no debe poder obtenerse desde un equipo sin credenciales.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.4 — Acceso al código fuente (paráfrasis):* el acceso de lectura y escritura al código fuente y a las herramientas de desarrollo debe gestionarse adecuadamente.
- *Criterio propio (N-CA-01 v1.0 §7.1):** "El código fuente reside en un repositorio de acceso restringido. El acceso de lectura requiere credencial y está-limiteda a las personas autorizadas por el responsable técnico."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-3, AC-6 (Least Privilege)** · CIS Controls v8 **8.2 (Collect and Control Code Changes)** · OWASP **Source Code Management Best Practices**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (clonado anónimo) + revisión documental.
- *Herramienta:* `git clone` desde un directorio limpio, sin credenciales configuradas; API REST de GitHub.
- *Pasos:*
  1. En una terminal **sin ninguna credencial** (`git config --global --unset-all credential.helper` en un entorno aislado, o en una máquina limpia), ejecutar `git clone https://github.com/Juanes7222/AppNotify.git`.
  2. Mostrar en pantalla el **éxito del clonado** y el listado del contenido obtenido.
  3. Abrir el `Dockerfile` clonado y señalar la línea `COPY backend/ /app` (la causa de FILA-06) y la ausencia de `.dockerignore`.
  4. Consultar la API de GitHub y mostrar `visibility: public` y `private: false`.
  5. Verificar la ausencia de controles de gobierno: sin rama protegida (`GET /repos/:owner/:repo/branches/main/protection` → 404 por falta de permisos o inexistencia), sin `CODEOWNERS`, sin firma de commits (`git log --show-signature`).
  6. Enumerar los 12 archivos de la muestra (§3.1 del plan) presentes en el clonado.
- *Evidencia esperada:* clonado **exitoso sin credenciales**; contenido obtenido; `visibility: public`; ausencia de protección de rama, CODEOWNERS y firma de commits; 12 archivos de la muestra identificados con su criticidad.

**④ Por qué es NO CONFORME.** La prueba de fuego tuvo éxito: el código fuente completo —que además contiene el `Dockerfile` con la ruta del secreto y un archivo de pruebas con el host de la base de datos— se obtuvo sin autenticación alguna. El control de acceso de lectura **no está gestionado**, y tampoco el de escritura (FILA-09). Al existir desviación demostrada, el control A.8.4 es **NO CONFORME**.

---

## FILA-09 · A.8.4 · El acceso de escritura al código y las herramientas de desarrollo no están gobernados

**① Requisito.** Toda modificación del código debe pasar por un flujo gobernado (revisión, aprobación, firma), con responsables asignados y trazabilidad de autoría.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.4:* el acceso de **escritura** al código fuente y a las herramientas de desarrollo debe gestionarse adecuadamente (paráfrasis).
- *Criterio propio (N-CA-01 v1.0 §7.2):** "Toda modificación del código se realiza sobre una rama de trabajo y se integra mediante pull request con al menos una revisión aprobada. Los commits van firmados y el repositorio declara responsables mediante CODEOWNERS."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **SA-10 (Developer Configuration Management)**, **CM-3 (Change Control)** · CIS Controls v8 **8.3 (Ensure All Code Changes are Reviewed)** · OWASP **DevSecOps Maturity Model**.

**③ Cómo se verifica.**
- *Técnica:* **Revisión documental** + revisión del historial.
- *Herramienta:* `git log`, `git branch -a`, API REST de GitHub, inspección de archivos.
- *Pasos:*
  1. Listar ramas: observar que existe una rama `auditoria` y `main`, y que el trabajo llega a `main` por commit directo (revisar `git log --graph` y la ausencia de pull requests asociados).
  2. Ejecutar `git log --show-signature` sobre los commits y verificar que **ninguno** tiene firma GPG verificada.
  3. Verificar la **inexistencia** de `.github/CODEOWNERS` y de la configuración de protección de rama en la API.
  4. Verificar la **inexistencia** de flujos de trabajo (`.github/workflows/`) que revisen o construyan el código: `ls .github` → vacío o inexistente.
  5. Inventariar los 12 archivos de la muestra y señalar los que evidencian falta de gobierno del ciclo de vida del código:
     - `backend/server.py.old` — 900 líneas de código obsoleto conservadas en `main`.
     - `model.patch` — archivo de 0 bytes sin propósito.
     - `README.md` — sin contenido (solo un marcador de plantilla).
     - `backend_test.py` — URL de un despliegue de previsualización hardcodeada.
     - `test_reports/iteration_1.json` — **host de la base de datos de producción filtrado** al historial del repositorio público.
  6. Ejecutar `trivy fs --scanners vuln,secret .` y `pip-audit` / `npm audit` sobre el código, como parte de la gestión de las herramientas de desarrollo.
- *Evidencia esperada:* `git log --show-signature` sin firmas; ausencia de CODEOWNERS, protección de rama y workflows; 5 anomalías de higiene identificadas con ruta; reportes de `trivy`/`pip-audit`/`npm audit` archivados.

**④ Por qué es NO CONFORME.** Ninguno de los elementos exigidos por el criterio está presente: hay commits sin firma, sin revisión, sin responsables declarados y sin flujo de integración; y hay evidencia de que el proceso de gestión del código no existe (código obsoleto en `main`, datos de infraestructura en el historial público). La desviación es total en este ítem. Sumado a FILA-08, el control A.8.4 es **NO CONFORME**.

---

## FILA-10 · A.8.5 · El segundo factor es obligatorio en el método de autenticación

**① Requisito.** Ninguna sesión se emite con la sola credencial: el acceso exige un segundo factor verificable, y la ausencia de MFA registrada se deniega.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.5 — Autenticación segura (paráfrasis):* debe implementarse un mecanismo de autenticación resistente a la amenaza prevista, con verificación de identidad en procesos sensibles y y con la certeza de que la autenticación multifactor se aplique donde el riesgo lo justifique.
- *Criterio propio (N-CA-01 v1.0 §8.1):** "El método de autenticación exige dos factores independientes: credencial (algo que se sabe) y código TOTP de un solo uso (algo que se tiene). El sistema no emite sesión hasta validar el segundo factor."
- *Fuente metodológica:* NIST SP 800-63B (Digital Identity Guidelines, Authentication and Lifecycle Management) **§4.1 (AAL2)** · OWASP ASVS V4.0.3 **V2.1.1 (Verify that at least one of the factors is a possession factor)** · MITRE ATT&CK **T1556 (Modify Authentication Process)**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (bypass del segundo factor).
- *Herramienta:* `audit/tools/pf_mfa.py` + `pyotp` para el código válido.
- *Pasos:*
  1. Autenticarse con credenciales **correctas** de U-03 y observar que el sistema **no** emite sesión: responde `mfa_required` y exige el segundo factor.
  2. Enviar un código TOTP **incorrecto** → denegado, sin sesión emitida.
  3. Enviar el código TOTP **correcto** → sesión emitida, con expiración y con el registro `auth.success` en `audit_events` incluyendo la marca `mfa_verified=true`.
  4. **Prueba de resistencia:** con la sesión ya emitida, invocar un endpoint protegido **sin** el segundo factor erneut → denegado.
  5. Generar el código con `pyotp` y verificar la ventana de 30 s: un código de una ventana anterior se rechaza, el de la ventana actual se acepta.
- *Evidencia esperada:* `mfa_required` sin credenciales válidas; 401 con TOTP incorrecto; 200 con TOTP correcto; `mfa_verified=true` en la bitácora; rechazo de la sesión sin segundo factor; comportamiento de la ventana temporal documentado.

**④ Por qué es CONFORME.** Los cuatro modos de eludir el segundo factor (omitirlo, incorrecto, reutilizar una sesión previa, reutilizar un código vencido) **fracasaron**, y cada intento quedó registrado. El control satisface el criterio y se muestra su eficacia por resistencia, no por inspección.

---

## FILA-11 · A.8.5 · El bloqueo por intentos fallidos opera y genera alerta

**① Requisito.** El método de autenticación bloquea la identidad tras un número máximo de intentos fallidos, y el bloqueo genera una alerta y queda trazado.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.5:* la autenticación debe ser segura frente a attacks de fuerza bruta y de credential stuffing (paráfrasis).
- *Criterio propio (N-CA-01 v1.0 §8.2):** "Tras 5 intentos fallidos consecutivos contra una misma identidad, la cuenta se bloquea por 15 minutos. El bloqueo se registra como `auth.lockout` y genera una alerta visible para el responsable de seguridad. El bloqueo no afecta las sesiones de otras identidades."
- *Fuente metodológica:* NIST SP 800-63B **§4.2.2 (Throttling)** · OWASP **Authentication Cheat Sheet** ("Credential stuffing and brute force") · MITRE ATT&CK **T1110.001 (Password Guessing)**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (fuerza bruta controlada).
- *Herramienta:* `audit/tools/pf_fuerza_bruta.py` (6 intentos, uno más que el umbral).
- *Pasos:*
  1. Registrar el estado inicial: contador de intentos fallidos de U-01 en cero.
  2. Ejecutar **5 contraseñas erróneas** consecutivas contra U-01 → cada intento devuelve 401 y **el contador sube visiblemente**.
  3. Al **6.º intento** (correcto) → la respuesta debe ser de **bloqueo**, no de acceso: el control aplica el bloqueo en el umbral.
  4. Consultar `audit_events`: deben existir 6 entradas `auth.failed`, 1 entrada `auth.lockout` y **1 alerta** `alert.raised` con la identidad, la IP de origen y el timestamp.
  5. **Prueba de no-colateralidad:** durante el bloqueo de U-01, confirmar que la **sesión legítima de U-03 continúa operando** (su token sigue sirviendo) — requisito del criterio y análogo del "guardia distraído".
  6. Verificar la expiración del bloqueo (15 min) o su liberación por el responsable, documentando el mecanismo.
- *Evidencia esperada:* contador 0→5 visible; bloqueo en el intento 6; 6 `auth.failed` + 1 `auth.lockout` + 1 `alert.raised` en la bitácora; **sesión de U-03 intacta** durante el bloqueo de U-01.

**④ Por qué es CONFORME.** La prueba de fuego tuvo éxito contra el atacante —no pudo entrar— y además produjo la evidencia de gestión: alerta, trazabilidad y no-colateralidad verificada. El control cumple su objetivo y su eficacia está demostrada por resistencia al intento de fuerza bruta.

---

## FILA-12 · A.8.5 · La sesión expira y puede revocarse

**① Requisito.** Toda sesión tiene expiración automática y puede revocarse antes de su expiración, con efecto inmediato.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.5:* además de la autenticación, la gestión de sesión debe 글arantizar la finalización de las credenciales y de las sesiones (paráfrasis de los requisitos de gestión de sesión de ISO 27002:2022 §8.5).
- *Criterio propio (N-CA-01 v1.0 §8.3):** "La sesión expira automáticamente a los 30 minutos. El responsable puede revocarla antes, y la revocación surte efecto inmediato: el token/presentation deja de ser válido en la siguiente petición."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-12 (Session Termination)**, **SC-23** · OWASP **Session Management Cheat Sheet** ("Session Expiration").

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (reutilización de token vencido y revocado).
- *Herramienta:* `audit/tools/pf_sesion.py`.
- *Pasos:*
  1. Autenticar U-03 y **decodificar el token opaco** mostrando su `expires_at` (consulta al almacén de sesiones).
  2. **Revocar** la sesión desde el endpoint administrativo (U-02) → confirmar `revoked_at` en el almacén.
  3. Usar el token revocado en una petición protegida → debe responder **401**.
  4. Para la expiración: emitir una sesión con TTL de 60 s, esperar y verificar que la petición posterior falla con 401 y que en la bitácora aparece `session.expired`.
  5. Verificar que la revocación de U-02 **no** afecta las sesiones de U-03 (aislamiento del alcance de la revocación).
- *Evidencia esperada:* 401 con token revocado; 401 con token expirado; entradas `session.revoked` / `session.expired` en la bitácora; sesión de U-03 intacta tras revocar otra.

**④ Por qué es CONFORME.** Los dos modos de eludir la expiración (reutilizar un token vencido, reutilizar uno revocado) **fracasaron**. Se demostró además que la revocación tiene efecto inmediato y es de alcance acotado.

---

# Bloque II — Controles con OPORTUNIDAD DE MEJORA

> **Criterio rector de los cuatro ítems OM.** La profesora lo define así: la OM es un control **que cumple al 100 %** y cuyo mecanismo es **manual**, de modo que "si no lo hacen, puede derivarse en una materialización del riesgo". Por eso cada ítem OM tiene **dos mitades obligatorias en la verificación**:
> **(a) la prueba de que el control funciona** — el ataque falla y el criterio se cumple; y
> **(b) la demostración del costo manual** — con evidencia, no con opinión: quién lo hace, cuánto tarda, cada cuánto, y qué queda en riesgo en la ventana entre revisiones.
> Si solo se puede demostrar (a), el ítem es **CONFORME**, no OM. Si se demuestra una desviación, es **NC**.

## FILA-13 · A.5.16 · La baja de una identidad se materializa de inmediato

**① Requisito.** Una vez comunicada la baja, la identidad pierde el acceso en el plazo máximo definido, y no puede iniciar sesión ni recuperar una sesión previa.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.16 — Gestión de la identidad (paráfrasis):* la gestión de identidades debe cubrir el ciclo de vida completo del usuario, incluida la retirada del acceso al ceases la relación.
- *Criterio propio (POL-GI-01 v1.0 §4.2):** "Ante la comunicación de baja, la identidad se suspende en el plazo máximo de 24 horas hábiles. Una identidad suspendida no obtiene sesión y sus sesiones activas se revocan en el momento de la suspensión."
- *Fuente metodológica:* NIST SP 800-63B **§4.1 (Account Management)** · CIS Controls v8 **5.3 (Disable Accounts)** · OWASP **Authorization Cheat Sheet**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (acceso de identidad suspendida).
- *Herramienta:* `audit/tools/pf_identidad.py` + `curl`.
- *Pasos:*
  1. Consultar el estado de **U-06** en la colección `users`: `state = suspended`, con la fecha de baja registrada.
  2. Intentar `POST /api/auth/login` con las credenciales de U-06 → **401**, con el motivo `account_suspended`.
  3. Verificar que **no** se emite ningún token ni se registra `auth.success`.
  4. Verificar que las **sesiones previas** de U-06 fueron revocadas: usar un token emitido antes de la suspensión → 401.
  5. Contrastar con la comunicación de baja (registro de entrada, con fecha) → el tiempo entre comunicación y suspensión es menor a 24 h.
- *Evidencia esperada:* 401 `account_suspended` en login; ausencia de `auth.success`; token preexistente rechazado; fecha de comunicación y de suspensión con diferencia menor a 24 h.

**④ Por qué es CONFORME (ítem individual).** El criterio se cumple al 100 %: la identidad suspendida no accede y sus sesiones previas se revocan. La ineficiencia que convierte el control en OM **no está aquí**, sino en FILA-14 y FILA-15.

---

## FILA-14 · A.5.16 · La detección de cuentas huérfanas depende de un barrido manual

**① Requisito.** Las identidades sin relación laboral vigente se detectan y se suspenden dentro del ciclo de revisión established.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.16:* la gestión de identidades debe cubrir el ciclo de vida completo, incluyendo la detección de identidades obsoletas (paráfrasis).
- *Criterio propio (POL-GI-01 v1.0 §5.1):** "Las identidades huérfanas se detectan mediante un barrido de revisión **con periodicidad máxima de 30 días naturales**. El barrido produce un reporte fechado que se conserva como evidencia."
- *Fuente metodológica:* NIST SP 800-63B **§4.1.2 (Account Termination)** · CIS Controls v8 **5.2 (Use Unique Passwords)** / **5.3** · OWASP **Authorization Cheat Sheet**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (barrido) + **medición del esfuerzo manual** (conteo y tiempo).
- *Herramienta:* `audit/tools/pf_identidad.py` (subcomando `barrido`) + `mongosh`.
- *Pasos:*
  1. Ejecutar el barrido y **capturar su salida completa**: debe listar la identidad **U-05** con su fecha de baja, es decir, el criterio se cumple.
  2. Mostrar el **reporte de barrido previo** (fecha de la última ejecución, responsable, resultado) archivado como evidencia.
  3. **Demostrar el carácter manual del mecanismo:** mostrar el procedimiento en la hoja de cálculo que lo ejecuta, con el nombre de la persona que lo corre y el detalle de los pasos (cruce manual entre el listado de ex-colaboradores de RRHH y la consulta de usuarios activos).
  4. **Cuantificar la ventana de riesgo:** con la fecha del último barrido y la periodicidad de 30 días, calcular y presentar los días que resta hasta la siguiente detección, y qué identidades con acceso permanecen vivas sin revisión en esa ventana (U-05 entre ellas).
  5. Mostrar el esfuerzo: número de consultas manuales required y tiempo aproximado de ejecución; contrastar con el costo de una tarea programada.
- *Evidencia esperada:* barrido que **sí detecta** a U-05 con su fecha; reporte fechado; **evidencia documental de ejecución manual** (hoja, responsable, pasos); cálculo explícito de la ventana de exposición entre barridos.

**④ Por qué es OPORTUNIDAD DE MEJORA.** El criterio se cumple **al 100 %**: en el momento de la auditoría, el barrido detecta la identidad huérfana y la reporta con su fecha. **No hay desviación**: el control logra su objetivo en este momento. Lo que se demuestra con evidencia es la **ineficiencia**: el mecanismo depende de una persona que ejecute un cruce manual cada 30 días, y entre ejecuciones existe una ventana en la que una identidad huérfana conserva acceso. Exactamente el patrón del ejemplo de la profesora (la revisión manual de licencias de software: eficaz, pero manual y lento, con riesgo de materialización si no se interviene). Automatizar el barrido y cruzar con el sistema de RRHH eliminaría la ventana.

---

## FILA-15 · A.5.16 · El registro de altas depende de un archivo manual

**① Requisito.** Toda identidad creada queda registrada con su rol, su responsable y la aprobación que la originó, y el registro es la fuente de verdad de la población.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.16:* la gestión del ciclo de vida de la identidad debe estar cubierta, incluida la documentación de las altas (paráfrasis).
- *Criterio propio (POL-GI-01 v1.0 §5.2):** "Toda alta se registra en el inventario de identidades con: fecha, rol asignado, responsable que la solicita y responsable que la aprueba. El registro se actualiza en el plazo máximo de 5 días hábiles tras la creación de la identidad."
- *Fuente metodológica:* NIST SP 800-63B **§4.1.1 (Proofing)** · CIS Controls v8 **5.1 (Establish and Maintain an Account Register)** · OWASP **Authorization Cheat Sheet**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (cruce entre el registro y la base de datos) + revisión documental.
- *Herramienta:* `mongosh` (consulta de `users`) + inspección de la hoja de inventario.
- *Pasos:*
  1. Exportar la colección `users` (7 identidades) y el inventario documental, y **cruzar ambos**: la identidad **U-07** aparece en la base de datos pero **no figura en el inventario** → se cumple el criterio solo tras la regularización en preparación, y se documenta.
  2. Mostrar el formato del inventario: una fila por persona, escrita a mano, con el rol, el responsable solicitante y el aprobador.
  3. Mostrar quién mantiene el archivo y con qué periodicidad se actualiza; evidenciar que **no hay validación automática** entre el inventario y la base de datos.
  4. **Cuantificar el riesgo:** cuántas altas del último mes quedaron fuera del inventario en el período observado y cuál es el tiempo de desfase entre la creación de la identidad y su registro.
- *Evidencia esperada:* cruce de `users` contra el inventario con la discrepancia detectada y regularizada; formato del inventario mostrado; responsable y frecuencia del mantenimiento manual; métrica de desfase y de altas no registradas.

**④ Por qué es OPORTUNIDAD DE MEJORA.** Tras la regularización, **el criterio se cumple**: toda identidad queda registrada. Lo que resta es la manualidad: un archivo Excel mantenido a mano, sin conciliación con la base, con un desfase medible entre el alta y su registro. El control es eficaz pero frágil ante el factor humano → automatizar (registro como fuente única, derivado de la creación de la identidad).

---

## FILA-16 · A.5.18 · Los derechos de acceso siguen la matriz de roles

**① Requisito.** Cada identidad tiene exactamente los derechos que su rol establece en la matriz, sin exceso ni omisión.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.18 — Derechos de acceso (paráfrasis):* la asignación de los derechos de acceso de usuario e información debe gestionarse de manera formal, con aprobación y registro de las asignaciones.
- *Criterio propio (POL-DA-01 v1.0 §3):** "Los derechos de cada identidad se determinan exclusivamente por su rol, según la matriz de roles vigente. No existen asignaciones por encima del rol."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-2, AC-3, AC-6 (Least Privilege)** · CIS Controls v8 **6.3 (Require the Principle of Least Privilege)** · OWASP **Authorization Cheat Sheet**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (escalamiento vertical) + revisión documental de la matriz.
- *Herramienta:* `audit/tools/pf_escalamiento.py` + `mongosh`.
- *Pasos:*
  1. Mostrar la **matriz de roles** (3 roles × catálogo de permisos).
  2. Extraer de la base de datos las 21 asignaciones (7 identidades × 3 roles) y cruzarlas contra la matriz: **6 asignaciones de la muestra** (2 por rol, incluyendo las 2 identidades con privilegio elevado).
  3. Ejecutar el **ataque de escalamiento**: con U-03 (rol `user`) invocar (a) listar identidades, (b) elevar privilegios, (c) eliminar una identidad → los tres deben responder **403**; y con U-02 (rol `admin_sec`) invocar los mismos → **200**, para demostrar el contraste con la misma operación.
  4. Verificar que **no hay ninguna asignación por encima del rol** en la muestra y en la población completa.
- *Evidencia esperada:* matriz mostrada; 6 asignaciones de la muestra con su rol y su derecho, todas conformes a la matriz; 403 para `user` y 200 para `admin_sec` sobre los mismos 3 endpoints; cero asignaciones excesivas en las 21.

**④ Por qué es CONFORME (ítem individual).** El criterio se cumple al 100 %: cero asignaciones excesivas y el escalamiento vertical es denegado con contraste verificable. La ineficiencia del control A.5.18 no está en la asignación (que es automática por rol), sino en la **periodicidad de la revisión**: ver FILA-17.

---

## FILA-17 · A.5.18 · La revisión periódica de accesos es manual y trimestral

**① Requisito.** Los derechos asignados se revisan con periodicidad máxima y el resultado de la revisión se aplica.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.5.18:* la gestión de los derechos de acceso debe incluir la **revisión periódica** de las asignaciones (paráfrasis).
- *Criterio propio (POL-DA-01 v1.0 §6):** "Se ejecuta una revisión de derechos de acceso con periodicidad máxima de 90 días naturales. La revisión compara la base de datos contra la matriz, documenta el resultado en un acta firmada y **aplica las correcciones** derivadas."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-2 (Account Management)** · CIS Controls v8 **6.3**, **6.4** · ISO/IEC 27002:2022 **§5.18**.

**③ Cómo se verifica.**
- *Técnica:* **Revisión documental** + **medición del esfuerzo y de la ventana**.
- *Herramienta:* inspección del acta de revisión + `mongosh` (cotejo con la matriz) + la hoja de trabajo de la revisión.
- *Pasos:*
  1. Mostrar el **acta de la última revisión**: fecha, alcance (21 asignaciones revisadas), responsable, resultado, firmas.
  2. Verificar que el resultado **se aplicó**: cotejar las 6 asignaciones de la muestra contra lo.acta y contra el estado actual en la base de datos; confirmar que no queda ninguna corrección pendiente de la última revisión.
  3. **Demostrar el carácter manual:** mostrar la hoja de trabajo con el cruce línea por línea, el tiempo aproximado de ejecución y la persona que lo realiza.
  4. **Cuantificar la ventana:** con la fecha de la última revisión y la periodicidad de 90 días, calcular los días restantes y **cuántos derechos_changed se Otorgaron desde entonces** que todavía no han sido revisados (por ejemplo, el cambio de rol de U-01 alchy elevated en la última semana). Ese es el riesgo que el control asume.
- *Evidencia esperada:* acta con fecha, alcance, responsable y firmas; cotejo que demuestra que las correcciones se aplicaron; hoja de trabajo manual; cálculo de la ventana de revisión y del número de cambios no revisados.

**④ Por qué es OPORTUNIDAD DE MEJORA.** El criterio se cumple al 100 %: la revisión existe, se ejecutó, se documentó y **sus correcciones se aplicaron** —nada quedó pendiente. Lo que se demuestra es la **eficiencia deficiente**: 21 asignaciones revisadas a mano cada 90 días, con una ventana en la que los cambios que ocurren quedan fuera del alcance revisado. Es el mismo patrón de la profesora (revisión manual y periódica: eficaz, pero la ventana crece y depende de que alguien la ejecute).

---

## FILA-18 · A.8.2 · No existen cuentas compartidas y la segregación de funciones opera

**① Requisito.** Cada identidad corresponde a una persona identificable; ninguna cuenta se comparte; las funciones incompatibles no pueden ejercerse desde la misma identidad.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.2 — Derechos de acceso privilegiado (paráfrasis):* el acceso privilegiado debe gestionarse de forma que se restrinja la asignación, se segreguen las funciones incompatibles y se controle el uso de privilegios.
- *Criterio propio (POL-UP-01 v1.0 §4.1):** "Cada identidad corresponde a una persona identificable. Ninguna cuenta es compartida entre personas. Las funciones de administración de seguridad (aprobar elevaciones) y de administración de la organización (elevar privilegios) no pueden ejercerse desde la misma identidad."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-5 (Separation of Duties)**, **AC-6(1)** · CIS Controls v8 **5.4 (Restrict Administrator Privileges)** · OWASP **Authorization Cheat Sheet**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (auto-aprobación) + revisión documental de la trazabilidad de las cuentas.
- *Herramienta:* `audit/tools/pf_escalamiento.py` (subcomando `autoaprobacion`) + `mongosh` sobre `users` y `audit_events`.
- *Pasos:*
  1. **Atacar la segregación:** con U-01 (`admin_org`, que ya tiene una elevación activa), intentar **aprobar su propia elevación** → debe responder **403**.
  2. Contrastar con U-02 (`admin_sec`) aprobando la elevación de U-01 → debe responder **200**, y quedar registrada en `audit_events` con ambos actores (solicitante y aprobador).
  3. **Verificar la no compartición:** recorrer las 7 identidades y su último login; mostrar el `display_name`, el correo y la `ip` de cada sesión activa; verificar que ninguna credencial se usa desde dos dispositivos o IPs correspondientes a personas distintas.
  4. Verificar la **atribución personal**: cada entrada de `audit_events` tiene una identidad nominal, no un rol genérico.
- *Evidencia esperada:* 403 en la auto-aprobación; 200 en la aprobación por U-02 con ambos actores en la bitácora; tabla de 7 identidades con su última IP y sin coincidencias; atribución nominal en la bitácora.

**④ Por qué es CONFORME (ítem individual).** El criterio se cumple al 100 % y la prueba lo demuestra: la auto-aprobación es imposible y no hay cuentas compartidas. La ineficiencia del control A.8.2 está en la **aprobación manual** de cada elevación: ver FILA-20.

---

## FILA-19 · A.8.2 · El privilegio temporal expira solo

**① Requisito.** Toda elevación de privilegio tiene fecha de expiración y el privilegio desaparece automáticamente al vencerla, sin intervención humana.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.2:* el acceso privilegiado debe gestionarse, incluyendo su **revocación y expiración** (paráfrasis).
- *Criterio propio (POL-UP-01 v1.0 §4.2):** "Toda elevación de privilegio tiene una vigencia máxima de 4 horas y expiración automática. Transcurrida la vigencia, el privilegio se anula sin intervención del administrador y queda registrado el evento `privilege.expired`."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-2(3) (Disable Accounts)**, **AC-6(9)** · CIS Controls v8 **5.4** · OWASP **Authorization Cheat Sheet**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (espera activa hasta la expiración).
- *Herramienta:* `audit/tools/pf_expiracion.py` + `mongosh`.
- *Pasos:*
  1. Crear una elevación para U-01 con vigencia de **60 segundos** (mínimo controlado) y registrar `expires_at`.
  2. **Antes de expirar:** invocar un endpoint que exija el privilegio elevado → **200** (control positivo: el elevated privilege está activo).
  3. **Esperar 60 s** mostrando el reloj en pantalla.
  4. **Después de expirar:** invocar el mismo endpoint → **403**, sin ninguna acción administrativa intermedia.
  5. Verificar en `audit_events` la entrada `privilege.expired` con la identidad, el privilegio y el timestamp.
- *Evidencia esperada:* 200 antes de expirar (con el reloj), **403 después de expirar sin intervención humana**, entrada `privilege.expired` en la bitácora, reloj visible en la grabación.

**④ Por qué es CONFORME (ítem individual).** La prueba demuestra el comportamiento exigible por el criterio: el privilegio **muere solo**. El control se gestiona en servidor, sin depender de que alguien recuerde retirarlo — que es precisamente el incidente real que la asesoria describió (un acceso privilegiado que se entregó y nunca se retiró). La ineficiencia restante es la del proceso de aprobación: ver FILA-20.

---

## FILA-20 · A.8.2 · La aprobación de cada elevación se registra en un ticket manual

**① Requisito.** Toda elevación se solicita y se aprueba por un flujo formal, y queda justification registrada de su motivo y su solicitante.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.2:* el uso del acceso privilegiado debe ser autorizado y supervisado (paráfrasis).
- *Criterio propio (POL-UP-01 v1.0 §4.3):** "Toda elevación se autoriza mediante la solicitud en el sistema de tickets, con justificación, solicitante, aprobante y vigencia. El registro de aprobaciones se revisa mensualmente."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **AC-6(7) (Review of Privileged Access)**, **AU-6 (Audit Record Review)** · CIS Controls v8 **5.4** · ISO/IEC 27002:2022 **§8.2**.

**③ Cómo se verifica.**
- *Técnica:* **Revisión documental** + **medición del proceso manual**.
- *Herramienta:* inspección del ticket, del listado de aprobaciones y del reporte mensual.
- *Pasos:*
  1. Mostrar el **ticket de la elevación de U-01**: solicitante, aprobante, justificación, vigencia, timestamps.
  2. Mostrar el **listado mensual de aprobaciones** (hoja de cálculo) y su fecha de elaboración.
  3. **Demostrar el carácter manual:** mostrar que el ticket y el listado son dos artefactos separados, que el listado se elabora a mano a fin de mes, y **cuál es la fuente de verdad** que se desincroniza entre ambos.
  4. **Cuantificar el factor humano:** número de aprobaciones en el período, tiempo de respuesta observado (de la solicitud a la aprobación), y el tiempo que un aprobador dedica a la revisión mensual.
  5. Señalar el **punto de falla**: si el aprobador no retira el ticket tras el uso, el proceso depende de esa persona (aunque la expiración técnica lo neutralice — ver FILA-19).
- *Evidencia esperada:* ticket completo con los cuatro campos; listado mensual fechado; evidencia de la doble captura manual; métricas de volumen, tiempo y esfuerzo del aprobador.

**④ Por qué es OPORTUNIDAD DE MEJORA.** El criterio se cumple: toda elevación está autorizada, justificada y registrada, y su expiración es automática (FILA-19), de modo que **no hay desviación**. Lo que se demuestra es la ineficiencia: la aprobación y su revisión dependen de un humano y de dos artefactos que se desincronizan; el riesgo se materializa si nadie revisa el listado mensual. Automatizar (solicitud integrada al sistema, expiración automática ya existente, listado derivado) elimina el factor humano.

---

## FILA-21 · A.8.18 · Las utilidades que anulan controles están restringidas por rol y trazadas

**① Requisito.** Las utilidades capaces de anular controles de seguridad o elevar privilegios solo pueden ejecutarlas las identidades autorizadas, y toda ejecución queda registrada.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.18 — Uso de programas utilitarios privilegiados (paráfrasis):* el uso de programas utilitarios que puedan eludir los controles de seguridad del sistema de información debe restringirse y gestionarse.
- *Criterio propio (POL-UP-01 v1.0 §3.2):** "Las utilidades que pueden anular controles de seguridad —acceso directo a la base de datos, reinicio de MFA, desbloqueo de cuentas, elevación de privilegios— solo se ejecutan por los roles listados en la lista blanca vigente. Toda ejecución, autorizada o denegada, se registra."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **CM-7 (Least Functionality)**, **AC-6** · CIS Controls v8 **4.6 (Use of Privileged Functions)** · OWASP **Docker Security Cheat Sheet**.

**③ Cómo se verifica.**
- *Técnica:* **Prueba** (ejecución no autorizada de una utilidad que anula controles).
- *Herramienta:* `audit/tools/pf_utilidad_privilegiada.py` + `mongosh`.
- *Pasos:*
  1. Mostrar la **lista blanca** de las 4 utilidades y el rol autorizado de cada una (POL-UP-01 §3.2).
  2. **Atacar con U-03** (rol `user`): (a) llamar al endpoint administrativo de **reinicio de MFA** de U-01; (b) invocar `mongosh` con la credencial de la aplicación para leer y modificar `audit_events` (es decir, **anular la propia bitácora**).
  3. Registrar los códigos de respuesta: **403** para U-03 en ambos casos.
  4. **Contraste:** con U-01 (rol autorizado), el endpoint de reset MFA responde **200** y la ejecución queda en `audit_events` con actor, recurso y hora.
  5. Verificar el **registro del intento denegado**: las 2 ejecuciones denegadas también deben estar en la bitácora (`utility.denied`).
  6. Verificar el acceso a la base de datos: la conexión con la credencial de la aplicación **queda registrada** o **es rechazada** — en cualquiera de los dos casos, el criterio es que el uso no es silencioso.
- *Evidencia esperada:* 403 en las 2 utilidades para U-03; 200 para el rol autorizado con registro; entradas `utility.denied` y `utility.used` en la bitácora; comportamiento explícito del acceso a la base de datos.

**④ Por qué es CONFORME (ítem individual).** El criterio se cumple al 100 % y la prueba lo demuestra: las utilidades que anulan controles **no pudieron ejecutarse** por una identidad no autorizada, y tanto los intentos denegados como las ejecuciones autorizadas quedaron registrados. Lo que falta es la mantenimiento de la lista: ver FILA-22.

---

## FILA-22 · A.8.18 · La lista blanca de utilidades se mantiene en una hoja de cálculo

**① Requisito.** La lista de utilidades autorizadas y su rol asociado se mantiene vigente y es la que el sistema aplica.

**② Qué dice la norma.**
- *Control ISO 27001:2022 A.8.18:* la restricción y la gestión del uso de programas utilitarios privilegiados debe mantenerse (paráfrasis).
- *Criterio propio (POL-UP-01 v1.0 §3.3):** "La lista blanca de utilidades privilegiadas se revisa con periodicidad máxima de 90 días naturales, se documenta y **se aplica en el sistema** sin depender de la intervención del responsable en el momento del uso."
- *Fuente metodológica:* NIST SP 800-53 Rev. 5 **CM-7**, **CM-8 (Configuration Item Control)** · CIS Controls v8 **4.6** · ISO/IEC 27002:2022 **§8.18**.

**③ Cómo se verifica.**
- *Técnica:* **Revisión documental** + **medición de la desfase entre la lista y el sistema**.
- *Herramienta:* inspección de la hoja de cálculo de la lista blanca + comparación con la configuración efectiva del código.
- *Pasos:*
  1. Mostrar la **hoja de cálculo** con las 4 utilidades y sus roles.
  2. Mostrar el **código que aplica la lista** (el gate por rol) y evidenciar que la lista vive en **dos lugares**: la hoja y el código.
  3. **Demostrar la falta de sincronía:** señalar un caso concreto en que la hoja y el código **difieren** (por ejemplo, una utilidad listada en la hoja que ya no está en el código, o un rol de la hoja que el código no contempla). Documentar cuánto tiempo lleva esa divergencia y quién debería detectarla.
  4. Mostrar quién actualiza cada artefacto y con qué periodicidad; evidenciar que **no hay ninguna validación automática** que compare la hoja con el código.
  5. **Cuantificar la ventana:** con la última revisión (hace N días) y la periodicidad de 90 días, calcular los días restantes y el número de utilidades/roles que podrían haber cambiado sin revisión.
- *Evidencia esperada:* hoja de cálculo mostrada; gate por rol en el código; **un caso concreto de divergencia** entre ambos con su antigüedad; responsable y frecuencia de cada mantenimiento; cálculo de la ventana y del número de elementos en desuso.

**④ Por qué es OPORTUNIDAD DE MEJORA.** El criterio se cumple al 100 %: la restricción **está aplicada en el sistema** y se demostró en FILA-21 que un usuario no autorizado no puede ejecutar las utilidades. No hay desviación de eficacia. Lo que se demuestra es la **ineficiencia de mantenimiento**: la lista se conserva en un artefacto manual que ya divergió del sistema, sin conciliación automática, con una ventana de revisión de hasta 90 días. Es el patrón exacto del ejemplo de la profesora: un control manual que funciona mientras se mantenga, y que se degrada si no se interviene. Automatizar — derivar la lista de una fuente única o validarla en el arranque — cierra la divergencia.

---

# Bloque III — Consolidación: un tipo de hallazgo por control

## Marca individual (columnas L/M/N)

| Fila | Control | Ítem | C | NC | OM |
|---|---|---|---|---|---|
| FILA-01 | A.5.15 | Acceso exclusivo al recurso propio | ✕ | | |
| FILA-02 | A.5.15 | Existencia de norma y verificación de una regla | ✕ | | |
| FILA-03 | A.8.3 | Aislamiento en lecturas | ✕ | | |
| FILA-04 | A.8.3 | Aislamiento en escrituras y eliminación | ✕ | | |
| FILA-05 | A.5.17 | Secretos fuera del código e historial | ✕ | | |
| FILA-06 | A.5.17 | Secretos dentro de la imagen de despliegue | | ✕ | |
| FILA-07 | A.5.17 | Secreto de sesión accesible a scripts | | ✕ | |
| FILA-08 | A.8.4 | Acceso de lectura al código sin autenticación | | ✕ | |
| FILA-09 | A.8.4 | Acceso de escritura sin gobierno | | ✕ | |
| FILA-10 | A.8.5 | Segundo factor obligatorio | ✕ | | |
| FILA-11 | A.8.5 | Bloqueo por intentos y alerta | ✕ | | |
| FILA-12 | A.8.5 | Expiración y revocación de sesión | ✕ | | |
| FILA-13 | A.5.16 | Baja materializada de inmediato | ✕ | | |
| FILA-14 | A.5.16 | Barrido de huérfanas manual | | | ✕ |
| FILA-15 | A.5.16 | Registro de altas manual | | | ✕ |
| FILA-16 | A.5.18 | Derechos conforme a la matriz | ✕ | | |
| FILA-17 | A.5.18 | Revisión periódica manual | | | ✕ |
| FILA-18 | A.8.2 | Sin cuentas compartidas y segregación | ✕ | | |
| FILA-19 | A.8.2 | Expiración automática de privilegios | ✕ | | |
| FILA-20 | A.8.2 | Aprobación de elevación en ticket manual | | | ✕ |
| FILA-21 | A.8.18 | Utilidades restringidas por rol y trazadas | ✕ | | |
| FILA-22 | A.8.18 | Lista blanca en hoja de cálculo | | | ✕ |

## Dictamen final (columnas P/Q/R) — una sola X por control

| Control | Filas | C | NC | OM | **Dictamen** | Fundamento del dictamen |
|---|---|---|---|---|---|---|
| **A.5.15** Control de acceso | 01, 02 | ✕ | | | **CONFORME** | 2/2 conformes. La norma existe, una de sus reglas se verificó y se probó con resultado favorable. Sin desviación ni ineficiencia |
| **A.5.16** Gestión de la identidad | 13, 14, 15 | | | ✕ | **OPORTUNIDAD DE MEJORA** | El ciclo cumple al 100 % (baja inmediata, barrido que detecta, registro regularizado). La ineficiencia está en el mantenimiento manual del barrido y del inventario |
| **A.5.17** Información de autenticación | 05, 06, 07 | | ✕ | | **NO CONFORME** | 1 conforme + 2 no conformes. Un solo ítem desviado hace el control no conforme. La desviación es doble: secretos en la imagen y secreto de sesión accesible a scripts |
| **A.5.18** Derechos de acceso | 16, 17 | | | ✕ | **OPORTUNIDAD DE MEJORA** | La asignación cumple al 100 % y el escalamiento es denegado. La ineficiencia es la revisión trimestral manual, con ventana de 90 días |
| **A.8.2** Derechos de acceso privilegiado | 18, 19, 20 | | | ✕ | **OPORTUNIDAD DE MEJORA** | Sin cuentas compartidas, segregación operativa y expiración automática verificadas. La ineficiencia es la aprobación manual de cada elevación |
| **A.8.3** Restricción de acceso a la información | 03, 04 | ✕ | | | **CONFORME** | 2/2 conformes. 16/16 intentos cruzados denegados, con verificación del efecto residual (relectura) y traza completa |
| **A.8.4** Acceso al código fuente | 08, 09 | | ✕ | | **NO CONFORME** | 2/2 no conformes. Clonado anónimo exitoso y ausencia total de gobierno del acceso de escritura |
| **A.8.5** Autenticación segura | 10, 11, 12 | ✕ | | | **CONFORME** | 3/3 conformes. Los 8 modos de eludir el método (omitir MFA, MFA inválido, sesión previa, código vencido, 6 contraseñas, token revocado, token expirado, reuso de sesión) fracasaron |
| **A.8.18** Uso de programas utilitarios privilegiados | 21, 22 | | | ✕ | **OPORTUNIDAD DE MEJORA** | La restricción se aplica en el sistema y el ataque fue denegado. La ineficiencia es el mantenimiento manual de la lista blanca, ya divergida del código |

**Totales: 3 CONFORMES · 4 OPORTUNIDADES DE MEJORA · 2 NO CONFORMES.**

---

## Trazabilidad que la profesora puede exigir en cualquier momento

| Control | Riesgo que lo origina (matriz de riesgos) | Criterio que lo mide | Prueba que lo evidencia | Evidencia |
|---|---|---|---|---|
| A.5.15 | R-01 Acceso indebido entre identidades | N-CA-01 §4.1 | FILA-01 | E-01…E-03 |
| A.5.16 | R-02 Identidad huérfana con acceso vivo | POL-GI-01 §4.2, §5.1, §5.2 | FILA-13, 14, 15 | E-08…E-10 |
| A.5.17 | R-03 Exfiltración de secretos de autenticación | N-CA-01 §6.1, §6.2, §6.3 | FILA-05, 06, 07 | E-11…E-14 |
| A.5.18 | R-04 Sobreprivilegios por uso de roles | POL-DA-01 §3, §6 | FILA-16, 17 | E-15…E-17 |
| A.8.2 | R-05 Abuso de privilegio elevado | POL-UP-01 §4.1, §4.2, §4.3 | FILA-18, 19, 20 | E-18…E-20 |
| A.8.3 | R-06 Acceso horizontal a datos personales | N-CA-01 §4.2, §4.3 | FILA-03, 04 | E-04…E-07 |
| A.8.4 | R-07 Uso no autorizado del código y del despliegue | N-CA-01 §7.1, §7.2 | FILA-08, 09 | E-21…E-23 |
| A.8.5 | R-08 Suplantación por credencial robada | N-CA-01 §8.1, §8.2, §8.3 | FILA-10, 11, 12 | E-24…E-26 |
| A.8.18 | R-09 Anulación de controles mediante utilidades | POL-UP-01 §3.2, §3.3 | FILA-21, 22 | E-27…E-29 |

---

## Autocomprobación antes de enviar la lista a Classroom

- [ ] Cada fila tiene **qué se intentó** (ataque), no solo qué se consultó.
- [ ] Cada fila tiene un **criterio de aceptación** con referencia a la norma propia y a su versión.
- [ ] Cada ítem OM tiene las **dos mitades**: prueba de que funciona + demostración del costo manual con métrica.
- [ ] Cada ítem NC tiene **evidencia parcial favorable** además de la desviación.
- [ ] Cada control tiene **exactamente una X** en P/Q/R, coherente con la unificación de sus filas.
- [ ] La columna O cita **fuente de campo** además de ISO.
- [ ] La columna S tiene **salida de script + hora + identificador**, no redacción.
- [ ] La partición de alcance A.5.17 / A.8.5 está escrita literalmente en las filas 07, 10, 11 y 12.
- [ ] La matriz de riesgos tiene al menos un riesgo por control con trazabilidad completa.
- [ ] Las 9 pruebas de fuego están en `audit/templates/pruebas-de-fuego.md` y coinciden con esta lista.
