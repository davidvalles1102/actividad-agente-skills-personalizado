# Sistema Agéntico con Skills Propias

Refactorización y personalización de un agente conversacional simple en
Python, separando **lógica**, **configuración** y **comportamiento**, e
incorporando **skills propias** reutilizables entre varios agentes
personalizados.

Actividad individual: *Refactorización y Personalización de un Sistema
Agéntico mediante Skills Propias*.

---

## 1. Resumen del proyecto

El punto de partida es `legacy/agente_monolitico.py`: un chatbot de
terminal con capacidades de calculadora, gestión de tareas, resumen de
texto y búsqueda de archivos, todo escrito en una sola función. A partir
de ahí se refactorizó el proyecto en:

- Un **núcleo** (`core/`) que orquesta la conversación y es agnóstico a
  qué skills existen o qué personalidad tiene el agente.
- Un **catálogo de skills propias** (`skills/`), cada una documentada con
  un `SKILL.md` y aislada en su propio módulo.
- **Agentes personalizados** (`agents/*.json`) que combinan un subconjunto
  de skills con una personalidad distinta, reutilizando el mismo motor.

## 2. Objetivo de la actividad

Evaluar la capacidad de tomar un proyecto con lógica monolítica, separar
sus responsabilidades, diseñar skills propias bien documentadas e
integrarlas en agentes personalizados, usando la IA como asistente
técnico y no como sustituto del criterio propio.

## 3. Proyecto base (antes de refactorizar)

`legacy/agente_monolitico.py` se conserva intacto como evidencia del
"antes". Resumen de sus problemas (detallados también en el docstring del
archivo):

| Problema | Evidencia en el código |
|---|---|
| Lógica monolítica | Una sola función `responder_mensaje` con un `if/elif` por cada capacidad |
| Configuración mezclada con lógica | `NOMBRE_AGENTE` hardcodeado junto al código de negocio |
| Sin reutilización | No hay forma de crear un segundo agente con otra personalidad o con menos capacidades |
| Estado volátil | `tareas_en_memoria` es una lista global que se pierde al cerrar el programa |
| Riesgo de seguridad | `eval(expresion)` sobre texto libre del usuario |
| Duplicación | Construcción manual de strings con `+` repetida en cada rama |
| Sin pruebas | No existe ningún test automatizado |

## 4. Arquitectura refactorizada

### 4.1 Separación de responsabilidades

La actividad pide separar **lógica**, **configuración** y
**comportamiento** del agente. Así se mapea en este proyecto:

| Responsabilidad | Dónde vive | Qué NO sabe |
|---|---|---|
| **Lógica** (orquestación) | `core/agent.py`, `core/skill_registry.py` | No conoce los textos de personalidad ni la implementación concreta de ninguna skill |
| **Configuración** | `agents/*.json` | No contiene código; solo describe quién es el agente y qué tiene permitido usar |
| **Comportamiento** (capacidades) | `skills/<nombre>/skill.py` + `SKILL.md` | No sabe qué agente la está usando ni si hay otras skills activas |

Esta separación es la razón por la que `agents/rex_tecnico.json` puede
desactivar `gestor_tareas` sin tocar ni una línea de `skills/gestor_tareas/`
ni de `core/`: ver la demostración en la sección 8.3.

### 4.2 Estructura de carpetas

```
agente-skills-personalizado/
├── legacy/
│   └── agente_monolitico.py      # proyecto base (antes de refactorizar)
├── core/                          # lógica / orquestación del agente
│   ├── agent.py                   # Agent: decide skill vs. LLM, guarda historial
│   ├── config.py                  # AgentConfig: carga agents/*.json
│   ├── skill_registry.py          # descubre skills/ dinámicamente (importlib)
│   ├── llm_provider.py            # Mock / Anthropic / OpenAI intercambiables
│   └── frontmatter.py             # parser minimalista para SKILL.md
├── skills/                        # comportamiento: una capacidad por carpeta
│   ├── calculadora/{SKILL.md, skill.py}
│   ├── gestor_tareas/{SKILL.md, skill.py}
│   ├── resumen_texto/{SKILL.md, skill.py}
│   └── buscador_archivos/{SKILL.md, skill.py}
├── agents/                        # configuración: personalidad + skills habilitadas
│   ├── ada_productividad.json
│   └── rex_tecnico.json
├── data/
│   └── ejemplo_texto.txt          # archivo de entrada usado por resumen_texto
├── tests/                         # pruebas unitarias (unittest, stdlib)
├── main.py                        # CLI: conecta config + registry + agent
├── requirements.txt
├── .env.example
└── README.md
```

