import os
import json
import streamlit as st
from dotenv import load_dotenv
import anthropic
from tavily import TavilyClient
from datetime import date

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
PERFIL_PATH = "perfil.json"
FAVORITOS_PATH = "favoritos.json"

st.set_page_config(page_title="StyleAgent", page_icon="🤍", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    background-color: #ffffff !important;
    color: #1b2a4a !important;
    font-family: 'Inter', sans-serif;
    font-weight: 300;
}
.stApp { background-color: #ffffff; }

.main-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 500;
    color: #1b2a4a;
    letter-spacing: 0.02em;
    margin-bottom: 0.1rem;
}
.main-subtitle {
    font-size: 0.72rem;
    font-weight: 400;
    color: #8a9bb5;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.greeting {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    color: #8a9bb5;
    font-style: italic;
    margin-bottom: 1rem;
}

section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e8edf5 !important;
}

.sidebar-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8a9bb5;
    margin-top: 1rem;
    margin-bottom: 0.2rem;
}
.sidebar-value {
    font-size: 0.82rem;
    color: #1b2a4a;
    line-height: 1.6;
}

.stButton > button {
    background-color: #ffffff !important;
    color: #1b2a4a !important;
    border: 1px solid #d0d9e8 !important;
    border-radius: 3px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.45rem 1rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #1b2a4a !important;
    color: #ffffff !important;
    border-color: #1b2a4a !important;
}

.stFormSubmitButton > button {
    background-color: #1b2a4a !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 3px !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 0.6rem !important;
    margin-top: 0.5rem !important;
}

.stChatMessage {
    background-color: #f8f9fc !important;
    border: 1px solid #e8edf5 !important;
    border-radius: 8px !important;
}

[data-testid="stChatMessageContent"] p {
    font-size: 0.875rem !important;
    line-height: 1.8 !important;
    color: #1b2a4a !important;
}

