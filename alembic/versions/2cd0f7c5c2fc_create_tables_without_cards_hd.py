"""create_tables_without_cards_hd

Revision ID: 2cd0f7c5c2fc
Revises: 
Create Date: 2026-02-10 11:46:54.079655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '2cd0f7c5c2fc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем все таблицы КРОМЕ cards (она уже должна существовать)
    
    # Таблица users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('language', sa.String(), server_default=text("'ru'"), nullable=True),
        
        # Основная валюта
        sa.Column('coins', sa.Integer(), server_default=text('500'), nullable=True),
        sa.Column('dust', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Прогресс
        sa.Column('level', sa.Integer(), server_default=text('1'), nullable=True),
        sa.Column('total_experience', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('cards_opened', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Колода
        sa.Column('selected_deck', postgresql.JSON(astext_type=sa.Text()), server_default=text("'[]'"), nullable=True),
        
        # Лимиты и таймеры
        sa.Column('expeditions_slots', sa.Integer(), server_default=text('2'), nullable=True),
        sa.Column('last_trade_time', sa.DateTime(), nullable=True),
        sa.Column('trade_cooldown_hours', sa.Integer(), server_default=text('12'), nullable=True),
        
        # Статистика
        sa.Column('arena_wins', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('arena_losses', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('arena_rating', sa.Integer(), server_default=text('1000'), nullable=True),
        sa.Column('total_expeditions', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('total_duplicates_dusted', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('total_cards_upgraded', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Достижения
        sa.Column('achievements', postgresql.JSON(astext_type=sa.Text()), server_default=text("'{}'"), nullable=True),
        
        # Время
        sa.Column('created_at', sa.DateTime(), server_default=text('now()'), nullable=True),
        sa.Column('last_active', sa.DateTime(), server_default=text('now()'), nullable=True),
        sa.Column('last_daily_tasks', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=False)
    
    # Таблица user_cards
    op.create_table('user_cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        
        # Статы копии
        sa.Column('level', sa.Integer(), server_default=text('1'), nullable=True),
        sa.Column('upgrade_points', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('times_upgraded', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Статусы
        sa.Column('is_in_deck', sa.Boolean(), server_default=text('false'), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), server_default=text('false'), nullable=True),
        sa.Column('is_in_expedition', sa.Boolean(), server_default=text('false'), nullable=True),
        sa.Column('expedition_end_time', sa.DateTime(), nullable=True),
        
        # Для боевой системы
        sa.Column('current_power', sa.Integer(), server_default=text('100'), nullable=True),
        sa.Column('current_health', sa.Integer(), server_default=text('100'), nullable=True),
        sa.Column('current_attack', sa.Integer(), server_default=text('10'), nullable=True),
        sa.Column('current_defense', sa.Integer(), server_default=text('10'), nullable=True),
        
        # Статистика использования
        sa.Column('arena_uses', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('expedition_uses', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        
        # Мета
        sa.Column('obtained_at', sa.DateTime(), server_default=text('now()'), nullable=True),
        sa.Column('source', sa.String(), server_default=text("'pack'"), nullable=True),
        
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_cards_card_id'), 'user_cards', ['card_id'], unique=False)
    op.create_index(op.f('ix_user_cards_user_id'), 'user_cards', ['user_id'], unique=False)
    
    # Таблица expeditions
    op.create_table('expeditions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Настройки экспедиции
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('expedition_type', sa.Enum('SHORT', 'MEDIUM', 'LONG', 'SPECIAL', name='expeditiontype'), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        
        # Карты в экспедиции
        sa.Column('card_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Награды
        sa.Column('reward_coins', sa.Integer(), nullable=True),
        sa.Column('reward_dust', sa.Integer(), nullable=True),
        sa.Column('reward_card_rarity', sa.String(), nullable=True),
        sa.Column('reward_card_chance', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Бонусы
        sa.Column('anime_bonus', sa.Boolean(), server_default=text('false'), nullable=True),
        sa.Column('rarity_bonus', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Время
        sa.Column('started_at', sa.DateTime(), server_default=text('now()'), nullable=True),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        
        # Статус
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'CANCELLED', name='expeditionstatus'), server_default=text("'ACTIVE'"), nullable=True),
        sa.Column('collected', sa.Boolean(), server_default=text('false'), nullable=True),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expeditions_user_id'), 'expeditions', ['user_id'], unique=False)
    
    # Таблица daily_tasks
    op.create_table('daily_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Задание
        sa.Column('task_type', sa.Enum('open_pack', 'send_expedition', 'trade_card', 'arena_battle', 'upgrade_card', 'dust_card', name='tasktype'), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('current_progress', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('required_progress', sa.Integer(), nullable=True),
        
        # Награда
        sa.Column('reward_coins', sa.Integer(), nullable=True),
        sa.Column('reward_dust', sa.Integer(), nullable=True),
        sa.Column('guaranteed_card_rarity', sa.String(), nullable=True),
        
        # Статус
        sa.Column('is_completed', sa.Boolean(), server_default=text('false'), nullable=True),
        sa.Column('is_claimed', sa.Boolean(), server_default=text('false'), nullable=True),
        
        # Время
        sa.Column('assigned_at', sa.DateTime(), server_default=text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_tasks_user_id'), 'daily_tasks', ['user_id'], unique=False)
    
    # Таблица arena_battles
    op.create_table('arena_battles',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Игроки
        sa.Column('attacker_id', sa.Integer(), nullable=False),
        sa.Column('defender_id', sa.Integer(), nullable=False),
        
        # Колоды игроков
        sa.Column('attacker_deck', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('defender_deck', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Результат
        sa.Column('winner_id', sa.Integer(), nullable=True),
        sa.Column('result', sa.String(), nullable=True),
        
        # Статистика боя
        sa.Column('rounds', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('attacker_damage', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('defender_damage', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Рейтинг
        sa.Column('attacker_rating_change', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('defender_rating_change', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('attacker_rating_before', sa.Integer(), nullable=True),
        sa.Column('defender_rating_before', sa.Integer(), nullable=True),
        
        # Награды
        sa.Column('attacker_reward_coins', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('attacker_reward_dust', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('defender_reward_coins', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('defender_reward_dust', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Карта-дроп
        sa.Column('dropped_card_id', sa.Integer(), nullable=True),
        sa.Column('dropped_to_user_id', sa.Integer(), nullable=True),
        
        # Время
        sa.Column('started_at', sa.DateTime(), server_default=text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['attacker_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['defender_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['dropped_card_id'], ['cards.id'], ),
        sa.ForeignKeyConstraint(['dropped_to_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_arena_battles_attacker_id'), 'arena_battles', ['attacker_id'], unique=False)
    op.create_index(op.f('ix_arena_battles_defender_id'), 'arena_battles', ['defender_id'], unique=False)
    
    # Таблица trades
    op.create_table('trades',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Игроки
        sa.Column('from_user_id', sa.Integer(), nullable=False),
        sa.Column('to_user_id', sa.Integer(), nullable=False),
        
        # Карты для обмена
        sa.Column('from_user_card_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('to_user_card_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Ограничения
        sa.Column('max_rarity', sa.String(), server_default=text("'S'"), nullable=True),
        sa.Column('level_reset', sa.Boolean(), server_default=text('true'), nullable=True),
        
        # Статус
        sa.Column('status', sa.Enum('pending', 'accepted', 'declined', 'completed', 'cancelled', 'expired', name='tradestatus'), server_default=text("'pending'"), nullable=True),
        
        # Подтверждения
        sa.Column('from_user_confirmed', sa.Boolean(), server_default=text('false'), nullable=True),
        sa.Column('to_user_confirmed', sa.Boolean(), server_default=text('false'), nullable=True),
        
        # Сообщение
        sa.Column('message', sa.String(), nullable=True),
        
        # Время
        sa.Column('created_at', sa.DateTime(), server_default=text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_from_user_id'), 'trades', ['from_user_id'], unique=False)
    op.create_index(op.f('ix_trades_to_user_id'), 'trades', ['to_user_id'], unique=False)
    
    # Таблица pack_openings
    op.create_table('pack_openings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        
        # Тип пачки
        sa.Column('pack_type', sa.String(), nullable=True),
        sa.Column('pack_price', sa.Integer(), nullable=True),
        
        # Полученные карты
        sa.Column('card_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('rarities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Pity-счетчики
        sa.Column('packs_since_last_a', sa.Integer(), server_default=text('0'), nullable=True),
        sa.Column('packs_since_last_s', sa.Integer(), server_default=text('0'), nullable=True),
        
        # Гарантии
        sa.Column('guaranteed_rarity', sa.String(), nullable=True),
        
        # Время
        sa.Column('opened_at', sa.DateTime(), server_default=text('now()'), nullable=True),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pack_openings_user_id'), 'pack_openings', ['user_id'], unique=False)


def downgrade() -> None:
    # Удаляем в обратном порядке (сначала таблицы с внешними ключами)
    op.drop_table('pack_openings')
    op.drop_table('trades')
    op.drop_table('arena_battles')
    op.drop_table('daily_tasks')
    op.drop_table('expeditions')
    op.drop_table('user_cards')
    op.drop_table('users')
    
    # Удаляем типы Enum (если они существуют)
    op.execute("DROP TYPE IF EXISTS expeditiontype")
    op.execute("DROP TYPE IF EXISTS expeditionstatus")
    op.execute("DROP TYPE IF EXISTS tasktype")
    op.execute("DROP TYPE IF EXISTS tradestatus")
