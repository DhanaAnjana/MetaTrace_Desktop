import hashlib


def calculate_file_hash(file_path, algorithm="sha256"):
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        return f"Error: {str(e)}"


def calculate_all_hashes(file_path):
    hashes = {}
    for algo in ["md5", "sha1", "sha256", "sha512"]:
        hashes[algo] = calculate_file_hash(file_path, algo)
    return hashes