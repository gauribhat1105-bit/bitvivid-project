import json
import re

def process_command(raw_output: str):

    try:

        raw_output = raw_output.strip()

        raw_output = raw_output.replace("```json", "")
        raw_output = raw_output.replace("```", "")

        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

        if not json_match:

            return {
                "action": "unknown"
            }

        command = json.loads(json_match.group())

        # Ensure schema fields exist
        return {
            "action": command.get("action", "unknown"),
            "camera_id": command.get("camera_id"),
            "camera_name": command.get("camera_name"),
            "place_name": command.get("place_name"),
            "object": command.get("object"),
            "intent": command.get("intent")
        }

    except Exception as e:

        print("Command parsing error:", e)

        return {
            "action": "unknown"
        }
