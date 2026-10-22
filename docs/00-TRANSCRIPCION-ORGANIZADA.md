# Dossier organizado — Parcial II: Auditoría técnica de seguridad de la información
> **Control de acceso lógico sobre AppNotify (RemindSender)**
> Fuente: `docs/PARCIAL 2.pdf` (especificación oficial), `docs/PARCIAL2.md` (transcripción de la clase), `docs/ASESORIA.md` (asesoría específica de acceso lógico), `docs/ITEMS.md` (controles asignados), `docs/2. Lista Chequeo.xlsx` (plantilla maestra).
> Compilado: 21-oct-2026. Las citas `(P2 Lxx)` = transcripción del parcial; `(ASE Lxx)` = transcripción de asesoría; `(PDF pN)` = página del PDF oficial.

---

## 1. Qué es la actividad

| Concepto | Definición | Fuente |
|---|---|---|
| Objetivo | Auditoría técnica de seguridad de la información, de alcance delimitado y **basada en muestreo**, mediante la evaluación de requisitos y controles de **NTC-ISO/IEC 27001:2022**. | PDF p1 |
| Naturaleza | Simulación académica: diagnóstico de madurez, muestreo justificado, pruebas controladas y evidencias verificables. | PDF p1 |
| Rol del equipo | **Doble rol**: (1) *fase de preparación* = área de TI que configura el laboratorio; (2) *fase de auditoría* = auditores que ejecutan y dictaminan. | PDF p1 §2.2 |
| Duración | 60 minutos por equipo, cronometrada. | PDF p1 |
| Fecha de inicio | PDF: "Jueves 29 de octubre (Modalidad Virtual)". Verbal: "las exposiciones inician el 27 de octubre"; acceso físico y **acceso lógico exponen primero**. | PDF p1 / P2 L286 |
| Rúbrica | 70 % ejecución técnica + defensa de eficacia · 20 % lista de chequeo e indexación de hallazgos · 10 % claridad, coherencia y tiempo. | PDF p13 / P2 L274 |
| Entregables | (1) Registro de lista de chequeo en Excel, diligenciada. (2) Presentación y sustentación práctica. | PDF p8 |

---

## 2. La paradoja del auditor — reglas de independencia

> "El auditor no debe fabricar, alterar, ocultar ni presentar evidencias artificiales… su responsabilidad consiste en obtener y evaluar evidencia objetiva frente a criterios previamente establecidos." (PDF p1 §2.1)

Reglas que rigen todo el ejercicio:

1. **El auditor no repara.** No cierra puertos, no altera código, no redacta políticas, no construye plan de acción durante la fase de auditoría. (P2 L18, L28)
2. **El auditor no da soluciones.** No propone cómo resolver el problema ni dicta planes de acción al auditado: "perdería su independencia y objetividad". (PDF p6)
3. **El auditor dictamina y documenta** el estado: conforme / no conforme / oportunidad de mejora, sustentado en evidencia. (PDF p6)
4. **Excepción pedagógica — el laboratorio sí se construye.** En la fase de preparación el equipo configura el entorno, prepara cuentas y **simula escenarios de funcionamiento correcto y de debilidad de seguridad**. En la fase de auditoría ese entorno ya existe y solo se verifica. (PDF p1 §2.2)
5. **El plan de acción del parcial 3 no es de este parcial.** El ejercicio NO termina en planes de acción; solo se incluye evidencia de plan de acción *ya ejecutado* cuando sirve para probar la eficacia de un control conforme. (P2 L28, L242)

---

## 3. Metodología: muestreo, codiseño de escenarios y pacto previo

### 3.1 Muestreo (obligatorio)

Cada equipo debe:

- Identificar la **población total** de elementos relacionados con los controles evaluados.
- Seleccionar una **muestra concreta, delimitada y técnicamente justificada**.
- Definir **criterios de selección**: criticidad para el negocio, sensibilidad de la información, exposición a amenazas, privilegios de acceso, funciones desempeñadas, riesgos identificados y características del control objeto de auditoría.
- **No está prohibido indicar cuántos elementos se evalúan**, pero es obligatorio **explicar por qué** se seleccionaron esos y qué permite comprobar su evaluación. (PDF p3 §1)
- La justificación debe **remitirse al análisis de contexto y a la valoración de activos críticos del Parcial 1**. (P2 L50)

