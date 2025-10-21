"""
COA Import/Export functionality with Excel support
"""

import streamlit as st
import pandas as pd
import io
from utils.coa_data_manager import COADataManager
import openpyxl
from datetime import datetime

# Keboola brand colors
KEBOOLA_PRIMARY = "#297cf7"
KEBOOLA_DARK = "#08255a"
KEBOOLA_LIGHT = "#e6f2ff"

def apply_keboola_theme():
    """Apply Keboola theme to import/export"""
    st.markdown(f"""
    <style>
    .main {{
        background-color: white;
    }}
    .stApp {{
        background-color: white;
    }}
    .keboola-import-export {{
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .upload-area {{
        border: 2px dashed {KEBOOLA_PRIMARY};
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background-color: {KEBOOLA_LIGHT};
        margin: 1rem 0;
    }}
    </style>
    """, unsafe_allow_html=True)

def show_coa_import_export(data_manager: COADataManager):
    """Display the COA import/export interface"""
    
    apply_keboola_theme()
    
    
    # Load data if not already loaded
    if data_manager.data is None:
        with st.spinner("Loading COA data..."):
            data_manager.load_coa_data()
    
    # Create tabs for import and export
    tab1, tab2, tab3 = st.tabs(["Export Data", "Import Data", "Template Management"])
    
    with tab1:
        show_export_interface(data_manager)
    
    with tab2:
        show_import_interface(data_manager)
    
    with tab3:
        show_template_management()

