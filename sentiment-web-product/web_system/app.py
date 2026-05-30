"""
舆情分析系统 - 主应用 v3 (高级科技风格UI)
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import os
import hashlib
from datetime import datetime
from models import (
    init_db, get_session, User, Project, RawData, DataSubset,
    Brand, CompetitorProduct, LabelRule, CleanRule, ReportTemplate, ExportRecord
)
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import plotly.express as px
import plotly.graph_objects as go

# ============== 页面配置 ==============
st.set_page_config(
    page_title="舆情分析系统",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# ============== 浅色专业企业风格 CSS ==============
st.markdown("""
<style>
    /* 全局字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    }

    /* 浅色主题背景 */
    .stApp {
        background: #F5F7FA;
        color: #333333;
    }

    /* 侧边栏 - 深蓝色 */
    [data-testid="stSidebar"] {
        background: #1A3A5C;
        border-right: none;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white;
    }

    /* 顶部栏隐藏 */
    [data-testid="stHeader"] {
        display: none;
    }

    /* 隐藏默认元素 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ========== 通用卡片 ========== */
    .card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E8E8E8;
    }

    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #1A3A5C;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid #2E7DCD;
    }

    /* ========== 指标卡片 ========== */
    .metric-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E8E8E8;
        transition: all 0.2s;
    }

    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    .metric-card .label {
        color: #666666;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .metric-card .value {
        color: #2E7DCD;
        font-size: 28px;
        font-weight: 700;
    }

    .metric-card .delta {
        color: #00A5E0;
        font-size: 12px;
        margin-top: 4px;
    }

    /* ========== 标题样式 ========== */
    h1, h2, h3 {
        color: #1A3A5C;
        font-weight: 600;
    }

    h1 {
        font-size: 24px;
        color: #1A3A5C;
    }

    h2 {
        font-size: 18px;
        margin-top: 24px;
    }

    /* ========== 按钮样式 ========== */
    .stButton > button {
        background: #2E7DCD;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        padding: 8px 20px;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: #1A5C9C;
        box-shadow: 0 2px 8px rgba(46,125,205,0.3);
    }

    .stButton > button:focus {
        background: #1A5C9C;
    }

    /* 次要按钮 */
    .stButton > button[kind="secondary"] {
        background: #F5F7FA;
        color: #333333;
        border: 1px solid #DDDDDD;
    }

    /* ========== 输入框样式 ========== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: #FFFFFF;
        border: 1px solid #DDDDDD;
        border-radius: 6px;
        color: #333333;
        padding: 10px 14px;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2E7DCD;
        box-shadow: 0 0 0 2px rgba(46,125,205,0.15);
    }

    /* ========== 选择框样式 ========== */
    .stSelectbox > div > div {
        background: #FFFFFF;
        border: 1px solid #DDDDDD;
        border-radius: 6px;
    }

    /* ========== 表格样式 ========== */
    [data-testid="stDataFrame"] {
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E8E8E8;
    }

    /* ========== Tab 样式 ========== */
    .stTabs [data-baseweb="tab-list"] {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #E8E8E8;
    }

    .stTabs [data-baseweb="tab"] {
        color: #666666;
        font-weight: 500;
        border-radius: 6px;
        padding: 10px 20px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #F0F5FA;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #2E7DCD;
        color: white;
    }

    /* ========== 展开器样式 ========== */
    .streamlit-expanderHeader {
        background: #FFFFFF;
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        color: #333333;
        padding: 14px 16px;
    }

    .streamlit-expanderHeader:hover {
        background: #F5F7FA;
    }

    /* ========== 分割线 ========== */
    hr {
        border: none;
        height: 1px;
        background: #E8E8E8;
        margin: 24px 0;
    }

    /* ========== 图表容器 ========== */
    [data-testid="stVegaLiteChart"],
    [data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E8E8E8;
        padding: 16px;
    }

    /* ========== 标签样式 ========== */
    .tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    }

    .tag-success {
        background: #E8F5E9;
        color: #2E7D32;
        border: 1px solid #C8E6C9;
    }

    .tag-warning {
        background: #FFF8E1;
        color: #F57C00;
        border: 1px solid #FFE082;
    }

    .tag-info {
        background: #E3F2FD;
        color: #2E7DCD;
        border: 1px solid #BBDEFB;
    }

    .tag-danger {
        background: #FFEBEE;
        color: #D32F2F;
        border: 1px solid #FFCDD2;
    }

    /* ========== 登录页面 - Google风格 ========== */
    .login-page {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Google Sans', 'Roboto', 'PingFang SC', sans-serif;
    }

    .login-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 48px 40px;
        width: 100%;
        max-width: 400px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1);
        border: 1px solid #DADCE0;
    }

    .login-icon {
        width: 75px;
        height: 75px;
        margin: 0 auto 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
    }

    .login-title {
        font-size: 24px;
        font-weight: 400;
        color: #202124;
        text-align: center;
        margin-bottom: 8px;
    }

    .login-subtitle {
        font-size: 16px;
        font-weight: 400;
        color: #4D5156;
        text-align: center;
        margin-bottom: 32px;
    }

    .login-form {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .login-input-wrapper {
        position: relative;
    }

    .login-input-wrapper input {
        width: 100%;
        padding: 14px 16px;
        border: 1px solid #DADCE0;
        border-radius: 4px;
        font-size: 16px;
        color: #202124;
        transition: border-color 0.2s;
        box-sizing: border-box;
        background: #FFFFFF;
    }

    .login-input-wrapper input:focus {
        border-color: #1A73E8;
        outline: none;
    }

    .login-input-wrapper input::placeholder {
        color: #9AA0A6;
    }

    .login-btn {
        background: #1A73E8;
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        transition: background 0.2s;
    }

    .login-btn:hover {
        background: #1557B0;
    }

    .login-footer {
        text-align: center;
        margin-top: 24px;
        font-size: 12px;
        color: #5F6368;
    }

    .login-error {
        background: #FDE7E7;
        color: #C5221F;
        padding: 12px 16px;
        border-radius: 4px;
        font-size: 14px;
        text-align: center;
        margin-bottom: 16px;
    }

    /* ========== 侧边栏导航 ========== */
    .sidebar-logo {
        padding: 20px 16px;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }

    .sidebar-logo h2 {
        color: white;
        font-size: 18px;
        margin: 0;
    }

    .sidebar-logo p {
        color: #666666;
        font-size: 11px;
        margin-top: 4px;
    }

    .sidebar-nav {
        padding: 0 8px;
    }

    .nav-item {
        padding: 12px 16px;
        border-radius: 6px;
        color: #444444;
        cursor: pointer;
        transition: all 0.2s;
        margin: 4px 0;
        font-size: 14px;
    }

    .nav-item:hover {
        background: rgba(0,0,0,0.05);
        color: white;
    }

    .nav-item.active {
        background: #2E7DCD;
        color: white;
    }

    .sidebar-user {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 16px;
        background: rgba(0,0,0,0.2);
        border-top: 1px solid rgba(0,0,0,0.05);
    }

    .sidebar-user .user-name {
        color: white;
        font-weight: 600;
        font-size: 14px;
    }

    .sidebar-user .user-role {
        color: #666666;
        font-size: 11px;
    }

    /* ========== 进度条 ========== */
    .progress-bar {
        background: #E8E8E8;
        border-radius: 4px;
        height: 8px;
        overflow: hidden;
    }

    .progress-bar .fill {
        background: linear-gradient(90deg, #2E7DCD, #00A5E0);
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s;
    }

    /* ========== 区块标题 ========== */
    .section-title {
        display: flex;
        align-items: center;
        margin: 24px 0 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid #2E7DCD;
    }

    .section-title .icon {
        font-size: 18px;
        margin-right: 10px;
    }

    .section-title h3 {
        margin: 0;
        color: #1A3A5C;
        font-size: 16px;
        font-weight: 600;
    }

    /* ========== 玻璃态效果 ========== */
    .glass {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border: 1px solid #E8E8E8;
        border-radius: 8px;
    }

    /* ========== 数据表格 ========== */
    .data-table {
        background: #FFFFFF;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E8E8E8;
    }

    .data-table table {
        width: 100%;
        border-collapse: collapse;
    }

    .data-table th {
        background: #F5F7FA;
        color: #1A3A5C;
        font-weight: 600;
        font-size: 13px;
        padding: 12px 16px;
        text-align: left;
        border-bottom: 2px solid #E8E8E8;
    }

    .data-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #F0F0F0;
        font-size: 14px;
        color: #333333;
    }

    .data-table tr:hover {
        background: #F5F7FA;
    }

    .data-table tr:nth-child(even) {
        background: #FAFAFA;
    }

    .data-table tr:nth-child(even):hover {
        background: #F5F7FA;
    }

    /* ========== 自定义滚动条 ========== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #F5F7FA;
    }

    ::-webkit-scrollbar-thumb {
        background: #CCCCCC;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #999999;
    }

    /* ========== 分页 ========== */
    .pagination {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin-top: 20px;
    }

    /* ========== 状态徽章 ========== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }

    .status-badge.online {
        background: #E8F5E9;
        color: #2E7D32;
    }

    .status-badge.offline {
        background: #FFEBEE;
        color: #D32F2F;
    }

    /* ========== 信息提示 ========== */
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============== 辅助函数 ==============

def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def verify_password(pwd, hashed):
    return hashlib.sha256(pwd.encode()).hexdigest() == hashed

def is_pure_at(content):
    if pd.isna(content) or content is None:
        return False
    content = str(content)
    if '@' not in content:
        return False
    if content.count('@') > 1:
        return True
    at_pos = content.find('@')
    before = content[:at_pos]
    if before.strip() != '':
        return False
    after = content[at_pos+1:]
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', after)
    cleaned = cleaned.strip(' \t\n\r.,!?;:，。！？；：""''（）()【】[]{}—...·~')
    return cleaned == ''

def is_pure_emoji(content):
    if pd.isna(content) or content is None:
        return False
    content = str(content).strip()
    if content == '':
        return False
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', content)
    cleaned = cleaned.strip(' \t\n\r.,!?;:，。！？；：""''（）()【】[]{}—...·~')
    return cleaned == '' and len(re.findall(emoji_pattern, content)) > 0

def is_filler_word(content):
    if pd.isna(content) or content is None:
        return False
    content = str(content).strip()
    if content == '':
        return False
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub('', content)
    cleaned = cleaned.strip(' \t\n\r.,!?;:，。！？；：""''（）()【】[]{}—...·~')
    if cleaned == '':
        return False
    filler_words = ['啊', '哈', '嗯', '哦', '呀', '哟', '嘻', '呵', '嘿嘿', '哈哈', '呵呵']
    count = sum(1 for c in cleaned if c in filler_words)
    if len(cleaned) > 0 and count / len(cleaned) > 0.6 and len(cleaned) <= 20:
        return True
    return False

def is_empty_content(content):
    if pd.isna(content) or content is None:
        return True
    content = str(content).strip()
    return content == '' or content == 'nan' or content == 'NaN'

def is_garbled(content):
    if pd.isna(content) or content is None:
        return False
    content = str(content)
    garbled_patterns = [r'[\x00-\x08\x0b\x0c\x0e-\x1f]', r'[▽▃◣◢◇◆]']
    for pattern in garbled_patterns:
        if re.search(pattern, content):
            return True
    weird_chars = sum(1 for c in content if ord(c) > 0xFFFF or ord(c) < 32)
    if len(content) > 5 and weird_chars / len(content) > 0.3:
        return True
    return False

def fuzzy_match(text, keyword):
    if not keyword:
        return True
    text = str(text).lower()
    keyword = keyword.lower()
    if keyword in text:
        return True
    for kw in keyword.split():
        if kw and kw in text:
            return True
    return False

def render_metric_card(label, value, delta=None, icon="📊"):
    """渲染浅色专业风格指标卡片"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">{icon} {label}</div>
        <div class="value">{value}</div>
        {f'<div class="delta">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def render_section_title(title, icon="📋"):
    """渲染区块标题"""
    st.markdown(f"""
    <div class="section-title">
        <span class="icon">{icon}</span>
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)

