import re

class AnalisadorLexico:
    def __init__(self, codigo_fonte):
        self.codigo_fonte = codigo_fonte
        self.tokens = []

    def analisar_tokens(self):
        especificacoes_tokens = [
            ("PROGRAM", r"\bprograma\b"),
            ("VAR", r"\bvar\b"),
            ("INT", r"\bint\b"),
            ("FLOAT", r"\bfloat\b"),
            ("BOOL", r"\bbool\b"),
            ("IF", r"\bif\b"),
            ("ELSE", r"\belse\b"),
            ("WHILE", r"\bwhile\b"),
            ("PRINT", r"\bprint\b"),
            ("TRUE", r"\btrue\b"),
            ("FALSE", r"\bfalse\b"),
            ("IDENTIFIER", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
            ("NUMBER", r"\b\d+(\.\d*)?\b"),
            ("SEMICOLON", r";"),
            ("COLON", r":"),
            ("LBRACE", r"\{"),
            ("RBRACE", r"\}"),
            ("MULTILINE_COMMENT", r"/\*.*?\*/"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("ADD_OP", r"[+-]"),
            ("MUL_OP", r"[\*/]"),
            ("REL_OP", r"[<>]=?|==|!="),
            ("ASSIGN", r"="),
            ("WHITESPACE", r"\s+"),
        ]
        

        """
        O código constrói uma expressão regular a partir das especificações de tokens e utiliza a biblioteca 're'
        para encontrar todas as correspondências no código-fonte.

        Cada correspondência é verificada para determinar o tipo e o valor do token. Os tokens de espaço em branco são ignorados,
        enquanto os demais tokens são adicionados à lista de tokens.

        Ao final, a lista de tokens é retornada.
        """
        regex = "|".join(f"(?P<{nome}>{padrao})" for nome, padrao in especificacoes_tokens)
        for correspondencia in re.finditer(regex, self.codigo_fonte):
            tipo_token = correspondencia.lastgroup
            valor_token = correspondencia.group(tipo_token)
            if tipo_token != "WHITESPACE":
                self.tokens.append((tipo_token, valor_token))

        return self.tokens

codigo_fonte = "var x:int; x=10; se (x == 10) { imprimir(x); }"
analisador_lexico = AnalisadorLexico(codigo_fonte)
tokens = analisador_lexico.analisar_tokens()
print(tokens)