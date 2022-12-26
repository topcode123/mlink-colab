import re


def replace_nth(string, sub, wanted, n):
    where = [m.start() for m in re.finditer(sub, string, re.IGNORECASE)][n - 1]
    before = string[:where]
    after = string[where:]
    after = after.replace(sub, wanted, 1)
    return before + after


strings = "Thành viên đội tuYển Tây Ban Nha đang là sinh viên chuyên đội tuyển Tây Ban Nha"

pattern = re.compile("đội tuyển tâY ban nha", re.IGNORECASE)
print(re.search("độI ", strings, re.IGNORECASE))
strings = pattern.sub("test",  strings, 1)
print(strings)
