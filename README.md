# Flask Calculator App

A comprehensive, modern calculator application built with Flask, featuring a responsive web interface, calculation history, keyboard support, and robust error handling.

## Features

### Core Functionality
- **Basic Arithmetic Operations**: Addition (+), Subtraction (-), Multiplication (×), Division (÷)
- **Real-time Calculations**: Instant results as you type
- **Keyboard Support**: Full keyboard navigation and input
- **Calculation History**: Persistent history with session management
- **Error Handling**: Comprehensive validation and error recovery
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

### User Interface
- **Modern Design**: Clean, professional interface with gradient backgrounds
- **Responsive Layout**: Adaptive design for all screen sizes
- **Visual Feedback**: Hover effects, button animations, and status indicators
- **Error Display**: Clear error messages with auto-dismiss
- **History Panel**: Interactive history with timestamp display

### Technical Features
- **Session Management**: Automatic session tracking with local storage
- **Database Storage**: SQLite database for persistent history
- **RESTful API**: Clean API endpoints for all operations
- **Input Validation**: Comprehensive expression validation
- **Error Recovery**: Graceful handling of edge cases

## Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

1. **Clone or download the project**
2. **Create virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```powershell
   python app.py
   ```

5. **Access the calculator**
   Open your browser and navigate to `http://localhost:5000`

### Running Tests
```powershell
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_calculator.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## API Endpoints

### Calculator Operations
- `POST /api/calculator/calculate` - Perform calculation
- `POST /api/calculator/validate` - Validate expression syntax
- `POST /api/calculator/clear` - Clear calculation history

### History Management
- `GET /api/history/` - Get calculation history
- `DELETE /api/history/<id>` - Delete specific calculation

### API Information
- `GET /api` - API documentation and endpoints

## Project Structure

```
project_1/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                      # Project documentation
├── tests/                         # Test suite
│   ├── test_api.py               # Original API tests
│   └── test_calculator.py        # Calculator-specific tests
├── static/                        # Static assets
│   ├── css/
│   │   ├── calculator.css        # Main calculator styles
│   │   └── responsive.css        # Mobile/tablet responsive styles
│   ├── js/
│   │   ├── calculator.js         # Calculator logic and UI interaction
│   │   ├── keyboard-handler.js   # Keyboard input handling
│   │   └── history-manager.js    # History panel management
│   └── fonts/                    # Web fonts
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   └── calculator.html           # Main calculator interface
├── models/                       # Database models
│   ├── __init__.py
│   └── calculation.py            # Calculation model
├── routes/                       # Flask route handlers
│   ├── __init__.py
│   ├── calculator_routes.py      # Calculator operation routes
│   └── history_routes.py         # History management routes
└── utils/                        # Utility functions
    ├── __init__.py
    ├── calculator_core.py        # Core calculation logic
    └── validators.py             # Input validation functions
```

## Usage

### Basic Operations
1. **Numbers**: Click number buttons or use keyboard (0-9)
2. **Operators**: Click operator buttons or use keyboard (+, -, *, /)
3. **Decimal**: Click decimal point or use keyboard (.)
4. **Equals**: Click equals button or press Enter/=
5. **Clear**: Click C to clear all, CE to clear entry
6. **Backspace**: Click backspace button or press Backspace

### Keyboard Shortcuts
- **Numbers**: 0-9
- **Operators**: +, -, *, /
- **Equals**: Enter or =
- **Clear All**: Delete, C, or c
- **Clear Entry**: Escape
- **Decimal**: .
- **Backspace**: Backspace

### History Features
- **View History**: All calculations are automatically saved
- **Click to Reuse**: Click any history item to load the result
- **Clear History**: Use the "Clear" button in the history panel
- **Session Based**: History is isolated between browser sessions

## Technical Details

### Backend Architecture
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database (development)
- **Blueprint Pattern**: Modular route organization

### Frontend Architecture
- **Vanilla JavaScript**: No framework dependencies
- **CSS Grid**: Modern layout system
- **Local Storage**: Client-side session management
- **Fetch API**: Modern HTTP requests

### Security Features
- **Input Sanitization**: All expressions are validated
- **SQL Injection Prevention**: Using SQLAlchemy ORM
- **Session Isolation**: History separated by session ID
- **Error Message Sanitization**: No sensitive data exposure

### Performance Optimizations
- **Efficient DOM Updates**: Minimal reflows and repaints
- **Debounced Validation**: Optimized input validation
- **Database Indexing**: Fast history queries
- **Responsive Images**: Optimized for mobile devices

## Testing

### Test Coverage
- **Unit Tests**: Calculator logic, validation functions
- **Integration Tests**: API endpoints, database operations
- **Frontend Tests**: UI interactions, keyboard handling
- **Error Handling**: Edge cases, error recovery

### Running Tests
```bash
# All tests
pytest

# Specific test categories
pytest tests/test_calculator.py::test_calculator_basic_operations
pytest tests/test_calculator.py::test_calculator_history_storage

# With verbose output
pytest -v

# With coverage report
pytest --cov=. --cov-report=term-missing
```

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `FLASK_ENV`: Environment (development/production)

### Database Configuration
- **Development**: SQLite file in project directory
- **Production**: Configure with your preferred database
- **Testing**: In-memory SQLite for isolation

## Browser Support
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change port in `app.py` or kill existing process
   ```powershell
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

2. **Database Errors**
   - Delete `calculator.db` file to reset database
   - Run `python app.py` to recreate tables

3. **Keyboard Not Working**
   - Ensure page has focus
   - Check browser console for JavaScript errors
   - Try refreshing the page

4. **History Not Saving**
   - Check browser localStorage support
   - Verify session ID is being generated
   - Check network requests in browser dev tools

### Debug Mode
Enable debug mode by setting `debug=True` in `app.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## Development

### Adding New Features
1. **Backend**: Add routes in `routes/`, models in `models/`
2. **Frontend**: Add JavaScript in `static/js/`, CSS in `static/css/`
3. **Tests**: Add tests in `tests/`

### Code Style
- **Python**: PEP 8 compliant
- **JavaScript**: ES6+ features, consistent naming
- **CSS**: BEM methodology for class naming

## License
This project is open source and available under the MIT License.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support
For issues, questions, or contributions, please create an issue in the repository.