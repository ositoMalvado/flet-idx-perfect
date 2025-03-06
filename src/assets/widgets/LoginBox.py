import flet as ft
from .FirebaseManager import FirebaseManager


class LoginBox(ft.Container):
    def try_login(self, e):
        if not self.tf_username.value:
            self.cb_notification("Debes colocra un usuario", "error")
            self.tf_username.focus()
            self.page.update()
            return
        if not self.tf_password.value:
            self.cb_notification("Debes colocar una contraseña", "error")
            self.tf_password.focus()
            self.page.update()
            return

        self.tf_username.disabled = True
        self.tf_password.disabled = True
        self.b_login.disabled = True
        self.b_clear.disabled = True
        self.cb_remember.disabled = True
        self.page.update()  # Actualizar la página antes de operaciones largas

        try:
            user = self.fbase.login(self.tf_username.value, self.tf_password.value)
            if user:
                if self.cb_remember.value:
                    self.page.client_storage.set("user", self.tf_username.value)
                    self.page.client_storage.set("pass", self.tf_password.value)

                if self.on_login:
                    self.cb_notification("Sesión iniciada correctamente", "success")
                    self.cb_notification(
                        f"Bienvenid{'a' if user['genero'] == 'F' else 'o'} {user['usuario']}",
                        "success",
                    )
                    self.on_login(user)
                    self.tf_username.disabled = True
                    self.tf_password.disabled = True
                    self.b_login.disabled = True
                    self.b_clear.disabled = True
                    self.cb_remember.disabled = True
                    self.update()
                    return user

                # Deshabilitar controles después de login exitoso
            else:
                self.page.client_storage.set("user", "")
                self.page.client_storage.set("pass", "")
                self.cb_notification("Credenciales incorrectas", "error")

        except Exception as error:  # Capturar excepciones correctamente
            pass
            # self.cb_notification(f"Error al iniciar sesión: {error}", "error")
        finally:
            # Restablecer controles solo si el login falló
            if not user:
                self.tf_username.disabled = False
                self.tf_password.disabled = False
                self.b_login.disabled = False
                self.b_clear.disabled = False
                self.cb_remember.disabled = False
                self.update()

    def clear(self, e):
        self.tf_username.value = ""
        self.tf_password.value = ""
        self.cb_remember.value = False
        self.b_login.disabled = True
        self.b_clear.disabled = True
        self.cb_remember.disabled = True  # Redundant, already disabled above
        self.tf_username.focus()
        self.update()

    def on_tf_change(self, e):
        if not self.tf_username.value or not self.tf_password.value:
            self.b_login.disabled = True
            self.b_clear.disabled = True
            self.cb_remember.disabled = (
                True  # Redundant, checkbox is not disabled/enabled by textfield change
            )
        else:
            self.b_login.disabled = False
            self.b_clear.disabled = False
            self.cb_remember.disabled = (
                False  # Redundant, checkbox is not disabled/enabled by textfield change
            )
        self.update()

    def __init__(self, on_login=None, notification=None, page: ft.Page = None):
        super().__init__()
        self.page = page
        self.on_login = on_login
        self.cb_notification = notification
        self.fbase = FirebaseManager("")
        self.title_text = ft.Text("Refacturador RUS", size=30)
        self.login_text = ft.Text("Bienvenid@", size=20)

        def handle_cb(e):
            if not e.control.value:
                self.page.client_storage.set("user", "")
                self.page.client_storage.set("pass", "")

        self.cb_remember = ft.Checkbox(label="Recordarme", on_change=handle_cb)
        user = ""
        passwd = ""
        if page.client_storage.get("user") and page.client_storage.get("pass"):
            user = page.client_storage.get("user")
            passwd = page.client_storage.get("pass")
            self.cb_remember.value = True
        self.tf_username = ft.TextField(
            value=user,
            width=200,
            on_change=self.on_tf_change,
            label="Nombre de usuario",
            autofocus=True,
            data="user",
            autofill_hints=ft.AutofillHint.USERNAME,
        )
        self.tf_password = ft.TextField(
            value=passwd,
            width=200,
            on_change=self.on_tf_change,
            label="Contraseña",
            password=True,
            data="pass",
            autofill_hints=ft.AutofillHint.PASSWORD,
            can_reveal_password=True
        )
        self.b_login = ft.ElevatedButton("Iniciar Sesión", on_click=self.try_login)
        self.b_clear = ft.ElevatedButton("Limpiar", on_click=self.clear)
        self.bgcolor = ft.Colors.with_opacity(0.4, ft.Colors.PRIMARY_CONTAINER)
        if not self.tf_username.value and not self.tf_password.value:
            self.b_login.disabled = True
            self.b_clear.disabled = True
            self.cb_remember.disabled = (
                True  # Redundant, checkbox is not disabled/enabled by textfield change
            )
        self.main_content = ft.Column(
            [
                self.title_text,
                self.login_text,
                self.tf_username,
                self.tf_password,
                ft.Row(
                    [self.b_login, self.b_clear], alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row([self.cb_remember], alignment=ft.MainAxisAlignment.CENTER),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.width = 500
        self.height = 500
        self.border_radius = 20
        self.border = ft.border.all(1, ft.Colors.PRIMARY)
        self.content = self.main_content
