"""
COA Editor with validation, audit trail, and role-based access
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.coa_data_manager import COADataManager
from datetime import datetime
from typing import Dict, List, Any
import io
import json

# Keboola brand colors
KEBOOLA_PRIMARY = "#297cf7"
KEBOOLA_DARK = "#08255a"
KEBOOLA_LIGHT = "#e6f2ff"

def apply_keboola_theme():
    """Apply Keboola theme to the editor"""
    st.markdown(f"""
    <style>
    .main {{
        background-color: white;
    }}
    .stApp {{
        background-color: white;
    }}
    .keboola-editor {{
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .validation-error {{
        background-color: #ffebee;
        border: 1px solid #f44336;
        border-radius: 4px;
        padding: 8px;
        margin: 4px 0;
    }}
    .validation-success {{
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 4px;
        padding: 8px;
        margin: 4px 0;
    }}
    </style>
    """, unsafe_allow_html=True)


def show_edit_data(df: pd.DataFrame, data_manager: COADataManager):
    """Show interface for editing existing COA data with Edit buttons"""
    
    st.subheader("Edit COA Data")
    
    if df.empty:
        st.info("No data to display. Please select a business unit or add some data.")
        return
    
    # Display data in a simple table with Edit buttons
    for idx, row in df.iterrows():
        with st.expander(f"**{row['CODE_FIN_STAT']}** - {row['NAME_FIN_STAT']} ({row['TYPE_ACCOUNT']}/{row['TYPE_FIN_STATEMENT']})"):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**Code:** {row['CODE_FIN_STAT']}")
                st.write(f"**Name:** {row['NAME_FIN_STAT']}")
                st.write(f"**Parent:** {row.get('CODE_PARENT_FIN_STAT', 'N/A')}")
                st.write(f"**Type:** {row['TYPE_ACCOUNT']} | **Statement:** {row['TYPE_FIN_STATEMENT']}")
                if row.get('NAME_FIN_STAT_ENG'):
                    st.write(f"**English Name:** {row['NAME_FIN_STAT_ENG']}")
                st.write(f"**Order:** {row.get('NUM_FIN_STAT_ORDER', 'N/A')}")
                st.write(f"**Business Unit:** {row.get('FK_BUSINESS_UNIT', 'N/A')}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{row['CODE_FIN_STAT']}"):
                    st.session_state[f"show_edit_account_{row['CODE_FIN_STAT']}"] = True
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{row['CODE_FIN_STAT']}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{row['CODE_FIN_STAT']}", False):
                        # Actually delete the item
                        success = data_manager.delete_coa_item(row['CODE_FIN_STAT'], user="current_user")
                        if success:
                            st.success(f"✅ Account '{row['CODE_FIN_STAT']}' deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete account")
                    else:
                        st.session_state[f"confirm_delete_{row['CODE_FIN_STAT']}"] = True
                        st.warning("⚠️ Click Delete again to confirm")
                        st.rerun()
    
    # Show editing instructions
    st.info("💡 **Editing Instructions:**\n"
            "- Click 'Edit' to modify account details in a popup\n"
            "- Click 'Delete' twice to remove an account\n"
            "- Changes are validated before saving")

def show_add_new_item(data_manager: COADataManager, business_unit: str = None):
    """Show interface for adding new COA items"""
    
    # Add custom CSS for blue buttons (including form submit buttons)
    st.markdown("""
    <style>
    .stButton > button, 
    .stFormSubmitButton > button,
    button[kind="primary"],
    button[type="submit"] {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    button[kind="primary"]:hover,
    button[type="submit"]:hover {
        background-color: #1e5bb8 !important;
    }
    
    /* Hide "Press Enter to submit form" message */
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.subheader("Add New COA Item")
    
    # Show persistent success message if item was added
    if st.session_state.get('item_added', False):
        st.success(f"✅ COA item '{st.session_state.get('added_item_code', '')}' added successfully!")
        # Clear the session state after showing the message
        st.session_state['item_added'] = False
        st.session_state['added_item_code'] = ''
    
    with st.form("add_coa_item_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            code = st.text_input("Code *", placeholder="e.g., BSA12345", help="Unique account code")
            name = st.text_input("Name *", placeholder="Account name", help="Account name in local language")
            parent_code = st.text_input("Parent Code", placeholder="e.g., BSA99999", help="Parent account code (optional)")
            type_account = st.selectbox("Account Type *", ["A", "P", "R", "C"], 
                                       help="A=Assets, P=Liabilities/Equity, R=Revenue, C=Cost")
        
        with col2:
            type_fin_statement = st.selectbox("Statement Type *", ["BS", "PL"],
                                            help="BS=Balance Sheet, PL=Profit & Loss")
            name_eng = st.text_input("English Name", placeholder="Account name in English")
            order = st.number_input("Order", min_value=0, value=1000, step=100,
                                  help="Order number (use hundreds apart for easy insertion)")
            bu = st.text_input("Business Unit", value=business_unit or "DEFAULT", 
                              help="Business unit identifier")
        
        # Submit button
        submitted = st.form_submit_button("Add COA Item", type="primary")
        
        if submitted:
            if code and name and type_account and type_fin_statement:
                # Create new item data
                new_item = {
                    'CODE_FIN_STAT': code,
                    'NAME_FIN_STAT': name,
                    'CODE_PARENT_FIN_STAT': parent_code if parent_code else None,
                    'TYPE_ACCOUNT': type_account,
                    'TYPE_FIN_STATEMENT': type_fin_statement,
                    'NAME_FIN_STAT_ENG': name_eng if name_eng else None,
                    'NUM_FIN_STAT_ORDER': order,
                    'FK_BUSINESS_UNIT': bu
                }
                
                # Add to data manager
                success = data_manager.add_coa_item(new_item, user="current_user")
                if success:
                    st.success(f"✅ COA item '{code}' added successfully!")
                    # Use session state to show persistent message
                    st.session_state['item_added'] = True
                    st.session_state['added_item_code'] = code
                else:
                    st.error("❌ Failed to add COA item")
            else:
                st.error("❌ Please fill in all required fields (marked with *)")


def show_validation_results(df: pd.DataFrame, data_manager: COADataManager):
    """Show COA validation results"""
    
    st.subheader("COA Validation Results")
    
    # Run validation
    errors = data_manager.validate_coa_rules(df)
    
    if errors:
        st.error(f"❌ Found {len(errors)} validation errors:")
        for i, error in enumerate(errors, 1):
            st.error(f"{i}. {error}")
    else:
        st.success("✅ All validation rules passed!")
    
    # Show validation rules
    st.markdown("### Validation Rules")
    
    rules = [
        "**Rule 1:** Balance Sheet accounts (A, P) must have TYPE_FIN_STATEMENT = 'BS'",
        "**Rule 2:** Profit & Loss accounts (R, C) must have TYPE_FIN_STATEMENT = 'PL'",
        "**Rule 3:** No duplicate codes within business unit",
        "**Rule 4:** No orphaned parent references",
        "**Rule 5:** All required fields must be filled"
    ]
    
    for rule in rules:
        st.write(rule)
    
    # Show data quality metrics
    st.markdown("### 📈 Data Quality Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_items = len(df)
        st.metric("Total Items", total_items)
    
    with col2:
        missing_names = df['NAME_FIN_STAT'].isna().sum()
        st.metric("Missing Names", missing_names)
    
    with col3:
        missing_codes = df['CODE_FIN_STAT'].isna().sum()
        st.metric("Missing Codes", missing_codes)

def show_audit_trail(data_manager: COADataManager):
    """Show audit trail of changes"""
    
    st.subheader("Audit Trail")
    
    audit_log = data_manager.get_audit_log()
    
    if not audit_log:
        st.info("No audit entries found")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        action_filter = st.selectbox("Filter by Action", ["All", "ADD", "UPDATE", "DELETE"])
    
    with col2:
        code_filter = st.text_input("Filter by Code", placeholder="Enter account code")
    
    # Apply filters
    filtered_log = audit_log.copy()
    
    if action_filter != "All":
        filtered_log = [entry for entry in filtered_log if entry['action'] == action_filter]
    
    if code_filter:
        filtered_log = [entry for entry in filtered_log if code_filter.lower() in entry['code'].lower()]
    
    # Display audit entries
    st.write(f"**Showing {len(filtered_log)} audit entries**")
    
    for entry in filtered_log[-20:]:  # Show last 20 entries
        with st.expander(f"{entry['action']} - {entry['code']} - {entry['timestamp']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Action:** {entry['action']}")
                st.write(f"**Code:** {entry['code']}")
                st.write(f"**User:** {entry['user']}")
                st.write(f"**Timestamp:** {entry['timestamp']}")
            
            with col2:
                if entry['new_values']:
                    st.write("**New Values:**")
                    for key, value in entry['new_values'].items():
                        st.write(f"- {key}: {value}")
                
                if entry['old_values']:
                    st.write("**Old Values:**")
                    for key, value in entry['old_values'].items():
                        st.write(f"- {key}: {value}")

# Dashboard functions merged from coa_dashboard.py

def show_coa_metrics(df: pd.DataFrame):
    """Display COA key metrics"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_accounts = len(df)
        st.metric("Total Accounts", total_accounts)
    
    with col2:
        balance_sheet = len(df[df['TYPE_FIN_STATEMENT'] == 'BS'])
        st.metric("Balance Sheet", balance_sheet)
    
    with col3:
        profit_loss = len(df[df['TYPE_FIN_STATEMENT'] == 'PL'])
        st.metric("Profit & Loss", profit_loss)
    
    with col4:
        max_level = df['HIERARCHY_LEVEL'].max() if 'HIERARCHY_LEVEL' in df.columns else 0
        st.metric("Max Hierarchy Level", max_level)
    
    with col5:
        root_accounts = len(df[df['CODE_PARENT_FIN_STAT'].isna() | (df['CODE_PARENT_FIN_STAT'] == '')])
        st.metric("Root Accounts", root_accounts)

def show_hierarchy_view(data_manager: COADataManager, business_unit: str = None, fin_statement: str = None):
    """Display hierarchical structure with drill-down"""
    
    # Ensure data is loaded
    if data_manager.data is None or data_manager.data.empty:
        with st.spinner("Loading COA data..."):
            data_manager.load_coa_data()
    
    # Get hierarchical structure
    hierarchy = data_manager.get_hierarchical_structure(business_unit, fin_statement)
    
    if not hierarchy:
        st.warning("No hierarchical data available")
        # Debug information
        if data_manager.data is not None:
            st.write(f"Data loaded: {len(data_manager.data)} rows")
            st.write(f"Columns: {list(data_manager.data.columns)}")
            if 'CODE_PARENT_FIN_STAT' in data_manager.data.columns:
                root_items = data_manager.data[(data_manager.data['CODE_PARENT_FIN_STAT'] == 'BS') | data_manager.data['CODE_PARENT_FIN_STAT'].isna() | (data_manager.data['CODE_PARENT_FIN_STAT'] == '')]
                st.write(f"Root items found: {len(root_items)}")
                if len(root_items) > 0:
                    st.write("Root items:", root_items[['CODE_FIN_STAT', 'NAME_FIN_STAT', 'CODE_PARENT_FIN_STAT']].head())
        return
    
    # Display hierarchy with drill-down
    for root_code, root_data in hierarchy.items():
        display_hierarchy_item(root_data, 0, "", data_manager)
    
    # Handle popups - use a single dialog state to prevent conflicts
    if 'active_dialog' not in st.session_state:
        st.session_state.active_dialog = None
    
    # Check for any popup requests
    for root_code, root_data in hierarchy.items():
        # Check for add child popup
        if st.session_state.get(f"show_add_child_{root_code}", False):
            st.session_state.active_dialog = f"add_child_{root_code}"
            show_add_child_popup(root_code, data_manager)
            break
        
        # Check for edit popup
        if st.session_state.get(f"show_edit_account_{root_code}", False):
            st.session_state.active_dialog = f"edit_account_{root_code}"
            show_edit_account_popup(root_code, data_manager)
            break
        
        # Check for delete confirmation popup
        if st.session_state.get(f"show_delete_confirm_{root_code}", False):
            st.session_state.active_dialog = f"delete_confirm_{root_code}"
            show_delete_confirmation_popup(root_code, data_manager)
            break
        
        # Check all children recursively for both popup types
        def check_children_for_popup(item_data, parent_path=""):
            data = item_data['data']
            children = item_data['children']
            current_path = f"{parent_path}/{data['CODE_FIN_STAT']}" if parent_path else data['CODE_FIN_STAT']
            
            # Check for add child popup
            if st.session_state.get(f"show_add_child_{data['CODE_FIN_STAT']}", False):
                st.session_state.active_dialog = f"add_child_{data['CODE_FIN_STAT']}"
                show_add_child_popup(data['CODE_FIN_STAT'], data_manager)
                return True
            
            # Check for edit popup
            if st.session_state.get(f"show_edit_account_{data['CODE_FIN_STAT']}", False):
                st.session_state.active_dialog = f"edit_account_{data['CODE_FIN_STAT']}"
                show_edit_account_popup(data['CODE_FIN_STAT'], data_manager)
                return True
            
            # Check for delete confirmation popup
            if st.session_state.get(f"show_delete_confirm_{data['CODE_FIN_STAT']}", False):
                st.session_state.active_dialog = f"delete_confirm_{data['CODE_FIN_STAT']}"
                show_delete_confirmation_popup(data['CODE_FIN_STAT'], data_manager)
                return True
            
            for child_data in children:
                if check_children_for_popup(child_data, current_path):
                    return True
            return False
        
        if check_children_for_popup(root_data):
            break

def display_hierarchy_item(item_data: Dict, level: int, parent_path: str = "", data_manager: COADataManager = None):
    """Recursively display hierarchy item with drill-down"""
    
    data = item_data['data']
    children = item_data['children']
    
    # Display current item
    current_path = f"{parent_path}/{data['CODE_FIN_STAT']}" if parent_path else data['CODE_FIN_STAT']
    
    # Create expandable section for each item with hierarchy level
    level_indicator = f"[Level {level}] " if level > 0 else ""
    order_value = data.get('NUM_FIN_STAT_ORDER', 'N/A')
    expander_title = f"{level_indicator}**{data['CODE_FIN_STAT']}** - {data['NAME_FIN_STAT']} (Order: {order_value})"
    
    # Add children count to title if there are children
    if children:
        expander_title += f" ({len(children)} children)"
    
    with st.expander(expander_title, expanded=False):
        # Action buttons with proper container width
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✏️ Edit", key=f"edit_{data['CODE_FIN_STAT']}", help=f"Edit account {data['CODE_FIN_STAT']}", use_container_width=True):
                st.session_state[f"show_edit_account_{data['CODE_FIN_STAT']}"] = True
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete", key=f"delete_{data['CODE_FIN_STAT']}", help=f"Delete account {data['CODE_FIN_STAT']}", type="secondary", use_container_width=True):
                st.session_state[f"show_delete_confirm_{data['CODE_FIN_STAT']}"] = True
                st.rerun()
        
        with col3:
            if st.button("➕ Add Child", key=f"add_child_{data['CODE_FIN_STAT']}", help=f"Add a new child account under {data['CODE_FIN_STAT']}", use_container_width=True):
                st.session_state[f"show_add_child_{data['CODE_FIN_STAT']}"] = True
                st.rerun()
        
        # Show children if any (recursively with nested expanders)
        if children:
            st.write("**Children:**")
            for child_data in children:
                display_hierarchy_item(child_data, level + 1, current_path, data_manager)


@st.dialog("✏️ Edit Account")
def show_edit_account_popup(account_code: str, data_manager: COADataManager):
    """Show dialog popup form for editing an existing account"""
    
    # Ensure data is loaded
    if data_manager.data is None or data_manager.data.empty:
        with st.spinner("Loading COA data..."):
            data_manager.load_coa_data()
    
    # Clear all popup flags when dialog opens to prevent conflicts
    for key in list(st.session_state.keys()):
        if key.startswith("show_edit_account_") or key.startswith("show_add_child_"):
            st.session_state[key] = False
    
    # Custom CSS to hide the "Press Enter to submit form" message and style buttons
    hide_submit_message = """
    <style>
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
    /* Style all form submit buttons in dialogs */
    .stFormSubmitButton > button {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button:hover {
        background-color: #1e5bb8 !important;
    }
    .stFormSubmitButton > button[kind="primary"] {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button[kind="primary"]:hover {
        background-color: #1e5bb8 !important;
    }
    </style>
    """
    st.markdown(hide_submit_message, unsafe_allow_html=True)
    
    # Get current account data
    account_data = data_manager.data[data_manager.data['CODE_FIN_STAT'] == account_code]
    if account_data.empty:
        st.error(f"Account '{account_code}' not found")
        return
    
    current_data = account_data.iloc[0].to_dict()
    st.info(f"Editing account: **{account_code}**")
    
    with st.form(f"edit_account_form_{account_code}"):
        col1, col2 = st.columns(2)
        
        with col1:
            code = st.text_input("Code *", value=current_data.get('CODE_FIN_STAT', ''), 
                                placeholder="e.g., BSA12345", help="Unique account code")
            name = st.text_input("Name *", value=current_data.get('NAME_FIN_STAT', ''), 
                                placeholder="Account name", help="Account name in local language")
            parent_code = st.text_input("Parent Code", value=current_data.get('CODE_PARENT_FIN_STAT', '') or '', 
                                       placeholder="e.g., BSA99999", help="Parent account code (optional)")
            type_account = st.selectbox("Account Type *", ["A", "P", "R", "C"], 
                                       index=["A", "P", "R", "C"].index(current_data.get('TYPE_ACCOUNT', 'A')),
                                       help="A=Assets, P=Liabilities/Equity, R=Revenue, C=Cost")
        
        with col2:
            type_fin_statement = st.selectbox("Statement Type *", ["BS", "PL"],
                                             index=["BS", "PL"].index(current_data.get('TYPE_FIN_STATEMENT', 'BS')),
                                             help="BS=Balance Sheet, PL=Profit & Loss")
            name_eng = st.text_input("English Name", value=current_data.get('NAME_FIN_STAT_ENG', '') or '', 
                                    placeholder="Account name in English")
            order = st.number_input("Order", min_value=0, value=int(current_data.get('NUM_FIN_STAT_ORDER', 1000)), 
                                   step=100, help="Order number (use hundreds apart for easy insertion)")
            business_unit = st.text_input("Business Unit", value=current_data.get('FK_BUSINESS_UNIT', ''), 
                                         help="Business unit (read-only)", disabled=True)
        
        # Submit and Cancel buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("Save", type="primary", use_container_width=True)
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.active_dialog = None
                st.session_state[f"show_edit_account_{account_code}"] = False
                st.rerun()
        
        if submitted:
            if code and name and type_account and type_fin_statement:
                # Prepare update data
                updates = {
                    'CODE_FIN_STAT': code,
                    'NAME_FIN_STAT': name,
                    'CODE_PARENT_FIN_STAT': parent_code if parent_code else None,
                    'TYPE_ACCOUNT': type_account,
                    'TYPE_FIN_STATEMENT': type_fin_statement,
                    'NAME_FIN_STAT_ENG': name_eng if name_eng else None,
                    'NUM_FIN_STAT_ORDER': order
                }
                
                # Update the account
                success = data_manager.update_coa_item(account_code, updates, user="current_user")
                if success:
                    st.success(f"✅ Account '{code}' updated successfully!")
                    # Clear all dialog states
                    st.session_state.active_dialog = None
                    for key in list(st.session_state.keys()):
                        if key.startswith("show_edit_account_") or key.startswith("show_add_child_"):
                            st.session_state[key] = False
                    st.rerun()
                else:
                    st.error("❌ Failed to update account")
            else:
                st.error("❌ Please fill in all required fields (marked with *)")

@st.dialog("➕ Add New Child Account")
def show_add_child_popup(parent_code: str, data_manager: COADataManager):
    """Show dialog popup form for adding a new child account"""
    
    # Ensure data is loaded
    if data_manager.data is None or data_manager.data.empty:
        with st.spinner("Loading COA data..."):
            data_manager.load_coa_data()
    
    # Clear all popup flags when dialog opens to prevent conflicts
    for key in list(st.session_state.keys()):
        if key.startswith("show_edit_account_") or key.startswith("show_add_child_"):
            st.session_state[key] = False
    
    # Custom CSS to hide the "Press Enter to submit form" message and style buttons
    hide_submit_message = """
    <style>
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
    /* Style all form submit buttons in dialogs */
    .stFormSubmitButton > button {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button:hover {
        background-color: #1e5bb8 !important;
    }
    .stFormSubmitButton > button[kind="primary"] {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button[kind="primary"]:hover {
        background-color: #1e5bb8 !important;
    }
    </style>
    """
    st.markdown(hide_submit_message, unsafe_allow_html=True)
    
    # Get the business unit and financial statement type from the parent
    parent_data = data_manager.data[data_manager.data['CODE_FIN_STAT'] == parent_code]
    business_unit = parent_data.iloc[0]['FK_BUSINESS_UNIT'] if not parent_data.empty else None
    parent_fin_statement = parent_data.iloc[0]['TYPE_FIN_STATEMENT'] if not parent_data.empty else None
    
    st.info(f"Adding child account under: **{parent_code}** (Statement Type: **{parent_fin_statement}** - inherited from parent)")
    
    # Calculate smart default order
    default_order = data_manager.get_next_order_for_parent(parent_code, business_unit)
    
    with st.form(f"add_child_form_{parent_code}"):
        col1, col2 = st.columns(2)
        
        with col1:
            code = st.text_input("Code *", placeholder="e.g., BSA12345", help="Unique account code")
            name = st.text_input("Name *", placeholder="Account name", help="Account name in local language")
            type_account = st.selectbox("Account Type *", ["A", "P", "R", "C"], 
                                       help="A=Assets, P=Liabilities/Equity, R=Revenue, C=Cost")
        
        with col2:
            # Inherit financial statement type from parent (non-editable)
            st.text_input("Statement Type *", value=parent_fin_statement, disabled=True,
                         help=f"Inherited from parent: {parent_fin_statement}")
            type_fin_statement = parent_fin_statement  # Use inherited value
            name_eng = st.text_input("English Name", placeholder="Account name in English")
            order = st.number_input("Order", min_value=0, value=default_order, step=100,
                                   help=f"Order number (default: {default_order}, use hundreds apart for easy insertion)")
        
        # Submit and Cancel buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("Add Child", type="primary", use_container_width=True)
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.active_dialog = None
                st.session_state[f"show_add_child_{parent_code}"] = False
                st.rerun()
        
        if submitted:
            if code and name and type_account and type_fin_statement:
                # Get the business unit from the parent
                parent_data = data_manager.data[data_manager.data['CODE_FIN_STAT'] == parent_code]
                if not parent_data.empty:
                    business_unit = parent_data.iloc[0]['FK_BUSINESS_UNIT']
                else:
                    business_unit = "DEFAULT"
                
                # Create new item data
                new_item = {
                    'CODE_FIN_STAT': code,
                    'NAME_FIN_STAT': name,
                    'CODE_PARENT_FIN_STAT': parent_code,
                    'TYPE_ACCOUNT': type_account,
                    'TYPE_FIN_STATEMENT': type_fin_statement,
                    'NAME_FIN_STAT_ENG': name_eng if name_eng else None,
                    'NUM_FIN_STAT_ORDER': order,
                    'FK_BUSINESS_UNIT': business_unit
                }
                
                # Add to data manager
                success = data_manager.add_coa_item(new_item, user="current_user")
                if success:
                    st.success(f"✅ Child account '{code}' added successfully!")
                    # Clear all dialog states
                    st.session_state.active_dialog = None
                    for key in list(st.session_state.keys()):
                        if key.startswith("show_edit_account_") or key.startswith("show_add_child_"):
                            st.session_state[key] = False
                    st.rerun()
                else:
                    st.error("❌ Failed to add child account")
            else:
                st.error("❌ Please fill in all required fields (marked with *)")

@st.dialog("⚠️ Confirm Account Deletion")
def show_delete_confirmation_popup(account_code: str, data_manager: COADataManager):
    """Show dialog popup for confirming account deletion"""
    
    # Clear all popup flags when dialog opens to prevent conflicts
    for key in list(st.session_state.keys()):
        if key.startswith("show_edit_account_") or key.startswith("show_add_child_") or key.startswith("show_delete_confirm_"):
            st.session_state[key] = False
    
    # Custom CSS to make delete button blue instead of red and full width
    st.markdown("""
    <style>
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
    /* Style all form submit buttons in dialogs */
    .stFormSubmitButton > button {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button:hover {
        background-color: #1e5bb8 !important;
    }
    .stFormSubmitButton > button[kind="primary"] {
        background-color: #297cf7 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button[kind="primary"]:hover {
        background-color: #1e5bb8 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get account data for display
    account_data = data_manager.data[data_manager.data['CODE_FIN_STAT'] == account_code]
    if account_data.empty:
        st.error(f"Account '{account_code}' not found")
        return
    
    current_data = account_data.iloc[0].to_dict()
    
    st.error("⚠️ **DANGER: This action cannot be undone!**")
    st.warning(f"You are about to delete account: **{account_code}**")
    
    # Show account details
    st.info(f"""
    **Account Details:**
    - **Code:** {current_data.get('CODE_FIN_STAT', 'N/A')}
    - **Name:** {current_data.get('NAME_FIN_STAT', 'N/A')}
    - **Type:** {current_data.get('TYPE_ACCOUNT', 'N/A')} | **Statement:** {current_data.get('TYPE_FIN_STATEMENT', 'N/A')}
    - **Business Unit:** {current_data.get('FK_BUSINESS_UNIT', 'N/A')}
    """)
    
    # Check for children
    children = data_manager.data[data_manager.data['CODE_PARENT_FIN_STAT'] == account_code]
    if not children.empty:
        st.error(f"❌ **Cannot delete account with {len(children)} child accounts!**")
        st.write("**Child accounts that must be deleted first:**")
        for _, child in children.iterrows():
            st.write(f"- {child['CODE_FIN_STAT']}: {child['NAME_FIN_STAT']}")
        st.stop()
    
    with st.form(f"delete_confirmation_form_{account_code}"):
        st.markdown("**To confirm deletion, please type the account code exactly as shown:**")
        confirmation_code = st.text_input(
            f"Type '{account_code}' to confirm deletion:",
            placeholder=f"Enter: {account_code}",
            help="This is a safety measure to prevent accidental deletions"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.form_submit_button("🗑️ Delete", type="primary", use_container_width=True):
                if confirmation_code == account_code:
                    # Actually delete the item
                    success = data_manager.delete_coa_item(account_code, user="current_user")
                    if success:
                        st.success(f"✅ Account '{account_code}' deleted successfully!")
                        # Clear all dialog states
                        st.session_state.active_dialog = None
                        for key in list(st.session_state.keys()):
                            if key.startswith("show_edit_account_") or key.startswith("show_add_child_") or key.startswith("show_delete_confirm_"):
                                st.session_state[key] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete account")
                else:
                    st.error(f"❌ Code mismatch! You entered '{confirmation_code}' but the account code is '{account_code}'")
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.active_dialog = None
                st.session_state[f"show_delete_confirm_{account_code}"] = False
                st.rerun()

def show_search_filter(data_manager: COADataManager, business_unit: str = None):
    """Show search and filter interface"""
    
    st.subheader("Search & Filter COA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_query = st.text_input("Search", placeholder="Search by name, code, or English name")
        
        type_account = st.selectbox(
            "Account Type",
            ["All", "A (Assets)", "P (Liabilities/Equity)", "R (Revenue)", "C (Cost)"],
            key="type_account_filter"
        )
        
        type_statement = st.selectbox(
            "Statement Type",
            ["All", "BS (Balance Sheet)", "PL (Profit & Loss)"],
            key="type_statement_filter"
        )
    
    with col2:
        hierarchy_level = st.selectbox(
            "Hierarchy Level",
            ["All"] + [str(i) for i in range(6)],
            key="hierarchy_level_filter"
        )
        
        if st.button("Apply Filters"):
            # Get filtered data
            df = data_manager.filter_by_business_unit(business_unit) if business_unit else data_manager.data
            
            if df is not None and not df.empty:
                # Apply filters
                filtered_df = df.copy()
                
                if search_query:
                    mask = (
                        filtered_df['NAME_FIN_STAT'].str.contains(search_query, case=False, na=False) |
                        filtered_df['CODE_FIN_STAT'].str.contains(search_query, case=False, na=False) |
                        filtered_df['NAME_FIN_STAT_ENG'].str.contains(search_query, case=False, na=False)
                    )
                    filtered_df = filtered_df[mask]
                
                if type_account != "All":
                    account_type_map = {
                        "A (Assets)": "A",
                        "P (Liabilities/Equity)": "P", 
                        "R (Revenue)": "R",
                        "C (Cost)": "C"
                    }
                    filtered_df = filtered_df[filtered_df['TYPE_ACCOUNT'] == account_type_map[type_account]]
                
                if type_statement != "All":
                    statement_map = {
                        "BS (Balance Sheet)": "BS",
                        "PL (Profit & Loss)": "PL"
                    }
                    filtered_df = filtered_df[filtered_df['TYPE_FIN_STATEMENT'] == statement_map[type_statement]]
                
                if hierarchy_level != "All":
                    filtered_df = filtered_df[filtered_df['HIERARCHY_LEVEL'] == int(hierarchy_level)]
                
                # Display results
                st.write(f"Found {len(filtered_df)} items matching your criteria:")
                st.dataframe(filtered_df[['CODE_FIN_STAT', 'NAME_FIN_STAT', 'TYPE_ACCOUNT', 'TYPE_FIN_STATEMENT']])
            else:
                st.warning("No data available for filtering")
