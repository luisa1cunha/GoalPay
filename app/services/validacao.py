from decimal import Decimal, InvalidOperation

class ErroDeNegocio(Exception):
    pass

def texto_obrigatorio(valor, rotulo: str, max_len: int | None = None) -> str:
    texto = (valor or "").strip()
    if not texto:
        raise ErroDeNegocio(f"Informe {rotulo}.")
    if max_len is not None and len(texto) > max_len:
        raise ErroDeNegocio(f"Texto muito longo em {rotulo} (máximo {max_len} caracteres)")
    
    return texto

def decimal_ou_erro(valor, rotulo: str) -> Decimal:
    if isinstance(valor, Decimal):
        resultado = valor
    elif isinstance(valor, (int, float)):
        resultado = Decimal(str(valor))
    else:
        texto = str(valor).strip().replace("R$", "").replace("%", "").replace(" ", "")
        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")
        try:
            resultado = Decimal(texto)
        except InvalidOperation:
            raise ErroDeNegocio(f"Valor inválido em {rotulo}.") from None
    if not resultado.is_finite():
        raise ErroDeNegocio(f"Valor inválido em {rotulo}.")
    return resultado

def inteiro_ou_erro(valor, rotulo: str) -> int:    
    try:
        return int(str(valor).strip())
    except ValueError:
        raise ErroDeNegocio(f"Valor inválido em {rotulo}: {valor}") from None