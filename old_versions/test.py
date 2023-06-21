import re

string = 'aasdasd ee4 asdgasd "a23"'

matches = re.findall(r"\b([a-h][1-8][a-h][1-8])\b", string)

print(matches)