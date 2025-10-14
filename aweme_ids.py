"""
Extract aweme_id and create_time from Douyin and TikTok user posts response files.

This script reads the JSON response files from Douyin and TikTok APIs,
extracts the aweme_id and create_time for each video, and outputs them
to a single JSON file with source labels.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def load_json_file(file_path: str) -> dict:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_aweme_info(data: dict, source: str) -> List[Dict[str, any]]:
    """
    Extract aweme_id and create_time from the response data.

    Args:
        data: The parsed JSON data from API response
        source: Source platform ('Douyin' or 'TikTok')

    Returns:
        List of dictionaries containing video information
    """
    aweme_list = data.get('data', {}).get('aweme_list', [])

    result = []
    for item in aweme_list:
        aweme_id = item.get('aweme_id')
        create_time = item.get('create_time')

        if aweme_id and create_time:
            # Convert Unix timestamp to readable datetime
            create_datetime = datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')

            result.append({
                'aweme_id': aweme_id,
                'create_time': create_time,
                'create_datetime': create_datetime,
                'source': source
            })

    return result


def main():
    """Main function to process both Douyin and TikTok response files."""
    # Define file paths
    current_dir = Path(__file__).parent
    douyin_file = current_dir / 'douyin_user_posts_response.json'
    tiktok_file = current_dir / 'tiktok_user_posts_response.json'
    output_file = current_dir / 'aweme_ids_output.json'

    # Process files
    print("Loading Douyin user posts...")
    douyin_data = load_json_file(douyin_file)
    douyin_videos = extract_aweme_info(douyin_data, 'Douyin')
    print(f"Extracted {len(douyin_videos)} videos from Douyin")

    print("\nLoading TikTok user posts...")
    tiktok_data = load_json_file(tiktok_file)
    tiktok_videos = extract_aweme_info(tiktok_data, 'TikTok')
    print(f"Extracted {len(tiktok_videos)} videos from TikTok")

    # Combine results
    all_videos = {
        'total_count': len(douyin_videos) + len(tiktok_videos),
        'douyin_count': len(douyin_videos),
        'tiktok_count': len(tiktok_videos),
        'videos': douyin_videos + tiktok_videos
    }

    # Save to output file
    print(f"\nSaving results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved {all_videos['total_count']} video records!")
    print(f"Output file: {output_file}")


if __name__ == '__main__':
    main()
