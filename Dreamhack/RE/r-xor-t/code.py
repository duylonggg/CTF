# Decode the input based on the described inverse pipeline

result2 = "C@qpl==Bppl@<=pG<>@l>@Blsp<@l@AArqmGr=B@A>q@@B=GEsmC@ArBmAGlA=@q"
# Step 1: XOR each byte with 3
result = [ord(c) ^ 3 for c in result2]

# Step 2: Reverse the array
rot = [result[63 - i] for i in range(64)]

# Step 3: Subtract 13 (mod 128) and convert to characters
plaintext = "".join(chr((b - 13) & 0x7F) for b in rot)

print(plaintext)