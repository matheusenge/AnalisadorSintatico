from lexer import AnalisadorLexico

class Nó:
    """
    Representa um nó em uma árvore sintática abstrata (AST).
    
    Atributos:
        tipo (str): O tipo do nó (por exemplo, "EXPR", "DECL_PRINT", "IDENTIFICADOR", etc.).
        filhos (list): Uma lista de nós filhos, que são as subexpressões ou subdeclarações do nó atual.
        folha: Um valor opcional que contém informações adicionais sobre o nó, como o valor de um número ou o nome de um identificador.
    """

    def __init__(self, _tipo, filhos=None, folha=None):
        self.tipo = _tipo
        self.filhos = filhos if filhos is not None else []
        self.folha = folha

    def __repr__(self, nivel=0):
        """
        Retorna uma representação em string do nó e de seus filhos, com recuo apropriado para mostrar a estrutura hierárquica da árvore.

        Args:
            nivel (int, opcional): O nível de recuo atual. Por padrão, é 0.

        Returns:
            str: A representação em string do nó e de seus filhos.
        """
        recuo = "  " * nivel
        resultado = f"{recuo}{self.tipo}"
        if self.folha is not None:
            resultado += f": {self.folha}"
        resultado += "\n"
        for filho in self.filhos:
            resultado += filho.__repr__(nivel + 1)
        return resultado
    
