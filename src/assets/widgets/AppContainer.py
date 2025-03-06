import flet as ft
from .RusSession import RusSession
from .NotificationCenter import NotificationStyle
from .funciones.guardar_excel import generar_excel_propuestas
from datetime import datetime


class PropuestaContainer(ft.Container):
    def __init__(self, prop, expand=True):
        super().__init__()
        self.expand = True
        self.border_radius = 5
        self.padding = ft.padding.only(left=10, right=10, top=2, bottom=2)
        self.bgcolor = ft.Colors.PRIMARY_CONTAINER
        self.border = ft.border.all(1, ft.Colors.PRIMARY)
        self.content = ft.Row(
            [
                ft.Text(prop["propuesta"], expand=1),
                ft.Text(prop["numero"], expand=1),
                ft.Text(
                    " ".join(word.capitalize() for word in prop["socio"].split()),
                    expand=2,
                ),
                ft.Text(prop["interesAsegurable"], expand=2),
                ft.Text(prop["patente"], expand=1),
                ft.Text(prop["periodoFacturacion"], expand=2),
                ft.Text(
                    f"${int(prop['sumaAseguradaAnterior'])} - ${int(prop['sumaAsegurada'])}",
                    expand=2,
                ),
                ft.Text(
                    f"${int(prop['premioAnterior'])} - ${int(prop['premio'])}",
                    expand=2,
                ),
            ],
            expand=True,
        )


