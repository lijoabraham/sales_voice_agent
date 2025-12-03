# Minimal Conversation Sample: EdTech Sales Agent

A shorter conversation sample where the parent provides only the required information.

---

## Conversation Sample (Minimal)

**Agent:** Hello! I'm Alex from XYZ Edtech. I'm here to help you find the best learning solutions for your child. How may I assist you today?

**Parent:** Hi, I need help with my son's studies.

**Agent:** I'd be happy to help! Which class is your child currently in?

**Parent:** He's in 10th grade.

**Agent:** Great! And which subjects does he need help with?

**Parent:** Math and Science.

**Agent:** Perfect! To have one of our counselors follow up with you, could I please get your contact phone number?

**Parent:** Sure, it's 9876543210.

**Agent:** Thank you! I've noted down that your child is in 10th grade, needs help with Math and Science, and your contact number is 9876543210. One of our counselors will reach out to you soon to discuss the best learning solutions. Is there anything else I can help you with?

**Parent:** No, that's all. Thanks!

**Agent:** You're welcome! Have a great day!

---

## Function Call Generated

```json
{
  "child_class": "10th grade",
  "subjects": "Math and Science",
  "contact_phone": "9876543210"
}
```

---

## Lead Data Captured

```json
{
  "conversation_id": "uuid-generated-by-system",
  "child_class": "10th grade",
  "subjects": "Math and Science",
  "contact_phone": "9876543210",
  "child_name": null,
  "exam_info": null,
  "budget_range": null,
  "decision_maker": null,
  "timeline": null,
  "urgency": null
}
```

---

## Notes

- This demonstrates that the agent can work with minimal information
- Only required fields (`child_class`, `subjects`, `contact_phone`) are collected
- The agent still calls `submit_lead` successfully with optional fields as `null`
- The conversation remains polite and professional even when information is limited

