# MySQL Setup Instructions for Tournament Calendar

## 📋 Prerequisites
1. **Install MySQL Server** (if not already installed)
2. **Install MySQL Workbench** (optional, for GUI management)
3. **Python MySQL connector** (already installed ✅)

## 🚀 Quick Setup Steps

### Option 1: If MySQL is Already Installed
```bash
# Run the MySQL integration script
python mysql_integration.py
```

### Option 2: Install MySQL First (if needed)

#### Windows Installation:
1. Download MySQL Installer from: https://dev.mysql.com/downloads/installer/
2. Run installer and select "MySQL Server" + "MySQL Workbench"
3. Set root password during installation
4. Start MySQL service

#### Quick Command Line Setup:
```bash
# Check if MySQL is running
net start mysql80  # or mysql57 depending on version

# If not installed, install via chocolatey (if you have it)
choco install mysql

# Or download from official site
```

## 🗄️ Database Schema Created

The script will create:
- **Database**: `tournament_calendar`
- **Table**: `tournaments` with these columns:
  - `id` (Primary Key, Auto Increment)
  - `tournament_name` (VARCHAR 255)
  - `sport` (VARCHAR 100)
  - `level` (VARCHAR 100) 
  - `start_date` (DATE)
  - `end_date` (DATE)
  - `official_url` (TEXT)
  - `streaming_links` (TEXT)
  - `image_url` (TEXT)
  - `summary` (TEXT)
  - `source_url` (TEXT)
  - `extraction_date` (DATETIME)
  - `created_at` (TIMESTAMP)
  - `updated_at` (TIMESTAMP)

## 📊 What the Script Does

1. ✅ **Connects** to MySQL server
2. ✅ **Creates** database `tournament_calendar`
3. ✅ **Creates** `tournaments` table with proper schema
4. ✅ **Imports** data from `sample_output/tournaments_sample.csv`
5. ✅ **Shows** statistics and confirmation

## 🔍 Verify Data in MySQL

### Command Line:
```sql
mysql -u root -p
USE tournament_calendar;
SELECT * FROM tournaments;
```

### MySQL Workbench:
1. Open MySQL Workbench
2. Connect to local server
3. Navigate to `tournament_calendar` schema
4. Browse `tournaments` table

## 🚨 Troubleshooting

### MySQL Not Found Error:
- **Windows**: Add MySQL to PATH or use full path
- **Check Service**: Services.msc → MySQL80 should be running

### Connection Error:
- Verify MySQL is running: `net start mysql80`
- Check username/password
- Ensure port 3306 is not blocked

### Permission Error: 
- Run terminal as Administrator
- Check MySQL user privileges

## 🎯 Expected Output

```
🚀 MySQL Integration for Tournament Calendar
==================================================
📋 MySQL Configuration:
   Host: localhost
   User: root
   Database: tournament_calendar

✅ Connected to MySQL server
✅ Database 'tournament_calendar' created/selected
✅ Tournaments table created successfully
✅ Loaded 4 tournaments from CSV
✅ Successfully imported 4/4 tournaments

📊 Database Statistics:
Total Tournaments: 4

🏆 By Sport:
   Cricket: 4

🎯 By Level:
   International: 4

✅ MySQL integration completed!
```

## 📁 Files Involved
- `mysql_integration.py` - Main integration script
- `sample_output/tournaments_sample.csv` - Source data
- `config.py` - Configuration settings
