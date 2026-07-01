import streamlit as st
import requests
import time
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Truck Theft Detection",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SESSION STATE INITIALIZATION
# =========================
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Default to light mode
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'prev_theft' not in st.session_state:
    st.session_state.prev_theft = "0"
if 'prev_door' not in st.session_state:
    st.session_state.prev_door = "0"
if 'prev_cmd' not in st.session_state:
    st.session_state.prev_cmd = "0"
if 'prev_weight' not in st.session_state:
    st.session_state.prev_weight = "0"

# =========================
# CONFIG
# =========================
READ_URL = "https://api.thingspeak.com/channels/3234262/feeds/last.json?api_key=76UI1H11CWP4O4DU"
WRITE_URL = "https://api.thingspeak.com/update?api_key=Z0TT1DCL1DUH6A5P"

# =========================
# THEME CONFIGURATION
# =========================
def get_theme_colors():
    """Returns enterprise-grade color palette based on current theme"""
    if st.session_state.theme == 'dark':
        return {
            'bg_primary': '#0B0E14',
            'bg_secondary': '#151A23',
            'bg_card': '#1A1F2E',
            'bg_card_hover': '#222938',
            'text_primary': '#E8EAED',
            'text_secondary': '#9AA0A6',
            'text_tertiary': '#5F6368',
            'border': '#2D3748',
            'border_light': '#1F2937',
            'accent': '#4F96FF',
            'accent_hover': '#6BA8FF',
            'success': '#34D399',
            'success_bg': '#065F46',
            'warning': '#FBBF24',
            'warning_bg': '#78350F',
            'danger': '#F87171',
            'danger_bg': '#7F1D1D',
            'info': '#60A5FA',
            'shadow': 'rgba(0, 0, 0, 0.5)',
            'shadow_light': 'rgba(0, 0, 0, 0.2)'
        }
    else:
        return {
            'bg_primary': '#F8FAFB',
            'bg_secondary': '#FFFFFF',
            'bg_card': '#FFFFFF',
            'bg_card_hover': '#F9FAFB',
            'text_primary': '#1F2937',
            'text_secondary': '#6B7280',
            'text_tertiary': '#9CA3AF',
            'border': '#E5E7EB',
            'border_light': '#F3F4F6',
            'accent': '#2563EB',
            'accent_hover': '#1D4ED8',
            'success': '#059669',
            'success_bg': '#D1FAE5',
            'warning': '#D97706',
            'warning_bg': '#FEF3C7',
            'danger': '#DC2626',
            'danger_bg': '#FEE2E2',
            'info': '#3B82F6',
            'shadow': 'rgba(0, 0, 0, 0.08)',
            'shadow_light': 'rgba(0, 0, 0, 0.04)'
        }

colors = get_theme_colors()

