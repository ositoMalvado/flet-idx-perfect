import os
import pandas as pd
from datetime import datetime


def generar_excel_propuestas(propuestas, folder="Propuestas"):
    """
    Genera archivos Excel con bordes completos:
      - Bordes en todas las celdas con datos.
      - Estilo uniforme en filas y columnas.
      - Eliminación de bordes fantasmas.

    Además, permite especificar un directorio (folder) donde se guardarán los archivos.
    Si el archivo ya existe, se agregarán únicamente aquellas propuestas nuevas (basado en 'PROPUESTA').
    """

    # LA CARPETA ESTARÁ EN *user/documents/folder*
    # folder = "Propuestas"
    folder = os.path.join(os.path.expanduser("~"), "Documents", folder)

    # Crear la carpeta de destino si no existe
    if not os.path.exists(folder):
        os.makedirs(folder)

    fecha_actual_str = datetime.now().strftime("%y-%m-%d")
    archivos_guardados = []

    # Mapeo de columnas: clave original -> nombre en español
    columnas_espanol = {
        "numeroSeccion": "N° SECCIÓN",
        "numeroPoliza": "N° PÓLIZA",
        "propuesta": "PROPUESTA",
        "socio": "ASEGURADO",
        "periodoFacturacion": "PERIODO FACTURACIÓN",
        "premio": "PREMIO ACTUAL (ARS)",
        "premioAnterior": "PREMIO ANTERIOR (ARS)",
        "cantidadCuota": "CUOTAS (ACTUAL)",
        "patente": "PATENTE",
        "interesAsegurable": "VEHÍCULO",
        "sumaAsegurada": "SUMA ASEGURADA (ARS)",
        "sumaAseguradaAnterior": "SUMA ANTERIOR (ARS)",
        "cobertura": "COBERTURA",
        "mensaje": "MENSAJE",
    }

    for grupo_propuestas in propuestas:
        codigo_grupo = grupo_propuestas.get("codigo", "SIN_CODIGO")
        data_propuestas = grupo_propuestas.get("data", [])

        if not data_propuestas:
            print(f"Advertencia: Sin datos para {codigo_grupo}")
            return "No hay datos"

        # Definir nombre del archivo y ruta completa desde el inicio
        nombre_archivo = f"Propuestas_{codigo_grupo}_{fecha_actual_str}.xlsx"
        ruta_archivo = os.path.join(folder, nombre_archivo)

        # Intentar leer el archivo existente (si existe)
        try:
            df_existente = pd.read_excel(
                ruta_archivo, sheet_name=f"Propuestas_{codigo_grupo}"
            )
        except FileNotFoundError:
            df_existente = pd.DataFrame()
        except Exception as e:
            print(f"❌ Error al leer el archivo existente {ruta_archivo}: {str(e)}")
            df_existente = pd.DataFrame()

        # Crear DataFrame con los nuevos datos
        df_nuevo = pd.DataFrame(data_propuestas)

        # Procesar columnas numéricas y calcular 'CUOTAS (ACTUAL)'
        if "premio" in df_nuevo.columns and "cantidadCuota" in df_nuevo.columns:
            df_nuevo["premio"] = pd.to_numeric(df_nuevo["premio"], errors="coerce")
            df_nuevo["cantidadCuota"] = pd.to_numeric(
                df_nuevo["cantidadCuota"], errors="coerce"
            )
            df_nuevo["cantidadCuota"] = df_nuevo.apply(
                lambda x: f"{int(x['cantidadCuota'])} cuotas de ${int(x['premio'] / x['cantidadCuota'])}"
                if pd.notnull(x["cantidadCuota"]) and x["cantidadCuota"] != 0
                else "N/A",
                axis=1,
            )

        # Generar el mensaje para cada propuesta
        df_nuevo["mensaje"] = df_nuevo.apply(
            lambda x: f"{'☀️ Buenos días' if datetime.now().hour < 12 else '☀️ Buenas tardes'} estimad@ {x['socio']} su póliza {x['numeroPoliza']} ha sido refacturada con éxito.\n\nRiesgo {'🏍' if x['numeroSeccion'] == 20 else '🚗'}: {x['interesAsegurable']} - {x['patente']}\n\nSus cuotas serán de ${int(float(x['premio']) / float(x['cantidadCuota']))}/mes\n\nMuchas gracias por su confianza.\n\nAtentamente\nProductor Asesor de Seguros",
            axis=1,
        )

        # Limpiar la columna 'socio'
        if "socio" in df_nuevo.columns:
            df_nuevo["socio"] = (
                df_nuevo["socio"].str.replace(r"\s+", " ", regex=True).str.strip()
            )

        # Procesar la columna 'interesAsegurable'
        if "interesAsegurable" in df_nuevo.columns:
            df_nuevo["interesAsegurable"] = (
                df_nuevo["interesAsegurable"]
                .str.replace("PARTICULAR ", "", regex=False)
                .str.split()  # Divide en palabras
                .str[:-1]  # Elimina la última palabra
                .str.join(" ")  # Une las palabras restantes
            )
            # Crear columna auxiliar con la primera palabra y limpiar repeticiones
            df_nuevo["interesAsegurableFix"] = (
                df_nuevo["interesAsegurable"].str.split().str[0].str.strip()
            )
            df_nuevo["interesAsegurableFix"] = df_nuevo[
                "interesAsegurableFix"
            ].str.replace(r"(.)\1{5,}", r"\1", regex=True)

        # Renombrar las columnas del nuevo DataFrame a los nombres en español
        df_nuevo_renombrado = df_nuevo.rename(columns=columnas_espanol)

        # Si ya existe un archivo, combinar y eliminar duplicados basados en 'PROPUESTA'
        if not df_existente.empty:
            df_combined = pd.concat(
                [df_existente, df_nuevo_renombrado], ignore_index=True
            )
            if "PROPUESTA" in df_combined.columns:
                df_combined.drop_duplicates(
                    subset=["PROPUESTA"], keep="first", inplace=True
                )
        else:
            df_combined = df_nuevo_renombrado.copy()

        # Ordenar por fecha extraída de 'PERIODO FACTURACIÓN'
        if "PERIODO FACTURACIÓN" in df_combined.columns:
            try:
                df_combined["fecha_orden"] = df_combined["PERIODO FACTURACIÓN"].apply(
                    lambda x: datetime.strptime(x.split(" - ")[0], "%d/%m/%Y")
                    if pd.notnull(x)
                    else datetime.min
                )
                df_combined.sort_values("fecha_orden", ascending=True, inplace=True)
                df_combined.drop(columns=["fecha_orden"], inplace=True)
            except Exception as e:
                print(f"❌ Error al ordenar por fecha en {codigo_grupo}: {str(e)}")

        # Seleccionar (y reordenar) únicamente las columnas definidas en el mapeo
        columnas_orden = [
            col for col in list(columnas_espanol.values()) if col in df_combined.columns
        ]
        df_final = df_combined[columnas_orden]

        # Generar Excel con bordes completos y formato
        try:
            with pd.ExcelWriter(ruta_archivo, engine="xlsxwriter") as writer:
                df_final.to_excel(
                    writer, index=False, sheet_name=f"Propuestas_{codigo_grupo}"
                )

                workbook = writer.book
                worksheet = writer.sheets[f"Propuestas_{codigo_grupo}"]

                # Formato base para bordes
                border_format = workbook.add_format(
                    {
                        "border": 1,
                        "border_color": "#D3D3D3",
                    }
                )

                # Formato para encabezados
                header_format = workbook.add_format(
                    {
                        "bold": True,
                        "bg_color": "#5B9BD5",
                        "font_color": "white",
                        "border": 1,
                        "align": "center",
                    }
                )

                # Formato para valores monetarios
                money_format = workbook.add_format(
                    {"num_format": "#,##0", "border": 1, "border_color": "#D3D3D3"}
                )

                # Obtener número de filas y columnas (sin contar el encabezado)
                max_row, max_col = df_final.shape

                # Aplicar bordes a todas las celdas con datos (incluye encabezado)
                worksheet.conditional_format(
                    0,
                    0,
                    max_row,
                    max_col - 1,
                    {"type": "no_blanks", "format": border_format},
                )

                # Aplicar formato a encabezados y ajustar ancho de columnas
                for col_num, col_name in enumerate(df_final.columns):
                    worksheet.write(0, col_num, col_name, header_format)
                    # Calcular ancho óptimo basado en el contenido y el título
                    max_width = (
                        max(
                            df_final[col_name].astype(str).str.len().max(),
                            len(col_name),
                        )
                        + 2
                    )
                    if "ARS" in col_name:
                        worksheet.set_column(col_num, col_num, max_width, money_format)
                    else:
                        worksheet.set_column(col_num, col_num, max_width)

            print(
                f"✅ {ruta_archivo}: Bordes completos aplicados en {max_row + 1} filas y {max_col} columnas"
            )
            archivos_guardados.append(ruta_archivo)
        except Exception as e:
            print(f"❌ Error en {codigo_grupo}: {str(e)}")

    return "Excel Generado!" if archivos_guardados else "Sin archivos generados"


# Ejemplo de uso:
# propuestas = [
#     {
#         "codigo": "GRUPO1",
#         "data": [
#             {
#                 "numeroSeccion": "001",
#                 "numeroPoliza": "12345",
#                 "propuesta": "PROP-001",
#                 "socio": "Juan Pérez",
#                 "periodoFacturacion": "01/01/2025 - 31/01/2025",
#                 "premio": "1000",
#                 "premioAnterior": "900",
#                 "cantidadCuota": "2",
#                 "patente": "ABC123",
#                 "interesAsegurable": "PARTICULAR Auto Sedan",
#                 "sumaAsegurada": "50000",
#                 "sumaAseguradaAnterior": "45000",
#                 "cobertura": "Completa"
#             },
#             # ... otros registros ...
#         ]
#     },
#     # ... otros grupos ...
# ]
#
# resultado = generar_excel_propuestas(propuestas, folder="/.Propuestas")
# print(resultado)
