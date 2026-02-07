"""
HarmLens Moderator Dashboard
Professional interface with authentication for moderators
Combines content analysis + audit logs + blockchain verification
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# API Configuration
# Priority: Streamlit secrets > Environment variable > localhost
import os
try:
    API_BASE = st.secrets.get("API_BASE_URL", os.getenv("API_BASE_URL", "http://localhost:8000"))
    DEMO_MODE = st.secrets.get("DEMO_MODE", os.getenv("DEMO_MODE", "false")).lower() == "true"
except:
    API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"


def get_mock_response(endpoint, method="GET", data=None):
    """Return mock data for demo mode"""
    if "/auth/login" in endpoint:
        return {
            "token": "demo_token_12345",
            "user": {
                "user_id": data.get("user_id", "demo_001"),
                "username": data.get("username", "demo"),
                "role": "moderator" if "moderator" in data.get("username", "") else "admin",
                "email": "demo@harmlens.ai",
                "permissions": ["view_content", "analyze_content", "view_audit_log", "manage_queue", "escalate"]
            },
            "message": "Login successful (Demo Mode)"
        }
    elif "/blockchain/stats" in endpoint:
        return {
            "connected": True,
            "mode": "Demo Mode",
            "network": "Simulation"
        }
    elif "/auth/users" in endpoint:
        return {
            "users": [
                {"username": "admin", "user_id": "admin_001", "role": "admin", "email": "admin@demo.com"},
                {"username": "moderator", "user_id": "moderator_001", "role": "moderator", "email": "mod@demo.com"}
            ]
        }
    elif "/audit/logs" in endpoint:
        return {
            "logs": [],
            "accessed_by": {"username": "demo", "role": "moderator"},
            "timestamp": "2026-02-07T12:00:00"
        }
    else:
        return {"status": "ok", "message": "Demo mode - no real data"}

# Page config
st.set_page_config(
    page_title="HarmLens Moderator Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "HarmLens - AI-Powered Content Moderation with Blockchain Audit Trail"
    }
)

# Force dark theme
st.markdown("""
<script>
    var stApp = window.parent.document.querySelector('.stApp');
    if (stApp) {
        stApp.classList.add('dark-mode');
    }