> Referencia del PDF (Tabla 1, p3): 5 repositorios inventariados → se auditan 2 (40 % de la población, R-01 y R-02), por criticidad de servicios y superficie de exposición.

### 3.2 Codiseño de escenarios y pacto con la docente

1. La **lista de chequeo se envía por Classroom** en la fecha indicada por la docente, **antes** de la reunión.
2. En la reunión el equipo **acuerda con la docente**: qué elementos de la muestra operan con eficacia total y cuál **fallará deliberadamente de forma controlada** (falso negativo técnico).
3. **Todo debe estar pactado y aprobado.** "No puedo valer una no conformidad que no haya sido pactada conmigo." (P2 L61–L68)

### 3.3 Reglas de arquitectura documental

- La auditoría se ejecuta contra **NTC-ISO/IEC 27001:2022 + la arquitectura documental de la organización**. La norma dice *qué* hacer; la arquitectura documental dice *cómo* lo hace la organización. Primero se valida que lo que se muestra corresponda a la norma; después se revisa según el *cómo* de la organización. (ASE L110)
- **Tipología documental** (taller Equilibrium): política, norma, regla y procedimiento son documentos distintos. Para el control de acceso lógico, A.5.15 **exige un documento obligatorio**: una **norma de control de acceso**. (ASE L116–L146)
- Se puede tomar **una sola norma** que cubra la política general de acceso y verificar sus reglas. Se recomienda tomar 2 normas para cubrir 2–3 controles de una vez. (ASE L144–L150)
- **Cada control se ancla a gobernanza y a gestión de TI**: reglas, mecanismos, directrices, políticas y "qué control se ejerce sobre el control". (ASE L174–L178)

### 3.4 Trazabilidad a la gestión del riesgo (obligatoria)

- Todo control **nace del ejercicio de gestión del riesgo** (ISO 27001:2022 §6.1, y los controles de §8.2/§8.3). No salen de la tabla del Anexo A. (ASE L91–L97)
- **Si no hay evidencia de gestión del riesgo que sustente el control → NO CONFORME.** (ASE L95)
- Para cada ítem **conforme** se diligencia la matriz con al menos un riesgo y **trazabilidad completa** (riesgo → control → evidencia). (ASE L79)
- Se escribe para la organización, no para el auditor: "el auditor lo tiene en la cabeza y lo planifica… no construye el documento". (ASE L45–L47)

---

## 4. Los tres tipos de hallazgo

### 4.1 Definiciones exactas

| Tipo | Definición de la docente | Prueba de la docente |
|---|---|---|
| **CONFORME (C)** | Cumplimiento cabal; el auditor **verificó la eficacia** de las acciones, no solo la existencia del control. | "El auditor fue y verificó la eficacia de las acciones, es decir, no es que solo esté el control… es que funciona adecuadamente, es decir, ¿cumple con el objetivo?" (P2 L90) |
| **NO CONFORME (NC)** | **Incumplimiento parcial o total** de un requisito. Un solo ítem desviado de cien vuelve el control **no conforme**. | "99 ítems conformes y un solo ítem no conforme… ¿qué le pongo? No conforme." (P2 L70–L82) |
| **OPORTUNIDAD DE MEJORA (OM)** | Cumple **al 100 %**, pero el mecanismo es **ineficiente**: hay riesgo latente de que se materialice una desviación si no se interviene. **Nunca es una desviación.** | "Oportunidad de mejora siempre es que cumples 10 de 10… lo que lo diferencia es que puede optimizarse o automatizarse para reducir el riesgo humano y elevar el nivel de madurez." (P2 L101–L111, PDF p6) |

### 4.2 Reglas de decisión

- Un control produce **un solo tipo de hallazgo final**: se unifican todos los ítems del control y se marca **una sola X**. (P2 L207–L223; columnas P/Q/R de la plantilla)
- **No se confunde una desviación parcial con una OM.** "Hay una pequeña desviación y entonces los estudiantes inmediatamente lo ponen como oportunidad de mejora. No, no es oportunidad de mejora, es no conforme." (P2 L82)
- El dictamen debe corresponderse **exactamente** con el tipo de hallazgo y con la evidencia objetiva. Sin evidencia objetiva que sustente el tipo de hallazgo, **el ítem no se puede valuar**. (P2 L231)
- **Un NC nunca es "cero evidencia"**: debe haber evidencia parcial que demuestre que el control existe pero es insuficiente. "No conforme… porque no está en ceros, no porque no haya nada." (ASE L191–L193)

