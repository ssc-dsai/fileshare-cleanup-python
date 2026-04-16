# run_full_pipeline.py
# Run the entire pipeline with one command
# Usage: python run_full_pipeline.py

import subprocess
import sys


def run_script(module_path: str, description: str):
    print(f"\n{'=' * 80}")
    print(f"🚀 Running {description}...")
    print(f"{'=' * 80}")

    try:
        result = subprocess.run(
            [sys.executable, "-m", module_path],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with return code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    print("Starting Full FileShare Pipeline\n")

    steps = [
        ("DeDuplication.0_dedup_analysis", "Deduplication Analysis"),
        ("Ingestion.1_Ingestion", "Ingestion"),
        ("Classification.2_Classification", "Classification"),
        ("Metadata_Placeholder.4_placeholder_creator", "Metadata Placeholder Creator"),
        ("Metadata_Injector.5_metadata_injector", "Metadata Injector")
    ]

    success_count = 0
    for module, desc in steps:
        if run_script(module, desc):
            success_count += 1

    print(f"\n{'=' * 80}")
    print(f"Pipeline Summary: {success_count}/{len(steps)} steps completed successfully")
    print(f"{'=' * 80}")

    if success_count == len(steps):
        print("🎉 Full pipeline completed successfully!")
    else:
        print("⚠️  Some steps had issues. Check logs above.")


if __name__ == "__main__":
    main()