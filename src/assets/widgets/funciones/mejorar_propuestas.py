from .mejorar_propuestas_data import get_anios, get_colores, get_marcas
import re


def mejorar_propuestas(fix_propuestas):
    for codigo in fix_propuestas:
        for fix_propuesta in codigo["data"]:
            fix_propuesta["marca"] = ""
            fix_propuesta["anios"] = ""
            fix_propuesta["colores"] = []
            fix_propuesta["modelo"] = ""
            fix_propuesta["socio"] = " ".join(fix_propuesta["socio"].split()).strip()
            fix_propuesta["interesAsegurable"] = (
                fix_propuesta["interesAsegurable"].replace("PARTICULAR ", "").strip()
            )
            fix_propuesta["interesAsegurable"] = (
                fix_propuesta["interesAsegurable"]
                .replace("CASA RODANTE CON PROPULSION PROPIA ", "")
                .strip()
            )
            temp_ia = fix_propuesta["interesAsegurable"]

            palabras = fix_propuesta["interesAsegurable"].split()

            # Eliminar marca si la primera palabra coincide con una de la lista

            # Eliminar duplicados en la lista, conservando la primera ocurrencia
            palabras_sin_duplicados = []
            visto = set()
            for p in palabras:
                # Comparamos en mayúsculas para hacerlo case-insensitive
                key = p.upper()
                if key not in visto:
                    palabras_sin_duplicados.append(p)
                    visto.add(key)
            # Asignamos la lista filtrada a 'palabras'
            palabras = palabras_sin_duplicados
            palabras = palabras[:-1]
            # Reconstruir el string limpio a partir de la lista sin duplicados
            fix_propuesta["interesAsegurable"] = " ".join(palabras)

            temp_ia = fix_propuesta["interesAsegurable"]
            for palabra in palabras[:]:
                if palabra and palabra.upper() in get_colores():
                    fix_propuesta["colores"].append(palabra)
                    palabras.remove(palabra)
                if palabra and palabra.upper() in get_anios():
                    fix_propuesta["anios"] = palabra
                    palabras.remove(palabra)

            # Obtener la primera palabra restante para 'interesAsegurableFix'
            fix_propuesta["interesAsegurableFix"] = palabras[0] if palabras else ""

            # Reemplazar secuencias de más de 5 caracteres repetidos en 'interesAsegurableFix'
            fix_propuesta["interesAsegurableFix"] = re.sub(
                r"(\w)\1{5,}", r"\1", fix_propuesta["interesAsegurableFix"]
            )

            fix_propuesta["modelo"] = fix_propuesta["interesAsegurableFix"]
            fix_propuesta["interesAsegurable"] = temp_ia

            fix_propuesta["premio"] = int(fix_propuesta["premio"])
    return fix_propuestas
