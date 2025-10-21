"""
Analytics page with modern visualizations and insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import altair as alt
from utils.coa_data_manager import COADataManager

def show_analytics(data_manager: COADataManager):
    """Display the modern analytics page"""
    
    # Load data if not already loaded
    if data_manager.data is None:
        with st.spinner("Loading data..."):
            data_manager.load_coa_data()
    
    df = data_manager.get_flat_data()
    
    # Add visualization library selector
    st.sidebar.markdown("### Visualization Options")
    viz_library = st.sidebar.selectbox(
        "Choose Visualization Library:",
        ["Plotly (Modern)", "Altair (Minimalist)"],
        help="Select your preferred visualization style"
    )
    
    # Single analytics view
    show_modern_overview_analytics(df, viz_library)

def show_modern_overview_analytics(df, viz_library):
    """Show modern overview analytics with contemporary styling"""
    
    st.markdown("## Data Overview")
    
    # Modern metrics cards with custom styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_accounts = len(df)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0; font-size: 0.875rem; font-weight: 500; opacity: 0.9;">Total Accounts</h3>
            <h1 style="margin: 0.5rem 0; font-size: 2rem; font-weight: 700;">{total_accounts:,}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        balance_sheet = len(df[df['TYPE_FIN_STATEMENT'] == 'BS'])
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0; font-size: 0.875rem; font-weight: 500; opacity: 0.9;">Balance Sheet</h3>
            <h1 style="margin: 0.5rem 0; font-size: 2rem; font-weight: 700;">{balance_sheet:,}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        profit_loss = len(df[df['TYPE_FIN_STATEMENT'] == 'PL'])
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0; font-size: 0.875rem; font-weight: 500; opacity: 0.9;">Profit & Loss</h3>
            <h1 style="margin: 0.5rem 0; font-size: 2rem; font-weight: 700;">{profit_loss:,}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        max_level = df['HIERARCHY_LEVEL'].max() if 'HIERARCHY_LEVEL' in df.columns else 0
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0; font-size: 0.875rem; font-weight: 500; opacity: 0.9;">Max Hierarchy Level</h3>
            <h1 style="margin: 0.5rem 0; font-size: 2rem; font-weight: 700;">{max_level}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Modern distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Account type distribution with modern styling
        type_counts = df['TYPE_ACCOUNT'].value_counts()
        
        if viz_library == "Plotly (Modern)":
            fig_pie = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Account Type Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(
                font=dict(family="Inter, sans-serif", size=12),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            # Altair version
            type_data = pd.DataFrame({
                'Account_Type': type_counts.index,
                'Count': type_counts.values
            })
            chart = alt.Chart(type_data).mark_arc(
                innerRadius=50,
                stroke='white',
                strokeWidth=2
            ).encode(
                theta=alt.Theta('Count:Q'),
                color=alt.Color('Account_Type:N', scale=alt.Scale(range=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'])),
                tooltip=['Account_Type:N', 'Count:Q']
            ).properties(
                title="Account Type Distribution",
                width=400,
                height=300
            )
            st.altair_chart(chart, use_container_width=True)
    
    with col2:
        # Financial statement distribution
        statement_counts = df['TYPE_FIN_STATEMENT'].value_counts()
        
        if viz_library == "Plotly (Modern)":
            fig_bar = px.bar(
                x=statement_counts.index,
                y=statement_counts.values,
                title="Financial Statement Distribution",
                color=statement_counts.index,
                color_discrete_sequence=['#667eea', '#764ba2']
            )
            fig_bar.update_layout(
                font=dict(family="Inter, sans-serif", size=12),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0),
                showlegend=False,
                hovermode='closest'
            )
            fig_bar.update_traces(
                marker=dict(line=dict(width=0), opacity=0.8),
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            # Altair version
            statement_data = pd.DataFrame({
                'Statement_Type': statement_counts.index,
                'Count': statement_counts.values
            })
            chart = alt.Chart(statement_data).mark_bar(
                cornerRadius=4,
                stroke='white',
                strokeWidth=1
            ).encode(
                x=alt.X('Statement_Type:N', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Count:Q'),
                color=alt.Color('Statement_Type:N', scale=alt.Scale(range=['#667eea', '#764ba2']))
            ).properties(
                title="Financial Statement Distribution",
                width=400,
                height=300
            )
            st.altair_chart(chart, use_container_width=True)
    
    # Modern hierarchy analysis
    st.markdown("## Hierarchy Analysis")
    
    if 'HIERARCHY_LEVEL' in df.columns:
        level_counts = df['HIERARCHY_LEVEL'].value_counts().sort_index()
        
        if viz_library == "Plotly (Modern)":
            fig_hierarchy = px.bar(
                x=level_counts.index,
                y=level_counts.values,
                title="Accounts by Hierarchy Level",
                color=level_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_hierarchy.update_layout(
                font=dict(family="Inter, sans-serif", size=12),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=40, b=0),
                showlegend=False
            )
            fig_hierarchy.update_traces(
                marker=dict(line=dict(width=0), opacity=0.8),
                hovertemplate='<b>Level %{x}</b><br>Count: %{y}<extra></extra>'
            )
            st.plotly_chart(fig_hierarchy, use_container_width=True)
        else:
            # Altair version
            level_data = pd.DataFrame({
                'Level': level_counts.index,
                'Count': level_counts.values
            })
            chart = alt.Chart(level_data).mark_bar(
                cornerRadius=4,
                stroke='white',
                strokeWidth=1
            ).encode(
                x=alt.X('Level:O', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Count:Q'),
                color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis'))
            ).properties(
                title="Accounts by Hierarchy Level",
                width=400,
                height=300
            )
            st.altair_chart(chart, use_container_width=True)

def count_children_by_parent(df, parent_code):
    """Count children for a given parent code"""
    if 'CODE_PARENT_FIN_STAT' in df.columns:
        return len(df[df['CODE_PARENT_FIN_STAT'] == parent_code])
    return 0


# Legacy functions kept for backward compatibility
def show_overview_analytics(df):
    """Legacy overview analytics - use show_modern_overview_analytics instead"""
    return show_modern_overview_analytics(df, "Plotly (Modern)")

def show_hierarchy_analytics(df):
    """Legacy hierarchy analytics - simplified version"""
    st.markdown("## Hierarchy Analysis")
    if 'HIERARCHY_LEVEL' in df.columns:
        level_counts = df['HIERARCHY_LEVEL'].value_counts().sort_index()
        fig = px.bar(
            x=level_counts.index,
            y=level_counts.values,
            title="Accounts by Hierarchy Level"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hierarchy level data available")

def show_trend_analytics(df):
    """Legacy trend analytics - simplified version"""
    st.markdown("## COA Structure Analysis")
    if 'TYPE_ACCOUNT' in df.columns:
        account_type_stats = df.groupby('TYPE_ACCOUNT').agg({
            'CODE_FIN_STAT': 'count'
        }).round(2)
        account_type_stats.columns = ['Account_Count']
        account_type_stats = account_type_stats.reset_index()
        
        fig = px.bar(
            account_type_stats,
            x='TYPE_ACCOUNT',
            y='Account_Count',
            title="Account Distribution by Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No account type data available")

def show_insights_analytics(df):
    """Legacy insights analytics - simplified version"""
    st.markdown("## Data Insights")
    insights = generate_insights(df)
    
    for i, insight in enumerate(insights, 1):
        with st.expander(f"Insight {i}: {insight['title']}", expanded=True):
            st.write(insight['description'])
            if 'recommendations' in insight:
                st.write("**Recommendations:**")
                for rec in insight['recommendations']:
                    st.write(f"• {rec}")

def calculate_hierarchy_depth(df, root_id, current_depth=0):
    """Calculate the maximum depth of a hierarchy starting from root_id"""
    children = df[df['parent_id'] == root_id]
    if children.empty:
        return current_depth
    
    max_child_depth = current_depth
    for _, child in children.iterrows():
        child_depth = calculate_hierarchy_depth(df, child['id'], current_depth + 1)
        max_child_depth = max(max_child_depth, child_depth)
    
    return max_child_depth

def count_children(df, parent_id):
    """Count total number of children (including grandchildren)"""
    children = df[df['parent_id'] == parent_id]
    total = len(children)
    
    for _, child in children.iterrows():
        total += count_children(df, child['id'])
    
    return total

def sum_children_values(df, parent_id):
    """Sum values of all children"""
    children = df[df['parent_id'] == parent_id]
    total = children['value'].sum()
    
    for _, child in children.iterrows():
        total += sum_children_values(df, child['id'])
    
    return total

def generate_insights(df):
    """Generate data insights and recommendations"""
    insights = []
    
    # Insight 1: Hierarchy depth analysis
    if 'HIERARCHY_LEVEL' in df.columns:
        max_depth = df['HIERARCHY_LEVEL'].max()
        avg_depth = df['HIERARCHY_LEVEL'].mean()
        
        insights.append({
            'title': 'Hierarchy Structure Analysis',
            'description': f'Your COA has a maximum depth of {max_depth} levels with an average depth of {avg_depth:.1f} levels.',
            'recommendations': [
                'Consider flattening the hierarchy if depth exceeds 5 levels',
                'Review parent-child relationships for consistency',
                'Ensure proper account classification at each level'
            ]
        })
    
    # Insight 2: Account type distribution
    if 'TYPE_ACCOUNT' in df.columns:
        account_dist = df['TYPE_ACCOUNT'].value_counts()
        total_accounts = len(df)
        
        insights.append({
            'title': 'Account Type Distribution',
            'description': f'Your COA contains {total_accounts} accounts distributed across {len(account_dist)} account types.',
            'recommendations': [
                'Ensure balanced distribution across account types',
                'Review account type classifications for accuracy',
                'Consider adding missing account types if needed'
            ]
        })
    
    # Insight 3: Financial statement balance
    if 'TYPE_FIN_STATEMENT' in df.columns:
        statement_dist = df['TYPE_FIN_STATEMENT'].value_counts()
        bs_count = statement_dist.get('BS', 0)
        pl_count = statement_dist.get('PL', 0)
        
        insights.append({
            'title': 'Financial Statement Balance',
            'description': f'Your COA has {bs_count} Balance Sheet accounts and {pl_count} Profit & Loss accounts.',
            'recommendations': [
                'Ensure proper balance between BS and PL accounts',
                'Review account classifications for accuracy',
                'Consider adding missing account types if needed'
            ]
        })
    
    # Insight 4: Parent-child relationships
    if 'CODE_PARENT_FIN_STAT' in df.columns:
        parent_count = len(df[df['CODE_PARENT_FIN_STAT'].notna() & (df['CODE_PARENT_FIN_STAT'] != '')])
        orphan_count = len(df[df['CODE_PARENT_FIN_STAT'].isna() | (df['CODE_PARENT_FIN_STAT'] == '')])
        
        insights.append({
            'title': 'Hierarchy Structure',
            'description': f'Your COA has {parent_count} child accounts and {orphan_count} root accounts.',
            'recommendations': [
                'Ensure all accounts have proper parent-child relationships',
                'Review orphan accounts for proper classification',
                'Maintain consistent hierarchy structure'
            ]
        })
    
    return insights
