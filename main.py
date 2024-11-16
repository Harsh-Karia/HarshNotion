from notion_client import Client
from config import API_KEY, DATABASE_ID #Import API Key and the database ID, which is provided in config. Do not usually push actual keys.
import datetime
import re

# Initialize Notion Client
notion = Client(auth=API_KEY)

# Send Mail Function
def send_mail(sender, recipient, message):
    if not sender or not recipient:
        raise ValueError("Sender and recipient cannot be empty.")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag = "general"  # Default tag for untagged emails
    message_with_metadata = f"[{tag}] [{timestamp}] {message}"

    response = notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Message": {
                "title": [
                    {
                        "text": {
                            "content": message_with_metadata
                        }
                    }
                ]
            },
            "Sender": {
                "rich_text": [
                    {
                        "text": {
                            "content": sender
                        }
                    }
                ]
            },
            "Recipient": {
                "rich_text": [
                    {
                        "text": {
                            "content": recipient
                        }
                    }
                ]
            }
        }
    )
    page_id = response["id"]
    print(f"Message sent from {sender} to {recipient}")
    return page_id

# Extracting the timestamp and message
def tag_email(user):
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            # Only show emails where the user is the recipient
            "property": "Recipient", 
            "rich_text": {"equals": user}
        }
    )

    emails = response['results']
    if not emails:
        print("No emails found to tag.")
        return

    print("Select an email to tag by entering the corresponding number:")
    for index, email in enumerate(emails):
        sender = email['properties']['Sender']['rich_text'][0]['text']['content']
        recipient = email['properties']['Recipient']['rich_text'][0]['text']['content']
        message_with_metadata = email['properties']['Message']['title'][0]['text']['content']

        # Extract timestamp and message content based on the number of bracketed segments (aka tags)
        match = re.findall(r"\[(.*?)\]", message_with_metadata)
        if len(match) == 3:
            general_tag, user_specific_tag, timestamp = match
            message = message_with_metadata.split(f"[{timestamp}] ", 1)[1]
        elif len(match) == 2:
            general_tag, timestamp = match
            message = message_with_metadata.split(f"[{timestamp}] ", 1)[1]
            user_specific_tag = "general"
        elif len(match) == 1:
            timestamp = match[0]
            message = message_with_metadata.split(f"[{timestamp}] ", 1)[1]
            general_tag = "general"
            user_specific_tag = "general"
        else:
            timestamp = "Unknown"
            general_tag = "general"
            user_specific_tag = "general"
            message = message_with_metadata

        print(f"{index + 1}. From: {sender}\n   To: {recipient}\n   Current Tag: {user_specific_tag}\n   Message: {message}")

    try:
        choice = int(input("Enter the number of the email you want to tag: ")) - 1
        if 0 <= choice < len(emails):
            selected_email = emails[choice]
            page_id = selected_email['id']
            tag = input("Enter the tag (work, social, promotions): ").lower()
            if tag not in ["work", "social", "promotions"]:
                print("Invalid tag. Please use 'work', 'social', or 'promotions'.")
                return

            # Get the original message content from the selected email
            original_message_with_metadata = selected_email['properties']['Message']['title'][0]['text']['content']
            match = re.findall(r"\[(.*?)\]", original_message_with_metadata)
            
            # Extract the original message without any tags
            original_message = re.sub(r"(\[.*?\] )+", "", original_message_with_metadata)
            
            # Create new message with the metadata
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_message_with_metadata = f"[general] [{tag}:{user}] [{timestamp}] {original_message}"

            notion.pages.update(
                page_id=page_id,
                properties={
                    "Message": {
                        "title": [
                            {
                                "text": {
                                    "content": new_message_with_metadata
                                }
                            }
                        ]
                    }
                }
            )
            print(f"Email tagged as {tag} successfully for {user}.")
        else:
            print("Invalid choice. Please select a number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def view_sent_inbox(user):
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={"property": "Sender", "rich_text": {"equals": user}}
    )

    print(f"Sent messages by {user}:")
    for email in response['results']:
        recipient = email['properties']['Recipient']['rich_text'][0]['text']['content']
        message_with_metadata = email['properties']['Message']['title'][0]['text']['content']

        # Extract timestamp and message content without displaying user-specific tags
        match = re.findall(r"\[(.*?)\]", message_with_metadata)
        timestamp = match[-1] if match else "Unknown"
        message = re.sub(r"(\[.*?\] )+", "", message_with_metadata)

        print(f"To: {recipient}\nSent on: {timestamp}\nMessage: {message}\n")

