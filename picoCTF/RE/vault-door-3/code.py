target = list("jU5t_a_sna_3lpm12g94c_u_4_m7ra41")
password = [''] * 32

# Step 1: buffer[0..7] = password[0..7]
for i in range(0, 8):
    password[i] = target[i]

# Step 2: buffer[8..15] = password[23 - i]
for i in range(8, 16):
    password[23 - i] = target[i]

# Step 3: buffer[16..30 step 2] = password[46 - i]
for i in range(16, 32, 2):
    password[46 - i] = target[i]

# Step 4: buffer[17..31 step 2] = password[i]
for i in range(31, 16, -2):
    password[i] = target[i]

print("".join(password))
