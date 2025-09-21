#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
from datetime import datetime


class EmailService:
    """Service for sending emails with HTML and plain text support."""
    
    def __init__(self, host: str, port: int, username: str, password: str, 
                 sender: str, recipient: str, public_url: str = ""):
        """Initialize the email service.
        
        Args:
            host: SMTP server hostname
            port: SMTP server port
            username: SMTP username
            password: SMTP password
            sender: Email sender address
            recipient: Email recipient address
            public_url: Public URL for the Linkding instance
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender
        self.recipient = recipient
        self.public_url = public_url
    
    def _create_html_content(self, bookmarks: List[Dict[str, Any]], tags: List[str]) -> str:
        """Create HTML content for the email.
        
        Args:
            bookmarks: List of bookmark dictionaries
            tags: List of tags that were queried
            
        Returns:
            HTML content string
        """
        # Create simple header
        header_html = ""
        if self.public_url:
            header_html = f"""
            <pre style="margin: 0; padding: 10px 0; border-bottom: 1px solid #ccc; font-family: monospace; font-size: 12px; color: #666;">
BOOKMARK REMINDER
Reminding you of the latest links at {self.public_url}
            </pre>
            """
        
        if not bookmarks:
            return f"""
            <html>
            <body style="font-family: monospace; margin: 0; padding: 20px; background: #fff; color: #000; font-size: 12px; line-height: 1.4;">
                {header_html}
                <pre style="margin: 20px 0;">
No bookmarks found for tags: {', '.join(f"#{tag}" for tag in tags)}
                </pre>
            </body>
            </html>
            """
        
        html_parts = [
            "<html>",
            "<body style='font-family: monospace; margin: 0; padding: 20px; background: #fff; color: #000; font-size: 12px; line-height: 1.4;'>",
            header_html,
            f"<pre style='margin: 20px 0;'>{len(bookmarks)} bookmarks for {', '.join(f'#{tag}' for tag in tags)}</pre>"
        ]
        
        for bookmark in bookmarks:
            title = bookmark.get("title") or "(no title)"
            url = bookmark.get("url", "")
            bookmark_tags = bookmark.get("tag_names", [])
            query_tag = bookmark.get("_query_tag", "")
            
            # Clean URL - remove any tags that might be appended
            if url and '#' in url:
                url = url.split('#')[0]
            
            # Format tags simply
            tag_text = ""
            if bookmark_tags:
                tag_text = f" | {', '.join(bookmark_tags)}"
            html_parts.extend([
                "<pre style='margin: 5px 0; padding: 2px 0;'>",
                f"<a href='{url}' style='color: #0066cc; text-decoration: none;'>{title}</a> | #{query_tag}{tag_text}",
                f"{url}",
                "</pre>"
            ])
        
        html_parts.extend([
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _create_plain_text_content(self, bookmarks: List[Dict[str, Any]], tags: List[str]) -> str:
        """Create plain text content for the email.
        
        Args:
            bookmarks: List of bookmark dictionaries
            tags: List of tags that were queried
            
        Returns:
            Plain text content string
        """
        # Create simple header
        header_lines = []
        if self.public_url:
            header_lines = [
                "BOOKMARK REMINDER",
                f"Reminding you of the latest links at {self.public_url}",
                "-" * 50,
                ""
            ]
        
        if not bookmarks:
            return "\n".join(header_lines + [f"No bookmarks found for tags: {', '.join(f'#{tag}' for tag in tags)}"])
        
        lines = header_lines + [
            f"{len(bookmarks)} bookmarks for {', '.join(f'#{tag}' for tag in tags)}",
            ""
        ]
        
        for bookmark in bookmarks:
            title = bookmark.get("title") or "(no title)"
            url = bookmark.get("url", "")
            bookmark_tags = bookmark.get("tag_names", [])
            query_tag = bookmark.get("_query_tag", "")
            
            # Clean URL - remove any tags that might be appended
            if url and '#' in url:
                url = url.split('#')[0]
            
            tag_text = ""
            if bookmark_tags:
                tag_text = f" | {', '.join(bookmark_tags)}"
            
            lines.extend([
                f"{title} | #{query_tag}{tag_text}",
                url
            ])
        
        return "\n".join(lines)
    
    def send_bookmark_reminder(self, bookmarks: List[Dict[str, Any]], tags: List[str], 
                              subject: Optional[str] = None) -> bool:
        """Send bookmark reminder email.
        
        Args:
            bookmarks: List of bookmark dictionaries
            tags: List of tags that were queried
            subject: Custom subject line (optional)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender
            msg["To"] = self.recipient
            
            if subject:
                msg["Subject"] = subject
            else:
                tag_list = ", ".join(f"#{tag}" for tag in tags)
                msg["Subject"] = f"Bookmarks: {tag_list}"
            
            # Create both plain text and HTML versions
            plain_text = self._create_plain_text_content(bookmarks, tags)
            html_content = self._create_html_content(bookmarks, tags)
            
            # Attach both versions
            msg.attach(MIMEText(plain_text, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            
            # Send email
            if self.port == 465:
                with smtplib.SMTP_SSL(self.host, self.port, timeout=30) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(self.username, self.password)
                    server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
