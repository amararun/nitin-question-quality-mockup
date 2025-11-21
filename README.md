# Nitin Question Quality Mockup

A React-based mockup application for managing and reviewing question quality, with database integration.

## 🔧 Setup Instructions

### 1. Database Scripts Setup

The database scripts require environment variables for security. 

**Create a `.env` file** in the root directory:

```bash
# Copy the example file
cp .env.example .env

# Then edit .env with your actual credentials
```

Your `.env` file should contain:

```
DB_HOST=your-host.aivencloud.com
DB_PORT=13288
DB_USER=avnadmin
DB_PASSWORD=your-actual-password
DB_NAME=defaultdb
```

**Install Python dependencies:**

```bash
cd db_scripts
pip install -r requirements.txt
```

### 2. React Mockup Setup

```bash
cd react-mockup
npm install
npm run dev
```

## 📁 Project Structure

```
.
├── db_scripts/          # Database import/export scripts (Python)
├── react-mockup/        # React frontend application
├── docs/                # Documentation and plans
├── llm_evals/          # LLM evaluation results
└── xlwings_lite_scripts/ # Excel integration scripts
```

## 🔒 Security

- **Never commit `.env` files** - they contain sensitive credentials
- All database passwords are stored in environment variables
- The `.gitignore` file is configured to exclude:
  - `.env` files
  - `node_modules/`
  - Python cache files (`__pycache__/`, `*.pyc`)
  - Build artifacts

## 🚀 Usage

### Database Scripts

```bash
# Explore database structure
python db_scripts/explore_database.py

# Import questions from SQL file
python db_scripts/import_questions_v2.py

# Export data to tab-delimited format
python db_scripts/export_to_tab_delimited.py
```

### React Mockup

```bash
cd react-mockup
npm run dev    # Start development server
npm run build  # Build for production
```

## 📝 Notes

- Make sure you have created your `.env` file before running database scripts
- The React mockup includes components for both question review and LLM integration
- All sensitive data is now properly secured with environment variables

