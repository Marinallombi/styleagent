import os
import sys
import json
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from dotenv import load_dotenv
import anthropic
from tavily import TavilyClient
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]

PERFIL_PATH = "perfil.json"
DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def cargar_perfil():
    try:
        with open(PERFIL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  No se encontró perfil.json. Ejecuta primero styleagent.py para crear tu perfil.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("⚠️  El archivo perfil.json está corrupto. Ejecuta styleagent.py para rehacerlo.")
        sys.exit(1)


def autenticar_google():
    creds = None
    try:
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    print("⚠️  No se encontró credentials.json. Descárgalo desde Google Cloud Console.")
                    sys.exit(1)
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds
    except Exception as e:
        print(f"⚠️  Error autenticando con Google: {e}")
        sys.exit(1)


def leer_calendario_semana(creds):
    servicio_cal = build("calendar", "v3", credentials=creds)

    hoy = datetime.now()
    dias_hasta_lunes = (7 - hoy.weekday()) % 7 or 7
    lunes = (hoy + timedelta(days=dias_hasta_lunes)).replace(hour=0, minute=0, second=0, microsecond=0)
    domingo = lunes + timedelta(days=7)

    eventos_por_dia = {dia: [] for dia in DIAS_ES}

    try:
        resultado = servicio_cal.events().list(
            calendarId="primary",
            timeMin=lunes.isoformat() + "Z",
            timeMax=domingo.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        for evento in resultado.get("items", []):
            inicio = evento["start"].get("dateTime", evento["start"].get("date"))
            fecha_evento = datetime.fromisoformat(inicio.replace("Z", "")).date()
            idx_dia = fecha_evento.weekday()
            if 0 <= idx_dia <= 6:
                titulo = evento.get("summary", "Evento sin título")
                eventos_por_dia[DIAS_ES[idx_dia]].append(titulo)

    except Exception as e:
        print(f"⚠️  Error leyendo calendario: {e}. Se generarán looks genéricos.")

    return eventos_por_dia, lunes


def generar_look(dia, contexto, perfil, tendencias, looks_anteriores=""):
    evitar = f"\nPrendas ya usadas esta semana, NO repetir: {looks_anteriores}" if looks_anteriores else ""

    try:
        respuesta = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=220,
            system=f"""StyleAgent. Moda personal. Sin asteriscos, sin markdown, texto plano.
Perfil: estilo {perfil['estilo']}, colores {perfil['colores']}, evita {perfil['evitar']}, talla {perfil['talla']}.
No le gusta: {', '.join(perfil.get('feedback_negativo', [])) or 'nada'}.{evitar}
Responde EXACTAMENTE en este formato sin líneas en blanco entre ellas y sin texto extra:
Contexto: [ocasión]
Superior: [prenda]
Inferior: [prenda]
Zapato: [calzado]
Accesorio: [accesorio]""",
            messages=[{
                "role": "user",
                "content": f"{dia} — {contexto}. Tendencias PV2026: {tendencias[:300]}"
            }]
        )
        return respuesta.content[0].text.strip()
    except Exception as e:
        print(f"⚠️  Error generando look para {dia}: {e}. Usando look de respaldo.")
        return f"Contexto: {contexto}\nSuperior: Camisa blanca\nInferior: Pantalón negro recto\nZapato: Botín negro\nAccesorio: Bolso tote neutro"


def crear_email(perfil, looks_por_dia, eventos_por_dia, lunes_fecha):
    asunto = f"👗 StyleAgent — Semana del {lunes_fecha.strftime('%d/%m')}"
    cuerpo = f"Hola {perfil['nombre']}! Tus looks para esta semana 👗\n\n{'='*50}\n\n"

    for dia in DIAS_ES:
        eventos = eventos_por_dia.get(dia, [])
        agenda = ", ".join(eventos) if eventos else "Sin eventos"
        cuerpo += f"📅 {dia.upper()}\n📌 {agenda}\n\n{looks_por_dia[dia]}\n\n{'-'*40}\n\n"

    cuerpo += "¡Que tengas una semana llena de estilo!\nStyleAgent 🎨"
    return asunto, cuerpo


def enviar_email(creds, destinatario, asunto, cuerpo):
    try:
        servicio = build("gmail", "v1", credentials=creds)
        mensaje = MIMEText(cuerpo)
        mensaje["to"] = destinatario
        mensaje["subject"] = asunto
        raw = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
        servicio.users().messages().send(userId="me", body={"raw": raw}).execute()
        return True
    except Exception as e:
        print(f"⚠️  Error enviando email: {e}")
        return False


def main():
    print("🎨 StyleAgent — Digest Semanal\n")

    perfil = cargar_perfil()

    print("🔐 Autenticando con Google...")
    creds = autenticar_google()

    print("📅 Leyendo Google Calendar...")
    eventos_por_dia, lunes_fecha = leer_calendario_semana(creds)

    print(f"\n   Semana del {lunes_fecha.strftime('%d/%m')}:\n")
    for dia in DIAS_ES:
        eventos = eventos_por_dia[dia]
        print(f"   {dia}: {', '.join(eventos) if eventos else 'sin eventos'}")

    confirmar = input("\n¿Genero los looks y envío el email? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Cancelado.")
        return

    print("\n🔍 Buscando tendencias...")
    try:
        resultados = tavily.search(query="tendencias moda primavera verano 2026", max_results=2)
        tendencias = "\n".join([r["content"][:150] for r in resultados["results"]])
        if not tendencias.strip():
            raise ValueError("Sin resultados")
    except Exception:
        tendencias = "Tendencias PV2026: colores tierra, lino, minimalismo, azul marino."
        print("   ⚠️  Usando tendencias de respaldo.")

    print("\n👗 Generando looks...")
    looks_por_dia = {}
    looks_generados = ""

    for dia in DIAS_ES:
        eventos = eventos_por_dia[dia]
        contexto = ", ".join(eventos) if eventos else "día sin planes, propón look casual de tendencia"
        looks_por_dia[dia] = generar_look(dia, contexto, perfil, tendencias, looks_generados)
        looks_generados += " | " + looks_por_dia[dia]
        print(f"   ✅ {dia}")

    tu_email = os.getenv("TU_EMAIL")
    if not tu_email:
        print("⚠️  No se encontró TU_EMAIL en el archivo .env")
        return

    asunto, cuerpo = crear_email(perfil, looks_por_dia, eventos_por_dia, lunes_fecha)
    exito = enviar_email(creds, tu_email, asunto, cuerpo)

    if exito:
        print(f"\n✅ Email enviado a {tu_email} — semana del {lunes_fecha.strftime('%d/%m')} lista.")
    else:
        print("\n❌ No se pudo enviar el email. Revisa tu conexión e inténtalo de nuevo.")


if __name__ == "__main__":
    main()