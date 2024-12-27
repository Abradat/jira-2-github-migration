import sqlite3
from github_tools import create_issue, create_comment
import json
from config_reader import load_config
import traceback

def fetch_issues_from_db(db_file, offset=0, limit=5):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM issues WHERE is_issue_created = 0 LIMIT ? OFFSET ?', (limit, offset))
    issues = cursor.fetchall()
    conn.close()
    return issues

def update_issue_status(db_file, issue_id, is_issue_created):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE issues
        SET is_issue_created = ?
        WHERE issue_id = ?
    ''', (is_issue_created, issue_id))
    conn.commit()
    conn.close()

def update_comment_status(db_file, issue_id, is_comment_added):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE issues
        SET is_comment_added = ?
        WHERE issue_id = ?
    ''', (is_comment_added, issue_id))
    conn.commit()
    conn.close()

def main():
    config = load_config("config.json")
    db_file = config["database"]
    repo = config["github_repo"]
    owner = config["github_username"]
    
    issues = fetch_issues_from_db(db_file, 0, 18)
    for issue in issues:
        issue_id = issue[3]
        title = issue[1]
        body = issue[15]
        assignees = [issue[7]] if issue[7] else []
        labels = json.loads(issue[17])
        
        try:
            response_issue_number = create_issue(repo, owner, title, body, assignees, labels, issue_id, db_file)
            update_issue_status(db_file, issue_id, True)

            comments = json.loads(issue[11]) if issue[11] else None
            if comments:
                for comment in comments:
                    comment_body = f"{comment['user']} on {comment['date']}:\n\n{comment['content']}"
                    create_comment(repo, owner, response_issue_number, comment_body)
            update_comment_status(db_file, issue_id, True)
        except Exception as e:
            print(f"Failed to create issue or comment for issue_id {issue_id}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
