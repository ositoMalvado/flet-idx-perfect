import flet as ft
import os
import logging
import asyncio
from assets.widgets.MainSwitcher import MainSwitcher
from assets.widgets.LoginBox import LoginBox
from assets.widgets.NotificationCenter import NotificationCenter
from assets.widgets.RusSession import RusSession
from assets.widgets.AppContainer import AppContainer
from assets.widgets.funciones.mejorar_propuestas import mejorar_propuestas
from assets.widgets.funciones.guardar_excel import generar_excel_propuestas

DEBUG = False

FOLDER_PATH = os.path.join(os.path.expanduser("~"), "Documents", "Propuestas")

# Configure logging
log_file = os.path.join(os.path.expanduser("~"), "Documents", "Propuestas", "app.log")
if DEBUG:
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
else:
    logging.disable(logging.CRITICAL)  # Disable all logging when DEBUG is False


def main(page: ft.Page):
    page.title = "Refacturador RUS"
    # page.window.maximizable = False

    # page.window.resizable = False
    # page.window.maximizable = False
    # page.window.movable = False
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.bgcolor = ft.Colors.TRANSPARENT
    page.window.title_bar_hidden = True
    page.window.frameless = True
    page.window.title_bar_buttons_hidden = True
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    notifications_left = NotificationCenter(alignment=ft.alignment.top_left)
    notifications_right = NotificationCenter(alignment=ft.alignment.top_right)

    def handle_window_button(e):
        if e.control.data == "min":
            page.window.minimized = True
            page.update()
        else:
            page.window.destroy()

    page.appbar = ft.AppBar(
        center_title=True,
        title=ft.Row(
            [
                ft.Text("Refacturador RUS", size=22),
                ft.Container(
                    ft.Text("Creado por Julián Perez", size=10),
                    on_click=lambda _: page.launch_url(
                        "https://github.com/ositoMalvado/"
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.END,
        ),
        # shape=ft.RoundedRectangleBorder(radius=20),
        shadow_color=ft.Colors.BLACK,
        actions=[
            ft.Container(
                padding=ft.padding.only(right=10),
                content=ft.Row(
                    [
                        ft.IconButton(
                            ft.icons.MINIMIZE,
                            on_click=handle_window_button,
                            tooltip="Minimizar",
                            data="min",
                        ),
                        ft.IconButton(
                            ft.icons.CLOSE,
                            on_click=handle_window_button,
                            tooltip="Cerrar",
                            data="exit",
                        ),
                    ]
                ),
            )
        ],
        bgcolor=ft.colors.with_opacity(0.6, ft.Colors.PRIMARY_CONTAINER),
        automatically_imply_leading=False,
    )
    # page.window.center()

    def log_out(e=None):
        for notification in notifications_left.notifications:
            notification.destroy(None)
        for notification in notifications_right.notifications:
            notification.destroy(None)
        switch(index=0)

        main_switcher.contents[0].tf_username.disabled = False
        main_switcher.contents[0].tf_password.disabled = False
        main_switcher.contents[0].b_login.disabled = False
        main_switcher.contents[0].b_clear.disabled = False
        main_switcher.contents[0].cb_remember.disabled = False
        main_switcher.contents[
            0
        ].update()  # Actualizar la página antes de operaciones largas

    def on_login(e=None):
        user = e.copy()
        sesion_actual = RusSession(user["username"], user["password"], user["codigos"])
        try:
            logging.info("Starting login process")
            buscando_notif = notifications_right.add_notification(
                ft.Text("Buscando Propuestas", color=ft.Colors.BLACK), duration=0
            )
            logging.debug("Switching to loading view")
            switch(index=1)
            sesion_actual.start()
            logging.info("Session started, searching for proposals")
            propuestas = sesion_actual.buscar_propuestas().copy()
            buscando_notif.destroy(None)
            texto = ""
            propuestas_mejoradas = None
            if not propuestas:
                texto = "No se han encontrado propuestas"
                logging.info("No proposals found")
            else:
                props = 0
                for codigo in propuestas:
                    props += len(codigo["data"])
                texto = f"Hay {props} {'propuesta' if props == 1 else 'propuestas'} para refacturar"
                logging.info(f"Found {props} proposals")
            buscando_notif = notifications_right.add_notification(
                ft.Text(texto, color=ft.Colors.BLACK), duration=12000, close_button=True
            )
            logging.debug("Improving proposals data")
            propuestas_mejoradas = mejorar_propuestas(propuestas)

            try:
                logging.debug("Generating Excel files")
                excels = generar_excel_propuestas(propuestas=propuestas_mejoradas)
                if not excels == "No hay datos":

                    def open_propuestas(e):
                        os.startfile(FOLDER_PATH)
                        excel_notif.destroy(None)

                    excel_notif = notifications_left.add_notification(
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Se {'generaron los Excel' if len(user['codigos']) > 1 else 'generó el Excel'} ",
                                    color=ft.Colors.BLACK,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    ft.Icons.FOLDER_OPEN,
                                    icon_color=ft.Colors.BLACK,
                                    on_click=open_propuestas,
                                    tooltip="Abrir carpeta de los Excel",
                                ),
                            ]
                        ),
                        duration=0,
                        close_button=True,
                    )
            except Exception as err:
                if DEBUG:
                    logging.error(f"Error generating Excel: {str(err)}")
                    print(f"Error generando excel: {str(err)}")
            logging.info("Creating AppContainer")
            app_container = AppContainer(
                propuestas_mejoradas,
                user,
                callback_logout=log_out,
                left_nc=notifications_left,
                right_nc=notifications_right,
            )
            logging.debug("Adding AppContainer to MainSwitcher")
            new_index = main_switcher.add_content(app_container)
            logging.debug(f"New container index: {new_index}")

            # Add a small delay before switching to ensure UI is ready
            async def delayed_switch():
                await asyncio.sleep(0.5)
                switch(index=new_index)
                logging.info("Successfully switched to AppContainer")

            # Schedule the delayed switch
            page.run_task(delayed_switch)
        except Exception as err:
            if DEBUG:
                logging.error(f"Error during login process: {str(err)}")
                print(f"Error: {str(err)}")
            notifications_right.add_notification(
                ft.Text(f"Error: {str(err)}", color=ft.Colors.RED),
                duration=5000,
                close_button=True,
            )
        finally:
            sesion_actual.stop()
            logging.info("Session stopped")

    def notify(mensaje, tipo):
        notifications_left.add_notification(
            ft.Text(mensaje, color=ft.Colors.BLACK), tipo, close_button=True
        )

    lb = LoginBox(page=page, on_login=on_login, notification=notify)
    app_container = ft.Container()

    main_switcher = MainSwitcher(
        [lb, ft.ProgressRing(width=200, height=200), app_container]
    )

    def switch(event=None, index=None):
        # if index > limit, then go to the first index
        main_switcher.switch_to(index)

    # page.floating_action_button = ft.FloatingActionButton(
    #     icon=ft.Icons.ADD, on_click=switch
    # )
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Stack(
                [
                    ft.Container(
                        expand=True,
                        image=ft.DecorationImage("img/bg.jpg", fit=ft.ImageFit.COVER),
                        opacity=0.8,
                    ),
                    main_switcher,
                    notifications_left,
                    notifications_right,
                ],
                expand=True,
            ),
        )
    )
    page.window.maximized = True
    page.update()


ft.app(main, assets_dir="assets")
