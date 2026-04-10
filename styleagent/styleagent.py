import sys
import os
import json
from dotenv import load_dotenv
import anthropic
from tavily import TavilyClient

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

PERFIL_PATH = "perfil.json"

# Ocasiones que requieren una pregunta de contexto antes de generar el look
CLARIFICACIONES = {
    "máster":      "¿Es un día normal de clase, tienes presentación, defensa o algo especial?",
    "master":      "¿Es un día normal de clase, tienes presentación, defensa o algo especial?",
    "oficina":     "¿Es un día normal de oficina, tienes reunión importante, presentación o evento?",
    "trabajo":     "¿Es un día normal de trabajo, tienes reunión, presentación o algo especial?",
    "universidad": "¿Es un día normal de clase, tienes presentación o evento especial?",
    "uni":         "¿Es un día normal de clase, tienes presentación o algo especial?",
    "salida":      "¿Es una salida casual con amigos, primera cita o cena especial?",
    "evento":      "¿Qué tipo de evento es? (formal, semiformal, fiesta, celebración...)",
    "boda":        "¿Eres invitada, dama de honor o es una boda informal?",
    "entrevista":  "¿Es para un puesto creativo, corporativo o startup?",
}

# Si el usuario ya incluye alguno de estos en su mensaje, no hace falta preguntar
CONTEXTO_YA_DADO = [
    "reunión", "reunion", "presentación", "presentacion", "defensa", "normal", "casual",
    "especial", "importante", "entrevista", "primera cita", "cita", "fiesta", "cena",
    "almuerzo", "formal", "informal", "semiformal", "clase", "examen", "corporativo",
    "creativo", "startup", "invitada", "dama de honor",
]

# Keywords que justifican llamar a Tavily (no buscar para preguntas de feedback o charla)
KEYWORDS_BUSQUEDA = [
    "tendencia", "tendencias", "color", "colores", "moda", "look", "outfit",
    "temporada", "qué se lleva", "que se lleva", "llevar", "combinar",
    "vestir", "prenda", "prendas", "estilo", "colección", "marca", "comprar",
    "qué me pongo", "que me pongo", "qué ponerme", "que ponerme",
]


def guardar_perfil(perfil):
    with open(PERFIL_PATH, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=2)


def crear_perfil():
    print("\n👗 Hola! Soy StyleAgent. Antes de empezar quiero conocerte un poco.\n")
    perfil = {}
    perfil["nombre"]    = input("¿Cómo te llamas? ")
    perfil["estilo"]    = input("¿Cómo describirías tu estilo? (ej: minimalista, clásico, colorido, casual): ")
    perfil["colores"]   = input("¿Qué colores te gustan o llevas más? (ej: neutros, azul, negro): ")
    perfil["evitar"]    = input("¿Hay colores o prendas que no te pongas nunca? ")
    perfil["contextos"] = input("¿Para qué situaciones necesitas looks principalmente? (ej: oficina, máster, salidas): ")
    perfil["talla"]     = input("¿Qué talla usas normalmente? (ej: S, M, 38): ")
    perfil["feedback_negativo"] = []
    perfil["feedback_positivo"] = []
    guardar_perfil(perfil)
    print(f"\n¡Perfecto, {perfil['nombre']}! Ya te conozco. Ahora puedo ayudarte mucho mejor.\n")
    return perfil


