import hashlib

def solve_decryption(encrypted_message, timestamp_str):
    # Hash the timestamp with SHA-256
    hash_object = hashlib.sha256(timestamp_str.encode())
    hex_hash = hash_object.hexdigest()
    
    # Convert hex hash to a list of integer shift values (0-15)
    hex_values = [int(h, 16) for h in hex_hash]
    
    decrypted_chars = []
    key_index = 0
    
    for i, char in enumerate(encrypted_message):
        if 'A' <= char <= 'Z':
            # Get the shift value from hex_values. 
            # The "shifting more as they march forward" hint suggests the shift might be related to the position.
            # Let's try shift = (hex_value + position_in_string) % 26
            # Or maybe shift = (hex_value + position_in_alphabet) % 26
            # Or maybe shift = (hex_value + i) % 26, where i is the index in the hex_values list.
            
            # Let's try: shift = (hex_value[key_index] + i) % 26. This 'i' is the index in the hex_hash string, not the char's position in the message.
            # It's more likely that the shift increases based on the *number of alphabetic characters processed so far*.
            
            # Let's try shift = (hex_values[key_index % len(hex_values)] + key_index) % 26
            # key_index here refers to the count of alphabetic characters processed.
            
            shift = (hex_values[key_index % len(hex_values)] + key_index) % 26
            
            original_pos = ord(char) - ord('A')
            decrypted_pos = (original_pos - shift + 26) % 26
            decrypted_chars.append(chr(decrypted_pos + ord('A')))
            key_index += 1
        elif 'a' <= char <= 'z':
            shift = (hex_values[key_index % len(hex_values)] + key_index) % 26
            
            original_pos = ord(char) - ord('a')
            decrypted_pos = (original_pos - shift + 26) % 26
            decrypted_chars.append(chr(decrypted_pos + ord('a')))
            key_index += 1
        else:
            decrypted_chars.append(char)
            # Do not increment key_index for non-alphabetic characters
            
    return "".join(decrypted_chars)

encrypted_message = "INNVC{rJXKrb_FFg_NFTx_FMHDWFmX!!}"
timestamp_str = "2024,3,15,14,30,03"

decrypted_message = solve_decryption(encrypted_message, timestamp_str)
print(f"Decrypted Message: {decrypted_message}")

# Trying to decipher 'INNVC' to 'BDSEC' with the shifts: 7, 10, 21, 17, 0
# Let's manually check the shifts derived from the hash using the formula:
# shift = (hex_values[key_index] + key_index) % 26
# hex_values = [15, 5, 14, 3, 11, 7, 10, 1, ...]

# key_index = 0 (for 'I'): shift = (15 + 0) % 26 = 15. Decrypt 'I'(8) with shift 15 -> (8 - 15 + 26) % 26 = 19 (T). Incorrect.