# Read Inbox Function
def read_inbox(user):
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={"property": "Recipient", "rich_text": {"equals": user}}
    )

    print(f"Inbox for {user}:")
    for email in response['results']:
        sender = email['properties']['Sender']['rich_text'][0]['text']['content']
        message_with_metadata = email['properties']['Message']['title'][0]['text']['content']

        # Determine the correct tag and timestamp
        match = re.findall(r"\[(.*?)\]", message_with_metadata)
        if len(match) == 3:
            general_tag, user_specific_tag, timestamp = match
        elif len(match) == 2:
            general_tag, timestamp = match
            user_specific_tag = "general"
        elif len(match) == 1:
            timestamp = match[0]
            general_tag = "general"
            user_specific_tag = "general"
        else:
            timestamp = "Unknown"
            general_tag = "general"
            user_specific_tag = "general"

        # Remove tags from message content for display
        message = re.sub(r"(\[.*?\] )+", "", message_with_metadata)

        print(f"From: {sender}\nSent on: {timestamp}\nMessage: {message}\n")

def view_tagged_inbox(user, tag):
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "Message",
            "title": {
                "contains": f"[{tag}:{user}]"
            }
        }
    )

    print(f"{tag.capitalize()} inbox for {user}:")
    for email in response['results']:
        sender = email['properties']['Sender']['rich_text'][0]['text']['content']
        recipient = email['properties']['Recipient']['rich_text'][0]['text']['content']
        message_with_metadata = email['properties']['Message']['title'][0]['text']['content']

        # Extract timestamp and message for tagged messages
        match = re.findall(r"\[(.*?)\]", message_with_metadata)
        timestamp = match[-1] if match else "Unknown"
        message = re.sub(r"(\[.*?\] )+", "", message_with_metadata)

        print(f"From: {sender}\nTo: {recipient}\nSent on: {timestamp}\nMessage: {message}\n")


def delete_email(user):
    # Query the database for emails sent or received by the user
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "or": [
                {"property": "Sender", "rich_text": {"equals": user}},
                {"property": "Recipient", "rich_text": {"equals": user}}
            ]
        }
    )

    emails = response['results']
    if not emails:
        print("No emails found for deletion.")
        return

    # Display emails and their details with numbered ordering
    print("Select an email to delete by entering the corresponding number:")
    for index, email in enumerate(emails):
        sender = email['properties']['Sender']['rich_text'][0]['text']['content']
        recipient = email['properties']['Recipient']['rich_text'][0]['text']['content']
        message_with_metadata = email['properties']['Message']['title'][0]['text']['content']

        # Extract timestamp and message content based on brackets/tags
        match = re.findall(r"\[(.*?)\]", message_with_metadata)
        if len(match) == 3:  # Case with tag and timestamp
            _, _, timestamp = match
            message = message_with_metadata.split(f"[{timestamp}] ", 1)[1]
        elif len(match) == 2:  # Case with just a general tag and timestamp
            _, timestamp = match
            message = message_with_metadata.split(f"[{timestamp}] ", 1)[1]
        elif len(match) == 1:  # Case with only a timestamp
            timestamp = match[0]
            message = message_with_metadata.split(f"[{timestamp}] ", 1)[1]
        else:
            timestamp = "Unknown"
            message = message_with_metadata

        print(f"{index + 1}. From: {sender}\n   To: {recipient}\n   Sent on: {timestamp}")
        print(f"   Message: {message}")

    # Prompt user to select an email to delete
    try:
        choice = int(input("Enter the number of the email you want to delete: ")) - 1
        if 0 <= choice < len(emails):
            page_id = emails[choice]['id']
            # Archive (delete) the selected email by page_id
            notion.pages.update(page_id=page_id, archived=True)
            print("Email deleted successfully.")
        else:
            print("Invalid choice. Please select a number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Main CLI Loop
def main():
    print("Welcome to NotionMail!")
    while True:
        choice = input("Choose an option by typing: send, read, delete, sent, tag, view_social, view_work, view_promotions, or exit: ").lower()
        if choice == "send":
            sender = input("Sender: ")
            recipient = input("Recipient: ")
            message = input("Message: ")
            send_mail(sender, recipient, message)
        elif choice == "read":
            user = input("User to read inbox from: ")
            read_inbox(user)
        elif choice == "sent":
            user = input("User to read sent emails from: ")
            view_sent_inbox(user)
        elif choice == "delete":
            user = input("User to delete emails from: ")
            delete_email(user)
        elif choice == "tag":
            user = input("User to tag emails for: ")
            tag_email(user)
        elif choice == "view_social":
            user = input("User to view social inbox for: ")
            view_tagged_inbox(user, "social")
        elif choice == "view_work":
            user = input("User to view work inbox for: ")
            view_tagged_inbox(user, "work")
        elif choice == "view_promotions":
            user = input("User to view promotions inbox for: ")
            view_tagged_inbox(user, "promotions")
        elif choice == "exit":
            break


if __name__ == "__main__":
    main()