</script>
""", unsafe_allow_html=True)

# Custom CSS for professional dark mode
st.markdown("""
<style>
    /* Dark mode theme colors */
    :root {
        --bg-primary: #0e1117;
        --bg-secondary: #1a1d29;
        --bg-tertiary: #262730;
        --text-primary: #fafafa;
        --text-secondary: #b0b3b8;
        --accent-blue: #4a9eff;
        --accent-purple: #8b5cf6;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-orange: #f59e0b;
        --border-color: #2d3139;
    }
    
    /* Main app background */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }
    
    /* Sidebar dark mode */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d29 0%, #0e1117 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary);
    }
    
    /* Header styling - dark mode */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }
    
    /* Card styling - dark mode */
    .metric-card {
        background: var(--bg-secondary);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--accent-blue);
        margin-bottom: 1rem;
        color: var(--text-primary);
    }
    
    .metric-card h3 {
        color: var(--text-primary);
    }
    
    .metric-card p {
        color: var(--text-secondary);
    }
    
    /* Button styling - dark mode */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        border-color: var(--accent-blue);
    }
    
    /* Primary button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        border: none;
        color: white;
    }
    
    /* Input fields - dark mode */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 1px var(--accent-blue);
    }
    
    /* Info boxes - dark mode */
    .info-box {
        background: rgba(74, 158, 255, 0.1);
        border-left: 4px solid var(--accent-blue);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: var(--text-primary);
        border: 1px solid rgba(74, 158, 255, 0.2);
    }
    
    .success-box {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--accent-green);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: var(--text-primary);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .warning-box {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid var(--accent-orange);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: var(--text-primary);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    
    .error-box {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid var(--accent-red);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: var(--text-primary);
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    /* Risk score styling - dark mode */
    .risk-low {
        color: var(--accent-green);
        font-weight: bold;
    }
    
    .risk-medium {
        color: var(--accent-orange);
        font-weight: bold;
    }
    
    .risk-high {
        color: var(--accent-red);
        font-weight: bold;
    }
    
    /* Metrics - dark mode */
    [data-testid="stMetricValue"] {
        color: var(--text-primary);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary);
    }
    
    /* Dataframe - dark mode */
    .stDataFrame {
        background-color: var(--bg-secondary);
    }
    
    /* Expander - dark mode */
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-top: none;
    }
    
    /* Tabs - dark mode */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--bg-secondary);
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary);
        background-color: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent-blue);
        background-color: var(--bg-tertiary);
    }
    
    /* Progress bar - dark mode */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
    }
    
    /* Divider - dark mode */
    hr {
        border-color: var(--border-color);
    }
    
    /* Code blocks - dark mode */
    code {
        background-color: var(--bg-tertiary);
        color: var(--accent-blue);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        border: 1px solid var(--border-color);
    }
    
    /* Scrollbar - dark mode */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-tertiary);
        border-radius: 5px;
        border: 2px solid var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-color);
    }
    
    /* Form styling - dark mode */
    .stForm {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    /* Caption text */
    .stCaption {
        color: var(--text-secondary);
    }
    
    /* Success/Error/Warning/Info messages */
    .stAlert {
        background-color: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = "login"


def api_request(endpoint, method="GET", data=None, auth_required=True):
    """Make API request with authentication and retry logic"""
    
    # Demo mode - return mock data
    if DEMO_MODE:
        return get_mock_response(endpoint, method, data)
    
    headers = {"Content-Type": "application/json"}
    
    if auth_required and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_BASE}{endpoint}"
    
    # Retry logic for connection issues
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 401:
                st.session_state.token = None
                st.session_state.user = None
                st.error("Session expired. Please login again.")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    continue
                return None
                
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                continue
            else:
                st.error(f"⚠️ Cannot connect to API server. Please ensure it's running on {API_BASE}")
                st.info("Start the API server: `python api_server.py`")
                return None
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                continue
            else:
                st.error("⚠️ API request timed out. Please try again.")
                return None
        except Exception as e:
            st.error(f"API Error: {e}")
            return None
    
    return None


def login_page():
    """Professional login page for moderators"""
    
    # Check API connection first
    try:
        test_response = requests.get(f"{API_BASE}/api/v1/blockchain/stats", timeout=2)
        api_online = test_response.status_code == 200
    except:
        api_online = False
    
    if not api_online:
        st.error("⚠️ API Server is not responding!")
        st.warning("""
        **Please start the API server:**
        
        ```bash
        python api_server.py
        ```
        
        Then refresh this page.
        """)
        st.stop()
    
    # Header - Generic for login page
    user_role = 'viewer'  # Default for login page
    
    if user_role == 'admin':
        header_title = "🔧 HarmLens Admin Panel"
        header_subtitle = "System Administration & User Management"
        header_gradient = "linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)"
    else:
        header_title = "🛡️ HarmLens"
        header_subtitle = "Content Moderation Platform with Blockchain Audit Trail"
        header_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    
    st.markdown(f"""
    <div class="main-header" style="background: {header_gradient};">
        <h1>{header_title}</h1>
        <p>{header_subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        st.markdown("---")
        
        # Credentials info (collapsed by default)
        with st.expander("📋 Demo Credentials", expanded=False):
            st.markdown("""
            **Admin Account:**
            - Username: `admin`
            - User ID: `admin_001`
            - Access: Full system access
            
            **Moderator Account:**
            - Username: `moderator`
            - User ID: `moderator_001`
            - Access: Content moderation + Audit logs
            
            *Note: Create more users after login via User Management*
            """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(
                "👤 Username",
                placeholder="Enter your username",
                help="Use 'admin' or 'moderator'"
            )
            user_id = st.text_input(
                "🆔 User ID",
                placeholder="Enter your user ID",
                help="Use 'admin_001' or 'moderator_001'"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")
            with col_b:
                st.form_submit_button("❓ Help", use_container_width=True)
            
            if submitted:
                if not username or not user_id:
                    st.error("⚠️ Please enter both username and user ID")
                else:
                    with st.spinner("🔄 Authenticating..."):
                        # Login
                        response = api_request(
                            "/api/v1/auth/login",
                            method="POST",
                            data={"username": username, "user_id": user_id},
                            auth_required=False
                        )
                        
                        if response:
                            st.session_state.token = response['token']
                            st.session_state.user = response['user']
                            st.session_state.page = "dashboard"
                            st.success(f"✅ Welcome, {response['user']['username']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please check your username and user ID.")
    
    # System status footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌐 API Status", "Online", delta="✓")
    
    with col2:
        blockchain_stats = api_request("/api/v1/blockchain/stats", auth_required=False)
        if blockchain_stats:
            mode = blockchain_stats.get('mode', blockchain_stats.get('network', 'Unknown'))
            st.metric("⛓️ Blockchain", mode, delta="Active")
    
    with col3:
        st.metric("🔐 Security", "Enabled", delta="✓")
    
    with col4:
        st.metric("📊 Version", "2.1.0", delta="Latest")


def sidebar():
    """Sidebar navigation - different styling for admin vs moderator"""
    with st.sidebar:
        # Demo mode banner
        if DEMO_MODE:
            st.warning("🎭 **DEMO MODE**\n\nUsing mock data. No real API connection.")
        
        user_role = st.session_state.user['role']
        
        # Different styling based on role
        if user_role == 'admin':
            st.title("🔧 Admin Panel")
            role_color = "#a855f7"
        else:
            st.title("🛡️ HarmLens")
            role_color = "#667eea"
        
        st.caption(f"Logged in as: **{st.session_state.user['username']}**")
        st.markdown(f"<p style='color: {role_color}; font-weight: bold;'>Role: {st.session_state.user['role'].upper()}</p>", unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation - role-based
        
        # Common pages for all roles
        pages = {
            "📊 Dashboard": "dashboard",
        }
        
        # Add pages based on permissions
        permissions = st.session_state.user.get('permissions', [])
        
        # Admins get analyze, moderators get escalation queue
        if user_role == 'admin' and 'analyze_content' in permissions:
            pages["🔍 Analyze Content"] = "analyze"
        elif user_role == 'moderator':
            pages["🚨 Escalation Queue"] = "escalations"
        
        if 'view_audit_log' in permissions:
            pages["📋 Audit Logs"] = "audit_logs"
        
        if 'view_blockchain' in permissions:
            pages["⛓️ Blockchain"] = "blockchain"
        
        if 'manage_users' in permissions:
            pages["👥 User Management"] = "users"
        
        # Settings available to all
        pages["⚙️ Settings"] = "settings"
        
        for label, page in pages.items():
            # Highlight admin-only features
            if page == "users" and user_role == 'admin':
                button_type = "primary"
            else:
                button_type = "secondary"
            
            if st.button(label, use_container_width=True, type=button_type if page == "users" else "secondary"):
                st.session_state.page = page
                st.rerun()
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()
        
        # System info
        st.divider()
        st.caption("**System Info**")
        st.caption(f"API: {API_BASE}")
        
        # Blockchain status
        blockchain_stats = api_request("/api/v1/blockchain/stats", auth_required=False)
        if blockchain_stats:
            st.caption(f"Blockchain: {blockchain_stats.get('mode', 'Active')}")


def dashboard_page():
    """Main dashboard - different for admin vs moderator"""
    
    user_role = st.session_state.user['role']
    
    # Different titles based on role
    if user_role == 'admin':
        st.title("🔧 Admin Dashboard")
        st.caption("System administration and oversight")
    else:
        st.title("📊 Content Moderation Dashboard")
        st.caption("Review and moderate flagged content")
    
    # Get real stats from database
    try:
        from core.database import ModerationDatabase
        db = ModerationDatabase()
        stats = db.get_stats()
        
        # Get queue counts
        priority_queue = db.get_queue_items("Priority Review Queue", "pending")
        child_queue = db.get_queue_items("Child Safety", "pending")
        medium_queue = db.get_queue_items("Automated + Sampling Review", "pending")
        
        pending_total = len(priority_queue) + len(child_queue) + len(medium_queue)
        
    except Exception as e:
        st.error(f"Error loading stats: {e}")
        stats = {'total_analyzed': 0, 'by_risk_level': {}, 'avg_processing_time_ms': 0}
        pending_total = 0
        priority_queue = []
        child_queue = []
        medium_queue = []
    
    # Stats - Different emphasis for admin vs moderator
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyzed", stats.get('total_analyzed', 0))
    
    with col2:
        delta_text = "⚠️ Needs attention" if pending_total > 0 else ""
        st.metric("Pending Review", pending_total, delta=delta_text)
    
    with col3:
        by_risk = stats.get('by_risk_level', {})
        high_risk = by_risk.get('High', 0)
        priority_text = "🚨 Priority" if len(priority_queue) > 0 else ""
        st.metric("High Risk", high_risk, delta=priority_text)
    
    with col4:
        avg_time = stats.get('avg_processing_time_ms', 0)
        st.metric("Avg Processing", f"{avg_time:.0f}ms")
    
    st.divider()
    
    # ADMIN VIEW - System management focus
    if user_role == 'admin':
        st.subheader("🔧 System Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>👥 User Management</h3>
                <p>Manage moderators, reviewers, and permissions</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Manage Users", use_container_width=True, type="primary"):
                st.session_state.page = "users"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>⛓️ Blockchain Status</h3>
                <p>Monitor blockchain integration and audit logs</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Blockchain", use_container_width=True):
                st.session_state.page = "blockchain"
                st.rerun()
        
        st.divider()
        
        # Admin sees system-wide stats
        st.subheader("📊 System Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Get user count
            users_response = api_request("/api/v1/auth/users")
            user_count = len(users_response.get('users', [])) if users_response else 0
            st.metric("Total Users", user_count)
        
        with col2:
            blockchain_stats = api_request("/api/v1/blockchain/stats", auth_required=False)
            if blockchain_stats:
                mode = blockchain_stats.get('mode', 'Unknown')
                st.metric("Blockchain Mode", mode)
        
        with col3:
            st.metric("API Status", "Online", delta="✓")
    
    # MODERATOR VIEW - Content moderation focus
    else:
        st.subheader("📋 Moderation Queue")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #dc2626;">
                <h3 style="color: #dc2626; margin: 0;">🚨 Priority Review</h3>
                <h1 style="margin: 0.5rem 0;">{len(priority_queue)}</h1>
                <p style="margin: 0; color: #999;">High-risk content</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #f59e0b;">
                <h3 style="color: #f59e0b; margin: 0;">👶 Child Safety</h3>
                <h1 style="margin: 0.5rem 0;">{len(child_queue)}</h1>
                <p style="margin: 0; color: #999;">Safety concerns</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #3b82f6;">
                <h3 style="color: #3b82f6; margin: 0;">⚠️ Medium Priority</h3>
                <h1 style="margin: 0.5rem 0;">{len(medium_queue)}</h1>
                <p style="margin: 0; color: #999;">For review</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Moderator quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚨 View Escalations", use_container_width=True, type="primary"):
                st.session_state.page = "escalations"
                st.rerun()
        
        with col2:
            if st.button("📋 View Full Queue", use_container_width=True):
                st.info("Opening full queue view...")
                st.markdown("[Open Queue Dashboard](http://localhost:8502)")
        
        with col3:
            if st.button("📊 View Audit Logs", use_container_width=True):
                st.session_state.page = "audit_logs"
                st.rerun()
        
        # Recent activity preview for moderators
        if pending_total > 0:
            st.divider()
            st.subheader("🔔 Recent Flagged Content")
            
            # Show first few items from priority queue
            recent_items = priority_queue[:3] if priority_queue else (child_queue[:3] if child_queue else medium_queue[:3])
            
            for item in recent_items:
                risk_label = item.get('risk_label', 'Medium')
                risk_score = item.get('risk_score', 0)
                text_preview = item.get('text', '')[:100] + "..."
                
                if risk_label == 'High':
                    st.error(f"**{risk_label} Risk ({risk_score}/100)**: {text_preview}")
                elif risk_label == 'Medium':
                    st.warning(f"**{risk_label} Risk ({risk_score}/100)**: {text_preview}")
                else:
                    st.info(f"**{risk_label} Risk ({risk_score}/100)**: {text_preview}")
            
            st.caption("View full queue for details and actions")


def analyze_page():
    """Professional content analysis page"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Content Analysis</h1>
        <p>AI-powered risk assessment with blockchain audit trail</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Content type and input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        content_type = st.selectbox(
            "📝 Content Type",
            [
                "Social Media Post",
                "Comment",
                "Article",
                "Forum Post",
                "Review",
                "Message",
                "Video Description",
                "Image Caption",
                "Other"
            ],
            help="Select the type of content being analyzed"
        )
    
    with col2:
        platform = st.selectbox(
            "🌐 Platform",
            [
                "Twitter/X",
                "Facebook",
                "Instagram",
                "Reddit",
                "TikTok",
                "YouTube",
                "LinkedIn",
                "Discord",
                "Other"
            ],
            help="Select the platform where content was posted"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Text input
    text = st.text_area(
        "📄 Content to Analyze",
        height=200,
        placeholder="Paste the content you want to analyze here...",
        help="Enter the text content for risk assessment"
    )
    
    # Content ID
    col1, col2 = st.columns([3, 1])
    
    with col1:
        content_id = st.text_input(
            "🆔 Content ID (Optional)",
            placeholder="Auto-generated if left empty",
            help="Unique identifier for this content"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button(
            "🔍 Analyze Content",
            use_container_width=True,
            type="primary"
        )
    
    if analyze_button:
        if not text:
            st.error("⚠️ Please enter content to analyze")
        else:
            with st.spinner("🔄 Analyzing content..."):
                result = api_request(
                    "/api/v1/analyze",
                    method="POST",
                    data={
                        "text": text,
                        "content_id": content_id or None,
                        "platform": platform,
                        "metadata": {"content_type": content_type}
                    },
                    auth_required=False
                )
                
                if result:
                    st.session_state.last_analysis = result
                    st.success("✅ Analysis complete!")
                    st.rerun()
    
    # Results
    if 'last_analysis' in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Analysis Results")
        
        result = st.session_state.last_analysis
        
        # Risk score with visual indicator
        risk_score = result['risk_score']
        risk_label = result['risk_label']
        
        # Color coding
        if risk_score < 40:
            risk_color = "🟢"
            risk_class = "risk-low"
            progress_color = "normal"
        elif risk_score < 70:
            risk_color = "🟡"
            risk_class = "risk-medium"
            progress_color = "normal"
        else:
            risk_color = "🔴"
            risk_class = "risk-high"
            progress_color = "normal"
        
        # Risk score display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin:0; color: #666;">Risk Score</h3>
                <h1 style="margin:0.5rem 0; class="{risk_class}">{risk_color} {risk_score}/100</h1>
                <p style="margin:0; color: #999;">{risk_label} Risk</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin:0; color: #666;">Action</h3>
                <h2 style="margin:0.5rem 0;">{result['action']}</h2>
                <p style="margin:0; color: #999;">Priority: {result['priority']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin:0; color: #666;">Queue</h3>
                <h2 style="margin:0.5rem 0;">{result['queue']}</h2>
                <p style="margin:0; color: #999;">Content ID: {result['content_id'][:15]}...</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            escalation = "Yes" if result['child_escalation'] else "No"
            escalation_color = "#f44336" if result['child_escalation'] else "#4caf50"
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin:0; color: #666;">Child Safety</h3>
                <h2 style="margin:0.5rem 0; color: {escalation_color};">{escalation}</h2>
                <p style="margin:0; color: #999;">Escalation Required</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Progress bar for risk score
        st.progress(risk_score / 100)
        
        # Categories
        st.markdown("### 🏷️ Detected Categories")
        categories = result.get('categories', [])
        if categories:
            cols = st.columns(min(len(categories), 4))
            for i, cat in enumerate(categories):
                with cols[i % 4]:
                    st.info(f"**{cat}**")
        else:
            st.info("No specific categories detected")
        
        # Reasons
        st.markdown("### 💡 Analysis Reasons")
        for i, reason in enumerate(result.get('reasons', []), 1):
            st.markdown(f"""
            <div class="info-box">
                <strong>{i}.</strong> {reason}
            </div>
            """, unsafe_allow_html=True)
        
        # Blockchain
        if result.get('blockchain'):
            st.markdown("### ⛓️ Blockchain Audit Record")
            bc = result['blockchain']
            
            if bc.get('logged'):
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ Logged to Blockchain</strong><br>
                    Transaction Hash: <code>{bc.get('tx_hash', 'N/A')}</code><br>
                    IPFS Hash: <code>{bc.get('ipfs_hash', 'N/A')}</code>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-box">
                    <strong>⚠️ Blockchain Logging</strong><br>
                    Currently in simulator mode. Enable real blockchain for production.
                </div>
                """, unsafe_allow_html=True)


def audit_logs_page():
    """Audit logs page (protected)"""
    st.title("📋 Audit Logs")
    st.caption("🔒 Protected - Moderator access only")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.selectbox("Limit", [10, 25, 50, 100], index=1)
    
    with col2:
        risk_filter = st.selectbox("Risk Level", ["All", "Low", "Medium", "High"])
    
    with col3:
        priority_filter = st.selectbox("Priority", ["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
    
    # Fetch logs
    params = f"?limit={limit}"
    if risk_filter != "All":
        params += f"&risk_label={risk_filter}"
    if priority_filter != "All":
        params += f"&priority={priority_filter}"
    
    logs = api_request(f"/api/v1/audit/logs{params}")
    
    if logs:
        st.success(f"✅ Audit logs accessed - Recorded on blockchain")
        st.info(f"**Accessed by**: {logs['accessed_by']['username']} ({logs['accessed_by']['role']})")
        st.caption(f"**Timestamp**: {logs['timestamp']}")
        
        # Export button
        if st.button("📥 Export Logs"):
            export = api_request("/api/v1/audit/export?format=json")
            if export:
                st.success(f"Export ready: {export.get('download_url', 'N/A')}")
        
        st.divider()
        
        # Display logs (placeholder)
        st.info("Audit logs will be displayed here. Currently showing access confirmation.")
        
    else:
        st.error("❌ Unable to access audit logs. Check permissions.")


def blockchain_page():
    """Blockchain status and verification"""
    st.title("⛓️ Blockchain Integration")
    
    # Get blockchain stats
    stats = api_request("/api/v1/blockchain/stats", auth_required=False)
    
    if stats:
        st.subheader("📊 Blockchain Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            connected = stats.get('connected', False)
            st.metric("Connection", "🟢 Connected" if connected else "🔴 Disconnected")
        
        with col2:
            network = stats.get('network', stats.get('mode', 'Unknown'))
            st.metric("Network", network)
        
        with col3:
            if stats.get('total_blocks'):
                st.metric("Total Blocks", stats['total_blocks'])
            elif stats.get('contract_deployed'):
                st.metric("Contract", "✅ Deployed")
            else:
                st.metric("Mode", "Simulator")
        
        st.divider()
        
        # Blockchain info
        st.subheader("ℹ️ Current Configuration")
        
        if network == "Local Simulation":
            st.info("""
            **🔧 Development Mode**
            
            Currently using local blockchain simulator:
            - No network connection required
            - Records stored in `blockchain_sim/audit_chain.json`
            - Perfect for development and testing
            
            **To enable real blockchain:**
            1. Run `python blockchain_setup.py`
            2. Choose network (Polygon recommended)
            3. Deploy smart contract
            4. Restart API server
            """)
        else:
            st.success(f"""
            **✅ Production Mode**
            
            Connected to: {network}
            Account: {stats.get('account', 'N/A')}
            Balance: {stats.get('balance', 0)} ETH
            Contract: {'Deployed' if stats.get('contract_deployed') else 'Not deployed'}
            """)
        
        # Verify content
        st.divider()
        st.subheader("🔍 Verify Content Integrity")
        
        content_id = st.text_input("Enter Content ID to verify")
        
        if st.button("🔐 Verify"):
            if content_id:
                verify = api_request(f"/api/v1/audit/blockchain/{content_id}/verify")
                
                if verify:
                    if verify.get('verified'):
                        st.success(f"✅ Content verified: {verify.get('integrity_check', 'passed')}")
                        st.info(f"Verified by: {verify['verified_by']['username']}")
                    else:
                        st.error("❌ Verification failed")
                else:
                    st.warning("Content not found or insufficient permissions")


def users_page():
    """User management (admin only)"""
    st.title("👥 User Management")
    
    # Check if admin
    if st.session_state.user['role'] != 'admin':
        st.error("❌ Admin access required")
        return
    
    # List users
    users = api_request("/api/v1/auth/users")
    
    if users:
        st.subheader("📋 Current Users")
        
        user_data = []
        for user in users['users']:
            user_data.append({
                "Username": user['username'],
                "User ID": user['user_id'],
                "Role": user['role'],
                "Email": user.get('email', 'N/A'),
                "ETH Address": user.get('eth_address', 'N/A')[:20] + "..." if user.get('eth_address') else 'N/A'
            })
        
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        
        # Create new user
        st.subheader("➕ Create New User")
        
        with st.form("create_user"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username")
                new_role = st.selectbox("Role", ["moderator", "reviewer", "viewer"])
            
            with col2:
                new_email = st.text_input("Email (optional)")
                new_eth = st.text_input("ETH Address (optional)")
            
            if st.form_submit_button("Create User"):
                if new_username:
                    result = api_request(
                        "/api/v1/auth/users",
                        method="POST",
                        data={
                            "username": new_username,
                            "role": new_role,
                            "email": new_email or None,
                            "eth_address": new_eth or None
                        }
                    )
                    
                    if result:
                        st.success(f"✅ User created: {result['user']['user_id']}")
                        st.rerun()
                else:
                    st.error("Username required")


def settings_page():
    """Settings page"""
    st.title("⚙️ Settings")
    
    # User info
    st.subheader("👤 Your Profile")
    
    user = st.session_state.user
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=user['username'], disabled=True)
        st.text_input("User ID", value=user['user_id'], disabled=True)
    
    with col2:
        st.text_input("Role", value=user['role'], disabled=True)
        st.text_input("Email", value=user.get('email', 'Not set'), disabled=True)
    
    # Permissions
    st.divider()
    st.subheader("🔐 Your Permissions")
    
    permissions = user.get('permissions', [])
    
    cols = st.columns(3)
    for i, perm in enumerate(permissions):
        with cols[i % 3]:
            st.success(f"✅ {perm.replace('_', ' ').title()}")
    
    # API info
    st.divider()
    st.subheader("🔌 API Information")
    
    st.code(f"Base URL: {API_BASE}", language=None)
    st.code(f"Token: {st.session_state.token[:20]}...", language=None)
    
    if st.button("📋 Copy Token"):
        st.code(st.session_state.token, language=None)


def escalations_page():
    """Escalation queue page for moderators"""
    st.title("🚨 Escalation Queue")
    st.caption("Track and manage escalated content issues")
    
    # Get escalations from database
    try:
        from core.database import ModerationDatabase
        db = ModerationDatabase()
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Status",
                ["All", "pending", "in-progress", "responded", "resolved"],
                index=0
            )
        
        with col2:
            priority_filter = st.selectbox(
                "Priority",
                ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
                index=0
            )
        
        with col3:
            escalation_type = st.selectbox(
                "Type",
                ["All", "Child Safety", "Legal Issue", "Urgent Review", "Policy Violation", "Other"],
                index=0
            )
        
        # Get escalations
        status = None if status_filter == "All" else status_filter
        escalations = db.get_escalations(status=status)
        
        # Filter by priority and type
        if priority_filter != "All":
            escalations = [e for e in escalations if e['priority'] == priority_filter]
        
        if escalation_type != "All":
            escalations = [e for e in escalations if e['escalation_type'] == escalation_type]
        
        # Stats
        st.divider()
        
        col1, col2, col3, col4 = st.columns(4)
        
        pending = len([e for e in escalations if e['status'] == 'pending'])
        in_progress = len([e for e in escalations if e['status'] == 'in-progress'])
        responded = len([e for e in escalations if e['status'] == 'responded'])
        resolved = len([e for e in escalations if e['status'] == 'resolved'])
        
        with col1:
            st.metric("⏳ Pending", pending, delta="Awaiting review")
        
        with col2:
            st.metric("🔄 In Progress", in_progress, delta="Being handled")
        
        with col3:
            st.metric("💬 Responded", responded, delta="Awaiting closure")
        
        with col4:
            st.metric("✅ Resolved", resolved, delta="Completed")
        
        st.divider()
        
        # Create new escalation
        with st.expander("➕ Create New Escalation", expanded=False):
            with st.form("new_escalation"):
                col1, col2 = st.columns(2)
                
                with col1:
                    content_id = st.text_input("Content ID", help="ID of the content to escalate")
                    escalation_type_new = st.selectbox(
                        "Escalation Type",
                        ["Child Safety", "Legal Issue", "Urgent Review", "Policy Violation", "Other"]
                    )
                
                with col2:
                    priority_new = st.selectbox("Priority", ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
                    reason = st.text_area("Reason for Escalation", height=100)
                
                if st.form_submit_button("🚨 Create Escalation", type="primary"):
                    if content_id and reason:
                        escalation_id = db.create_escalation(
                            content_id=content_id,
                            escalated_by=st.session_state.user['username'],
                            reason=reason,
                            escalation_type=escalation_type_new,
                            priority=priority_new
                        )
                        st.success(f"✅ Escalation created: #{escalation_id}")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")
        
        st.divider()
        
        # Display escalations
        if not escalations:
            st.info("📭 No escalations found matching your filters")
        else:
            st.subheader(f"📋 Escalations ({len(escalations)})")
            
            for esc in escalations:
                # Status color coding
                status_colors = {
                    'pending': '#f59e0b',
                    'in-progress': '#3b82f6',
                    'responded': '#8b5cf6',
                    'resolved': '#10b981'
                }
                
                priority_colors = {
                    'CRITICAL': '#dc2626',
                    'HIGH': '#f59e0b',
                    'MEDIUM': '#3b82f6',
                    'LOW': '#6b7280'
                }
                
                status_color = status_colors.get(esc['status'], '#6b7280')
                priority_color = priority_colors.get(esc['priority'], '#6b7280')
                
                # Calculate time elapsed
                created_at = datetime.fromisoformat(esc['created_at'])
                elapsed = datetime.now() - created_at
                
                if elapsed.days > 0:
                    time_elapsed = f"{elapsed.days}d {elapsed.seconds // 3600}h ago"
                elif elapsed.seconds >= 3600:
                    time_elapsed = f"{elapsed.seconds // 3600}h ago"
                else:
                    time_elapsed = f"{elapsed.seconds // 60}m ago"
                
                # Escalation card
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 4px solid {priority_color};">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h3 style="margin: 0; color: {priority_color};">
                                    #{esc['id']} - {esc['escalation_type']}
                                </h3>
                                <p style="margin: 0.5rem 0; color: #666;">
                                    <strong>Content ID:</strong> {esc['content_id'][:20]}...
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <span style="background: {status_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600;">
                                    {esc['status'].upper()}
                                </span>
                                <p style="margin: 0.5rem 0 0 0; color: #999; font-size: 0.85rem;">
                                    {time_elapsed}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Reason:** {esc['escalation_reason']}")
                        content_preview = esc.get('content_text', '')[:150] + "..."
                        st.caption(f"Content: {content_preview}")
                    
                    with col2:
                        st.markdown(f"**Priority:** {esc['priority']}")
                        st.markdown(f"**Risk Score:** {esc.get('risk_score', 'N/A')}/100")
                        st.markdown(f"**Escalated by:** {esc['escalated_by']}")
                    
                    with col3:
                        st.markdown(f"**Response Time:** {esc['response_time_estimate']}")
                        
                        if esc['assigned_to']:
                            st.markdown(f"**Assigned to:** {esc['assigned_to']}")
                        
                        if esc['responded_at']:
                            responded_at = datetime.fromisoformat(esc['responded_at'])
                            response_time = responded_at - created_at
                            st.markdown(f"**Responded in:** {response_time.seconds // 60}m")
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if esc['status'] == 'pending':
                            if st.button(f"▶️ Start", key=f"start_{esc['id']}"):
                                db.update_escalation_status(
                                    esc['id'], 
                                    'in-progress',
                                    assigned_to=st.session_state.user['username']
                                )
                                st.success("Status updated to In Progress")
                                st.rerun()
                    
                    with col2:
                        if esc['status'] in ['pending', 'in-progress']:
                            if st.button(f"💬 Respond", key=f"respond_{esc['id']}"):
                                db.update_escalation_status(esc['id'], 'responded')
                                st.success("Status updated to Responded")
                                st.rerun()
                    
                    with col3:
                        if esc['status'] in ['responded', 'in-progress']:
                            if st.button(f"✅ Resolve", key=f"resolve_{esc['id']}"):
                                db.update_escalation_status(
                                    esc['id'], 
                                    'resolved',
                                    resolution_notes="Resolved by moderator"
                                )
                                st.success("Escalation resolved")
                                st.rerun()
                    
                    with col4:
                        if st.button(f"👁️ View Details", key=f"view_{esc['id']}"):
                            st.session_state.selected_escalation = esc['id']
                    
                    st.divider()
        
        # Show selected escalation details
        if 'selected_escalation' in st.session_state:
            selected = next((e for e in escalations if e['id'] == st.session_state.selected_escalation), None)
            
            if selected:
                st.markdown("---")
                st.subheader(f"📄 Escalation Details - #{selected['id']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Content ID:** {selected['content_id']}")
                    st.markdown(f"**Type:** {selected['escalation_type']}")
                    st.markdown(f"**Priority:** {selected['priority']}")
                    st.markdown(f"**Status:** {selected['status']}")
                    st.markdown(f"**Escalated by:** {selected['escalated_by']}")
                
                with col2:
                    st.markdown(f"**Created:** {selected['created_at']}")
                    st.markdown(f"**Updated:** {selected['updated_at']}")
                    st.markdown(f"**Response Time Estimate:** {selected['response_time_estimate']}")
                    
                    if selected['assigned_to']:
                        st.markdown(f"**Assigned to:** {selected['assigned_to']}")
                    
                    if selected['resolved_at']:
                        st.markdown(f"**Resolved:** {selected['resolved_at']}")
                
                st.markdown("**Escalation Reason:**")
                st.info(selected['escalation_reason'])
                
                st.markdown("**Content:**")
                st.text_area("", value=selected.get('content_text', 'N/A'), height=150, disabled=True)
                
                if selected.get('resolution_notes'):
                    st.markdown("**Resolution Notes:**")
                    st.success(selected['resolution_notes'])
                
                if st.button("❌ Close Details"):
                    del st.session_state.selected_escalation
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error loading escalations: {e}")
        import traceback
        st.code(traceback.format_exc())


# Main app
def main():
    if st.session_state.token is None:
        login_page()
    else:
        sidebar()
        
        # Route to pages
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "analyze":
            analyze_page()
        elif st.session_state.page == "escalations":
            escalations_page()
        elif st.session_state.page == "audit_logs":
            audit_logs_page()
        elif st.session_state.page == "blockchain":
            blockchain_page()
        elif st.session_state.page == "users":
            users_page()
        elif st.session_state.page == "settings":
            settings_page()


if __name__ == "__main__":
    main()
