import flet as ft
from datetime import datetime

chats = {}

def main(page: ft.Page):
    page.title = "Flet Chat System"
    page.padding = 20
    page.spacing = 10

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
        chats_list = ft.Column()
        for chat_name, chat_data in chats.items():
            chats_list.controls.append(
                ft.Text(f"• {chat_name} ({len(chat_data['users'])} пользователей)")
            )
        
        page.add(
            ft.Text("Система чатов", size=24, weight=ft.FontWeight.BOLD),
            status_text,
            ft.Container(height=20),
            
            ft.Text("Доступные чаты:", size=16, weight=ft.FontWeight.BOLD),
            chats_list if chats else ft.Text("Чатов пока нет"),
            ft.Container(height=20),
            
            ft.Text("Создать новый чат:", size=18, weight=ft.FontWeight.BOLD),
            chat_name_input,
            chat_password_input,
            ft.ElevatedButton("Создать чат", on_click=create_chat, width=200),
            
            ft.Container(height=30),
            
            ft.Text("Подключиться к чату:", size=18, weight=ft.FontWeight.BOLD),
            join_chat_name_input,
            join_chat_password_input,
            user_name_input,
            ft.ElevatedButton("Подключиться", on_click=join_chat, width=200)
        )

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
            'subscribers': set()  # Храним подписчиков этого чата
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
        
        # Сохраняем текущий чат и пользователя
        global current_chat_name, current_user_name
        current_chat_name = chat_name
        current_user_name = user_name
            
        chats[chat_name]['users'].add(user_name)
        show_chat_interface(chat_name, user_name)

    def show_chat_interface(chat_name, user_name):
        page.clean()
        
        # Функция для обработки сообщений ТОЛЬКО этого чата
        def on_chat_message(msg):
            # Проверяем, что сообщение для этого чата
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

        # Подписываемся на сообщения
        page.pubsub.subscribe(on_chat_message)

        def send_message(e):
            text = message_input.value.strip()
            if text:
                # Создаем сообщение с идентификатором чата
                message_data = {
                    'chat_name': chat_name,  # Важно: указываем для какого чата сообщение
                    'user': user_name,
                    'text': text,
                    'time': datetime.now().strftime("%H:%M")
                }
                
                # Отправляем сообщение всем подписчикам
                page.pubsub.send_all(message_data)
                
                # Сохраняем сообщение в истории этого чата
                chats[chat_name]['messages'].append(message_data)
                message_input.value = ""
                page.update()

        # Загружаем историю ТОЛЬКО этого чата
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

        # Интерфейс чата
        page.add(
            ft.Row([
                ft.Text(f"Чат: {chat_name}", size=20, weight=ft.FontWeight.BOLD, expand=True),
                ft.Text(f"Вы: {user_name}"),
                ft.ElevatedButton("Выйти", on_click=lambda e: exit_chat(chat_name, user_name))
            ]),
            
            ft.Container(
                content=messages,
                expand=True,
                border=ft.border.all(1)
            ),
            
            ft.Row([
                message_input,
                ft.ElevatedButton("Отправить", on_click=send_message)
            ])
        )
        
        # Прокручиваем к последнему сообщению
        if messages.controls:
            messages.scroll_to(offset=-1, duration=0)

    def exit_chat(chat_name, user_name):
        # Удаляем пользователя из чата
        if chat_name in chats and user_name in chats[chat_name]['users']:
            chats[chat_name]['users'].remove(user_name)
        
        # Возвращаем в главное меню
        show_main_menu()

    show_main_menu()
    
if __name__ == "__main__":

    ft.app(target=main)


