import subprocess

def dict_attack(wordlist):
    for x in wordlist:
        try:
            subprocess.check_output(["steghide", "extract", 
                                     "-sf", "7.bmp", "-p", x], 
                                     stderr=subprocess.DEVNULL)
            return x
        except subprocess.CalledProcessError:
            pass
    return 0

if __name__ == "__main__":
    with open('lol_wordlist.txt') as f:
        lines = f.read().splitlines()

    passphrase = dict_attack(lines)
    
    if passphrase:
        print("Success! Passphrase is " + passphrase)
    else:
        print("Sorry, no cigar.")
