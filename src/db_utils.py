
import sqlite3

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
        SET are_comments_added = ?
        WHERE issue_id = ?
    ''', (is_comment_added, issue_id))
    conn.commit()
    conn.close()

def update_project_fields_status(db_file, issue_id, are_project_fields_added):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE issues
        SET are_project_fields_added = ?
        WHERE issue_id = ?
    ''', (are_project_fields_added, issue_id))
    conn.commit()
    conn.close()

def get_issue_node_id(db_file, issue_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT issue_node_id FROM issues WHERE issue_id = ?', (issue_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        raise ValueError(f"No issue_node_id found for issue_id {issue_id}")

def update_project_issue_node_id(db_file, issue_id, project_issue_node_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE issues
        SET project_issue_node_id = ?
        WHERE issue_id = ?
    ''', (project_issue_node_id, issue_id))
    conn.commit()
    conn.close()