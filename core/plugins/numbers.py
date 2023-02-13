def to_brl(number):
    value = "{:,.2f}".format(number).split('.')
    value = "{0},{1}".format(value[0].replace(',','.'), value[1])
    return value