def show_export_interface(data_manager: COADataManager):
    """Show export interface"""
    
    st.subheader("Export COA Data")
    
    # Business unit selection
    business_units = data_manager.get_business_units()
    if business_units:
        selected_bu = st.selectbox(
            "Select Business Unit to Export",
            business_units,
            key="export_bu_filter"
        )
    else:
        selected_bu = None
        st.warning("No business units found")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Export Format",
            ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
            key="export_format"
        )
    
    with col2:
        include_audit = st.checkbox("Include Audit Trail", value=False)
    
    # Export button
    if st.button("Export Data", type="primary"):
        if selected_bu:
            # Get filtered data
            df = data_manager.filter_by_business_unit(selected_bu)
            
            if export_format == "Excel (.xlsx)":
                # Create Excel file
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='COA_Data', index=False)
                    
                    if include_audit:
                        audit_df = pd.DataFrame(data_manager.get_audit_log())
                        if not audit_df.empty:
                            audit_df.to_excel(writer, sheet_name='Audit_Trail', index=False)
                
                output.seek(0)
                
                st.download_button(
                    label="Download Excel File",
                    data=output.getvalue(),
                    file_name=f"coa_export_{selected_bu}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            elif export_format == "CSV (.csv)":
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV File",
                    data=csv_data,
                    file_name=f"coa_export_{selected_bu}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            elif export_format == "JSON (.json)":
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="Download JSON File",
                    data=json_data,
                    file_name=f"coa_export_{selected_bu}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            st.success(f"✅ Export prepared for {selected_bu}")
        else:
            st.error("Please select a business unit")

def show_import_interface(data_manager: COADataManager):
    """Show import interface"""
    
    st.subheader("Import COA Data")
    
    # Upload area
    st.markdown("""
    <div class="upload-area">
        <h3>Upload COA Data File</h3>
        <p>Supported formats: Excel (.xlsx), CSV (.csv)</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['xlsx', 'csv'],
        help="Upload COA data file to import"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.info(f"📁 **File:** {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Import options
        col1, col2 = st.columns(2)
        
        with col1:
            import_mode = st.radio(
                "Import Mode",
                ["Replace All", "Append New", "Update Existing"],
                help="Choose how to handle existing data"
            )
        
        with col2:
            validate_data = st.checkbox("Validate Data", value=True, 
                                     help="Run validation rules on imported data")
        
        # Preview data
        if st.button("👁️ Preview Data"):
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                
                st.write("**Data Preview:**")
                st.dataframe(df.head(10))
                
                st.write(f"**Rows:** {len(df)}")
                st.write(f"**Columns:** {list(df.columns)}")
                
                # Show validation results
                if validate_data:
                    errors = data_manager.validate_coa_rules(df)
                    if errors:
                        st.error("❌ Validation errors found:")
                        for error in errors:
                            st.error(error)
                    else:
                        st.success("✅ Data validation passed!")
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Import button
        if st.button("Import Data", type="primary"):
            try:
                # Read the file
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_csv(uploaded_file)
                
                # Validate data
                if validate_data:
                    errors = data_manager.validate_coa_rules(df)
                    if errors:
                        st.error("❌ Validation errors found:")
                        for error in errors:
                            st.error(error)
                        return
                
                # Import based on mode
                if import_mode == "Replace All":
                    data_manager.data = df
                    st.success("✅ Data replaced successfully!")
                elif import_mode == "Append New":
                    if data_manager.data is not None:
                        data_manager.data = pd.concat([data_manager.data, df], ignore_index=True)
                    else:
                        data_manager.data = df
                    st.success("✅ Data appended successfully!")
                elif import_mode == "Update Existing":
                    # Update existing records
                    for _, row in df.iterrows():
                        code = row['CODE_FIN_STAT']
                        mask = data_manager.data['CODE_FIN_STAT'] == code
                        if mask.any():
                            data_manager.data.loc[mask] = row
                        else:
                            data_manager.data = pd.concat([data_manager.data, pd.DataFrame([row])], ignore_index=True)
                    st.success("✅ Data updated successfully!")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error importing data: {str(e)}")

def show_template_management():
    """Show template management interface"""
    
    st.subheader("Template Management")
    
    # Create template
    st.markdown("### Create COA Template")
    
    col1, col2 = st.columns(2)
    
    with col1:
        template_name = st.text_input("Template Name", placeholder="e.g., Standard COA Template")
        business_unit = st.text_input("Business Unit", placeholder="e.g., DEFAULT")
    
    with col2:
        account_types = st.multiselect(
            "Account Types to Include",
            ["A (Assets)", "P (Liabilities/Equity)", "R (Revenue)", "C (Cost)"],
            default=["A (Assets)", "P (Liabilities/Equity)", "R (Revenue)", "C (Cost)"]
        )
    
    if st.button("Create Template", type="primary"):
        if template_name and business_unit:
            # Create template structure
            template_data = create_coa_template(business_unit, account_types)
            
            # Convert to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                template_data.to_excel(writer, sheet_name='COA_Template', index=False)
                
                # Add instructions sheet
                instructions = pd.DataFrame({
                    'Field': ['CODE_FIN_STAT', 'NAME_FIN_STAT', 'CODE_PARENT_FIN_STAT', 'TYPE_ACCOUNT', 'TYPE_FIN_STATEMENT', 'NAME_FIN_STAT_ENG', 'NUM_FIN_STAT_ORDER'],
                    'Description': [
                        'Unique account code (required)',
                        'Account name in local language (required)',
                        'Parent account code (optional)',
                        'Account type: A, P, R, C (required)',
                        'Financial statement type: BS, PL (required)',
                        'Account name in English (optional)',
                        'Order number for sorting (required)'
                    ],
                    'Example': [
                        'BSA12345',
                        'Cash and Cash Equivalents',
                        'BSA99999',
                        'A',
                        'BS',
                        'Cash and Cash Equivalents',
                        '1000'
                    ]
                })
                instructions.to_excel(writer, sheet_name='Instructions', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="Download Template",
                data=output.getvalue(),
                file_name=f"{template_name}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("✅ Template created successfully!")
        else:
            st.error("Please fill in template name and business unit")
    
    # Template examples
    st.markdown("### 📚 Template Examples")
    
    examples = [
        {
            "name": "Basic COA Template",
            "description": "Standard chart of accounts with main categories",
            "accounts": ["Assets", "Liabilities", "Equity", "Revenue", "Expenses"]
        },
        {
            "name": "Detailed COA Template", 
            "description": "Comprehensive chart of accounts with sub-categories",
            "accounts": ["Current Assets", "Fixed Assets", "Current Liabilities", "Long-term Liabilities", "Equity", "Operating Revenue", "Operating Expenses"]
        }
    ]
    
    for example in examples:
        with st.expander(f"{example['name']}"):
            st.write(f"**Description:** {example['description']}")
            st.write(f"**Includes:** {', '.join(example['accounts'])}")
            
            if st.button(f"Use {example['name']}", key=f"example_{example['name']}"):
                st.info(f"Template '{example['name']}' selected. Use the create template function above.")

def create_coa_template(business_unit: str, account_types: list) -> pd.DataFrame:
    """Create a COA template with basic structure"""
    
    # Map account types
    type_mapping = {
        "A (Assets)": {"type": "A", "statement": "BS", "name": "Assets"},
        "P (Liabilities/Equity)": {"type": "P", "statement": "BS", "name": "Liabilities & Equity"},
        "R (Revenue)": {"type": "R", "statement": "PL", "name": "Revenue"},
        "C (Cost)": {"type": "C", "statement": "PL", "name": "Costs & Expenses"}
    }
    
    template_data = []
    order = 1000
    
    for account_type in account_types:
        if account_type in type_mapping:
            mapping = type_mapping[account_type]
            
            # Add main category
            template_data.append({
                'FK_BUSINESS_UNIT': business_unit,
                'NUM_FIN_STAT_ORDER': order,
                'CODE_FIN_STAT': f"BS{account_type[0]}99999",
                'NAME_FIN_STAT': mapping['name'],
                'CODE_PARENT_FIN_STAT': None,
                'TYPE_ACCOUNT': mapping['type'],
                'TYPE_FIN_STATEMENT': mapping['statement'],
                'NAME_FIN_STAT_ENG': mapping['name'],
                'HIERARCHY_LEVEL': 0
            })
            order += 100
            
            # Add sub-categories
            if mapping['type'] in ['A', 'P']:  # Balance Sheet
                sub_categories = [
                    ("Current", "BSA19999"),
                    ("Fixed", "BSA29999"),
                    ("Current", "BSP19999"),
                    ("Long-term", "BSP29999")
                ]
            else:  # Profit & Loss
                sub_categories = [
                    ("Operating", "BSR19999"),
                    ("Non-operating", "BSR29999"),
                    ("Operating", "BSC19999"),
                    ("Non-operating", "BSC29999")
                ]
            
            for sub_name, sub_code in sub_categories:
                template_data.append({
                    'FK_BUSINESS_UNIT': business_unit,
                    'NUM_FIN_STAT_ORDER': order,
                    'CODE_FIN_STAT': sub_code,
                    'NAME_FIN_STAT': f"{sub_name} {mapping['name']}",
                    'CODE_PARENT_FIN_STAT': f"BS{account_type[0]}99999",
                    'TYPE_ACCOUNT': mapping['type'],
                    'TYPE_FIN_STATEMENT': mapping['statement'],
                    'NAME_FIN_STAT_ENG': f"{sub_name} {mapping['name']}",
                    'HIERARCHY_LEVEL': 1
                })
                order += 100
    
    return pd.DataFrame(template_data)