### 4.3 Ciclo de evidencia exigido por fase (PDF p5)

**Ítem CONFORME — ciclo completo en 3 fases operativas:**
1. **Fase 1 · Configuración operativa**: muestra en vivo la configuración global de accesos (IAM, Directorio Activo u homólogo) que evidencia la política de MFA y de bloqueo por intentos fallidos.
2. **Fase 2 · Prueba de fuego (eficacia técnica)**: un intento de fuerza bruta contra la consola; se debe ver el **bloqueo automático**, la **alerta en el visor de logs centralizado** y la descripción del control funcionando.
3. **Fase 3 · Ejecución de acciones y evidencia del plan de acción**: qué pasó después del log — activación de la alerta, ticket/orden de aislamiento temporal de la IP atacante, verificación de identidad por canal seguro, orden de restablecimiento de credenciales, y **trazabilidad histórica** (reporte mensual de indicadores revisado por gerencia de TI). *Si hay un registro en el log, debe haber una acción documentada que responda a él.*

**Ítem NO CONFORME — 3 pasos (PDF p6):**
1. **Cruce de información**: solicitar registro oficial de contratos/logs de auditoría/tablas de usuarios; mostrar el contraste documental (p. ej. un "Proveedor de Soporte Técnico X" con contrato vigente).
2. **Ejecución técnica**: abrir en vivo las herramientas de auditoría (Active Directory, consola AWS/Azure, tablas de usuarios de VPN); buscar credenciales asignadas a ex-proveedores y ejecutar consultas.
3. **Evidencia contingente e irrefutable**: el estado del caso figura como "Active"/"Enabled"; el auditor toma la captura del log con fecha y hora, exporta el reporte técnico y dicta: *"Se evidencia una No Conformidad Mayor/Menor…"*, dejando la evidencia lista y blindada, **sin tocar un solo botón para solucionarlo**.

**Ítem OPORTUNIDAD DE MEJORA:** control conforme y funcional, con evidencia que demuestra **cumplimiento estricto**; el OM consiste en **proponer o simular la transición a una herramienta centralizada y automatizada** (p. ej. de revisión manual de logs a gestión automatizada). (PDF p6)

### 4.4 PHVA: el error número uno de los equipos

Cada verificación debe ser **extensible al ciclo PHVA** (Planear · Hacer · Verificar · Actuar), no solo "hacer":

| Fase | Qué se debe evidenciar |
|---|---|
| **Planear** | Mecanismos de control planificados y su origen en la gestión del riesgo. |
| **Hacer** | Ejecución de lo planificado. |
| **Verificar** | Monitoreo, alertas, revisiones periódicas. |
| **Actuar** | Preparación y ejecución ante la materialización del riesgo: qué se hizo, quién, con qué evidencia, cadena de custodia válida. (P2 L265–L285) |

> "Muchos solo se quedan en el planear, y muchos solo en el hacer. Muy pocos o cero estudiantes traslapan esto al resto del ciclo." (P2 L275)

---

## 5. Evidencia: qué se exige y qué no se acepta

**Se exige** (PDF p8, p10):
- Cada verificación debe tener: control o requisito evaluado · objetivo de la verificación · procedimiento ejecutado y herramientas utilizadas · resultado · **evidencia objetiva y justificación técnica del hallazgo**.
- Las **herramientas** deben ser informáticas especializadas y aplicadas **mediante pasos concretos y autorizados**.
- La ejecución de una herramienta **no constituye automáticamente** una conformidad o no conformidad: sus resultados se interpretan y contrastan con los criterios aplicables.
- Las evidencias deben estar **referenciadas en la matriz** y disponibles para demostración.

**No se acepta** (PDF p8):
- Descripciones genéricas ("verificar seguridad", "revisar el sistema", "ejecutar herramienta") **sin explicar el procedimiento**.
- Justificaciones técnicas y empresariales que solo digan "porque es importante".
- Ítems **sin procedimiento de verificación**, sin resultados con evidencia objetiva o sin justificación técnica.
- Un ítem con solo captura de pantalla sin report/interpretación: *"Un auditor no se conforma con que le muestren una pantalla que diga 'miren, aquí está el log que muestra que alguien falló la contraseña'. El auditor les preguntará de inmediato: ¿Y qué hizo la empresa al respecto? ¿Cuál fue el plan de acción?"* (PDF p6)