.stTextInput input {
    background-color: #f8f9fc !important;
    border: 1px solid #d0d9e8 !important;
    border-radius: 4px !important;
    color: #1b2a4a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
.stTextInput input:focus {
    border-color: #1b2a4a !important;
    box-shadow: 0 0 0 2px rgba(27,42,74,0.08) !important;
}

.stTextInput label {
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #8a9bb5 !important;
}

.favorito-card {
    background: #f8f9fc;
    border: 1px solid #e8edf5;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.8rem;
    color: #1b2a4a;
    line-height: 1.7;
}
.fav-date {
    font-size: 0.62rem;
    color: #8a9bb5;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}

.stCaption {
    font-size: 0.65rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #8a9bb5 !important;
}
img { border-radius: 6px !important; }
hr { border-color: #e8edf5 !important; }
</style>
""", unsafe_allow_html=True)

def cargar_perfil():
    if os.path.exists(PERFIL_PATH):
        with open(PERFIL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def guardar_perfil(perfil):
    with open(PERFIL_PATH, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=2)

def cargar_favoritos():
    if os.path.exists(FAVORITOS_PATH):
        with open(FAVORITOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_favorito(look, fecha):
    favoritos = cargar_favoritos()
    favoritos.append({"look": look, "fecha": fecha})
    with open(FAVORITOS_PATH, "w", encoding="utf-8") as f:
        json.dump(favoritos, f, ensure_ascii=False, indent=2)

def borrar_favorito(index):
    favoritos = cargar_favoritos()
    favoritos.pop(index)
    with open(FAVORITOS_PATH, "w", encoding="utf-8") as f:
        json.dump(favoritos, f, ensure_ascii=False, indent=2)

perfil = cargar_perfil()

# ONBOARDING
if not perfil:
    st.markdown('<div class="main-title">StyleAgent</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Tu asistente personal de moda con IA</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<p style="font-family: Playfair Display, serif; font-size:1.2rem; font-style:italic; color:#1b2a4a; margin-bottom:0.5rem">Bienvenida — cuéntame un poco sobre ti</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.75rem; color:#8a9bb5; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1.5rem">5 pasos rápidos</p>', unsafe_allow_html=True)

    if "onb" not in st.session_state:
        st.session_state.onb = {}

    onb = st.session_state.onb

    # Paso 1 — Nombre
    nombre = st.text_input("¿Cómo te llamas?", value=onb.get("nombre", ""))
    if nombre:
        onb["nombre"] = nombre

    # Paso 2 — Estilo
    st.markdown('<p style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#8a9bb5; margin-top:1rem; margin-bottom:0.3rem">Tu estilo</p>', unsafe_allow_html=True)
    estilos = ["Clásico", "Minimalista", "Casual chic", "Romántico", "Sporty", "Boho", "Atrevido"]
    estilo_sel = st.pills("estilo", estilos, selection_mode="multi", label_visibility="collapsed")
    if estilo_sel:
        onb["estilo"] = ", ".join(estilo_sel)

    # Paso 3 — Colores
    st.markdown('<p style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#8a9bb5; margin-top:1rem; margin-bottom:0.3rem">Colores que más llevas</p>', unsafe_allow_html=True)
    colores_op = ["Negro", "Blanco", "Azul marino", "Gris", "Beige", "Camel", "Colores tierra", "Colores vivos"]
    colores_sel = st.pills("colores", colores_op, selection_mode="multi", label_visibility="collapsed")
    colores_extra = st.text_input("¿Algún color que nunca te pondrías?", value=onb.get("colores_evitar", ""), placeholder="ej: amarillo, naranja...")
    if colores_sel:
        onb["colores"] = ", ".join(colores_sel)
        if colores_extra:
            onb["colores"] += f". Nunca: {colores_extra}"

    # Paso 4 — Prendas y zapatos a evitar
    st.markdown('<p style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#8a9bb5; margin-top:1rem; margin-bottom:0.3rem">Nunca me pondría...</p>', unsafe_allow_html=True)
    evitar_op = ["Tacón de aguja", "Tacón alto", "Faldas cortas", "Ropa muy ajustada", "Flecos", "Estampados llamativos", "Chanclas", "Deportivas", "Ropa oversized"]
    evitar_sel = st.pills("evitar", evitar_op, selection_mode="multi", label_visibility="collapsed")
    evitar_extra = st.text_input("¿Algo más que quieras añadir?", value=onb.get("evitar_extra", ""), placeholder="ej: sombreros, cinturones...")
    if evitar_sel:
        onb["evitar"] = ", ".join(evitar_sel)
        if evitar_extra:
            onb["evitar"] += f", {evitar_extra}"

    # Paso 5 — Contextos
    st.markdown('<p style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#8a9bb5; margin-top:1rem; margin-bottom:0.3rem">¿Para qué necesitas looks?</p>', unsafe_allow_html=True)
    contextos_op = ["Oficina formal", "Oficina casual", "Máster / Universidad", "Salidas con amigas", "Cenas y eventos", "Fin de semana", "Deporte", "Viajes"]
    contextos_sel = st.pills("contextos", contextos_op, selection_mode="multi", label_visibility="collapsed")
    if contextos_sel:
        onb["contextos"] = ", ".join(contextos_sel)

    # Talla
    st.markdown('<p style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.12em; color:#8a9bb5; margin-top:1rem; margin-bottom:0.3rem">Tu talla</p>', unsafe_allow_html=True)
    tallas = ["XS", "S", "M", "L", "XL"]
    talla_sel = st.pills("talla", tallas, selection_mode="single", label_visibility="collapsed")
    talla_num = st.text_input("O escribe tu talla en número", value=onb.get("talla_num", ""), placeholder="ej: 36, 38, 40...")
    if talla_sel:
        onb["talla"] = talla_sel
    elif talla_num:
        onb["talla"] = talla_num

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    if st.button("Comenzar →", type="primary"):
        if onb.get("nombre") and onb.get("estilo") and onb.get("colores") and onb.get("contextos") and onb.get("talla"):
            perfil = {
                "nombre": onb.get("nombre", ""),
                "estilo": onb.get("estilo", ""),
                "colores": onb.get("colores", ""),
                "evitar": onb.get("evitar", ""),
                "contextos": onb.get("contextos", ""),
                "talla": onb.get("talla", ""),
                "feedback_negativo": [],
                "feedback_positivo": []
            }
            guardar_perfil(perfil)
            st.session_state.onb = {}
            st.rerun()
        else:
            st.warning("Por favor completa al menos: nombre, estilo, colores, contextos y talla.")
else:
    # SIDEBAR
    with st.sidebar:
        st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family: Playfair Display, serif; font-size:1.3rem; color:#1b2a4a; font-weight:500; margin-bottom:1.5rem">StyleAgent</div>', unsafe_allow_html=True)
        st.divider()

        # Mi perfil — expandible
        with st.expander("Mi perfil"):
            st.markdown(f'<div class="sidebar-label">Nombre</div><div class="sidebar-value">{perfil["nombre"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-label">Estilo</div><div class="sidebar-value">{perfil["estilo"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-label">Colores</div><div class="sidebar-value">{perfil["colores"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-label">Evita</div><div class="sidebar-value">{perfil["evitar"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-label">Contextos</div><div class="sidebar-value">{perfil["contextos"]}</div>', unsafe_allow_html=True)
            st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
            if st.button("Actualizar perfil"):
                os.remove(PERFIL_PATH)
                st.rerun()

        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

        # Favoritos — expandible
        with st.expander("Mis favoritos"):
            favoritos = cargar_favoritos()
            if not favoritos:
                st.markdown('<div style="font-size:0.78rem; color:#8a9bb5; line-height:1.6">Todavía no tienes looks guardados. Pulsa 🤍 en cualquier respuesta para guardarla aquí.</div>', unsafe_allow_html=True)
            else:
                for i, fav in enumerate(favoritos):
                    st.markdown(f'<div class="favorito-card"><div class="fav-date">{fav["fecha"]}</div>{fav["look"]}</div>', unsafe_allow_html=True)
                    if st.button("Eliminar", key=f"del_{i}"):
                        borrar_favorito(i)
                        st.rerun()
                        # Digest semanal
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        with st.expander("📧 Digest semanal"):
            st.markdown('<div style="font-size:0.78rem; color:#8a9bb5; line-height:1.6; margin-bottom:1rem">Genera tu semana de looks y recíbela por email.</div>', unsafe_allow_html=True)
            if st.button("Generar y enviar →"):
                import json
                import base64
                from email.mime.text import MIMEText
                from google.auth.transport.requests import Request
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from googleapiclient.discovery import build

                SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

                def autenticar_gmail():
                    creds = None
                    if os.path.exists("token.json"):
                        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
                    if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        else:
                            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                            creds = flow.run_local_server(port=0)
                        with open("token.json", "w") as token:
                            token.write(creds.to_json())
                    return build("gmail", "v1", credentials=creds)

                def generar_look_dia(dia, contexto):
                    evitar_texto = perfil.get("evitar", "")
                    r = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=300,
                        system=f"""Eres StyleAgent, experto en moda.
PERFIL: Estilo: {perfil['estilo']}, Colores: {perfil['colores']}, Evita: {evitar_texto}, Talla: {perfil['talla']}
Genera un look en texto plano sin asteriscos ni símbolos:
Contexto: [ocasión]
Superior: [prenda]
Inferior: [prenda]
Zapato: [prenda]
Accesorio: [prenda]""",
                        messages=[{"role": "user", "content": f"Look para {dia} — {contexto}"}]
                    )
                    return r.content[0].text

                dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                contextos = [
                    "oficina formal", "máster o universidad", "oficina casual",
                    "máster o universidad", "oficina formal",
                    "salida casual fin de semana", "salida o plan especial"
                ]

                with st.spinner("Generando tus 7 looks..."):
                    resultados_tavily = tavily.search(query="tendencias moda primavera verano 2026", max_results=2)
                    tendencias = "\n".join([r["content"][:150] for r in resultados_tavily["results"]])

                    looks = []
                    for dia, ctx in zip(dias, contextos):
                        look = generar_look_dia(dia, ctx)
                        looks.append(look)

                cuerpo = f"Hola {perfil['nombre']}! Aquí tienes tus looks para esta semana 👗\n\n"
                cuerpo += "=" * 50 + "\n\n"
                for dia, look in zip(dias, looks):
                    cuerpo += f"📅 {dia.upper()}\n{look}\n\n"
                    cuerpo += "-" * 40 + "\n\n"
                cuerpo += "¡Que tengas una semana con mucho estilo!\nStyleAgent 🎨"

                try:
                    servicio = autenticar_gmail()
                    tu_email = os.getenv("TU_EMAIL")
                    mensaje = MIMEText(cuerpo)
                    mensaje["to"] = tu_email
                    mensaje["subject"] = "👗 StyleAgent — Tu semana de looks"
                    raw = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
                    servicio.users().messages().send(userId="me", body={"raw": raw}).execute()
                    st.success(f"Email enviado a {tu_email} ✓")
                except Exception as e:
                    st.error(f"Error al enviar: {e}")

    # CHAT PRINCIPAL
    st.markdown('<div class="main-title">StyleAgent</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Tu asistente personal de moda con IA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="greeting">Hola de nuevo, {perfil["nombre"]}</div>', unsafe_allow_html=True)
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for i, msg in enumerate(st.session_state.messages):
        avatar = "👠" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                es_look = all(p in msg["content"].lower() for p in ["superior:", "inferior:", "zapato:"])
                if es_look:
                    if st.button("🤍 Guardar look", key=f"fav_{i}"):
                        guardar_favorito(msg["content"], date.today().strftime("%d %b %Y"))
                        st.success("Look guardado en favoritos ✓")
                        st.rerun()

    if pregunta := st.chat_input("Pregúntame sobre tendencias, looks o estilo..."):
        with st.chat_message("user", avatar="👤"):
            st.write(pregunta)
        st.session_state.messages.append({"role": "user", "content": pregunta})

        frases_negativas = ["no me gusta", "nunca más", "no quiero", "no me pongas", "jamás", "quita"]
        frases_cambio_look = ["prefiero", "mejor con", "en vez de", "cambia", "ponme", "cámbialo", "quiero cambiar"]
        frases_positivas = ["me encanta", "me ha gustado", "me gusta mucho", "perfecto", "genial"]
        es_negativo = any(f in pregunta.lower() for f in frases_negativas)
        es_cambio = any(f in pregunta.lower() for f in frases_cambio_look)
        es_positivo = any(f in pregunta.lower() for f in frases_positivas)

        if es_cambio:
            # Solo modifica el look actual, no guarda como feedback permanente
            with st.spinner("Buscando tendencias..."):
                try:
                    resultados = tavily.search(query=pregunta + " moda tendencias 2026", max_results=3)
                    contexto = "\n".join([r["content"] for r in resultados["results"]])
                    if not contexto.strip():
                        contexto = "No se encontraron tendencias actualizadas. Responde basándote en conocimiento general de moda PV2026."
                except Exception:
                    contexto = "Búsqueda no disponible. Responde basándote en conocimiento general de moda PV2026."
            
            evitar_texto = perfil.get("evitar", "")
            system_prompt = f"""Eres StyleAgent, asistente de moda de {perfil['nombre']}.
PERFIL: Estilo: {perfil['estilo']}, Colores: {perfil['colores']}, Evita: {evitar_texto}, Talla: {perfil['talla']}
REGLA: Solo texto plano. Sin **, sin #. Máximo 5 líneas.
El usuario quiere modificar el look anterior. Genera el look completo corregido con el cambio que pide.
Formato exacto:
Contexto: [ocasión]
Superior: [prenda]
Inferior: [prenda]
Zapato: [prenda]
Accesorio: [prenda]"""

            historial = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            historial[-1]["content"] = f"Información:\n{contexto}\n\nCambio solicitado: {pregunta}"

            try:
                respuesta_api = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=500,
                    system=system_prompt,
                    messages=historial
                )
                respuesta = respuesta_api.content[0].text
            except Exception as e:
                respuesta = "Ha habido un problema al conectar con el agente. Inténtalo de nuevo en unos segundos."
                st.error(f"Error: {e}")

            with st.chat_message("assistant", avatar="👠"):
                st.write(respuesta)
                es_look = all(p in respuesta.lower() for p in ["superior:", "inferior:", "zapato:"])
                if es_look:
                    if st.button("🤍 Guardar look", key="fav_cambio"):
                        guardar_favorito(respuesta, date.today().strftime("%d %b %Y"))
                        st.success("Look guardado en favoritos ✓")
                        st.rerun()
                    st.divider()
                    lineas_look = [l for l in respuesta.split("\n") if any(p in l.lower() for p in ["superior:", "inferior:", "zapato:"])]
                    prendas = " ".join([l.split(":")[-1].strip() for l in lineas_look[:2]])
                    query_pinterest = (prendas + " outfit minimal 2026").replace(" ", "+").replace(",", "")
                    url_pinterest = f"https://pinterest.com/search/pins/?q={query_pinterest}"
                    st.markdown(f'<a href="{url_pinterest}" target="_blank" style="display:inline-block; padding:0.4rem 1rem; border:1px solid #d0d9e8; border-radius:4px; font-size:0.72rem; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; color:#1b2a4a; text-decoration:none;">🔍 Ver inspiración en Pinterest</a>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            
            # Detectar si el usuario pide ver Pinterest
        pide_pinterest = any(f in pregunta.lower() for f in ["pinterest", "verlo en pinterest", "ver en pinterest", "inspiración", "inspiracion"])
        
        if pide_pinterest:
            # Buscar el último look en el historial
            ultimo_look = None
            for msg in reversed(st.session_state.messages):
                if msg["role"] == "assistant" and all(p in msg["content"].lower() for p in ["superior:", "inferior:", "zapato:"]):
                    ultimo_look = msg["content"]
                    break
            
            if ultimo_look:
                lineas_look = [l for l in ultimo_look.split("\n") if any(p in l.lower() for p in ["superior:", "inferior:", "zapato:"])]
                prendas = " ".join([l.split(":")[-1].strip() for l in lineas_look[:2]])
                query_pinterest = (prendas + " outfit minimal 2026").replace(" ", "+").replace(",", "")
                url_pinterest = f"https://pinterest.com/search/pins/?q={query_pinterest}"
                respuesta = "Aquí tienes la búsqueda en Pinterest con las prendas de tu look 👇"
                with st.chat_message("assistant", avatar="👠"):
                    st.write(respuesta)
                    st.markdown(f'<a href="{url_pinterest}" target="_blank" style="display:inline-block; padding:0.4rem 1rem; border:1px solid #d0d9e8; border-radius:4px; font-size:0.72rem; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; color:#1b2a4a; text-decoration:none;">🔍 Ver inspiración en Pinterest</a>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
            else:
                with st.chat_message("assistant", avatar="👠"):
                    st.write("Primero pídeme un look y luego te muestro la inspiración en Pinterest.")
                st.session_state.messages.append({"role": "assistant", "content": "Primero pídeme un look y luego te muestro la inspiración en Pinterest."})
            st.stop()
            

        elif es_negativo:
            perfil["feedback_negativo"].append(pregunta)
            guardar_perfil(perfil)
            respuesta = "Entendido, no te lo sugeriré más."
            with st.chat_message("assistant", avatar="👠"):
                st.write(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

        elif es_positivo:
            perfil["feedback_positivo"].append(pregunta)
            guardar_perfil(perfil)
            respuesta = "Perfecto, lo tendré en cuenta para futuros looks."
            with st.chat_message("assistant", avatar="👠"):
                st.write(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

        else:
            with st.spinner("Buscando tendencias..."):
                resultados = tavily.search(query=pregunta + " moda tendencias 2026", max_results=3)
                contexto = "\n".join([r["content"] for r in resultados["results"]])
               
            evitar_texto = perfil.get("evitar", "")
            if perfil.get("feedback_negativo"):
                evitar_texto += ". NO sugerir: " + "; ".join(perfil["feedback_negativo"])

            system_prompt = f"""Eres StyleAgent, asistente de moda personal de {perfil['nombre']}.

PERFIL:
- Estilo: {perfil['estilo']}
- Colores: {perfil['colores']}
- Nunca sugerir: {evitar_texto}
- Contextos: {perfil['contextos']}
- Talla: {perfil['talla']}

FECHA: Abril 2026. Temporada: Primavera-Verano 2026.

REGLA ABSOLUTA: Solo texto plano. PROHIBIDO usar **, *, #, _ o cualquier símbolo Markdown.
Solo moda y estilo. Máximo 2 líneas. Lenguaje natural y cercano.
Sin frases motivacionales. Termina siempre en el accesorio.
LÍMITES:
- Si el usuario usa slang o abreviaciones de planes (vinitos, cañas, tapas, gym, curro, clase...) entiéndelos como contextos de moda y genera el look adecuado sin preguntar qué significan.

CUANDO TE PIDAN UN LOOK:
- Si mencionaron la ocasión pero no el tipo de día, pregunta UNA VEZ: ¿día normal o tienes algo especial?
- Si ya tienen contexto completo, genera el look DIRECTAMENTE
- Formato exacto:
Contexto: [ocasión]
Superior: [prenda]
Inferior: [prenda]
Zapato: [prenda]
Accesorio: [prenda]"""

            historial = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            historial[-1]["content"] = f"Información de internet:\n{contexto}\n\nPregunta: {pregunta}"

            respuesta_api = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                system=system_prompt,
                messages=historial
            )
            respuesta = respuesta_api.content[0].text
            
            es_pregunta = respuesta.strip().endswith("?")
            urls_imagenes = []
            try:
                if not es_pregunta and any(palabra in respuesta.lower() for palabra in ["superior:", "inferior:", "zapato:", "accesorio:"]):
                    contexto_look = perfil.get("estilo", "") + " " + perfil.get("colores", "")
                    imagenes = tavily.search(
                        query=f"outfit {contexto_look} moda oficina 2026 minimal",
                        max_results=3,
                        include_images=True
                    )
                    urls_imagenes = imagenes.get("images", [])[:2]
            except Exception:
                urls_imagenes = []
            with st.chat_message("assistant", avatar="👠"):
                st.write(respuesta)
                es_look = all(p in respuesta.lower() for p in ["superior:", "inferior:", "zapato:"])
                if es_look:
                    if st.button("🤍 Guardar look", key="fav_new"):
                        guardar_favorito(respuesta, date.today().strftime("%d %b %Y"))
                        st.success("Look guardado en favoritos ✓")
                        st.rerun()
                if es_look:
                    st.divider()
                    # Construir query de Pinterest basada en el look
                    # Extraer prendas del look para una búsqueda más precisa
                    lineas_look = [l for l in respuesta.split("\n") if any(p in l.lower() for p in ["superior:", "inferior:", "zapato:"])]
                    prendas = " ".join([l.split(":")[-1].strip() for l in lineas_look[:2]])
                    query_pinterest = (prendas + " outfit minimal 2026").replace(" ", "+").replace(",", "")
                    url_pinterest = f"https://pinterest.com/search/pins/?q={query_pinterest}"
                    st.markdown(f'<a href="{url_pinterest}" target="_blank" style="display:inline-block; padding:0.4rem 1rem; border:1px solid #d0d9e8; border-radius:4px; font-size:0.72rem; font-weight:500; letter-spacing:0.1em; text-transform:uppercase; color:#1b2a4a; text-decoration:none;">🔍 Ver inspiración en Pinterest</a>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": respuesta})