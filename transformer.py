import csv
import json
import sqlite3

def read_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = [row for row in reader]
    return rows

def load_mapping(mapping_file):
    with open(mapping_file, mode='r', encoding='utf-8') as file:
        mapping = json.load(file)
    return mapping

def extract_fields(row, username_mapping, epic_mapping):
    assignee = row.get("Assignee")
    github_assignee = username_mapping.get(assignee, "")

    epic = row.get("Custom field (Epic Link)")
    epic_name = epic_mapping.get(epic, None)

    labels = [row.get("Issue Type")]

    body = f"**Jira Ticket**: {row.get('Issue key')}\n\n" \
           f"**Description**: {row.get('Description')}\n\n" \
           f"**Last Updated**: {row.get('Updated')}"

    fields = {
        "summary": row.get("Summary"),
        "issuekey": row.get("Issue key"),
        "issueId": row.get("Issue id"),
        "issueType": row.get("Issue Type"),
        "status": row.get("Status"),
        "priority": row.get("Priority"),
        "assignee": github_assignee,
        "created": row.get("Created"),
        "updated": row.get("Updated"),
        "description": row.get("Description"),
        "comments": extract_comments(row),
        "isIssueCreated": False,
        "areProjectFieldsAdded": False,
        "areCommentsAdded": False,
        "body": body,  # Updated body with markdown format
        "githubNumber": "",
        "issueNodeId": "",
        "projectIssueNodeId": "",
        "labels": labels,
        "epic": epic_name
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

def transform_csv_to_json(file_path, username_mapping, epic_mapping):
    rows = read_csv(file_path)
    json_objects = [extract_fields(row, username_mapping, epic_mapping) for row in rows]
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
            are_project_fields_added BOOLEAN,
            are_comments_added BOOLEAN,
            body TEXT,
            github_number TEXT,
            issue_node_id TEXT,
            project_issue_node_id TEXT,
            labels TEXT,
            epic TEXT
        )
    ''')
    for obj in json_objects:
        cursor.execute('''
            INSERT INTO issues (
            summary, issue_key, issue_id, issue_type, status, priority, assignee, created, updated, description, comment, is_issue_created, are_project_fields_added, are_comments_added, body, github_number, issue_node_id, project_issue_node_id, labels, epic
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj["summary"], obj["issuekey"], obj["issueId"], obj["issueType"], obj["status"], obj["priority"], obj["assignee"], obj["created"], obj["updated"], obj["description"], json.dumps(obj["comments"]), obj["isIssueCreated"], obj["areProjectFieldsAdded"], obj["areCommentsAdded"], obj["body"], obj["githubNumber"], obj["issueNodeId"], obj["projectIssueNodeId"], json.dumps(obj["labels"]), obj["epic"]
        ))
    conn.commit()
    conn.close()