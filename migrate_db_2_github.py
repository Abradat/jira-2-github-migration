import traceback
import json
from github_tools import *
from config_reader import load_config
from db_utils import *

def main():
    config = load_config("config.json")
    db_file = config["database"]
    repo = config["github_repo"]
    owner = config["github_username"]
    project_name = config["github_project_name"]

    # project_id = get_project_id(owner, repo, project_name) # This is for personal projects
    project_id = get_org_project_id(owner, project_name) # This is for organization projects
    field_ids = get_field_ids(project_id)
    
    issues = fetch_issues_from_db(db_file, 0, config["migrate_offset_number"])
    for issue in issues:
        issue_id = issue[3]
        title = issue[1]
        body = issue[15]
        assignees = [issue[7]] if issue[7] else []
        labels = json.loads(issue[19])
        epic_value = issue[20]
        priority_value = issue[6]
        
        try:
            response_issue_number = create_issue(repo, owner, title, body, assignees, labels, issue_id, db_file)
            update_issue_status(db_file, issue_id, True)

            comments = json.loads(issue[11]) if issue[11] else None
            if comments:
                for comment in comments:
                    comment_body = f"{comment['user']} on {comment['date']}:\n\n{comment['content']}"
                    create_comment(repo, owner, response_issue_number, comment_body)
            update_comment_status(db_file, issue_id, True)

            if config["add_to_project"]:
                issue_node_id = get_issue_node_id(db_file, issue_id)

                project_issue_response = add_issue_to_project(project_id, issue_node_id)

                project_issue_id = project_issue_response['data']['addProjectV2ItemById']['item']['id']

                update_project_issue_node_id(db_file, issue_id, project_issue_id)

                # Map custom fields to their IDs and use option IDs for single select fields
                custom_fields_with_ids = []

                # Assign Status: ALCS-Backlog
                status_field = field_ids.get("Status")
                if status_field and "options" in status_field and config["add_status"]:
                    status_option_id = next((opt["id"] for opt in status_field["options"] if opt["name"] == "ALCS Backlog"), None)
                    if status_option_id:
                        custom_fields_with_ids.append({"fieldId": status_field["id"], "value": status_option_id, "type": "option"})

                # Assign Epic
                epic_field = field_ids.get("Epic")
                if epic_field and config["add_epic"]:
                    custom_fields_with_ids.append({"fieldId": epic_field["id"], "value": epic_value, "type": "text"})

                # Assign Priority
                priority_field = field_ids.get("Priority")
                if priority_field and "options" in priority_field and config["add_priority"]:
                    priority_option_id = next((opt["id"] for opt in priority_field["options"] if opt["name"].lower() == priority_value.lower()), None)
                    if priority_option_id:
                        custom_fields_with_ids.append({"fieldId": priority_field["id"], "value": priority_option_id, "type": "option"})

                # Add custom fields to the project
                response = add_custom_fields_to_project(project_id, project_issue_id, custom_fields_with_ids)
                if 'errors' not in response:
                    update_project_fields_status(db_file, issue_id, True)
        except Exception as e:
            print(f"Failed to create issue, comment, or project fields for issue_id {issue_id}: {e}")
            traceback.print_exc()
        print("=========================================")

if __name__ == "__main__":
    main()
