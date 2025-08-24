from thefuzz import process

def load_valid_genres(file_path='genres.txt'):
    try:
        with open(file_path, 'r') as file:
            return [line.strip().lower() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. No genre validation will be performed.")
        return []
    
def find_closest_genre(user_input: str, genre_list: list[str]) -> str | None:
    """
    Finds the single best match for a user's input from a list of genres.
    Returns the best match as a string, or None if no good match is found.
    """
    if not genre_list:
        return None
    
    # 1. Get the result, which could be a tuple or None
    result = process.extractOne(user_input, genre_list, score_cutoff=75)
    
    # 2. Check if a result was returned before trying to unpack it
    if result:
        # We only need the first item (the string), so we can unpack it here
        #best_match, score = result
        return result[0]
    else:
        # No match was found above the score_cutoff
        return None
