from flask import Flask, render_template, request
import re
import math

app = Flask(__name__)

class Calculadora:
    """Classe responsável por analisar e calcular a expressão matemática em Python puro."""
    
    def __init__(self):
        self.elementos = []
        self.posicao = 0

    def elemento_atual(self):
        if self.posicao < len(self.elementos):
            return self.elementos[self.posicao]
        return None

    def calcular(self, expressao_texto: str):
        # Normalização de símbolos
        expressao_texto = expressao_texto.replace(' ', '')
        expressao_texto = expressao_texto.replace('√', 'raiz')
        expressao_texto = expressao_texto.replace(',', '.')

        # Separa números, palavras e operadores
        padrao = r'([0-9]+(?:\.[0-9]+)?|[a-zA-Z]+|[\+\-\*\/\^\(\)\!])'
        self.elementos = re.findall(padrao, expressao_texto)
        self.posicao = 0

        if not self.elementos:
            raise ValueError("Expressão vazia.")

        resultado = self._analisar_expressao()

        if self.posicao < len(self.elementos):
            raise ValueError("Sintaxe incorreta na expressão.")

        return resultado

    # Processa Soma (+) e Subtração (-)
    def _analisar_expressao(self):
        resultado = self._analisar_termo()
        while self.elemento_atual() in ('+', '-'):
            operador = self.elemento_atual()
            self.posicao += 1
            proximo = self._analisar_termo()
            if operador == '+':
                resultado += proximo
            else:
                resultado -= proximo
        return resultado

    # Processa Multiplicação (*) e Divisão (/)
    def _analisar_termo(self):
        resultado = self._analisar_potencia()
        while self.elemento_atual() in ('*', '/'):
            operador = self.elemento_atual()
            self.posicao += 1
            proximo = self._analisar_potencia()
            if operador == '/':
                if proximo == 0:
                    raise ValueError("Divisão por zero não permitida.")
                resultado /= proximo
            else:
                resultado *= proximo
        return resultado

    # Processa Exponenciação (^)
    def _analisar_potencia(self):
        resultado = self._analisar_fatorial()
        if self.elemento_atual() == '^':
            self.posicao += 1
            expoente = self._analisar_potencia()
            resultado = resultado ** expoente
        return resultado

    # Processa Fatorial (!)
    def _analisar_fatorial(self):
        resultado = self._analisar_primario()
        while self.elemento_atual() == '!':
            self.posicao += 1
            if resultado < 0 or int(resultado) != resultado:
                raise ValueError("Fatorial apenas para números inteiros positivos.")
            if resultado > 170:
                raise ValueError("Número grande demais para fatorial.")
            resultado = math.factorial(int(resultado))
        return resultado

    # Processa Números, Parênteses, Raiz e Logaritmo
    def _analisar_primario(self):
        item = self.elemento_atual()

        # Operadores unários
        if item == '-':
            self.posicao += 1
            return -self._analisar_primario()
        if item == '+':
            self.posicao += 1
            return self._analisar_primario()

        # Parênteses
        if item == '(':
            self.posicao += 1
            resultado = self._analisar_expressao()
            if self.elemento_atual() != ')':
                raise ValueError("Faltou fechar parêntese ')'.")
            self.posicao += 1
            return resultado

        # Funções matemáticas
        item_min = item.lower() if item else ''
        if item_min in ('raiz', 'sqrt', 'log'):
            funcao = item_min
            self.posicao += 1

            if self.elemento_atual() != '(':
                raise ValueError(f"Use parênteses após a função {funcao}.")
            self.posicao += 1
            argumento = self._analisar_expressao()

            if self.elemento_atual() != ')':
                raise ValueError("Faltou fechar parêntese ')'.")
            self.posicao += 1

            if funcao in ('raiz', 'sqrt'):
                if argumento < 0:
                    raise ValueError("Raiz quadrada de número negativo não permitida.")
                return math.sqrt(argumento)
            elif funcao == 'log':
                if argumento <= 0:
                    raise ValueError("Logaritmo aceita apenas valores > 0.")
                return math.log10(argumento)

        # Número
        try:
            valor = float(item)
            self.posicao += 1
            # Se for número inteiro, exibe sem decimal (ex: 5 em vez de 5.0)
            return int(valor) if valor.is_integer() else valor
        except (ValueError, TypeError):
            pass

        raise ValueError(f"Símbolo inválido: '{item}'")


@app.route('/', methods=['GET', 'POST'])
def index():
    expressao = ''
    erro = ''

    if request.method == 'POST':
        expressao = request.form.get('expressao', '')
        botao = request.form.get('botao', '')

        if botao == 'ADEL':
            expressao = ''
        elif botao == 'DEL':
            if expressao.endswith('raiz('):
                expressao = expressao[:-5]
            elif expressao.endswith('log('):
                expressao = expressao[:-4]
            elif len(expressao) > 0:
                expressao = expressao[:-1]
        elif botao == '=':
            if expressao.strip():
                try:
                    calc = Calculadora()
                    resultado = calc.calcular(expressao)
                    expressao = str(resultado)
                except Exception as e:
                    erro = str(e)
        else:
            expressao += botao

    return render_template('index.html', expressao=expressao, erro=erro)


if __name__ == '__main__':
    app.run(debug=True)