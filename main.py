import flet as ft
from datetime import datetime

chats = {}
current_chat_name = None
current_user_name = None

def main(page: ft.Page):
    page.title = "WebChat"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Элементы интерфейса
    messages = ft.ListView(
        expand=True,
        spacing=12,
        padding=20,
        auto_scroll=False
    )
    
    message_input = ft.TextField(
        hint_text="Напишите сообщение...",
        expand=True,
        border_color=ft.Colors.OUTLINE,
        filled=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=25,
        text_size=14,
        content_padding=ft.padding.only(left=20, right=20, top=15, bottom=15)
    )
    
    # Переменные для удаления
    delete_password_verify = ft.TextField(
        label="Пароль для удаления",
        password=True,
        border_color=ft.Colors.OUTLINE,
        filled=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=12,
        text_size=14
    )
    delete_status_text = ft.Text("", size=14)

    def show_welcome_screen(e=None):
        global current_chat_name, current_user_name
        current_chat_name = None
        current_user_name = None
        page.pubsub.unsubscribe_all()
        page.clean()
        
        welcome_content = ft.Container(
            content=ft.Column([
                # Заголовок
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "WebChat",
                            size=32,
                            weight=ft.FontWeight.W_700,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.BLUE
                        ),
                        ft.Text(
                            "Общайтесь легко и безопасно",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_600
                        )
                    ]),
                    padding=ft.padding.only(bottom=40)
                ),
                
                # Карточки выбора действия
                ft.ResponsiveRow(
                    [
                        # Создать чат
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINED, size=48, color=ft.Colors.BLUE),
                                        ft.Text("Создать чат", size=20, weight=ft.FontWeight.W_600),
                                        ft.Text("Создайте новый чат для общения", size=14, color=ft.Colors.GREY_600),
                                        ft.Container(height=20),
                                        ft.FilledButton(
                                            "Создать",
                                            on_click=lambda e: show_create_chat_screen(),
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                                padding=20
                                            )
                                        )
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                                    padding=30,
                                    alignment=ft.alignment.center
                                ),
                                elevation=3
                            ),
                            col={"sm": 12, "md": 6},
                            padding=10
                        ),
                        
                        # Войти в чат
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Icon(ft.Icons.LOGIN_OUTLINED, size=48, color=ft.Colors.GREEN),
                                        ft.Text("Войти в чат", size=20, weight=ft.FontWeight.W_600),
                                        ft.Text("Подключитесь к существующему чату", size=14, color=ft.Colors.GREY_600),
                                        ft.Container(height=20),
                                        ft.FilledButton(
                                            "Войти",
                                            on_click=lambda e: show_join_chat_screen(),
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                                padding=20,
                                                bgcolor=ft.Colors.GREEN
                                            )
                                        )
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                                    padding=30,
                                    alignment=ft.alignment.center
                                ),
                                elevation=3
                            ),
                            col={"sm": 12, "md": 6},
                            padding=10
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                
                # Список доступных чатов (если есть)
                ft.Container(
                    content=ft.Column([
                        ft.Text("Доступные чаты", size=18, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                        ft.Container(
                            content=create_chats_list(),
                            padding=10
                        )
                    ]) if chats else ft.Container(),
                    padding=ft.padding.only(top=40)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
            padding=40,
            alignment=ft.alignment.center
        )
        
        page.add(
            ft.Container(
                content=welcome_content,
                expand=True,
                alignment=ft.alignment.center
            )
        )

    def create_chats_list():
        chats_list = ft.Column(spacing=8)
        for chat_name, chat_data in chats.items():
            chat_type_icon = "🔒" if chat_data['type'] == 'private' else "🔓"
            chats_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(
                        ft.Icons.LOCK_OUTLINED if chat_data['type'] == 'private' else ft.Icons.PUBLIC_OUTLINED,
                        color=ft.Colors.BLUE
                    ),
                    title=ft.Text(chat_name),
                    subtitle=ft.Text(f"{chat_type_icon} {len(chat_data['users'])} участников"),
                    on_click=lambda e, cn=chat_name: prefill_and_join(cn),
                )
            )
        return chats_list

    def prefill_and_join(chat_name):
        show_join_chat_screen(chat_name)

    def show_create_chat_screen():
        page.clean()
        
        # Поля для создания чата
        chat_name_input = ft.TextField(
            label="Название чата",
            border_color=ft.Colors.OUTLINE,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            text_size=14
        )
        
        chat_type = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="public", label="🔓 Публичный чат (без пароля для входа)"),
                ft.Radio(value="private", label="🔒 Приватный чат (требуется пароль для входа)"),
            ]),
            value="public"
        )
        
        chat_password_input = ft.TextField(
            label="Пароль для входа",
            password=True,
            border_color=ft.Colors.OUTLINE,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            visible=False
        )
        
        delete_password_input = ft.TextField(
            label="Пароль для удаления*",
            password=True,
            border_color=ft.Colors.OUTLINE,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            text_size=14
        )
        
        status_text = ft.Text("", size=14)

        def update_chat_type(e):
            chat_password_input.visible = chat_type.value == "private"
            page.update()

        chat_type.on_change = update_chat_type

        def create_chat(e):
            name = chat_name_input.value.strip()
            password = chat_password_input.value.strip() if chat_type.value == "private" else ""
            delete_password = delete_password_input.value.strip()
            
            if not name:
                status_text.value = "Введите название чата"
                status_text.color = ft.Colors.RED
                page.update()
                return
                
            if not delete_password:
                status_text.value = "Введите пароль для удаления чата"
                status_text.color = ft.Colors.RED
                page.update()
                return
                
            if name in chats:
                status_text.value = "Чат с таким названием уже существует"
                status_text.color = ft.Colors.RED
                page.update()
                return
                
            chats[name] = {
                'type': chat_type.value,
                'password': password,
                'delete_password': delete_password,
                'messages': [],
                'users': set(),
                'creator': "Неизвестный"
            }
            
            status_text.value = f"✅ Чат '{name}' успешно создан!"
            status_text.color = ft.Colors.GREEN
            page.update()
            
            # Возврат на главный экран через 2 секунды
            import threading
            timer = threading.Timer(2.0, show_welcome_screen)
            timer.start()

        create_content = ft.Container(
            content=ft.Column([
                # Заголовок
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_OUTLINED,
                            on_click=lambda e: show_welcome_screen()
                        ),
                        ft.Text("Создание чата", size=24, weight=ft.FontWeight.W_700, expand=True),
                    ]),
                    padding=ft.padding.only(bottom=30)
                ),
                
                # Форма создания
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Настройки чата", size=20, weight=ft.FontWeight.W_600),
                            ft.Text("Создайте новый чат для общения", size=14, color=ft.Colors.GREY_600),
                            ft.Container(height=20),
                            
                            chat_name_input,
                            
                            ft.Text("Тип чата:", size=16, weight=ft.FontWeight.W_500),
                            chat_type,
                            chat_password_input,
                            
                            ft.Text("Безопасность:", size=16, weight=ft.FontWeight.W_500),
                            ft.Text("Пароль для удаления потребуется для удаления чата в будущем", 
                                   size=12, color=ft.Colors.GREY_600),
                            delete_password_input,
                            
                            ft.Container(height=20),
                            status_text,
                            
                            ft.Container(
                                content=ft.FilledButton(
                                    "Создать чат",
                                    on_click=create_chat,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        padding=20
                                    )
                                ),
                                alignment=ft.alignment.center
                            )
                        ], spacing=16),
                        padding=30
                    ),
                    width=400
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
            padding=20,
            alignment=ft.alignment.center
        )
        
        page.add(
            ft.Container(
                content=create_content,
                expand=True,
                alignment=ft.alignment.center
            )
        )

    def show_join_chat_screen(prefilled_chat_name=None):
        page.clean()
        
        # Поля для входа
        join_chat_name_input = ft.TextField(
            label="Название чата",
            border_color=ft.Colors.OUTLINE,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            text_size=14,
            value=prefilled_chat_name or ""
        )
        
        join_chat_password_input = ft.TextField(
            label="Пароль (если требуется)",
            password=True,
            border_color=ft.Colors.OUTLINE,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            text_size=14
        )
        
        user_name_input = ft.TextField(
            label="Ваше имя",
            border_color=ft.Colors.OUTLINE,
            filled=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            text_size=14
        )
        
        status_text = ft.Text("", size=14)

        def join_chat(e):
            global current_chat_name, current_user_name
            chat_name = join_chat_name_input.value.strip()
            password = join_chat_password_input.value.strip()
            user_name = user_name_input.value.strip()
            
            if not all([chat_name, user_name]):
                status_text.value = "Введите название чата и ваше имя"
                status_text.color = ft.Colors.RED
                page.update()
                return
                
            if chat_name not in chats:
                status_text.value = "Чат не найден"
                status_text.color = ft.Colors.RED
                page.update()
                return
                
            chat_data = chats[chat_name]
            
            if chat_data['type'] == 'private':
                if not password:
                    status_text.value = "Для приватного чата нужен пароль"
                    status_text.color = ft.Colors.RED
                    page.update()
                    return
                if chat_data['password'] != password:
                    status_text.value = "Неверный пароль для чата"
                    status_text.color = ft.Colors.RED
                    page.update()
                    return
            
            current_chat_name = chat_name
            current_user_name = user_name
            chats[chat_name]['users'].add(user_name)
            show_chat_interface()

        join_content = ft.Container(
            content=ft.Column([
                # Заголовок
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_OUTLINED,
                            on_click=lambda e: show_welcome_screen()
                        ),
                        ft.Text("Вход в чат", size=24, weight=ft.FontWeight.W_700, expand=True),
                    ]),
                    padding=ft.padding.only(bottom=30)
                ),
                
                # Форма входа
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Подключение к чату", size=20, weight=ft.FontWeight.W_600),
                            ft.Text("Войдите в существующий чат", size=14, color=ft.Colors.GREY_600),
                            ft.Container(height=20),
                            
                            ft.Text("Доступные чаты:", size=16, weight=ft.FontWeight.W_500),
                            ft.Container(
                                content=create_chats_list(),
                                height=150,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                padding=10,
                                border_radius=8
                            ),
                            
                            ft.Text("Данные для входа:", size=16, weight=ft.FontWeight.W_500),
                            join_chat_name_input,
                            join_chat_password_input,
                            user_name_input,
                            
                            ft.Container(height=20),
                            status_text,
                            
                            ft.Container(
                                content=ft.FilledButton(
                                    "Войти в чат",
                                    on_click=join_chat,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=12),
                                        padding=20,
                                        bgcolor=ft.Colors.GREEN
                                    )
                                ),
                                alignment=ft.alignment.center
                            )
                        ], spacing=16),
                        padding=30
                    ),
                    width=400
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
            padding=20,
            alignment=ft.alignment.center
        )
        
        page.add(
            ft.Container(
                content=join_content,
                expand=True,
                alignment=ft.alignment.center
            )
        )

    def show_chat_interface():
        global current_chat_name, current_user_name
        
        page.clean()
        delete_password_verify.value = ""
        delete_status_text.value = ""
        
        def on_chat_message(msg):
            if msg.get('chat_name') == current_chat_name:
                messages.controls.append(create_message_bubble(msg))
                messages.scroll_to(offset=-1, duration=300)
                page.update()

        def create_message_bubble(msg):
            is_own = msg['user'] == current_user_name
            return ft.Container(
                content=ft.Column([
                    ft.Text(
                        msg['user'],
                        size=12,
                        color=ft.Colors.BLUE if is_own else ft.Colors.GREY_600,
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(
                        content=ft.Text(msg['text'], size=14),
                        padding=12,
                        bgcolor=ft.Colors.BLUE_50 if is_own else ft.Colors.GREY_100,
                        border_radius=12
                    ),
                    ft.Text(
                        msg.get('time', ''),
                        size=10,
                        color=ft.Colors.GREY_500
                    )
                ], spacing=4),
                margin=ft.margin.only(
                    left=50 if is_own else 0,
                    right=0 if is_own else 50,
                    bottom=12
                ),
                alignment=ft.alignment.center_right if is_own else ft.alignment.center_left
            )

        page.pubsub.subscribe(on_chat_message)

        def send_message(e):
            text = message_input.value.strip()
            if text:
                message_data = {
                    'chat_name': current_chat_name,
                    'user': current_user_name,
                    'text': text,
                    'time': datetime.now().strftime("%H:%M")
                }
                page.pubsub.send_all(message_data)
                chats[current_chat_name]['messages'].append(message_data)
                message_input.value = ""
                page.update()

        # Загружаем историю
        messages.controls.clear()
        for msg in chats[current_chat_name]['messages']:
            messages.controls.append(create_message_bubble(msg))

        chat_info = chats[current_chat_name]
        
        # Интерфейс чата
        chat_layout = ft.Column([
            # Шапка
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Icon(
                                ft.Icons.LOCK_OUTLINED if chat_info['type'] == 'private' else ft.Icons.PUBLIC_OUTLINED,
                                size=16,
                                color=ft.Colors.BLUE
                            ),
                            ft.Text(current_chat_name, size=18, weight=ft.FontWeight.W_600),
                        ]),
                        ft.Text(f"{len(chat_info['users'])} участников • Вы: {current_user_name}", 
                               size=12, color=ft.Colors.GREY_600),
                    ], expand=True),
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINED,
                            on_click=lambda e: show_delete_dialog(),
                            tooltip="Удалить чат",
                            icon_color=ft.Colors.RED
                        ),
                        ft.ElevatedButton(
                            "Выйти",
                            on_click=lambda e: exit_chat(),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                padding=15
                            )
                        ),
                    ], spacing=10)
                ]),
                padding=16,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300))
            ),
            
            # Сообщения
            ft.Container(
                content=messages,
                expand=True,
                padding=10,
                bgcolor=ft.Colors.GREY_50
            ),
            
            # Ввод сообщения
            ft.Container(
                content=ft.Row([
                    message_input,
                    ft.IconButton(
                        ft.Icons.SEND_OUTLINED,
                        on_click=send_message,
                        style=ft.ButtonStyle(
                            shape=ft.CircleBorder(),
                            padding=15,
                            bgcolor=ft.Colors.BLUE
                        ),
                        icon_color=ft.Colors.WHITE
                    )
                ], vertical_alignment=ft.CrossAxisAlignment.END),
                padding=16,
                bgcolor=ft.Colors.WHITE
            )
        ], expand=True)
        
        page.add(chat_layout)
        
        if messages.controls:
            messages.scroll_to(offset=-1, duration=0)

    def show_delete_dialog():
        page.clean()
        
        chat_info = chats.get(current_chat_name, {})
        
        delete_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DELETE_OUTLINED, size=64, color=ft.Colors.RED),
                ft.Text("Удаление чата", size=28, weight=ft.FontWeight.W_700),
                ft.Text(f"Чат: {current_chat_name}", size=18),
                ft.Text(f"Тип: {'🔒 Приватный' if chat_info.get('type') == 'private' else '🔓 Публичный'}", size=14),
                ft.Container(height=30),
                
                ft.Text("Введите пароль для удаления:", size=16),
                delete_password_verify,
                delete_status_text,
                
                ft.Container(height=30),
                
                ft.Row([
                    ft.OutlinedButton(
                        "Отмена", 
                        on_click=lambda e: show_chat_interface(),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=20
                        )
                    ),
                    ft.ElevatedButton(
                        "Удалить чат",
                        on_click=lambda e: verify_delete_chat(),
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=20,
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.RED
                        )
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
            width=400,
            alignment=ft.alignment.center
        )
        
        page.add(
            ft.Container(
                content=delete_content,
                expand=True,
                alignment=ft.alignment.center
            )
        )

    def verify_delete_chat():
        input_password = delete_password_verify.value.strip()
        
        if not input_password:
            delete_status_text.value = "Введите пароль для удаления"
            delete_status_text.color = ft.Colors.RED
            page.update()
            return
            
        if current_chat_name not in chats:
            delete_status_text.value = "Чат уже удален"
            delete_status_text.color = ft.Colors.RED
            page.update()
            return
            
        if chats[current_chat_name]['delete_password'] != input_password:
            delete_status_text.value = "Неверный пароль для удаления"
            delete_status_text.color = ft.Colors.RED
            page.update()
            return
        
        del chats[current_chat_name]
        show_welcome_screen()

    def exit_chat():
        if current_chat_name in chats and current_user_name in chats[current_chat_name]['users']:
            chats[current_chat_name]['users'].remove(current_user_name)
        show_welcome_screen()

    # Запуск приложения
    show_welcome_screen()
    
if __name__ == "__main__":

    ft.app(target=main)




