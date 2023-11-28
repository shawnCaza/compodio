import string

txt = "power up!".lower().translate(str.maketrans('', '', string.punctuation))

print(txt)