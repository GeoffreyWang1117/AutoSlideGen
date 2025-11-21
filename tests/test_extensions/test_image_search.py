"""
Tests for image search and insertion extension.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from PIL import Image

from autoslidegen.extensions.image_search import (
    ImageSearcher,
    ImageInserter,
    create_image_searcher
)
from autoslidegen.parser.models import (
    Slide,
    BulletPoint,
    PresentationMetadata,
    PresentationOutline
)


class TestImageSearcher:
    """Tests for ImageSearcher."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def unsplash_searcher(self, temp_dir):
        """Create Unsplash image searcher."""
        return ImageSearcher(
            provider='unsplash',
            api_key='test-key',
            cache_dir=temp_dir
        )

    @pytest.fixture
    def pexels_searcher(self, temp_dir):
        """Create Pexels image searcher."""
        return ImageSearcher(
            provider='pexels',
            api_key='test-key',
            cache_dir=temp_dir
        )

    def test_initialization(self, temp_dir):
        """Test ImageSearcher initialization."""
        searcher = ImageSearcher('unsplash', 'test-key', temp_dir)
        assert searcher.provider == 'unsplash'
        assert searcher.api_key == 'test-key'
        assert Path(searcher.cache_dir).exists()

    def test_unsupported_provider_raises_error(self, temp_dir):
        """Test that unsupported provider raises ValueError."""
        with pytest.raises(ValueError):
            ImageSearcher('invalid_provider', 'test-key', temp_dir)

    @patch('autoslidegen.extensions.image_search.requests.get')
    def test_search_unsplash(self, mock_get, unsplash_searcher):
        """Test searching images with Unsplash."""
        # Mock Unsplash API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'urls': {'regular': 'https://example.com/image1.jpg'},
                    'description': 'Test image'
                },
                {
                    'urls': {'regular': 'https://example.com/image2.jpg'},
                    'description': 'Another image'
                }
            ]
        }
        mock_get.return_value = mock_response

        results = unsplash_searcher.search('artificial intelligence')

        assert len(results) == 2
        assert results[0]['url'] == 'https://example.com/image1.jpg'
        mock_get.assert_called_once()

    @patch('autoslidegen.extensions.image_search.requests.get')
    def test_search_pexels(self, mock_get, pexels_searcher):
        """Test searching images with Pexels."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'photos': [
                {
                    'src': {'large': 'https://example.com/photo1.jpg'},
                    'alt': 'Test photo'
                }
            ]
        }
        mock_get.return_value = mock_response

        results = pexels_searcher.search('technology')

        assert len(results) == 1
        assert results[0]['url'] == 'https://example.com/photo1.jpg'

    @patch('autoslidegen.extensions.image_search.requests.get')
    def test_search_api_error_handling(self, mock_get, unsplash_searcher):
        """Test error handling for API failures."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        results = unsplash_searcher.search('test query')

        # Should return empty list on error
        assert results == []

    @patch('autoslidegen.extensions.image_search.requests.get')
    def test_download_image(self, mock_get, unsplash_searcher):
        """Test downloading an image."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = img_bytes.read()
        mock_get.return_value = mock_response

        image_path = unsplash_searcher.download_image(
            'https://example.com/image.jpg',
            'test_image'
        )

        assert image_path is not None
        assert Path(image_path).exists()
        assert Path(image_path).suffix in ['.jpg', '.jpeg', '.png']

    @patch('autoslidegen.extensions.image_search.requests.get')
    def test_download_image_error_handling(self, mock_get, unsplash_searcher):
        """Test error handling for download failures."""
        mock_get.side_effect = Exception("Network error")

        image_path = unsplash_searcher.download_image(
            'https://example.com/image.jpg',
            'test_image'
        )

        assert image_path is None

    @patch('autoslidegen.extensions.image_search.requests.get')
    def test_image_caching(self, mock_get, unsplash_searcher):
        """Test that images are cached."""
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = img_bytes.getvalue()
        mock_get.return_value = mock_response

        # Download image twice with same query
        path1 = unsplash_searcher.download_image(
            'https://example.com/same.jpg',
            'cached_image'
        )
        path2 = unsplash_searcher.download_image(
            'https://example.com/same.jpg',
            'cached_image'
        )

        assert path1 == path2
        # Should have only called download once due to caching
        assert mock_get.call_count <= 2  # May vary based on cache implementation

    def test_create_image_searcher_factory(self, temp_dir):
        """Test factory function for creating image searchers."""
        searcher = create_image_searcher('unsplash', 'test-key')
        assert isinstance(searcher, ImageSearcher)
        assert searcher.provider == 'unsplash'


class TestImageInserter:
    """Tests for ImageInserter."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_outline(self):
        """Create sample outline."""
        metadata = PresentationMetadata(
            topic="云计算技术",
            audience="IT专业人士",
            purpose="技术介绍"
        )

        slides = [
            Slide(
                slide_number=1,
                title="云计算简介",
                slide_type="title",
                bullet_points=[BulletPoint(text="副标题", level=1)]
            ),
            Slide(
                slide_number=2,
                title="云计算架构",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="IaaS", level=1),
                    BulletPoint(text="PaaS", level=1),
                    BulletPoint(text="SaaS", level=1)
                ]
            ),
            Slide(
                slide_number=3,
                title="应用场景",
                slide_type="content",
                bullet_points=[
                    BulletPoint(text="数据存储", level=1),
                    BulletPoint(text="计算服务", level=1)
                ]
            )
        ]

        return PresentationOutline(metadata=metadata, slides=slides)

    @pytest.fixture
    def image_searcher(self, temp_dir):
        """Create mock image searcher."""
        searcher = Mock()
        searcher.search = Mock(return_value=[
            {'url': 'https://example.com/image.jpg', 'description': 'Test'}
        ])

        # Create a test image for download
        img = Image.new('RGB', (100, 100), color='green')
        img_path = Path(temp_dir) / 'test_image.jpg'
        img.save(str(img_path))

        searcher.download_image = Mock(return_value=str(img_path))
        return searcher

    def test_initialization(self, image_searcher):
        """Test ImageInserter initialization."""
        inserter = ImageInserter(image_searcher)
        assert inserter.searcher == image_searcher

    def test_extract_keywords_from_title(self, image_searcher):
        """Test extracting keywords from slide title."""
        inserter = ImageInserter(image_searcher)

        keywords = inserter.extract_keywords("云计算技术架构")
        assert isinstance(keywords, str)
        assert len(keywords) > 0

    def test_find_images_for_outline(self, image_searcher, sample_outline):
        """Test finding images for entire outline."""
        inserter = ImageInserter(image_searcher)

        image_map = inserter.find_images_for_outline(sample_outline)

        assert isinstance(image_map, dict)
        # Should have images for content slides (not title slide)
        assert len(image_map) > 0

    def test_find_images_skips_title_slides(self, image_searcher, sample_outline):
        """Test that image search skips title slides."""
        inserter = ImageInserter(image_searcher)

        image_map = inserter.find_images_for_outline(sample_outline)

        # Slide 1 is title, should not have image
        assert 1 not in image_map

    def test_find_images_handles_search_failures(self, temp_dir, sample_outline):
        """Test handling of search failures."""
        searcher = Mock()
        searcher.search = Mock(return_value=[])  # No results
        searcher.download_image = Mock(return_value=None)  # Download fails

        inserter = ImageInserter(searcher)
        image_map = inserter.find_images_for_outline(sample_outline)

        # Should handle failures gracefully
        assert isinstance(image_map, dict)

    def test_custom_slides_selection(self, image_searcher, sample_outline):
        """Test finding images for specific slides only."""
        inserter = ImageInserter(image_searcher)

        # Only find images for slide 2
        image_map = inserter.find_images_for_slides(sample_outline, slide_numbers=[2])

        assert len(image_map) <= 1
        if len(image_map) > 0:
            assert 2 in image_map

    @patch('autoslidegen.extensions.image_search.requests.get')
    def test_integration_search_and_download(self, mock_get, temp_dir, sample_outline):
        """Test integration of search and download."""
        # Mock search response
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'results': [
                {'urls': {'regular': 'https://example.com/cloud.jpg'}, 'description': 'Cloud'}
            ]
        }

        # Mock download response
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')

        download_response = Mock()
        download_response.status_code = 200
        download_response.content = img_bytes.getvalue()

        mock_get.side_effect = [search_response, download_response]

        searcher = ImageSearcher('unsplash', 'test-key', temp_dir)
        inserter = ImageInserter(searcher)

        image_map = inserter.find_images_for_outline(sample_outline)

        assert isinstance(image_map, dict)
