---
name: send-message
description: Draft and send a visitor's message to Pamudu's inbox (hiring, collaboration, a question, feedback). Read this as soon as a visitor wants to contact, hire, or leave a message for Pamudu.
---

# Sending Pamudu a message

The goal is a ready-to-send draft in front of the visitor in as few turns as possible. The chat shows the draft as an editable card with Send and Cancel buttons, so the visitor can change any field there. You write the draft; you do not interview the visitor.

## What you need from the visitor

Only two things: their **name** and their **email address** (so Pamudu can reply).

- If both are already in the conversation, draft straight away.
- If either is missing, ask for both in one short sentence, for example: "What's your name and email, so he can reply to you?"
- Never ask for a subject line. Never ask them to word the message. Never list the fields you need.

## Writing the draft

Write the subject and the message yourself from what the visitor has already said.

- **Subject:** short and specific, for example "Hiring enquiry", "Collaboration on a computer vision project", "Question about Y-Net".
- **Message:** first person, in the visitor's voice, two to four sentences. Say who they are, what they want, and invite a reply.
- Fix typos and tidy the wording, but keep their meaning.
- Use only what the visitor told you. Do not invent a company, a role, a salary, dates or any other detail.
- If they gave very little ("I want to hire him"), keep it short and general, for example: "Hi Pamudu, I'm Sunimal. I'd like to talk to you about a hiring opportunity. Could we set up a time to discuss it?"

## Sending

1. Call `send_message_to_pamudu` with the name, email, your subject and your message. The card appears and the chat waits for the visitor.
2. Do not ask "shall I send it?" in text. The card's buttons are the confirmation.
3. Read the tool's result before you say anything:
   - `sent` is true: confirm in one sentence that the message reached Pamudu's inbox.
   - It has an `error`: say plainly that the message could not be delivered and nothing was sent, then call `show_contact_card` so the visitor can reach him directly. Do not say a draft is showing, do not say it was sent, and do not tell them to click Send again.
   - The visitor cancelled: acknowledge it in one sentence and move on.

## Limits

Messages only ever go to Pamudu. You cannot email anyone else; say so if asked.
