import telebot
import requests
from datetime import datetime
import os

# Reemplaza por tu token del bot
TOKEN = '7622519958:AAFYUQoiOUuUiME_gSqeM5vZPqRRHcJZVtc'
bot = telebot.TeleBot(TOKEN)

# Definir el ID del creador
CREATOR_ID = 7389165283  # Reemplaza con tu propio ID de usuario de Telegram

# Definir el archivo donde se guardarán los registros de interacciones
log_file = "user_interactions.txt"

# Crear el archivo si no existe
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write("🚨 *Interacciones de usuarios* 🚨\n\n")

# Guardar la interacción de los usuarios en el archivo
def log_interaction(user_id, username, chat_type, user_message, bot_reply):
    with open(log_file, "a") as f:
        f.write(f"👤 *Usuario*: {username}\n"
                f"🆔 *ID*: {user_id}\n"
                f"👥 *Tipo de chat*: {chat_type}\n"
                f"💬 *Mensaje*: {user_message}\n"
                f"🤖 *Respuesta del bot*: {bot_reply}\n"
                f"📅 *Hora*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "¡Hola! 👋 Bienvenido al bot de BIN Checker 🚨\n\n"
        "Este bot te permite verificar información sobre un BIN (Bank Identification Number). "
        "Simplemente usa el comando `/bin` seguido del número de BIN que deseas consultar.\n\n"
        "🔎 *Comandos disponibles*:\n"
        "/bin [BIN] - Consulta información sobre el BIN proporcionado.\n"
        "📜 *Cómo usar el comando `/bin`*:\n"
        "Envía un mensaje como el siguiente para verificar un BIN: `/bin 123456`\n"
        "El bot te devolverá información sobre la tarjeta asociada al BIN.\n\n"
        "¡Utiliza el bot para obtener información rápida y precisa sobre los BINs! 🚀"
    )
    bot.reply_to(message, welcome_message)

# Comando /bin
@bot.message_handler(commands=['bin'])
def bin_lookup(message):
    # Obtener el BIN enviado por el usuario
    bin_number = message.text.split()[1] if len(message.text.split()) > 1 else None

    if bin_number:
        try:
            # Hacer la solicitud a la API
            url = f"http://bin-dybd.onrender.com/{bin_number}"
            response = requests.get(url)
            data = response.json()

            # Verificar si la API devolvió información válida
            if response.status_code == 200 and data:
                # Formatear los datos con emojis y estilo
                result = (f"🔍 **Información del BIN {bin_number}** 🔍\n\n"
                          f"💳 **Marca de Tarjeta**: {data.get('Marca de carro', 'Desconocido')}\n"
                          f"💼 **Tipo de Tarjeta**: {data.get('Tipo de tarjeta', 'Desconocido')}\n"
                          f"⭐ **Nivel de Tarjeta**: {data.get('Nivel de tarjeta', 'Desconocido')}\n"
                          f"🏦 **Banco/Emisor**: {data.get('Nombre del emisor / Banco', 'Desconocido')}\n"
                          f"🌐 **Sitio Web del Emisor**: {data.get('Sitio web del emisor/banco', 'No disponible')}\n"
                          f"📞 **Teléfono del Emisor**: {data.get('Teléfono del emisor/banco', 'No disponible')}\n"
                          f"🌍 **País**: {data.get('Nombre de país ISO', 'Desconocido')} ({data.get('Código de país ISO A2', 'N/A')})\n"
                          f"💱 **Moneda**: {data.get('Moneda del país ISO', 'Desconocido')}\n\n"
                          f"🔒 **Estado de la BIN**: {'Válida ✅' if data.get('Marca de carro') != 'Desconocido' else 'No válida ❌'}")

                # Guardar la interacción
                log_interaction(message.from_user.id, message.from_user.username, message.chat.type, message.text, result)

                # Enviar la información al usuario
                bot.reply_to(message, result, parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ No se encontró información para el BIN proporcionado.")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Error al procesar la solicitud: {e}")
    else:
        bot.reply_to(message, "❗ Por favor, proporciona un BIN válido después del comando. Ejemplo: `/bin 473248`", parse_mode="Markdown")


# Comando /infobot (solo para el creador)
@bot.message_handler(commands=['infobot'])
def info_bot(message):
    if message.from_user.id == CREATOR_ID:
        # Contar el número de interacciones hoy
        with open(log_file, "r") as f:
            interactions = f.readlines()

        today = datetime.now().strftime('%Y-%m-%d')
        todays_interactions = [line for line in interactions if today in line]

        # Mostrar la cantidad de interacciones de hoy
        bot.send_message(message.chat.id, f"📊 **Usuarios que han usado el bot hoy**: {len(todays_interactions)//6}")

        # Enviar botón para descargar el informe
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = telebot.types.KeyboardButton("🗂️ Descargar informe")
        markup.add(btn)

        bot.send_message(message.chat.id, "¿Deseas descargar el informe?", reply_markup=markup)
    else:
        bot.reply_to(message, "❗ No tienes permiso para usar este comando.")

# Manejar la solicitud para descargar el informe
@bot.message_handler(func=lambda message: message.text == "🗂️ Descargar informe")
def send_report(message):
    if message.from_user.id == CREATOR_ID:
        # Enviar el archivo con las interacciones
        with open(log_file, "rb") as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.reply_to(message, "❗ No tienes permiso para descargar el informe.")

if __name__ == "__main__":
    bot.polling(none_stop=True)