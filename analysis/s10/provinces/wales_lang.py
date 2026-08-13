"""Welsh-vs-English detection for the Senedd Record.

The 2016+ bilingual XML carries a first-party per-contribution
<contribution_language> label, so detection is only needed for the PDF era
(2006-2010, 2015).  Having both on the same corpus lets the detector be
calibrated against ground truth rather than guessed at -- see
wales_calibrate_lang.py, which reports its accuracy on the labelled years.

Method: share of tokens that are Welsh function words, minus the share that are
English function words.  The brief's list (yr y ac yn i o ar mae bod wedi) is
kept but 'i' is dropped: lowercased English speech is full of 'I', which alone
pushes ordinary English over any sensible threshold.
"""
import re

CY = {
    # brief's list, less the 'i' collision with English "I"
    "yr", "y", "ac", "yn", "o", "ar", "mae", "bod", "wedi",
    # the rest of the Welsh closed class
    "a", "am", "at", "ei", "eu", "ein", "ni", "chi", "hwn", "hon", "hynny",
    "yna", "yma", "fel", "gan", "gyda", "dros", "drwy", "trwy", "rhwng",
    "os", "oherwydd", "achos", "ond", "neu", "hefyd", "iawn", "nid", "ddim",
    "roedd", "oedd", "byddwn", "bydd", "byddai", "gallwn", "gall", "gallai",
    "rydym", "rwyf", "ydych", "ydy", "yw", "sydd", "sy", "wrth", "cael",
    "gwneud", "mwy", "llawer", "pob", "holl", "dim", "dyna", "dyma", "felly",
    "ynghylch", "ynglŷn", "diolch", "cwestiwn", "cwestiynau", "aelodau",
    "aelod", "llywodraeth", "cymru", "gymru", "bobl", "phobl", "ar-gyfer",
}
EN = {
    "the", "of", "to", "and", "in", "that", "is", "it", "for", "we", "you",
    "this", "have", "are", "with", "be", "not", "on", "as", "will", "would",
    "which", "they", "there", "has", "what", "was", "from", "but", "can",
    "about", "very", "thank", "member", "members", "government", "wales",
}
TOKEN = re.compile(r"[a-zâêîôûŵŷáéíóúàèìòùäëïöüçñ'’-]+", re.I)
THRESHOLD = 0.0      # cy_share - en_share > THRESHOLD  =>  Welsh


def scores(text):
    toks = [t.lower().strip("'’-") for t in TOKEN.findall(text or "")]
    toks = [t for t in toks if t]
    if not toks:
        return 0.0, 0.0
    n = len(toks)
    return (sum(t in CY for t in toks) / n, sum(t in EN for t in toks) / n)


def is_welsh(text):
    cy, en = scores(text)
    return (cy - en) > THRESHOLD
