#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from typing import List
from dotenv import load_dotenv
from linkding_client import LinkdingClient
from email_service import EmailService

# Load environment variables from .env file
load_dotenv()

# ---------- CONFIG ----------
# Linkding
LINKDING_URL        = os.getenv("LINKDING_URL", "http://192.168.50.5:9090")
LINKDING_PUBLIC_URL = os.getenv("LINKDING_PUBLIC_URL", LINKDING_URL)
LINKDING_TOKEN      = os.getenv("LINKDING_TOKEN")
LINKDING_TAGS       = os.getenv("LINKDING_TAGS", "2do")

# SMTP
SMTP_HOST      = os.getenv("SMTP_HOST")
SMTP_PORT      = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME  = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD  = os.getenv("SMTP_PASSWORD")
SMTP_SENDER    = os.getenv("SMTP_SENDER")
SMTP_RECIPIENT = os.getenv("SMTP_RECIPIENT")

# Validate required environment variables
required_vars = {
    "LINKDING_TOKEN": LINKDING_TOKEN,
    "SMTP_HOST": SMTP_HOST,
    "SMTP_USERNAME": SMTP_USERNAME,
    "SMTP_PASSWORD": SMTP_PASSWORD,
    "SMTP_SENDER": SMTP_SENDER,
    "SMTP_RECIPIENT": SMTP_RECIPIENT,
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
# ----------------------------


def parse_tags(tags_string: str) -> List[str]:
    """Parse comma-separated tags string into a list.
    
    Args:
        tags_string: Comma-separated tags string
        
    Returns:
        List of cleaned tag names
    """
    if not tags_string:
        return ["2do"]  # Default tag
    
    return [tag.strip() for tag in tags_string.split(",") if tag.strip()]


async def remind() -> None:
    """Main function to fetch bookmarks and send email reminder."""
    # Parse tags from environment variable
    tags = parse_tags(LINKDING_TAGS)
    
    # Initialize services
    linkding_client = LinkdingClient(LINKDING_URL, LINKDING_TOKEN)
    email_service = EmailService(
        host=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        sender=SMTP_SENDER,
        recipient=SMTP_RECIPIENT,
        public_url=LINKDING_PUBLIC_URL
    )
    
    try:
        # Fetch bookmarks for all tags
        print(f"Fetching bookmarks for tags: {', '.join(f'#{tag}' for tag in tags)}")
        bookmarks = await linkding_client.get_bookmarks_by_tags(tags)
        
        print(f"Found {len(bookmarks)} bookmarks")
        
        # Send email with HTML and plain text versions
        success = email_service.send_bookmark_reminder(bookmarks, tags)
        
        if success:
            print("Email sent successfully!")
        else:
            print("Failed to send email")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await linkding_client.close()


if __name__ == "__main__":
    asyncio.run(remind())
