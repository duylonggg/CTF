from math import ceil
from scipy.constants import golden

def phinary_to_decimal(phigit):
    integer, fraction = phigit.split(".")
    integer = integer[::-1] #reverse integer string

    number = 0

    for i, x in enumerate(integer):
        if x == "1":
            number = number + golden ** (i)
    for i, x in enumerate(fraction):
        if x == "1":
            number = number + golden ** -(i+1)
    
    return number

if __name__ == "__main__":
    with open("phi_enc.txt") as f:
        string = f.read()
        string = string.rstrip("\n")
    
    #Split string every 15th character
    phigits = [string[i: i + 15] for i in range(0, len(string), 15)]
    
    decoded_phi = []

    for phigit in phigits:
        decoded_phi.append(ceil(phinary_to_decimal(phigit)))

    print(''.join(map(chr,decoded_phi)))
