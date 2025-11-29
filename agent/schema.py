# Function-call schema for OpenAI Realtime
extract_bant_schema = {
    "name": "submit_lead",
    "description": "Submit captured EdTech lead details.",
    "parameters": {
        "type": "object",
        "properties": {
            "conversation_id": {"type": "string", "description": "Unique conversation identifier for tracking"},
            "child_name": {"type": "string"},
            "child_class": {"type": "string"},
            "subjects": {"type": "string"},
            "exam_info": {"type": "string"},
            "budget_range": {"type": "string"},
            "decision_maker": {"type": "string"},
            "timeline": {"type": "string"},
            "urgency": {"type": "string"},
            "contact_phone": {"type": "string"}
        },
        "required": ["child_class", "subjects", "contact_phone"]
    }
}

def pretty_print_lead(data: dict):
    import json
    print("\n===== NEW LEAD CAPTURED =====")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("================================\n")