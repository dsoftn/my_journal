import re

def ocisti_text(tekst):
    # Koristi regularni izraz da izbaci sve što nije alfanumeričko niti razmak
    cisti_tekst = re.sub(r'[^\w\s]', '', tekst)
    return cisti_tekst

# Primer korišćenja funkcije
tekst = "\"\"Ovo je tekst sa specijalnim 1212 !&^@$!*&@karakterima kao što su: ░ i slicni.''"
cisti_tekst = ocisti_text(tekst)
print(cisti_tekst)
a = ""
print (repr(tekst)[1:-1])
print (repr(a)[1:-1])