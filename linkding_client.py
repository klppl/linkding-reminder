#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import List, Dict, Any, Optional
from aiolinkding import async_get_client


class LinkdingClient:
    """Client for interacting with Linkding API."""
    
    def __init__(self, url: str, token: str):
        """Initialize the Linkding client.
        
        Args:
            url: Linkding instance URL
            token: API token for authentication
        """
        self.url = url
        self.token = token
        self._client = None
    
    async def _get_client(self):
        """Get or create the async client."""
        if self._client is None:
            self._client = await async_get_client(self.url, self.token)
        return self._client
    
    async def get_bookmarks_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Get bookmarks that match any of the specified tags.
        
        Args:
            tags: List of tags to search for (without #)
            
        Returns:
            List of bookmark dictionaries
        """
        client = await self._get_client()
        all_bookmarks = []
        
        for tag in tags:
            try:
                # Query bookmarks with the specific tag
                resp = await client.bookmarks.async_get_all(query=f"#{tag}")
                results = resp.get("results", []) if isinstance(resp, dict) else []
                
                # Add tag information to each bookmark
                for bookmark in results:
                    bookmark["_query_tag"] = tag
                    all_bookmarks.append(bookmark)
                    
            except Exception as e:
                print(f"Error fetching bookmarks for tag '{tag}': {e}")
                continue
        
        # Remove duplicates based on URL (in case a bookmark has multiple tags)
        seen_urls = set()
        unique_bookmarks = []
        for bookmark in all_bookmarks:
            url = bookmark.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_bookmarks.append(bookmark)
        
        return unique_bookmarks
    
    async def get_bookmarks_by_single_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get bookmarks for a single tag (backward compatibility).
        
        Args:
            tag: Tag to search for (without #)
            
        Returns:
            List of bookmark dictionaries
        """
        return await self.get_bookmarks_by_tags([tag])
    
    async def close(self):
        """Close the client connection."""
        if self._client:
            # aiolinkding doesn't have an explicit close method, but we can clear the reference
            self._client = None
