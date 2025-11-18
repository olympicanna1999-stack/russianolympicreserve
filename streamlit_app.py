# 🏆 Олимпийский резерв - Веб-приложение
# Полностью рабочая версия для Streamlit Cloud
# Версия: 3.0 PRODUCTION
# Дата: 18 ноября 2025 г.

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ===== КОНФИГУРАЦИЯ =====
st.set_page_config(
    page_title="🏆 Олимпийский резерв РФ",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = 'olympic_reserve.db'
CACHE_DURATION = 3600

# Скрыть меню по умолчанию
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ===== ТЕСТОВЫЕ АККАУНТЫ =====
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin', 'sport': None},
    'curator_rowing': {'password': 'curator123', 'role': 'curator', 'sport': 'Гребля'},
    'curator_skiing': {'password': 'curator123', 'role': 'curator', 'sport': 'Лыжные гонки'},
    'curator_biathlon': {'password': 'curator123', 'role': 'curator', 'sport': 'Биатлон'},
}

# ===== ФУНКЦИИ РАБОТЫ С БД =====

@st.cache_resource
def get_db_connection():
    """Получить подключение к БД"""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        return None

@st.cache_data(ttl=CACHE_DURATION)
def load_athletes():
    """Загрузить спортсменов"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM athletes ORDER BY full_name', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_DURATION)
def load_medical_records():
    """Загрузить медицинские записи"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM medical_records ORDER BY exam_date DESC', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_DURATION)
def load_psychological_records():
    """Загрузить психологические записи"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM psychological_records', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_DURATION)
def load_financial_records():
    """Загрузить финансовые записи"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM financial_records', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_DURATION)
def load_mentorship():
    """Загрузить наставничество"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM mentorship', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_DURATION)
def load_training_camps():
    """Загрузить тренировочные сборы"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM training_camps', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_DURATION)
def load_functional_tests():
    """Загрузить функциональные тесты"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('SELECT * FROM functional_tests', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ===== АУТЕНТИФИКАЦИЯ =====

def authenticate(username, password):
    """Проверить аутентификацию"""
    if username in USERS and USERS[username]['password'] == password:
        return USERS[username]
    return None

def login_page():
    """Страница входа"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🏆 Олимпийский резерв")
        st.markdown("## Система мониторинга и управления")
        st.markdown("---")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Имя пользователя")
            password = st.text_input("🔐 Пароль", type="password")
            submit = st.form_submit_button("Войти", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.logged_in = True
                        st.success("✅ Вход выполнен!")
                        st.rerun()
                    else:
                        st.error("❌ Неверные учетные данные")
                else:
                    st.warning("⚠️ Введите имя пользователя и пароль")
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📝 **Тестовые аккаунты:**\n\n"
                "**Администратор:**\n"
                "- Логин: `admin`\n"
                "- Пароль: `admin123`\n\n"
                "**Кураторы:**\n"
                "- Логин: `curator_rowing`, `curator_skiing`, `curator_biathlon`\n"
                "- Пароль: `curator123`")

# ===== ГЛАВНОЕ ПРИЛОЖЕНИЕ =====

