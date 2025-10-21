# COA Management System

A professional Streamlit application for managing Chart of Accounts (COA) data with Keboola integration, hierarchical visualization, and advanced data transformation capabilities.

## Features

- **🏦 Chart of Accounts Management**: Complete CRUD operations for financial account structures
- **🌳 Hierarchical Data Visualization**: Drill-down navigation through COA hierarchy
- **📝 Advanced Data Editing**: Full CRUD operations with session-based data management
- **🔄 Keboola Integration**: Direct data loading and saving to Keboola platform
- **📊 Interactive Analytics**: Comprehensive charts and financial insights
- **🔄 Data Transformation**: COA enrichment and business subunit mapping
- **🎨 Modern UI**: Professional design with responsive layout
- **👥 Multi-user Support**: Session-based data isolation for concurrent users

## Technology Stack

- **Streamlit**: Web application framework
- **Keboola Streamlit**: Direct integration with Keboola platform
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **AG Grid**: Advanced data grid with editing capabilities
- **Hydralit Components**: Modern UI components

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cao
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Keboola credentials**:
   Create `.streamlit/secrets.toml`:
   ```toml
   kbc_token="your-keboola-token"
   kbc_url="https://connection.europe-west3.gcp.keboola.com/"
   ```

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
cao/
├── app.py                           # Main application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── .gitignore                      # Git exclusions
├── .streamlit/
│   └── secrets.toml                # Keboola credentials
├── pages/                          # Application pages
│   ├── __init__.py
│   ├── coa_editor.py              # COA editing interface
│   ├── coa_import_export.py       # Data import/export
│   ├── coa_transformation.py     # Data transformation
│   └── analytics.py               # Analytics and insights
└── utils/                          # Utility modules
    ├── __init__.py
    ├── coa_data_manager.py        # COA data management
    └── coa_transformer.py         # Data transformation logic
```

## Usage

### Dashboard (Editor)
- **Hierarchical View**: Navigate through COA structure with expand/collapse
- **Data Table**: View and edit accounts in tabular format
- **Search & Filter**: Find specific accounts by code, name, or business unit
- **Add/Edit/Delete**: Full CRUD operations with validation
- **Session Management**: Changes are isolated per user session

### Import/Export
- **Excel Import**: Upload COA data from Excel files
- **Data Validation**: Comprehensive validation rules
- **Export Options**: Download data in various formats
- **Bulk Operations**: Handle large datasets efficiently

### Transform
- **Business Subunits**: Load from Keboola with caching
- **COA Enrichment**: Build hierarchy levels and identify leaf nodes
- **Business Unit Mapping**: Create subunit-specific COA structures
- **Central COA Mapping**: Generate mappings to central (FININ) COA
- **Debug Tools**: Validate transformation completeness

### Analytics
- **Overview Metrics**: Account counts, business units, statement types
- **Hierarchy Analysis**: Depth analysis and relationship mapping
- **Trends**: Time-series analysis and patterns
- **Insights**: Data quality and completeness metrics

## Key Features

### Keboola Integration
- **Direct Data Loading**: Read COA data from Keboola tables
- **Incremental Updates**: Session-based change tracking
- **Caching**: Optimized data loading with 5-minute cache
- **Error Handling**: Robust error management and user feedback

### Session-Based Data Management
- **User Isolation**: Each user has independent working copy
- **Change Tracking**: Track all modifications with audit trail
- **Unsaved Changes Warning**: Prevent accidental data loss
- **Refresh Control**: Manual data refresh with confirmation

### Hierarchical Data Management
- **Multi-level Structure**: Support for complex COA hierarchies
- **Parent-Child Relationships**: Automatic relationship management
- **Level Calculation**: Dynamic hierarchy depth calculation
- **Bulk Operations**: Hierarchy-aware bulk operations

### Data Transformation
- **COA Enrichment**: Add hierarchy levels and metadata
- **Business Subunit Mapping**: Create unit-specific COA structures
- **Central COA Integration**: Map to central accounting standards
- **Validation**: Comprehensive data quality checks

## Configuration

### Keboola Setup
1. **Get Credentials**: Obtain Keboola token and URL from your project
2. **Update secrets.toml**: Add your credentials to `.streamlit/secrets.toml`
3. **Table Access**: Ensure access to required Keboola tables:
   - `in.c-keboola-ex-google-drive-01k7haj8zpdqrevsrchqxx4p87.KBC_COA_INPUT`
   - `out.c-999_initiation_tables_creation.DC_BUSINESS_SUBUNIT`

### Data Format
The application works with COA data containing:
- `CODE_FIN_STAT`: Account code
- `NAME_FIN_STAT`: Account name
- `CODE_PARENT_FIN_STAT`: Parent account code
- `FK_BUSINESS_UNIT`: Business unit identifier
- `TYPE_FIN_STATEMENT`: Statement type (BS/PL)
- `TYPE_ACCOUNT`: Account type
- `NUM_FIN_STAT_ORDER`: Display order

## Development

### Code Structure
- **Modular Design**: Separate concerns across pages and utilities
- **Session Management**: Proper state management with Streamlit
- **Error Handling**: Comprehensive error handling and user feedback
- **Caching**: Optimized performance with Streamlit caching

### Best Practices
- **Data Validation**: All inputs are validated before processing
- **Audit Trail**: Complete change tracking for compliance
- **User Experience**: Intuitive interface with clear feedback
- **Performance**: Optimized for large datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.