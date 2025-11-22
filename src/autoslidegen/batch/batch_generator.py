"""
Batch generation module for AutoSlideGen.
Supports batch generation from CSV and JSON files.
"""

import csv
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..parser.models import GenerationRequest
from ..main import AutoSlideGen

logger = logging.getLogger(__name__)


class BatchGenerationRequest:
    """Represents a batch of generation requests."""

    def __init__(self, requests: List[Dict[str, Any]]):
        """
        Initialize batch request.

        Args:
            requests: List of request dictionaries
        """
        self.requests = requests
        self.total = len(requests)

    @classmethod
    def from_csv(cls, csv_path: str) -> 'BatchGenerationRequest':
        """
        Load batch requests from CSV file.

        CSV format:
        topic,audience,purpose,language,num_slides,bullets_per_slide,additional_requirements

        Args:
            csv_path: Path to CSV file

        Returns:
            BatchGenerationRequest instance
        """
        requests = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Convert numeric fields
                if 'num_slides' in row and row['num_slides']:
                    row['num_slides'] = int(row['num_slides'])
                if 'bullets_per_slide' in row and row['bullets_per_slide']:
                    row['bullets_per_slide'] = int(row['bullets_per_slide'])

                # Handle optional fields
                if 'language' not in row or not row['language']:
                    row['language'] = 'zh'

                requests.append(row)

        logger.info(f"Loaded {len(requests)} requests from CSV: {csv_path}")
        return cls(requests)

    @classmethod
    def from_json(cls, json_path: str) -> 'BatchGenerationRequest':
        """
        Load batch requests from JSON file.

        JSON format:
        {
            "requests": [
                {
                    "topic": "...",
                    "audience": "...",
                    "purpose": "...",
                    ...
                }
            ]
        }

        Args:
            json_path: Path to JSON file

        Returns:
            BatchGenerationRequest instance
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        requests = data.get('requests', [])
        logger.info(f"Loaded {len(requests)} requests from JSON: {json_path}")
        return cls(requests)


class BatchGenerator:
    """Handles batch generation of presentations."""

    def __init__(
        self,
        provider: Optional[str] = None,
        config_path: Optional[str] = None,
        max_workers: int = 3,
        use_cache: bool = True
    ):
        """
        Initialize batch generator.

        Args:
            provider: LLM provider
            config_path: Config file path
            max_workers: Maximum parallel workers
            use_cache: Whether to use caching
        """
        self.provider = provider
        self.config_path = config_path
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_batch(
        self,
        batch_request: BatchGenerationRequest,
        output_dir: Optional[str] = None,
        parallel: bool = True,
        save_json: bool = True,
        on_progress: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Generate presentations in batch.

        Args:
            batch_request: Batch generation request
            output_dir: Output directory for generated files
            parallel: Whether to use parallel processing
            save_json: Whether to save JSON outlines
            on_progress: Progress callback function(completed, total, current_topic)

        Returns:
            Dictionary with generation results and statistics
        """
        self.logger.info(
            f"Starting batch generation: {batch_request.total} presentations"
        )

        # Create output directory
        if output_dir is None:
            output_dir = f"./output/batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {
            'total': batch_request.total,
            'completed': 0,
            'failed': 0,
            'successes': [],
            'failures': [],
            'output_dir': str(output_path)
        }

        start_time = datetime.now()

        if parallel:
            results = self._generate_parallel(
                batch_request,
                output_path,
                save_json,
                on_progress,
                results
            )
        else:
            results = self._generate_sequential(
                batch_request,
                output_path,
                save_json,
                on_progress,
                results
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        results['duration_seconds'] = duration
        results['avg_time_per_presentation'] = duration / batch_request.total

        self.logger.info(
            f"Batch generation completed: "
            f"{results['completed']}/{results['total']} succeeded, "
            f"{results['failed']} failed, "
            f"duration: {duration:.2f}s"
        )

        # Save batch report
        self._save_batch_report(results, output_path)

        return results

    def _generate_sequential(
        self,
        batch_request: BatchGenerationRequest,
        output_path: Path,
        save_json: bool,
        on_progress: Optional[callable],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate presentations sequentially."""
        asg = AutoSlideGen(
            provider=self.provider,
            config_path=self.config_path,
            use_cache=self.use_cache
        )

        for idx, request_data in enumerate(batch_request.requests, 1):
            topic = request_data.get('topic', f'Presentation_{idx}')

            if on_progress:
                on_progress(idx - 1, batch_request.total, topic)

            try:
                # Prepare output path
                sanitized_topic = "".join(
                    c for c in topic if c.isalnum() or c in "._- "
                )[:50]
                pptx_path = output_path / f"{idx:03d}_{sanitized_topic}.pptx"

                # Generate presentation
                result = asg.generate(
                    output_path=str(pptx_path),
                    save_json=save_json,
                    **request_data
                )

                results['successes'].append({
                    'index': idx,
                    'topic': topic,
                    'pptx_path': result['pptx_path'],
                    'json_path': result.get('json_path')
                })
                results['completed'] += 1

                self.logger.info(f"[{idx}/{batch_request.total}] Completed: {topic}")

            except Exception as e:
                self.logger.error(f"[{idx}/{batch_request.total}] Failed: {topic} - {e}")
                results['failures'].append({
                    'index': idx,
                    'topic': topic,
                    'error': str(e)
                })
                results['failed'] += 1

        return results

    def _generate_parallel(
        self,
        batch_request: BatchGenerationRequest,
        output_path: Path,
        save_json: bool,
        on_progress: Optional[callable],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate presentations in parallel."""

        def generate_one(idx: int, request_data: Dict[str, Any]) -> Dict[str, Any]:
            """Generate single presentation (worker function)."""
            asg = AutoSlideGen(
                provider=self.provider,
                config_path=self.config_path,
                use_cache=self.use_cache
            )

            topic = request_data.get('topic', f'Presentation_{idx}')

            try:
                sanitized_topic = "".join(
                    c for c in topic if c.isalnum() or c in "._- "
                )[:50]
                pptx_path = output_path / f"{idx:03d}_{sanitized_topic}.pptx"

                result = asg.generate(
                    output_path=str(pptx_path),
                    save_json=save_json,
                    **request_data
                )

                return {
                    'success': True,
                    'index': idx,
                    'topic': topic,
                    'pptx_path': result['pptx_path'],
                    'json_path': result.get('json_path')
                }

            except Exception as e:
                return {
                    'success': False,
                    'index': idx,
                    'topic': topic,
                    'error': str(e)
                }

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(generate_one, idx, req): idx
                for idx, req in enumerate(batch_request.requests, 1)
            }

            for future in as_completed(futures):
                result = future.result()

                if result['success']:
                    results['successes'].append({
                        'index': result['index'],
                        'topic': result['topic'],
                        'pptx_path': result['pptx_path'],
                        'json_path': result.get('json_path')
                    })
                    results['completed'] += 1
                    self.logger.info(
                        f"[{results['completed']}/{batch_request.total}] "
                        f"Completed: {result['topic']}"
                    )
                else:
                    results['failures'].append({
                        'index': result['index'],
                        'topic': result['topic'],
                        'error': result['error']
                    })
                    results['failed'] += 1
                    self.logger.error(
                        f"[{results['completed'] + results['failed']}/{batch_request.total}] "
                        f"Failed: {result['topic']}"
                    )

                if on_progress:
                    on_progress(
                        results['completed'] + results['failed'],
                        batch_request.total,
                        result['topic']
                    )

        return results

    def _save_batch_report(self, results: Dict[str, Any], output_path: Path):
        """Save batch generation report."""
        report_path = output_path / "batch_report.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Batch report saved to: {report_path}")

        # Also create a summary text file
        summary_path = output_path / "batch_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("Batch Generation Summary\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Requests: {results['total']}\n")
            f.write(f"Completed: {results['completed']}\n")
            f.write(f"Failed: {results['failed']}\n")
            f.write(f"Duration: {results['duration_seconds']:.2f}s\n")
            f.write(f"Avg Time: {results['avg_time_per_presentation']:.2f}s\n\n")

            if results['successes']:
                f.write("Successful Generations:\n")
                f.write("-" * 60 + "\n")
                for item in results['successes']:
                    f.write(f"{item['index']:3d}. {item['topic']}\n")
                    f.write(f"     PPTX: {item['pptx_path']}\n")

            if results['failures']:
                f.write("\nFailed Generations:\n")
                f.write("-" * 60 + "\n")
                for item in results['failures']:
                    f.write(f"{item['index']:3d}. {item['topic']}\n")
                    f.write(f"     Error: {item['error']}\n")

        self.logger.info(f"Batch summary saved to: {summary_path}")
