import os
import requests
import sqlite3
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_GRAPHQL_TOKEN = os.getenv('GITHUB_GRAPHQL_TOKEN')

if not GITHUB_TOKEN:
    raise ValueError("GitHub token not found in environment variables")

if not GITHUB_GRAPHQL_TOKEN:
    raise ValueError("GitHub GraphQL token not found in environment variables")

GITHUB_API_URL = "https://api.github.com"
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

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
    issue_node_id = response.json().get("node_id")
    
    if issue_number and issue_id:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE issues
            SET github_number = ?, issue_node_id = ?
            WHERE issue_id = ?
        ''', (issue_number, issue_node_id, issue_id))
        conn.commit()
        conn.close()
    
    print(f"Issue {title} created successfully with number {issue_number}") 
    return issue_number

def create_comment(repo, owner, issue_number, body):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "body": body
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Comment added to issue #{issue_number}")
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

def get_project_id(owner, repo, project_name):
    headers = {
        "Authorization": f"Bearer {GITHUB_GRAPHQL_TOKEN}",
        "Content-Type": "application/json"
    }
    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        projectsV2(first: 100) {
          nodes {
            id
            title
          }
        }
      }
    }
    """
    variables = {
        "owner": owner,
        "repo": repo
    }
    response = requests.post(GITHUB_GRAPHQL_URL, headers=headers, json={"query": query, "variables": variables})
    if response.status_code != 200:
        raise Exception(f"GraphQL API call failed: {response.text}")
    projects = response.json()["data"]["repository"]["projectsV2"]["nodes"]
    for project in projects:
        if project["title"] == project_name:
            return project["id"]
    raise ValueError(f"Project '{project_name}' not found")

def add_issue_to_project(project_id, issue_node_id):
    headers = {
        "Authorization": f"Bearer {GITHUB_GRAPHQL_TOKEN}",
        "Content-Type": "application/json"
    }
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
        addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item {
                id
            }
        }
    }
    """
    variables = {
        "projectId": project_id,
        "contentId": issue_node_id
    }
    response = requests.post(GITHUB_GRAPHQL_URL, headers=headers, json={"query": query, "variables": variables})
    if response.status_code != 200:
        raise Exception(f"GraphQL API call failed: {response.text}")
    return response.json()

def get_field_ids(project_id):
    headers = {
        "Authorization": f"Bearer {GITHUB_GRAPHQL_TOKEN}",
        "Content-Type": "application/json"
    }
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 100) {
            nodes {
              ... on ProjectV2Field {
                id
                name
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {
        "projectId": project_id
    }
    response = requests.post(GITHUB_GRAPHQL_URL, headers=headers, json={"query": query, "variables": variables})
    if response.status_code != 200:
        raise Exception(f"GraphQL API call failed: {response.text}")
    fields = response.json()["data"]["node"]["fields"]["nodes"]
    return {field["name"]: field for field in fields}

def add_custom_fields_to_project(project_id, issue_node_id, custom_fields):
    headers = {
        "Authorization": f"Bearer {GITHUB_GRAPHQL_TOKEN}",
        "Content-Type": "application/json"
    }
    query = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
        updateProjectV2ItemFieldValue(input: {projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: $value}) {
            projectV2Item {
                id
            }
        }
    }
    """
    responses = []
    for field in custom_fields:
        value = field["value"]

        if (field["type"] == "option"):
            value = {"singleSelectOptionId": value}
        else:
            value = {"text": value}
        
        variables = {
            "projectId": project_id,
            "itemId": issue_node_id,
            "fieldId": field["fieldId"],
            "value": value
        }

        response = requests.post(GITHUB_GRAPHQL_URL, headers=headers, json={"query": query, "variables": variables})

        if response.status_code != 200:
            raise Exception(f"GraphQL API call failed: {response.text}")
        responses.append(response.json())
    return responses