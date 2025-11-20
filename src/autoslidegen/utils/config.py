"""
Configuration management for AutoSlideGen.
Loads and manages settings from config.yaml and environment variables.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for AutoSlideGen."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config.yaml file. If None, searches in default locations.
        """
        # Load environment variables from .env file
        load_dotenv()

        # Find and load config file
        if config_path is None:
            config_path = self._find_config_file()

        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_config(config_path)

        # Setup logging
        self._setup_logging()

    def _find_config_file(self) -> str:
        """
        Search for config.yaml in default locations.

        Returns:
            Path to config file

        Raises:
            FileNotFoundError: If config file not found
        """
        # Search locations in order
        search_paths = [
            Path.cwd() / "config.yaml",
            Path.cwd() / "config" / "config.yaml",
            Path(__file__).parent.parent.parent.parent / "config.yaml",
        ]

        for path in search_paths:
            if path.exists():
                logger.info(f"Found config file at: {path}")
                return str(path)

        raise FileNotFoundError(
            "config.yaml not found. Please create a config file or specify path."
        )

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise

    def _setup_logging(self):
        """Setup logging based on configuration."""
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_format = log_config.get(
            'format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format
        )

        # Create log file if specified
        log_file = log_config.get('file')
        if log_file:
            log_dir = Path(log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level))
            file_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(file_handler)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'llm.provider')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get LLM configuration for specified provider.

        Args:
            provider: LLM provider name. If None, uses default from config.

        Returns:
            LLM configuration dictionary
        """
        if provider is None:
            provider = self.get('llm.provider', 'openai')

        llm_config = self.get(f'llm.models.{provider}', {})

        # Get API key from environment
        api_key_env = llm_config.get('api_key_env')
        if api_key_env:
            api_key = os.getenv(api_key_env)
            if not api_key:
                logger.warning(
                    f"API key not found in environment variable: {api_key_env}"
                )
            llm_config['api_key'] = api_key

        return llm_config

    def get_output_dir(self) -> Path:
        """
        Get output directory path.

        Returns:
            Path to output directory
        """
        output_dir = self.get('output.default_dir', './output')
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_ppt_config(self) -> Dict[str, Any]:
        """
        Get PPT generation configuration.

        Returns:
            PPT configuration dictionary
        """
        return self.get('ppt', {})

    def get_outline_config(self) -> Dict[str, Any]:
        """
        Get outline generation configuration.

        Returns:
            Outline configuration dictionary
        """
        return self.get('outline', {})


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        Config instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = Config(config_path)

    return _config_instance