def render_page_header(title, description="", icon="📊"):
    """渲染页面标题和顶部导航"""
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h1 style="color: #1A3A5C; margin-bottom: 8px;">{icon} {title}</h1>
        {f'<p style="color: #666666; margin: 0;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)

def render_breadcrumb_nav(items):
    """渲染面包屑导航 items: [(name, url_or_page), ...]"""
    nav_html = '<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-size: 13px;">'
    for i, (name, _) in enumerate(items):
        if i > 0:
            nav_html += '<span style="color: #999999;">›</span>'
        nav_html += f'<span style="color: {"#2E7DCD" if i == len(items)-1 else "#666666"};">{name}</span>'
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)

# ============== 数据库初始化 ==============
init_db()

# ============== 登录页 - Google风格 ==============
if 'user_id' not in st.session_state:
    st.markdown('<div class="login-page">', unsafe_allow_html=True)
    st.markdown("""
    <div class="login-card">
        <div class="login-icon">📊</div>
        <div class="login-title">舆情分析系统</div>
        <div class="login-subtitle">Sign in to continue</div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("", placeholder="用户名 / Username", label_visibility="collapsed")
        password = st.text_input("", placeholder="密码 / Password", type="password", label_visibility="collapsed")
        submitted = st.form_submit_button("登 录", type="primary")

    st.markdown("""
    </div>
    """, unsafe_allow_html=True)

    # 错误提示
    if 'login_error' in st.session_state:
        st.markdown(f'<div class="login-error">{st.session_state.login_error}</div>', unsafe_allow_html=True)
        del st.session_state['login_error']

    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        session = get_session()
        user = session.query(User).filter(User.username == username, User.is_active == True).first()
        session.close()
        if user and verify_password(password, user.password_hash):
            st.session_state['user_id'] = user.id
            st.session_state['username'] = user.username
            st.session_state['display_name'] = user.display_name or user.username
            st.session_state['role'] = user.role
            st.rerun()
        else:
            st.session_state['login_error'] = "用户名或密码错误"
            st.rerun()

    st.stop()

# ============== 侧边栏 ==============
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>📊 舆情分析</h2>
        <p>Sentiment Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)

    session = get_session()
    projects = session.query(Project).filter(Project.status == 'active').all()
    session.close()

    project_names = [p.name for p in projects]
    selected = st.selectbox("", ["📁 选择项目"] + ["➕ 创建新项目"] + project_names, label_visibility="collapsed")

    if selected == "➕ 创建新项目":
        new_name = st.text_input("", placeholder="项目名称", label_visibility="collapsed")
        if st.button("创建", use_container_width=True):
            if new_name:
                session = get_session()
                p = Project(name=new_name, created_by=st.session_state['user_id'])
                session.add(p)
                session.commit()
                session.close()
                st.success("创建成功")
                st.rerun()
    elif selected != "📁 选择项目":
        session = get_session()
        current_project = session.query(Project).filter(Project.name == selected).first()
        session.close()
        if current_project:
            st.session_state['current_project_id'] = current_project.id
            st.session_state['current_project_name'] = current_project.name

    # 如果没有项目，自动创建一个默认项目
    if 'current_project_id' not in st.session_state:
        session = get_session()
        default_project = session.query(Project).filter(Project.status == 'active').first()
        if not default_project:
            default_project = Project(
                name="舆情分析项目",
                description="默认项目",
                created_by=st.session_state.get('user_id')
            )
            session.add(default_project)
            session.commit()
        st.session_state['current_project_id'] = default_project.id
        st.session_state['current_project_name'] = default_project.name
        session.close()

    project_id = st.session_state['current_project_id']

    menu_items = [
        ("📥", "数据导入"),
        ("📊", "数据总览"),
        ("🧹", "数据清洗"),
        ("📋", "内容管理"),
        ("📋", "数据子集"),
        ("🏭", "品牌竞品"),
        ("📝", "规则管理"),
        ("🏷️", "标签管理"),
        ("✏️", "手动标注"),
        ("📊", "数据统计"),
        ("📄", "报告生成"),
        ("📋", "模板管理"),
        ("📁", "导出记录"),
    ]

    if st.session_state.get('role') == 'admin':
        menu_items.append(("👤", "用户管理"))

    menu_items.append(("⚙️", "系统设置"))

    selected_menu = st.radio("", [f"{icon} {name}" for icon, name in menu_items], label_visibility="collapsed")

    menu_map = {f"{icon} {name}": name for icon, name in menu_items}
    page = menu_map.get(selected_menu, "数据总览")

    st.divider()
    st.markdown(f"""
    <div class="sidebar-user">
        <div class="user-name">{st.session_state.get('display_name', '用户')}</div>
        <div class="user-role">{st.session_state.get('role', 'user').upper()}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 退出登录", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ============== 数据导入页 ==============
if page == "数据导入":
    render_page_header("📥 数据导入", "上传Excel数据文件，系统将自动进行数据清洗和预处理")

    uploaded_file = st.file_uploader("选择Excel文件", type=['xlsx', 'xls'])

    if uploaded_file:
        file_size = len(uploaded_file.getvalue()) / 1024
        st.markdown(f"""
        <div class="card" style="padding: 20px; margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 14px; color: #333333;">📎 {uploaded_file.name}</div>
                    <div style="font-size: 12px; color: #666666; margin-top: 4px;">{file_size:.1f} KB</div>
                </div>
                <div class="tag tag-info">待导入</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 开始导入", use_container_width=True):
            with st.spinner("正在导入数据..."):
                df = pd.read_excel(uploaded_file)

                # 分批次导入，每批1万条，支持10万级数据
                batch_size = 10000
                total_rows = len(df)

                # 先删除旧数据
                session = get_session()
                session.query(RawData).filter(RawData.project_id == project_id).delete()
                session.commit()
                session.close()

                # 批量插入新数据
                for batch_start in range(0, total_rows, batch_size):
                    batch_end = min(batch_start + batch_size, total_rows)
                    session = get_session()

                    for idx in range(batch_start, batch_end):
                        row = df.iloc[idx]
                        comment_content = str(row.get('评论内容', '')) if pd.notna(row.get('评论内容')) else ''
                        rd = RawData(
                            project_id=project_id,
                            row_index=int(idx) if pd.notna(idx) else idx,
                            video_id=str(row.get('视频ID', '')) if pd.notna(row.get('视频ID')) else '',
                            video_link=str(row.get('视频链接', '')) if pd.notna(row.get('视频链接')) else '',
                            keyword=str(row.get('关键词', '')) if pd.notna(row.get('关键词')) else '',
                            content=str(row.get('内容', '')) if pd.notna(row.get('内容')) else '',
                            topic_tags=str(row.get('话题标签', '')) if pd.notna(row.get('话题标签')) else '',
                            publish_time=str(row.get('发布时间', '')) if pd.notna(row.get('发布时间')) else '',
                            blogger=str(row.get('博主名', '')) if pd.notna(row.get('博主名')) else '',
                            likes=int(row.get('点赞量', 0)) if pd.notna(row.get('点赞量')) else 0,
                            comments_count=int(row.get('评论量', 0)) if pd.notna(row.get('评论量')) else 0,
                            favorites=int(row.get('收藏量', 0)) if pd.notna(row.get('收藏量')) else 0,
                            shares=int(row.get('分享量', 0)) if pd.notna(row.get('分享量')) else 0,
                            comment_id=str(row.get('评论id', '')) if pd.notna(row.get('评论id')) else '',
                            comment_time=str(row.get('评论时间', '')) if pd.notna(row.get('评论时间')) else '',
                            ip_location=str(row.get('ip_location', '')) if pd.notna(row.get('ip_location')) else '',
                            comment_content=comment_content,
                            nickname=str(row.get('昵称', '')) if pd.notna(row.get('昵称')) else '',
                            reply_count=int(row.get('二级评论数', 0)) if pd.notna(row.get('二级评论数')) else 0,
                            reply_likes=int(row.get('评论获赞', 0)) if pd.notna(row.get('评论获赞')) else 0,
                            content_type=str(row.get('评论内容类型', '')) if pd.notna(row.get('评论内容类型')) else '',
                            brand_mentions=str(row.get('品牌提及', '')) if pd.notna(row.get('品牌提及')) else '',
                        )
                        rd.is_pure_at = is_pure_at(comment_content)
                        rd.is_pure_emoji = is_pure_emoji(comment_content)
                        rd.is_filler_word = is_filler_word(comment_content)
                        rd.is_empty = is_empty_content(comment_content)
                        rd.is_garbled = is_garbled(comment_content)
                        rd.is_valid = not any([rd.is_pure_at, rd.is_pure_emoji, rd.is_filler_word, rd.is_empty, rd.is_garbled])
                        session.add(rd)

                    session.commit()
                    session.close()
                    progress = min(batch_end, total_rows)
                    st.info(f"已导入 {progress}/{total_rows} 条...")

                # 更新项目统计
                session = get_session()
                project = session.query(Project).filter(Project.id == project_id).first()
                if project:
                    project.total_rows = total_rows
                    project.source_file = uploaded_file.name
                    valid_count = session.query(RawData).filter(RawData.project_id == project_id, RawData.is_valid == True).count()
                    project.valid_rows = valid_count
                    session.commit()
                session.close()

            st.success(f"✅ 成功导入 {total_rows} 条数据！")
            st.rerun()

    session = get_session()
    count = session.query(RawData).filter(RawData.project_id == project_id).count()
    session.close()

    if count > 0:
        st.markdown("<hr>", unsafe_allow_html=True)
        render_section_title("📊 数据概览", "📊")

        session = get_session()
        records = session.query(RawData).filter(RawData.project_id == project_id).all()
        df_all = pd.DataFrame([r.to_dict() for r in records])
        session.close()

        total = len(df_all)
        valid = df_all['is_valid'].sum()
        s1 = df_all['comment_time'].astype(str).str.startswith('2026-04').sum()

        cols = st.columns(4)
        for col, (label, value, icon) in zip(cols, [
            ("总数据量", f"{total} 条", "📦"),
            ("有效数据", f"{valid} 条", "✅"),
            ("已清洗", f"{total - valid} 条", "🧹"),
            ("第一阶段", f"{s1} 条", "🗓️")
        ]):
            with col:
                render_metric_card(label, value, icon=icon)

# ============== 数据总览页 ==============
elif page == "数据总览":
    render_page_header("📊 数据总览", "查看项目数据总览和统计信息")

    session = get_session()
    records = session.query(RawData).filter(RawData.project_id == project_id).all()
    df = pd.DataFrame([r.to_dict() for r in records])
    session.close()

    if len(df) == 0:
        st.markdown("""
        <div class="card" style="padding: 40px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 16px;">📋</div>
            <div style="font-size: 18px; color: #333333; margin-bottom: 8px;">暂无数据</div>
            <div style="font-size: 14px; color: #666666;">请前往「数据导入」上传数据，或继续「手动标注」已有数据</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        total = len(df)
        valid = df['is_valid'].sum()
        s1_mask = df['comment_time'].astype(str).str.startswith('2026-04')
        s2_mask = df['comment_time'].astype(str).str.startswith('2026-05')
        labeled = df['cognitive_s2'].notna() & (df['cognitive_s2'] != '')

        cols = st.columns(4)
        metrics = [
            ("总数据量", total, "📦"),
            ("有效数据", valid, "✅"),
            ("无效数据", total - valid, "❌"),
            ("已标注", labeled.sum(), "🏷️")
        ]
        for col, (label, value, icon) in zip(cols, metrics):
            with col:
                render_metric_card(label, value, icon=icon)

        cols2 = st.columns(3)
        metrics2 = [
            ("第一阶段(4月)", int(s1_mask.sum()), "🗓️"),
            ("第二阶段(5月)", int(s2_mask.sum()), "🗓️"),
            ("有效率", f"{valid/total*100:.1f}%", "📝")
        ]
        for col, (label, value, icon) in zip(cols2, metrics2):
            with col:
                render_metric_card(label, value, icon=icon)

        st.markdown("<hr>", unsafe_allow_html=True)

        render_section_title("🧹 清洗规则统计", "🧹")

        rule_stats = []
        for code, name in [('pure_at', '纯@无互动'), ('pure_emoji', '纯表情'), ('filler_word', '无意义语气词'), ('empty', '空内容'), ('garbled', '乱码')]:
            col_name = f'is_{code}'
            cnt = df[col_name].sum() if col_name in df.columns else 0
            pct = cnt / total * 100
            rule_stats.append({"规则": name, "数量": int(cnt), "占比": pct})

        rule_df = pd.DataFrame(rule_stats)

        cols = st.columns(5)
        for i, (_, row) in enumerate(rule_df.iterrows()):
            with cols[i]:
                st.markdown(f"""
                <div class="card" style="padding: 16px; text-align: center;">
                    <div style="font-size: 11px; color: #666666; text-transform: uppercase;">{row['规则']}</div>
                    <div style="font-size: 28px; color: #2E7DCD; font-weight: 700; margin: 8px 0;">{int(row['数量'])}</div>
                    <div style="font-size: 12px; color: #999999;">{row['占比']:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        render_section_title("📋 数据列表", "📋")

        col1, col2, col3 = st.columns(3)
        with col1:
            show_filter = st.selectbox("", ["全部", "有效数据", "无效数据"], label_visibility="collapsed")
        with col2:
            stage_filter = st.selectbox("", ["全部", "阶段一(4月)", "阶段二(5月)"], label_visibility="collapsed")
        with col3:
            search = st.text_input("", placeholder="🔍 搜索内容...", label_visibility="collapsed")

        display_df = df.copy()
        if show_filter == "有效数据":
            display_df = display_df[display_df['is_valid'] == True]
        elif show_filter == "无效数据":
            display_df = display_df[display_df['is_valid'] == False]
        if stage_filter == "阶段一(4月)":
            display_df = display_df[s1_mask]
        elif stage_filter == "阶段二(5月)":
            display_df = display_df[s2_mask]
        if search:
            display_df = display_df[display_df['comment_content'].astype(str).str.contains(search, na=False)]

        st.markdown(f"<div style='color: #666666; margin: 16px 0;'>共 <span style='color: #2E7DCD;'>{len(display_df)}</span> 条数据</div>", unsafe_allow_html=True)

        page_size = 50
        total_pages = max(1, (len(display_df) - 1) // page_size + 1)
        page = st.number_input("", min_value=1, max_value=total_pages, value=1, label_visibility="collapsed")
        start_idx = (page - 1) * page_size
        page_df = display_df.iloc[start_idx:start_idx + page_size].copy()

        page_df['comment_content'] = page_df['comment_content'].astype(str).str[:60] + "..."
        page_df['is_valid'] = page_df['is_valid'].apply(lambda x: "✅" if x else "❌")

        st.dataframe(page_df[['id', 'comment_content', 'comment_time', 'is_valid', 'cognitive_s1', 'emotional_s1', 'action_s1']], hide_index=True, use_container_width=True, height=400)

# ============== 数据清洗页 ==============
elif page == "数据清洗":
    render_page_header("🧹 数据清洗", "配置清洗规则，实时预览效果")
    st.markdown("<p style='color: #666666;'>勾选清洗规则，实时预览效果</p>", unsafe_allow_html=True)

    session = get_session()
    records = session.query(RawData).filter(RawData.project_id == project_id).all()
    df = pd.DataFrame([r.to_dict() for r in records])
    rules = session.query(CleanRule).order_by(CleanRule.priority.desc()).all()
    session.close()

    if len(df) == 0:
        st.warning("⚠️ 请先导入数据")
        st.stop()

    render_section_title("🧹 清洗规则配置", "🧹")

    rule_enabled = {}
    cols = st.columns(3)
    for i, rule in enumerate(rules):
        with cols[i % 3]:
            enabled = st.checkbox(f"☑️ {rule.name}", value=rule.enabled, key=f"rule_{rule.code}")
            rule_enabled[rule.code] = enabled

    def calc_valid(row):
        if rule_enabled.get('pure_at', True) and row.get('is_pure_at'):
            return False
        if rule_enabled.get('pure_emoji', True) and row.get('is_pure_emoji'):
            return False
        if rule_enabled.get('filler_word', True) and row.get('is_filler_word'):
            return False
        if rule_enabled.get('empty', True) and row.get('is_empty'):
            return False
        if rule_enabled.get('garbled', True) and row.get('is_garbled'):
            return False
        return True

    df['_temp_valid'] = df.apply(calc_valid, axis=1)
    new_valid = df['_temp_valid'].sum()
    new_invalid = len(df) - new_valid

    st.markdown("<hr>", unsafe_allow_html=True)
    render_section_title("📊 清洗效果预览", "📊")

    cols = st.columns(4)
    metrics = [
        ("总数据量", len(df), "📦"),
        ("有效（启用后）", int(new_valid), "✅"),
        ("无效（剔除）", int(new_invalid), "❌"),
        ("有效率", f"{new_valid/len(df)*100:.1f}%", "📝")
    ]
    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            render_metric_card(label, value, icon=icon)

    st.markdown("<hr>", unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        if st.button("💾 保存规则配置", use_container_width=True):
            session = get_session()
            for code, enabled in rule_enabled.items():
                rule = session.query(CleanRule).filter(CleanRule.code == code).first()
                if rule:
                    rule.enabled = enabled
            session.commit()
            session.close()
            st.success("规则配置已保存！")
    with cols[1]:
        if st.button("🔄 重新检测", use_container_width=True):
            with st.spinner("重新检测中..."):
                session = get_session()
                records = session.query(RawData).filter(RawData.project_id == project_id).all()
                for rd in records:
                    rd.is_pure_at = is_pure_at(rd.comment_content)
                    rd.is_pure_emoji = is_pure_emoji(rd.comment_content)
                    rd.is_filler_word = is_filler_word(rd.comment_content)
                    rd.is_empty = is_empty_content(rd.comment_content)
                    rd.is_garbled = is_garbled(rd.comment_content)
                    rd.is_valid = not any([rd.is_pure_at, rd.is_pure_emoji, rd.is_filler_word, rd.is_empty, rd.is_garbled])
                session.commit()
                session.close()
            st.success("重新检测完成！")
            st.rerun()

# ============== 手动标注页 ==============
elif page == "手动标注":
    render_page_header("✏️ 手动标注", "在大表格中直接编辑标注，类似Excel操作体验")

    session = get_session()
    records = session.query(RawData).filter(RawData.project_id == project_id).all()
    df = pd.DataFrame([r.to_dict() for r in records])
    session.close()

    if len(df) == 0:
        st.warning("⚠️ 请先导入数据")
        st.stop()

    df_valid = df[df['is_valid'] == True].copy()

    # 筛选条件
    col1, col2, col3 = st.columns(3)
    with col1:
        stage_filter = st.selectbox("阶段", ["全部", "阶段一(4月)", "阶段二(5月)"], key="stage_filter")
    with col2:
        label_filter = st.selectbox("标注状态", ["全部", "未标注", "已标注"], key="label_filter")
    with col3:
        content_filter = st.selectbox("内容类型", ["全部", "普通内容", "长内容(>100字)", "提及竞品", "视频内容"], key="content_filter")

    filtered = df_valid.copy()
    if stage_filter == "阶段一(4月)":
        filtered = filtered[filtered['comment_time'].astype(str).str.startswith('2026-04')]
    elif stage_filter == "阶段二(5月)":
        filtered = filtered[filtered['comment_time'].astype(str).str.startswith('2026-05')]
    if label_filter == "未标注":
        filtered = filtered[filtered['cognitive_s2'].isna() | (filtered['cognitive_s2'] == '')]
    elif label_filter == "已标注":
        filtered = filtered[filtered['cognitive_s2'].notna() & (filtered['cognitive_s2'] != '')]
    if content_filter != "全部":
        filtered = filtered[filtered['content_type'] == content_filter]

    st.markdown(f"<div style='color: #666666; margin: 16px 0;'>共 <span style='color: #2E7DCD; font-weight: 600;'>{len(filtered)}</span> 条数据待标注</div>", unsafe_allow_html=True)

    # 准备编辑表格数据
    edit_df = filtered[['id', 'comment_content', 'comment_time', 'ip_location', 'content_type',
                        'cognitive_s1', 'cognitive_s2', 'emotional_s1', 'emotional_s2',
                        'action_s1', 'action_s2', 'brand_detected']].copy()

    edit_df.columns = ['ID', '评论内容', '评论时间', 'IP属地', '内容类型',
                       '认知-S1', '认知-S2', '情绪-S1', '情绪-S2',
                       '行动-S1', '行动-S2', '品牌']

    # 使用data_editor实现类Excel编辑
    editable = st.data_editor(
        edit_df,
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small", disabled=True),
            "评论内容": st.column_config.TextColumn("评论内容", width="large"),
            "评论时间": st.column_config.TextColumn("评论时间", width="medium", disabled=True),
            "IP属地": st.column_config.TextColumn("IP属地", width="small", disabled=True),
            "内容类型": st.column_config.TextColumn("内容类型", width="medium", disabled=True),
            "认知-S1": st.column_config.SelectboxColumn("认知-S1", width="medium",
                options=["", "无明确认知", "信息混淆", "精准认知", "泛化抵触"]),
            "认知-S2": st.column_config.SelectboxColumn("认知-S2", width="medium",
                options=["", "无明确认知", "信息混淆", "精准认知", "泛化抵触"]),
            "情绪-S1": st.column_config.SelectboxColumn("情绪-S1", width="medium",
                options=["", "正面", "中性", "恐慌焦虑", "庆幸旁观", "愤怒背叛"]),
            "情绪-S2": st.column_config.SelectboxColumn("情绪-S2", width="medium",
                options=["", "正面", "中性", "恐慌焦虑", "庆幸旁观", "愤怒背叛"]),
            "行动-S1": st.column_config.SelectboxColumn("行动-S1", width="medium",
                options=["", "暂无行动", "寻求帮助", "转奶流失", "维权诉求"]),
            "行动-S2": st.column_config.SelectboxColumn("行动-S2", width="medium",
                options=["", "暂无行动", "寻求帮助", "转奶流失", "维权诉求"]),
            "品牌": st.column_config.TextColumn("品牌", width="medium"),
        }
    )

    # 保存按钮
    if st.button("💾 批量保存所有修改", type="primary", use_container_width=True):
        save_count = 0
        session = get_session()
        for idx, row in editable.iterrows():
            rd = session.query(RawData).filter(RawData.id == row['ID']).first()
            if rd:
                rd.cognitive_s1 = row['认知-S1'] if pd.notna(row['认知-S1']) else ''
                rd.cognitive_s2 = row['认知-S2'] if pd.notna(row['认知-S2']) else ''
                rd.emotional_s1 = row['情绪-S1'] if pd.notna(row['情绪-S1']) else ''
                rd.emotional_s2 = row['情绪-S2'] if pd.notna(row['情绪-S2']) else ''
                rd.action_s1 = row['行动-S1'] if pd.notna(row['行动-S1']) else ''
                rd.action_s2 = row['行动-S2'] if pd.notna(row['行动-S2']) else ''
                rd.brand_detected = row['品牌'] if pd.notna(row['品牌']) else ''
                rd.manual_override = True
                rd.labeled_by = st.session_state.get('user_id')
                rd.labeled_at = datetime.now()
                save_count += 1
        session.commit()
        session.close()
        st.success(f"✅ 已保存 {save_count} 条标注记录！")
        st.rerun()

    # 导出按钮 - 导出与参考文件相同格式的Excel
    if st.button("📥 导出Excel（参考格式）", use_container_width=True):
        # 读取原始数据并合并标注结果
        session = get_session()
        all_records = session.query(RawData).filter(RawData.project_id == project_id).all()
        session.close()

        # 构建导出数据
        export_data = []
        for rd in all_records:
            export_data.append({
                '视频ID': rd.video_id or '',
                '视频链接': rd.video_link or '',
                '关键词': rd.keyword or '',
                '内容': rd.content or '',
                '话题标签': rd.topic_tags or '',
                '发布时间': rd.publish_time or '',
                '博主名': rd.blogger or '',
                '收藏量': rd.favorites or 0,
                '评论量': rd.comments_count or 0,
                '点赞量': rd.likes or 0,
                '分享量': rd.shares or 0,
                '评论id': rd.comment_id or '',
                '评论时间': rd.comment_time or '',
                'ip_location': rd.ip_location or '',
                '评论内容': rd.comment_content or '',
                '昵称': rd.nickname or '',
                '二级评论数': rd.reply_count or 0,
                '评论获赞': rd.reply_likes or 0,
                '评论内容类型': rd.content_type or '',
                '认知层阶段一': rd.cognitive_s1 or '',
                '认知层阶段二': rd.cognitive_s2 or '',
                '情绪层阶段一': rd.emotional_s1 or '',
                '情绪层阶段二': rd.emotional_s2 or '',
                '行动层阶段一': rd.action_s1 or '',
                '行动层阶段二': rd.action_s2 or '',
                '品牌提及': rd.brand_detected or ''
            })

        export_df = pd.DataFrame(export_data)

        # 保存为Excel
        export_path = os.path.join(os.path.dirname(__file__), 'exports', f'标注导出_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        export_df.to_excel(export_path, index=False, engine='openpyxl')

        st.success(f"✅ 已导出 {len(export_df)} 条数据到 Excel！")
        with open(export_path, 'rb') as f:
            st.download_button(
                "📥 下载导出的Excel文件",
                data=f.read(),
                file_name=os.path.basename(export_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # CSV导出按钮
    st.download_button(
        "📥 导出CSV",
        data=editable.to_csv(index=False).encode('utf-8-sig'),
        file_name="舆情标注数据.csv",
        mime="text/csv",
        use_container_width=True
    )

# ============== 品牌竞品页 ==============
elif page == "品牌竞品":
    render_page_header("🏭 品牌与竞品管理", "管理品牌和竞品信息")

    tab1, tab2 = st.tabs(["🏢 品牌管理", "📦 竞品产品"])

    with tab1:
        session = get_session()
        brands = session.query(Brand).all()
        session.close()

        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"""
            <div class="card" style="padding: 24px; text-align: center;">
                <div style="font-size: 12px; color: #666666; text-transform: uppercase;">品牌总数</div>
                <div style="font-size: 48px; color: #2E7DCD; font-weight: 700; margin-top: 8px;">{len(brands)}</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            active = sum(1 for b in brands if b.is_active)
            st.markdown(f"""
            <div class="card" style="padding: 24px; text-align: center;">
                <div style="font-size: 12px; color: #666666; text-transform: uppercase;">活跃品牌</div>
                <div style="font-size: 48px; color: #4CAF50; font-weight: 700; margin-top: 8px;">{active}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        with st.expander("➕ 添加新品牌"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("品牌名称")
                new_alias = st.text_input("别名（用|分隔）")
            with col2:
                new_category = st.selectbox("类别", ["奶粉", "辅食", "营养品", "纸尿裤", "其他"])
                new_priority = st.slider("优先级", 0, 10, 5)

            if st.button("添加品牌"):
                if new_name:
                    session = get_session()
                    brand = Brand(name=new_name, alias=new_alias, category=new_category, priority=new_priority)
                    session.add(brand)
                    session.commit()
                    session.close()
                    st.success(f"已添加品牌「{new_name}」")
                    st.rerun()

        brand_data = []
        for b in brands:
            brand_data.append({
                "ID": b.id,
                "品牌名": b.name,
                "别名": b.alias,
                "类别": b.category,
                "优先级": b.priority,
                "状态": "✅ 活跃" if b.is_active else "❌ 禁用"
            })
        st.dataframe(pd.DataFrame(brand_data), hide_index=True, use_container_width=True)

    with tab2:
        session = get_session()
        brands = session.query(Brand).filter(Brand.is_active == True).all()
        competitors = session.query(CompetitorProduct).all()
        session.close()

        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"""
            <div class="card" style="padding: 24px; text-align: center;">
                <div style="font-size: 12px; color: #666666; text-transform: uppercase;">竞品总数</div>
                <div style="font-size: 48px; color: #2E7DCD; font-weight: 700; margin-top: 8px;">{len(competitors)}</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            active = sum(1 for c in competitors if c.is_active)
            st.markdown(f"""
            <div class="card" style="padding: 24px; text-align: center;">
                <div style="font-size: 12px; color: #666666; text-transform: uppercase;">活跃竞品</div>
                <div style="font-size: 48px; color: #4CAF50; font-weight: 700; margin-top: 8px;">{active}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        with st.expander("➕ 添加竞品"):
            col1, col2 = st.columns(2)
            with col1:
                brand_choice = st.selectbox("所属品牌", [b.name for b in brands])
                prod_name = st.text_input("产品名称")
            with col2:
                prod_line = st.text_input("产品系列")
                prod_keywords = st.text_area("识别关键词（逗号分隔）")

            if st.button("添加竞品"):
                if prod_name and brand_choice:
                    session = get_session()
                    brand_obj = session.query(Brand).filter(Brand.name == brand_choice).first()
                    if brand_obj:
                        comp = CompetitorProduct(
                            brand_id=brand_obj.id,
                            name=prod_name,
                            product_line=prod_line,
                            keywords=[k.strip() for k in prod_keywords.split(',') if k.strip()]
                        )
                        session.add(comp)
                        session.commit()
                    session.close()
                    st.success(f"已添加竞品「{prod_name}」")
                    st.rerun()

        comp_data = []
        for c in competitors:
            brand_name = session.query(Brand).filter(Brand.id == c.brand_id).first().name if session.query(Brand).filter(Brand.id == c.brand_id).first() else "未知"
            comp_data.append({
                "ID": c.id,
                "产品名": c.name,
                "品牌": brand_name,
                "系列": c.product_line,
                "关键词": ", ".join(c.keywords or []),
                "状态": "✅ 活跃" if c.is_active else "❌ 禁用"
            })
        st.dataframe(pd.DataFrame(comp_data), hide_index=True, use_container_width=True)

# ============== 其他页面（简化版） ==============
elif page == "标签管理":
    render_page_header("🏷️ 标签管理", "查看和管理标签统计")

    session = get_session()
    records = session.query(RawData).filter(RawData.project_id == project_id).all()
    df = pd.DataFrame([r.to_dict() for r in records])
    project = session.query(Project).filter(Project.id == project_id).first()
    session.close()

    if len(df) == 0:
        st.warning("⚠️ 请先导入数据")
        st.stop()

    df_valid = df[df['is_valid'] == True]
    s1_d = project.s1_denominator or 586
    s2_d = project.s2_denominator or 4093
    s1_mask = df_valid['comment_time'].astype(str).str.startswith('2026-04')
    s2_mask = df_valid['comment_time'].astype(str).str.startswith('2026-05')

    tab_cog, tab_emo, tab_act, tab_brand = st.tabs(["🧠 认知层", "😀 情绪层", "🎯 行动层", "🏢 品牌"])

    labels_map = {
        "认知层": ["无明确认知", "信息混淆", "精准认知", "泛化抵触"],
        "情绪层": ["中性", "正面", "恐慌焦虑", "庆幸旁观", "愤怒背叛"],
        "行动层": ["暂无行动", "寻求帮助", "转奶流失", "维权诉求"],
        "品牌": ["品牌提及", "竞品提及", "无品牌"]
    }

    for tab_name, labels, tab in [("认知层", labels_map["认知层"], tab_cog), ("情绪层", labels_map["情绪层"], tab_emo), ("行动层", labels_map["行动层"], tab_act), ("品牌", labels_map["品牌"], tab_brand)]:
        with tab:
            cols = st.columns(2)
            for i, (stage_name, stage_key, stage_mask, denom) in enumerate([("阶段一(4月)", "S1", s1_mask, s1_d), ("阶段二(5月)", "S2", s2_mask, s2_d)]):
                stage_df = df_valid[stage_mask]
                col_map = {"认知层": ('cognitive_s1', 'cognitive_s2'), "情绪层": ('emotional_s1', 'emotional_s2'), "行动层": ('action_s1', 'action_s2'), "品牌": ('brand_detected', 'brand_detected')}
                col = col_map.get(tab_name, ('cognitive_s1', 'cognitive_s2'))[0 if stage_key == 'S1' else 1]
                stats = stage_df[col].value_counts().to_dict() if col in stage_df.columns else {}

                with cols[i]:
                    st.markdown(f"""
                    <div class="card" style="padding: 20px;">
                        <div style="font-size: 14px; color: #2E7DCD; margin-bottom: 16px;">{stage_name} (总计: {denom} 条)</div>
                    """, unsafe_allow_html=True)
                    for label in labels:
                        count = stats.get(label, 0)
                        pct = count / denom * 100 if denom > 0 else 0
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(0,212,255,0.1);">
                            <span style="color: #444444;">{label}</span>
                            <span style="color: #2E7DCD;">{count} <span style="color: #999999;">({pct:.1f}%)</span></span>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

elif page == "系统设置":
    render_page_header("⚙️ 系统设置", "系统配置和个人信息")

    st.markdown("""
    <div class="card" style="padding: 24px; margin: 16px 0;">
        <h3 style="color: #2E7DCD; margin-bottom: 16px;">👤 个人信息</h3>
        <p style="color: #666666;">用户名: {}</p>
        <p style="color: #666666;">角色: {}</p>
    </div>
    """.format(st.session_state.get('username', ''), st.session_state.get('role', '').upper()), unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="padding: 24px; margin: 16px 0;">
        <h3 style="color: #2E7DCD; margin-bottom: 16px;">🔧 系统信息</h3>
        <p style="color: #666666;">系统版本: 3.0.0</p>
        <p style="color: #666666;">数据库版本: SQLite</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "用户管理" and st.session_state.get('role') == 'admin':
    render_page_header("👤 用户管理", "管理系统用户")

    session = get_session()
    users = session.query(User).all()
    session.close()

    user_data = []
    for u in users:
        user_data.append({
            "ID": u.id,
            "用户名": u.username,
            "显示名": u.display_name or "-",
            "角色": u.role,
            "状态": "✅ 活跃" if u.is_active else "❌ 禁用",
            "最后登录": u.last_login or "从未登录"
        })
    st.dataframe(pd.DataFrame(user_data), hide_index=True, use_container_width=True)

    with st.expander("➕ 添加用户"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("用户名")
            new_password = st.text_input("密码", type="password")
        with col2:
            new_display = st.text_input("显示名称")
            new_role = st.selectbox("角色", ["user", "admin", "viewer"])

        if st.button("添加用户"):
            if new_username and new_password:
                session = get_session()
                user = User(username=new_username, password_hash=hash_password(new_password), display_name=new_display, role=new_role)
                session.add(user)
                session.commit()
                session.close()
                st.success("用户添加成功！")
                st.rerun()

# ============== 内容管理页 ==============
elif page == "内容管理":
    render_page_header("📋 内容管理", "多维度筛选内容，创建数据子集")
    st.markdown("<p style='color: #666666;'>多维度筛选内容，创建数据子集</p>", unsafe_allow_html=True)

    session = get_session()
    records = session.query(RawData).filter(RawData.project_id == project_id).all()
    df = pd.DataFrame([r.to_dict() for r in records])
    session.close()

    if len(df) == 0:
        st.warning("⚠️ 请先导入数据")
        st.stop()

    # 初始化筛选状态
    if 'content_filter_type' not in st.session_state:
        st.session_state['content_filter_type'] = 'all'

    render_section_title("🔍 筛选条件", "🔍")

    col1, col2, col3 = st.columns(3)
    with col1:
        stage = st.selectbox("阶段", ["全部", "阶段一(4月)", "阶段二(5月)"], key="content_stage")
    with col2:
        content_type = st.selectbox("内容类型", ["全部", "普通内容", "长内容(>100字)", "提及竞品", "视频内容"], key="content_type")
    with col3:
        label_status = st.selectbox("标注状态", ["全部", "已标注", "未标注"], key="content_label")

    col1, col2 = st.columns(2)
    with col1:
        keyword = st.text_input("🔍 关键词搜索", placeholder="输入关键词...", key="content_keyword")
    with col2:
        ip_loc = st.text_input("📍 IP地区", placeholder="如：北京、上海...", key="content_ip")

    # 应用筛选条件
    filtered = df.copy()
    if stage == "阶段一(4月)":
        filtered = filtered[filtered['comment_time'].astype(str).str.startswith('2026-04')]
    elif stage == "阶段二(5月)":
        filtered = filtered[filtered['comment_time'].astype(str).str.startswith('2026-05')]
    if content_type != "全部":
        filtered = filtered[filtered['content_type'] == content_type]
    if label_status == "已标注":
        filtered = filtered[filtered['cognitive_s2'].notna() & (filtered['cognitive_s2'] != '')]
    elif label_status == "未标注":
        filtered = filtered[(filtered['cognitive_s2'].isna()) | (filtered['cognitive_s2'] == '')]
    if keyword:
        filtered = filtered[filtered['comment_content'].astype(str).str.contains(keyword, na=False)]
    if ip_loc:
        filtered = filtered[filtered['ip_location'].astype(str).str.contains(ip_loc, na=False)]

    st.markdown("<hr>", unsafe_allow_html=True)

    # 可点击的筛选结果标签
    total_count = len(filtered)
    valid_count = int(filtered['is_valid'].sum())
    invalid_count = total_count - valid_count
    labeled_count = int((filtered['cognitive_s2'].notna() & (filtered['cognitive_s2'] != '')).sum())

    st.markdown("<div style='margin-bottom: 12px;'><span style='color: #666666; font-size: 14px;'>筛选结果：</span></div>", unsafe_allow_html=True)

    filter_cols = st.columns(4)
    with filter_cols[0]:
        if st.button(f"📦 总数据 ({total_count})", use_container_width=True):
            st.session_state['content_filter_type'] = 'all'
    with filter_cols[1]:
        if st.button(f"✅ 有效数据 ({valid_count})", use_container_width=True):
            filtered = filtered[filtered['is_valid'] == True]
            st.session_state['content_filter_type'] = 'valid'
    with filter_cols[2]:
        if st.button(f"❌ 无效数据 ({invalid_count})", use_container_width=True):
            filtered = filtered[filtered['is_valid'] == False]
            st.session_state['content_filter_type'] = 'invalid'
    with filter_cols[3]:
        if st.button(f"🏷️ 已标注 ({labeled_count})", use_container_width=True):
            filtered = filtered[filtered['cognitive_s2'].notna() & (filtered['cognitive_s2'] != '')]
            st.session_state['content_filter_type'] = 'labeled'

    st.markdown(f"<div style='color: #666666; margin: 16px 0;'>当前显示 <span style='color: #2E7DCD; font-weight: 600;'>{len(filtered)}</span> 条数据</div>", unsafe_allow_html=True)

    # 可编辑的数据表格 - 支持双击编辑
    edit_df = filtered[['id', 'comment_content', 'comment_time', 'ip_location', 'content_type',
                        'cognitive_s1', 'cognitive_s2', 'emotional_s1', 'emotional_s2',
                        'action_s1', 'action_s2']].copy()

    edit_df.columns = ['ID', '评论内容', '评论时间', 'IP属地', '内容类型',
                       '认知-S1', '认知-S2', '情绪-S1', '情绪-S2', '行动-S1', '行动-S2']

    edited_df = st.data_editor(
        edit_df,
        use_container_width=True,
        height=700,  # 约20行数据
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small", disabled=True),
            "评论内容": st.column_config.TextColumn("评论内容", width="large"),
            "评论时间": st.column_config.TextColumn("评论时间", width="medium", disabled=True),
            "IP属地": st.column_config.TextColumn("IP属地", width="small", disabled=True),
            "内容类型": st.column_config.TextColumn("内容类型", width="medium", disabled=True),
            "认知-S1": st.column_config.SelectboxColumn("认知-S1", width="medium",
                options=["", "无明确认知", "信息混淆", "精准认知", "泛化抵触"]),
            "认知-S2": st.column_config.SelectboxColumn("认知-S2", width="medium",
                options=["", "无明确认知", "信息混淆", "精准认知", "泛化抵触"]),
            "情绪-S1": st.column_config.SelectboxColumn("情绪-S1", width="medium",
                options=["", "正面", "中性", "恐慌焦虑", "庆幸旁观", "愤怒背叛"]),
            "情绪-S2": st.column_config.SelectboxColumn("情绪-S2", width="medium",
                options=["", "正面", "中性", "恐慌焦虑", "庆幸旁观", "愤怒背叛"]),
            "行动-S1": st.column_config.SelectboxColumn("行动-S1", width="medium",
                options=["", "暂无行动", "寻求帮助", "转奶流失", "维权诉求"]),
            "行动-S2": st.column_config.SelectboxColumn("行动-S2", width="medium",
                options=["", "暂无行动", "寻求帮助", "转奶流失", "维权诉求"]),
        }
    )

    # 保存按钮
    if st.button("💾 批量保存所有修改", type="primary", use_container_width=True):
        save_count = 0
        session = get_session()
        for idx, row in edited_df.iterrows():
            rd = session.query(RawData).filter(RawData.id == row['ID']).first()
            if rd:
                rd.cognitive_s1 = row['认知-S1'] if pd.notna(row['认知-S1']) else ''
                rd.cognitive_s2 = row['认知-S2'] if pd.notna(row['认知-S2']) else ''
                rd.emotional_s1 = row['情绪-S1'] if pd.notna(row['情绪-S1']) else ''
                rd.emotional_s2 = row['情绪-S2'] if pd.notna(row['情绪-S2']) else ''
                rd.action_s1 = row['行动-S1'] if pd.notna(row['行动-S1']) else ''
                rd.action_s2 = row['行动-S2'] if pd.notna(row['行动-S2']) else ''
                rd.manual_override = True
                rd.labeled_by = st.session_state.get('user_id')
                rd.labeled_at = datetime.now()
                save_count += 1
        session.commit()
        session.close()
        st.success(f"✅ 已保存 {save_count} 条修改记录！")
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    render_section_title("📋 创建数据子集", "📋")

    col1, col2 = st.columns(2)
    with col1:
        subset_name = st.text_input("子集名称", placeholder="输入子集名称...")
    with col2:
        subset_desc = st.text_input("子集描述", placeholder="输入子集描述...")

    if st.button("📋 创建子集", use_container_width=True):
        if subset_name:
            session = get_session()
            subset = DataSubset(
                project_id=project_id,
                name=subset_name,
                description=subset_desc,
                data_ids=json.dumps(filtered['id'].tolist()),
                record_count=len(filtered)
            )
            session.add(subset)
            session.commit()
            session.close()
            st.success(f"✅ 子集「{subset_name}」创建成功！共 {len(filtered)} 条数据")
        else:
            st.warning("请输入子集名称")

# ============== 数据子集页 ==============
elif page == "数据子集":
    render_page_header("📋 数据子集管理", "管理已创建的数据子集")
    st.markdown("<p style='color: #666666;'>管理已创建的数据子集</p>", unsafe_allow_html=True)

    session = get_session()
    subsets = session.query(DataSubset).filter(DataSubset.project_id == project_id).all()
    session.close()

    if len(subsets) == 0:
        st.info("📭 暂无数据子集，请从「内容管理」创建")
    else:
        cols = st.columns(3)
        for i, sub in enumerate(subsets):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card" style="padding: 20px;">
                    <div style="font-size: 16px; color: #2E7DCD; font-weight: 600; margin-bottom: 8px;">{sub.name}</div>
                    <div style="font-size: 12px; color: #666666; margin-bottom: 12px;">{sub.description or '无描述'}</div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #999999; font-size: 11px;">记录数</span>
                        <span style="color: #4CAF50; font-size: 14px; font-weight: 600;">{sub.record_count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============== 规则管理页 ==============
elif page == "规则管理":
    render_page_header("📝 规则管理", "配置标签规则和清洗规则")

    tab1, tab2, tab3, tab4 = st.tabs(["🏷️ 标签规则", "🧹 清洗规则", "📊 优先级配置", "ℹ️ 使用说明"])

    with tab1:
        session = get_session()
        rules = session.query(LabelRule).all()
        session.close()

        # 层和阶段选择
        col_layer, col_stage = st.columns(2)
        with col_layer:
            layer = st.selectbox("选择层级", ["全部", "认知层", "情绪层", "行动层"])
        with col_stage:
            stage = st.selectbox("选择阶段", ["全部", "阶段一(S1)", "阶段二(S2)"])

        # 过滤规则
        stage_map = {"阶段一(S1)": "s1", "阶段二(S2)": "s2", "全部": None}
        stage_val = stage_map.get(stage)
        filtered_rules = rules
        if layer != "全部":
            filtered_rules = [r for r in filtered_rules if r.layer == layer.lower()]
        if stage_val:
            filtered_rules = [r for r in filtered_rules if r.stage == stage_val]

        st.markdown("""
        <div class="card" style="padding: 16px; margin: 12px 0;">
            <h3 style="color: #2E7DCD; margin-bottom: 12px;">标签规则说明</h3>
            <p style="color: #666666; line-height: 1.6; font-size: 13px;">
            <b style="color: #4CAF50;">认知层</b>：无明确认知 → 信息混淆 → 精准认知 → 泛化抵触（优先级依次升高）<br>
            <b style="color: #4CAF50;">情绪层</b>：中性 → 正面 → 恐慌焦虑 → 庆幸旁观 → 愤怒背叛<br>
            <b style="color: #4CAF50;">行动层</b>：暂无行动 → 寻求帮助 → 转奶流失 → 维权诉求
            </p>
        </div>
        """, unsafe_allow_html=True)

        if len(filtered_rules) == 0:
            st.info("暂无标签规则")
        else:
            # 按层级+阶段分组展示
            layer_stage_groups = {}
            for r in filtered_rules:
                key = f"{r.layer}_{r.stage}"
                if key not in layer_stage_groups:
                    layer_stage_groups[key] = []
                layer_stage_groups[key].append(r)

            for key, group_rules in layer_stage_groups.items():
                layer_name = {"cognitive": "认知层", "emotional": "情绪层", "action": "行动层"}.get(group_rules[0].layer, group_rules[0].layer)
                stage_name = "S1" if group_rules[0].stage == "s1" else "S2"
                with st.expander(f"📋 {layer_name} - {stage_name} ({len(group_rules)}条规则)", expanded=True):
                    # 显示每条规则的完整关键词
                    for r in sorted(group_rules, key=lambda x: x.priority, reverse=True):
                        keywords_str = ", ".join(r.keywords) if r.keywords else "(无关键词)"
                        st.markdown(f"""
                        <div style="background: #F5F7FA; border-radius: 6px; padding: 12px; margin: 8px 0; border-left: 3px solid #2E7DCD;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 600; color: #1A3A5C;">{r.label}</span>
                                <span style="font-size: 12px; color: #666;">优先级: {r.priority} | {'✅ 启用' if r.enabled else '❌ 禁用'}</span>
                            </div>
                            <div style="font-size: 12px; color: #666; margin-top: 6px;">关键词: {keywords_str}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # 添加新规则
        st.markdown("---")
        st.markdown("### ➕ 添加新规则")
        with st.form("add_rule_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_layer = st.selectbox("层级", ["cognitive", "emotional", "action"], format_func=lambda x: {"cognitive": "认知层", "emotional": "情绪层", "action": "行动层"}.get(x, x))
            with col2:
                new_stage = st.selectbox("阶段", ["s1", "s2"], format_func=lambda x: "S1" if x == "s1" else "S2")
            with col3:
                new_priority = st.number_input("优先级", min_value=1, max_value=10, value=5)

            col_label, col_keywords = st.columns([1, 3])
            with col_label:
                new_label = st.text_input("标签名称")
            with col_keywords:
                new_keywords_str = st.text_input("关键词（逗号分隔）")

            col_submit, col_clear = st.columns([1, 4])
            with col_submit:
                submitted = st.form_submit_button("添加规则")
            if submitted:
                if new_label:
                    keywords_list = [k.strip() for k in new_keywords_str.split(",") if k.strip()] if new_keywords_str else []
                    session = get_session()
                    lr = LabelRule(
                        layer=new_layer,
                        stage=new_stage,
                        label=new_label,
                        keywords=keywords_list,
                        priority=new_priority,
                        enabled=True
                    )
                    session.add(lr)
                    session.commit()
                    session.close()
                    st.success(f"规则「{new_label}」添加成功！")
                    st.rerun()

        # 批量导入规则
        st.markdown("---")
        st.markdown("### 📥 批量导入规则（JSON格式）")
        with st.expander("批量导入"):
            json_input = st.text_area("粘贴JSON格式规则", height=150, placeholder='[{"layer": "emotional", "stage": "s1", "label": "恐慌焦虑", "keywords": ["吐奶", "拉肚子"], "priority": 3}]')
            if st.button("导入"):
                if json_input:
                    try:
                        rules_data = json.loads(json_input)
                        session = get_session()
                        for rule in rules_data:
                            lr = LabelRule(
                                layer=rule.get("layer"),
                                stage=rule.get("stage"),
                                label=rule.get("label"),
                                keywords=rule.get("keywords", []),
                                priority=rule.get("priority", 1),
                                enabled=rule.get("enabled", True)
                            )
                            session.add(lr)
                        session.commit()
                        session.close()
                        st.success(f"成功导入 {len(rules_data)} 条规则！")
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("JSON格式错误，请检查格式")

    with tab2:
        session = get_session()
        clean_rules = session.query(CleanRule).order_by(CleanRule.priority.desc()).all()
        session.close()

        render_section_title("🧹 清洗规则配置", "🧹")

        rules_data = []
        for r in clean_rules:
            rules_data.append({
                "ID": r.id,
                "规则名称": r.name,
                "规则代码": r.code,
                "描述": r.description or "-",
                "优先级": r.priority,
                "状态": "✅ 启用" if r.enabled else "❌ 禁用"
            })
        st.dataframe(pd.DataFrame(rules_data), hide_index=True, use_container_width=True)

        with st.expander("➕ 添加清洗规则"):
            col1, col2 = st.columns(2)
            with col1:
                cr_name = st.text_input("规则名称")
                cr_code = st.text_input("规则代码")
            with col2:
                cr_desc = st.text_input("规则描述")
                cr_priority = st.number_input("优先级", min_value=0, max_value=100, value=5)

            if st.button("添加规则"):
                if cr_name and cr_code:
                    session = get_session()
                    cr = CleanRule(name=cr_name, code=cr_code, description=cr_desc, priority=cr_priority)
                    session.add(cr)
                    session.commit()
                    session.close()
                    st.success("规则添加成功！")
                    st.rerun()

    with tab3:
        st.markdown("""
        <div class="card" style="padding: 24px; margin: 16px 0;">
            <h3 style="color: #2E7DCD; margin-bottom: 20px;">📊 标签匹配优先级</h3>

            <h4 style="color: #4CAF50; margin: 16px 0 8px;">认知层优先级</h4>
            <div style="color: #555555; line-height: 1.8;">
            1. <b>泛化抵触</b> > 其他（所有奶粉都有问题、企业欺骗等）<br>
            2. <b>精准认知</b> > 无明确认知（提到FDA、批次、国标等具体信息）<br>
            3. <b>信息混淆</b> > 无明确认知（分不清版本区别）<br>
            4. 默认：无明确认知
            </div>

            <h4 style="color: #4CAF50; margin: 20px 0 8px;">情绪层优先级</h4>
            <div style="color: #555555; line-height: 1.8;">
            1. <b>愤怒背叛</b> > 其他（企业不负责任、双标、欺骗）<br>
            2. <b>恐慌焦虑</b> > 中性（担忧宝宝健康）<br>
            3. <b>正面</b> > 中性（对a2持信任态度）<br>
            4. <b>庆幸旁观</b> > 中性（庆幸自己没买/已换）<br>
            5. 默认：中性
            </div>

            <h4 style="color: #4CAF50; margin: 20px 0 8px;">行动层优先级</h4>
            <div style="color: #555555; line-height: 1.8;">
            1. <b>维权诉求</b> > 其他（12315、投诉、赔偿）<br>
            2. <b>转奶流失</b> > 寻求帮助 > 暂无行动<br>
            3. <b>寻求帮助</b> > 暂无行动（询问怎么办、哪个安全）<br>
            4. 默认：暂无行动
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("""
        <div class="card" style="padding: 24px; margin: 16px 0;">
            <h3 style="color: #2E7DCD; margin-bottom: 20px;">ℹ️ 使用说明</h3>

            <h4 style="color: #4CAF50; margin: 16px 0 8px;">标签规则</h4>
            <p style="color: #666666; line-height: 1.8;">
            标签规则用于自动打标签，每个层级（认知/情绪/行动/品牌）都有对应的关键词配置。
            系统按优先级顺序匹配，匹配到即停止。
            </p>

            <h4 style="color: #4CAF50; margin: 20px 0 8px;">清洗规则</h4>
            <p style="color: #666666; line-height: 1.8;">
            清洗规则用于过滤无效数据，如纯@无互动、纯表情、乱码等。
            可以在数据清洗页面单独开关，实时预览效果。
            </p>

            <h4 style="color: #4CAF50; margin: 20px 0 8px;">分母配置</h4>
            <p style="color: #666666; line-height: 1.8;">
            每个项目的分母可配置，影响标签占比统计。
            第一阶段默认586条，第二阶段默认4093条（已剔除纯@无互动）。
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============== 数据统计页 ==============
elif page == "数据统计":
    render_page_header("📊 数据统计", "查看标签分布和可视化图表")
    st.markdown("<p style='color: #666666;'>查看标签分布和可视化图表</p>", unsafe_allow_html=True)

    session = get_session()
    records = session.query(RawData).filter(RawData.project_id == project_id).all()
    df = pd.DataFrame([r.to_dict() for r in records])
    project = session.query(Project).filter(Project.id == project_id).first()
    session.close()

    if len(df) == 0:
        st.warning("⚠️ 请先导入数据")
        st.stop()

    df_valid = df[df['is_valid'] == True]
    s1_d = project.s1_denominator or 586
    s2_d = project.s2_denominator or 4093

    render_section_title("📊 统计配置", "📊")

    col1, col2, col3 = st.columns(3)
    with col1:
        stat_layer = st.selectbox("选择层级", ["认知层", "情绪层", "行动层"])
    with col2:
        stat_stage = st.selectbox("选择阶段", ["阶段一(4月)", "阶段二(5月)", "全部阶段"])
    with col3:
        chart_type = st.selectbox("图表类型", ["柱状图", "饼图"])

    layer_col_map = {"认知层": "cognitive_s2", "情绪层": "emotional_s2", "行动层": "action_s2"}
    denom_map = {"阶段一(4月)": s1_d, "阶段二(5月)": s2_d, "全部阶段": s1_d + s2_d}
    col = layer_col_map.get(stat_layer)
    denom = denom_map.get(stat_stage)

    if stat_stage == "全部阶段":
        s1_mask = df_valid['comment_time'].astype(str).str.startswith('2026-04')
        s2_mask = df_valid['comment_time'].astype(str).str.startswith('2026-05')
        s1_df = df_valid[s1_mask]
        s2_df = df_valid[s2_mask]
        s1_stats = s1_df[col].value_counts().to_dict() if col in s1_df.columns else {}
        s2_stats = s2_df[col].value_counts().to_dict() if col in s2_df.columns else {}

        labels_map = {"认知层": ["无明确认知", "信息混淆", "精准认知", "泛化抵触"],
                      "情绪层": ["中性", "正面", "恐慌焦虑", "庆幸旁观", "愤怒背叛"],
                      "行动层": ["暂无行动", "寻求帮助", "转奶流失", "维权诉求"]}

        cols = st.columns(2)
        for idx, (stage_name, stage_df, stage_stats, stage_denom) in enumerate([("阶段一(4月)", s1_df, s1_stats, s1_d), ("阶段二(5月)", s2_df, s2_stats, s2_d)]):
            with cols[idx]:
                st.markdown(f"""
                <div class="card" style="padding: 20px;">
                    <div style="font-size: 14px; color: #2E7DCD; margin-bottom: 16px;">{stage_name} (分母: {stage_denom})</div>
                """, unsafe_allow_html=True)
                for label in labels_map.get(stat_layer, []):
                    count = stage_stats.get(label, 0)
                    pct = count / stage_denom * 100 if stage_denom > 0 else 0
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(0,212,255,0.1);">
                        <span style="color: #444444;">{label}</span>
                        <span style="color: #2E7DCD;">{count} <span style="color: #999999;">({pct:.1f}%)</span></span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        stage_mask = df_valid['comment_time'].astype(str).str.startswith('2026-04' if '一' in stat_stage else '2026-05')
        stage_df = df_valid[stage_mask]
        stats = stage_df[col].value_counts().to_dict() if col in stage_df.columns else {}

        labels_map = {"认知层": ["无明确认知", "信息混淆", "精准认知", "泛化抵触"],
                      "情绪层": ["中性", "正面", "恐慌焦虑", "庆幸旁观", "愤怒背叛"],
                      "行动层": ["暂无行动", "寻求帮助", "转奶流失", "维权诉求"]}

        cols = st.columns(2)
        for idx, label in enumerate(labels_map.get(stat_layer, [])):
            with cols[idx % 2]:
                count = stats.get(label, 0)
                pct = count / denom * 100 if denom > 0 else 0
                st.markdown(f"""
                <div class="card" style="padding: 16px; margin: 8px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #444444; font-size: 14px;">{label}</span>
                        <span style="color: #2E7DCD; font-size: 20px; font-weight: 600;">{count}</span>
                    </div>
                    <div style="margin-top: 8px;">
                        <div class="progress-bar"><div class="fill" style="width: {pct}%;"></div></div>
                    </div>
                    <div style="text-align: right; font-size: 11px; color: #999999; margin-top: 4px;">{pct:.1f}% (分母: {denom})</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    render_section_title("📈 可视化图表", "📈")

    if stat_stage == "全部阶段":
        chart_df = pd.DataFrame([
            {"分类": label, "阶段一(4月)": s1_stats.get(label, 0), "阶段二(5月)": s2_stats.get(label, 0)}
            for label in labels_map.get(stat_layer, [])
        ])
    else:
        chart_df = pd.DataFrame([
            {"分类": label, "数量": stats.get(label, 0)}
            for label in labels_map.get(stat_layer, [])
        ])

    if chart_type == "柱状图":
        if stat_stage == "全部阶段":
            fig = px.bar(chart_df, x="分类", y=["阶段一(4月)", "阶段二(5月)"], barmode="group",
                        template="plotly_dark", color_discrete_sequence=["#2E7DCD", "#4CAF50"])
        else:
            fig = px.bar(chart_df, x="分类", y="数量", template="plotly_dark", color_discrete_sequence=["#2E7DCD"])
    else:
        fig = px.pie(chart_df, names="分类", values="数量" if stat_stage != "全部阶段" else "阶段一(4月)",
                    template="plotly_dark", hole=0.4, color_discrete_sequence=["#2E7DCD", "#4CAF50", "#FF5252", "#FFAA00", "#9C27B0"])

    fig.update_layout(plot_bgcolor="rgba(13,27,42,0.8)", paper_bgcolor="rgba(13,27,42,0.8)",
                      font_color="white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ============== 报告生成页 ==============
elif page == "报告生成":
    render_page_header("📄 报告生成", "选择模板生成Word/PDF报告")
    st.markdown("<p style='color: #666666;'>选择模板和板块，生成Word/PDF报告</p>", unsafe_allow_html=True)

    session = get_session()
    templates = session.query(ReportTemplate).all()
    session.close()

    render_section_title("📋 模板选择", "📋")

    template_options = {t.name: t for t in templates}
    selected_template = st.selectbox("选择报告模板", list(template_options.keys()))

    template = template_options.get(selected_template)
    if template:
        st.markdown(f"""
        <div class="card" style="padding: 16px; margin: 16px 0;">
            <div style="font-size: 12px; color: #999999;">版本</div>
            <div style="font-size: 14px; color: #2E7DCD;">{template.version}</div>
            <div style="font-size: 12px; color: #999999; margin-top: 8px;">描述</div>
            <div style="font-size: 14px; color: #444444;">{template.description or '无描述'}</div>
        </div>
        """, unsafe_allow_html=True)

        render_section_title("📌 板块勾选", "📌")

        sections = template.sections or []
        enabled_sections = []
        for sec in sections:
            if st.checkbox(f"☑️ {sec.get('name', '未命名')}", value=sec.get('enabled', True), key=f"sec_{sec.get('id')}"):
                enabled_sections.append(sec)

        st.markdown("<hr>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            filename_tpl = st.text_input("文件名模板", value=template.filename_template or "{project_name}_{date}_{version}")
        with col2:
            export_type = st.selectbox("导出格式", ["word", "pdf"])

        if st.button("📄 生成报告", use_container_width=True):
            with st.spinner("正在生成报告..."):
                session = get_session()
                records = session.query(RawData).filter(RawData.project_id == project_id).all()
                df = pd.DataFrame([r.to_dict() for r in records])
                project = session.query(Project).filter(Project.id == project_id).first()
                session.close()

                date_str = datetime.now().strftime("%Y%m%d")
                filename = filename_tpl.replace("{project_name}", project.name).replace("{date}", date_str).replace("{version}", template.version) + f".{export_type}"

                doc = Document()
                doc.add_heading(f"{project.name} 舆情分析报告", 0)
                doc.add_paragraph(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                doc.add_paragraph(f"模板版本：{template.version}")

                for sec in enabled_sections:
                    doc.add_heading(sec.get('name', '未命名'), level=1)
                    doc.add_paragraph("板块内容占位符...")

                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                export_dir = os.path.join(BASE_DIR, "exports")
                os.makedirs(export_dir, exist_ok=True)
                file_path = os.path.join(export_dir, filename)
                doc.save(file_path)

                session = get_session()
                record = ExportRecord(
                    project_id=project_id,
                    template_id=template.id,
                    template_name=template.name,
                    export_type=export_type,
                    filename=filename,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    exported_by=st.session_state.get('user_id'),
                    included_sections=[s.get('id') for s in enabled_sections],
                    filename_template=filename_tpl
                )
                session.add(record)
                session.commit()
                session.close()

                st.success(f"✅ 报告已生成：{filename}")
                st.download_button("📥 下载报告", open(file_path, "rb").read(), filename=filename)

# ============== 模板管理页 ==============
elif page == "模板管理":
    render_page_header("📋 模板管理", "管理报告模板和板块配置")
    st.markdown("<p style='color: #666666;'>管理报告模板和板块配置</p>", unsafe_allow_html=True)

    session = get_session()
    templates = session.query(ReportTemplate).all()
    session.close()

    render_section_title("📋 模板列表", "📋")

    if len(templates) == 0:
        st.info("暂无报告模板")
    else:
        for t in templates:
            st.markdown(f"""
            <div class="card" style="padding: 20px; margin: 12px 0;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div style="font-size: 16px; color: #2E7DCD; font-weight: 600;">{t.name}</div>
                        <div style="font-size: 12px; color: #999999; margin-top: 4px;">版本: {t.version} | 板块: {len(t.sections) if t.sections else 0}</div>
                        <div style="font-size: 12px; color: #666666; margin-top: 8px;">{t.description or '无描述'}</div>
                    </div>
                    <div class="tag {'tag-success' if t.is_default else 'tag-info'}">{'(默认)' if t.is_default else ''}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    render_section_title("➕ 创建新模板", "➕")

    col1, col2 = st.columns(2)
    with col1:
        tmpl_name = st.text_input("模板名称")
        tmpl_version = st.text_input("版本", value="1.0")
    with col2:
        tmpl_desc = st.text_input("模板描述")
        tmpl_default = st.checkbox("设为默认模板")

    st.markdown("**板块配置**")
    section_names = st.text_area("板块名称（每行一个）", placeholder="报告概述\n评论内容类型分布\n认知分析...")

    if st.button("💾 创建模板", use_container_width=True):
        if tmpl_name:
            session = get_session()
            sections = [{"id": f"sec_{i}", "name": name.strip(), "enabled": True, "order": i+1}
                       for i, name in enumerate(section_names.split('\n')) if name.strip()]
            tmpl = ReportTemplate(
                name=tmpl_name,
                version=tmpl_version,
                description=tmpl_desc,
                sections=sections,
                is_default=tmpl_default
            )
            session.add(tmpl)
            if tmpl_default:
                session.query(ReportTemplate).update({ReportTemplate.is_default: False})
            session.commit()
            session.close()
            st.success("模板创建成功！")
            st.rerun()
        else:
            st.warning("请输入模板名称")

# ============== 导出记录页 ==============
elif page == "导出记录":
    render_page_header("📁 导出记录", "查看所有导出历史记录")
    st.markdown("<p style='color: #666666;'>查看所有导出历史记录</p>", unsafe_allow_html=True)

    session = get_session()
    exports = session.query(ExportRecord).filter(ExportRecord.project_id == project_id).order_by(ExportRecord.exported_at.desc()).all()
    session.close()

    if len(exports) == 0:
        st.info("📭 暂无导出记录")
    else:
        render_section_title("📋 导出历史", "📋")

        export_data = []
        for e in exports:
            export_data.append({
                "ID": e.id,
                "文件名": e.filename,
                "模板": e.template_name or "-",
                "格式": e.export_type.upper(),
                "大小": f"{e.file_size/1024:.1f} KB" if e.file_size else "-",
                "时间": e.exported_at.strftime("%Y-%m-%d %H:%M") if e.exported_at else "-",
                "板块": len(e.included_sections) if e.included_sections else 0
            })
        st.dataframe(pd.DataFrame(export_data), hide_index=True, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        render_section_title("⚙️ 文件名模板配置", "⚙️")

        st.markdown("""
        <div class="card" style="padding: 20px; margin: 16px 0;">
            <p style="color: #666666; line-height: 1.8;">
            <b style="color: #2E7DCD;">可用变量：</b><br>
            <code style="color: #4CAF50;">{project_name}</code> - 项目名称<br>
            <code style="color: #4CAF50;">{date}</code> - 生成日期<br>
            <code style="color: #4CAF50;">{version}</code> - 模板版本
            </p>
        </div>
        """, unsafe_allow_html=True)

        default_tpl = "{project_name}_{date}_{version}"
        new_tpl = st.text_input("文件名模板", value=default_tpl)

        if st.button("💾 保存模板", use_container_width=True):
            st.success("文件名模板已保存")

else:
    st.markdown(f"""
    <div style="text-align: center; padding: 100px 0;">
        <h2 style="color: rgba(255,255,255,0.3);">🚧 功能开发中</h2>
        <p style="color: rgba(0,0,0,0.08); margin-top: 16px;">页面: {page}</p>
    </div>
    """, unsafe_allow_html=True)