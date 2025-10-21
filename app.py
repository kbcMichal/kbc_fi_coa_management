"""
Professional COA Management App with Keboola Branding
Main application entry point with Hydralit navigation
"""

import streamlit as st
import streamlit_nested_layout
import hydralit_components as hc
import pandas as pd
from pages.coa_editor import show_coa_metrics, show_hierarchy_view, show_search_filter, show_edit_data, show_add_new_item, display_hierarchy_item
from pages.coa_import_export import show_coa_import_export
from pages.analytics import show_analytics
from pages.coa_transformation import show_coa_transformation
from utils.coa_data_manager import COADataManager

# Configure page
st.set_page_config(
    page_title="COA Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize data manager
data_manager = COADataManager()

def main():
    """Main application function"""
    
    # Create navigation menu
    menu_data = [
        {'label': "Import/Export"},
        {'label': "Transform"},
        {'label': "Analytics"},
    ]
    
    # Create Hydralit navigation
    menu_id = hc.nav_bar(
        menu_definition=menu_data,
        override_theme={
            'txc_inactive': '#FFFFFF',
            'menu_background': '#297cf7',
            'txc_active': '#000000',
            'option_active': '#FFFFFF'
        },
        home_name='Editor',
        login_name=None,
        hide_streamlit_markers=True,
        sticky_nav=True,
        sticky_mode='pinned'
    )
    
    # Route to appropriate page
    if menu_id == "Editor" or menu_id is None:
        show_merged_editor(data_manager)
    elif menu_id == "Import/Export":
        show_coa_import_export(data_manager)
    elif menu_id == "Transform":
        show_coa_transformation(data_manager)
    elif menu_id == "Analytics":
        show_analytics(data_manager)
    elif menu_id == "Settings":
        show_settings()
    else:
        # Default to Editor for any other navigation
        show_merged_editor(data_manager)

def show_account_hierarchy(data_manager: COADataManager, account_code: str, business_unit: str = None, fin_statement: str = None):
    """Show complete hierarchy for a specific account (including all sub-children)"""
    
    # Ensure data is loaded
    if data_manager.data is None or data_manager.data.empty:
        with st.spinner("Loading COA data..."):
            data_manager.load_coa_data()
    
    # Get the account details
    df = data_manager.data
    if df is None or df.empty:
        st.error("No data available")
        return
    
    # Filter to the specific business unit and financial statement
    if business_unit and fin_statement:
        df = df[(df['FK_BUSINESS_UNIT'] == business_unit) & (df['TYPE_FIN_STATEMENT'] == fin_statement)]
    
    # Find the selected account
    selected_account = df[df['CODE_FIN_STAT'] == account_code]
    if selected_account.empty:
        st.warning(f"Account {account_code} not found")
        return
    
    account_info = selected_account.iloc[0]
    
    # Get the complete hierarchical structure starting from this account
    hierarchy = data_manager.get_hierarchical_structure(business_unit, fin_statement)
    
    if not hierarchy or account_code not in hierarchy:
        st.info("This account has no child accounts.")
        return
    
    # Display the complete hierarchy using the same format as the original
    st.markdown(f"**Hierarchy for {account_info['CODE_FIN_STAT']} - {account_info['NAME_FIN_STAT']}:**")
    
    # Use the same display function as the original hierarchy view
    display_hierarchy_item(hierarchy[account_code], 0, "", data_manager)

def show_merged_editor(data_manager: COADataManager):
    """Merged editor that combines dashboard and editor functionality"""
    # Check if force reload is requested
    if st.session_state.get('force_reload', False):
        st.session_state['force_reload'] = False
        if 'coa_grid' in st.session_state:
            del st.session_state['coa_grid']
        try:
            st.cache_data.clear()
        except Exception:
            pass
    
    # Custom CSS for button alignment
    st.markdown("""
    <style>
    .stButton > button {
        height: 38px !important;
        vertical-align: top !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        height: 38px !important;
        vertical-align: top !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1e5bb8 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Status and controls
    top_col1, top_col2, top_col3 = st.columns([1, 1, 6])
    
    # Show unsaved changes indicator
    if st.session_state.get('has_unsaved_changes', False):
        st.warning("⚠️ You have unsaved changes")
    
    # Show refresh confirmation warning
    if st.session_state.get('confirm_refresh', False):
        st.error("⚠️ You have unsaved changes! Refreshing will lose all unconfirmed changes. Click Refresh again to confirm.")
    
    with top_col1:
        if st.button("🔄 Refresh from Keboola"):
            # Check for unsaved changes
            if st.session_state.get('has_unsaved_changes', False):
                if not st.session_state.get('confirm_refresh', False):
                    st.session_state['confirm_refresh'] = True
                    st.rerun()
                else:
                    # User confirmed, proceed with refresh
                    st.session_state['confirm_refresh'] = False
                    # Clear all session state and force reload
                    for key in ['data_loaded', 'coa_original_data', 'coa_working_data', 'has_unsaved_changes', 'confirm_refresh']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.session_state['force_reload'] = True
                    try:
                        st.cache_data.clear()
                    except Exception:
                        pass
                    st.rerun()
            else:
                # No unsaved changes, proceed with refresh
                # Clear all session state and force reload
                for key in ['data_loaded', 'coa_original_data', 'coa_working_data', 'has_unsaved_changes', 'confirm_refresh']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state['force_reload'] = True
                try:
                    st.cache_data.clear()
                except Exception:
                    pass
                st.rerun()
    
    with top_col2:
        
        if st.button("💾 Save to Keboola", type="primary", disabled=not st.session_state.get('has_unsaved_changes', False)):
            st.error("❌ Save to Keboola functionality is not implemented yet")
            # TODO: Implement actual save to Keboola
            # For now, just mark as saved
            st.session_state['has_unsaved_changes'] = False
            st.success("✅ Changes saved to session (Keboola save pending)")

    # Load only once per session unless refresh requested
    if 'data_loaded' not in st.session_state or st.session_state.get('force_reload', False):
        with st.spinner("Loading COA data from Keboola..."):
            try:
                data_manager.load_coa_data()
                # Only mark as loaded if data is actually available
                if data_manager.data is not None and not data_manager.data.empty:
                    st.session_state['data_loaded'] = True
                    # Store the original data and create a working copy
                    st.session_state['coa_original_data'] = data_manager.data.copy()
                    st.session_state['coa_working_data'] = data_manager.data.copy()
                    st.session_state['has_unsaved_changes'] = False
                else:
                    st.error("Failed to load data from Keboola - no data returned")
                    return
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                st.exception(e)
                return
        st.session_state['force_reload'] = False
    
    # Restore working data from session state if available
    if 'coa_working_data' in st.session_state and st.session_state['coa_working_data'] is not None:
        data_manager.data = st.session_state['coa_working_data']
    elif 'coa_original_data' in st.session_state and st.session_state['coa_original_data'] is not None:
        # Fallback to original data if working data is not available
        data_manager.data = st.session_state['coa_original_data']
    
    # Get all data
    df = data_manager.data
    
    if df is None or df.empty:
        st.error("No data available")
        return
    
    # All filters on one line
    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1, 1])
    
    with col1:
        # Business Unit Selector
        business_units = sorted(df['FK_BUSINESS_UNIT'].unique().tolist())
        selected_bu = st.selectbox(
            "Business Unit:",
            options=business_units,
            help="Choose a business unit to edit its Chart of Accounts"
        )
    
    with col2:
        # Financial Statement Type Selector
        fin_statements = sorted(df['TYPE_FIN_STATEMENT'].unique().tolist())
        selected_fin_stmt = st.selectbox(
            "Statement:",
            options=fin_statements,
            help="Choose a financial statement type (BS=Balance Sheet, PL=Profit & Loss)"
        )
    
    with col3:
        # Searchable dropdown for account selection
        # Get all unique account names for the dropdown, sorted by name for easier searching
        account_options = df[['CODE_FIN_STAT', 'NAME_FIN_STAT']].drop_duplicates()
        account_options = account_options.sort_values('NAME_FIN_STAT')
        account_options['display_name'] = account_options['CODE_FIN_STAT'] + ' - ' + account_options['NAME_FIN_STAT']
        account_list = [''] + account_options['display_name'].tolist()
        
        selected_account_display = st.selectbox(
            "Search Account:",
            options=account_list,
            help="Start typing to search for accounts. Select an account to view its hierarchy.",
            index=0,
            placeholder="Type to search accounts..."
        )
        
        # Extract the account code from the selected display name
        if selected_account_display and selected_account_display != '':
            selected_account_code = selected_account_display.split(' - ')[0]
        else:
            selected_account_code = None
    
    with col4:
        # Account Type Filter
        account_types = ["All"] + sorted(df['TYPE_ACCOUNT'].unique().tolist())
        selected_account_type = st.selectbox(
            "Type:",
            options=account_types,
            help="Filter by account type"
        )
    
    with col5:
        # Hierarchy Level Filter
        if 'HIERARCHY_LEVEL' in df.columns:
            hierarchy_levels = ["All"] + [str(int(x)) for x in sorted(df['HIERARCHY_LEVEL'].unique()) if pd.notna(x)]
            selected_hierarchy = st.selectbox(
                "Level:",
                options=hierarchy_levels,
                help="Filter by hierarchy level"
            )
        else:
            selected_hierarchy = "All"
    
    # Filter data by selected business unit and financial statement
    df = df[(df['FK_BUSINESS_UNIT'] == selected_bu) & (df['TYPE_FIN_STATEMENT'] == selected_fin_stmt)].copy()
    
    # Sort by order column for proper display
    if 'NUM_FIN_STAT_ORDER' in df.columns:
        df = df.sort_values('NUM_FIN_STAT_ORDER', na_position='last')
    
    # Show selected account info and hierarchy
    if selected_account_code:
        # Find the selected account details
        selected_account = df[df['CODE_FIN_STAT'] == selected_account_code]
        if not selected_account.empty:
            account_info = selected_account.iloc[0]
            st.success(f"Selected: {account_info['CODE_FIN_STAT']} - {account_info['NAME_FIN_STAT']}")
            
            # Show account details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Account Code", account_info['CODE_FIN_STAT'])
            with col2:
                st.metric("Account Type", account_info['TYPE_ACCOUNT'])
            with col3:
                st.metric("Statement Type", account_info['TYPE_FIN_STATEMENT'])
            
            # Show hierarchy for this specific account
            st.markdown("### Account Hierarchy")
            show_account_hierarchy(data_manager, selected_account_code, business_unit=selected_bu, fin_statement=selected_fin_stmt)
        else:
            st.warning(f"Account {selected_account_code} not found in the current selection.")
    
    # Show hierarchy view with integrated editing (only if no specific account selected)
    if not selected_account_code:
        show_hierarchy_view(data_manager, selected_bu, selected_fin_stmt)

def show_settings():
    """Settings page"""
    st.title("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Display Settings")
        st.checkbox("Dark Mode", value=False)
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
        
    with col2:
        st.subheader("Data Settings")
        st.number_input("Max Rows", value=1000, min_value=100, max_value=10000)
        st.checkbox("Auto-save", value=True)

if __name__ == "__main__":
    main()
