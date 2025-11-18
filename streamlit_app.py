# 🏆 Олимпийский резерв - Полнофункциональное приложение v4.0
# С русскими именами, спортивными результатами и графиками динамики
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

DB_NAME = 'olympic_reserve_russian.db'
CACHE_DURATION = 3600

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
        st.error(f"❌ Ошибка: {e}")
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
def load_competition_results():
    """Загрузить спортивные результаты"""
    try:
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql('''
            SELECT * FROM competition_results 
            ORDER BY competition_date DESC
        ''', conn)
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
        st.markdown("## Система управления и мониторинга")
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
                    st.warning("⚠️ Введите данные")
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📝 **Тестовые аккаунты:**\n\n"
                "- admin / admin123\n"
                "- curator_rowing / curator123\n"
                "- curator_skiing / curator123\n"
                "- curator_biathlon / curator123")

# ===== ГЛАВНОЕ ПРИЛОЖЕНИЕ =====

def main():
    """Главная функция"""
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        with st.sidebar:
            st.title("🏆 Олимпийский резерв")
            
            user = st.session_state.user
            username = [k for k, v in USERS.items() if v == user][0]
            
            st.markdown(f"**Пользователь:** {username}")
            st.markdown(f"**Роль:** {user['role'].title()}")
            if user['sport']:
                st.markdown(f"**Спорт:** {user['sport']}")
            
            st.markdown("---")
            
            page = st.radio("📊 Навигация",
                           ["🏠 Главная",
                            "👥 Спортсмены",
                            "💼 Профиль",
                            "📈 Результаты",
                            "📊 Динамика",
                            "💪 Медико-биолог."])
            
            st.markdown("---")
            
            if st.button("🚪 Выход", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        if page == "🏠 Главная":
            show_home()
        elif page == "👥 Спортсмены":
            show_athletes()
        elif page == "💼 Профиль":
            show_profile()
        elif page == "📈 Результаты":
            show_results()
        elif page == "📊 Динамика":
            show_dynamics()
        elif page == "💪 Медико-биолог.":
            show_medical()

# ===== СТРАНИЦЫ =====

def show_home():
    """Главная страница"""
    st.title("🏆 Программа развития олимпийского резерва")
    
    df_athletes = load_athletes()
    
    if df_athletes.empty:
        st.error("❌ БД не загружена")
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
        st.metric("📅 Средний возраст", f"{avg_age:.1f}")
    
    st.markdown("---")
    
    # Распределение по видам спорта
    col1, col2 = st.columns(2)
    
    with col1:
        sport_counts = df_athletes['sport'].value_counts()
        fig = px.pie(values=sport_counts.values, names=sport_counts.index,
                    title="Распределение по видам спорта")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        gender_counts = df_athletes['gender'].value_counts()
        fig = px.bar(x=['Мужчины' if g == 'М' else 'Женщины' for g in gender_counts.index], 
                    y=gender_counts.values,
                    title="Распределение по полу")
        st.plotly_chart(fig, use_container_width=True)

def show_athletes():
    """Страница спортсменов"""
    st.title("👥 Список спортсменов")
    
    df = load_athletes()
    
    if df.empty:
        st.error("❌ Данные не загружены")
        return
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sports = df['sport'].unique()
        selected_sport = st.selectbox("🏃 Вид спорта", ["Все"] + list(sports))
    
    with col2:
        regions = df['region'].unique()
        selected_region = st.selectbox("🗺️ Регион", ["Все"] + list(regions))
    
    with col3:
        gender = st.selectbox("👫 Пол", ["Все", "М", "Ж"])
    
    # Фильтрация
    if selected_sport != "Все":
        df = df[df['sport'] == selected_sport]
    if selected_region != "Все":
        df = df[df['region'] == selected_region]
    if gender != "Все":
        df = df[df['gender'] == gender]
    
    # Таблица
    display_df = df[['full_name', 'gender', 'age', 'sport', 'region',
                     'reserve_level', 'vo2_max_ml_kg_min']].copy()
    display_df.columns = ['ФИО', 'Пол', 'Возраст', 'Вид спорта', 'Регион',
                          'Пул', 'VO₂max']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown(f"**Всего:** {len(df)} спортсменов")

def show_profile():
    """Страница профиля"""
    st.title("💼 Профиль спортсмена")
    
    df_athletes = load_athletes()
    
    if df_athletes.empty:
        st.error("❌ Данные не загружены")
        return
    
    # Выбор спортсмена
    athlete_options = [f"{row['full_name']} ({row['sport']})" 
                       for _, row in df_athletes.iterrows()]
    selected = st.selectbox("Выберите спортсмена", athlete_options)
    
    athlete_name = selected.split(' (')[0]
    athlete = df_athletes[df_athletes['full_name'] == athlete_name].iloc[0]
    
    # Основная информация
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Основная информация")
        st.write(f"**ФИО:** {athlete['full_name']}")
        st.write(f"**Возраст:** {athlete['age']} лет")
        st.write(f"**Пол:** {'Мужской' if athlete['gender'] == 'М' else 'Женский'}")
        st.write(f"**Регион:** {athlete['region']}")
        st.write(f"**Вид спорта:** {athlete['sport']}")
    
    with col2:
        st.subheader("💪 Антропометрия")
        st.write(f"**Рост:** {athlete['height_cm']} см")
        st.write(f"**Вес:** {athlete['weight_kg']} кг")
        st.write(f"**Жировая ткань:** {athlete['body_fat_percent']}%")
        st.write(f"**Мышечная масса:** {athlete['muscle_mass_percent']}%")
    
    with col3:
        st.subheader("🏃 Физиологические показатели")
        st.write(f"**VO₂max:** {athlete['vo2_max_ml_kg_min']} мл·кг⁻¹·мин⁻¹")
        st.write(f"**ЧСС покоя:** {athlete['resting_heart_rate_bpm']} уд/мин")
        st.write(f"**ЧСС макс:** {athlete['heart_rate_peak_bpm']} уд/мин")
        st.write(f"**Тренировочный опыт:** {athlete['training_experience_years']} лет")

def show_results():
    """Страница спортивных результатов"""
    st.title("📈 Спортивные результаты за 2 года")
    
    df_athletes = load_athletes()
    df_results = load_competition_results()
    
    if df_results.empty or df_athletes.empty:
        st.warning("⚠️ Данные не загружены")
        return
    
    # Выбор спортсмена
    athlete_options = [f"{row['full_name']}" for _, row in df_athletes.iterrows()]
    selected = st.selectbox("Выберите спортсмена", athlete_options)
    
    athlete = df_athletes[df_athletes['full_name'] == selected].iloc[0]
    athlete_results = df_results[df_results['athlete_id'] == athlete['athlete_id']].copy()
    athlete_results['competition_date'] = pd.to_datetime(athlete_results['competition_date'])
    athlete_results = athlete_results.sort_values('competition_date')
    
    if not athlete_results.empty:
        st.subheader(f"📊 Результаты {selected}")
        
        # Таблица результатов
        display_results = athlete_results[['competition_date', 'competition_name', 
                                          'distance_km', 'finish_position', 'medal']].copy()
        display_results.columns = ['Дата', 'Соревнование', 'Дистанция', 'Место', 'Медаль']
        st.dataframe(display_results, use_container_width=True, hide_index=True)
        
        # График динамики позиций
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(athlete_results, x='competition_date', y='finish_position',
                         title='Динамика позиций',
                         labels={'competition_date': 'Дата', 'finish_position': 'Позиция'},
                         markers=True)
            fig.update_layout(yaxis_autorange='reversed')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            medal_counts = athlete_results['medal'].value_counts()
            fig = px.pie(values=medal_counts.values, names=medal_counts.index,
                        title='Распределение медалей')
            st.plotly_chart(fig, use_container_width=True)

def show_dynamics():
    """Страница динамики показателей"""
    st.title("📊 Динамика физиологических показателей")
    
    df_athletes = load_athletes()
    df_medical = load_medical_records()
    
    if df_medical.empty or df_athletes.empty:
        st.info("ℹ️ Медицинские данные еще не добавлены")
        return
    
    athlete_options = [f"{row['full_name']}" for _, row in df_athletes.iterrows()]
    selected = st.selectbox("Выберите спортсмена", athlete_options)
    
    athlete = df_athletes[df_athletes['full_name'] == selected].iloc[0]
    athlete_medical = df_medical[df_medical['athlete_id'] == athlete['athlete_id']].copy()
    
    if not athlete_medical.empty:
        athlete_medical['exam_date'] = pd.to_datetime(athlete_medical['exam_date'])
        athlete_medical = athlete_medical.sort_values('exam_date')
        
        # Графики
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(athlete_medical, x='exam_date', y='vo2_peak_ml_kg_min',
                         title='Динамика VO₂peak',
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(athlete_medical, x='exam_date', y='weight_kg',
                         title='Динамика веса',
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)

def show_medical():
    """Страница медико-биологических показателей"""
    st.title("💪 Медико-биологические показатели")
    
    df_athletes = load_athletes()
    
    if df_athletes.empty:
        st.error("❌ Данные не загружены")
        return
    
    athlete_options = [f"{row['full_name']}" for _, row in df_athletes.iterrows()]
    selected = st.selectbox("Выберите спортсмена", athlete_options)
    
    athlete = df_athletes[df_athletes['full_name'] == selected].iloc[0]
    
    st.subheader(f"📊 Показатели {selected}")
    
    # Основные показатели
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("VO₂max", f"{athlete['vo2_max_ml_kg_min']} мл·кг⁻¹·мин⁻¹")
        st.metric("Рост", f"{athlete['height_cm']} см")
        st.metric("ЧСС покоя", f"{athlete['resting_heart_rate_bpm']} уд/мин")
    
    with col2:
        st.metric("Вес", f"{athlete['weight_kg']} кг")
        st.metric("Жировая ткань", f"{athlete['body_fat_percent']}%")
        st.metric("ЧСС макс", f"{athlete['heart_rate_peak_bpm']} уд/мин")
    
    with col3:
        st.metric("Мышечная масса", f"{athlete['muscle_mass_percent']}%")
        st.metric("BMI", f"{athlete['weight_kg'] / (athlete['height_cm']/100)**2:.1f}")
        st.metric("Опыт", f"{athlete['training_experience_years']} лет")

if __name__ == "__main__":
    main()
