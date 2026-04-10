# 🎨 StyleAgent

> Agente personal de moda con IA que aprende tu estilo, busca tendencias reales y te propone looks personalizados para cada ocasión.

---

## ¿Por qué existe StyleAgent?

Perder tiempo cada mañana decidiendo qué ponerse, hacer scroll infinito en Pinterest sin encontrar inspiración, o llegar a una reunión importante sin haber pensado el look con antelación. StyleAgent nació para resolver ese problema: un agente con IA que te conoce, aprende de ti y trabaja para que tú no tengas que pensar en esto.

---

## ¿Qué hace StyleAgent?

- Onboarding visual con opciones clickables — aprende tu estilo, colores, prendas que evitas y contextos en menos de 2 minutos
- Chat de moda con búsqueda web en tiempo real — responde preguntas sobre tendencias consultando Vogue, Harper's Bazaar y desfiles de temporada
- Propone looks personalizados adaptados a tu ocasión — oficina, máster, salidas, eventos, o cualquier plan con slang incluido (vinitos, cañas, gym...)
- Aprende de tu feedback — si dices "no me gustan los flecos" nunca más te los sugiere. Si dices "me encanta este look" lo tiene en cuenta para los siguientes
- Guarda tus looks favoritos para consultarlos cuando quieras
- Enlace directo a Pinterest con tu búsqueda personalizada para inspiración visual
- Lee tu Google Calendar y adapta los looks a tus eventos reales de la semana
- Digest semanal por email — cada semana genera 7 looks (uno por día) basados en tu agenda y te los manda por Gmail
- Interfaz web profesional con Streamlit — diseño limpio tipo Zara, blanco y azul marino

---

## 🛠️ Stack tecnológico

| Herramienta | Para qué sirve |
|-------------|----------------|
| Python 3.14 | Lenguaje base del proyecto |
| Anthropic API — Claude Haiku | Motor de IA del agente |
| Tavily API | Búsqueda web de tendencias en tiempo real |
| Google Calendar API | Lee los eventos de la semana para adaptar los looks |
| Gmail API | Envío del digest semanal automático |
| Streamlit | Interfaz web visual |

---

## 💰 Coste estimado

| Servicio | Coste mensual |
|----------|---------------|
| Anthropic API (Claude Haiku) | ~$0.25 |
| Tavily API | Gratis (1000 búsquedas/mes) |
| Gmail API | Gratis |
| Google Calendar API | Gratis |
| Streamlit Cloud | Gratis |
| **TOTAL** | **~$0.25/mes** |

---

## 🗂️ Estructura del proyecto
styleagent/
├── app.py                  # Interfaz web Streamlit — chat, favoritos, digest
├── styleagent.py           # Agente de chat en terminal
├── digest.py               # Script de digest semanal con Google Calendar
├── perfil.json             # Perfil del usuario (generado en onboarding)
├── favoritos.json          # Looks guardados como favoritos
├── credentials.json        # Credenciales Google OAuth (no se sube a GitHub)
├── token.json              # Token de acceso Google (no se sube a GitHub)
├── .env                    # API keys (no se sube a GitHub)
├── .gitignore              # Archivos ignorados por Git
├── README.md               # Este archivo
└── venv/                   # Entorno virtual (no se sube a GitHub)

---

## 🚀 Cómo ejecutarlo

### 1. Clona el repositorio
```bash
git clone https://github.com/tuusuario/styleagent.git
cd styleagent
```

### 2. Crea y activa el entorno virtual
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Instala las dependencias
```bash
pip install anthropic python-dotenv tavily-python streamlit google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4. Crea el archivo `.env` con tus API keys
ANTHROPIC_API_KEY=sk-ant-tuclaveaqui
TAVILY_API_KEY=tvly-tuclaveaqui
TU_EMAIL=tuemail@gmail.com

### 5. Configura las credenciales de Google
- Ve a console.cloud.google.com
- Crea un proyecto y activa Gmail API y Google Calendar API
- Descarga las credenciales OAuth como `credentials.json`
- Colócalo en la carpeta raíz del proyecto

### 6. Ejecuta la app web
```bash
python -m streamlit run app.py
```

### O ejecuta el chat en terminal
```bash
python styleagent.py
```

### O genera el digest semanal manualmente
```bash
python digest.py
```

---

## 🧠 Cómo funciona por dentro

### El chat (styleagent.py y app.py)
Cada vez que haces una pregunta el agente:
1. Detecta si necesita pedir más contexto antes de generar el look
2. Decide si merece la pena buscar en internet (no busca para preguntas de feedback o charla)
3. Lanza una búsqueda en Tavily si la pregunta es sobre tendencias o looks
4. Construye el system prompt con tu perfil completo — estilo, colores, feedback acumulado
5. Envía el historial completo de la conversación a Claude para que tenga contexto
6. Muestra el look en formato estructurado y ofrece guardarlo en favoritos
7. Si es un look real, muestra el enlace a Pinterest con tu búsqueda personalizada

### El digest semanal (digest.py)
1. Lee tu Google Calendar para la semana siguiente
2. Busca tendencias actuales con Tavily
3. Genera un look por día adaptado a tus eventos reales
4. Evita repetir prendas a lo largo de la semana
5. Formatea el email con la agenda de cada día junto al look
6. Lo envía por Gmail automáticamente

### La memoria de feedback
Cada vez que dices "no me gusta X" o "me encanta Y", el agente lo guarda en `perfil.json`. El system prompt se reconstruye en cada conversación incluyendo todo el feedback acumulado, por lo que StyleAgent nunca olvida lo que no te gusta.

---

## 📍 Estado del proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1. Base | Chat con API de Claude y búsqueda web | ✅ Completado |
| 2. Personalización | Onboarding y perfil de usuario | ✅ Completado |
| 3. Digest semanal | Email automático con Google Calendar | ✅ Completado |
| 4. Interfaz web | App Streamlit con diseño profesional | ✅ Completado |
| 5. Favoritos | Guardar y gestionar looks favoritos | ✅ Completado |
| 6. Pinterest | Inspiración visual sin API | ✅ Completado |
| 7. Publicación | Streamlit Cloud + GitHub público | 🔜 Próximo paso |

---

## 👩‍💻 Autora

Marina Llombart — Máster en Data Analytics con IA

Proyecto construido para aprender desarrollo de agentes con IA aplicados a un problema real.