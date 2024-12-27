import csv
import json
import sqlite3

def read_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]
    return rows

def load_username_mapping(mapping_file):
    with open(mapping_file, mode='r', encoding='utf-8') as file:
        mapping = json.load(file)
    return mapping

def extract_fields(row):
    assignee = row.get("Assignee")
    github_assignee = username_mapping.get(assignee, "")
    labels = [row.get("Issue Type"), f"priority: {row.get('Priority')}", "status: ALCS Backlog"]

    body = f"**Jira Ticket**: {row.get('Issue key')}\n\n" \
           f"**Description**: {row.get('Description')}\n\n" \
           f"**Last Updated**: {row.get('Updated')}"

    fields = {
        "Summary": row.get("Summary"),
        "Issue key": row.get("Issue key"),
        "Issue id": row.get("Issue id"),
        "Issue Type": row.get("Issue Type"),
        "Status": row.get("Status"),
        "Priority": row.get("Priority"),
        "Assignee": github_assignee,
        "Created": row.get("Created"),
        "Updated": row.get("Updated"),
        "Description": row.get("Description"),
        "Comments": extract_comments(row),
        "isIssueCreated": False,
        "isPriorityAdded": False,
        "isCommentAdded": False,
        "body": body,  # Updated body with markdown format
        "github_number": "",
        "labels": labels
    }
    return fields

def extract_comments(row):
    comments = []
    for i in range(1, 4):
        comment = row.get(f"Comment {i}")
        if comment:
            parts = comment.split(';')
            if len(parts) >= 3:
                date, user, *content = parts
                content = ';'.join(content).strip()
                comments.append({
                    "date": date.strip(),
                    "user": user.strip(),
                    "content": content
                })
    return comments if comments else None

def transform_csv_to_json(file_path):
    rows = read_csv(file_path)
    json_objects = [extract_fields(row) for row in rows]
    return json_objects

def save_json(json_objects, output_file):
    with open(output_file, mode='w', encoding='utf-8') as file:
        json.dump(json_objects, file, indent=4)

def save_to_db(json_objects, db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary TEXT,
            issue_key TEXT,
            issue_id TEXT UNIQUE,
            issue_type TEXT,
            status TEXT,
            priority TEXT,
            assignee TEXT,
            created TEXT,
            updated TEXT,
            description TEXT,
            comment TEXT,
            is_issue_created BOOLEAN,
            is_priority_added BOOLEAN,
            is_comment_added BOOLEAN,
            body TEXT,
            github_number TEXT,
            labels TEXT
        )
    ''')
    for obj in json_objects:
        cursor.execute('''
            INSERT INTO issues (
                summary, issue_key, issue_id, issue_type, status, priority, assignee, created, updated, description, comment, is_issue_created, is_priority_added, is_comment_added, body, github_number, labels
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj["Summary"], obj["Issue key"], obj["Issue id"], obj["Issue Type"], obj["Status"], obj["Priority"], obj["Assignee"], obj["Created"], obj["Updated"], obj["Description"], json.dumps(obj["Comments"]), obj["isIssueCreated"], obj["isPriorityAdded"], obj["isCommentAdded"], obj["body"], obj["github_number"], json.dumps(obj["labels"])
        ))
    conn.commit()
    conn.close()

# Example usage
if __name__ == "__main__":
    input_csv = "files/sample.csv"  # Replace with your CSV file path
    output_json = "output.json"  # Replace with your desired output JSON file path
    db_file = "issues.db"  # Replace with your desired database file path
    username_mapping_file = "jira_to_github_username.json"  # Replace with your JSON mapping file path


    username_mapping = load_username_mapping(username_mapping_file)
    json_objects = transform_csv_to_json(input_csv)
    save_json(json_objects, output_json)
    save_to_db(json_objects, db_file)
    print(f"JSON data saved to {output_json}")
    print(f"Data saved to database {db_file}")