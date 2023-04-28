from decimal import Decimal

def numeric_to_string(number):
    assert isinstance(number, float) or isinstance(number, Decimal)
    number = "{:,.2f}".format(number).split('.')
    number = "{0},{1}".format(number[0].replace(',','.'), number[1])
    return number