**Sobre los logs** (ASE L244–L246): registrar **usuario, acción, fecha y hora, IP**; los logs **deben estar protegidos** (alguien puede borrar la factura *y* el log); debe existir **segregación** entre administración y control; y debe haber **alertas ante uso anómalo**.

---

## 6. Cronometría y formato de la exposición

| Bloque | Tiempo | Contenido |
|---|---|---|
| **1 · Contexto operativo del entorno** | **máx. 3 min** | Rol de auditor inmediato, sin preámbulo: alcance, sistemas, la muestra seleccionada, una prueba el control asignado y paso a la auditoría operativa. |
| **2 · Ejecución técnica, evidencia y dictamen en vivo** | **45–50 min** | Núcleo de la evaluación. Interacción con herramientas (Nmap, Nessus, OpenVAS, SonarQube, Wireshark, AWS/Azure, Active Directory, logs del sistema). El equipo pasa las herramientas sobre los ítems pactados, presenta resultados, dictamina cada ítem y el hallazgo del panel. |
| **3 · Conclusiones académicas y lecciones aprendidas** | **máx. 7 min** | Se quita el sombrero de auditor. Responde: (1) **brecha real** entre lo que dice el estándar y lo que se encontró/configuró/auditó; (2) **complejidad de la evidencia** para obtener evidencia objetiva trulyIRC e irrefutable; (3) **madurez corporativa**: qué lecciones deja el ejercicio. |

- **Prohibido** el uso de exposiciones teóricas, lecturas extensas de diapositivas o introducciones conceptuales sobre el significado del control. Si se hace, la exposición se detiene de inmediato. (P2 L117, PDF p7)
- **Si se requiere tiempo adicional** por complejidad de los laboratorios, debe **comunicarse formalmente y con anticipación** a la docente para que evalúe la viabilidad. "No va a ser excusa que es que no les dio el tiempo." (PDF p7, P2 L124–L134)
- **Modalidades**: **A** grabación de video + sustentación en vivo de conclusiones (bloque 3 en vivo) · **B** exposición práctica en vivo y directo · **C** **mixta** — exposición técnica en vivo apoyada en evidencias previamente recopiladas (videos, capturas, logs, reportes). *La docente prefiere la C por ser la más utilizada y la más práctica.* (PDF p8, P2 L170–L173)
- **Plan B**: si hay riesgo de corte de internet/fluido, grabar la exposición. Al día siguiente, las conclusiones y las preguntas se hacen en vivo. (P2 L288)

---

## 7. Generalidades: qué debe demostrar el equipo

Por cada aspecto evaluado (PDF p8): (1) control o requisito evaluado (numeral, requisito legal o criterio de auditoría) · (2) objetivo de la verificación · (3) procedimiento ejecutado y herramientas · (4) resultado y clasificación C/NC/OM · (5) **evidencia objetiva y justificación técnica**.

En la sustentación se debe demostrar (PDF p8): contexto y alcance · muestra y su justificación · técnicas de auditoría · ejecución técnica con herramienta especializada · evidencias objetivas · análisis de resultados · **verificación de eficacia** (qué comprobaciones se hicieron para determinar si los controles funcionan conforme a los criterios) · conclusiones y limitaciones · **sustentación individual de todos los integrantes**.

Criterio fundamental por verificación (PDF p10): *¿qué control evalúo? ¿qué requisito debe cumplirse? ¿qué elemento de la muestra y por qué? ¿qué técnica? ¿qué procedimiento? ¿qué herramienta y cómo corresponde? ¿qué evidencia? ¿cómo se demuestra? ¿puedo verificar la funcionamiento o la eficacia del control? ¿cuál es mi conclusión y cómo la sustento?*

**La calificación no depende de la cantidad de herramientas ni del número de capturas, sino de la pertinencia de las verificaciones, la calidad de las evidencias y la capacidad de sustento técnico.** (PDF p10, PDF p13)

---

## 8. Fuentes técnicas y bibliografía

