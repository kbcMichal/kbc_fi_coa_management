# Hierarchical Data Visualizer

A professional Streamlit application for visualizing and managing hierarchical data with modern UI components and advanced analytics.

## Features

- **🌳 Hierarchical Data Visualization**: Drill-down navigation through complex data structures
- **📝 Advanced Data Editing**: Full CRUD operations with AG Grid integration
- **📊 Interactive Analytics**: Comprehensive charts and insights
- **🎨 Modern UI**: Professional design using Hydralit Components
- **📱 Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Streamlit**: Web application framework
- **AG Grid**: Advanced data grid with editing capabilities
- **Hydralit Components**: Modern UI components
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation and analysis

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hierarchical-data-visualizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
hierarchical-data-visualizer/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── pages/                # Application pages
│   ├── __init__.py
│   ├── dashboard.py      # Main dashboard with data visualization
│   ├── data_editor.py    # Data editing interface
│   └── analytics.py      # Advanced analytics and insights
└── utils/                # Utility modules
    ├── __init__.py
    ├── config.py         # Application configuration
    └── data_manager.py   # Data management utilities
```

## Usage

### Dashboard
- View hierarchical data in multiple formats
- Interactive data tables with filtering and sorting
- Real-time metrics and KPIs
- Drill-down navigation through data hierarchy

### Data Editor
- **Edit Existing**: Modify data directly in the grid
- **Add New**: Create new items with form validation
- **Delete Items**: Remove items with hierarchy awareness

### Analytics
- **Overview**: Key metrics and distributions
- **Hierarchy Analysis**: Depth analysis and relationships
- **Trends**: Time-series analysis and patterns
- **Insights**: AI-generated recommendations

## Key Features

### Hierarchical Data Management
- Support for multi-level data structures
- Parent-child relationships
- Automatic hierarchy depth calculation
- Bulk operations with hierarchy awareness

### Advanced Data Grid
- Inline editing capabilities
- Column filtering and sorting
- Row selection and bulk operations
- Export functionality
- Responsive design

### Interactive Visualizations
- Dynamic charts with Plotly
- Real-time data updates
- Customizable chart types
- Export capabilities

### Modern UI Components
- Professional navigation with Hydralit
- Responsive design
- Dark/light theme support
- Mobile-friendly interface

## Configuration

The application can be configured through `utils/config.py`:

- Grid display options
- Theme settings
- Data limits
- Auto-save preferences

## Data Format

The application expects hierarchical data with the following structure:

- `id`: Unique identifier
- `name`: Item name
- `category`: Top-level category
- `subcategory`: Sub-category
- `parent_id`: Reference to parent item (None for root items)
- `level`: Hierarchy level (0 for root, 1 for children, etc.)
- `value`: Numeric value
- `status`: Item status (Active, Inactive, Pending)
- `created_date`: Creation timestamp

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
