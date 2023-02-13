class Numerais:
    unidade = {
        1: 'um',
        2: 'dois',
        3: 'três',
        4: 'quatro',
        5: 'cinco',
        6: 'seis',
        7: 'sete',
        8: 'oito',
        9: 'nove',
    }
    dezena = {
        1: 'dez',
        2: 'vinte',
        3: 'trinta',
        4: 'quarenta',
        5: 'cinquenta',
        6: 'sessenta',
        7: 'setenta',
        8: 'oitenta',
        9: 'noventa',
    }
    dezena_dez = {
        11: 'onze',
        12: 'doze',
        13: 'treze',
        14: 'quatorze',
        15: 'quinze',
        16: 'dezesseis',
        17: 'dezessete',
        18: 'dezoito',
        19: 'dezenove',
    }
    centena = {
        1: 'cento',
        2: 'duzentos',
        3: 'trezentos',
        4: 'quatrocentos',
        5: 'quinhentos',
        6: 'seiscentos',
        7: 'setecentos',
        8: 'oitocentos',
        9: 'novecentos',
    }

    @staticmethod
    def numero_extenso(numero):
        assert(isinstance(numero, str), "O 'número' precisa ser uma string")
        casas_decimais = len(numero)
        string = []
        for i in range(1, casas_decimais+1):
            if i == 1:
                if Numerais.unidade.get(int(numero[-i])):
                    string.insert(0, Numerais.unidade.get(int(numero[-i])) )
            elif i == 2:
                n = numero[-i]+numero[-1]
                if Numerais.dezena_dez.get(int(n)):
                    string[0] = Numerais.dezena_dez.get(int(n))
                elif Numerais.dezena.get(int(numero[-i])):       
                    string.insert(0, Numerais.dezena.get(int(numero[-i])))
            elif i == 3:
                if Numerais.centena.get(int(numero[-i])):
                    if numero[-i] == '1' and numero[-2] == '0' and numero[-1] == '0':
                        string.insert(0, 'cem')
                    else:
                        string.insert(0, Numerais.centena.get(int(numero[-i])))
            elif i == 4:
                if Numerais.unidade.get(int(numero[-i])):
                    string.insert(0, Numerais.unidade.get(int(numero[-i])) + " mil")
            elif i == 5:
                n = numero[-i]+numero[-4]
                if Numerais.dezena_dez.get(int(n)):
                    string[0] = Numerais.dezena_dez.get(int(n)) + " mil"
                elif Numerais.dezena.get(int(numero[-i])):      
                    if numero[-4] == '0':
                        string.insert(0, Numerais.dezena.get(int(numero[-i]))+ " mil") 
                    else:
                        string.insert(0, Numerais.dezena.get(int(numero[-i])))
            elif i == 6:
                if numero[-4] == '0' and numero[-5] == '0':
                    string.insert(0, Numerais.centena.get(int(numero[-i])) + ' mil') 
                else:
                    string.insert(0, Numerais.centena.get(int(numero[-i])))
        return string

    @staticmethod
    def concatenar_numeros(numero):
        numero_string = ''
        for i in range(0, len(numero)):
            if i < len(numero) -1:
                numero_string += numero[i] + ' e '
            else: 
                numero_string += numero[i]
        return numero_string