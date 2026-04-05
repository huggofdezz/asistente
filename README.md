# 🤖 Tu Asistente Personal de Telegram

Bot inteligente con Claude AI, completamente gratuito.

---

## 📋 PASO A PASO COMPLETO

### PASO 1 — Crear tu bot en Telegram (2 min)

1. Abre Telegram y busca **@BotFather**
2. Escríbele: `/newbot`
3. Pon el nombre de tu bot (ej: "Mi Asistente Personal")
4. Pon el username (debe terminar en `bot`, ej: `miasistente_bot`)
5. BotFather te dará un token así: `7123456789:AAH...`
6. **Guarda ese token** — lo necesitarás luego

### PASO 2 — Obtener tu API Key de Anthropic (gratis)

1. Ve a **https://console.anthropic.com**
2. Crea una cuenta gratuita (no pide tarjeta)
3. Ve a "API Keys" → "Create Key"
4. Copia la key (empieza con `sk-ant-...`)
5. **Guárdala** — solo se muestra una vez

> 💡 Anthropic da créditos gratuitos al registrarte (~$5 USD)
> El modelo `claude-haiku-4-5` es muy económico — te duran meses

### PASO 3 — Saber tu ID de Telegram (opcional, para seguridad)

1. Busca **@userinfobot** en Telegram
2. Escríbele `/start`
3. Te dirá tu ID numérico (ej: `123456789`)
4. Guárdalo si quieres que solo tú uses el bot

### PASO 4 — Subir el código a GitHub

1. Crea cuenta en **https://github.com** si no tienes
2. Crea un repositorio nuevo (ponle "mi-bot-telegram")
3. Sube todos los archivos de esta carpeta
   - Si sabes usar git:
     ```bash
     git init
     git add .
     git commit -m "Mi bot"
     git remote add origin https://github.com/TU_USUARIO/mi-bot-telegram.git
     git push -u origin main
     ```
   - Si no sabes git: usa la interfaz web de GitHub (arrastra los archivos)
4. **⚠️ NO subas el archivo `.env`** (está en .gitignore por seguridad)

### PASO 5 — Desplegar en Railway (gratis, 24/7)

1. Ve a **https://railway.app**
2. Entra con tu cuenta de GitHub
3. Haz clic en **"New Project"**
4. Selecciona **"Deploy from GitHub repo"**
5. Elige tu repositorio `mi-bot-telegram`
6. Railway detectará el `Procfile` automáticamente

**Añadir las variables de entorno en Railway:**
1. En tu proyecto, ve a la pestaña **"Variables"**
2. Añade estas 3 variables:
   ```
   TELEGRAM_TOKEN     = (tu token de BotFather)
   ANTHROPIC_API_KEY  = (tu API key de Anthropic)
   YOUR_TELEGRAM_ID   = (tu ID de Telegram, opcional)
   ```
3. Railway reiniciará el bot automáticamente

### PASO 6 — ¡Probar tu bot!

1. Ve a Telegram y busca el username de tu bot
2. Escríbele `/start`
3. ¡Listo! Ya tienes tu asistente personal funcionando 🎉

---

## 💬 Cómo usarlo

Una vez activo, simplemente escríbele en lenguaje natural:

| Lo que escribes | Lo que hace |
|----------------|-------------|
| "añade tarea: comprar leche" | Añade la tarea a tu lista |
| "ya fui al gym" | Registra el hábito |
| "anota: contraseña wifi es 1234" | Guarda la nota |
| "¿qué tengo pendiente?" | Te muestra tus tareas |
| "dame un resumen del día" | Resumen completo |
| Cualquier pregunta | Responde con IA |

### Comandos disponibles
- `/start` — Menú principal
- `/tareas` — Ver tareas pendientes
- `/notas` — Ver notas guardadas
- `/habitos` — Ver hábitos de hoy
- `/resumen` — Resumen del día

---

## 🆓 ¿De verdad es gratis?

| Servicio | Plan gratuito |
|---------|--------------|
| Telegram Bot API | ✅ Siempre gratis |
| Railway | ✅ 500 horas/mes gratis |
| Anthropic (Claude) | ✅ ~$5 de créditos gratis |

> Con uso personal normal, los créditos de Anthropic duran **varios meses**.
> El modelo `claude-haiku-4-5` cuesta ~$0.001 por conversación.

---

## 🔧 Personalización

Puedes editar `bot.py` para:
- Cambiar el idioma o tono del bot (en el `system_prompt`)
- Añadir más comandos
- Integrar con otras APIs (clima, noticias, etc.)
- Cambiar cuántos mensajes recuerda (variable `20` en `save_message`)

---

## ❓ Problemas frecuentes

**El bot no responde:**
- Verifica que las variables de entorno estén bien en Railway
- Revisa los logs en Railway (pestaña "Deployments")

**Error de API Key:**
- La key de Anthropic solo se muestra una vez, créa una nueva si la perdiste

**Railway no arranca el bot:**
- Asegúrate de que el archivo `Procfile` está en la raíz del proyecto
