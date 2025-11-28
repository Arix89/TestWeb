import os
import flet as ft

def main(page: ft.Page):
    page.title = "Мое приложение на Railway"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    counter = 0
    
    def button_clicked(e):
        nonlocal counter
        counter += 1
        text_field.value = f"Зачетов по физике {counter} шт"
        page.update()

    text_field = ft.Text(size=20, weight="bold")
    
    page.add(
        ft.Column([
            ft.Text("🚀 Удачи на физике!", size=24),
            ft.ElevatedButton("Нажми меня", on_click=button_clicked),
            text_field,
        ], alignment=ft.MainAxisAlignment.CENTER)
    )
'''
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, host="0.0.0.0", view=None)
'''    
if __name__ == "__main__":

    ft.app(target=main)
