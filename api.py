from flask import Flask, jsonify
import imaplib
import email
from email.header import decode_header
import re

app = Flask(__name__)

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
USERNAME = "arufanguyen@gmail.com"
PASSWORD = "skibidi"  #pass api google 

@app.route('/read-email', methods=['GET'])
def read_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()
        latest_email_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                from_ = msg.get("From")
                to_ = msg.get("To") 
                body = None
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" not in content_disposition:
                            if content_type == "text/plain": 
                                body = part.get_payload(decode=True)
                                break
                else:
                    body = msg.get_payload(decode=True)
                body_text = body.decode() if body else "No body content"
                code_match = re.search(r'\b\d{6}\b', body_text)
                code = code_match.group(0) if code_match else None
                if code:
                    return jsonify({
                        "subject": subject,
                        "from": from_,
                        "to": to_, 
                        "verification_code": code
                    })
                else:
                    return jsonify({
                        "message": "No verification code found in the latest email"
                    })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
