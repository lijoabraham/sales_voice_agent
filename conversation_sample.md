# Sample Conversation: EdTech Sales Agent

This document contains a sample conversation between the voice agent and a parent, demonstrating the BANT-style lead qualification process.

---

## Conversation Sample

**Agent:** Hello! I'm Alex from XYZ Edtech. I'm here to help you find the best learning solutions for your child. How may I assist you today?

**Parent:** Hi, I'm looking for some help with my child's studies.

**Agent:** That's wonderful! I'd be happy to help you find the right program. To get started, could you please tell me which class or grade your child is currently studying in?

**Parent:** She's in 8th grade.

**Agent:** Great! And which subjects does she need help with?

**Parent:** Mainly Physics and Chemistry. She's struggling a bit with these subjects.

**Agent:** I understand. Physics and Chemistry can be challenging. Are there any specific exams or tests she's preparing for?

**Parent:** Yes, she's preparing for NEET exam next year. That's why we're looking for help now.

**Agent:** That's excellent planning! NEET preparation requires focused attention. May I ask, who typically makes the decisions about your child's education - is it you, your spouse, or both parents together?

**Parent:** Both my husband and I make decisions together about her education.

**Agent:** That's great to have both parents involved. Now, regarding the timeline - when would you like to start the program?

**Parent:** As soon as possible, actually. We want to get started right away.

**Agent:** I understand the urgency. How urgent would you say this need is - would you say it's immediate, or are you planning ahead?

**Parent:** It's pretty immediate. We want to start this week if possible.

**Agent:** Perfect! Now, to help us recommend the best program, could you share what budget range you're comfortable with? Please let me know in Indian Rupees.

**Parent:** We're looking at something under ₹10,000 per month.

**Agent:** Thank you for that information. To complete the process and have one of our counselors follow up with you, may I please have your contact phone number?

**Parent:** Sure, it's 8512131516.

**Agent:** Thank you! And just to confirm, what's your child's name?

**Parent:** Her name is Priya.

**Agent:** Perfect! Thank you so much for providing all this information, Priya's mom. I've captured all the details, and one of our counselors will reach out to you soon to discuss the best learning solutions for Priya's NEET preparation. Is there anything else I can help you with today?

**Parent:** No, that's all. Thank you!

**Agent:** You're welcome! Have a wonderful day, and we'll be in touch soon!

---

## Function Call Generated

After this conversation, the agent would call `submit_lead` with the following data:

```json
{
  "child_class": "8th grade",
  "subjects": "Physics, Chemistry",
  "contact_phone": "8512131516",
  "exam_info": "Preparing for NEET exam next year",
  "budget_range": "Under ₹10,000 per month",
  "decision_maker": "Both parents",
  "timeline": "As soon as possible",
  "urgency": "Immediate"
}
```

---

## Lead Data Captured

```json
{
  "conversation_id": "uuid-generated-by-system",
  "child_name": "Priya",
  "child_class": "8th grade",
  "subjects": "Physics, Chemistry",
  "exam_info": "Preparing for NEET exam next year",
  "budget_range": "Under ₹10,000 per month",
  "decision_maker": "Both parents",
  "timeline": "As soon as possible",
  "urgency": "Immediate",
  "contact_phone": "8512131516"
}
```

---

## Notes

- The agent collects **required fields** first: `child_class`, `subjects`, and `contact_phone`
- **Optional fields** are collected naturally during the conversation
- The agent maintains a warm, friendly, and patient tone throughout
- All budget discussions are in Indian Rupees (₹)
- The agent asks one question at a time to keep the conversation natural
- After collecting all information, the agent calls `submit_lead` function once
- The conversation ends politely after the lead is submitted

