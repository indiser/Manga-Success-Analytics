import requests
import random
import json
import time
import os

OUTPUT_FILE = "manga.jsonl" # Changed to .jsonl (Standard for this)
TARGET_COUNT = 1000           # How many successful items you want
MAX_RETRIES = 50            # Safety break so loop doesn't run forever

# --- STEP 1: LOAD HISTORY (So we don't repeat IDs from yesterday) ---
seen_ids = set()

if os.path.exists(OUTPUT_FILE):
    print("Loading existing IDs to avoid duplicates...")
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip(): # Skip empty lines
                    try:
                        record = json.loads(line)
                        seen_ids.add(record["id"])
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Error reading history: {e}")

print(f"Already collected {len(seen_ids)} manga. Starting scrape...")

# --- STEP 2: THE "SMART" WHILE LOOP ---
success_count = 0
attempts = 0

while success_count < TARGET_COUNT and attempts < MAX_RETRIES:
    attempts += 1
    
    # Generate ID
    manga_id = random.randint(1, 50000) # Jikan has roughly 50k+ entries
    
    # CHECK: Have we done this one?
    if manga_id in seen_ids:
        print(f"Skipping ID {manga_id} (Already scraped)")
        continue

    print(f"Attempt {attempts}: Checking ID {manga_id}...")

    try:
        url = f"https://api.jikan.moe/v4/manga/{manga_id}/full"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url=url, headers=headers)

        if response.status_code == 429:
            print(f"!! Rate Limit. Sleeping 10s...")
            time.sleep(10)
            # Don't increment success_count, just retry loop
            continue
        
        if response.status_code == 404:
            print(f"-- ID {manga_id} empty.")
            seen_ids.add(manga_id) # Mark as seen so we don't check it again
            time.sleep(1)
            continue

        if response.status_code != 200:
            print(f"xx Error {response.status_code}")
            time.sleep(2)
            continue

        # --- EXTRACT DATA ---
        data = response.json()
        manga_data = data.get("data", {})
        
        # Use simple get calls
        title = manga_data.get("title_english") or manga_data.get("title")
        
        genres = [g["name"] for g in manga_data.get("genres", [])]
        themes = [t["name"] for t in manga_data.get("themes", [])]
        
        demographics = manga_data.get("demographics", [])
        demographic = demographics[0]["name"] if demographics else "Unknown"

        record = {
            "id": manga_data.get("mal_id"),
            "title": title,
            "score": manga_data.get("score"),
            "members": manga_data.get("members"),
            "demographic": demographic,
            "tags": genres + themes
        }

        # --- STEP 3: SAVE (NO INDENT) ---
        # Crucial: remove 'indent=4'. It breaks line-by-line reading.
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        print(f"++ Success: {title}")
        
        # Update trackers
        seen_ids.add(manga_id)
        success_count += 1
        
        # Reset retry counter on success so we don't stop early
        attempts = 0 

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    
    time.sleep(1.5) # Polite delay

print(f"Done. Scraped {success_count} new items.")