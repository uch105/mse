# Copyright 2025 Tanvir Saklan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_email(
    subject: str,
    to: list[str],
    context: dict = None,
    template_name: str | None = None,
    body: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[str] | None = None,
    html: bool = True,
    from_email: str | None = None,
) -> bool:
    """
    Sends an email using Django's EmailMessage with optional HTML, CC, BCC, and attachments.
    """
    try:
        # Prepare body
        if template_name:
            message_body = render_to_string(template_name, context or {})
        elif body:
            message_body = body
        else:
            raise ValueError("Either template_name or body must be provided")

        # Create EmailMessage
        email = EmailMessage(
            subject=subject,
            body=message_body,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=to,
            cc=cc or [],
            bcc=bcc or [],
        )

        # HTML support
        if html:
            email.content_subtype = "html"

        # Attachments
        if attachments:
            for file_path in attachments:
                try:
                    email.attach_file(file_path)
                except Exception as e:
                    print(f"Attachment error for {file_path}: {e}")

        email.send(fail_silently=False)
        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False