**Regla dura:** remitirse **solo** a ISO 27001 e ISO 27002 es un error. "Jamás. Es muy complejo que, si no tengo base de conocimiento, pretender que con lo que está en estas dos normas voy a poder hacer una auditoría apropiada." La 27001 dice *qué* hacer; **el *cómo* está en OWASP, NIST, CIS, etc.** (P2 L264–L272)

- Cada ítem de la lista de chequeo debe estar **amarrado simultáneamente** al control de ISO 27001:2022 **y** a su **fuente metodológica de campo**. (PDF p12)
- La columna "ENLACES DE INTERÉS Y MATERIAL DE APOYO" debe citar **fuentes oficiales de auditoría**, con metodología global de auditoría y buenas prácticas técnicas verificables (CoBIT, ISO 27002, NIST, OWASP, ISO 22301). (PDF p13)
- Fuentes sugeridas en el PDF por tema (§7): OWASP Top 10 / ASVS / SAMM, NIST SP 800-218 (SSDF), NIST SP 800-40, NIST SP 800-92 (gestión de logs), CIS Benchmarks, ISO/IEC 27017, 27018, CSA CCM. **Son "algunas"**: se pueden consultar otras. (P2 L272)

---

## 9. Catálogo de errores señalados por la docente (catálogo de trampas)

| # | Error | Corrección exigida | Fuente |
|---|---|---|---|
| 1 | Exposición teórica, lectura de diapositivas, introducción conceptual | Arranque directo a la fase operativa; máx. 3 min de contexto | P2 L117, PDF p7 |
| 2 | Ejercicio 100 % no conforme (monótono) | Debe haber los tres tipos de hallazgo; las no conformidades se **pactan** | P2 L34, L61 |
| 3 | Conformidad declarada sin verificar **eficacia** | Verificar que el control **cumple su objetivo** en contexto, no que exista | P2 L90–L97 |
| 4 | No conforme "en ceros" sin evidencia | Debe haber evidencia parcial que muestre insuficiencia | ASE L191 |
| 5 | Desviación parcial clasificada como OM | Una desviación parcial es **NO CONFORME** | P2 L82 |
| 6 | Controles sin origen en la gestión del riesgo | Sin evidencia de gestión del riesgo → **NO CONFORME** | ASE L95 |
| 7 | Verificaciones detenidas en Planear/Hacer | Trasladar a **Verificar** (monitoreo, alertas, revisiones) y **Actuar** | P2 L275 |
| 8 | Descripción de prueba genérica ("revisar el firewall") | Describir **qué** se revisa, **cómo**, **qué es válido y qué no**, paso a paso | P2 L185–L191 |
| 9 | Bibliografía limitada a ISO 27001/27002 | Amarrar cada ítem a control 27001 **+** fuente metodológica de campo | P2 L264 |
| 10 | Auditor que arregla o propone soluciones | Solo dictamina y documenta | PDF p6 |
| 11 | Mostrar captura sin interpretación | Interpretar y contrastar con el criterio; responder "¿qué hizo la organización?" | PDF p6 |
| 12 | Evidencia sin correlación con el riesgo | Interpretar el resultado técnico contra requisito + regla + **riesgo identificado** | PDF p3 |
| 13 | Una X por ítem en vez de por control | Unificar los ítems del control en **un solo hallazgo final** | P2 L223 |

---

## 10. Anexo A — Notas de la asesoría específicas de Control de Acceso Lógico

> Fuente: `docs/ASESORIA.md`. Última sesión previa a la exposición; el equipo debe llegar con base de conocimiento.

**A.1 Insumo obligatorio.** Se necesita un **sistema de información** para auditar. Si es propio y modificable, se puede construir el laboratorio alrededor. → **AppNotify**.

**A.2 Conceptos que hay que dominar** (si no, "la auditoría me va a quedar mal"):
- **Gestión de identidades y su ciclo de vida** (alta, mantenimiento, baja), **perfiles y roles** dentro del sistema.
- **Gobernanza y gestión de TI** ancladas a cada control y a cada temática: "qué control se ejerce sobre el control".
- **Gestión del riesgo** como vestimenta del auditor.

**A.3 A.5.15 → CONFORME, obligatoriamente.** Requiere: (1) la **norma de control de acceso** (documento, descargable de internet, alineado al contexto) como evidencia documental; (2) **validar y probar al menos una de sus reglas** contra el sistema. Si se validan reglas de 2 normas distintas, se cubren 3 controles de una vez. (ASE L130–L150)

