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
                 sender: str, recipient: str):
        """Initialize the email service.
        
        Args:
            host: SMTP server hostname
            port: SMTP server port
            username: SMTP username
            password: SMTP password
            sender: Email sender address
            recipient: Email recipient address
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sender = sender
        self.recipient = recipient
    
    def _create_html_content(self, bookmarks: List[Dict[str, Any]], tags: List[str]) -> str:
        """Create HTML content for the email.
        
        Args:
            bookmarks: List of bookmark dictionaries
            tags: List of tags that were queried
            
        Returns:
            HTML content string
        """
        if not bookmarks:
            return f"""
            <html>
            <body>
                <h2>📚 Linkding Bookmark Reminder</h2>
                <p>No bookmarks found for tags: <strong>{', '.join(f"#{tag}" for tag in tags)}</strong></p>
                <p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            </body>
            </html>
            """
        
        html_parts = [
            "<html>",
            "<head>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "h2 { color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }",
            ".bookmark { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }",
            ".bookmark-title { font-size: 18px; font-weight: bold; margin-bottom: 8px; }",
            ".bookmark-title a { color: #007acc; text-decoration: none; }",
            ".bookmark-title a:hover { text-decoration: underline; }",
            ".bookmark-url { color: #666; font-size: 14px; margin-bottom: 5px; }",
            ".bookmark-tags { color: #888; font-size: 12px; }",
            ".tag { background-color: #e1ecf4; color: #39739d; padding: 2px 6px; border-radius: 3px; margin-right: 5px; }",
            ".footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h2>📚 Linkding Bookmark Reminder</h2>",
            f"<p>Found <strong>{len(bookmarks)}</strong> bookmarks for tags: <strong>{', '.join(f'#{tag}' for tag in tags)}</strong></p>",
            "<hr>"
        ]
        
        for bookmark in bookmarks:
            title = bookmark.get("title") or "(no title)"
            url = bookmark.get("url", "")
            bookmark_tags = bookmark.get("tag_names", [])
            query_tag = bookmark.get("_query_tag", "")
            
            # Create clickable title
            if url:
                title_html = f'<a href="{url}" target="_blank">{title}</a>'
            else:
                title_html = title
            
            # Format tags
            tag_html = ""
            if bookmark_tags:
                tag_html = " | Tags: " + " ".join([f'<span class="tag">{tag}</span>' for tag in bookmark_tags])
            
            html_parts.extend([
                "<div class='bookmark'>",
                f"<div class='bookmark-title'>{title_html}</div>",
                f"<div class='bookmark-url'>{url}</div>",
                f"<div class='bookmark-tags'>Found via: #{query_tag}{tag_html}</div>",
                "</div>"
            ])
        
        html_parts.extend([
            "<div class='footer'>",
            f"<p><em>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>",
            "</div>",
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
        if not bookmarks:
            return f"No bookmarks found for tags: {', '.join(f'#{tag}' for tag in tags)}"
        
        lines = [
            f"Found {len(bookmarks)} bookmarks for tags: {', '.join(f'#{tag}' for tag in tags)}",
            "=" * 60
        ]
        
        for bookmark in bookmarks:
            title = bookmark.get("title") or "(no title)"
            url = bookmark.get("url", "")
            bookmark_tags = bookmark.get("tag_names", [])
            query_tag = bookmark.get("_query_tag", "")
            
            lines.extend([
                "",
                title,
                url,
                f"Found via: #{query_tag}" + (f" | Tags: {', '.join(bookmark_tags)}" if bookmark_tags else ""),
                "-" * 40
            ])
        
        lines.extend([
            "",
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
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
                msg["Subject"] = f"Your Linkding Bookmark Reminder for tags: {tag_list}"
            
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
