import flet as ft


class MainSwitcher(ft.Container):
    def switch_to(self, index: int):
        if index < len(self.contents):
            self.main_switcher.content = self.contents[index]
        self.main_switcher.update()
        self.index = index

    def add_content(self, content: ft.Control):
        print(len(self.contents))
        self.contents.append(content)
        print(len(self.contents))
        return len(self.contents) - 1

    def __init__(
        self,
        contents: list[ft.Control] = [],
        index=0,
        transition: ft.AnimatedSwitcherTransition = ft.AnimatedSwitcherTransition.FADE,
        duration: int = 300,
        reverse_duration: int = 300,
    ):
        super().__init__()
        self.contents = contents
        self.expand = True
        self.index = index
        # self.bgcolor = ft.
        self.main_switcher = ft.AnimatedSwitcher(
            ft.Container(),
            expand=True,
            transition=transition,
            duration=duration,
            reverse_duration=reverse_duration,
        )
        if len(self.contents) > 0 and self.index < len(self.contents):
            self.main_switcher.content = self.contents[self.index]
        self.content = ft.Row(
            [
                ft.Column(
                    [self.main_switcher],
                    expand=True,
                    alignment="center",
                    horizontal_alignment="center",
                )
            ],
            expand=True,
            alignment="center",
            vertical_alignment="center",
        )
