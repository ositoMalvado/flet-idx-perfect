from funciones.calcular_premio import calcular_valor_minimo
import flet as ft


class CalculadoraPremio(ft.Container):
    def did_mount(self):
        if self.page.client_storage.get("CalculadoraPremio_premio"):
            print(self.page.client_storage.get("CalculadoraPremio_premio"))
            self.precio.value = self.page.client_storage.get("CalculadoraPremio_premio")
        if self.page.client_storage.get("CalculadoraPremio_descuento"):
            self.descuento_slider.value = self.page.client_storage.get(
                "CalculadoraPremio_descuento"
            )
            self.texto_descuento.value = f"Descuento aplicado: %{int(self.page.client_storage.get('CalculadoraPremio_descuento'))}"
        if self.page.client_storage.get("CalculadoraPremio_cuotas"):
            self.cuotas_slider.value = self.page.client_storage.get(
                "CalculadoraPremio_cuotas"
            )
            self.texto_cuotas.value = f"Cantida de cuotas: {int(self.page.client_storage.get('CalculadoraPremio_cuotas'))}"

        self.update()
        return super().did_mount()

    def __init__(self):
        super().__init__()
        self.precio = ft.TextField(
            label="Precio total",
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"[0-9]", replacement_string=""
            ),
            on_change=self.calcular,
            width=300,
        )
        self.descuento_slider = ft.Slider(
            min=0,
            max=15,
            divisions=15,
            label="{value}%",
            expand=True,
            on_change=self.slider_change,
            data="descuento",
        )

        self.texto_descuento = ft.Text("Descuento aplicado: %", size=16)

        self.cuotas_slider = ft.Slider(
            min=1,
            max=6,
            divisions=5,
            label="{value} cuotas",
            expand=True,
            on_change=self.slider_change,
            data="cuotas",
        )

        self.texto_cuotas = ft.Text("Cantidad de cuotas:", size=16)

        self.resultado = ft.Text(value="", size=20, weight="bold", text_align="center")

        self.content = self._crear_interfaz()
        self.padding = 20
        self.margin = 10
        self.border = ft.border.all(1)
        self.border_radius = 10
        self.width = 400

    def _crear_interfaz(self):
        return ft.Column(
            controls=[
                ft.Text("Calculadora de Premio", size=24, weight="bold"),
                self.precio,
                self.texto_descuento,
                self.descuento_slider,
                self.texto_cuotas,
                self.cuotas_slider,
                ft.Container(self.resultado),
            ],
            spacing=10,
            horizontal_alignment="center",
        )

    def slider_change(self, e):
        if e.control.data == "descuento":
            e.control.label = f"{int(e.control.value)}%"
        else:
            e.control.label = f"{int(e.control.value)} cuotas"
        e.control.update()
        self.calcular()

    def calcular(self, e=None):
        try:
            precio = float(self.precio.value)
            if precio <= 0:
                raise ValueError

            descuento = self.descuento_slider.value
            cuotas = int(self.cuotas_slider.value)

            valor_minimo = calcular_valor_minimo(
                precio=precio, descuento=descuento, n_cuotas=cuotas
            )

            self.texto_descuento.value = f"Descuento aplicado: %{int(descuento)}"
            self.texto_cuotas.value = f"Cantida de cuotas: {int(cuotas)}"

            self.resultado.value = f"Premio final: ${valor_minimo}\n{cuotas} cuotas de ${int(valor_minimo / cuotas)}"

            # Guardamos el precio correcto en el client_storage
            self.page.client_storage.set("CalculadoraPremio_premio", self.precio.value)
            self.page.client_storage.set("CalculadoraPremio_descuento", descuento)
            self.page.client_storage.set("CalculadoraPremio_cuotas", cuotas)
            self.update()

        except ValueError:
            self.resultado.value = "¡Ingrese un precio válido!"
            self.update()


def main(page: ft.Page):
    page.title = "Calculadora de Premio"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.add(CalculadoraPremio())


ft.app(target=main, view=ft.AppView.WEB_BROWSER)
