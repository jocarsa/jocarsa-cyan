import subprocess
import json
import os
import sys
import shlex

class TinyDbConnector:
    """
    A tiny connector/wrapper around the C++ database engine.
    It spawns the engine as a subprocess with the appropriate command-line arguments.
    """

    def __init__(self, db_name: str):
        """
        :param path_to_engine: The path (absolute or relative) to the compiled C++ database engine.
        :param db_name:        The name of the database folder (passed as <databaseName> to the engine).
        """
        self.path_to_engine = "/var/www/html/jocarsa-cyan/cyan.out"
        self.db_name = db_name

    def insert_record(self, record_data: dict) -> bool:
        """
        Inserts a record (as JSON) into the database by calling the engine's 'insert' operation.
        :param record_data: A Python dictionary representing the record to be inserted.
        :return: True on success, False otherwise.
        """
        # Convert the Python dict to a JSON string (ensure ascii=False if you have non-ASCII data).
        json_str = json.dumps(record_data)

        # Build the command:
        #   <path_to_engine> <databaseName> insert "<json_str>"
        # We wrap <json_str> in quotes to ensure it's treated as one argument by the engine.
        command = [
            self.path_to_engine,
            self.db_name,
            "insert",
            json_str  # The engine will receive the JSON as argv[3]
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False  # We'll handle errors manually
            )
        except FileNotFoundError:
            print(f"Error: Could not find the database engine at: {self.path_to_engine}")
            return False

        # Check the result
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            # If there's an error, the engine prints to stderr
            print(f"Error inserting record:\n{result.stderr.strip()}")
            return False

    def select_records_raw(self) -> str:
        """
        Executes the engine's 'select' operation and returns the raw output as a string.
        Useful if you just want the exact console output.
        :return: The raw text output from the engine's 'select' command.
        """
        command = [
            self.path_to_engine,
            self.db_name,
            "select"
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
        except FileNotFoundError:
            print(f"Error: Could not find the database engine at: {self.path_to_engine}")
            return ""

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error selecting records:\n{result.stderr.strip()}")
            return ""

    def select_records(self) -> list:
        """
        Executes the engine's 'select' operation, parses the output,
        and returns a list of records (filename + JSON content).

        :return: A list of dicts like:
                 [
                   {
                     "filename": "<file name>",
                     "content": { ... parsed JSON ... }
                   },
                   ...
                 ]
        """
        raw_output = self.select_records_raw()
        if not raw_output:
            return []

        records = []
        lines = raw_output.splitlines()

        current_record = {}
        content_lines = []
        parsing_content = False

        for line in lines:
            line = line.strip()
            if line.startswith("File: "):
                # If there's an ongoing record (and we have some content lines),
                # we should finalize it first before starting a new one.
                if current_record and content_lines:
                    # Join content lines to get the JSON chunk, parse if possible
                    joined_content = "\n".join(content_lines)
                    try:
                        current_record["content"] = json.loads(joined_content)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, store raw
                        current_record["content"] = joined_content
                    records.append(current_record)

                # Start a new record
                filename = line[6:].strip()  # everything after "File: "
                current_record = {"filename": filename}
                content_lines = []
                parsing_content = False

            elif line.startswith("Content:"):
                # Next lines are JSON (until we reach an empty line or next "File:")
                parsing_content = True
                # Possibly there's nothing else in this line after "Content:"
                continue
            else:
                # It's either part of the JSON content or an empty line
                if line == "":  # empty line means we ended content
                    parsing_content = False
                elif parsing_content:
                    content_lines.append(line)

        # After the loop ends, check if there's a trailing record with content
        if current_record and content_lines:
            joined_content = "\n".join(content_lines)
            try:
                current_record["content"] = json.loads(joined_content)
            except json.JSONDecodeError:
                current_record["content"] = joined_content
            records.append(current_record)

        return records
