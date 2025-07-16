with open('lol_champs.txt') as f:
    lines = f.read().splitlines()

with open("lol_wordlist.txt", "a") as g:
    for x in lines:
        for y in lines:
            pw = ("yasuoaatrox"+x+y+"\n").lower()
            g.write(pw)
