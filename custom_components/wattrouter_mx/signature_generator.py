import hashlib
from .dataview import DataView
import logging


_LOGGER = logging.getLogger(__name__)


def generate_signature(config: str, user: str, password: str) -> str:
    #_LOGGER.debug("po user admin %", po(user, 16))
    un = "455156572e" #sigdata(po(user, 16))
    pr = "e3e5e7f4" #sigdata(po(password, 16))
    pf = config + un + pr
    return hashlib.sha256(pf.encode('utf-8')).hexdigest()


def sigdata(data) -> str:
    pl = DataView(data)
    counter = 0
    byte_length = pl.byte_length
    pm = ''

    while counter < byte_length:
        hex_num = hex(pl.get_uint_8(counter))
        if len(hex_num) < 2:
            hex_num = "0" + hex_num
        pm += hex_num
        counter += 1

    return pm


def po(src: str, length: int):
    ef = 0
    dR = len(src)
    if dR > length:
        dR = length
    pq = []
    _LOGGER.debug("shit src %s, length %s, dR %s, ", src, length, dR)
    while ef < length and ef < dR:
        pq.append(ord(src[ef]) - 0x80)
        _LOGGER.debug("shit ef %s, dR %s", ef, dR)
        if ef < (dR - 1):
            pq[ef] += ord(src[ef+1])
        else:
            pq[ef] += 0x40
        ef += 1
    return pq