def main():
    """Главная функция"""
    
    # Инициализация сессии
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Боковая панель
        with st.sidebar:
            st.title("🏆 Олимпийский резерв")
            
            # Информация пользователя
            user = st.session_state.user
            username = [k for k, v in USERS.items() if v == user][0]
            
            st.markdown(f"**Пользователь:** {username}")
            st.markdown(f"**Роль:** {user['role'].title()}")
            if user['sport']:
                st.markdown(f"**Спорт:** {user['sport']}")
            
            st.markdown("---")
            
            # Навигация
            page = st.radio("📊 Навигация",
                           ["🏠 Главная",
                            "👥 Спортсмены",
                            "💼 Профиль",
                            "📈 Статистика",
                            "💰 Финансы",
                            "👨‍🏫 Наставничество"])
            
            st.markdown("---")
            
            if st.button("🚪 Выход", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        # Главный контент
        if page == "🏠 Главная":
            show_home()
        elif page == "👥 Спортсмены":
            show_athletes()
        elif page == "💼 Профиль":
            show_profile()
        elif page == "📈 Статистика":
            show_statistics()
        elif page == "💰 Финансы":
            show_finances()
        elif page == "👨‍🏫 Наставничество":
            show_mentorship()

# ===== СТРАНИЦЫ =====

def show_home():
    """Главная страница"""
    st.title("🏆 Добро пожаловать в систему управления олимпийским резервом")
    
    df_athletes = load_athletes()
    
    if df_athletes.empty:
        st.error("❌ База данных не загружена. Убедитесь, что olympic_reserve.db находится в директории.")
        return
    
    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Спортсменов", len(df_athletes))
    
    with col2:
        main_pool = len(df_athletes[df_athletes['reserve_level'] == 'Основной пул'])
        st.metric("🎯 Основной пул", main_pool)
    
    with col3:
        avg_vo2 = df_athletes['vo2_max_ml_kg_min'].mean()
        st.metric("📈 Средний VO₂max", f"{avg_vo2:.1f}")
    
    with col4:
        avg_age = df_athletes['age'].mean()
        st.metric("📅 Средний возраст", f"{avg_age:.1f} лет")
    
    st.markdown("---")
    
    # Распределение по видам спорта
    col1, col2 = st.columns(2)
    
    with col1:
        sport_counts = df_athletes['sport'].value_counts()
        fig = px.pie(values=sport_counts.values, names=sport_counts.index,
                    title="📊 Распределение по видам спорта")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        reserve_counts = df_athletes['reserve_level'].value_counts()
        fig = px.bar(x=reserve_counts.index, y=reserve_counts.values,
                    title="📊 Распределение по резервным пулам",
                    labels={'x': 'Пул', 'y': 'Количество'})
        st.plotly_chart(fig, use_container_width=True)

def show_athletes():
    """Страница со спортсменами"""
    st.title("👥 Список спортсменов")
    
    df = load_athletes()
    
    if df.empty:
        st.error("❌ Спортсмены не загружены")
        return
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sports = df['sport'].unique()
        selected_sport = st.selectbox("🏃 Вид спорта", ["Все"] + list(sports))
    
    with col2:
        reserve_levels = df['reserve_level'].unique()
        selected_reserve = st.selectbox("🎯 Резервный пул", ["Все"] + list(reserve_levels))
    
    with col3:
        gender = st.selectbox("👫 Пол", ["Все", "М", "Ж"])
    
    # Фильтрация
    if selected_sport != "Все":
        df = df[df['sport'] == selected_sport]
    
    if selected_reserve != "Все":
        df = df[df['reserve_level'] == selected_reserve]
    
    if gender != "Все":
        df = df[df['gender'] == gender]
    
    # Таблица
    display_df = df[['athlete_id', 'full_name', 'gender', 'age', 'sport',
                     'reserve_level', 'vo2_max_ml_kg_min', 'status']].copy()
    display_df.columns = ['ID', 'ФИО', 'Пол', 'Возраст', 'Вид спорта',
                          'Пул', 'VO₂max', 'Статус']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown(f"**Всего:** {len(df)} спортсменов")

def show_profile():
    """Страница профиля"""
    st.title("💼 Профиль спортсмена")
    
    df_athletes = load_athletes()
    
    if df_athletes.empty:
        st.error("❌ Спортсмены не загружены")
        return
    
    # Выбор спортсмена
    athlete_options = [f"{row['athlete_id']} - {row['full_name']}" 
                       for _, row in df_athletes.iterrows()]
    
    selected = st.selectbox("Выберите спортсмена", athlete_options)
    athlete_id = selected.split(' - ')[0]
    
    athlete = df_athletes[df_athletes['athlete_id'] == athlete_id].iloc[0]
    
    # Основная информация
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Основная информация")
        st.write(f"**ФИО:** {athlete['full_name']}")
        st.write(f"**Возраст:** {athlete['age']} лет")
        st.write(f"**Пол:** {'Мужской' if athlete['gender'] == 'М' else 'Женский'}")
        st.write(f"**Вид спорта:** {athlete['sport']}")
        st.write(f"**Статус:** {athlete['status']}")
    
    with col2:
        st.subheader("💪 Антропометрия")
        st.write(f"**Рост:** {athlete['height_cm']} см")
        st.write(f"**Вес:** {athlete['weight_kg']} кг")
        st.write(f"**Жировая ткань:** {athlete['body_fat_percent']}%")
        st.write(f"**Мышечная масса:** {athlete['muscle_mass_percent']}%")
        st.write(f"**Опыт:** {athlete['training_experience_years']} лет")
    
    with col3:
        st.subheader("🏃 Физические показатели")
        st.write(f"**VO₂max:** {athlete['vo2_max_ml_kg_min']} мл·кг⁻¹·мин⁻¹")
        st.write(f"**ЧСС покоя:** {athlete['resting_heart_rate_bpm']} уд/мин")
        st.write(f"**Макс. ЧСС:** {athlete['heart_rate_peak_bpm']} уд/мин")
        st.write(f"**Резервный пул:** {athlete['reserve_level']}")
        st.write(f"**Рейтинг:** {athlete['rating_position']} место")

def show_statistics():
    """Страница статистики"""
    st.title("📈 Статистика")
    
    df_athletes = load_athletes()
    
    if df_athletes.empty:
        st.error("❌ Данные не загружены")
        return
    
    # Выбор вида спорта
    sport = st.selectbox("Выберите вид спорта", df_athletes['sport'].unique())
    
    df_sport = df_athletes[df_athletes['sport'] == sport]
    
    # Графики
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(df_sport, x='height_cm', y='weight_kg',
                        color='gender', size='vo2_max_ml_kg_min',
                        hover_name='full_name',
                        title='Антропометрия')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(df_sport, x='vo2_max_ml_kg_min', nbins=10,
                          color='gender', barmode='overlay',
                          title='Распределение VO₂max')
        st.plotly_chart(fig, use_container_width=True)

def show_finances():
    """Страница финансов"""
    st.title("💰 Финансирование")
    
    df_financial = load_financial_records()
    
    if df_financial.empty:
        st.warning("⚠️ Финансовые данные не загружены")
        return
    
    total_budget = df_financial['total_monthly_budget_rub'].sum()
    st.metric("Общий ежемесячный бюджет", f"₽{total_budget:,.0f}")
    
    st.markdown("---")
    
    # Распределение по источникам
    budget_by_source = df_financial.groupby('funding_source')['total_monthly_budget_rub'].sum()
    
    fig = px.pie(values=budget_by_source.values, names=budget_by_source.index,
                title='Распределение по источникам финансирования')
    st.plotly_chart(fig, use_container_width=True)

def show_mentorship():
    """Страница наставничества"""
    st.title("👨‍🏫 Программа наставничества")
    
    df_mentorship = load_mentorship()
    
    if df_mentorship.empty:
        st.warning("⚠️ Данные о наставничестве не загружены")
        return
    
    display_df = df_mentorship[['athlete_id', 'mentor_name', 
                                'consultation_frequency_per_month',
                                'mentee_progress_rating_1_10']].copy()
    display_df.columns = ['ID спортсмена', 'Наставник', 
                         'Консультации/месяц', 'Оценка прогресса']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()