---
name: send-message
description: Draft and send a visitor's message to Pamudu's inbox (hiring, collaboration, a question, feedback). Read this as soon as a visitor wants to contact, hire, or leave a message for Pamudu.
---

# Sending Pamudu a message

The goal is a ready-to-send draft in front of the visitor in as few turns as possible. Two chat components do the work, so you never ask for details in plain text:

- a **question panel** (`ask_visitor`) that collects the visitor's name and email in one small form, and
- a **draft card** (`send_message_to_pamudu`) that shows the message you wrote, with Send and Cancel buttons.

## Step 1: get the name and email with the question panel

You need the visitor's **name** and **email address** (so Pamudu can reply). Nothing else.

- If both are already in the conversation, skip to step 2.
- Otherwise call `ask_visitor` with `fields=["Your name", "Your email"]` and a short question such as "Who should Pamudu reply to?". Leave out a field you already have. The visitor fills in the panel and you get their answers back.
- Never ask for a name, an email, a subject line or the wording of the message in plain text. Never list the fields you need.
- If the visitor skips the panel, say that you need a name and an email to send a message, and offer the contact card instead.

## Step 2: write the draft

Write the subject and the message yourself from what the visitor has already said.

- **Subject:** short and specific, for example "Hiring enquiry", "Collaboration on a computer vision project", "Question about Y-Net".
- **Message:** first person, in the visitor's voice, two to four sentences. Say who they are, what they want, and invite a reply.
- Fix typos and tidy the wording, but keep their meaning.
- Use only what the visitor told you. Do not invent a company, a role, a salary, dates or any other detail.
- If they gave very little ("I want to hire him"), keep it short and general, for example: "Hi Pamudu, I'd like to talk to you about a hiring opportunity. Could we set up a time to discuss it?"
- Do not invent a name or sign with one you were not given.

## Step 3: show the draft card

1. Call `send_message_to_pamudu` with the name, the email, your subject and your message. Do not write any text before the call. The draft card appears and the chat waits for the visitor, who can still edit any field.
2. Do not ask "shall I send it?" in text. The card's buttons are the confirmation.
3. Read the tool's result before you say anything:
   - `sent` is true: confirm in one sentence that the message reached Pamudu's inbox.
   - It has an `error`: say plainly that the message could not be delivered and nothing was sent, then call `show_contact_card` so the visitor can reach him directly. Do not say a draft is showing, do not say it was sent, and do not tell them to click Send again.
   - The visitor cancelled: acknowledge it in one sentence and move on.

## Limits

Messages only ever go to Pamudu. You cannot email anyone else; say so if asked.
