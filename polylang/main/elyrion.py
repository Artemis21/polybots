import string


ALPHABET = 'ao#Δ∑₼þţiƒ§∫mŋȱπ¦r^Ŧ₺‡~eỹΩ'
TABLE = str.maketrans(
    string.ascii_lowercase+string.ascii_uppercase, ALPHABET*2
)
BWDS = str.maketrans(
    ALPHABET*2, string.ascii_uppercase+string.ascii_lowercase
)

def eng_to_ely(eng):
    return eng.translate(TABLE)


def ely_to_eng(ely):
    return ely.translate(BWDS)