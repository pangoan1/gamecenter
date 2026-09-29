import json
import os
import random
import hashlib

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.core.window import Window

# ------------------------------------------------------------
# Local Game Center
# Accounts and scores are stored locally in users.json.
# Admin/owner password: 1392javad1392
# ------------------------------------------------------------

Window.clearcolor = (0.05, 0.07, 0.14, 1)

DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "users.json"
)

ADMIN_PASSWORD = "1392javad1392"
current_user = None


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def add_points(username, amount):
    users = load_users()
    if username in users:
        users[username]["score"] += int(amount)
        save_users(users)


def get_score(username):
    users = load_users()
    return users.get(username, {}).get("score", 0)


def rtl(text):
    # Kept simple so the app can run without extra packages.
    return str(text)


class BaseScreen(Screen):
    def button(self, text, callback):
        b = Button(
            text=rtl(text),
            font_size=dp(17),
            size_hint_y=None,
            height=dp(56)
        )
        b.bind(on_release=callback)
        return b

    def title(self, text):
        return Label(
            text=rtl(text),
            font_size=dp(27),
            size_hint_y=None,
            height=dp(62)
        )

    def go(self, name, *_):
        self.manager.current = name


class LoginScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()

        box = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(10)
        )

        box.add_widget(self.title("🎮 GAME CENTER"))

        box.add_widget(Label(
            text=rtl("ورود به حساب"),
            size_hint_y=None,
            height=dp(35)
        ))

        self.username = TextInput(
            hint_text=rtl("نام کاربری"),
            multiline=False,
            size_hint_y=None,
            height=dp(55)
        )
        self.password = TextInput(
            hint_text=rtl("رمز عبور"),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(self.username)
        box.add_widget(self.password)

        self.message = Label(text="", font_size=dp(15))
        box.add_widget(self.message)

        box.add_widget(self.button("🔐 ورود", self.login))
        box.add_widget(self.button("📝 ساخت حساب", lambda *_: self.go("register")))
        box.add_widget(self.button("👑 پنل ادمین", lambda *_: self.go("admin_login")))

        self.add_widget(box)

    def login(self, *_):
        global current_user

        username = self.username.text.strip()
        password = self.password.text

        users = load_users()

        if username not in users:
            self.message.text = rtl("❌ این حساب وجود ندارد.")
            return

        if users[username]["password"] != hash_password(password):
            self.message.text = rtl("❌ رمز عبور اشتباه است.")
            return

        current_user = username
        self.manager.current = "menu"


class RegisterScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()

        box = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(10)
        )

        box.add_widget(self.title("📝 ساخت حساب"))

        self.username = TextInput(
            hint_text=rtl("نام کاربری"),
            multiline=False,
            size_hint_y=None,
            height=dp(55)
        )
        self.password = TextInput(
            hint_text=rtl("رمز عبور"),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(55)
        )
        self.password2 = TextInput(
            hint_text=rtl("تکرار رمز عبور"),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(self.username)
        box.add_widget(self.password)
        box.add_widget(self.password2)

        self.message = Label(text="")
        box.add_widget(self.message)

        box.add_widget(self.button("✅ ساخت حساب", self.register))
        box.add_widget(self.button("⬅️ بازگشت", lambda *_: self.go("login")))

        self.add_widget(box)

    def register(self, *_):
        username = self.username.text.strip()
        password = self.password.text
        password2 = self.password2.text

        if len(username) < 3:
            self.message.text = rtl("❌ نام کاربری حداقل ۳ حرف باشد.")
            return

        if not username.replace("_", "").isalnum():
            self.message.text = rtl("❌ فقط حروف، عدد و _ استفاده کن.")
            return

        if len(password) < 4:
            self.message.text = rtl("❌ رمز حداقل ۴ کاراکتر باشد.")
            return

        if password != password2:
            self.message.text = rtl("❌ دو رمز یکسان نیستند.")
            return

        users = load_users()

        if username in users:
            self.message.text = rtl("❌ این نام کاربری قبلاً گرفته شده.")
            return

        users[username] = {
            "password": hash_password(password),
            "score": 0
        }
        save_users(users)

        self.message.text = rtl("🎉 حساب ساخته شد! حالا وارد شو.")
        self.username.text = ""
        self.password.text = ""
        self.password2.text = ""


class MenuScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()

        if not current_user:
            self.manager.current = "login"
            return

        box = BoxLayout(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(9)
        )

        box.add_widget(self.title("🎮 GAME CENTER"))

        self.info = Label(
            text="",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(48)
        )
        box.add_widget(self.info)
        self.refresh()

        box.add_widget(self.button("🎯 حدس عدد", lambda *_: self.go("guess")))
        box.add_widget(self.button("✊ سنگ، کاغذ، قیچی", lambda *_: self.go("rps")))
        box.add_widget(self.button("🎲 تاس", lambda *_: self.go("dice")))
        box.add_widget(self.button("🧠 اطلاعات عمومی", lambda *_: self.go("quiz")))
        box.add_widget(self.button("🏆 لیدربورد", lambda *_: self.go("leaderboard")))
        box.add_widget(self.button("🚪 خروج از حساب", self.logout))

        self.add_widget(box)

    def refresh(self):
        self.info.text = rtl(
            f"👤 {current_user}    ⭐ امتیاز: {get_score(current_user)}"
        )

    def logout(self, *_):
        global current_user
        current_user = None
        self.manager.current = "login"


class GuessScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.secret = random.randint(1, 100)
        self.attempts_left = 3
        self.finished = False

        box = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(10)
        )

        box.add_widget(self.title("🎯 حدس عدد"))

        self.info = Label(
            text=rtl("یک عدد بین ۱ تا ۱۰۰ پیدا کن.\n۳ فرصت داری."),
            font_size=dp(17)
        )
        box.add_widget(self.info)

        self.entry = TextInput(
            hint_text=rtl("عدد"),
            input_filter="int",
            multiline=False,
            halign="center",
            font_size=dp(23),
            size_hint_y=None,
            height=dp(60)
        )
        box.add_widget(self.entry)

        self.result = Label(text=rtl("عددت را وارد کن."))
        box.add_widget(self.result)

        self.check_button = self.button("🔎 حدس بزن", self.check)
        box.add_widget(self.check_button)

        box.add_widget(self.button("⬅️ بازگشت", self.go_menu))
        self.add_widget(box)

    def go_menu(self, *_):
        self.manager.current = "menu"

    def check(self, *_):
        if self.finished:
            return

        value = self.entry.text.strip()
        self.entry.text = ""

        if not value:
            self.result.text = rtl("⚠️ یک عدد وارد کن.")
            return

        guess = int(value)

        if guess < 1 or guess > 100:
            self.result.text = rtl("⚠️ عدد باید بین ۱ تا ۱۰۰ باشد.")
            return

        self.attempts_left -= 1

        if guess == self.secret:
            points = {2: 30, 1: 20, 0: 10}[self.attempts_left]
            add_points(current_user, points)
            self.finished = True
            self.check_button.disabled = True
            self.result.text = rtl(
                f"🎉 درست گفتی!\nعدد {self.secret} بود.\n+{points} امتیاز"
            )
            return

        if self.attempts_left == 0:
            add_points(current_user, -10)
            self.finished = True
            self.check_button.disabled = True
            self.result.text = rtl(
                f"❌ باختی!\nعدد {self.secret} بود.\n-10 امتیاز"
            )
            return

        hint = "بزرگ‌تر" if guess < self.secret else "کوچک‌تر"
        self.info.text = rtl(f"باید عدد {hint} باشد.\nفرصت باقی‌مانده: {self.attempts_left}")
        self.result.text = rtl("❌ این حدس درست نبود.")


class RPSScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(10))
        box.add_widget(self.title("✊ سنگ، کاغذ، قیچی"))

        self.result = Label(text=rtl("انتخاب کن."), font_size=dp(18))
        box.add_widget(self.result)

        for text, value in [("✊ سنگ", "سنگ"), ("✋ کاغذ", "کاغذ"), ("✌️ قیچی", "قیچی")]:
            box.add_widget(self.button(text, lambda _, v=value: self.play(v)))

        box.add_widget(self.button("⬅️ بازگشت", self.go_menu))
        self.add_widget(box)

    def go_menu(self, *_):
        self.manager.current = "menu"

    def play(self, player):
        computer = random.choice(["سنگ", "کاغذ", "قیچی"])

        if player == computer:
            self.result.text = rtl(f"🤝 کامپیوتر: {computer}\nمساوی؛ امتیازی تغییر نکرد.")
            return

        win = (
            (player == "سنگ" and computer == "قیچی") or
            (player == "کاغذ" and computer == "سنگ") or
            (player == "قیچی" and computer == "کاغذ")
        )

        if win:
            add_points(current_user, 10)
            self.result.text = rtl(f"🎉 بردی! +10\n🤖 کامپیوتر: {computer}")
        else:
            add_points(current_user, -10)
            self.result.text = rtl(f"😅 باختی! -10\n🤖 کامپیوتر: {computer}")


class DiceScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        box = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(12))
        box.add_widget(self.title("🎲 تاس"))

        self.face = Label(text="🎲", font_size=dp(70))
        box.add_widget(self.face)

        self.result = Label(text=rtl("تو و کامپیوتر تاس می‌اندازید."))
        box.add_widget(self.result)

        box.add_widget(self.button("🎲 انداختن تاس", self.roll))
        box.add_widget(self.button("⬅️ بازگشت", self.go_menu))
        self.add_widget(box)

    def go_menu(self, *_):
        self.manager.current = "menu"

    def roll(self, *_):
        player = random.randint(1, 6)
        computer = random.randint(1, 6)
        self.face.text = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][player - 1]

        if player == computer:
            self.result.text = rtl(f"تو: {player} | کامپیوتر: {computer}\n🤝 مساوی؛ امتیازی تغییر نکرد.")
        elif player > computer:
            add_points(current_user, 10)
            self.result.text = rtl(f"تو: {player} | کامپیوتر: {computer}\n🎉 بردی! +10")
        else:
            add_points(current_user, -10)
            self.result.text = rtl(f"تو: {player} | کامپیوتر: {computer}\n😅 باختی! -10")


QUESTIONS = [
    ("پایتخت ایران کدام است؟", ["تهران", "تبریز", "شیراز", "کرمان"], 0),
    ("سیاره سرخ کدام است؟", ["زهره", "مریخ", "مشتری", "عطارد"], 1),
    ("آب در چند درجه سانتی‌گراد می‌جوشد؟", ["۵۰", "۷۵", "۱۰۰", "۱۵۰"], 2),
    ("حاصل ۷ × ۸ چند است؟", ["۴۸", "۵۴", "۵۶", "۶۴"], 2),
]


class QuizScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        self.index = 0
        self.answered = False

        box = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(8))
        box.add_widget(self.title("🧠 اطلاعات عمومی"))

        self.question = Label(font_size=dp(17))
        box.add_widget(self.question)

        self.status = Label(font_size=dp(16))
        box.add_widget(self.status)

        self.answers = []
        for i in range(4):
            b = Button(font_size=dp(17), size_hint_y=None, height=dp(53))
            b.bind(on_release=lambda _, n=i: self.answer(n))
            self.answers.append(b)
            box.add_widget(b)

        box.add_widget(self.button("⬅️ بازگشت", self.go_menu))
        self.add_widget(box)
        self.show_question()

    def go_menu(self, *_):
        self.manager.current = "menu"

    def show_question(self):
        if self.index >= len(QUESTIONS):
            self.question.text = rtl("🏆 مسابقه تمام شد!")
            self.status.text = rtl("همه سؤال‌ها تمام شد.")
            for b in self.answers:
                b.disabled = True
            return

        self.answered = False
        q, options, correct = QUESTIONS[self.index]
        self.correct = correct

        self.question.text = rtl(f"سؤال {self.index + 1} از {len(QUESTIONS)}\n{q}")
        self.status.text = rtl("یک گزینه را انتخاب کن.")

        for i, b in enumerate(self.answers):
            b.text = rtl(options[i])
            b.disabled = False

    def answer(self, selected):
        if self.answered:
            return

        self.answered = True

        if selected == self.correct:
            add_points(current_user, 10)
            self.status.text = rtl("✅ درست! +10 امتیاز")
        else:
            add_points(current_user, -5)
            self.status.text = rtl("❌ اشتباه! -5 امتیاز")

        for b in self.answers:
            b.disabled = True

        self.index += 1

        from kivy.clock import Clock
        Clock.schedule_once(lambda _: self.show_question(), 0.8)


class LeaderboardScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()

        box = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(8))
        box.add_widget(self.title("🏆 لیدربورد"))

        users = load_users()
        ranking = sorted(
            users.items(),
            key=lambda item: item[1].get("score", 0),
            reverse=True
        )

        if not ranking:
            box.add_widget(Label(text=rtl("هنوز حسابی ساخته نشده.")))
        else:
            for pos, (name, data) in enumerate(ranking[:20], 1):
                box.add_widget(Label(
                    text=rtl(f"{pos}. {name} — ⭐ {data.get('score', 0)}"),
                    font_size=dp(17),
                    size_hint_y=None,
                    height=dp(38)
                ))

        box.add_widget(self.button("⬅️ بازگشت", self.go_menu))
        self.add_widget(box)

    def go_menu(self, *_):
        self.manager.current = "menu"


class AdminLoginScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()

        box = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(10))
        box.add_widget(self.title("👑 ورود ادمین"))

        self.password = TextInput(
            hint_text=rtl("رمز ادمین"),
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(58)
        )
        box.add_widget(self.password)

        self.message = Label(text="")
        box.add_widget(self.message)

        box.add_widget(self.button("🔓 ورود", self.login))
        box.add_widget(self.button("⬅️ بازگشت", lambda *_: self.go("login")))
        self.add_widget(box)

    def login(self, *_):
        if self.password.text == ADMIN_PASSWORD:
            self.manager.current = "admin"
        else:
            self.message.text = rtl("❌ رمز ادمین اشتباه است.")


class AdminScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()

        box = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(8))
        box.add_widget(self.title("👑 پنل ادمین"))

        users = load_users()

        if not users:
            box.add_widget(Label(text=rtl("هیچ کاربری وجود ندارد.")))
        else:
            for username, data in sorted(users.items()):
                row = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(55),
                    spacing=dp(5)
                )

                row.add_widget(Label(
                    text=rtl(f"{username}: ⭐ {data.get('score', 0)}"),
                    font_size=dp(15)
                ))

                minus = Button(text="-10", size_hint_x=None, width=dp(55))
                minus.bind(on_release=lambda _, u=username: self.change(u, -10))
                row.add_widget(minus)

                plus = Button(text="+10", size_hint_x=None, width=dp(55))
                plus.bind(on_release=lambda _, u=username: self.change(u, 10))
                row.add_widget(plus)

                box.add_widget(row)

        box.add_widget(self.button("➕ امتیاز دلخواه", lambda *_: self.go("admin_points")))
        box.add_widget(self.button("🔄 تازه‌سازی", lambda *_: self.go("admin")))
        box.add_widget(self.button("⬅️ خروج از پنل", lambda *_: self.go("login")))

        self.add_widget(box)

    def change(self, username, amount):
        add_points(username, amount)
        self.on_enter()


class AdminPointsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()

        box = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(10))
        box.add_widget(self.title("➕ تغییر امتیاز"))

        self.username = TextInput(
            hint_text=rtl("نام کاربری"),
            multiline=False,
            size_hint_y=None,
            height=dp(55)
        )
        self.amount = TextInput(
            hint_text=rtl("مقدار امتیاز، مثلاً 100 یا -50"),
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=dp(55)
        )

        box.add_widget(self.username)
        box.add_widget(self.amount)

        self.message = Label(text="")
        box.add_widget(self.message)

        box.add_widget(self.button("💾 اعمال", self.apply))
        box.add_widget(self.button("⬅️ بازگشت به پنل", lambda *_: self.go("admin")))

        self.add_widget(box)

    def apply(self, *_):
        username = self.username.text.strip()
        amount = self.amount.text.strip()

        users = load_users()

        if username not in users:
            self.message.text = rtl("❌ چنین کاربری وجود ندارد.")
            return

        if not amount:
            self.message.text = rtl("❌ مقدار امتیاز را وارد کن.")
            return

        add_points(username, int(amount))
        self.message.text = rtl(
            f"✅ انجام شد. امتیاز {username}: {get_score(username)}"
        )
        self.amount.text = ""


class GameCenterApp(App):
    def build(self):
        manager = ScreenManager()

        manager.add_widget(LoginScreen(name="login"))
        manager.add_widget(RegisterScreen(name="register"))
        manager.add_widget(MenuScreen(name="menu"))
        manager.add_widget(GuessScreen(name="guess"))
        manager.add_widget(RPSScreen(name="rps"))
        manager.add_widget(DiceScreen(name="dice"))
        manager.add_widget(QuizScreen(name="quiz"))
        manager.add_widget(LeaderboardScreen(name="leaderboard"))
        manager.add_widget(AdminLoginScreen(name="admin_login"))
        manager.add_widget(AdminScreen(name="admin"))
        manager.add_widget(AdminPointsScreen(name="admin_points"))

        return manager


GameCenterApp().run()
