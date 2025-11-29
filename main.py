import flet as ft
from datetime import datetime

chats = {}

def main(page: ft.Page):
    page.title = "Flet Chat System"
    page.padding = 0
    page.spacing = 0
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Элементы интерфейса
    chat_name_input = ft.TextField(label="Название чата", width=300)
    chat_password_input = ft.TextField(label="Пароль чата", password=True, width=300)
    join_chat_name_input = ft.TextField(label="Название чата", width=300)
    join_chat_password_input = ft.TextField(label="Пароль", password=True, width=300)
    user_name_input = ft.TextField(label="Ваше имя", width=300)
    
    messages = ft.ListView(expand=True, spacing=8, padding=15, auto_scroll=False)
    message_input = ft.TextField(label="Сообщение...", expand=True)
    
    status_text = ft.Text("", size=14)
    
    current_chat_name = None
    current_user_name = None

    def show_main_menu(e=None):
        # Очищаем подписки при выходе из чата
        page.pubsub.unsubscribe_all()
        
        page.clean()
        
        # Создаем список доступных чатов
        chats_list = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
        for chat_name, chat_data in chats.items():
            chats_list.controls.append(
                ft.Container(
                    content=ft.Text(f"• {chat_name} ({len(chat_data['users'])} пользователей)"),
                    padding=5
                )
            )
        
        main_content = ft.Container(
            content=ft.Column([
                ft.Text("Система чатов", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                status_text,
                ft.Container(height=20),
                
                ft.Text("Доступные чаты:", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=chats_list if chats else ft.Text("Чатов пока нет"),
                    height=150,
                    border=ft.border.all(1),
                    padding=10,
                    border_radius=10
                ),
                ft.Container(height=20),
                
                ft.Text("Создать новый чат:", size=18, weight=ft.FontWeight.BOLD),
                chat_name_input,
                chat_password_input,
                ft.Container(
                    content=ft.ElevatedButton("Создать чат", on_click=create_chat, width=200),
                    alignment=ft.alignment.center
                ),
                
                ft.Container(height=30),
                
                ft.Text("Подключиться к чату:", size=18, weight=ft.FontWeight.BOLD),
                join_chat_name_input,
                join_chat_password_input,
                user_name_input,
                ft.Container(
                    content=ft.ElevatedButton("Подключиться", on_click=join_chat, width=200),
                    alignment=ft.alignment.center
                )
            ], 
            scroll=ft.ScrollMode.ADAPTIVE,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            width=400,
            alignment=ft.alignment.center
        )
        
        # Обертка для свайпа
        swipe_container = ft.GestureDetector(
            content=main_content,
            on_vertical_drag_update=lambda e: handle_swipe(e),
        )
        
        page.add(
            ft.Container(
                content=swipe_container,
                expand=True,
                alignment=ft.alignment.center
            )
        )

    def handle_swipe(e):
        # Обработка свайпа вниз для обновления
        if abs(e.delta_y) > 50:  # Минимальная дистанция свайпа
            if e.delta_y > 0:
                # Свайп вниз - обновляем список чатов
                show_main_menu()
            # Свайп вверх тоже можно обработать при необходимости

    def create_chat(e):
        chat_name = chat_name_input.value.strip()
        password = chat_password_input.value.strip()
        
        if not chat_name:
            status_text.value = "Введите название чата"
            page.update()
            return
            
        if not password:
            status_text.value = "Введите пароль для чата"
            page.update()
            return
            
        if chat_name in chats:
            status_text.value = "Чат с таким названием уже существует"
            page.update()
            return
            
        chats[chat_name] = {
            'password': password,
            'messages': [],
            'users': set(),
            'subscribers': set()
        }
        
        status_text.value = f"Чат '{chat_name}' успешно создан!"
        chat_name_input.value = ""
        chat_password_input.value = ""
        page.update()

    def join_chat(e):
        chat_name = join_chat_name_input.value.strip()
        password = join_chat_password_input.value.strip()
        user_name = user_name_input.value.strip()
        
        if not all([chat_name, password, user_name]):
            status_text.value = "Заполните все поля"
            page.update()
            return
            
        if chat_name not in chats:
            status_text.value = "Чат не найден"
            page.update()
            return
            
        if chats[chat_name]['password'] != password:
            status_text.value = "Неверный пароль"
            page.update()
            return
        
        current_chat_name = chat_name
        current_user_name = user_name
            
        chats[chat_name]['users'].add(user_name)
        show_chat_interface(chat_name, user_name)

    def show_chat_interface(chat_name, user_name):
        page.clean()
        
        def on_chat_message(msg):
            if msg.get('chat_name') == chat_name:
                current_time = datetime.now().strftime("%H:%M")
                message_text = f"{msg['user']}: {msg['text']}"
                
                message_container = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(message_text, size=16),
                        ], spacing=2, expand=True),
                        ft.Text(current_time, size=10)
                    ], 
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    border_radius=10,
                    margin=ft.margin.only(bottom=5)
                )
                messages.controls.append(message_container)
                messages.scroll_to(offset=-1, duration=300)
                page.update()

        page.pubsub.subscribe(on_chat_message)

        def send_message(e):
            text = message_input.value.strip()
            if text:
                message_data = {
                    'chat_name': chat_name,
                    'user': user_name,
                    'text': text,
                    'time': datetime.now().strftime("%H:%M")
                }
                
                page.pubsub.send_all(message_data)
                chats[chat_name]['messages'].append(message_data)
                message_input.value = ""
                page.update()

        # Загружаем историю чата
        for msg in chats[chat_name]['messages']:
            current_time = msg.get('time', datetime.now().strftime("%H:%M"))
            message_text = f"{msg['user']}: {msg['text']}"
            
            message_container = ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(message_text, size=16),
                    ], spacing=2, expand=True),
                    ft.Text(current_time, size=10)
                ], 
                vertical_alignment=ft.CrossAxisAlignment.START,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10,
                border_radius=10,
                margin=ft.margin.only(bottom=5)
            )
            messages.controls.append(message_container)

        # Интерфейс чата с адаптацией для мобильных
        chat_content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(f"Чат: {chat_name}", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Вы: {user_name}", size=12),
                    ], expand=True),
                    ft.ElevatedButton("Выйти", on_click=lambda e: exit_chat(chat_name, user_name))
                ]),
                padding=15,
                border=ft.border.only(bottom=ft.border.BorderSide(1))
            ),
            
            ft.Container(
                content=messages,
                expand=True,
            ),
            
            ft.Container(
                content=ft.Row([
                    message_input,
                    ft.ElevatedButton("Отправить", on_click=send_message)
                ], vertical_alignment=ft.CrossAxisAlignment.END),
                padding=15,
                border=ft.border.only(top=ft.border.BorderSide(1))
            )
        ], expand=True)
        
        # Обертка для свайпа в чате
        chat_swipe_container = ft.GestureDetector(
            content=chat_content,
            on_vertical_drag_update=lambda e: handle_chat_swipe(e, chat_name, user_name),
        )
        
        page.add(
            ft.Container(
                content=chat_swipe_container,
                expand=True
            )
        )
        
        # Прокручиваем к последнему сообщению
        if messages.controls:
            messages.scroll_to(offset=-1, duration=0)

    def handle_chat_swipe(e, chat_name, user_name):
        # Свайп вниз для выхода из чата
        if e.delta_y > 100:  # Свайп вниз на значительное расстояние
            exit_chat(chat_name, user_name)

    def exit_chat(chat_name, user_name):
        if chat_name in chats and user_name in chats[chat_name]['users']:
            chats[chat_name]['users'].remove(user_name)
        
        show_main_menu()

    # Начальная настройка страницы
    page.on_resize = lambda e: handle_resize()
    
    def handle_resize():
        # Адаптация под разные размеры экрана
        page.update()

    show_main_menu()
    
if __name__ == "__main__":

    ft.app(target=main)