**A.4 A.8.18 — Uso de programas utilitarios privilegiados.** Herramientas que pueden anular controles de seguridad, modificar configuraciones o **elevar privilegios**. Verificaciones posibles:
- Lista blanca de aplicaciones permitidas; restricción de instalación de herramientas no autorizadas.
- Bloqueo de scripts inseguros; restricciones de PowerShell; ejecución remota habilitada o no.
- **Cuentas huérfanas** (ex-empleado que lleva meses sin trabajar y conserva permisos de administrador) — se cruza con la lista de ex-empleados de Recursos Humanos. (ASE L254)
- Privilegios mínimos, **revisiones periódicas**, **privilegios temporales con expiración**.
- **Cuentas compartidas** o **exceso de privilegios** en cuentas nominally individuales. Caso real: acceso privilegiado entregado a un ingeniero de confianza y **no retirado**; otro ingeniero lo usó y borró información durante una auditoría. (ASE L238)
- **Control de acceso de terceros**: revisar contratos y hasta dónde llega el acceso; p. ej. dar acceso a un sistema de un tercero mediante AnyDesk. (ASE L261)
- **Segregación** entre usuarios normales y privilegiados (matriz de segregación). (ASE L232)
- Según contexto: restricción de acceso **local o remoto**; validación de VPN segura o insegura. (ASE L236)

**A.5 Monitoreo y trazabilidad.** El mecanismo de monitoreo debe registrar **usuario, acción, fecha y hora, IP**; **los logs deben estar protegidos**; debe existir **segregación** entre desarrollo y administración; y **alertas ante uso anómalo**. No se exige SIEM. (ASE L244–L246)

**A.6 Ejemplo de NC con evidencia trazable (ASE L242):** un usuario sin permiso de eliminación **igual elimina** información; se muestra el perfil del cargo (solo lectura), el log con la eliminación, se pregunta *"muéstreme qué acciones tomó, muéstreme cómo subsanó las brechas"*; si hay plan de acción, se muestran **evidencias de su ejecución**; si el plan se construyó pero **no se ejecutó**, tampoco hay cierre → NC.

**A.7 Identidad y cuentas.** Se debe poder verificar: **revisión de cuentas huérfanas**, **evitación de cuentas compartidas**, **expiración de privilegios temporales**, **eliminación de accesos innecesarios**, **control de acceso de terceros**. (ASE L240, L254, L259, L261)

**A.8 "Actuar" — cadena de custodia.** Si el riesgo se materializa, la organización debe estar preparada: saber qué hacer, y que la evidencia sea **válida ante una instancia judicial** (cadena de custodia). Caso real: el computador de Raúl Reyes no pudo usarse como prueba por fallo en la cadena de custodia. (P2 L271–L285)

---

## 11. Anexo B — Estructura de la lista de chequeo (plantilla `2. Lista Chequeo.xlsx`)

Dos hojas: `LISTA DE CHEQUEO` (matriz) y `Columnas B3:D18` (diccionario). **Una fila = una verificación específica.** Un mismo control puede aparecer en varias filas; al final se **unifica en un solo tipo de hallazgo por control**.

| Col | Campo | Qué se diligencia |
|---|---|---|
| B | PROCESO | ¿Qué proceso de la organización se audita? |
| C | **CONTROL** | Numeral ISO 27001:2022 (A.5.15 … A.8.18). |
| D | Población | ¿Cuántos elementos existen para revisar? |
| E | Muestra | ¿Cuáles elementos se revisan realmente? |
| F | Criterios de selección | ¿Cómo se escogió la muestra? (criticidad, exposición, riesgo) |
| G | Justificación técnica y empresarial | ¿Por qué importa? ¿Qué consecuencia tendría una falla? |
| H | TÉCNICA | ¿Cómo se obtiene información? (entrevista, observación, revisión documental, prueba) |
| I | **DESCRIPCIÓN DE LA TÉCNICA** | **¿Qué revisar y cómo? Procedimientos previstos** — pasos concretos de la verificación. |
| J | Evidencias esperadas | ¿Qué documentos, registros o resultados se espera encontrar? |
| K | Criterios de aceptación | ¿Qué condiciones deben cumplirse para declarar conforme? |
| L / M / N | CONFORME / NO CONFORME / OPORTUNIDAD — **individual** | Marca por ítem. |
| O | ENLACES DE INTERÉS Y MATERIAL DE APOYO | Fuentes (no solo ISO). |
| **P / Q / R** | CONFORME / NO CONFORME / OPORTUNIDAD — **final por control** | **Una sola X por control**, unificando sus ítems. |
| S | **EVIDENCIA OBJETIVA** | ¿Qué se encontró realmente? Hechos comprobables, fechas, resultados, identificadores. |

