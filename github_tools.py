import os
import requests
import sqlite3
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found in environment variables")

GITHUB_API_URL = "https://api.github.com"

def create_issue(repo, owner, title, body=None, assignees=None, labels=None, issue_id=None, db_file="issues.db"):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "title": title,
        "body": body,
        "assignees": assignees,
        "labels": labels
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        raise Exception(response.text)
    
    issue_number = response.json().get("number")
    
    if issue_number and issue_id:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE issues
            SET github_number = ?
            WHERE issue_id = ?
        ''', (issue_number, issue_id))
        conn.commit()
        conn.close()
    
    return f"Issue {title} created successfully with number {issue_number}"

def create_comment(repo, owner, issue_number, body):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "body": body
    }
    response = requests.post(url, headers=headers, json=data)
    if (response.status_code != 201):
        raise Exception(response.text)
    return "Comment added successfully"

def create_label(repo, owner, name, color, description=None):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/labels"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "22-11-28"
    }
    data = {
        "name": name,
        "color": color,
        "description": description
    }
    response = requests.post(url, headers=headers, json=data)
    if (response.status_code != 201):
        raise Exception(response.text)
    return "Label created successfully"

def create_milestone(repo, title, state="open", description=None, due_on=None):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/milestones"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "22-11-28"
    }
    data = {
        "title": title,
        "state": state,
        "description": description,
        "due_on": due_on
    }
    response = requests.post(url, headers=headers, json=data)
    if (response.status_code != 201):
        raise Exception(response.text)
    return "Milestone created successfully"