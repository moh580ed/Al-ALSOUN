from flet import *

# ألوان مخصصة
PRIMARY_COLOR = Colors.BLUE_800
SECONDARY_COLOR = Colors.GREY_200
ACCENT_COLOR = Colors.AMBER_600
TEXT_COLOR = Colors.BLACK87

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

    def validate_login(e):
        app_state.is_loading = True
        page.update()
        username, password = username_field.value.strip(), password_field.value.strip()
        # محاكاة تسجيل الدخول بدون قاعدة بيانات
        if username == "admin" and password == "adminpass":
            app_state.current_user.update({"email": "Admin", "code": "admin123", "role": "admin", "department": "إدارة"})
            page.go("/الصفحه الراسية")
        else:
            page.snack_bar = SnackBar(content=Text("بيانات غير صحيحة", color=Colors.RED), open=True)
        app_state.is_loading = False
        page.update()

    def route_change(route):
        page.views.clear()
        is_admin = app_state.current_user["role"] == "admin"

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
                            on_click=validate_login,
                            width=200, height=50, elevation=5,
                            style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, shape=RoundedRectangleBorder(radius=12)),
                        ),
                        TextButton("هل نسيت كلمة المرور؟", style=ButtonStyle(color=PRIMARY_COLOR))
                    ], alignment=MainAxisAlignment.CENTER, spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER)
                )
            )

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

        elif page.route == "/الملف_الشخصي":
            if not app_state.current_user["code"]:
                page.go("/")
                page.snack_bar = SnackBar(content=Text("يرجى تسجيل الدخول أولاً", color=Colors.RED), open=True)
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
                                    Row([Icon(icons.PERSON, color=PRIMARY_COLOR), Text(f"الاسم: {app_state.current_user['email']}", size=16, color=TEXT_COLOR)]),
                                    Row([Icon(icons.LOCK, color=PRIMARY_COLOR), Text(f"الكود: {app_state.current_user['code']}", size=16, color=TEXT_COLOR)]),
                                    Row([Icon(icons.GROUP, color=PRIMARY_COLOR), Text(f"القسم: {app_state.current_user['department']}", size=16, color=TEXT_COLOR)]),
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

        elif page.route == "/ادارة_المستخدمين" and is_admin:
            page.views.append(
                create_view(
                    page,
                    "/ادارة_المستخدمين",
                    Column([
                        Text("إدارة المستخدمين", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Text("هذه الصفحة غير متاحة في النسخة المحمولة حاليًا", size=16, color=Colors.GREY_600),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=True
                )
            )

        elif page.route == "/رفع_المحتوى" and is_admin:
            page.views.append(
                create_view(
                    page,
                    "/رفع_المحتوى",
                    Column([
                        Text("رفع المحتوى", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Text("هذه الصفحة غير متاحة في النسخة المحمولة حاليًا", size=16, color=Colors.GREY_600),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=ACCENT_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=True
                )
            )

        elif page.route == "/المحتوى":
            page.views.append(
                create_view(
                    page,
                    "/المحتوى",
                    Column([
                        Text("المحتوى التعليمي", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Text("لا يوجد محتوى متاح حاليًا", size=16, color=Colors.GREY_600),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

        elif page.route == "/الشات":
            page.views.append(
                create_view(
                    page,
                    "/الشات",
                    Column([
                        Text("الشات", size=28, weight=FontWeight.BOLD, color=PRIMARY_COLOR),
                        Text("هذه الصفحة غير متاحة في النسخة المحمولة حاليًا", size=16, color=Colors.GREY_600),
                        ElevatedButton("عودة", on_click=lambda _: page.go("/الصفحه الراسية"), width=200, style=ButtonStyle(bgcolor=PRIMARY_COLOR, color=Colors.WHITE, elevation=3))
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

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
                                    Text("البريد: alalsunacademy@gmail.com", size=14, color=TEXT_COLOR),
                                    Text("الهاتف: 01023828155", size=14, color=TEXT_COLOR),
                                    Divider(),
                                    Text("ساعات العمل: 9 صباحاً - 4 مساءً", size=14, color=TEXT_COLOR),
                                ]),
                                padding=15
                            ),
                            elevation=5, shape=RoundedRectangleBorder(radius=15), width=340
                        ),
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    is_admin=is_admin
                )
            )

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