# =========================
# ENTERPRISE-GRADE CSS
# =========================
st.markdown(f"""
<style>
    /* Global Reset & Base Styles */
    .main {{
        background-color: {colors['bg_primary']};
        color: {colors['text_primary']};
        padding: 1rem 2rem;
    }}
    
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}
    
    /* Remove Streamlit's default animations on rerun to prevent flicker */
    .element-container {{
        animation: none !important;
    }}
    
    /* Metric Card - Stable Layout */
    .metric-card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px {colors['shadow_light']};
        transition: box-shadow 0.2s ease, transform 0.2s ease;
        height: 100%;
        min-height: 140px;
        display: flex;
        flex-direction: column;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 4px 12px {colors['shadow']};
        transform: translateY(-2px);
    }}
    
    .metric-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.75rem;
        opacity: 0.85;
        line-height: 1;
    }}
    
    .metric-label {{
        font-size: 0.813rem;
        font-weight: 600;
        color: {colors['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {colors['text_primary']};
        margin-top: auto;
        line-height: 1.2;
    }}
    
    /* Status Colors - No animation by default */
    .status-open {{
        color: {colors['danger']};
    }}
    
    .status-closed {{
        color: {colors['success']};
    }}
    
    .status-on {{
        color: {colors['success']};
    }}
    
    .status-off {{
        color: {colors['text_tertiary']};
    }}
    
    /* Theft Alert - Subtle, No Blink */
    .theft-alert {{
        background: {colors['danger_bg']};
        border: 1px solid {colors['danger']};
        border-left: 4px solid {colors['danger']};
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
    }}
    
    .theft-alert-content {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}
    
    .theft-alert-icon {{
        font-size: 1.5rem;
        color: {colors['danger']};
    }}
    
    .theft-alert-text {{
        color: {colors['danger']};
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }}
    
    /* Header Section */
    .page-header {{
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {colors['border_light']};
    }}
    
    .page-title {{
        font-size: 2rem;
        font-weight: 700;
        color: {colors['text_primary']};
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}
    
    .live-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background: {colors['success_bg']};
        color: {colors['success']};
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    .live-dot {{
        width: 6px;
        height: 6px;
        background: {colors['success']};
        border-radius: 50%;
    }}
    
    .page-subtitle {{
        color: {colors['text_secondary']};
        font-size: 0.875rem;
        margin: 0.5rem 0 0 0;
    }}
    
    /* Section Card */
    .section-card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px {colors['shadow_light']};
        margin-top: 1.5rem;
    }}
    
    .section-header {{
        font-size: 1.125rem;
        font-weight: 600;
        color: {colors['text_primary']};
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    /* Sidebar Styles */
    .sidebar-section {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    
    .sidebar-section-title {{
        font-size: 0.875rem;
        font-weight: 600;
        color: {colors['text_primary']};
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .info-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid {colors['border_light']};
    }}
    
    .info-row:last-child {{
        border-bottom: none;
    }}
    
    .info-label {{
        font-size: 0.813rem;
        color: {colors['text_secondary']};
    }}
    
    .info-value {{
        font-size: 0.813rem;
        font-weight: 600;
        color: {colors['text_primary']};
    }}
    
    /* Notification Item */
    .notification-item {{
        background: {colors['bg_card']};
        border-left: 3px solid {colors['info']};
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.813rem;
    }}
    
    .notification-critical {{
        border-left-color: {colors['danger']};
        background: {colors['danger_bg']};
    }}
    
    .notification-warning {{
        border-left-color: {colors['warning']};
        background: {colors['warning_bg']};
    }}
    
    .notification-info {{
        border-left-color: {colors['info']};
    }}
    
    .notification-message {{
        color: {colors['text_primary']};
        font-weight: 500;
        margin-bottom: 0.25rem;
    }}
    
    .notification-time {{
        color: {colors['text_tertiary']};
        font-size: 0.75rem;
    }}
    
    /* Buttons */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        border: none;
        transition: all 0.2s ease;
        padding: 0.625rem 1.25rem;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 8px {colors['shadow']};
    }}
    
    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .main {{
            padding: 0.75rem;
        }}
        
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        
        .metric-card {{
            padding: 1rem;
            min-height: 120px;
        }}
        
        .metric-value {{
            font-size: 1.5rem;
        }}
        
        .page-title {{
            font-size: 1.5rem;
        }}
        
        .section-card {{
            padding: 1rem;
        }}
    }}
    
    /* Hide Streamlit Elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    
    /* Smooth theme transitions */
    .main, .metric-card, .section-card, .sidebar-section {{
        transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
    }}
</style>
""", unsafe_allow_html=True)

# =========================
# HELPER FUNCTIONS
# =========================
def add_notification(message, severity="INFO"):
    """Add notification to session state with timestamp"""
    notification = {
        'time': datetime.now().strftime("%I:%M:%S %p"),
        'message': message,
        'severity': severity
    }
    st.session_state.notifications.insert(0, notification)
    # Keep only last 15 notifications
    if len(st.session_state.notifications) > 15:
        st.session_state.notifications = st.session_state.notifications[:15]

def get_data():
    """Fetch data from ThingSpeak API"""
    try:
        r = requests.get(READ_URL, timeout=5)
        return r.json()
    except Exception as e:
        return {}