## 5. Skills propias implementadas

Cada skill sigue el mismo estándar: una carpeta con `SKILL.md`
(metadata + documentación legible por humanos) y `skill.py`
(una función `run(message, context) -> str`). `core/skill_registry.py`
las descubre automáticamente leyendo esas carpetas; **agregar una skill
nueva nunca requiere editar `core/`**.

| Skill | Qué hace | Triggers | Estado propio | Usa LLM |
|---|---|---|---|---|
| `calculadora` | Evalúa expresiones aritméticas de forma segura (`ast`, no `eval`) | calcula, cuánto es, suma... | No | No |
| `gestor_tareas` | Agrega, lista y completa tareas | tarea, tareas | Sí (`data/tareas.json`) | No |
| `resumen_texto` | Resume un texto o archivo | resume, resumen | No | Sí, si hay un proveedor real configurado; si no, resumen extractivo local |
| `buscador_archivos` | Busca archivos por nombre dentro de `data/` | busca archivo... | No | No |

Detalle completo de cada una (entradas, salidas, ejemplos y notas de
diseño) en su propio `SKILL.md`.

## 6. Agentes personalizados

Dos agentes comparten exactamente el mismo motor (`core/`) y el mismo
catálogo de skills, pero tienen personalidad y capacidades distintas
definidas solo por su archivo JSON:

| | Ada (`ada_productividad.json`) | Rex (`rex_tecnico.json`) |
|---|---|---|
| Rol | Asistente de Productividad | Asistente Técnico de Soporte |
| Tono | Cercano y motivador | Directo y sin rodeos |
| Skills habilitadas | `gestor_tareas`, `resumen_texto`, `calculadora`, `buscador_archivos` | `calculadora`, `buscador_archivos` |
| Proveedor LLM | `mock` (configurable a `anthropic`/`openai`) | `mock` |

Que Rex no tenga `gestor_tareas` habilitada no es una validación manual
en el código: `Agent.__init__` filtra `skills` contra
`config.enabled_skills`, así que para Rex esa skill simplemente no existe
en memoria. Si le escribes "agrega tarea...", cae al LLM en vez de
ejecutar la skill (ver demostración en 8.3).

## 7. Flujo LLM y proveedor configurable

`core/llm_provider.py` define `LLMProvider` como clase abstracta con tres
implementaciones intercambiables: `MockProvider` (determinista, sin red,
usada por defecto para que el proyecto se pueda ejecutar y calificar sin
API keys), `AnthropicProvider` y `OpenAIProvider` (llaman a la API real si
hay `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` configuradas). `get_provider()`
degrada automáticamente a `MockProvider` si el proveedor pedido falla al
inicializarse, avisando por consola pero sin interrumpir la ejecución.

La skill `resumen_texto` es la única que usa `context.provider`
directamente: si hay un proveedor real, le pide el resumen al modelo; si
no, usa un resumen extractivo local. Así se muestra tanto el flujo con
LLM real como un modo de ejecución 100% local y determinista para
pruebas.

## 8. Cómo ejecutar el proyecto

### 8.1 Requisitos

- Python 3.10 o superior (probado con Python 3.14).
- Sin dependencias externas obligatorias (ver `requirements.txt`).

### 8.2 Ejecutar un agente

```bash
python main.py --agent ada_productividad
python main.py --agent rex_tecnico
```

Comandos dentro del chat: `skills` (lista las capacidades del agente
actual) y `salir` (termina el programa).

### 8.3 Ejemplo de sesión real (capturada al validar el proyecto)

```
== Ada (Asistente de Productividad) ==
Tu: calcula 12 * (4 + 1)
Ada [skill:calculadora]: El resultado de 12 * (4 + 1) es 60.

Tu: agrega tarea revisar el informe final
Ada [skill:gestor_tareas]: Tarea agregada: 'revisar el informe final' (#1)

Tu: resume archivo ejemplo_texto.txt
Ada [skill:resumen_texto]: Resumen (extractivo):
Los sistemas agenticos combinan modelos de lenguaje con herramientas externas...

== Rex (Asistente Tecnico de Soporte) ==
Tu: agrega tarea esto no deberia funcionar
Rex [llm:mock]: (Eres Rex...) Entiendo tu mensaje: "agrega tarea esto no deberia funcionar".
Por ahora no tengo una skill especifica para esto...
```

