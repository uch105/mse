from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import timedelta

from core.models import Blog,PressRelease,Career

User = get_user_model()


def send_new_content_notification():
    since = timezone.now() - timedelta(days=1)

    content_types = [
        (Blog, "Blog Post"),
        (PressRelease, "Press Release"),
        (Career, "Career Post"),
    ]

    items = []

    for model, label in content_types:
        qs = model.objects.filter(created_at__gte=since, notified=False)

        for obj in qs:
            items.append({
                "type": label,
                "title": obj.title,
                "summary": getattr(obj, "excerpt") or getattr(obj, "disclaimer") or getattr(obj, "description") or "No summary available",
                "url": obj.get_absolute_url() if hasattr(obj, "get_absolute_url") else "",
                "instance": obj
            })

    if not items:
        return  # nothing to send

    # Render HTML email
    html_body = render_to_string("emails/new_content_notification.html", {
        "items": items
    })

    subject = "New Updates Published"
    users = User.objects.all()
    recipients = [user.email for user in users if user.email]

    email = EmailMultiAlternatives(
        subject,
        "",  # plain-text body (optional)
        settings.DEFAULT_FROM_EMAIL,
        recipients
    )
    email.attach_alternative(html_body, "text/html")
    email.send()

    # Mark as notified
    for item in items:
        inst = item["instance"]
        inst.notified = True
        inst.save()