class Analisador:
    """
    Representa um analisador sintático que constrói uma árvore sintática abstrata (AST) a partir de uma lista de tokens.

    Atributos:
        tokens (list): A lista de tokens a serem analisados.
        token_atual: O token atual sendo analisado.
        ast (Nó): A árvore sintática abstrata gerada após a análise.
    """

    def __init__(self, tokens):
        """
        Inicializa um novo objeto Analisador.

        Args:
            tokens (list): A lista de tokens a serem analisados.
        """
        self.tokens = tokens
        self.token_atual = self.tokens.pop(0)
        self.ast = None

    def analisar(self):
        """
        Analisa a lista de tokens e constrói a árvore sintática abstrata (AST).

        A AST gerada pode ser acessada através do atributo `ast` da classe.
        """
        self.ast = self.programa()

    def programa(self):
        """
        Analisa a estrutura do programa e retorna o nó raiz da árvore sintática abstrata (AST).

        A estrutura do programa inclui a palavra-chave "PROGRAM", um identificador, a seção de variáveis e as declarações.

        Returns:
            Nó: O nó raiz da AST representando o programa.
        """
        self.combinar("PROGRAM")
        identificador = self.combinar("IDENTIFIER")
        self.combinar("LBRACE")
        secao_var = self.secao_var()
        declaracoes = self.declaracoes()
        self.combinar("RBRACE")
        return Nó("PROGRAMA", [secao_var, declaracoes], identificador[1])

    def secao_var(self):
        """
        Analisa a seção de variáveis do programa e retorna um nó representando essa seção.

        Returns:
            Nó: Um nó representando a seção de variáveis do programa.
        """
        nos = []
        while self.token_atual[0] == "VAR":
            self.combinar("VAR")
            identificador = self.combinar("IDENTIFIER")
            self.combinar("COLON")
            tipo = self.combinar("INT", "FLOAT", "BOOL")
            self.combinar("SEMICOLON")
            nos.append(Nó("DECL_VAR", [], (identificador[1], tipo[0])))
        return Nó("SECAO_VAR", nos)

    def declaracoes(self):
        """
        Analisa as declarações do programa e retorna um nó representando essas declarações.

        Returns:
            Nó: Um nó representando as declarações do programa.
        """
        nos = []
        while self.token_atual[0] in ("IDENTIFIER", "IF", "WHILE", "PRINT"):
            if self.token_atual[0] == "IDENTIFIER":
                nos.append(self.atribuicao())
            elif self.token_atual[0] == "IF":
                nos.append(self.decl_if())
            elif self.token_atual[0] == "WHILE":
                nos.append(self.decl_while())
            elif self.token_atual[0] == "PRINT":
                nos.append(self.decl_print())
        return Nó("DECLARACOES", nos)

    def atribuicao(self):
        """
        Analisa uma atribuição de variável e retorna um nó representando essa atribuição.

        Returns:
            Nó: Um nó representando a atribuição de variável.
        """
        identificador = self.combinar("IDENTIFIER")
        self.combinar("ASSIGN")
        expr = self.expr()
        self.combinar("SEMICOLON")
        return Nó("ATRIBUICAO", [expr], identificador[1])

    def decl_if(self):
        """
        Analisa uma declaração if e retorna um nó representando essa declaração.

        Returns:
            Nó: Um nó representando a declaração if.
        """
        self.combinar("IF")
        self.combinar("LPAREN")
        condicao = self.expr()
        self.combinar("RPAREN")
        self.combinar("LBRACE")
        declaracoes_verdadeiras = self.declaracoes()
        self.combinar("RBRACE")
        declaracoes_falsas = None
        if self.token_atual[0] == "ELSE":
            self.combinar("ELSE")
            self.combinar("LBRACE")
            declaracoes_falsas = self.declaracoes()
            self.combinar("RBRACE")
        return Nó("DECL_IF", [condicao, declaracoes_verdadeiras, declaracoes_falsas])

    def decl_while(self):
        """
        Analisa uma declaração while e retorna um nó representando essa declaração.

        Returns:
            Nó: Um nó representando a declaração while.
        """
        self.combinar("WHILE")
        self.combinar("LPAREN")
        condicao = self.expr()
        self.combinar("RPAREN")
        self.combinar("LBRACE")
        declaracoes_loop = self.declaracoes()
        self.combinar("RBRACE")
        return Nó("DECL_WHILE", [condicao, declaracoes_loop])

    def decl_print(self):
        """
        Analisa uma declaração print e retorna um nó representando essa declaração.

        Returns:
            Nó: Um nó representando a declaração print.
        """
        self.combinar("PRINT")
        self.combinar("LPAREN")
        expr = self.expr()
        self.combinar("RPAREN")
        self.combinar("SEMICOLON")
        return Nó("DECL_PRINT", [expr])

    def expr(self):
        """
        Analisa uma expressão e retorna um nó representando essa expressão.

        Returns:
            Nó: Um nó representando a expressão.
        """
        esquerda = self.expr_simples()
        while self.token_atual[0] == "REL_OP":
            op = self.combinar("REL_OP")
            direita = self.expr_simples()
            esquerda = Nó("EXPR", [esquerda, direita], op[1])
        return esquerda

    def expr_simples(self):
        """
        Analisa uma expressão simples e retorna um nó representando essa expressão.

        Returns:
            Nó: Um nó representando a expressão simples.
        """
        esquerda = self.termo()
        while self.token_atual[0] == "ADD_OP":
            op = self.combinar("ADD_OP")
            direita = self.termo()
            esquerda = Nó("EXPR", [esquerda, direita], op[1])
        return esquerda

    def termo(self):
        """
        Analisa um termo e retorna um nó representando esse termo.

        Returns:
            Nó: Um nó representando o termo.
        """
        esquerda = self.fator()
        while self.token_atual[0] == "MUL_OP":
            op = self.combinar("MUL_OP")
            direita = self.fator()
            esquerda = Nó("EXPR", [esquerda, direita], op[1])
        return esquerda

    def fator(self):
        """
        Analisa um fator e retorna um nó representando esse fator.

        Returns:
            Nó: Um nó representando o fator.
        """
        if self.token_atual[0] == "IDENTIFIER":
            return Nó("IDENTIFICADOR", [], self.combinar("IDENTIFIER")[1])
        elif self.token_atual[0] == "NUMBER":
            return Nó("NUMERO", [], self.combinar("NUMBER")[1])
        elif self.token_atual[0] == "LPAREN":
            self.combinar("LPAREN")
            expr = self.expr()
            self.combinar("RPAREN")
            return expr
        elif self.token_atual[0] == "TRUE":
            return Nó("BOOLEANO", [], self.combinar("TRUE")[1])
        elif self.token_atual[0] == "FALSE":
            return Nó("BOOLEANO", [], self.combinar("FALSE")[1])

    def combinar(self, *tipos_esperados):
        """
        Verifica se o token atual corresponde a um dos tipos esperados e avança para o próximo token.

        Args:
            *tipos_esperados: Um ou mais tipos de token esperados.

        Returns:
            tuple: O token atual, se corresponder a um dos tipos esperados.

        Raises:
            SyntaxError: Se o token atual não corresponder a nenhum dos tipos esperados.
        """
        if self.token_atual[0] in tipos_esperados:
            token = self.token_atual
            self.token_atual = self.tokens.pop(0) if self.tokens else None
            return token
        else:
            raise SyntaxError(f"Token inesperado: {self.token_atual}")
        
codigo_fonte = """programa teste
{
    var x : int;
    var y : float;
    var z : bool;
    x = 10;
    y = 3.14;
    z = true;
    
    if (x > 5) {
        print(x);
    } else {
        print(x - 1);
    }

    while (x > 0) {
        x = x - 1;
        print(x);
    }

    if (z) {
        print("TRUE");
    } else {
        print("FALSE");
    }
}"""


"""
Uso do analisador léxico e do analisador para analisar o código-fonte de um programa.

O código-fonte é analisado pelo analisador léxico para produzir uma lista de tokens. Em seguida, o analisador é usado
para analisar a lista de tokens e construir uma árvore sintática abstrata (AST).

A AST é então impressa para mostrar a estrutura do programa.
"""

analisador_lexico = AnalisadorLexico(codigo_fonte)
tokens = analisador_lexico.analisar_tokens()
analisador = Analisador(tokens)
analisador.analisar()

print(analisador.ast)