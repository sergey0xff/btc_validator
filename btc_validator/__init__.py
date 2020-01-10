import hashlib

__all__ = [
    'is_valid_btc_address',
]

_mainnet_address_prefix = '1'
_testnet_address_prefix = 'm'
_testnet_address_prefix_2 = 'n'
_mainnet_script_address_prefix = '3'
_testnet_script_address_prefix = '2'

_mainnet_segwit_address_prefix = 'bc'
_testnet_segwit_address_prefix = 'tb'

_mainnet_segwit_address_byte_prefix = b'\x03\x03\x00\x02\x03'
_testnet_segwit_address_byte_prefix = b'\x03\x03\x00\x14\x02'

_base32charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_base32charset_upcase = "QPZRY9X8GF2TVDW0S3JN54KHCE6MUA7L"

_int_base32_map = {
    i: n
    for n, i in enumerate(_base32charset)
}

_b58_alphabet = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def _scrub_input(v):
    if isinstance(v, str) and not isinstance(v, bytes):
        v = v.encode('ascii')

    if not isinstance(v, bytes):
        raise TypeError(
            f"a bytes-like object is required (also str), not '{type(v).__name__}'"
        )

    return v


def _b58decode_int(v):
    """
    Decode a Base58 encoded string as an integer
    """
    v = v.rstrip()

    decimal = 0

    for char in v:
        decimal = decimal * 58 + _b58_alphabet.index(char)

    return decimal


def _base58_decode(v):
    """
    Decode a Base58 encoded string
    """
    v = v.rstrip()
    v = _scrub_input(v)

    origlen = len(v)
    v = v.lstrip(_b58_alphabet[0:1])
    newlen = len(v)

    acc = _b58decode_int(v)

    result = []

    while acc > 0:
        acc, mod = divmod(acc, 256)
        result.append(mod)

    return b'\0' * (origlen - newlen) + bytes(reversed(result))


def _rebase_32_to_5(data):
    if isinstance(data, bytes):
        data = data.decode()

    b = bytearray()
    append = b.append

    try:
        [append(_int_base32_map[i]) for i in data]
    except KeyError:
        raise Exception(
            "Non base32 characters"
        )

    return b


def _bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1

    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value

        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0

    return chk ^ 1


def _rebase_bits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = bytearray()
    append = ret.append
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1

    for value in data:
        if value < 0 or (value >> frombits):
            raise ValueError("invalid bytes")

        acc = ((acc << frombits) | value) & max_acc
        bits += frombits

        while bits >= tobits:
            bits -= tobits
            append((acc >> bits) & maxv)
    if pad:
        if bits:
            append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        raise ValueError("invalid padding")

    return ret


def _rebase_8_to_5(data, pad=True):
    return _rebase_bits(data, 8, 5, pad)


def _double_sha256(data):
    rv = data

    for _ in range(2):
        h = hashlib.sha256()
        h.update(rv)
        rv = h.digest()

    return rv


def is_valid_btc_address(
    address: str,
    testnet: bool = False,
) -> bool:
    """
    Check is address valid.
    :param address: address in base58 or bech32 format.
    :param testnet: (optional) flag for testnet network, by default is False.
    :return: boolean.
    """
    if not address or type(address) != str:
        return False

    if address[0] in (
        _mainnet_address_prefix,
        _mainnet_script_address_prefix,
        _testnet_address_prefix,
        _testnet_address_prefix_2,
        _testnet_script_address_prefix
    ):
        if testnet:
            if address[0] not in (
                _testnet_address_prefix,
                _testnet_address_prefix_2,
                _testnet_script_address_prefix
            ):
                return False
        else:
            if address[0] not in (
                _mainnet_address_prefix,
                _mainnet_script_address_prefix
            ):
                return False

        h = _base58_decode(address)

        if len(h) != 25:
            return False

        checksum = h[-4:]

        if _double_sha256(h[:-4])[:4] != checksum:
            return False

        return True
    elif address[:2].lower() in (
        _testnet_segwit_address_prefix,
        _mainnet_segwit_address_prefix
    ):
        if len(address) not in (42, 62):
            return False

        try:
            prefix, payload = address.split('1')
        except:
            return False

        upp = True if prefix[0].isupper() else False

        for i in payload[1:]:
            if upp:
                if not i.isupper() or i not in _base32charset_upcase:
                    return False
            else:
                if i.isupper() or i not in _base32charset:
                    return False

        payload = payload.lower()
        prefix = prefix.lower()

        if testnet:
            if prefix != _testnet_segwit_address_prefix:
                return False
            stripped_prefix = _testnet_segwit_address_byte_prefix
        else:
            if prefix != _mainnet_segwit_address_prefix:
                return False
            stripped_prefix = _mainnet_segwit_address_byte_prefix

        d = _rebase_32_to_5(payload)
        address_hash = d[:-6]
        checksum = d[-6:]
        checksum2 = _bech32_polymod(
            stripped_prefix +
            address_hash +
            b"\x00" * 6
        )
        checksum2 = _rebase_8_to_5(checksum2.to_bytes(5, "big"))[2:]

        if checksum != checksum2:
            return False

        return True

    return False
