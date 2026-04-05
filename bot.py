"""
🤖 Tu Asistente Personal de Telegram
Powered by Claude AI (Anthropic) - 100% Gratuito
"""

import os
import json
import httpx
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import anthropic

# ─── Configuración ────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MEMORY_FILE = "memory.json"
YOUR_TELEGRAM_ID = os.environ.get("YOUR_TELEGRAM_ID", "")

# ─── Sistema de Memoria ───────────────────────────────────────────────────────
def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "conversations": {},
        "notes": [],
        "tasks": [],
        "habits": {},
        "preferences": {
            "nombre_usuario": "amigo",
            "idioma": "español",
            "zona_horaria": "Europe/Madrid"
        }
    }

def save_memory(memory: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def get_conversation(memory: dict, user_id: str) -> list:
    return memory["conversations"].get(user_id, [])

def save_message(memory: dict, user_id: str, role: str, content: str):
    if user_id not in memory["conversations"]:
        memory["conversations"][user_id] = []
    memory["conversations"][user_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    if len(memory["conversations"][user_id]) > 20:
        memory["conversations"][user_id] = memory["conversations"][user_id][-20:]
    save_memory(memory)

# ─── Cliente de IA ────────────────────────────────────────────────────────────
def get_ai_response(conversation_history: list, memory: dict) -> str:
    http_client = httpx.Client()
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, http_client=http_client)

    tasks_str = "\n".join([f"- {'✅' if t.get('done') else '⬜'} {t['text']}" for t in memory["tasks"][-10:]]) or "Sin tareas"
    notes_str = "\n".join([f"- {n['text']}" for n in memory["notes"][-5:]]) or "Sin notas"

    today = datetime.now().strftime("%Y-%m-%d")
    habits_today = memory["habits"].get(today, {})

    system_prompt = f"""Eres el asistente personal de {memory['preferences']['nombre_usuario']}. 
Eres inteligente, proactivo, y hablas siempre en español de manera natural y cercana.

📅 Fecha y hora actual: {datetime.now().strftime("%d/%m/%Y %H:%M")}

📋 TAREAS PENDIENTES DEL USUARIO:
{tasks_str}

📝 NOTAS RECIENTES:
{notes_str}

✅ HÁBITOS DE HOY:
{json.dumps(habits_today, ensure_ascii=False) if habits_today else "Ninguno registrado aún"}

🎯 TUS CAPACIDADES:
- Gestión de tareas: puedes añadir, marcar como hechas o borrar tareas
- Notas rápidas: guardar cualquier información importante
- Seguimiento de hábitos: registrar actividades diarias
- Conversación inteligente: responder preguntas, ayudar a pensar, dar consejos

🔧 COMANDOS QUE PUEDES EJECUTAR (inclúyelos en tu respuesta cuando sea apropiado):
- Para añadir tarea: [TAREA: descripción]
- Para completar tarea: [COMPLETAR_TAREA: número]
- Para guardar nota: [NOTA: contenido]
- Para registrar hábito: [HABITO: nombre]

Responde de forma concisa y útil. Máximo 3-4 párrafos salvo que te pidan más detalle."""

    messages = []
    for msg in conversation_history[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=messages
    )

    http_client.close()
    return response.content[0].text

def process_ai_commands(response_text: str, memory: dict) -> str:
    import re

    tarea_matches = re.findall(r'\[TAREA: ([^\]]+)\]', response_text)
    for tarea in tarea_matches:
        memory["tasks"].append({
            "text": tarea,
            "done": False,
            "created": datetime.now().isoformat()
        })
        response_text = response_text.replace(f'[TAREA: {tarea}]', f'📌 _{tarea}_ añadida a tareas')

    completar_matches = re.findall(r'\[COMPLETAR_TAREA: (\d+)\]', response_text)
    for idx in completar_matches:
        try:
            i = int(idx) - 1
            if 0 <= i < len(memory["tasks"]):
                memory["tasks"][i]["done"] = True
                response_text = response_text.replace(f'[COMPLETAR_TAREA: {idx}]', '✅')
        except:
            pass

    nota_matches = re.findall(r'\[NOTA: ([^\]]+)\]', response_text)
    for nota in nota_matches:
        memory["notes"].append({
            "text": nota,
            "created": datetime.now().isoformat()
        })
        response_text = response_text.replace(f'[NOTA: {nota}]', f'📝 _Nota guardada_')

    habito_matches = re.findall(r'\[HABITO: ([^\]]+)\]', response_text)
    today = datetime.now().strftime("%Y-%m-%d")
    for habito in habito_matches:
        if today not in memory["habits"]:
            memory["habits"][today] = {}
        memory["habits"][today][habito] = datetime.now().strftime("%H:%M")
        response_text = response_text.replace(f'[HABITO: {habito}]', f'💪 _{habito}_ registrado')

    if any([tarea_matches, completar_matches, nota_matches, habito_matches]):
        save_memory(memory)

    return response_text

# ─── Verificación de usuario ──────────────────────────────────────────────────
def is_authorized(update: Update) -> bool:
    if not YOUR_TELEGRAM_ID:
        return True
    return str(update.effective_user.id) == YOUR_TELEGRAM_ID

# ─── Comandos del Bot ─────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("❌ No tienes acceso a este bot.")
        return

    keyboard = [
        [InlineKeyboardButton("📋 Ver tareas", callback_data="ver_tareas"),
         InlineKeyboardButton("📝 Ver notas", callback_data="ver_notas")],
        [InlineKeyboardButton("💪 Hábitos de hoy", callback_data="ver_habitos"),
         InlineKeyboardButton("🆘 Ayuda", callback_data="ayuda")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    nombre = update.effective_user.first_name
    memory = load_memory()
    memory["preferences"]["nombre_usuario"] = nombre
    save_memory(memory)

    await update.message.reply_text(
        f"¡Hola {nombre}! 👋 Soy tu asistente personal.\n\n"
        f"Puedo ayudarte con:\n"
        f"• 💬 Conversar y responder preguntas\n"
        f"• 📋 Gestionar tus tareas\n"
        f"• 📝 Guardar notas\n"
        f"• 💪 Seguir tus hábitos\n\n"
        f"¡Simplemente escríbeme lo que necesitas!",
        reply_markup=reply_markup
    )

async def ver_tareas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    memory = load_memory()
    tasks = memory["tasks"]
    if not tasks:
        await update.message.reply_text("No tienes tareas. ¡Dime qué añadir!")
        return
    pendientes = [t for t in tasks if not t.get("done")]
    completadas = [t for t in tasks if t.get("done")]
    msg = "📋 *Tus tareas:*\n\n"
    if pendientes:
        msg += "*Pendientes:*\n"
        for i, t in enumerate(pendientes, 1):
            msg += f"  {i}. ⬜ {t['text']}\n"
    if completadas:
        msg += f"\n*Completadas:* {len(completadas)} ✅"
    keyboard = [[InlineKeyboardButton("🗑️ Limpiar completadas", callback_data="limpiar_completadas")]]
    await update.message.reply_text(msg, parse_mode="Markdown",
                                     reply_markup=InlineKeyboardMarkup(keyboard))

async def ver_notas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    memory = load_memory()
    notes = memory["notes"][-10:]
    if not notes:
        await update.message.reply_text("No tienes notas guardadas.")
        return
    msg = "📝 *Tus notas recientes:*\n\n"
    for i, n in enumerate(reversed(notes), 1):
        fecha = n.get("created", "")[:10]
        msg += f"{i}. {n['text']}\n   _({fecha})_\n\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ver_habitos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    memory = load_memory()
    today = datetime.now().strftime("%Y-%m-%d")
    habits_today = memory["habits"].get(today, {})
    if not habits_today:
        await update.message.reply_text(
            "💪 Aún no has registrado hábitos hoy.\n"
            "Dime algo como: _'ya hice ejercicio'_ o _'bebí 2L de agua'_",
            parse_mode="Markdown"
        )
        return
    msg = f"💪 *Hábitos de hoy ({today}):*\n\n"
    for habito, hora in habits_today.items():
        msg += f"✅ {habito} — _{hora}_\n"
    dias_con_habitos = len(memory["habits"])
    msg += f"\n🔥 Llevas *{dias_con_habitos} días* registrando hábitos"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    memory = load_memory()
    today = datetime.now().strftime("%Y-%m-%d")
    pendientes = [t for t in memory["tasks"] if not t.get("done")]
    completadas = [t for t in memory["tasks"] if t.get("done")]
    habits_today = memory["habits"].get(today, {})
    msg = f"📊 *Resumen de hoy - {today}*\n\n"
    msg += f"📋 Tareas pendientes: *{len(pendientes)}*\n"
    msg += f"✅ Tareas completadas: *{len(completadas)}*\n"
    msg += f"💪 Hábitos registrados: *{len(habits_today)}*\n"
    msg += f"📝 Notas guardadas: *{len(memory['notes'])}*\n"
    if pendientes:
        msg += f"\n*Tienes pendiente:*\n"
        for t in pendientes[:5]:
            msg += f"  • {t['text']}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ─── Manejador de Mensajes ────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    user_id = str(update.effective_user.id)
    user_text = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    memory = load_memory()
    save_message(memory, user_id, "user", user_text)

    try:
        conversation = get_conversation(memory, user_id)
        response = get_ai_response(conversation, memory)
        response = process_ai_commands(response, memory)
        save_message(memory, user_id, "assistant", response)
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ─── Manejador de Botones ─────────────────────────────────────────────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    memory = load_memory()

    if query.data == "ver_tareas":
        pendientes = [t for t in memory["tasks"] if not t.get("done")]
        if not pendientes:
            await query.message.reply_text("¡No tienes tareas pendientes! 🎉")
        else:
            msg = "📋 *Tareas pendientes:*\n\n"
            for i, t in enumerate(pendientes, 1):
                msg += f"{i}. ⬜ {t['text']}\n"
            await query.message.reply_text(msg, parse_mode="Markdown")

    elif query.data == "ver_notas":
        notes = memory["notes"][-5:]
        if not notes:
            await query.message.reply_text("No tienes notas guardadas.")
        else:
            msg = "📝 *Notas recientes:*\n\n"
            for n in reversed(notes):
                msg += f"• {n['text']}\n"
            await query.message.reply_text(msg, parse_mode="Markdown")

    elif query.data == "ver_habitos":
        today = datetime.now().strftime("%Y-%m-%d")
        habits = memory["habits"].get(today, {})
        if not habits:
            await query.message.reply_text("Aún no has registrado hábitos hoy 💪")
        else:
            msg = "💪 *Hábitos de hoy:*\n\n"
            for h, hora in habits.items():
                msg += f"✅ {h} ({hora})\n"
            await query.message.reply_text(msg, parse_mode="Markdown")

    elif query.data == "ayuda":
        await query.message.reply_text(
            "🆘 *Comandos disponibles:*\n\n"
            "/start — Menú principal\n"
            "/tareas — Ver tareas pendientes\n"
            "/notas — Ver notas guardadas\n"
            "/habitos — Ver hábitos de hoy\n"
            "/resumen — Resumen del día\n\n"
            "💬 *O simplemente escríbeme:*\n"
            "• _'añade tarea: ir al gym'_\n"
            "• _'anota que debo llamar al médico'_\n"
            "• _'ya hice mis 10.000 pasos'_\n"
            "• Cualquier pregunta que tengas 😊",
            parse_mode="Markdown"
        )

    elif query.data == "limpiar_completadas":
        before = len(memory["tasks"])
        memory["tasks"] = [t for t in memory["tasks"] if not t.get("done")]
        after = len(memory["tasks"])
        save_memory(memory)
        await query.message.reply_text(f"🗑️ Eliminadas {before - after} tareas completadas.")

# ─── Arranque del Bot ─────────────────────────────────────────────────────────
def main():
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: Falta TELEGRAM_TOKEN")
        return
    if not ANTHROPIC_API_KEY:
        print("❌ ERROR: Falta ANTHROPIC_API_KEY")
        return

    print("🤖 Iniciando bot...")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tareas", ver_tareas))
    app.add_handler(CommandHandler("notas", ver_notas))
    app.add_handler(CommandHandler("habitos", ver_habitos))
    app.add_handler(CommandHandler("resumen", resumen))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("✅ Bot activo. Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
