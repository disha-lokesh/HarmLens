"""
HarmLens Moderator Dashboard
REAL moderation queue - see actual flagged content and take action
"""

import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from core.database import ModerationDatabase

# Initialize database
db = ModerationDatabase()

# Page config
st.set_page_config(
    page_title="HarmLens Moderator Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Dark theme like the screenshot
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Metrics */
    .metric-card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    /* Queue tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* Content cards */
    .content-card {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 1rem;
    }
    
    .content-card-high {
        border-left-color: #dc2626;
        background-color: #1f1315;
    }
    
    .content-card-medium {
        border-left-color: #f59e0b;
        background-color: #1f1b13;
    }
    
    /* Risk badges */
    .risk-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85em;
    }
    
    .risk-high {
        background-color: #dc2626;
        color: white;
    }
    
    .risk-medium {
        background-color: #f59e0b;
        color: white;
    }
    
    .risk-low {
        background-color: #10b981;
        color: white;
    }
    
    /* Empty state */
    .empty-queue {
        background-color: #064e3b;
        color: #6ee7b7;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        margin: 2rem 0;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'selected_content' not in st.session_state:
    st.session_state.selected_content = None


def get_queue_stats():
    """Get statistics for all queues"""
    stats = db.get_stats()
    
    # Get queue counts
    priority_queue = db.get_queue_items("Priority Review Queue", "pending")
    child_queue = db.get_queue_items("Child Safety", "pending")
    medium_queue = db.get_queue_items("Automated + Sampling Review", "pending")
    
    return {
        'total_analyzed': stats.get('total_analyzed', 0),
        'pending_review': len(priority_queue) + len(child_queue) + len(medium_queue),
        'high_risk': stats.get('by_risk_level', {}).get('High', 0),
        'avg_time': stats.get('avg_processing_time_ms', 0),
        'priority_count': len(priority_queue),
        'child_count': len(child_queue),
        'medium_count': len(medium_queue)
    }


def render_content_card(item, queue_type):
    """Render a content card for review"""
    
    # Get risk level styling
    risk_label = item.get('risk_label', 'Medium')
    if risk_label == 'High':
        card_class = "content-card-high"
        badge_class = "risk-high"
    elif risk_label == 'Medium':
        card_class = "content-card-medium"
        badge_class = "risk-medium"
    else:
        card_class = "content-card"
        badge_class = "risk-low"
    
    # Content preview
    text = item.get('text', '')
    text_preview = text[:200] + "..." if len(text) > 200 else text
    
    # Render card
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div class="{card_class}">
                <div style="margin-bottom: 12px;">
                    <span class="risk-badge {badge_class}">{risk_label} Risk - {item.get('risk_score', 0)}/100</span>
                    <span style="margin-left: 12px; color: #94a3b8;">
                        {item.get('content_id', 'N/A')[:20]}...
                    </span>
                </div>
                <div style="color: #e2e8f0; margin-bottom: 12px;">
                    {text_preview}
                </div>
                <div style="color: #64748b; font-size: 0.9em;">
                    <strong>Categories:</strong> {', '.join(item.get('categories', []))}
                </div>
                <div style="color: #64748b; font-size: 0.9em; margin-top: 8px;">
                    <strong>Action:</strong> {item.get('action', 'N/A')} | 
                    <strong>Priority:</strong> {item.get('priority', 'N/A')} |
                    <strong>Time:</strong> {item.get('timestamp', 'N/A')[:19]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("👁️ Review", key=f"review_{item.get('queue_id')}", use_container_width=True):
                st.session_state.selected_content = item
                st.rerun()
            
            if st.button("✅ Approve", key=f"approve_{item.get('queue_id')}", use_container_width=True, type="primary"):
                db.update_queue_status(
                    item['queue_id'],
                    status='reviewed',
                    reviewer='moderator',
                    decision='approved',
                    notes='Approved by moderator'
                )
                st.success("✅ Approved")
                st.rerun()
            
            if st.button("🗑️ Remove", key=f"remove_{item.get('queue_id')}", use_container_width=True):
                db.update_queue_status(
                    item['queue_id'],
                    status='reviewed',
                    reviewer='moderator',
                    decision='removed',
                    notes='Removed by moderator'
                )
                st.success("🗑️ Removed")
                st.rerun()


def render_detail_modal(item):
    """Render detailed view of selected content"""
    st.markdown("### 📋 Content Details")
    
    # Back button
    if st.button("← Back to Queue"):
        st.session_state.selected_content = None
        st.rerun()
    
    st.divider()
    
    # Risk score
    risk_score = item.get('risk_score', 0)
    risk_label = item.get('risk_label', 'Medium')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Risk Score", f"{risk_score}/100")
    with col2:
        st.metric("Risk Level", risk_label)
    with col3:
        st.metric("Priority", item.get('priority', 'N/A'))
    
    # Full text
    st.markdown("#### 📄 Full Content")
    st.text_area("", value=item.get('text', ''), height=200, disabled=True)
    
    # Categories
    st.markdown("#### 🏷️ Categories")
    categories = item.get('categories', [])
    if categories:
        cols = st.columns(min(len(categories), 4))
        for i, cat in enumerate(categories):
            with cols[i % 4]:
                st.info(cat)
    
    # Reasons
    st.markdown("#### 💡 Analysis Reasons")
    reasons = item.get('reasons', [])
    for i, reason in enumerate(reasons, 1):
        st.markdown(f"{i}. {reason}")
    
    # Metadata
    st.markdown("#### ℹ️ Metadata")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text(f"Content ID: {item.get('content_id', 'N/A')}")
        st.text(f"User ID: {item.get('user_id', 'N/A')}")
        st.text(f"Platform: {item.get('platform', 'N/A')}")
    
    with col2:
        st.text(f"Queue: {item.get('queue', 'N/A')}")
        st.text(f"Status: {item.get('status', 'N/A')}")
        st.text(f"Timestamp: {item.get('timestamp', 'N/A')}")
    
    # Actions
    st.divider()
    st.markdown("#### 🎯 Take Action")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve Content", use_container_width=True, type="primary"):
            db.update_queue_status(
                item['queue_id'],
                status='reviewed',
                reviewer='moderator',
                decision='approved',
                notes='Approved after review'
            )
            st.success("✅ Content approved")
            st.session_state.selected_content = None
            st.rerun()
    
    with col2:
        if st.button("🗑️ Remove Content", use_container_width=True):
            db.update_queue_status(
                item['queue_id'],
                status='reviewed',
                reviewer='moderator',
                decision='removed',
                notes='Removed after review'
            )
            st.success("🗑️ Content removed")
            st.session_state.selected_content = None
            st.rerun()
    
    with col3:
        if st.button("🚨 Escalate", use_container_width=True):
            db.update_queue_status(
                item['queue_id'],
                status='escalated',
                reviewer='moderator',
                decision='escalated',
                notes='Escalated to senior moderator'
            )
            st.success("🚨 Escalated")
            st.session_state.selected_content = None
            st.rerun()


def main():
    """Main dashboard"""
    
    # Check if viewing detail
    if st.session_state.selected_content:
        render_detail_modal(st.session_state.selected_content)
        return
    
    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem;">
        <div>
            <h1 style="margin: 0;">🛡️ HarmLens Moderator Dashboard</h1>
            <p style="margin: 0.5rem 0 0 0; color: #94a3b8;">
                REAL moderation queue - see actual flagged content and take action
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get stats
    stats = get_queue_stats()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyzed", stats['total_analyzed'])
    
    with col2:
        pending = stats['pending_review']
        delta_text = "⚠️ Needs attention" if pending > 0 else ""
        st.metric("Pending Review", pending, delta=delta_text)
    
    with col3:
        high_risk = stats['high_risk']
        priority_text = "🚨 Priority" if stats['priority_count'] > 0 else ""
        st.metric("High Risk", high_risk, delta=priority_text)
    
    with col4:
        st.metric("Avg Response Time", f"{stats['avg_time']:.0f}ms")
    
    st.divider()
    
    # Queue tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🚨 Priority Review Queue ({stats['priority_count']})",
        f"👶 Child Safety Queue ({stats['child_count']})",
        f"⚠️ Medium Priority ({stats['medium_count']})",
        "✅ Reviewed"
    ])
    
    with tab1:
        st.markdown("### Priority Review Queue")
        st.caption("High-risk content requiring immediate human review")
        
        priority_items = db.get_queue_items("Priority Review Queue", "pending")
        
        if not priority_items:
            st.markdown("""
            <div class="empty-queue">
                <h3>✅ Queue is empty - no priority items pending</h3>
                <p>All high-risk content has been reviewed</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for item in priority_items:
                render_content_card(item, "priority")
    
    with tab2:
        st.markdown("### Child Safety Queue")
        st.caption("Content flagged for child safety concerns")
        
        child_items = db.get_queue_items("Child Safety", "pending")
        
        if not child_items:
            st.markdown("""
            <div class="empty-queue">
                <h3>✅ Queue is empty - no child safety items pending</h3>
                <p>No child safety concerns detected</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for item in child_items:
                render_content_card(item, "child_safety")
    
    with tab3:
        st.markdown("### Medium Priority")
        st.caption("Automated + sampling review queue")
        
        medium_items = db.get_queue_items("Automated + Sampling Review", "pending")
        
        if not medium_items:
            st.markdown("""
            <div class="empty-queue">
                <h3>✅ Queue is empty - no medium priority items pending</h3>
                <p>All medium-risk content has been processed</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for item in medium_items:
                render_content_card(item, "medium")
    
    with tab4:
        st.markdown("### Reviewed Content")
        st.caption("Previously reviewed items")
        
        # Get reviewed items from all queues
        reviewed_items = []
        for queue_name in ["Priority Review Queue", "Child Safety", "Automated + Sampling Review"]:
            reviewed_items.extend(db.get_queue_items(queue_name, "reviewed"))
        
        if not reviewed_items:
            st.info("No reviewed items yet")
        else:
            # Show as table
            df_data = []
            for item in reviewed_items[:50]:  # Show last 50
                df_data.append({
                    "Content ID": item.get('content_id', 'N/A')[:20] + "...",
                    "Risk": f"{item.get('risk_label', 'N/A')} ({item.get('risk_score', 0)})",
                    "Decision": item.get('decision', 'N/A'),
                    "Reviewer": item.get('reviewer', 'N/A'),
                    "Time": item.get('reviewed_at', 'N/A')[:19] if item.get('reviewed_at') else 'N/A'
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
