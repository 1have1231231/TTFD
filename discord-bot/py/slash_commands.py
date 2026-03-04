# Slash команды для Discord бота
import discord
from discord import app_commands
from discord.ext import commands
from font_converter import convert_to_font
from theme import BotTheme

async def setup_slash_commands(bot, db):
    """Регистрация всех slash команд"""
    
    @bot.tree.command(name="profile", description="Посмотреть профиль пользователя")
    @app_commands.describe(member="Пользователь (оставь пустым чтобы посмотреть свой)")
    async def profile_slash(interaction: discord.Interaction, member: discord.Member = None):
        """Slash команда для профиля"""
        target = member or interaction.user
        user_data = db.get_user(str(target.id))
        
        embed = BotTheme.create_embed(
            title=convert_to_font(f"📊 профиль {target.name}"),
            embed_type='info'
        )
        
        embed.add_field(
            name=convert_to_font("💎 xp"),
            value=convert_to_font(str(user_data.get('xp', 0))),
            inline=True
        )
        
        embed.add_field(
            name=convert_to_font("💰 монеты"),
            value=convert_to_font(str(user_data.get('coins', 0))),
            inline=True
        )
        
        embed.add_field(
            name=convert_to_font("🎮 игр сыграно"),
            value=convert_to_font(str(user_data.get('games_played', 0))),
            inline=True
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="balance", description="Посмотреть баланс монет")
    @app_commands.describe(member="Пользователь (оставь пустым чтобы посмотреть свой)")
    async def balance_slash(interaction: discord.Interaction, member: discord.Member = None):
        """Slash команда для баланса"""
        target = member or interaction.user
        user_data = db.get_user(str(target.id))
        
        embed = BotTheme.create_embed(
            title=convert_to_font(f"💰 баланс {target.name}"),
            description=convert_to_font(f"монеты: {user_data.get('coins', 0)}"),
            embed_type='success'
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="rank", description="Посмотреть свой ранг")
    async def rank_slash(interaction: discord.Interaction):
        """Slash команда для ранга"""
        user_data = db.get_user(str(interaction.user.id))
        xp = user_data.get('xp', 0)
        rank_id = user_data.get('rank_id', 1)
        
        from database import RANKS
        current_rank = RANKS[rank_id - 1]
        
        # Следующий ранг
        next_rank = RANKS[rank_id] if rank_id < len(RANKS) else None
        
        embed = BotTheme.create_embed(
            title=convert_to_font(f"🏆 твой ранг"),
            embed_type='info'
        )
        
        embed.add_field(
            name=convert_to_font("текущий ранг"),
            value=f"{current_rank['emoji']} {convert_to_font(current_rank['name'])}",
            inline=False
        )
        
        embed.add_field(
            name=convert_to_font("💎 твой xp"),
            value=convert_to_font(str(xp)),
            inline=True
        )
        
        if next_rank:
            xp_needed = next_rank['required_xp'] - xp
            embed.add_field(
                name=convert_to_font(f"до {next_rank['name']}"),
                value=convert_to_font(f"ещё {xp_needed} xp"),
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="top", description="Таблица лидеров")
    @app_commands.describe(category="Категория (xp, coins, games)")
    @app_commands.choices(category=[
        app_commands.Choice(name="XP", value="xp"),
        app_commands.Choice(name="Монеты", value="coins"),
        app_commands.Choice(name="Игры", value="games")
    ])
    async def top_slash(interaction: discord.Interaction, category: str = "xp"):
        """Slash команда для топа"""
        all_users = db.get_all_users()
        
        # Сортировка
        if category == 'xp':
            sorted_users = sorted(all_users.items(), key=lambda x: x[1].get('xp', 0), reverse=True)
            title = "💎 топ по xp"
        elif category == 'coins':
            sorted_users = sorted(all_users.items(), key=lambda x: x[1].get('coins', 0), reverse=True)
            title = "💰 топ по монетам"
        else:
            sorted_users = sorted(all_users.items(), key=lambda x: x[1].get('games_played', 0), reverse=True)
            title = "🎮 топ по играм"
        
        embed = BotTheme.create_embed(
            title=convert_to_font(title),
            embed_type='info'
        )
        
        # Топ 10
        for i, (user_id, user_data) in enumerate(sorted_users[:10], 1):
            try:
                member = interaction.guild.get_member(int(user_id))
                if member:
                    if category == 'xp':
                        value = user_data.get('xp', 0)
                    elif category == 'coins':
                        value = user_data.get('coins', 0)
                    else:
                        value = user_data.get('games_played', 0)
                    
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {member.name}",
                        value=convert_to_font(str(value)),
                        inline=False
                    )
            except:
                pass
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="shop", description="Открыть магазин ролей")
    async def shop_slash(interaction: discord.Interaction):
        """Slash команда для магазина ролей"""
        user_data = db.get_user(str(interaction.user.id))
        
        # Роли в магазине
        roles_data = [
            {"role_id": 1478224551287590983, "price": 20000, "emoji": "💎", "name": "Премиум"},
            {"role_id": 1478208144319582312, "price": 15000, "emoji": "👑", "name": "VIP"},
            {"role_id": 1478222910794502335, "price": 15000, "emoji": "⭐", "name": "Звезда"},
            {"role_id": 1478226541094637628, "price": 5000, "emoji": "🎯", "name": "Саппорт"},
        ]
        
        embed = BotTheme.create_embed(
            title=convert_to_font("🏪 магазин ролей"),
            description=convert_to_font(f"твой баланс: {user_data.get('coins', 0)} монет"),
            embed_type='info'
        )
        
        for role_data in roles_data:
            role = interaction.guild.get_role(role_data["role_id"])
            if role:
                has_role = role in interaction.user.roles
                status = "✅ куплено" if has_role else f"{role_data['price']} монет"
                
                embed.add_field(
                    name=f"{role_data['emoji']} {role_data['name']}",
                    value=convert_to_font(f"{role.mention}\n{status}"),
                    inline=True
                )
        
        embed.add_field(
            name=convert_to_font("💱 обмен XP"),
            value=convert_to_font("используй /exchange для обмена XP на монеты\n1 XP = 5 монет"),
            inline=False
        )
        
        embed.set_footer(text=convert_to_font("используй /buyrole [id роли] для покупки"))
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="exchange", description="Обменять XP на монеты")
    @app_commands.describe(xp_amount="Количество XP для обмена (1 XP = 5 монет)")
    async def exchange_slash(interaction: discord.Interaction, xp_amount: int):
        """Slash команда для обмена XP на монеты"""
        if xp_amount <= 0:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("укажи положительное количество XP"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        from shop_system import exchange_xp_to_coins
        
        result = exchange_xp_to_coins(db, str(interaction.user.id), xp_amount)
        
        if not result['success']:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка обмена"),
                description=convert_to_font(result['error']),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = BotTheme.create_embed(
            title=convert_to_font("💱 обмен выполнен!"),
            description=convert_to_font(f"обменял {result['xp_spent']} XP на {result['coins_received']} монет"),
            embed_type='success'
        )
        embed.add_field(
            name=convert_to_font("💎 твой XP"),
            value=convert_to_font(str(result['new_xp'])),
            inline=True
        )
        embed.add_field(
            name=convert_to_font("💰 твои монеты"),
            value=convert_to_font(str(result['new_coins'])),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="inventory", description="Посмотреть инвентарь")
    @app_commands.describe(member="Пользователь (оставь пустым чтобы посмотреть свой)")
    async def inventory_slash(interaction: discord.Interaction, member: discord.Member = None):
        """Slash команда для инвентаря"""
        target = member or interaction.user
        user_data = db.get_user(str(target.id))
        inventory = user_data.get('inventory', [])
        
        embed = BotTheme.create_embed(
            title=convert_to_font(f"🎒 инвентарь {target.name}"),
            embed_type='info'
        )
        
        if not inventory:
            embed.description = convert_to_font("инвентарь пуст")
        else:
            for item in inventory:
                embed.add_field(
                    name=convert_to_font(item.get('name', 'предмет')),
                    value=convert_to_font(f"количество: {item.get('quantity', 1)}"),
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="daily", description="Получить ежедневную награду")
    async def daily_slash(interaction: discord.Interaction):
        """Slash команда для ежедневной награды"""
        user_data = db.get_user(str(interaction.user.id))
        
        from datetime import datetime, timedelta
        last_daily = user_data.get('last_daily')
        
        if last_daily:
            # Если это строка - конвертируем в datetime (для JSON)
            if isinstance(last_daily, str):
                last_daily_time = datetime.fromisoformat(last_daily)
            else:
                # PostgreSQL возвращает datetime объект напрямую
                last_daily_time = last_daily
            
            time_since = datetime.now() - last_daily_time
            
            if time_since < timedelta(hours=24):
                time_left = timedelta(hours=24) - time_since
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                
                embed = BotTheme.create_embed(
                    title=convert_to_font("⏰ слишком рано"),
                    description=convert_to_font(f"следующая награда через: {hours}ч {minutes}м"),
                    embed_type='error'
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Выдаём награду
        reward_coins = 100
        reward_xp = 50
        
        user_data['coins'] = user_data.get('coins', 0) + reward_coins
        user_data['xp'] = user_data.get('xp', 0) + reward_xp
        user_data['last_daily'] = datetime.now().isoformat()
        
        db.save_user(str(interaction.user.id), user_data)
        
        embed = BotTheme.create_embed(
            title=convert_to_font("🎁 ежедневная награда"),
            description=convert_to_font(f"ты получил:\n💰 {reward_coins} монет\n💎 {reward_xp} xp"),
            embed_type='success'
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="work", description="Поработать и заработать монеты")
    async def work_slash(interaction: discord.Interaction):
        """Slash команда для работы"""
        user_data = db.get_user(str(interaction.user.id))
        
        from datetime import datetime, timedelta
        import random
        
        last_work = user_data.get('last_work')
        
        if last_work:
            # Если это строка - конвертируем в datetime (для JSON)
            if isinstance(last_work, str):
                last_work_time = datetime.fromisoformat(last_work)
            else:
                # PostgreSQL возвращает datetime объект напрямую
                last_work_time = last_work
            
            time_since = datetime.now() - last_work_time
            
            if time_since < timedelta(hours=1):
                time_left = timedelta(hours=1) - time_since
                minutes = int(time_left.total_seconds() // 60)
                
                embed = BotTheme.create_embed(
                    title=convert_to_font("⏰ ты устал"),
                    description=convert_to_font(f"отдохни ещё {minutes} минут"),
                    embed_type='error'
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Работа
        reward_coins = random.randint(50, 150)
        reward_xp = random.randint(10, 30)
        
        jobs = [
            "поработал курьером",
            "помог в магазине",
            "убрал мусор",
            "выгулял собак",
            "помыл машины"
        ]
        
        job = random.choice(jobs)
        
        user_data['coins'] = user_data.get('coins', 0) + reward_coins
        user_data['xp'] = user_data.get('xp', 0) + reward_xp
        user_data['last_work'] = datetime.now().isoformat()
        
        db.save_user(str(interaction.user.id), user_data)
        
        embed = BotTheme.create_embed(
            title=convert_to_font("💼 работа"),
            description=convert_to_font(f"ты {job} и заработал:\n💰 {reward_coins} монет\n💎 {reward_xp} xp"),
            embed_type='success'
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="clear", description="Очистить сообщения (только для администраторов)")
    @app_commands.describe(amount="Количество сообщений для удаления (1-100)")
    async def clear_slash(interaction: discord.Interaction, amount: int = 10):
        """Slash команда для очистки сообщений"""
        # Проверка прав администратора
        if not interaction.user.guild_permissions.administrator:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ нет прав"),
                description=convert_to_font("у тебя нет прав администратора"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount < 1 or amount > 100:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("укажи число от 1 до 100"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Отправляем ephemeral ответ (видно только пользователю)
        await interaction.response.send_message(
            convert_to_font(f"🗑️ удаляю {amount} сообщений..."),
            ephemeral=True
        )
        
        # Удаляем сообщения
        deleted = await interaction.channel.purge(limit=amount)
        
        # Обновляем ephemeral ответ
        await interaction.edit_original_response(
            content=convert_to_font(f"✅ удалено сообщений: {len(deleted)}")
        )
    
    @bot.tree.command(name="help", description="Список всех команд")
    async def help_slash(interaction: discord.Interaction):
        """Slash команда для помощи (динамический список)"""
        # Получаем все зарегистрированные команды
        cmds = bot.tree.get_commands()
        
        # Группируем команды по категориям
        categories = {
            '👤 Профиль': ['profile', 'balance', 'rank', 'top', 'stats'],
            '🛒 Магазин': ['shop', 'inventory', 'buy', 'pay'],
            '💰 Заработок': ['daily', 'work'],
            '🎮 Игры': ['dice', 'coinflip'],
            '🎮 Интеграция': ['gamelink', 'unlink', 'gamestats'],
            '🎫 Поддержка': ['ticket', 'close'],
            '⚙️ Утилиты': ['clear', 'help', 'ping', 'links']
        }
        
        embed = BotTheme.create_embed(
            title=convert_to_font("📋 список команд"),
            description=convert_to_font(f"всего команд: {len(cmds)}"),
            embed_type='info'
        )
        
        # Создаём словарь команд для быстрого поиска
        cmd_dict = {c.name: c for c in cmds}
        
        # Добавляем команды по категориям
        for category, cmd_names in categories.items():
            lines = []
            for name in cmd_names:
                if name in cmd_dict:
                    cmd = cmd_dict[name]
                    desc = cmd.description or 'без описания'
                    lines.append(f"/{name} — {convert_to_font(desc)}")
            
            if lines:
                embed.add_field(
                    name=convert_to_font(category),
                    value='\n'.join(lines),
                    inline=False
                )
        
        embed.add_field(
            name=convert_to_font("📍 канал команд"),
            value=f"<#1466295322002067607>",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="ping", description="Проверка задержки бота")
    async def ping_slash(interaction: discord.Interaction):
        """Slash команда для пинга"""
        latency = round(bot.latency * 1000)
        embed = BotTheme.create_embed(
            title=convert_to_font("🏓 понг!"),
            description=convert_to_font(f"задержка: {latency}ms"),
            embed_type='info'
        )
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="stats", description="Статистика бота")
    async def stats_slash(interaction: discord.Interaction):
        """Slash команда для статистики"""
        from datetime import datetime
        
        if bot.stats['start_time']:
            uptime = datetime.now() - bot.stats['start_time']
            hours, remainder = divmod(int(uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{hours}ч {minutes}м {seconds}с"
        else:
            uptime_str = "Неизвестно"
        
        embed = BotTheme.create_embed(
            title=convert_to_font("📊 статистика бота"),
            embed_type='info'
        )
        embed.timestamp = datetime.now()
        embed.add_field(name=convert_to_font("⏰ аптайм"), value=convert_to_font(uptime_str), inline=True)
        embed.add_field(name=convert_to_font("🌐 серверов"), value=convert_to_font(str(len(bot.guilds))), inline=True)
        embed.add_field(name=convert_to_font("👥 пользователей"), value=convert_to_font(str(len(bot.users))), inline=True)
        embed.add_field(name=convert_to_font("📝 команд использовано"), value=convert_to_font(str(bot.stats['commands_used'])), inline=True)
        embed.add_field(name=convert_to_font("💬 сообщений обработано"), value=convert_to_font(str(bot.stats['messages_seen'])), inline=True)
        embed.add_field(name=convert_to_font("📡 задержка"), value=convert_to_font(f"{round(bot.latency * 1000)}ms"), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="links", description="Актуальные ссылки")
    async def links_slash(interaction: discord.Interaction):
        """Slash команда для ссылок"""
        embed = BotTheme.create_embed(
            title=convert_to_font("🔗 актуальные ссылки"),
            description=convert_to_font("все важные ссылки в одном месте!"),
            embed_type='info'
        )
        embed.add_field(
            name=convert_to_font("🌐 сайт"),
            value="[перейти на сайт](https://bubbly-blessing-production-0c06.up.railway.app/)",
            inline=False
        )
        embed.add_field(
            name=convert_to_font("💬 discord"),
            value="[сервер discord](https://discord.gg/your-invite)",
            inline=False
        )
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="buyrole", description="Купить роль за монеты")
    @app_commands.describe(role="Роль которую хочешь купить")
    async def buyrole_slash(interaction: discord.Interaction, role: discord.Role):
        """Slash команда для покупки роли"""
        # Роли в магазине с ценами
        roles_prices = {
            1478224551287590983: {"price": 20000, "emoji": "💎", "name": "Премиум"},
            1478208144319582312: {"price": 15000, "emoji": "👑", "name": "VIP"},
            1478222910794502335: {"price": 15000, "emoji": "⭐", "name": "Звезда"},
            1478226541094637628: {"price": 5000, "emoji": "🎯", "name": "Саппорт"},
        }
        
        # Проверяем что роль есть в магазине
        if role.id not in roles_prices:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("эта роль не продаётся в магазине"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Проверяем что роль ещё не куплена
        if role in interaction.user.roles:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("у тебя уже есть эта роль!"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        role_info = roles_prices[role.id]
        price = role_info["price"]
        
        user_data = db.get_user(str(interaction.user.id))
        
        # Проверяем баланс
        if user_data.get('coins', 0) < price:
            needed = price - user_data.get('coins', 0)
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ недостаточно монет"),
                description=convert_to_font(f"нужно: {price} монет\nу тебя: {user_data.get('coins', 0)} монет\nне хватает: {needed} монет"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Покупка
        user_data['coins'] -= price
        db.save_user(str(interaction.user.id), user_data)
        
        # Выдаём роль
        try:
            await interaction.user.add_roles(role)
            
            embed = BotTheme.create_embed(
                title=convert_to_font("✅ покупка успешна!"),
                description=convert_to_font(f"ты купил роль {role.mention}"),
                embed_type='success'
            )
            embed.add_field(
                name=convert_to_font("💰 потрачено"),
                value=convert_to_font(f"{price} монет"),
                inline=True
            )
            embed.add_field(
                name=convert_to_font("💰 осталось"),
                value=convert_to_font(f"{user_data['coins']} монет"),
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            # Возвращаем монеты если не удалось выдать роль
            user_data['coins'] += price
            db.save_user(str(interaction.user.id), user_data)
            
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("не удалось выдать роль. монеты возвращены."),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="pay", description="Перевести монеты другому пользователю")
    @app_commands.describe(member="Кому перевести", amount="Сумма")
    async def pay_slash(interaction: discord.Interaction, member: discord.Member, amount: int):
        """Slash команда для перевода монет"""
        if member == interaction.user:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("нельзя перевести монеты самому себе!"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member.bot:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("нельзя перевести монеты боту!"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount <= 0:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("сумма должна быть больше 0!"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        sender = db.get_user(str(interaction.user.id))
        receiver = db.get_user(str(member.id))
        
        if sender.get('coins', 0) < amount:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ недостаточно монет"),
                description=convert_to_font(f"у тебя: {sender.get('coins', 0)} монет"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Перевод
        sender['coins'] = sender.get('coins', 0) - amount
        receiver['coins'] = receiver.get('coins', 0) + amount
        
        db.save_user(str(interaction.user.id), sender)
        db.save_user(str(member.id), receiver)
        
        embed = BotTheme.create_embed(
            title=convert_to_font("💸 перевод выполнен!"),
            description=convert_to_font(f"{interaction.user.mention} → {member.mention}"),
            embed_type='success'
        )
        embed.add_field(
            name=convert_to_font("сумма"),
            value=convert_to_font(f"{amount} монет"),
            inline=True
        )
        embed.add_field(
            name=convert_to_font("твой баланс"),
            value=convert_to_font(f"{sender['coins']} монет"),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="dice", description="Бросить кубик (1 раз в час)")
    async def dice_slash(interaction: discord.Interaction):
        """Slash команда для броска кубика"""
        from datetime import datetime, timedelta
        import random
        
        try:
            user_data = db.get_user(str(interaction.user.id))
            
            # Проверка кулдауна
            if 'last_dice' in user_data and user_data['last_dice']:
                last_dice = user_data['last_dice']
                # Если это строка - конвертируем в datetime
                if isinstance(last_dice, str):
                    last_dice = datetime.fromisoformat(last_dice)
                
                time_diff = (datetime.now() - last_dice).total_seconds()
                
                if time_diff < 3600:
                    time_left = 3600 - time_diff
                    hours = int(time_left // 3600)
                    minutes = int((time_left % 3600) // 60)
                    
                    embed = BotTheme.create_embed(
                        title=convert_to_font("⏰ слишком рано"),
                        description=convert_to_font(f"следующий бросок через: {hours}ч {minutes}м"),
                        embed_type='error'
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            result = random.randint(1, 6)
            xp_reward = result * 5
            
            # Сохраняем старый XP для проверки повышения ранга
            old_xp = user_data.get('xp', 0)
            
            user_data['xp'] = old_xp + xp_reward
            user_data['games_played'] = user_data.get('games_played', 0) + 1
            
            if result >= 5:
                user_data['games_won'] = user_data.get('games_won', 0) + 1
            
            user_data['last_dice'] = datetime.now().isoformat()
            
            # Проверяем повышение ранга
            db.check_rank_up(user_data)
            db.save_user(str(interaction.user.id), user_data)
            
            dice_emoji = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
            
            embed = BotTheme.create_embed(
                title=convert_to_font("🎲 бросок кубика"),
                description=convert_to_font(f"выпало: {dice_emoji[result-1]} {result}"),
                embed_type='info'
            )
            embed.add_field(
                name=convert_to_font("💎 получено xp"),
                value=convert_to_font(f"+{xp_reward}"),
                inline=True
            )
            
            if result >= 5:
                embed.add_field(
                    name=convert_to_font("🎉"),
                    value=convert_to_font("отличный бросок!"),
                    inline=True
                )
            
            embed.set_footer(text=convert_to_font("следующий бросок через 1 час"))
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"❌ Ошибка в /dice: {e}")
            import traceback
            traceback.print_exc()
            
            # Пытаемся отправить ошибку пользователю
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        convert_to_font(f"❌ ошибка: {e}"),
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        convert_to_font(f"❌ ошибка: {e}"),
                        ephemeral=True
                    )
            except:
                pass
    
    @bot.tree.command(name="coinflip", description="Подбросить монетку (1 раз в час)")
    @app_commands.describe(choice="Твой выбор: орёл или решка")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Орёл", value="орёл"),
        app_commands.Choice(name="Решка", value="решка")
    ])
    async def coinflip_slash(interaction: discord.Interaction, choice: str):
        """Slash команда для подбрасывания монетки"""
        from datetime import datetime, timedelta
        import random
        
        try:
            user_data = db.get_user(str(interaction.user.id))
            
            # Проверка кулдауна
            if 'last_coinflip' in user_data and user_data['last_coinflip']:
                last_coinflip = user_data['last_coinflip']
                # Если это строка - конвертируем в datetime
                if isinstance(last_coinflip, str):
                    last_coinflip = datetime.fromisoformat(last_coinflip)
                
                time_diff = (datetime.now() - last_coinflip).total_seconds()
                
                if time_diff < 3600:
                    time_left = 3600 - time_diff
                    hours = int(time_left // 3600)
                    minutes = int((time_left % 3600) // 60)
                    
                    embed = BotTheme.create_embed(
                        title=convert_to_font("⏰ слишком рано"),
                        description=convert_to_font(f"следующее подбрасывание через: {hours}ч {minutes}м"),
                        embed_type='error'
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            result = random.choice(['орёл', 'решка'])
            won = result == choice
            
            # Сохраняем старый XP для проверки повышения ранга
            old_xp = user_data.get('xp', 0)
            
            user_data['games_played'] = user_data.get('games_played', 0) + 1
            
            if won:
                user_data['games_won'] = user_data.get('games_won', 0) + 1
                xp_reward = 25
            else:
                xp_reward = 5
            
            user_data['xp'] = old_xp + xp_reward
            user_data['last_coinflip'] = datetime.now().isoformat()
            
            # Проверяем повышение ранга
            db.check_rank_up(user_data)
            db.save_user(str(interaction.user.id), user_data)
            
            embed = BotTheme.create_embed(
                title=convert_to_font("🪙 подбрасывание монетки"),
                description=convert_to_font("🎉 ты выиграл!" if won else "😔 ты проиграл..."),
                embed_type='success' if won else 'error'
            )
            embed.add_field(
                name=convert_to_font("твой выбор"),
                value=convert_to_font(choice.capitalize()),
                inline=True
            )
            embed.add_field(
                name=convert_to_font("результат"),
                value=convert_to_font(result.capitalize()),
                inline=True
            )
            embed.add_field(
                name=convert_to_font("💎 получено xp"),
                value=convert_to_font(f"+{xp_reward}"),
                inline=False
            )
            
            embed.set_footer(text=convert_to_font("следующее подбрасывание через 1 час"))
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"❌ Ошибка в /coinflip: {e}")
            import traceback
            traceback.print_exc()
            
            # Пытаемся отправить ошибку пользователю
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        convert_to_font(f"❌ ошибка: {e}"),
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        convert_to_font(f"❌ ошибка: {e}"),
                        ephemeral=True
                    )
            except:
                pass
    
    @bot.tree.command(name="ticket", description="Создать тикет поддержки")
    async def ticket_slash(interaction: discord.Interaction):
        """Slash команда для создания тикета"""
        import tickets_system
        
        # Создаём фейковый контекст для совместимости
        class FakeContext:
            def __init__(self, interaction):
                self.author = interaction.user
                self.guild = interaction.guild
                self.channel = interaction.channel
                self.interaction = interaction
            
            async def send(self, *args, **kwargs):
                if hasattr(self, 'interaction') and not self.interaction.response.is_done():
                    return await self.interaction.response.send_message(*args, **kwargs)
                else:
                    return await self.interaction.followup.send(*args, **kwargs)
        
        fake_ctx = FakeContext(interaction)
        await tickets_system.create_ticket(fake_ctx, bot)
    
    @bot.tree.command(name="close", description="Закрыть тикет поддержки")
    async def close_slash(interaction: discord.Interaction):
        """Slash команда для закрытия тикета"""
        import tickets_system
        
        # Создаём фейковый контекст
        class FakeContext:
            def __init__(self, interaction):
                self.author = interaction.user
                self.guild = interaction.guild
                self.channel = interaction.channel
                self.interaction = interaction
            
            async def send(self, *args, **kwargs):
                if hasattr(self, 'interaction') and not self.interaction.response.is_done():
                    return await self.interaction.response.send_message(*args, **kwargs)
                else:
                    return await self.interaction.followup.send(*args, **kwargs)
        
        fake_ctx = FakeContext(interaction)
        await tickets_system.close_ticket(fake_ctx, bot)
    
    # ==================== АДМИНСКИЕ КОМАНДЫ ====================
    
    @bot.tree.command(name="updatecommands", description="Обновить список команд в канале (только админы)")
    async def updatecommands_slash(interaction: discord.Interaction):
        """Slash команда для обновления списка команд"""
        if not interaction.user.guild_permissions.administrator:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ нет прав"),
                description=convert_to_font("у тебя нет прав администратора"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Импортируем функцию обновления
            from bot import update_commands_list
            await update_commands_list()
            
            embed = BotTheme.create_embed(
                title=convert_to_font("✅ готово"),
                description=convert_to_font("список команд обновлён!"),
                embed_type='success'
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font(f"ошибка: {e}"),
                embed_type='error'
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="setupverification", description="Настроить систему верификации (только админы)")
    async def setupverification_slash(interaction: discord.Interaction):
        """Slash команда для настройки верификации"""
        if not interaction.user.guild_permissions.administrator:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ нет прав"),
                description=convert_to_font("у тебя нет прав администратора"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            import verification_system
            success = await verification_system.setup_verification(bot)
            
            if success:
                embed = BotTheme.create_embed(
                    title=convert_to_font("✅ готово"),
                    description=convert_to_font("система верификации настроена!"),
                    embed_type='success'
                )
            else:
                embed = BotTheme.create_embed(
                    title=convert_to_font("❌ ошибка"),
                    description=convert_to_font("не удалось настроить верификацию"),
                    embed_type='error'
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font(f"ошибка: {e}"),
                embed_type='error'
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="setuptickets", description="Настроить кнопку тикетов (только админы)")
    async def setuptickets_slash(interaction: discord.Interaction):
        """Slash команда для настройки тикетов"""
        if not interaction.user.guild_permissions.administrator:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ нет прав"),
                description=convert_to_font("у тебя нет прав администратора"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            import tickets_system
            success = await tickets_system.setup_ticket_button(bot)
            
            if success:
                embed = BotTheme.create_embed(
                    title=convert_to_font("✅ готово"),
                    description=convert_to_font("кнопка тикетов настроена!"),
                    embed_type='success'
                )
            else:
                embed = BotTheme.create_embed(
                    title=convert_to_font("❌ ошибка"),
                    description=convert_to_font("не удалось настроить кнопку"),
                    embed_type='error'
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font(f"ошибка: {e}"),
                embed_type='error'
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="setuprankroles", description="Настроить роли для рангов (только админы)")
    @app_commands.describe(
        tier="Ранг (F/E/D/C/B/A/S)",
        role="Роль для этого ранга"
    )
    @app_commands.choices(tier=[
        app_commands.Choice(name="F", value="F"),
        app_commands.Choice(name="E", value="E"),
        app_commands.Choice(name="D", value="D"),
        app_commands.Choice(name="C", value="C"),
        app_commands.Choice(name="B", value="B"),
        app_commands.Choice(name="A", value="A"),
        app_commands.Choice(name="S", value="S")
    ])
    async def setuprankroles_slash(interaction: discord.Interaction, tier: str = None, role: discord.Role = None):
        """Slash команда для настройки ролей рангов"""
        if not interaction.user.guild_permissions.administrator:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ нет прав"),
                description=convert_to_font("у тебя нет прав администратора"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        import rank_roles
        
        # Если параметры не указаны - показываем текущие настройки
        if not tier or not role:
            config = rank_roles.get_rank_roles_config()
            
            embed = BotTheme.create_embed(
                title=convert_to_font("⚙️ настройка ролей рангов"),
                description=convert_to_font("текущие настройки ролей для каждого ранга"),
                embed_type='info'
            )
            
            for rank_tier in ['F', 'E', 'D', 'C', 'B', 'A', 'S']:
                role_data = config.get(rank_tier, {})
                role_id = role_data.get('role_id') if isinstance(role_data, dict) else role_data
                
                if role_id:
                    role_obj = interaction.guild.get_role(role_id)
                    if role_obj:
                        required_xp = role_data.get('required_xp', 0) if isinstance(role_data, dict) else 0
                        embed.add_field(
                            name=convert_to_font(f"ранг {rank_tier}"),
                            value=f"{role_obj.mention} ({required_xp} xp)",
                            inline=True
                        )
                    else:
                        embed.add_field(
                            name=convert_to_font(f"ранг {rank_tier}"),
                            value=convert_to_font(f"роль не найдена (id: {role_id})"),
                            inline=True
                        )
                else:
                    embed.add_field(
                        name=convert_to_font(f"ранг {rank_tier}"),
                        value=convert_to_font("не настроено"),
                        inline=True
                    )
            
            embed.add_field(
                name=convert_to_font("📝 как настроить"),
                value=convert_to_font("/setuprankroles <tier> <@role>"),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Устанавливаем роль
        success = rank_roles.set_rank_role(tier, role.id)
        
        if success:
            embed = BotTheme.create_embed(
                title=convert_to_font("✅ роль настроена!"),
                embed_type='success'
            )
            embed.add_field(
                name=convert_to_font(f"ранг {tier}"),
                value=role.mention,
                inline=True
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font("ошибка настройки роли"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="syncrankroles", description="Синхронизировать роли всех пользователей (только админы)")
    async def syncrankroles_slash(interaction: discord.Interaction):
        """Slash команда для синхронизации ролей"""
        if not interaction.user.guild_permissions.administrator:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ нет прав"),
                description=convert_to_font("у тебя нет прав администратора"),
                embed_type='error'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        embed = BotTheme.create_embed(
            title=convert_to_font("🔄 синхронизация..."),
            description=convert_to_font("начинаю синхронизацию ролей..."),
            embed_type='info'
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        try:
            import rank_roles
            stats = await rank_roles.sync_all_user_roles(bot, db)
            
            embed = BotTheme.create_embed(
                title=convert_to_font("✅ синхронизация завершена!"),
                embed_type='success'
            )
            embed.add_field(
                name=convert_to_font("всего пользователей"),
                value=convert_to_font(str(stats['total'])),
                inline=True
            )
            embed.add_field(
                name=convert_to_font("обновлено"),
                value=convert_to_font(str(stats['updated'])),
                inline=True
            )
            embed.add_field(
                name=convert_to_font("пропущено"),
                value=convert_to_font(str(stats['skipped'])),
                inline=True
            )
            embed.add_field(
                name=convert_to_font("ошибок"),
                value=convert_to_font(str(stats['errors'])),
                inline=True
            )
            
            await interaction.edit_original_response(embed=embed)
        except Exception as e:
            embed = BotTheme.create_embed(
                title=convert_to_font("❌ ошибка"),
                description=convert_to_font(f"ошибка синхронизации: {e}"),
                embed_type='error'
            )
            await interaction.edit_original_response(embed=embed)
    
    print("✅ Slash команды зарегистрированы (27 команд)")
    # ==================== КОМАНДЫ ПРИВЯЗКИ TELEGRAM ====================
    
    @bot.tree.command(name="getcode", description="Получить код для привязки Telegram аккаунта")
    async def getcode_slash(interaction: discord.Interaction):
        """Генерировать код для привязки Telegram"""
        await interaction.response.defer(ephemeral=True)
        
        discord_id = str(interaction.user.id)
        
        # Генерируем код
        import secrets
        from datetime import datetime, timedelta
        import json
        
        alphabet = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
        code = ''.join(secrets.choice(alphabet) for _ in range(6))
        
        # Сохраняем код в БД (используем game_stats для хранения)
        user = db.get_user(discord_id)
        
        # Получаем game_stats
        game_stats = user.get('game_stats', {})
        if isinstance(game_stats, str):
            game_stats = json.loads(game_stats)
        
        # Добавляем код привязки
        game_stats['link_code'] = {
            'code': code,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=3)).isoformat(),
            'used': False
        }
        
        user['game_stats'] = json.dumps(game_stats)
        db.save_user(discord_id, user)
        
        # Отправляем код в ЛС
        try:
            dm_embed = discord.Embed(
                title="🔗 Код для привязки Telegram",
                description=f"**Твой код:** `{code}`",
                color=discord.Color.green()
            )
            dm_embed.add_field(
                name="📝 Как использовать:",
                value="1. Зайди в Telegram бот\n"
                      f"2. Используй команду `/code {code}`\n"
                      "3. Аккаунты автоматически привяжутся! 🎉",
                inline=False
            )
            dm_embed.add_field(
                name="⏰ Важно:",
                value="Код действителен **3 минуты**",
                inline=False
            )
            dm_embed.set_footer(text=f"Discord ID: {discord_id}")
            
            await interaction.user.send(embed=dm_embed)
            
            # Удаляем ephemeral ответ - код уже в ЛС
            await interaction.delete_original_response()
        
        except discord.Forbidden:
            embed = discord.Embed(
                title="🔗 Код для привязки Telegram",
                description=f"**Твой код:** `{code}`",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="⚠️ Не удалось отправить в ЛС",
                value="Включи личные сообщения от участников сервера",
                inline=False
            )
            embed.add_field(
                name="📝 Как использовать:",
                value="1. Зайди в Telegram бот\n"
                      f"2. Используй команду `/code {code}`\n"
                      "3. Аккаунты автоматически привяжутся! 🎉",
                inline=False
            )
            embed.add_field(
                name="⏰ Важно:",
                value="Код действителен **3 минуты**",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    
    @bot.tree.command(name="checklink", description="Проверить статус привязки Telegram")
    async def checklink_slash(interaction: discord.Interaction):
        """Проверить привязан ли Telegram аккаунт"""
        await interaction.response.defer(ephemeral=True)
        
        discord_id = str(interaction.user.id)
        telegram_id = db.get_telegram_link(discord_id)
        
        if not telegram_id:
            embed = discord.Embed(
                title="❌ Telegram не привязан",
                description="Твой Discord не привязан к Telegram аккаунту",
                color=discord.Color.red()
            )
            embed.add_field(
                name="🔗 Как привязать?",
                value="1. Используй команду `/getcode` здесь в Discord\n"
                      "2. Получи код в личные сообщения\n"
                      "3. Зайди в Telegram бот\n"
                      "4. Используй команду `/code <КОД>`",
                inline=False
            )
        else:
            user_data = db.get_user(discord_id)
            
            embed = discord.Embed(
                title="✅ Аккаунты привязаны!",
                description="Твои аккаунты синхронизированы",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📱 Telegram",
                value=f"ID: `{telegram_id}`",
                inline=True
            )
            embed.add_field(
                name="💬 Discord",
                value=f"ID: `{discord_id}`\n"
                      f"Username: {interaction.user.name}",
                inline=True
            )
            embed.add_field(
                name="📊 Синхронизированные данные",
                value=f"💰 Монеты: {user_data.get('coins', 0)}\n"
                      f"✨ XP: {user_data.get('xp', 0)}\n"
                      f"⭐ Ранг: #{user_data.get('rank_id', 0)}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    
    @bot.tree.command(name="unlink", description="Отвязать Telegram аккаунт")
    async def unlink_slash(interaction: discord.Interaction):
        """Отвязать Telegram аккаунт от Discord"""
        await interaction.response.defer(ephemeral=True)
        
        discord_id = str(interaction.user.id)
        telegram_id = db.get_telegram_link(discord_id)
        
        if not telegram_id:
            await interaction.followup.send(
                "❌ **Telegram не привязан**\n\n"
                "У тебя нет привязанного Telegram аккаунта.",
                ephemeral=True
            )
            return
        
        db.unlink_telegram(discord_id)
        
        embed = discord.Embed(
            title="✅ Telegram отвязан",
            description=f"Telegram ID `{telegram_id}` успешно отвязан от твоего Discord",
            color=discord.Color.green()
        )
        embed.add_field(
            name="🔗 Чтобы привязать снова:",
            value="1. Используй `/getcode` здесь\n"
                  "2. Используй `/code <КОД>` в Telegram боте",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    
    print(f"✅ Slash команды зарегистрированы ({len(bot.tree.get_commands())} команд)")
