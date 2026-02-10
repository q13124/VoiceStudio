"""
Batch Processor CLI for VoiceStudio
Command-line interface for batch processing operations

Compatible with:
- Python 3.10+
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import batch processing components
try:
    from ..engines.router import EngineRouter

    HAS_ENGINE_ROUTER = True
except ImportError:
    HAS_ENGINE_ROUTER = False
    EngineRouter = None  # type: ignore[misc,assignment]
    logger.warning("Engine router not available")


class BatchProcessorCLI:
    """
    Batch Processor CLI for command-line batch processing.

    Supports:
    - Text file processing
    - CSV file processing
    - JSON configuration
    - Progress tracking
    - Error handling
    - Output management
    """

    def __init__(self, engine_router: Optional[EngineRouter] = None):
        """
        Initialize Batch Processor CLI.

        Args:
            engine_router: Optional EngineRouter instance
        """
        self.engine_router = engine_router

    def process_text_file(
        self,
        input_file: Path,
        output_dir: Path,
        engine_name: str,
        voice_profile_id: Optional[str] = None,
        language: str = "en",
        quality_threshold: Optional[float] = None,
        enhance_quality: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a text file with one text per line.

        Args:
            input_file: Path to input text file
            output_dir: Output directory for generated audio
            engine_name: Engine name to use
            voice_profile_id: Optional voice profile ID
            language: Language code
            quality_threshold: Optional quality threshold
            enhance_quality: Whether to enhance quality

        Returns:
            Dictionary with processing results
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Read text file
        texts = []
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    texts.append(line)

        if not texts:
            raise ValueError("No text found in input file")

        logger.info(f"Processing {len(texts)} texts from {input_file}")

        # Process each text
        results = {
            "total": len(texts),
            "successful": 0,
            "failed": 0,
            "outputs": [],
            "errors": [],
        }

        for idx, text in enumerate(texts, 1):
            try:
                logger.info(f"Processing {idx}/{len(texts)}: {text[:50]}...")

                # Generate output filename
                output_filename = f"output_{idx:04d}.wav"
                output_path = output_dir / output_filename

                # Synthesize
                if not HAS_ENGINE_ROUTER or not self.engine_router:
                    raise RuntimeError("Engine router not available")

                engine = self.engine_router.get_engine(engine_name)
                if not engine:
                    raise RuntimeError(f"Engine '{engine_name}' not available")

                # Perform synthesis
                synthesis_result = engine.synthesize(
                    text=text,
                    speaker_wav=voice_profile_id,  # Assuming voice_profile_id is a path
                    language=language,
                )

                if synthesis_result and "audio" in synthesis_result:
                    audio = synthesis_result["audio"]
                    sample_rate = synthesis_result.get("sample_rate", 24000)

                    # Save audio
                    try:
                        import soundfile as sf

                        sf.write(str(output_path), audio, sample_rate)
                        logger.info(f"Saved: {output_path}")
                    except ImportError:
                        import numpy as np

                        # Fallback: save as raw numpy array
                        np.save(str(output_path.with_suffix(".npy")), audio)
                        logger.warning(
                            f"soundfile not available, saved as numpy array: {output_path.with_suffix('.npy')}"
                        )

                    results["successful"] += 1
                    results["outputs"].append(
                        {
                            "index": idx,
                            "text": text,
                            "output_path": str(output_path),
                            "status": "success",
                        }
                    )
                else:
                    raise RuntimeError("Synthesis returned no audio")

            except Exception as e:
                logger.error(f"Failed to process text {idx}: {e}")
                results["failed"] += 1
                results["errors"].append(
                    {
                        "index": idx,
                        "text": text,
                        "error": str(e),
                    }
                )

        return results

    def process_csv_file(
        self,
        input_file: Path,
        output_dir: Path,
        engine_name: str,
        text_column: str = "text",
        language_column: Optional[str] = None,
        default_language: str = "en",
        voice_profile_id: Optional[str] = None,
        quality_threshold: Optional[float] = None,
        enhance_quality: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a CSV file with text data.

        Args:
            input_file: Path to input CSV file
            output_dir: Output directory for generated audio
            engine_name: Engine name to use
            text_column: Name of text column
            language_column: Optional name of language column
            default_language: Default language if not specified
            voice_profile_id: Optional voice profile ID
            quality_threshold: Optional quality threshold
            enhance_quality: Whether to enhance quality

        Returns:
            Dictionary with processing results
        """
        try:
            import csv
        except ImportError:
            raise ImportError("CSV module not available")

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Read CSV file
        rows = []
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        if not rows:
            raise ValueError("No rows found in CSV file")

        logger.info(f"Processing {len(rows)} rows from {input_file}")

        # Process each row
        results = {
            "total": len(rows),
            "successful": 0,
            "failed": 0,
            "outputs": [],
            "errors": [],
        }

        for idx, row in enumerate(rows, 1):
            try:
                text = row.get(text_column, "").strip()
                if not text:
                    logger.warning(f"Row {idx} has no text, skipping")
                    continue

                language = (
                    row.get(language_column, default_language).strip()
                    if language_column
                    else default_language
                )

                logger.info(f"Processing {idx}/{len(rows)}: {text[:50]}...")

                # Generate output filename
                output_filename = f"output_{idx:04d}.wav"
                output_path = output_dir / output_filename

                # Synthesize
                if not HAS_ENGINE_ROUTER or not self.engine_router:
                    raise RuntimeError("Engine router not available")

                engine = self.engine_router.get_engine(engine_name)
                if not engine:
                    raise RuntimeError(f"Engine '{engine_name}' not available")

                # Perform synthesis
                synthesis_result = engine.synthesize(
                    text=text,
                    speaker_wav=voice_profile_id,
                    language=language,
                )

                if synthesis_result and "audio" in synthesis_result:
                    audio = synthesis_result["audio"]
                    sample_rate = synthesis_result.get("sample_rate", 24000)

                    # Save audio
                    try:
                        import soundfile as sf

                        sf.write(str(output_path), audio, sample_rate)
                        logger.info(f"Saved: {output_path}")
                    except ImportError:
                        import numpy as np

                        np.save(str(output_path.with_suffix(".npy")), audio)
                        logger.warning(
                            f"soundfile not available, saved as numpy array: {output_path.with_suffix('.npy')}"
                        )

                    results["successful"] += 1
                    results["outputs"].append(
                        {
                            "index": idx,
                            "text": text,
                            "language": language,
                            "output_path": str(output_path),
                            "status": "success",
                        }
                    )
                else:
                    raise RuntimeError("Synthesis returned no audio")

            except Exception as e:
                logger.error(f"Failed to process row {idx}: {e}")
                results["failed"] += 1
                results["errors"].append(
                    {
                        "index": idx,
                        "row": row,
                        "error": str(e),
                    }
                )

        return results

    def process_json_config(
        self, config_file: Path, output_dir: Path
    ) -> Dict[str, Any]:
        """
        Process a JSON configuration file.

        Args:
            config_file: Path to JSON configuration file
            output_dir: Output directory for generated audio

        Returns:
            Dictionary with processing results
        """
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # Load configuration
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Extract configuration
        input_file = Path(config.get("input_file", ""))
        engine_name = config.get("engine", "xtts_v2")
        voice_profile_id = config.get("voice_profile_id")
        language = config.get("language", "en")
        quality_threshold = config.get("quality_threshold")
        enhance_quality = config.get("enhance_quality", False)

        # Determine input file type
        if input_file.suffix.lower() == ".csv":
            text_column = config.get("text_column", "text")
            language_column = config.get("language_column")
            default_language = config.get("default_language", "en")

            return self.process_csv_file(
                input_file=input_file,
                output_dir=output_dir,
                engine_name=engine_name,
                text_column=text_column,
                language_column=language_column,
                default_language=default_language,
                voice_profile_id=voice_profile_id,
                quality_threshold=quality_threshold,
                enhance_quality=enhance_quality,
            )
        else:
            return self.process_text_file(
                input_file=input_file,
                output_dir=output_dir,
                engine_name=engine_name,
                voice_profile_id=voice_profile_id,
                language=language,
                quality_threshold=quality_threshold,
                enhance_quality=enhance_quality,
            )

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """
        Save processing results to JSON file.

        Args:
            results: Processing results dictionary
            output_path: Output file path
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="VoiceStudio Batch Processor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Input file (text, CSV, or JSON config)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output directory",
    )

    parser.add_argument(
        "-e",
        "--engine",
        type=str,
        default="xtts_v2",
        help="Engine name (default: xtts_v2)",
    )

    parser.add_argument(
        "--voice-profile",
        type=str,
        help="Voice profile ID or path",
    )

    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="en",
        help="Language code (default: en)",
    )

    parser.add_argument(
        "-q",
        "--quality-threshold",
        type=float,
        help="Quality threshold (0.0-1.0)",
    )

    parser.add_argument(
        "--enhance-quality",
        action="store_true",
        help="Enable quality enhancement",
    )

    parser.add_argument(
        "--text-column",
        type=str,
        default="text",
        help="CSV text column name (default: text)",
    )

    parser.add_argument(
        "--language-column",
        type=str,
        help="CSV language column name",
    )

    parser.add_argument(
        "--default-language",
        type=str,
        default="en",
        help="Default language for CSV (default: en)",
    )

    parser.add_argument(
        "-r",
        "--results",
        type=Path,
        help="Save results to JSON file",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize CLI
    try:
        from ..engines.router import EngineRouter

        engine_router = EngineRouter()
        cli = BatchProcessorCLI(engine_router=engine_router)
    except Exception as e:
        logger.error(f"Failed to initialize engine router: {e}")
        sys.exit(1)

    # Process based on file type
    try:
        if args.input_file.suffix.lower() == ".json":
            results = cli.process_json_config(args.input_file, args.output)
        elif args.input_file.suffix.lower() == ".csv":
            results = cli.process_csv_file(
                input_file=args.input_file,
                output_dir=args.output,
                engine_name=args.engine,
                text_column=args.text_column,
                language_column=args.language_column,
                default_language=args.default_language,
                voice_profile_id=args.voice_profile,
                quality_threshold=args.quality_threshold,
                enhance_quality=args.enhance_quality,
            )
        else:
            results = cli.process_text_file(
                input_file=args.input_file,
                output_dir=args.output,
                engine_name=args.engine,
                voice_profile_id=args.voice_profile,
                language=args.language,
                quality_threshold=args.quality_threshold,
                enhance_quality=args.enhance_quality,
            )

        # Print summary
        print(f"\nProcessing complete!")
        print(f"Total: {results['total']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")

        # Save results if requested
        if args.results:
            cli.save_results(results, args.results)

        # Exit with error code if failures
        if results["failed"] > 0:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Batch processing failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