def cargar_perfil():
    with open(PERFIL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def construir_system_prompt(perfil):
    neg = ', '.join(perfil.get('feedback_negativo', [])) or 'nada anotado aún'
    pos = ', '.join(perfil.get('feedback_positivo', [])) or 'nada anotado aún'
    return f"""Eres StyleAgent, asistente experto en moda y estilo personal femenino.

PERFIL DE USUARIA:
- Nombre: {perfil['nombre']}
- Estilo personal: {perfil['estilo']}
- Colores favoritos: {perfil['colores']}
- Evita siempre: {perfil['evitar']}
- Contextos habituales: {perfil['contextos']}
- Talla: {perfil['talla']}
- No le ha gustado: {neg}
- Le ha gustado: {pos}

TEMPORADA ACTUAL: Abril 2026 — Primavera/Verano 2026.

REGLAS DE COMPORTAMIENTO:
- Solo respondes sobre moda, estilo, looks y tendencias. Si preguntan otra cosa di: "Soy StyleAgent, solo puedo ayudarte con moda y estilo."
- Responde siempre en español de España, tono cercano y directo
- Máximo 4 líneas por respuesta. Sin excepciones.
- Sin markdown, sin asteriscos, sin almohadillas. Texto plano limpio.
- Sin frases motivacionales ni cierres genéricos del tipo "¡espero que te ayude!" o "¡a por ello!"
- Adapta siempre la respuesta al perfil de la usuaria: su estilo, sus colores, lo que evita
- Nunca repitas una pregunta de aclaración que ya hayas hecho en la misma conversación
- Si ya tienes el contexto necesario, genera el look directamente sin volver a preguntar

FORMATO OBLIGATORIO PARA LOOKS — úsalo siempre que generes un look:
Contexto: [ocasión y subtipo exacto, ej: "Máster — presentación"]
Superior: [prenda concreta]
Inferior: [prenda concreta]
Zapato: [calzado concreto]
Accesorio opcional: [accesorio]

TENDENCIAS Y COLORES:
- Cita 1 color principal + máximo 2 alternativos
- Menciona siempre la temporada y la fuente (Vogue, Pantone, desfiles)
- Sugiere una prenda concreta adaptada al estilo de la usuaria

USO DE LA INFORMACIÓN DE INTERNET:
- Cuando el mensaje incluya "Información actualizada de internet", úsala para fundamentar tu respuesta con datos reales
- Prioriza esa información sobre tu conocimiento general
- Si la información no es útil o fiable di: "No tengo datos actualizados sobre esto, pero según las tendencias generales..."
- Nunca inventes fuentes ni datos

MEMORIA DE SESIÓN:
- Recuerda todo lo hablado en esta conversación
- No repitas información ni preguntas ya hechas
- Si la usuaria ya dio un dato de contexto, úsalo directamente"""


def procesar_feedback(texto, perfil):
    texto_lower = texto.lower()
    negativos = ["no me gusta", "no quiero", "odio", "nunca más", "no me pongo", "quita", "sin"]
    positivos = ["me encanta", "me gusta", "perfecto", "genial", "me lo quedo", "repite"]
    for p in negativos:
        if p in texto_lower:
            perfil["feedback_negativo"].append(texto)
            guardar_perfil(perfil)
            return True, "negativo"
    for p in positivos:
        if p in texto_lower:
            perfil["feedback_positivo"].append(texto)
            guardar_perfil(perfil)
            return True, "positivo"
    return False, None


def detectar_si_necesita_clarificacion(texto):
    """Devuelve (ocasion, pregunta) si hay que pedir más contexto antes de generar el look."""
    texto_lower = texto.lower()

    # Solo actúa si es una petición de look
    es_peticion_look = any(kw in texto_lower for kw in [
        "look", "outfit", "qué me pongo", "que me pongo",
        "qué ponerme", "que ponerme", "combinar", "vestir", "qué llevo", "que llevo"
    ])
    if not es_peticion_look:
        return None, None

    # Si ya hay contexto suficiente, no preguntar
    if any(c in texto_lower for c in CONTEXTO_YA_DADO):
        return None, None

    # Buscar una ocasión que necesite clarificación
    for ocasion, pregunta in CLARIFICACIONES.items():
        if ocasion in texto_lower:
            return ocasion, pregunta

    return None, None


def necesita_busqueda(texto):
    """Decide si merece la pena llamar a Tavily para esta pregunta."""
    texto_lower = texto.lower()
    return any(kw in texto_lower for kw in KEYWORDS_BUSQUEDA)


# ── INICIO ──────────────────────────────────────────────────────────────────

if os.path.exists(PERFIL_PATH):
    perfil = cargar_perfil()
    if "feedback_negativo" not in perfil:
        perfil["feedback_negativo"] = []
    if "feedback_positivo" not in perfil:
        perfil["feedback_positivo"] = []
    guardar_perfil(perfil)
    print(f"\n👗 Hola de nuevo, {perfil['nombre']}! Soy StyleAgent.")
    print("Pregúntame lo que quieras sobre tendencias, looks o estilo.")
    print("Escribe 'salir' para terminar o 'actualizar perfil' para cambiar tus preferencias.\n")
else:
    perfil = crear_perfil()
    print("Pregúntame lo que quieras sobre tendencias, looks o estilo.")
    print("Escribe 'salir' para terminar.\n")

system_prompt = construir_system_prompt(perfil)
conversacion = []
peticion_pendiente = None  # Guarda la petición original mientras esperamos la aclaración

# ── BUCLE PRINCIPAL ──────────────────────────────────────────────────────────

while True:
    try:
        pregunta = input("Tú: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n¡Hasta pronto, {perfil['nombre']}! 👋")
        break

    if not pregunta:
        continue

    if pregunta.lower() == "salir":
        print(f"\n¡Hasta pronto, {perfil['nombre']}! 👋")
        break

    if pregunta.lower() == "actualizar perfil":
        os.remove(PERFIL_PATH)
        perfil = crear_perfil()
        system_prompt = construir_system_prompt(perfil)
        peticion_pendiente = None
        conversacion = []
        continue

    # Detectar feedback
    es_feedback, tipo = procesar_feedback(pregunta, perfil)
    if es_feedback:
        system_prompt = construir_system_prompt(perfil)  # Actualiza el prompt con el nuevo feedback
        if tipo == "negativo":
            print(f"\nStyleAgent: Anotado, {perfil['nombre']}. No te sugeriré eso más. ¿Algo más que cambiar?\n")
        else:
            print(f"\nStyleAgent: Me alegra que te haya gustado. Lo tendré en cuenta para futuros looks.\n")
        continue

    # Si había una petición pendiente de clarificación, combinarla con la respuesta actual
    if peticion_pendiente:
        pregunta_final = f"{peticion_pendiente} — detalle adicional: {pregunta}"
        peticion_pendiente = None
    else:
        pregunta_final = pregunta

        # ¿Necesita una pregunta de contexto antes de buscar?
        _, pregunta_clarif = detectar_si_necesita_clarificacion(pregunta)
        if pregunta_clarif:
            peticion_pendiente = pregunta
            conversacion.append({"role": "user", "content": pregunta})
            conversacion.append({"role": "assistant", "content": pregunta_clarif})
            print(f"\nStyleAgent: {pregunta_clarif}\n")
            continue

    # Buscar en Tavily solo si la pregunta lo justifica
    if necesita_busqueda(pregunta_final):
        print("\n🔍 Buscando tendencias actuales...\n")
        try:
            resultados = tavily.search(
                query=pregunta_final + " moda tendencias primavera verano 2026",
                max_results=3
            )
            contexto_web = "\n".join([r["content"] for r in resultados["results"]])
            mensaje_usuario = f"Información actualizada de internet:\n{contexto_web}\n\nPregunta: {pregunta_final}"
        except Exception:
            mensaje_usuario = f"Pregunta: {pregunta_final}"
    else:
        mensaje_usuario = f"Pregunta: {pregunta_final}"

    conversacion.append({"role": "user", "content": mensaje_usuario})

    try:
        respuesta = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=system_prompt,
            messages=conversacion
        )
        texto_respuesta = respuesta.content[0].text
    except Exception as e:
        texto_respuesta = "Ha habido un error al conectar con el servidor. Inténtalo de nuevo."
        print(f"\nStyleAgent: {texto_respuesta}\n")
        continue

    conversacion.append({"role": "assistant", "content": texto_respuesta})
    print(f"\nStyleAgent: {texto_respuesta}\n")