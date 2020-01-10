import pytest

from btc_validator import is_valid_btc_address


@pytest.mark.parametrize(
    'btc_address',
    [
        '17VZNX1SN5NtKa8UQFxwQbFeFc3iqRYhem',
        '3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX',
        'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4',
        'bc1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3qccfmv3',
    ]
)
def test_main_net_addresses(btc_address):
    assert is_valid_btc_address(btc_address)


@pytest.mark.parametrize(
    'btc_address',
    [
        'tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx',
        'tb1qrp33g0q5c5txsp9arysrx4k6zdkfs4nce4xj0gdcccefvpysxf3q0sl5k7',
    ]
)
def test_testnet_address(btc_address):
    assert is_valid_btc_address(
        btc_address,
        testnet=True,
    )


@pytest.mark.parametrize(
    'invalid_address',
    [
        '',
        'tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjz',
        'tb1508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx',
        'bc1qrp33g0q5c5txsp9arysrx4k6zdk5s4nce4xj0gdcccefvpysxf3qccfmv3',
        '1A1z[1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    ]
)
@pytest.mark.parametrize(
    'testnet',
    [True, False]
)
def test_invalid_address(invalid_address, testnet):
    assert not is_valid_btc_address(
        invalid_address,
        testnet=testnet,
    )