Agrupaciones de la fila 1 (técnicas): B–C *Observación* · E–G *Revisión documental* · H *Entrevista* · I *Prueba* · J–K *Revisión documental* · O *Otra*.

---

## 12. Anexo C — Nuestro alcance: 9 controles de acceso lógico (`docs/ITEMS.md`)

| Control | Nombre oficial | Ancla conceptual de la verificación |
|---|---|---|
| A.5.15 | Control de acceso | Arquitectura documental + reglas verificadas sobre la aplicación. **Debe ser CONFORME.** |
| A.5.16 | Gestión de la identidad | Ciclo de vida de la identidad: alta, mantenimiento, baja; perfiles y roles. |
| A.5.17 | Información de autenticación | Protección de la información de autenticación (secretos, tokens, credenciales). |
| A.5.18 | Derechos de acceso | Asignación y revisión de derechos de acceso por rol/función. |
| A.8.2 | Derechos de acceso privilegiado | Cuentas privilegiadas, segregación, elevación controlada. |
| A.8.3 | Restricción de acceso a la información | Aislamiento de la información por propietario/clasificación; control de su acceso. |
| A.8.4 | Acceso al código fuente | Gestión del acceso de lectura/escritura al código y a las herramientas de desarrollo. |
| A.8.5 | Autenticación segura | MFA, gestión de sesiones, bloqueo por intentos fallidos, resistencia a fuerza bruta. |
| A.8.18 | Uso de programas utilitarios privilegiados | Restricción de utilidades que anulan controles o elevan privilegios. |

**Fuentes de campo sugeridas por control** (a confirmar en el pacto, no son solo ISO):

| Control | Fuente metodológica de campo |
|---|---|
| A.5.15 | ISO/IEC 27002:2022 §5.15 · NIST SP 800-53 Rev.5 AC-2, AC-3, AC-6 · CIS Controls v8 6.1 |
| A.5.16 | ISO 27002 §5.16 · NIST SP 800-63B (Digital Identity Guidelines) · CIS v8 5.2, 5.3 |
| A.5.17 | ISO 27002 §5.17 · OWASP Authentication Cheat Sheet · NIST SP 800-63B §4 |
| A.5.18 | ISO 27002 §5.18 · NIST SP 800-53 AC-2, AC-3, AC-6 · CIS v8 6.3 |
| A.8.2 | ISO 27002 §8.2 · NIST SP 800-53 AC-6(9) · CIS v8 5.4 |
| A.8.3 | ISO 27002 §8.3 · OWASP ASVS V4 · NIST SP 800-53 AC-3, AC-4 |
| A.8.4 | ISO 27002 §8.4 · NIST SP 800-53 SA-10 · CIS v8 8.2 |
| A.8.5 | ISO 27002 §8.5 · OWASP ASVS V2 · NIST SP 800-63B · MITRE ATT&CK T1110 |
| A.8.18 | ISO 27002 §8.18 · NIST SP 800-53 AC-6 · CIS v8 4.6, 5.2 |

---

## 13. Pendientes que solo decide el equipo

1. **Fecha real de exposición**: 27 (verbal) vs. 29 de octubre (PDF) — define el cronograma de preparación.
2. **Modalidad**: A, B o C (la docente sugiere C).
3. **Los ítems NO CONFORMES y de OM** que se pactarán con la docente (deben ser los que realmente se puedan construir en el laboratorio, con evidencia parcial real).
4. **Alcance exacto del laboratorio** de AppNotify: qué se construye (MFA, bitácora, roles, etc.) y qué se deja deliberadamente débil.
5. **Participantes**: cuántos integrantes y quién sostiene qué, para la sustentación individual (PDF p8).