Esto confirma, con ejecución real y no solo en teoría, que la
personalización por configuración cambia el comportamiento observable del
agente sin tocar código.

### 8.4 Usar un proveedor LLM real (opcional)

```bash
cp .env.example .env
# editar .env: LLM_PROVIDER=anthropic y ANTHROPIC_API_KEY=...
pip install anthropic
python main.py --agent ada_productividad
```

### 8.5 Ejecutar las pruebas

```bash
python -m unittest discover -s tests -v
```

15 pruebas cubren: el parser de frontmatter, el descubrimiento dinámico
de skills, cada skill por separado (casos normales y de error) y el
enrutamiento skill-vs-LLM del `Agent`, incluyendo que una skill
deshabilitada para un agente no se ejecute.

## 9. Uso de IA como herramienta de apoyo al desarrollo

Se usó Claude (Claude Code) como asistente técnico durante el desarrollo,
con supervisión y decisiones humanas explícitas en vez de aceptar
sugerencias sin revisar:

- **Decisión humana — alcance del "antes".** Se pidió conservar el
  agente monolítico original en `legacy/`, en vez de borrarlo, para que
  la refactorización se pueda comparar línea a línea en vez de describirse
  solo en prosa.
- **Decisión humana — sin dependencias externas obligatorias.** Se optó
  por JSON (`json`, estándar) en vez de YAML (`PyYAML`, de terceros) para
  la configuración de agentes, y por un parser de frontmatter propio en
  `core/frontmatter.py` en vez de instalar una librería, priorizando que
  el proyecto se instale y corra sin `pip install` para quien lo revise.
- **Decisión humana — seguridad.** Se revisó explícitamente que
  `skills/calculadora/skill.py` no usara `eval()` (el proyecto original sí
  lo hacía) y se reemplazó por un evaluador basado en `ast` con una lista
  cerrada de operadores permitidos.
- **Validación — pruebas y ejecución real.** Cada skill y el enrutamiento
  del agente se validaron con pruebas automatizadas (`tests/`) y además
  con una sesión real de consola para ambos agentes (sección 8.3), no solo
  leyendo el código generado.
- **Ajuste explícito sobre una sugerencia.** La primera versión de
  `resumen_texto` solo contemplaba resumen extractivo; se decidió
  ampliarla para que pueda apoyarse en `context.provider` cuando hay un
  LLM real configurado, de modo que al menos una skill demuestre el flujo
  LLM pedido por la actividad y no solo lógica determinista.

## 10. Decisiones de diseño y trade-offs

- **Descubrimiento por carpeta (`importlib`) en vez de un registro
  central manual**: agregar una skill nueva es crear una carpeta con
  `SKILL.md` + `skill.py`; no hay una lista en `core/` que mantener
  sincronizada a mano.
- **`SKILL.md` como contrato, no como decoración**: `skill_registry.py`
  obtiene `name`, `description` y `triggers` del propio `SKILL.md`, así
  que la documentación y el comportamiento no pueden desincronizarse
  silenciosamente.
- **Historial corto en memoria (`Agent.history`, máx. 10 turnos)**: es
  suficiente para dar contexto a un proveedor LLM real sin necesitar
  persistencia entre ejecuciones, que no es un requisito de la actividad.

## 11. Posibles mejoras futuras

- Selección de skill por intención (NLU) en vez de coincidencia de
  substrings, para lenguaje más libre.
- Persistir el historial de conversación por agente en disco.
- Añadir una skill con llamada a una API externa real (clima, noticias)
  para ejercitar manejo de errores de red dentro del mismo patrón de
  skill.

## 12. Archivos de entrada

- `agents/ada_productividad.json`, `agents/rex_tecnico.json`: configuración
  de personalidad y skills habilitadas por agente.
- `skills/*/SKILL.md`: definición y documentación de cada skill.
- `data/ejemplo_texto.txt`: texto de entrada usado por la skill
  `resumen_texto`.
- `.env.example`: plantilla de variables de entorno para usar un proveedor
  LLM real.
