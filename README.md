# Jira to GitHub Migration Tool

This tool automates the migration of Jira issues to GitHub issues, including comments, labels, and project fields.

## Installation

Follow these steps to set up the migration tool:

### 1. Clone this repository:

```sh
git clone https://github.com/Abradat/jira-2-github-migration
```

### 2. Create a virtual environment:

```sh
python -m venv venv
```

### 3. Activate the virtual environment:

On Windows:

```sh
venv\Scripts\activate
```

On macOS/Linux:

```sh
source venv/bin/activate
```

### 4. Install the required dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

### Environment Variables (.env)

Create a `.env` file in the root directory with your GitHub API tokens:

```
GITHUB_TOKEN=<your-github-token>
```

Make sure your token is `classic` has the following permissions:

- `repo` (Full control of private repositories)
- `project` (For project access)
- `admin:org` (Full control of orgs and teams, read and write org projects)

### Config File (config.json)

Modify the `config.json` file to match your migration requirements:

```json
{
  "github_repo": "Target GitHub repository name",
  "github_username": "GitHub username or organization name",
  "github_project_name": "GitHub project board name",
  "is_org_project": true, // if project is organizational or personal
  "input_csv_file": "Path to your Jira CSV export file",
  "output_json_file": "Path where the transformed JSON will be saved",
  "j2g_json_file": "JSON file mapping Jira usernames to GitHub usernames",
  "database": "SQLite database file path",
  "migrate_offset_number": 100, // number of tickets to migrate
  "add_to_project": true, // flag to add fields to the project
  "add_status": true, // add "status" field to the project
  "add_epic": true, // add "epic" field to the project
  "add_priority": true // add "priority" field to the project
}
```

### Username Mapping (jira_to_github_username.json)

Create a mapping between Jira and GitHub usernames:

```json
{
  "jira_username": "github_username"
}
```

## File Structure and Process

### Core Files

- `config_reader.py`: Utility to load configuration from `config.json`
- `transformer.py`: Transforms Jira CSV data into structured JSON
- `migrate_jira_2_db.py`: Loads CSV data into SQLite database
- `github_tools.py`: Contains GitHub API integration functions
- `db_utils.py`: Database utility functions
- `migrate_db_2_github.py`: Migrates data from SQLite to GitHub

### Process Flow

1. **Export data from Jira**: Export issues as CSV and place in the input directory

2. **Transform Jira data**:

   - This loads the Jira CSV into a SQLite database and generates a structured JSON file.

3. **Migrate to GitHub**:
   - This creates GitHub issues, adds comments, labels, and updates project fields.

## Migration Process Details

### Data Transformation:

- CSV data is read and transformed to JSON format
- Jira fields are mapped to GitHub issue fields
- Comments are extracted and formatted

### Database Storage:

- Transformed data is stored in SQLite for tracking migration status
- Tables track which issues have been created and which still need processing

### GitHub Migration:

- Issues are created via GitHub REST API
- Comments are added to issues
- Issues are added to project boards
- Custom fields (like status, epic, priority) are updated via GraphQL API

### Status Tracking:

- The migration process updates the SQLite database to track progress
- You can resume migration if it's interrupted

## Troubleshooting

- **GitHub Token Issues**: Make sure your tokens have the correct permissions
- **Project Fields Not Updating**: Verify the field names match exactly with your GitHub project
- **Rate Limiting**: GitHub has API rate limits; the script may need to be run in batches
