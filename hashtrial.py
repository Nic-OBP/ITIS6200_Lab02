import hashlib
import json
from pathlib import Path

HASH_DB = "hash_table.json"

def hash_file(file_path, algorithm='sha256'):
    try:
        with open(file_path, 'rb') as f:
            digest = hashlib.file_digest(f, algorithm) #google said to user file_digest
        return digest.hexdigest()
    except Exception as e:
        return None

def traverse_directory(directory_path):
    path = Path(directory_path)
    file_hashes = {}
    if path.is_dir():
        for file in path.iterdir():
            if file.is_file():
                h = hash_file(file)
                if h:
                    file_hashes[str(file.absolute())] = h
    return file_hashes

def generate_table(directory_path):
    data = traverse_directory(directory_path)
    with open(HASH_DB, 'w') as f: # store JSON
        json.dump(data, f, indent=4)
    print(f"\nHash table for {directory_path} generated.")

def validate_hash(directory_path):
    if not Path(HASH_DB).exists():
        print("Error: No hash table found. Please generate one first.")
        return

    with open(HASH_DB, 'r') as f:
        stored_data = json.load(f)

    if not Path(directory_path).exists:
        print(f"directory {directory_path} does not exist.")
        return 0
    current_data = traverse_directory(directory_path)
    
    # sort by hashes instead of names
    stored_hashes_rev = {h: p for p, h in stored_data.items()}

    # check for valid, invalid, and renamed files
    for current_path, current_hash in current_data.items():
        if current_path in stored_data: # file stored
            if current_hash == stored_data[current_path]: # compare hash
                print(f"{current_path}: Valid.")
            else:
                print(f"{current_path}: Invalid hash (contents modified).")
        else:
            # file not stored, renamed or new
            if current_hash in stored_hashes_rev: # hash exists
                old_path = stored_hashes_rev[current_hash]
                print(f"{current_path}: Valid hash ({old_path} was renamed to {current_path}).")
                stored_data[current_path] = stored_data.pop(old_path)
            else:
                print(f"{current_path}: New file.") # otherwise new

    # deleted
    for stored_path in list(stored_data.keys()):
        if stored_path not in current_data:
            if not any(h == stored_data[stored_path] for h in current_data.values()):
                print(f"{stored_path}: File deleted.")

    # update JSON
    with open(HASH_DB, 'w') as f:
        json.dump(stored_data, f, indent=4)

def main():
    print("1. Generate New Hash Table")
    print("2. Verify Hashes")
    choice = input("Select an option: ")

    if choice == '1':
        dir_path = input("Enter directory path: ")
        generate_table(dir_path)
    elif choice == '2':
        dir_path = input("Enter directory path to verify: ")
        validate_hash(dir_path)
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    main()