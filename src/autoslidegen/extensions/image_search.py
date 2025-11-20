"""
Image search and insertion module.
Searches for relevant images and inserts them into slides.
"""

import logging
import os
from typing import List, Optional, Tuple
from pathlib import Path
import io

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from ..parser.models import PresentationOutline, Slide

logger = logging.getLogger(__name__)


class ImageSearcher:
    """Searches for images using various APIs."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "unsplash"):
        """
        Initialize image searcher.

        Args:
            api_key: API key for image service
            provider: Image provider (unsplash, pexels, local)
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package required for image search. Install with: pip install requests")

        self.api_key = api_key or os.getenv("IMAGE_API_KEY")
        self.provider = provider
        self.logger = logging.getLogger(self.__class__.__name__)

        # API endpoints
        self.endpoints = {
            "unsplash": "https://api.unsplash.com/search/photos",
            "pexels": "https://api.pexels.com/v1/search",
        }

    def search_unsplash(self, query: str, per_page: int = 5) -> List[dict]:
        """
        Search images on Unsplash.

        Args:
            query: Search query
            per_page: Number of results

        Returns:
            List of image metadata
        """
        if not self.api_key:
            self.logger.warning("No Unsplash API key provided")
            return []

        try:
            response = requests.get(
                self.endpoints["unsplash"],
                params={
                    "query": query,
                    "per_page": per_page,
                    "orientation": "landscape"
                },
                headers={"Authorization": f"Client-ID {self.api_key}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("results", []):
                    results.append({
                        "url": item["urls"]["regular"],
                        "thumb_url": item["urls"]["thumb"],
                        "description": item.get("description") or item.get("alt_description", ""),
                        "author": item["user"]["name"],
                        "width": item["width"],
                        "height": item["height"]
                    })

                return results
            else:
                self.logger.error(f"Unsplash API error: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Error searching Unsplash: {e}")
            return []

    def search_pexels(self, query: str, per_page: int = 5) -> List[dict]:
        """
        Search images on Pexels.

        Args:
            query: Search query
            per_page: Number of results

        Returns:
            List of image metadata
        """
        if not self.api_key:
            self.logger.warning("No Pexels API key provided")
            return []

        try:
            response = requests.get(
                self.endpoints["pexels"],
                params={
                    "query": query,
                    "per_page": per_page,
                    "orientation": "landscape"
                },
                headers={"Authorization": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("photos", []):
                    results.append({
                        "url": item["src"]["large"],
                        "thumb_url": item["src"]["small"],
                        "description": item.get("alt", ""),
                        "author": item["photographer"],
                        "width": item["width"],
                        "height": item["height"]
                    })

                return results
            else:
                self.logger.error(f"Pexels API error: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"Error searching Pexels: {e}")
            return []

    def search(self, query: str, count: int = 5) -> List[dict]:
        """
        Search for images.

        Args:
            query: Search query
            count: Number of images to return

        Returns:
            List of image metadata
        """
        if self.provider == "unsplash":
            return self.search_unsplash(query, count)
        elif self.provider == "pexels":
            return self.search_pexels(query, count)
        else:
            self.logger.warning(f"Unknown provider: {self.provider}")
            return []

    def download_image(self, url: str, save_path: Optional[str] = None) -> Optional[bytes]:
        """
        Download image from URL.

        Args:
            url: Image URL
            save_path: Optional path to save image

        Returns:
            Image bytes or None if failed
        """
        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                image_data = response.content

                if save_path:
                    Path(save_path).write_bytes(image_data)
                    self.logger.info(f"Image saved to: {save_path}")

                return image_data
            else:
                self.logger.error(f"Failed to download image: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            return None


class ImageInserter:
    """Inserts images into presentation slides."""

    def __init__(self, searcher: Optional[ImageSearcher] = None):
        """
        Initialize image inserter.

        Args:
            searcher: ImageSearcher instance
        """
        if not PIL_AVAILABLE:
            raise ImportError("Pillow package required for image insertion. Install with: pip install Pillow")

        self.searcher = searcher
        self.logger = logging.getLogger(self.__class__.__name__)
        self.image_cache = {}

    def generate_search_query(self, slide: Slide, context: str = "") -> str:
        """
        Generate search query from slide content.

        Args:
            slide: Slide to generate query for
            context: Additional context

        Returns:
            Search query string
        """
        # Use slide title as primary query
        query = slide.title

        # Add context if available
        if context:
            query = f"{context} {query}"

        # Clean and limit query length
        query = query.replace("：", " ").replace(":", " ")
        query = " ".join(query.split()[:5])  # Limit to 5 words

        return query

    def find_image_for_slide(
        self,
        slide: Slide,
        context: str = "",
        cache_dir: Optional[str] = None
    ) -> Optional[str]:
        """
        Find and download appropriate image for slide.

        Args:
            slide: Slide to find image for
            context: Presentation context
            cache_dir: Directory to cache images

        Returns:
            Path to downloaded image or None
        """
        if not self.searcher:
            self.logger.warning("No image searcher configured")
            return None

        # Generate search query
        query = self.generate_search_query(slide, context)
        self.logger.info(f"Searching images for: {query}")

        # Check cache
        if query in self.image_cache:
            self.logger.debug(f"Using cached image for: {query}")
            return self.image_cache[query]

        # Search for images
        results = self.searcher.search(query, count=3)

        if not results:
            self.logger.warning(f"No images found for: {query}")
            return None

        # Download first result
        image_url = results[0]["url"]

        # Setup cache directory
        if cache_dir is None:
            cache_dir = "./output/images"

        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = f"slide_{slide.slide_number}_{hash(query) % 10000}.jpg"
        image_path = cache_path / filename

        # Download image
        image_data = self.searcher.download_image(image_url, str(image_path))

        if image_data:
            self.image_cache[query] = str(image_path)
            return str(image_path)

        return None

    def add_images_to_outline(
        self,
        outline: PresentationOutline,
        image_dir: Optional[str] = None,
        slide_types: List[str] = ["content"]
    ) -> dict:
        """
        Find and prepare images for outline slides.

        Args:
            outline: Presentation outline
            image_dir: Directory to store images
            slide_types: Which slide types to add images to

        Returns:
            Dictionary mapping slide numbers to image paths
        """
        if not self.searcher:
            self.logger.warning("No image searcher configured, skipping image search")
            return {}

        self.logger.info("Finding images for slides...")

        context = outline.metadata.topic
        image_map = {}

        for slide in outline.slides:
            # Skip slides we don't want images for
            if slide.slide_type not in slide_types:
                continue

            # Find image
            image_path = self.find_image_for_slide(slide, context, image_dir)

            if image_path:
                image_map[slide.slide_number] = image_path
                self.logger.info(f"Found image for slide {slide.slide_number}")

        self.logger.info(f"Found {len(image_map)} images")
        return image_map


def create_image_searcher(provider: str = "unsplash", api_key: Optional[str] = None) -> ImageSearcher:
    """
    Factory function to create image searcher.

    Args:
        provider: Image provider
        api_key: API key

    Returns:
        ImageSearcher instance
    """
    return ImageSearcher(api_key=api_key, provider=provider)
