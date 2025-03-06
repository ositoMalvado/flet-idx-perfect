import math


def calcular_valor_minimo(precio: float, descuento: float, n_cuotas: int) -> int:
    """
    Calcula el valor mínimo ajustado de forma que las cuotas resultantes sean redondas (múltiplo de 100)
    tras aplicar un descuento a un precio dado.

    Parámetros:
        precio (float): El precio original del producto o servicio.
        descuento (float): El porcentaje de descuento a aplicar sobre el precio.
        n_cuotas (int): El número de cuotas en las que se dividirá el pago.

    Retorna:
        int: El valor mínimo total ajustado. Este valor es mayor o igual al precio con descuento redondeado
             al múltiplo de 100 superior y, además, al dividirlo entre n_cuotas se obtiene un valor que es múltiplo de 100.

    Excepciones:
        ValueError: Si el número de cuotas es menor o igual a 0.
        TypeError: Si el número de cuotas no es un entero.
    """
    # Validación de parámetros
    if n_cuotas <= 0:
        raise ValueError("El número de cuotas debe ser positivo")
    if not isinstance(n_cuotas, int):
        raise TypeError("El número de cuotas debe ser un entero")

    # Calcular precio con descuento
    precio_con_descuento = precio * (1 - descuento / 100)

    # Redondear el precio con descuento al múltiplo de 100 superior
    redondeado = math.ceil(precio_con_descuento / 100) * 100

    # Para que cada cuota sea redonda (múltiplo de 100), el total debe ser divisible por (n_cuotas * 100).
    # Si no lo es, se ajusta al siguiente múltiplo de (n_cuotas * 100).
    if redondeado % (n_cuotas * 100) == 0:
        return redondeado
    else:
        return math.ceil(redondeado / (n_cuotas * 100)) * (n_cuotas * 100)


if __name__ == "__main__":
    # Ejemplo de uso:
    # Para un precio de 12,000, un descuento del 15% y 4 cuotas:
    # precio_con_descuento = 12,000 * 0.85 = 10,200
    # Redondeado a 100: 10,200 (ya es múltiplo de 100)
    # Pero 10,200 / 4 = 2,550 (no es múltiplo de 100)
    # Se ajusta al siguiente múltiplo de (4*100 = 400): ceil(10200/400)=26, 26*400 = 10,400
    # Así, 10,400 / 4 = 2,600 (cuota redonda)
    print(calcular_valor_minimo(12000, 15, 4))  # Salida esperada: 10400
