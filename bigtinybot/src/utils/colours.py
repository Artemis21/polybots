import requests
import re


r = requests.get(
    'https://blogs.msdn.microsoft.com/smallbasic/2015/06/20/the-hex-colors-in'
    '-small-basic/'
)
matches = re.findall(
    r'([a-zA-Z]+?)</td>\\n<td style="width: 80px;">#([A-Z0-9]{6})',
    str(r.content)
)

colours = {}
for i in matches:
    colours[i[0].lower()] = int(i[1], 16)


if __name__ == '__main__':
    for i in colours:
        h = hex(colours[i])[2:].upper()
        h = h + '0' * (6 - len(h))
        print(h, i)
