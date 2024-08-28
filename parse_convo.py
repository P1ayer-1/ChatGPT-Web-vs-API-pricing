#
##
##########################################################################################################################################################
### MOST OF THE CODE IN THIS FILE COMES FROM: https://community.openai.com/t/decoding-exported-data-by-parsing-conversations-json-and-or-chat-html/403144/6
##########################################################################################################################################################
##
#



"""
This script processes conversation data from a JSON file, extracts messages,
and writes them to text files. It also creates a summary JSON file with a summary
of the conversations. The script is designed to be run as a command-line interface (CLI),
allowing the user to specify the input JSON file and output directory.

Usage:
    python script_name.py /path/to/conversations.json /path/to/output_directory
"""

import unicodedata
import json
import re
from datetime import datetime
from pathlib import Path
from utils import read_file


def extract_message_parts(message):
    """
    Extract the text parts from a message content.

    Args:
        message (dict): A message object.

    Returns:
        list: List of text parts.
    """
    content = message.get("content")
    if content and content.get("content_type") == "text":
        return content.get("parts", [])
    return []


def get_author_name(message):
    """
    Get the author name from a message.

    Args:
        message (dict): A message object.

    Returns:
        str: The author's role or a custom label.
    """
    author = message.get("author", {}).get("role", "")
    if author == "assistant":
        return "ChatGPT"
    elif author == "system":
        return "Custom user info"
    return author


def get_conversation_messages(conversation):
    """
    Extract messages from a conversation.

    Args:
        conversation (dict): A conversation object.

    Returns:
        list: List of messages with author and text.
    """
    messages = []
    current_node = conversation.get("current_node")
    mapping = conversation.get("mapping", {})
    while current_node:
        node = mapping.get(current_node, {})
        message = node.get("message") if node else None
        if message:
            parts = extract_message_parts(message)
            author = get_author_name(message)
            if parts and len(parts) > 0 and len(parts[0]) > 0:
                if author != "system" or message.get("metadata", {}).get(
                    "is_user_system_message"
                ):
                    messages.append({"author": author, "text": parts[0]})
        current_node = node.get("parent") if node else None
    return messages[::-1]


def create_directory(base_dir, date):
    """
    Create a directory based on the date.

    Args:
        base_dir (Path): Base output directory.
        date (datetime): The date to base the directory name on.

    Returns:
        Path: The path of the created directory.
    """
    directory_name = date.strftime("%Y_%m")
    directory_path = base_dir / directory_name
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def sanitize_title(title):
    """
    Sanitize the title to create a valid file name, preserving non-ASCII characters.

    Args:
        title (str): The title of the conversation.

    Returns:
        str: Sanitized title.
    """
    title = unicodedata.normalize("NFKC", title)
    title = re.sub(r'[<>:"/\\|?*\x00-\x1F\s]', '_', title)
    return title[:140]


def create_file_name(directory_path, title, date):
    """
    Create a sanitized file name.

    Args:
        directory_path (Path): The directory where the file will be saved.
        title (str): The title of the conversation.
        date (datetime): The date to base the file name on.

    Returns:
        Path: The path of the created file.
    """
    sanitized_title = sanitize_title(title)
    return (
        directory_path / f"{date.strftime('%Y_%m_%d')}_{sanitized_title}.txt"
    )


def write_messages_to_file(file_path, messages):
    """
    Write messages to a text file.

    Args:
        file_path (Path): The path of the file to write to.
        messages (list): List of messages to write.
    """
    with file_path.open("w", encoding="utf-8") as file:
        for message in messages:
            file.write(f"{message['author']}\n")
            file.write(f"{message['text']}\n")


def update_conversation_summary(summary, directory_name, conversation, date, messages):
    """
    Update the conversation summary dictionary.

    Args:
        summary (dict): The conversation summary dictionary.
        directory_name (str): The name of the directory.
        conversation (dict): The conversation object.
        date (datetime): The updated date of the conversation.
        messages (list): List of messages in the conversation.
    """
    if directory_name not in summary:
        summary[directory_name] = []

    summary[directory_name].append(
        {
            "title": conversation.get("title", "Untitled"),
            "create_time": datetime.fromtimestamp(
                conversation.get("create_time")
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": date.strftime("%Y-%m-%d %H:%M:%S"),
            "messages": messages,
        }
    )


def write_summary_json(output_dir, summary):
    """
    Write the conversation summary to a JSON file.

    Args:
        output_dir (Path): The output directory.
        summary (dict): The conversation summary to write.
    """
    summary_json_path = output_dir / "conversation_summary.json"
    with summary_json_path.open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, ensure_ascii=False, indent=4)


def write_conversations_and_summary(conversations_data, output_dir, return_only=False):
    """
    Write conversation messages to text files and create a conversation summary JSON file.

    Args:
        conversations_data (list): List of conversation objects.
        output_dir (Path): Directory to save the output files.
        return_only (bool, optional): Return only the created directories and files. Defaults to False.

    Returns:
        list or tuple: List of created directories and files, or conversation summary if return_only is True.
    """
    created_directories_info = []
    conversation_summary = {}

    for conversation in conversations_data:
        updated = conversation.get("update_time")
        if not updated:
            continue

        updated_date = datetime.fromtimestamp(updated)
        if not return_only:
            print(f"Processing conversation {conversation['title']}")
            directory_path, file_name = create_conversation_path(output_dir, conversation, updated_date)

        messages = get_conversation_messages(conversation)

        if not return_only:
            print(f"Writing messages to {file_name}")
            write_messages_to_file(file_name, messages)

        update_conversation_summary(
            conversation_summary,
            directory_path.name if not return_only else updated_date.strftime("%Y_%m"),
            conversation,
            updated_date,
            messages,
        )

        if not return_only:
            created_directories_info.append(
                {"directory": str(directory_path), "file": str(file_name)}
            )

    if not return_only:
        write_summary_json(output_dir, conversation_summary)

    output = conversation_summary if return_only else (created_directories_info, conversation_summary)
    return output

def create_conversation_path(output_dir, conversation, updated_date):
    """
    Create a directory and file path for a conversation.

    Args:
        output_dir (Path): The output directory.
        conversation (dict): A conversation object.
        updated_date (datetime): The updated date of the conversation.

    Returns:
        tuple: (directory_path, file_name)
    """
    directory_path = create_directory(output_dir, updated_date)
    title = conversation.get("title", "Untitled")
    file_name = create_file_name(directory_path, title, updated_date)
    return directory_path, file_name




def process_conversations(args):
    conversations_data = read_file(args.input_file)

    output = write_conversations_and_summary(
        conversations_data, args.output_dir, args.return_only
    )
    
    return output