def render_metric_card(icon, label, value, status_class=""):
    """Render professional metric card with stable layout"""
    return f"""
    <div class='metric-card'>
        <div class='metric-icon'>{icon}</div>
        <div class='metric-label'>{label}</div>
        <div class='metric-value {status_class}'>{value}</div>
    </div>
    """

# =========================
# SIDEBAR - CONTROL CENTER
# =========================
st.sidebar.markdown(f"<div style='padding: 0.5rem 0;'><h2 style='color: {colors['text_primary']}; font-size: 1.25rem; margin: 0;'>Control Center</h2></div>", unsafe_allow_html=True)

# Theme Toggle
st.sidebar.markdown(f"""
<div class='sidebar-section'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <span style='color: {colors['text_secondary']}; font-size: 0.875rem; font-weight: 600;'>Theme</span>
    </div>
</div>
""", unsafe_allow_html=True)

theme_col1, theme_col2 = st.sidebar.columns([3, 1])
with theme_col2:
    if st.button("🌓", key="theme_toggle", help="Toggle Dark/Light Mode"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

# =========================
# FETCH DATA
# =========================
data = get_data()

door = data.get("field1", "0")
weight = data.get("field2", "0")
theft = data.get("field3", "0")
truck = data.get("field4", "TRUCK-001")
lat = data.get("field5")
lon = data.get("field6")
cmd = data.get("field7", "0")

# =========================
# NOTIFICATION DETECTION
# =========================
# Detect theft
if theft == "1" and st.session_state.prev_theft == "0":
    add_notification("Theft detected - Unauthorized access attempt", "CRITICAL")
st.session_state.prev_theft = theft

# Detect door changes
if door == "1" and st.session_state.prev_door == "0":
    add_notification("Door opened", "WARNING")
elif door == "0" and st.session_state.prev_door == "1":
    add_notification("Door secured", "INFO")
st.session_state.prev_door = door

# Detect command changes
if cmd != st.session_state.prev_cmd:
    if cmd == "1":
        add_notification("Unloading authorized by owner", "INFO")
    else:
        add_notification("Unloading access revoked by owner", "WARNING")
st.session_state.prev_cmd = cmd

# Detect significant weight changes
try:
    weight_diff = abs(float(weight) - float(st.session_state.prev_weight))
    if weight_diff > 100:  # Significant change threshold
        add_notification(f"Cargo weight changed: {weight}g", "INFO")
except:
    pass
st.session_state.prev_weight = weight

# =========================
# SIDEBAR - TRUCK INFO
# =========================
st.sidebar.markdown(f"""
<div class='sidebar-section'>
    <div class='sidebar-section-title'>Vehicle Information</div>
    <div style='text-align: center; padding: 0.75rem 0;'>
        <div style='color: {colors['text_tertiary']}; font-size: 0.75rem; margin-bottom: 0.25rem;'>TRUCK ID</div>
        <div style='color: {colors['text_primary']}; font-size: 1.25rem; font-weight: 700;'>{truck}</div>
    </div>
    <div style='border-top: 1px solid {colors['border_light']}; padding-top: 0.75rem; margin-top: 0.75rem;'>
        <div style='text-align: center;'>
            <div style='color: {colors['text_tertiary']}; font-size: 0.75rem; margin-bottom: 0.25rem;'>SECURITY STATUS</div>
            <div style='color: {"" + colors['danger'] if theft == "1" else colors['success']}; font-size: 0.938rem; font-weight: 700;'>
                {"🚨 ALERT" if theft == "1" else "✓ SECURE"}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR - LIVE STATUS
# =========================
st.sidebar.markdown(f"""
<div class='sidebar-section'>
    <div class='sidebar-section-title'>Live Sensor Data</div>
    <div class='info-row'>
        <span class='info-label'>Door</span>
        <span class='info-value' style='color: {"" + colors['danger'] if door == "1" else colors['success']};'>
            {"OPEN" if door == "1" else "CLOSED"}
        </span>
    </div>
    <div class='info-row'>
        <span class='info-label'>Weight</span>
        <span class='info-value'>{weight} g</span>
    </div>
    <div class='info-row'>
        <span class='info-label'>GPS</span>
        <span class='info-value' style='color: {"" + colors['success'] if lat and lon and lat != "0" else colors['text_tertiary']};'>
            {"Active" if lat and lon and lat != "0" else "No Signal"}
        </span>
    </div>
    <div class='info-row'>
        <span class='info-label'>Command</span>
        <span class='info-value' style='color: {"" + colors['success'] if cmd == "1" else colors['text_tertiary']};'>
            {"ON" if cmd == "1" else "OFF"}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR - OWNER CONTROL
# =========================
st.sidebar.markdown(f"""
<div class='sidebar-section'>
    <div class='sidebar-section-title'>Owner Control</div>
    <div style='padding-top: 0.5rem;'>
""", unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("✅ Enable", use_container_width=True, type="primary", key="enable_unload"):
        try:
            requests.get(WRITE_URL + "&field7=1", timeout=5)
            st.success("Authorized", icon="✅")
        except:
            st.error("Request Failed", icon="❌")

with col2:
    if st.button("⛔ Disable", use_container_width=True, key="disable_unload"):
        try:
            requests.get(WRITE_URL + "&field7=0", timeout=5)
            st.warning("Blocked", icon="⛔")
        except:
            st.error("Request Failed", icon="❌")

st.sidebar.markdown("</div></div>", unsafe_allow_html=True)

# =========================
# SIDEBAR - NOTIFICATIONS
# =========================
st.sidebar.markdown(f"""
<div class='sidebar-section'>
    <div class='sidebar-section-title'>Activity Log</div>
""", unsafe_allow_html=True)

if st.session_state.notifications:
    for notif in st.session_state.notifications[:8]:  # Show last 8
        severity_class = f"notification-{notif['severity'].lower()}"
        st.sidebar.markdown(f"""
        <div class='notification-item {severity_class}'>
            <div class='notification-message'>{notif['message']}</div>
            <div class='notification-time'>{notif['time']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.sidebar.info("No recent activity")

st.sidebar.markdown("</div>", unsafe_allow_html=True)

# =========================
# MAIN - HEADER
# =========================
st.markdown(f"""
<div class='page-header'>
    <div class='page-title'>
        Truck Theft Detection
        <span class='live-badge'>
            <span class='live-dot'></span>
            LIVE
        </span>
    </div>
    <div class='page-subtitle'>Real-time IoT monitoring and fleet security management</div>
</div>
""", unsafe_allow_html=True)

# =========================
# THEFT ALERT BANNER
# =========================
if theft == "1":
    st.markdown(f"""
    <div class='theft-alert'>
        <div class='theft-alert-content'>
            <span class='theft-alert-icon'>🚨</span>
            <span class='theft-alert-text'>Theft Alert: Unauthorized access detected on {truck}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# METRIC CARDS
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    door_status = "OPEN" if door == "1" else "CLOSED"
    door_class = "status-open" if door == "1" else "status-closed"
    st.markdown(render_metric_card("🚪", "Door Status", door_status, door_class), unsafe_allow_html=True)

with col2:
    st.markdown(render_metric_card("⚖️", "Cargo Weight", f"{weight} g"), unsafe_allow_html=True)

with col3:
    st.markdown(render_metric_card("🚚", "Vehicle ID", truck), unsafe_allow_html=True)

with col4:
    cmd_status = "ENABLED" if cmd == "1" else "DISABLED"
    cmd_class = "status-on" if cmd == "1" else "status-off"
    st.markdown(render_metric_card("📡", "Unload Access", cmd_status, cmd_class), unsafe_allow_html=True)

# =========================
# GPS TRACKING SECTION
# =========================
st.markdown(f"""
<div class='section-card'>
    <div class='section-header'>📍 Live GPS Tracking</div>
""", unsafe_allow_html=True)

if lat and lon and lat != "0" and lon != "0":
    try:
        st.map([{"lat": float(lat), "lon": float(lon)}], zoom=13)
    except:
        st.info("📍 GPS coordinates available but unable to render map")
else:
    st.info("📍 Waiting for GPS signal - location data not available")

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# AUTO REFRESH
# =========================
time.sleep(5)
st.rerun()