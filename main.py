from flet import *
import sqlite3
import pandas as pd
from io import BytesIO
import asyncio
import uuid
import os
from datetime import datetime

# ألوان مخصصة
PRIMARY_COLOR = Colors.BLUE_800
SECONDARY_COLOR = Colors.GREY_200
ACCENT_COLOR = Colors.AMBER_600
TEXT_COLOR = Colors.BLACK87

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect("alson_education.db")
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        code TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        department TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        password TEXT NOT NULL
    )''')
    # جدول المحتوى
    c.execute('''CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        uploaded_by TEXT NOT NULL,
        upload_date TEXT NOT NULL
    )''')
    # جدول الشات
    c.execute('''CREATE TABLE IF NOT EXISTS chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_code TEXT NOT NULL,
        receiver_code TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )''')
    # إضافة أدمن افتراضي
    c.execute("SELECT * FROM users WHERE code='admin123'")
    if not c.fetchone():
        c.execute("INSERT INTO users (code, username, department, role, password) VALUES (?, ?, ?, ?, ?)",
                  ("admin123", "Admin", "إدارة", "admin", "adminpass"))
    conn.commit()
    conn.close()

init_db()

# متغيرات الحالة
class AppState:
    def __init__(self):
        self.current_user = {"email": None, "code": None, "role": None, "department": None}
        self.is_loading = False

app_state = AppState()

# شريط التطبيق
def create_appbar(page, is_admin=False):
    items = [
        PopupMenuItem(text="الملف الشخصي", on_click=lambda _: page.go("/الملف_الشخصي"), icon=icons.PERSON),
        PopupMenuItem(text="النتيجة", on_click=lambda _: page.go("/النتيجه"), icon=icons.GRADE),
        PopupMenuItem(text="المحتوى", on_click=lambda _: page.go("/المحتوى"), icon=icons.FOLDER),
        PopupMenuItem(text="الشات", on_click=lambda _: page.go("/الشات"), icon=icons.CHAT),
        PopupMenuItem(text="المساعدة", on_click=lambda _: page.go("/المساعدة"), icon=icons.HELP),
        PopupMenuItem(text="تسجيل الخروج", on_click=lambda _: page.go("/"), icon=icons.LOGOUT),
    ]
    if is_admin:
        items.insert(0, PopupMenuItem(text="إدارة المستخدمين", on_click=lambda _: page.go("/ادارة_المستخدمين"), icon=icons.EDIT))
        items.insert(1, PopupMenuItem(text="رفع المحتوى", on_click=lambda _: page.go("/رفع_المحتوى"), icon=icons.UPLOAD))

    return AppBar(
        title=Text('الألسن للعلوم الحديثة', color=Colors.WHITE, size=25, weight=FontWeight.BOLD),
        bgcolor=PRIMARY_COLOR,
        center_title=True,
        elevation=10,
        leading=Icon(icons.SCHOOL, color=Colors.WHITE, size=30),
        actions=[PopupMenuButton(icon=icons.MORE_VERT, items=items, tooltip="القائمة")]
    )

# دالة لإنشاء واجهة مع رسوم متحركة
def create_view(page, route, content, is_admin=False):
    stack_controls = [AnimatedSwitcher(content, transition=AnimatedSwitcherTransition.FADE, duration=500)]
    if app_state.is_loading:
        stack_controls.append(CircularProgressIndicator(color=PRIMARY_COLOR))

    return View(
        route,
        [
            create_appbar(page, is_admin),
            Container(
                content=Stack(stack_controls),
                padding=padding.all(20),
                bgcolor=SECONDARY_COLOR,
                expand=True,
                border_radius=10,
                shadow=BoxShadow(blur_radius=10, color=Colors.GREY_400)
            )
        ],
        vertical_alignment=MainAxisAlignment.START,
        horizontal_alignment=CrossAxisAlignment.CENTER,
        bgcolor=SECONDARY_COLOR,
        scroll=ScrollMode.AUTO
    )

# الواجهة الرئيسية
def main(page: Page):
    page.title = 'Alson Education'
    page.theme_mode = ThemeMode.LIGHT
    page.bgcolor = SECONDARY_COLOR
    page.padding = 0

    # حقول الإدخال
    username_field = TextField(
        label="اسم الطالب", prefix_icon=icons.PERSON, border_radius=15, bgcolor=Colors.WHITE,
        border_color=PRIMARY_COLOR, text_style=TextStyle(color=TEXT_COLOR, size=16)
    )
    password_field = TextField(
        label="كود الطالب", prefix_icon=icons.LOCK, password=True, can_reveal_password=True,
        border_radius=15, bgcolor=Colors.WHITE, border_color=PRIMARY_COLOR,
        text_style=TextStyle(color=TEXT_COLOR, size=16)
    )

    async def validate_login_async(e):
        app_state.is_loading = True
        page.update()
        username, password = username_field.value.strip(), password_field.value.strip()
        conn = sqlite3.connect("alson_education.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            app_state.current_user.update({"email": user[1], "code": user[0], "role": user[3], "department": user[2]})
            page.go("/الصفحه الراسية")
        else:
            page.snack_bar = SnackBar(content=Text("بيانات غير صحيحة", color=Colors.RED), open=True)
        app_state.is_loading = False
        page.update()

    def route_change(route):
        page.views.clear()
        is_admin = app_state.current_user["role"] == "admin"

        # صفحة تسجيل الدخول
        if page.route == "/":
            page.views.append(
                create_view(
                    page,
                    "/",
                    Column([
                        Image(src="assets/img/icon.png", width=150, fit=ImageFit.CONTAIN),
                        Text("مرحبًا بك في الألسن!", size=30, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        username_field,
                        password_field,
                        ElevatedButton(
                            "تسجيل الدخول",
                            on_click=lambda e: asyncio.run(validate_login_async(e)),
                            width=200, height=50, elevation=5,
                            style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, shape=RoundedRectangleBorder(radius=12)),
                        ),
                        TextButton("هل نسيت كلمة المرور؟", style=ButtonStyle(color=PRIMARY_COLOR))
                    ], alignment=MainAxisAlignment.CENTER, spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER)
                )
            )

        # الصفحة الرئيسية
        elif page.route == "/الصفحه الراسية":
            page.views.append(
                create_view(
                    page,
                    "/الصفحه الراسية",
                    Column([
                        Text(f"مرحباً {app_state.current_user['email']}", size=24, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Card(
                            content=Container(
                                Column([
                                    Text(f"جدول قسم {app_state.current_user['department']}", size=18, weight=FontWeight.BOLD),
                                    Image(src="assets/img/po.jpg", width=340, fit=ImageFit.COVER, border_radius=10),
                                   
                                ]),
                                padding=10
                            ),
                            elevation=8, shape=RoundedRectangleBorder(radius=15), surface_tint_color=Colors.BLUE_50
                        ),
                        ResponsiveRow([
                            ElevatedButton("عرض النتيجة", on_click=lambda _: page.go("/النتيجه"), style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3), col={"xs": 6, "md": 4}),
                            ElevatedButton("المحتوى", on_click=lambda _: page.go("/المحتوى"), style=ButtonStyle(bgcolor=ACCENT_COLOR, color=Colors.WHITE, elevation=3), col={"xs": 6, "md": 4}),
                            ElevatedButton("الشات", on_click=lambda _: page.go("/الشات"), style=ButtonStyle(bgcolor=Colors.GREEN_600, color=Colors.WHITE, elevation=3), col={"xs": 6, "md": 4})
                        ])
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        # صفحة الملف الشخصي
        elif page.route == "/الملف_الشخصي":
            if not app_state.current_user["code"]:
                page.go("/")
                page.snack_bar = SnackBar(content=Text("يرجى تسجيل الدخول أولاً", color=Colors.RED), open=True)
                page.update()
                return

            conn = sqlite3.connect("alson_education.db")
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE code=?", (app_state.current_user["code"],))
            user = c.fetchone()
            conn.close()

            if user is None:
                page.go("/")
                page.snack_bar = SnackBar(content=Text("المستخدم غير موجود", color=Colors.RED), open=True)
                page.update()
                return

            page.views.append(
                create_view(
                    page,
                    "/الملف_الشخصي",
                    Column([
                        Text("الملف الشخصي", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Card(
                            content=Container(
                                Column([
                                    Row([Icon(icons.PERSON, color=PRIMARY_COLOR), Text(f"الاسم: {user[1]}", size=16, color=TEXT_COLOR)]),
                                    Row([Icon(icons.LOCK, color=PRIMARY_COLOR), Text(f"الكود: {user[0]}", size=16, color=TEXT_COLOR)]),
                                    Row([Icon(icons.GROUP, color=PRIMARY_COLOR), Text(f"القسم: {user[2]}", size=16, color=TEXT_COLOR)]),
                                ], spacing=10),
                                padding=15
                            ),
                            elevation=5, shape=RoundedRectangleBorder(radius=15), width=340
                        ),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        # صفحة إدارة المستخدمين
        elif page.route == "/ادارة_المستخدمين" and is_admin:
            file_picker = FilePicker(on_result=lambda e: asyncio.run(upload_users_async(e, page)))

            async def upload_users_async(e, page):
                app_state.is_loading = True
                page.update()
                if e.files:
                    file_path = e.files[0].path
                    try:
                        xl = pd.ExcelFile(file_path)
                        conn = sqlite3.connect("alson_education.db")
                        c = conn.cursor()
                        for sheet_name in xl.sheet_names:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                            department = sheet_name
                            for index, row in df.iterrows():
                                username = str(row.iloc[0])
                                password = str(row.iloc[1])
                                code = str(uuid.uuid4())[:8]
                                c.execute("INSERT OR REPLACE INTO users (code, username, department, role, password) VALUES (?, ?, ?, ?, ?)",
                                          (code, username, department, "user", password))
                        conn.commit()
                        conn.close()
                        page.snack_bar = SnackBar(content=Text("تم رفع المستخدمين بنجاح", color=Colors.GREEN), open=True)
                    except ImportError:
                        page.snack_bar = SnackBar(content=Text("يرجى تثبيت مكتبة openpyxl لرفع ملفات Excel", color=Colors.RED), open=True)
                    except Exception as ex:
                        page.snack_bar = SnackBar(content=Text(f"حدث خطأ أثناء رفع الملف: {str(ex)}", color=Colors.RED), open=True)
                else:
                    page.snack_bar = SnackBar(content=Text("لم يتم اختيار ملف", color=Colors.RED), open=True)
                app_state.is_loading = False
                page.update()
                page.go("/ادارة_المستخدمين")

            conn = sqlite3.connect("alson_education.db")
            c = conn.cursor()
            c.execute("SELECT * FROM users")
            users = c.fetchall()
            conn.close()

            user_table = DataTable(
                columns=[
                    DataColumn(Text("الكود", size=16, weight=FontWeight.BOLD)),
                    DataColumn(Text("اسم المستخدم", size=16, weight=FontWeight.BOLD)),
                    DataColumn(Text("القسم", size=16, weight=FontWeight.BOLD)),
                    DataColumn(Text("الدور", size=16, weight=FontWeight.BOLD)),
                    DataColumn(Text("كلمة المرور", size=16, weight=FontWeight.BOLD)),
                    DataColumn(Text("إجراءات", size=16, weight=FontWeight.BOLD)),
                ],
                rows=[
                    DataRow(cells=[
                        DataCell(Text(user[0])),
                        DataCell(Text(user[1])),
                        DataCell(Text(user[2])),
                        DataCell(Text(user[3])),
                        DataCell(Text(user[4])),
                        DataCell(Row([
                            IconButton(icons.VISIBILITY, icon_color=Colors.GREEN, on_click=lambda e, u=user: view_user(u, page), tooltip="عرض"),
                            IconButton(icons.EDIT, icon_color=Colors.BLUE, on_click=lambda e, u=user: edit_user(u, page), tooltip="تعديل"),
                            IconButton(icons.DELETE, icon_color=Colors.RED, on_click=lambda e, u=user: delete_user(u, page), tooltip="حذف")
                        ]))
                    ]) for user in users
                ],
                border=border.all(1, Colors.GREY_400),
                heading_row_color=Colors.GREY_200,
                column_spacing=20,
                data_row_max_height=50,
            )

            def view_user(user, page):
                page.dialog = AlertDialog(
                    title=Text("تفاصيل المستخدم"),
                    content=Column([
                        Text(f"الكود: {user[0]}", size=16),
                        Text(f"اسم المستخدم: {user[1]}", size=16),
                        Text(f"القسم: {user[2]}", size=16),
                        Text(f"الدور: {user[3]}", size=16),
                        Text(f"كلمة المرور: {user[4]}", size=16),
                    ], spacing=10),
                    actions=[TextButton("إغلاق", on_click=lambda _: setattr(page.dialog, "open", False) or page.update())],
                    actions_alignment=MainAxisAlignment.END
                )
                page.dialog.open = True
                page.update()

            def edit_user(user, page):
                edit_username = TextField(label="اسم المستخدم", value=user[1])
                edit_department = TextField(label="القسم", value=user[2])
                edit_role = Dropdown(
                    label="الدور",
                    options=[dropdown.Option("user", "مستخدم"), dropdown.Option("admin", "أدمن")],
                    value=user[3]
                )
                edit_password = TextField(label="كلمة المرور", value=user[4], password=True, can_reveal_password=True)

                def save_changes(e):
                    conn = sqlite3.connect("alson_education.db")
                    c = conn.cursor()
                    c.execute("UPDATE users SET username=?, department=?, role=?, password=? WHERE code=?",
                              (edit_username.value, edit_department.value, edit_role.value, edit_password.value, user[0]))
                    conn.commit()
                    conn.close()
                    page.dialog.open = False
                    page.update()
                    page.go("/ادارة_المستخدمين")

                page.dialog = AlertDialog(
                    title=Text("تعديل بيانات المستخدم"),
                    content=Column([edit_username, edit_department, edit_role, edit_password], spacing=10),
                    actions=[
                        ElevatedButton("حفظ", on_click=save_changes),
                        TextButton("إلغاء", on_click=lambda _: setattr(page.dialog, "open", False) or page.update())
                    ],
                    actions_alignment=MainAxisAlignment.END
                )
                page.dialog.open = True
                page.update()

            def delete_user(user, page):
                conn = sqlite3.connect("alson_education.db")
                c = conn.cursor()
                c.execute("DELETE FROM users WHERE code=?", (user[0],))
                conn.commit()
                conn.close()
                page.go("/ادارة_المستخدمين")

            page.views.append(
                create_view(
                    page,
                    "/ادارة_المستخدمين",
                    Column([
                        Text("إدارة المستخدمين", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        ElevatedButton(
                            "رفع ملف Excel", on_click=lambda _: file_picker.pick_files(allowed_extensions=["xlsx"]),
                            width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3)
                        ),
                        Text("الصيغة: العمود الأول: اسم المستخدم، العمود الثاني: كلمة المرور، اسم الورقة: القسم", size=14, color=Colors.GREY_600),
                        Divider(),
                        Text("قائمة المستخدمين", size=20, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Column(controls=[Container(content=user_table, width=800)], scroll="auto", expand=True),
                        file_picker
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=True
                )
            )

        # صفحة رفع المحتوى (للأدمن فقط)
        elif page.route == "/رفع_المحتوى" and is_admin:
            content_title = TextField(label="عنوان المحتوى", border_radius=15, bgcolor=Colors.WHITE, border_color=PRIMARY_COLOR)
            content_picker = FilePicker(on_result=lambda e: asyncio.run(upload_content_async(e, page, content_title.value)))

            async def upload_content_async(e, page, title):
                if not title.strip():
                    page.snack_bar = SnackBar(content=Text("يرجى إدخال عنوان المحتوى", color=Colors.RED), open=True)
                    page.update()
                    return
                if e.files:
                    file = e.files[0]
                    file_path = os.path.join("uploads", file.name)
                    os.makedirs("uploads", exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(open(file.path, "rb").read())
                    file_type = file.name.split(".")[-1].lower()
                    conn = sqlite3.connect("alson_education.db")
                    c = conn.cursor()
                    c.execute("INSERT INTO content (title, file_path, file_type, uploaded_by, upload_date) VALUES (?, ?, ?, ?, ?)",
                              (title, file_path, file_type, app_state.current_user["code"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    conn.close()
                    page.snack_bar = SnackBar(content=Text("تم رفع المحتوى بنجاح", color=Colors.GREEN), open=True)
                    page.update()
                else:
                    page.snack_bar = SnackBar(content=Text("لم يتم اختيار ملف", color=Colors.RED), open=True)
                    page.update()

            page.views.append(
                create_view(
                    page,
                    "/رفع_المحتوى",
                    Column([
                        Text("رفع المحتوى", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        content_title,
                        ElevatedButton(
                            "اختر ملف", on_click=lambda _: content_picker.pick_files(),
                            width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3)
                        ),
                        Text("الصيغ المدعومة: PDF, صور (PNG, JPG), نصوص (TXT)", size=14, color=Colors.GREY_600),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=ACCENT_COLOR, color=Colors.WHITE, elevation=3)),
                        content_picker
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=True
                )
            )

        # صفحة عرض المحتوى (للمستخدمين العاديين)
        elif page.route == "/المحتوى":
            conn = sqlite3.connect("alson_education.db")
            c = conn.cursor()
            c.execute("SELECT * FROM content")
            contents = c.fetchall()
            conn.close()

            content_list = Column([
                Card(
                    content=Container(
                        Column([
                            Text(f"العنوان: {content[1]}", size=16, weight=FontWeight.BOLD),
                            Text(f"نوع الملف: {content[3]}", size=14),
                            Text(f"تاريخ الرفع: {content[5]}", size=14),
                            ElevatedButton("عرض", on_click=lambda e, path=content[2]: page.launch_url(path) if os.path.exists(path) else page.snack_bar.__setattr__("content", Text("الملف غير موجود", color=Colors.RED)) or page.snack_bar.__setattr__("open", True) or page.update())
                        ], spacing=10),
                        padding=10
                    ),
                    elevation=5, shape=RoundedRectangleBorder(radius=15)
                ) for content in contents
            ], scroll="auto")

            page.views.append(
                create_view(
                    page,
                    "/المحتوى",
                    Column([
                        Text("المحتوى التعليمي", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        content_list if contents else Text("لا يوجد محتوى متاح حاليًا", size=16, color=Colors.GREY_600),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        # صفحة الشات
        elif page.route == "/الشات":
            conn = sqlite3.connect("alson_education.db")
            c = conn.cursor()
            c.execute("SELECT code, username FROM users WHERE code != ?", (app_state.current_user["code"],))
            users = c.fetchall()
            conn.close()

            receiver_dropdown = Dropdown(
                label="اختر المستخدم",
                options=[dropdown.Option(user[0], user[1]) for user in users],
                border_radius=15, bgcolor=Colors.WHITE, border_color=PRIMARY_COLOR
            )
            message_field = TextField(label="اكتب رسالتك", border_radius=15, bgcolor=Colors.WHITE, border_color=PRIMARY_COLOR, multiline=True)
            chat_display = Column(scroll="auto", expand=True)

            def load_chat(e=None):
                if receiver_dropdown.value:
                    conn = sqlite3.connect("alson_education.db")
                    c = conn.cursor()
                    c.execute("SELECT sender_code, message, timestamp FROM chat WHERE (sender_code=? AND receiver_code=?) OR (sender_code=? AND receiver_code=?) ORDER BY timestamp",
                              (app_state.current_user["code"], receiver_dropdown.value, receiver_dropdown.value, app_state.current_user["code"]))
                    messages = c.fetchall()
                    conn.close()
                    chat_display.controls = [
                        Container(
                            content=Text(f"{msg[1]} - {msg[2]}", size=14, color=TEXT_COLOR if msg[0] == app_state.current_user["code"] else Colors.BLUE_600),
                            padding=padding.all(10),
                            bgcolor=Colors.GREY_100 if msg[0] == app_state.current_user["code"] else Colors.BLUE_50,
                            border_radius=10,
                            alignment=alignment.top_right if msg[0] == app_state.current_user["code"] else alignment.top_left
                        ) for msg in messages
                    ]
                    page.update()

            def send_message(e):
                if receiver_dropdown.value and message_field.value.strip():
                    conn = sqlite3.connect("alson_education.db")
                    c = conn.cursor()
                    c.execute("INSERT INTO chat (sender_code, receiver_code, message, timestamp) VALUES (?, ?, ?, ?)",
                              (app_state.current_user["code"], receiver_dropdown.value, message_field.value.strip(), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    conn.close()
                    message_field.value = ""
                    load_chat()

            receiver_dropdown.on_change = load_chat

            page.views.append(
                create_view(
                    page,
                    "/الشات",
                    Column([
                        Text("الشات", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        receiver_dropdown,
                        chat_display,
                        Row([
                            message_field,
                            IconButton(icons.SEND, icon_color=PRIMARY_COLOR, on_click=send_message)
                        ]),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        # صفحة استعلام النتائج
        elif page.route == "/النتيجه":
            student_id = TextField(label="رقم الجلوس", prefix_icon=icons.NUMBERS, border_radius=15, bgcolor=Colors.WHITE, width=320, keyboard_type=KeyboardType.NUMBER, border_color=PRIMARY_COLOR)
            def show_results(e):
                if student_id.value.strip():
                    page.go("/عرض النتيجة")
                else:
                    page.snack_bar = SnackBar(content=Text("يرجى إدخال رقم الجلوس", color=Colors.RED), open=True)
                    page.update()

            page.views.append(
                create_view(
                    page,
                    "/النتيجه",
                    Column([
                        Text("استعلام النتائج", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Card(content=Container(Column([student_id, Text("تأكد من إدخال رقم الجلوس الصحيح", size=14, color=Colors.GREY_600)]), padding=10), elevation=5, shape=RoundedRectangleBorder(radius=15), width=340),
                        ElevatedButton("عرض النتيجة", on_click=show_results, width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], alignment=MainAxisAlignment.CENTER, spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        # صفحة عرض النتيجة
        elif page.route == "/عرض النتيجة":
            results = {"math": "85/100", "science": "92/100", "arabic": "88/100"}
            page.views.append(
                create_view(
                    page,
                    "/عرض النتيجة",
                    Column([
                        Text("نتائج الامتحانات", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Card(
                            content=Container(
                                Column([
                                    Text(f"الاسم: {app_state.current_user['email']}", size=16, color=TEXT_COLOR),
                                    Divider(),
                                    Text(f"html: {results.get('math')}", size=14, color=TEXT_COLOR),
                                    Text(f"Ai: {results.get('science')}", size=14, color=TEXT_COLOR),
                                    Text(f"python: {results.get('arabic')}", size=14, color=TEXT_COLOR),
                                ]),
                                padding=15
                            ),
                            elevation=5, shape=RoundedRectangleBorder(radius=15), width=340
                        ),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/النتيجه"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        # صفحة المساعدة
        elif page.route == "/المساعدة":
            page.views.append(
                create_view(
                    page,
                    "/المساعدة",
                    Column([
                        Text("مركز المساعدة", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Card(
                            content=Container(
                                Column([
                                    Text("تواصلوا معنا", size=18, weight=FontWeight.BOLD, color=TEXT_COLOR),
                                    Text("البريد: support@alson.edu", size=14, color=TEXT_COLOR),
                                    Text("الهاتف: 01023828155", size=14, color=TEXT_COLOR),
                                    Divider(),
                                    Text("ساعات العمل: 8 صباحاً - 4 مساءً", size=14, color=TEXT_COLOR),
                                ]),
                                padding=15
                            ),
                            elevation=5, shape=RoundedRectangleBorder(radius=15), width=340
                        ),
                      
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        # صفحة الخطأ
        else:
            page.views.append(
                create_view(
                    page,
                    page.route,
                    Column([
                        Text("الصفحة غير موجودة", size=20, color=Colors.RED),
                        ElevatedButton("العودة للرئيسية", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], alignment=MainAxisAlignment.CENTER, spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        page.update()

    def view_pop(view):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    from flet import app
    app(target=main, assets_dir="assets")