class PropuestasContainer(ft.Container):
    def __init__(self, propuestas):
        super().__init__()
        self.propuesta = propuestas
        self.expand = True
        self.props_column = ft.Column(
            [PropuestaContainer(prop) for prop in propuestas],
            expand=True,
            scroll="auto",
            spacing=2,
        )
        self.content = ft.Column(
            controls=[
                ft.Column(
                    [
                        ft.Container(
                            padding=ft.padding.only(top=5, bottom=5, left=10, right=10),
                            bgcolor=ft.Colors.PRIMARY_CONTAINER,
                            content=ft.Row(
                                [
                                    ft.Text(
                                        "Propuesta",
                                        expand=1,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Póliza", expand=1, weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        "Socio", expand=2, weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        "Vehículo",
                                        expand=2,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Patente",
                                        expand=1,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Facturación",
                                        expand=2,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Sumas (Antes - Ahora)",
                                        expand=2,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Premios (Antes - Ahora)",
                                        expand=2,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                            ),
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=15,
                                color=ft.Colors.BLUE_GREY_300,
                                offset=ft.Offset(0, 0),
                                blur_style=ft.ShadowBlurStyle.OUTER,
                            ),
                        )
                    ]
                ),
                ft.Container(
                    margin=ft.margin.only(top=5),
                    expand=True,
                    content=self.props_column,
                ),
            ],
            spacing=0,
        )

    def remove_propuesta(self, propuesta_id):
        # Find and remove the PropuestaContainer with matching propuesta ID
        for control in self.props_column.controls:
            if (
                isinstance(control, PropuestaContainer)
                and control.content.controls[0].value == propuesta_id
            ):
                self.props_column.controls.remove(control)
                self.props_column.update()
                break


class AppContainer(ft.Container):
    def cerrar_sesion(self, e):
        self.callback_logout(e)

    def refacturar_todo(self, e):
        for prop in self.propuestas:
            if not prop["data"]:
                pass
        sesion_actual = RusSession(
            self.usuario["username"], self.usuario["password"], self.usuario["codigos"]
        )
        self.button_close_session.disabled = True
        self.button_refacturar_todo.disabled = True
        self.update()

        sesion_actual.start()

        def update_premio(e):
            if "propuesta" not in e:
                return

            # Get the tab content (PropuestasContainer) for the current propuesta's codigo
            for tab in self.content.controls[0].controls[0].controls[0].tabs:
                tab_content = tab.content
                if isinstance(tab_content, PropuestasContainer):
                    # Find and update the PropuestaContainer with matching propuesta ID
                    for control in tab_content.props_column.controls:
                        if (
                            isinstance(control, PropuestaContainer)
                            and control.content.controls[0].value
                            == e["propuesta"]["propuesta"]
                        ):
                            # Update the premio text (last control in the row)
                            control.content.controls[
                                -1
                            ].value = f"${int(e['propuesta']['premioAnterior'])} - ${int(e['propuesta']['premio'])}"
                            control.content.controls[-1].update()
                            break

        def eliminar_tile(e):
            # Get the tab content (PropuestasContainer) for the current propuesta's codigo
            for tab in self.content.controls[0].controls[0].controls[0].tabs:
                tab_content = tab.content
                if isinstance(tab_content, PropuestasContainer):
                    # Remove the propuesta from the container
                    tab_content.remove_propuesta(e["propuesta"]["propuesta"])

                    # Check if there are no more proposals in this tab
                    if len(tab_content.props_column.controls) == 0:
                        # Create a message container
                        empty_message = ft.Container(
                            expand=True,
                            padding=10,
                            content=ft.Column(
                                [
                                    ft.Text(
                                        f"Ya no hay más propuestas en el código {tab.text.split(' ')[1]}",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        text_align=ft.TextAlign.CENTER,
                                    )
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.PRIMARY_CONTAINER,
                            border_radius=10,
                            border=ft.border.all(1, ft.Colors.PRIMARY),
                        )
                        tab.content = empty_message
                        tab.update()

            def get_alert_dialog(event, data):
                saludo = ""
                if datetime.now().hour < 12:
                    saludo = "☀️ Buenos días"
                else:
                    saludo = "☀️ Buenas tardes"
                mensaje = f"{saludo} estimad@ {data['propuesta']['socio']} su póliza {data['propuesta']['numeroPoliza']} ha sido refacturada con éxito.\n\nRiesgo {'🏍' if data['propuesta']['numeroSeccion'] == 20 else '🚗'}: {e['propuesta']['interesAsegurable']} - {e['propuesta']['patente']}\n\nSus cuotas serán de ${int(e['propuesta']['premio'] / e['propuesta']['cantidadCuota'])}/mes\n\nMuchas gracias por su confianza.\n\nAtentamente\n{'Productora Asesora' if self.usuario['genero'] == 'F' else 'Productor Asesor'} de Seguros {self.usuario['usuario']} {'🙋🏻‍♀' if self.usuario['genero'] == 'F' else '🙋🏻‍♂'}"
                try:
                    excel = generar_excel_propuestas(
                        self.propuestas,
                    )
                    print(excel)
                except Exception as e:
                    print(e)
                copy_tf = ft.TextField(
                    multiline=True,
                    value=mensaje,
                )

                def copy(e):
                    self.page.set_clipboard(mensaje)
                    self.page.open(
                        ft.SnackBar(ft.Text("Mensaje copiado"), duration=1000)
                    )

                ad = ft.AlertDialog(
                    content=copy_tf,
                )
                ad.actions = [
                    ft.Button("Copiar", on_click=copy),
                    ft.Button("X", on_click=lambda _: self.page.close(ad)),
                ]

                self.page.open(ad)

            self.right_nc.add_notification(
                ft.Container(
                    on_click=lambda _: get_alert_dialog(_, e),
                    content=ft.Text(
                        f"Propuesta {e['propuesta']['numero']} refacturada\nPremio: ${e['propuesta']['premio']}\nAsegurado: {e['propuesta']['socio']}\n{e['propuesta']['cantidadCuota']} cuotas de ${int(e['propuesta']['premio'] / e['propuesta']['cantidadCuota'])}\nRiesgo: {e['propuesta']['interesAsegurable']}",
                        color=ft.Colors.BLACK,
                    ),
                ),
                "success",
                duration=0,
                close_button=True,
                notification_style=NotificationStyle(
                    height=120,
                    width=400,
                    in_offset=ft.Offset(2, 0),
                    out_offset=ft.Offset(0, -4),
                ),
            )

        try:
            # refacturando = True
            sesion_actual.refacturar_propuestas(
                propuestas=self.propuestas,
                datos_refactura=self.usuario,
                callback_refactura=update_premio,
                callback_success=eliminar_tile,
            )
        except Exception as e:
            # refacturando = False
            print(e)
        finally:
            sesion_actual.stop()
            # refacturando = False
            self.button_close_session.disabled = False
            self.button_refacturar_todo.disabled = False
            self.update()
            # for tile in tiles:
            # if tile:
            # tile.disabled = False
            # page.update()

    def __init__(self, propuestas, usuario, callback_logout, left_nc, right_nc):
        super().__init__()
        self.propuestas = propuestas
        self.usuario = usuario
        self.callback_logout = callback_logout
        self.left_nc = left_nc
        self.right_nc = right_nc
        self.expand = True
        self.margin = 10
        self.border = ft.border.all(1, ft.Colors.PRIMARY)
        self.border_radius = 10
        self.padding = 5
        self.bgcolor = ft.Colors.with_opacity(0.3, ft.Colors.PRIMARY_CONTAINER)
        self.button_close_session = ft.Button(
            "Cerrar Sesión", on_click=self.cerrar_sesion
        )
        self.button_refacturar_todo = ft.Button(
            "Refacturar", on_click=self.refacturar_todo
        )
        self.content = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Stack(
                            [
                                ft.Tabs(
                                    [
                                        ft.Tab(
                                            text=f"Codigo {codigo}",
                                            content=PropuestasContainer(
                                                propuestas[i]["data"]
                                            )
                                            if propuestas[i]["data"]
                                            else ft.Container(
                                                expand=True,
                                                padding=10,
                                                content=ft.Column(
                                                    [
                                                        ft.Text(
                                                            f"Ya no hay más propuestas en el código {codigo}",
                                                            size=16,
                                                            weight=ft.FontWeight.BOLD,
                                                            text_align=ft.TextAlign.CENTER,
                                                        )
                                                    ],
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                    alignment=ft.MainAxisAlignment.CENTER,
                                                ),
                                                alignment=ft.alignment.center,
                                                bgcolor=ft.Colors.PRIMARY_CONTAINER,
                                                border_radius=10,
                                                border=ft.border.all(
                                                    1, ft.Colors.PRIMARY
                                                ),
                                            ),
                                        )
                                        for i, codigo in enumerate(usuario["codigos"])
                                    ],
                                    tab_alignment=ft.TabAlignment.CENTER,
                                    expand=True,
                                ),
                                ft.Row(
                                    [
                                        self.button_close_session,
                                        self.button_refacturar_todo,
                                    ],
                                    expand=True,
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            expand=True,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
