from flask import Flask, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import html

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "belgorod-rp-change-this-key")
DB = os.path.join(os.path.dirname(__file__), "forum.db")


def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


with connect() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        section TEXT NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")


def page(content, msg=""):
    return render_template_string("""
    <!doctype html>
    <html lang="ru">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="theme-color" content="#0b0b10">
    <title>BELGOROD RP — Игровой портал</title>
    <style>
    :root {
      --bg:#0b0b10;
      --panel:#15151e;
      --panel2:#1c1c28;
      --red:#ed263b;
      --red2:#ff5263;
      --text:#f4f4f8;
      --muted:#a6a6b8;
      --border:#30303d;
    }
    * { box-sizing:border-box; }
    html { min-height:100%; }
    body {
      margin:0;
      color:var(--text);
      background:
        radial-gradient(ellipse at 50% 0%, #35121c 0, transparent 48%),
        var(--bg);
      font:16px/1.6 system-ui,-apple-system,"Segoe UI",Arial,sans-serif;
    }
    a {
      color:var(--red2);
      text-decoration:none;
      transition:color .2s,background .2s,border-color .2s;
    }
    a:hover { color:#fff; }
    header {
      position:relative;
      overflow:hidden;
      padding:32px 18px 27px;
      text-align:center;
      background:linear-gradient(135deg,#211018,#171720 55%,#101017);
      border-bottom:1px solid #6d202d;
      box-shadow:0 8px 35px #0008;
    }
    header:after {
      content:"";
      display:block;
      height:3px;
      max-width:240px;
      margin:18px auto 0;
      border-radius:9px;
      background:linear-gradient(90deg,transparent,var(--red),transparent);
    }
    .brand {
      margin:0;
      color:#fff;
      font-size:clamp(28px,6vw,44px);
      font-weight:950;
      letter-spacing:2px;
      text-shadow:0 0 28px #ed263b55;
    }
    .brand span { color:var(--red2); }
    .tagline {
      margin:5px 0 0;
      color:var(--muted);
      letter-spacing:2px;
      text-transform:uppercase;
      font-size:12px;
    }
    main { max-width:1000px; margin:24px auto; padding:0 16px 40px; }
    nav {
      display:flex;
      flex-wrap:wrap;
      align-items:center;
      gap:8px;
      margin-bottom:24px;
      padding:12px;
      background:#14141cdd;
      border:1px solid var(--border);
      border-radius:14px;
    }
    nav a {
      display:inline-block;
      margin:0;
      padding:8px 12px;
      border-radius:8px;
      color:#dddde8;
      font-size:14px;
    }
    nav a:hover { background:#38202a; color:#fff; }
    .welcome {
      margin-left:auto;
      color:var(--muted);
      font-size:13px;
      padding:0 8px;
    }
    h2 { font-size:23px; line-height:1.3; margin:24px 0 14px; }
    .card {
      background:linear-gradient(145deg,var(--panel2),var(--panel));
      border:1px solid var(--border);
      padding:19px;
      margin:12px 0;
      border-radius:13px;
      box-shadow:0 7px 20px #0002;
      overflow-wrap:anywhere;
      transition:transform .18s,border-color .18s;
    }
    .card:hover { border-color:#71303b; }
    .card h2 { margin-top:0; }
    .card p { color:#d1d1dc; }
    .card a { font-weight:650; }
    input,textarea,select,button {
      display:block;
      box-sizing:border-box;
      width:100%;
      padding:12px 14px;
      margin:9px 0;
      color:var(--text);
      background:#0e0e15;
      border:1px solid #3b3b4b;
      border-radius:9px;
      font:inherit;
    }
    input:focus,textarea:focus,select:focus {
      outline:2px solid #ed263b66;
      border-color:var(--red);
    }
    textarea { min-height:120px; resize:vertical; }
    button {
      cursor:pointer;
      border:1px solid #ff5364;
      background:linear-gradient(135deg,#ed263b,#a91529);
      color:white;
      font-weight:750;
      box-shadow:0 5px 15px #ed263b22;
    }
    button:hover { filter:brightness(1.13); }
    small { color:var(--muted); }
    .error {
      color:#ff9aa4;
      background:#36141c;
      border:1px solid #78303d;
      border-radius:9px;
      padding:10px 13px;
    }
    footer {
      text-align:center;
      color:#777787;
      padding:20px 10px;
      font-size:12px;
    }
    @media(min-width:650px) {
      main { padding-left:22px; padding-right:22px; }
      nav { gap:12px; }
      .card { padding:22px; }
    }
    @media(max-width:480px) {
      header { padding:25px 12px 20px; }
      .tagline { letter-spacing:1px; }
      main { margin-top:15px; padding:0 11px 28px; }
      nav { gap:4px; padding:8px; }
      nav a { padding:8px; font-size:13px; }
      .welcome { margin-left:0; width:100%; padding:5px 8px; }
      h2 { font-size:21px; }
      .card { padding:15px; border-radius:11px; }
    }
    
    /* BELGOROD RP — улучшенное оформление обсуждений */
    .topic-hero {
      position:relative;
      overflow:hidden;
      padding:clamp(20px,4vw,32px);
      border:1px solid #57303b;
      border-top:3px solid #ed263b;
      border-radius:18px;
      background:radial-gradient(ellipse at top right,#51202d88,transparent 55%),
                 linear-gradient(145deg,#211720,#121219);
      box-shadow:0 14px 35px #0004;
    }
    .topic-hero h2 {
      overflow-wrap:anywhere;
      line-height:1.25;
    }
    .topic-author {
      display:flex;
      align-items:center;
      flex-wrap:wrap;
      gap:12px;
      padding:14px;
      margin:16px 0;
      border:1px solid #343441;
      border-radius:13px;
      background:#0e0e15aa;
    }
    .topic-message {
      padding:18px;
      border:1px solid #30303d;
      border-radius:13px;
      background:#101017;
      line-height:1.85;
      white-space:pre-wrap;
      overflow-wrap:anywhere;
    }
    .topic-reply {
      padding:clamp(14px,3vw,20px);
      margin:14px 0;
      border:1px solid #30303d;
      border-left:3px solid #ed263b;
      border-radius:14px;
      background:linear-gradient(145deg,#1c1c28,#14141b);
      transition:border-color .2s,transform .2s;
    }
    .topic-reply:hover {
      border-color:#71303b;
      transform:translateY(-1px);
    }
    .topic-reply-head {
      display:flex;
      align-items:flex-start;
      gap:12px;
      margin-bottom:14px;
    }
    .topic-reply-body {
      padding-top:12px;
      border-top:1px solid #30303d;
      line-height:1.8;
      white-space:pre-wrap;
      overflow-wrap:anywhere;
    }
    .topic-reply-number {
      margin-left:auto;
      color:#9999aa;
      font-size:12px;
    }
    .topic-compose {
      padding:clamp(16px,3vw,24px);
      margin-top:24px;
      border:1px solid #57303b;
      border-top:3px solid #ed263b;
      border-radius:16px;
      background:linear-gradient(145deg,#211720,#15151e);
    }
    .topic-compose textarea {
      min-height:150px;
      line-height:1.7;
    }
    .topic-compose button {
      min-height:46px;
    }
    @media(max-width:600px) {
      .topic-author,.topic-reply-head { gap:9px; }
      .topic-message { padding:14px; }
      .topic-reply-number { font-size:11px; }
    }
    @media(prefers-reduced-motion:reduce) {
      .topic-reply { transition:none; }
      .topic-reply:hover { transform:none; }
    }

    </style>
    </head>
    <body>
    <header>
      <h1 class="brand">BELGOROD <span>RP</span></h1>
      <p class="tagline">Игровое сообщество · Форум игроков</p>
    </header>
    <main>
      <nav>
        <a href="/">⌂ Главная</a>
        <a href="/new">＋ Создать тему</a>
        <a href="/rating">🏆 Рейтинг</a>
        {% if user %}
          <span class="welcome">Игрок: {{user}}</span>
          <a href="/profile/{{user}}">Профиль</a>
          <a href="/logout">Выйти</a>
        {% else %}
          <a href="/register">Регистрация</a>
          <a href="/login">Войти</a>
        {% endif %}
      </nav>
      {% if msg %}<p class="error">{{msg}}</p>{% endif %}
      {{content|safe}}
      <footer>BELGOROD RP · Играй по правилам сообщества</footer>
    </main>
    </body>
    </html>
    """, content=content, msg=msg, user=session.get("username"))


def search_topics(search_text="", section_name="", sort="new"):
    allowed_sorts = {"new", "old", "active"}
    if sort not in allowed_sorts:
        sort = "new"

    sql = """
        SELECT topics.*, users.username,
               (SELECT COUNT(*) FROM posts
                WHERE posts.topic_id = topics.id) AS reply_count
        FROM topics
        JOIN users ON users.id = topics.user_id
        WHERE 1=1
    """
    params = []

    if search_text:
        sql += " AND (topics.title LIKE ? OR topics.body LIKE ?)"
        pattern = "%" + search_text + "%"
        params.extend([pattern, pattern])

    if section_name:
        sql += " AND topics.section = ?"
        params.append(section_name)

    if sort == "old":
        sql += " ORDER BY topics.id ASC"
    elif sort == "active":
        sql += " ORDER BY reply_count DESC, topics.id DESC"
    else:
        sql += " ORDER BY topics.id DESC"

    sql += " LIMIT 100"

    with connect() as c:
        return c.execute(sql, params).fetchall()


@app.route("/")
def home():
    search_text = request.args.get("q", "").strip()[:100]
    section_name = request.args.get("section", "").strip()
    sort = request.args.get("sort", "new")

    allowed_sections = [
        "Новости сервера",
        "Государственные организации",
        "Жалобы на игроков",
        "Обсуждения",
        "Вопросы и помощь"
    ]

    if section_name not in allowed_sections:
        section_name = ""

    if sort not in ("new", "old", "active"):
        sort = "new"

    topics = search_topics(search_text, section_name, sort)

    with connect() as c:
        topic_count = c.execute(
            "SELECT COUNT(*) FROM topics"
        ).fetchone()[0]
        user_count = c.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]
        post_count = c.execute(
            "SELECT COUNT(*) FROM posts"
        ).fetchone()[0]

    sections = [
        ("📰", "Новости сервера",
         "Обновления, события и объявления администрации."),
        ("🏛️", "Государственные организации",
         "Фракции, государственные службы и наборы."),
        ("🛡️", "Жалобы на игроков",
         "Сообщи о нарушении правил сообщества."),
        ("💬", "Обсуждения",
         "Общение игроков, идеи и интересные темы."),
        ("❔", "Вопросы и помощь",
         "Задавай вопросы и помогай другим игрокам.")
    ]

    content = """
    <style>
      .rp-hero {
        position:relative;
        overflow:hidden;
        padding:clamp(25px,6vw,48px) 22px;
        border:1px solid #71303b;
        border-radius:20px;
        background:
          radial-gradient(ellipse at 90% 10%,#ed263b35,transparent 45%),
          linear-gradient(135deg,#32121d,#191923 65%,#111119);
        box-shadow:0 15px 45px #0005;
      }
      .rp-kicker {
        color:#ff7180;
        font-size:12px;
        font-weight:850;
        letter-spacing:2px;
        text-transform:uppercase;
      }
      .rp-hero h2 {
        margin:12px 0;
        font-size:clamp(27px,5vw,42px);
        line-height:1.15;
      }
      .rp-hero p { color:#ceceda; }
      .rp-actions {
        display:flex;
        flex-wrap:wrap;
        gap:10px;
        margin-top:22px;
      }
      .rp-btn {
        display:inline-block;
        padding:11px 17px;
        border:1px solid #ff6575;
        border-radius:11px;
        background:linear-gradient(135deg,#ed263b,#a91529);
        color:#fff;
        font-weight:800;
      }
      .rp-btn:hover { color:white; filter:brightness(1.12); }
      .rp-btn-secondary {
        background:#ffffff08;
        border-color:#ffffff30;
      }
      .rp-stats {
        display:grid;
        grid-template-columns:repeat(3,minmax(0,1fr));
        gap:12px;
        margin:16px 0 28px;
      }
      .rp-stat {
        min-width:0;
        padding:17px 10px;
        text-align:center;
        background:linear-gradient(145deg,#20202c,#14141c);
        border:1px solid #30303f;
        border-radius:15px;
      }
      .rp-stat-icon { font-size:23px; }
      .rp-stat-number {
        color:#fff;
        font-size:clamp(21px,4vw,29px);
        font-weight:900;
        line-height:1.4;
      }
      .rp-stat-label { color:#a6a6b8; font-size:12px; }
      .rp-section-list {
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));
        gap:12px;
      }
      .rp-section {
        display:flex;
        align-items:flex-start;
        gap:13px;
        min-width:0;
        padding:18px;
        margin:0;
        color:inherit;
        background:linear-gradient(145deg,#20202c,#14141c);
        border:1px solid #30303f;
        border-radius:15px;
        transition:transform .2s,border-color .2s;
      }
      .rp-section:hover {
        color:inherit;
        border-color:#8a3442;
        transform:translateY(-2px);
      }
      .rp-section-icon {
        display:grid;
        place-items:center;
        flex:0 0 44px;
        height:44px;
        border-radius:12px;
        background:#ed263b18;
        font-size:25px;
      }
      .rp-section-name { color:#ff7180; font-weight:850; }
      .rp-section-desc { margin-top:4px; color:#b9b9c9; font-size:13px; }
      .rp-topic {
        padding:16px;
        margin:11px 0;
        border:1px solid #30303f;
        border-left:3px solid #ed263b;
        border-radius:13px;
        background:#171720;
      }
      .rp-topic-title { font-size:16px; font-weight:800; }
      .rp-meta { margin-top:8px; color:#a6a6b8; font-size:12px; }
      .rp-form-grid {
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));
        gap:0 12px;
      }
      .rp-search-heading {
        display:flex;
        align-items:center;
        flex-wrap:wrap;
        gap:8px;
      }
      .rp-count {
        padding:3px 9px;
        border:1px solid #71303b;
        border-radius:20px;
        color:#ff7180;
        font-size:12px;
      }
      @media(max-width:480px) {
        .rp-stats { gap:7px; }
        .rp-stat { padding:13px 5px; }
        .rp-stat-label { font-size:11px; }
        .rp-section { padding:15px; }
      }
      @media(prefers-reduced-motion:reduce) {
        .rp-section { transition:none; }
      }
    </style>

    <section class="rp-hero">
      <div class="rp-kicker">🔴 Игровое сообщество · BELGOROD RP</div>
      <h2>Твой город.<br>Твоя история.</h2>
      <p>Общайся с игроками, следи за новостями сервера,
      обсуждай события и создавай собственные темы.</p>
      <div class="rp-actions">
        <a class="rp-btn" href="/new">＋ Создать тему</a>
        <a class="rp-btn rp-btn-secondary" href="/rating">🏆 Рейтинг игроков</a>
      </div>
    </section>

    <div class="rp-stats">
      <div class="rp-stat">
        <div class="rp-stat-icon">📚</div>
        <div class="rp-stat-number">""" + str(topic_count) + """</div>
        <div class="rp-stat-label">Тем на форуме</div>
      </div>
      <div class="rp-stat">
        <div class="rp-stat-icon">👥</div>
        <div class="rp-stat-number">""" + str(user_count) + """</div>
        <div class="rp-stat-label">Игроков</div>
      </div>
      <div class="rp-stat">
        <div class="rp-stat-icon">💬</div>
        <div class="rp-stat-number">""" + str(post_count) + """</div>
        <div class="rp-stat-label">Ответов</div>
      </div>
    </div>

    <h2>🎮 Разделы форума</h2>
    <div class="rp-section-list">
    """

    for icon, name, description in sections:
        safe_name = html.escape(name, quote=True)
        content += (
            '<a class="rp-section" href="/section/' + safe_name + '">'
            '<div class="rp-section-icon">' + icon + '</div>'
            '<div style="min-width:0;flex:1;">'
            '<div class="rp-section-name">' + safe_name + '</div>'
            '<div class="rp-section-desc">'
            + html.escape(description)
            + '</div></div><div style="color:#ed5263;font-size:22px;">›</div>'
            '</a>'
        )

    content += """
    </div>

    <h2>🔎 Поиск по форуму</h2>
    <div class="card">
      <form method="get" action="/">
        <label for="rp-q">Название или текст темы</label>
        <input id="rp-q" name="q" maxlength="100"
          placeholder="Например, набор во фракцию"
          value="""" + html.escape(search_text, quote=True) + """">
        <div class="rp-form-grid">
          <div>
            <label for="rp-section">Раздел</label>
            <select id="rp-section" name="section">
              <option value="">Все разделы</option>
    """

    for name in allowed_sections:
        selected = ' selected' if name == section_name else ''
        content += (
            '<option value="' + html.escape(name, quote=True) + '"'
            + selected + '>' + html.escape(name) + '</option>'
        )

    content += """
            </select>
          </div>
          <div>
            <label for="rp-sort">Сортировка</label>
            <select id="rp-sort" name="sort">
    """

    sort_options = [
        ("new", "Сначала новые"),
        ("old", "Сначала старые"),
        ("active", "Сначала обсуждаемые")
    ]

    for value, label in sort_options:
        selected = ' selected' if value == sort else ''
        content += (
            '<option value="' + value + '"' + selected + '>'
            + label + '</option>'
        )

    content += """
            </select>
          </div>
        </div>
        <button type="submit">🔎 Найти темы</button>
        <a href="/" style="display:inline-block;margin-top:5px;">Сбросить фильтры</a>
      </form>
    </div>

    <div class="rp-search-heading">
      <h2>🔥 Темы сообщества</h2>
      <span class="rp-count">""" + str(len(topics)) + """ результатов</span>
    </div>
    """

    if not topics:
        content += (
            '<div class="card"><p>Пока ничего не найдено. '
            'Попробуй изменить запрос или сбросить фильтры.</p></div>'
        )
    else:
        for t in topics:
            content += (
                '<article class="rp-topic">'
                '<a class="rp-topic-title" href="/topic/'
                + str(t["id"]) + '">'
                + html.escape(t["title"]) + '</a>'
                '<div class="rp-meta">📂 '
                + html.escape(t["section"]) + ' · 👤 '
                + html.escape(t["username"]) + ' · 💬 '
                + str(t["reply_count"]) + ' ответов</div>'
                '</article>'
            )

    if len(topics) == 100:
        content += (
            '<p><small>Показаны первые 100 результатов. '
            'Уточни поиск для более точного списка.</small></p>'
        )

    return page(content)


@app.route("/rating")
def rating():
    with connect() as c:
        players = c.execute("""
            SELECT
                users.id,
                users.username,
                users.role,
                COUNT(DISTINCT topics.id) AS topics_count,
                COUNT(DISTINCT posts.id) AS posts_count
            FROM users
            LEFT JOIN topics ON topics.user_id = users.id
            LEFT JOIN posts ON posts.user_id = users.id
            GROUP BY users.id, users.username, users.role
            ORDER BY
                (COUNT(DISTINCT topics.id) * 2
                 + COUNT(DISTINCT posts.id)) DESC,
                users.username COLLATE NOCASE ASC
            LIMIT 100
        """).fetchall()

    content = """
    <div class="card" style="background:linear-gradient(135deg,#35131d,#191923);border-color:#71303b;">
      <h2>🏆 Рейтинг игроков</h2>
      <p style="color:#c8c8d5;">Активность сообщества BELGOROD RP</p>
      <small>Расчёт: 2 балла за тему и 1 балл за ответ.</small>
    </div>
    """

    if not players:
        content += '<div class="card">Пока нет зарегистрированных игроков.</div>'
    else:
        for i, player in enumerate(players, start=1):
            score = player["topics_count"] * 2 + player["posts_count"]
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = "#" + str(i)

            username = html.escape(player["username"])
            role = html.escape(player["role"] or "Игрок")
            content += (
                '<div class="card" style="display:flex;gap:12px;align-items:center;'
                'border-left:3px solid #ed263b;">'
                '<div style="font-size:22px;min-width:42px;font-weight:800;">'
                + medal + '</div><div style="flex:1;min-width:0;">'
                '<a href="/profile/' + username
                + '" style="font-size:17px;font-weight:800;">' + username + '</a>'
                '<p style="margin:6px 0;color:#b9b9c9;"><small>'
                + role + ' · Тем: ' + str(player["topics_count"])
                + ' · Ответов: ' + str(player["posts_count"])
                + '</small></p></div>'
                '<div style="text-align:right;white-space:nowrap;">'
                '<b style="color:#ff6878;font-size:20px;">' + str(score)
                + '</b><br><small>баллов</small></div></div>'
            )

    content += '<p><a href="/">← На главную</a></p>'
    return page(content)

@app.route("/profile/<username>")
def profile(username):
    with connect() as c:
        u = c.execute(
            "SELECT id, username, role, bio FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if not u:
            return page(
                "<div class='card'><h2>Игрок не найден</h2></div>"
            ), 404

        topics_count = c.execute(
            "SELECT COUNT(*) FROM topics WHERE user_id=?",
            (u["id"],)
        ).fetchone()[0]

        posts_count = c.execute(
            "SELECT COUNT(*) FROM posts WHERE user_id=?",
            (u["id"],)
        ).fetchone()[0]

    bio = html.escape(u["bio"] or "Игрок пока не добавил описание.")
    name = html.escape(u["username"])
    role = html.escape(u["role"] or "Игрок")

    initials = "".join(
        part[0] for part in u["username"].split() if part
    )[:2].upper()
    initials = html.escape(initials or "?")

    achievements = []
    if topics_count >= 1:
        achievements.append(("📝", "Первая тема", "Создал свою тему"))
    if posts_count >= 10:
        achievements.append(("💬", "Активный участник", "10 ответов"))
    if posts_count >= 50:
        achievements.append(("🏆", "Мастер обсуждений", "50 ответов"))
    if topics_count >= 10:
        achievements.append(("🌟", "Ветеран форума", "10 тем"))

    achievements_html = "".join(
        "<div class='profile-achievement'>"
        "<span class='profile-achievement-icon'>" + icon + "</span>"
        "<span><b>" + html.escape(title) + "</b>"
        "<small>" + html.escape(description) + "</small></span></div>"
        for icon, title, description in achievements
    )

    if not achievements:
        achievements_html = (
            "<p class='profile-muted'>Достижения пока впереди — "
            "создай тему или присоединись к обсуждению!</p>"
        )

    is_owner = session.get("uid") == u["id"]

    content = """
    <style>
      .profile-wrap { max-width:800px; margin:0 auto; }
      .profile-hero {
        position:relative; overflow:hidden;
        display:flex; align-items:center; gap:20px;
        padding:26px;
        border:1px solid #71303b; border-radius:20px;
        background:radial-gradient(ellipse at 90% 0%,#ed263b30,transparent 50%),
          linear-gradient(135deg,#29121c,#191923);
      }
      .profile-avatar {
        display:grid; place-items:center; flex:0 0 84px;
        width:84px; height:84px; border-radius:23px;
        border:2px solid #ff657588;
        background:linear-gradient(135deg,#ed263b,#6c1729);
        color:white; font-size:29px; font-weight:950;
        box-shadow:0 8px 25px #ed263b35;
      }
      .profile-name { margin:0 0 8px; font-size:clamp(23px,5vw,32px); overflow-wrap:anywhere; }
      .profile-role {
        display:inline-block; padding:5px 10px; border-radius:20px;
        background:#ed263b20; border:1px solid #71303b;
        color:#ff8794; font-size:12px; font-weight:800;
      }
      .profile-muted { color:#a6a6b8; }
      .profile-stats {
        display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
        gap:12px; margin:14px 0;
      }
      .profile-stat {
        padding:17px; border:1px solid #30303f; border-radius:14px;
        background:linear-gradient(145deg,#20202c,#14141c);
      }
      .profile-stat-number { font-size:27px; font-weight:900; }
      .profile-stat-label { color:#a6a6b8; font-size:13px; }
      .profile-achievements {
        display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));
        gap:10px;
      }
      .profile-achievement {
        display:flex; align-items:center; gap:12px; padding:13px;
        border:1px solid #49303a; border-radius:12px; background:#201820;
      }
      .profile-achievement-icon {
        display:grid; place-items:center; width:42px; height:42px;
        flex-shrink:0; border-radius:12px; background:#ed263b1c; font-size:22px;
      }
      .profile-achievement small { display:block; margin-top:3px; color:#a6a6b8; }
      .profile-bio { white-space:pre-wrap; overflow-wrap:anywhere; }
      @media(max-width:480px) {
        .profile-hero { padding:19px; gap:14px; }
        .profile-avatar { flex-basis:64px; width:64px; height:64px; font-size:23px; border-radius:18px; }
        .profile-stat { padding:13px; }
      }
    </style>
    <div class="profile-wrap">
      <section class="profile-hero">
        <div class="profile-avatar">""" + initials + """</div>
        <div style="min-width:0;">
          <h2 class="profile-name">""" + name + """</h2>
          <span class="profile-role">""" + role + """</span>
          <p class="profile-muted" style="margin:10px 0 0;">Профиль участника BELGOROD RP</p>
        </div>
      </section>

      <div class="profile-stats">
        <div class="profile-stat">
          <div class="profile-stat-number">📝 """ + str(topics_count) + """</div>
          <div class="profile-stat-label">Создано тем</div>
        </div>
        <div class="profile-stat">
          <div class="profile-stat-number">💬 """ + str(posts_count) + """</div>
          <div class="profile-stat-label">Ответов на форуме</div>
        </div>
      </div>

      <section class="card">
        <h2>👤 Об игроке</h2>
        <div class="profile-bio">""" + bio + """</div>
      </section>

      <section class="card">
        <h2>🏅 Достижения</h2>
        <div class="profile-achievements">""" + achievements_html + """</div>
      </section>
    """

    if is_owner:
        content += """
      <section class="card">
        <h2>✏️ Редактировать описание</h2>
        <form method="post" action="/profile/edit">
          <textarea name="bio" maxlength="500"
            placeholder="Расскажи о себе (до 500 символов)">""" + html.escape(u["bio"] or "") + """</textarea>
          <small>Расскажи другим игрокам немного о себе.</small>
          <button type="submit">💾 Сохранить описание</button>
        </form>
      </section>
        """

    content += "</div>"
    return page(content)


@app.route("/profile/edit", methods=["POST"])
def edit_profile():
    if not session.get("uid"):
        return redirect("/login")
    bio = request.form.get("bio", "").strip()[:500]
    with connect() as c:
        c.execute("UPDATE users SET bio=? WHERE id=?",
                  (bio, session["uid"]))
        u = c.execute("SELECT username FROM users WHERE id=?",
                      (session["uid"],)).fetchone()
    return redirect("/profile/" + u["username"])




@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("uid"):
        return redirect("/login")

    allowed_roles = ("Игрок", "Модератор", "Администратор")
    message = ""

    with connect() as c:
        me = c.execute(
            "SELECT id, username, role FROM users WHERE id=?",
            (session["uid"],)
        ).fetchone()

        if not me or me["role"] != "Администратор":
            return page(
                "<div class='card'><h2>Доступ запрещён</h2>"
                "<p>Панель доступна только администратору.</p></div>"
            ), 403

        if request.method == "POST":
            user_id = request.form.get("user_id", type=int)
            new_role = request.form.get("role", "")

            target = c.execute(
                "SELECT id, username, role FROM users WHERE id=?",
                (user_id,)
            ).fetchone() if user_id else None

            if not target:
                message = "Игрок не найден."
            elif new_role not in allowed_roles:
                message = "Недопустимая роль."
            elif target["id"] == me["id"] and new_role != me["role"]:
                message = "Нельзя изменить собственную роль."
            elif target["role"] == new_role:
                message = "У игрока уже установлена эта роль."
            else:
                admins = c.execute(
                    "SELECT COUNT(*) FROM users WHERE role='Администратор'"
                ).fetchone()[0]

                if target["role"] == "Администратор" and new_role != "Администратор" and admins <= 1:
                    message = "Нельзя снять роль у последнего администратора."
                else:
                    c.execute(
                        "UPDATE users SET role=? WHERE id=?",
                        (new_role, user_id)
                    )
                    c.execute(
                        """INSERT INTO moderation_log(moderator, action, details)
                           VALUES(?,?,?)""",
                        (
                            me["username"],
                            "Изменение роли",
                            target["username"] + ": " + target["role"] + " → " + new_role
                        )
                    )
                    message = "Роль игрока " + html.escape(target["username"]) + " изменена."

        users = c.execute(
            "SELECT id, username, role, bio FROM users ORDER BY id"
        ).fetchall()

        topics_count = c.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
        posts_count = c.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        admins_count = c.execute(
            "SELECT COUNT(*) FROM users WHERE role='Администратор'"
        ).fetchone()[0]
        moderators_count = c.execute(
            "SELECT COUNT(*) FROM users WHERE role='Модератор'"
        ).fetchone()[0]

    content = """
    <div class="card">
      <h2>🛡️ Центр управления BELGOROD RP</h2>
      <p>Управление игроками, ролями и безопасностью форума.</p>
      <p><a href="/admin/log">📋 Открыть журнал модерации →</a></p>
    </div>
    <div class="card">
      <h3>📊 Сводка форума</h3>
      <div style="display:flex;flex-wrap:wrap;gap:10px">
        <div class="card" style="flex:1;min-width:110px;margin:0">
          <b>Игроки</b><h2>""" + str(len(users)) + """</h2>
        </div>
        <div class="card" style="flex:1;min-width:110px;margin:0">
          <b>Темы</b><h2>""" + str(topics_count) + """</h2>
        </div>
        <div class="card" style="flex:1;min-width:110px;margin:0">
          <b>Ответы</b><h2>""" + str(posts_count) + """</h2>
        </div>
        <div class="card" style="flex:1;min-width:110px;margin:0">
          <b>Администраторы</b><h2>""" + str(admins_count) + """</h2>
        </div>
        <div class="card" style="flex:1;min-width:110px;margin:0">
          <b>Модераторы</b><h2>""" + str(moderators_count) + """</h2>
        </div>
      </div>
    </div>
    <div class="card">
      <h3>👥 Игроки и управление ролями</h3>
      <p>Выбери роль и сохрани изменения. Собственную роль изменить нельзя.</p>
    </div>
    """

    if message:
        content += "<div class='card'><b>" + message + "</b></div>"

    for u in users:
        uid = int(u["id"])
        uname = html.escape(u["username"])
        role = u["role"] or "Игрок"
        safe_role = html.escape(role)
        bio = html.escape(u["bio"] or "Игрок пока не добавил описание.")
        initial = html.escape((u["username"] or "?")[:1].upper())

        role_color = {
            "Администратор": "#c62828",
            "Модератор": "#1976d2",
            "Игрок": "#7b1fa2"
        }.get(role, "#555")

        options = ""
        for r in allowed_roles:
            selected = " selected" if r == role else ""
            options += (
                "<option value='" + r + "'" + selected + ">"
                + r + "</option>"
            )

        is_self = uid == int(me["id"])
        form = (
            "<p style='color:#aaa'>Это ваш аккаунт. Смена собственной роли запрещена.</p>"
            if is_self else
            "<form method='post' style='display:flex;flex-wrap:wrap;gap:8px;align-items:center'>"
            "<input type='hidden' name='user_id' value='" + str(uid) + "'>"
            "<select name='role' aria-label='Роль игрока'>" + options + "</select>"
            "<button type='submit'>Сохранить роль</button></form>"
        )

        content += (
            "<div class='card' style='border-left:4px solid " + role_color + "'>"
            "<div style='display:flex;gap:12px;align-items:center'>"
            "<div style='width:44px;height:44px;min-width:44px;border-radius:50%;"
            "background:" + role_color + ";display:flex;align-items:center;"
            "justify-content:center;font-size:20px;font-weight:bold;color:white'>"
            + initial + "</div><div><b>" + uname + "</b><br>"
            "<span style='display:inline-block;margin-top:5px;padding:4px 9px;"
            "border-radius:12px;background:" + role_color + ";color:white;font-size:12px'>"
            + safe_role + "</span></div></div>"
            "<p style='color:#aaa'>" + bio + "</p>"
            "<p><a href='/profile/" + uname + "'>Открыть профиль →</a></p>"
            + form + "</div>"
        )

    return page(content)


def can_moderate():
    if not session.get("uid"):
        return False
    with connect() as c:
        u = c.execute(
            "SELECT role FROM users WHERE id=?",
            (session["uid"],)
        ).fetchone()
    return bool(u and u["role"] in ("Администратор", "Модератор"))



def init_moderation_log():
    with connect() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS moderation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


init_moderation_log()


@app.route("/moderation/delete-topic/<int:tid>", methods=["POST"])
def moderation_delete_topic(tid):
    if not can_moderate():
        return page("<div class='card'><h2>Доступ запрещён</h2></div>"), 403

    with connect() as c:
        t = c.execute(
            "SELECT title FROM topics WHERE id=?", (tid,)
        ).fetchone()
        if not t:
            return redirect("/")
        actor = c.execute(
            "SELECT username FROM users WHERE id=?", (session["uid"],)
        ).fetchone()["username"]
        c.execute(
            "INSERT INTO moderation_log(moderator, action, details) VALUES(?,?,?)",
            (actor, "Удаление темы", t["title"])
        )
        c.execute("DELETE FROM posts WHERE topic_id=?", (tid,))
        c.execute("DELETE FROM topics WHERE id=?", (tid,))

    return redirect("/")


@app.route("/moderation/delete-post/<int:pid>", methods=["POST"])
def moderation_delete_post(pid):
    if not can_moderate():
        return page("<div class='card'><h2>Доступ запрещён</h2></div>"), 403

    with connect() as c:
        post = c.execute(
            "SELECT topic_id FROM posts WHERE id=?", (pid,)
        ).fetchone()
        if not post:
            return redirect("/")
        tid = post["topic_id"]
        actor = c.execute(
            "SELECT username FROM users WHERE id=?", (session["uid"],)
        ).fetchone()["username"]
        c.execute(
            "INSERT INTO moderation_log(moderator, action, details) VALUES(?,?,?)",
            (actor, "Удаление ответа", "ID ответа: " + str(pid))
        )
        c.execute("DELETE FROM posts WHERE id=?", (pid,))

    return redirect("/topic/" + str(tid))




@app.route("/admin/log")
def admin_log():
    if not session.get("uid"):
        return redirect("/login")

    with connect() as c:
        me = c.execute(
            "SELECT role FROM users WHERE id=?",
            (session["uid"],)
        ).fetchone()

        if not me or me["role"] != "Администратор":
            return page(
                "<div class='card'><h2>Доступ запрещён</h2>"
                "<p>Журнал доступен только администратору.</p></div>"
            ), 403

        rows = c.execute(
            """SELECT moderator, action, details, created
               FROM moderation_log ORDER BY id DESC LIMIT 100"""
        ).fetchall()

        total = c.execute(
            "SELECT COUNT(*) FROM moderation_log"
        ).fetchone()[0]

    content = (
        "<div class='card'><h2>📋 Журнал модерации</h2>"
        "<p>Последние 100 записей. Всего записей: "
        + str(total) + ".</p><p><a href='/admin'>← Вернуться в админ-панель</a></p></div>"
    )

    if not rows:
        content += "<div class='card'>Пока действий нет.</div>"

    for r in rows:
        moderator = html.escape(r["moderator"] or "Неизвестно")
        action = html.escape(r["action"] or "Действие")
        details = html.escape(r["details"] or "")
        created = html.escape(r["created"] or "")
        content += (
            "<div class='card' style='border-left:4px solid #a51d2d'>"
            "<b>" + action + "</b>"
            "<p style='margin-bottom:6px'>" + details + "</p>"
            "<small>👮 " + moderator + " · 🕒 " + created + "</small></div>"
        )

    return page(content)


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        if len(name) < 3 or len(name) > 24 or len(pw) < 8:
            msg = "Ник: 3–24 символа, пароль: минимум 8 символов."
        else:
            try:
                with connect() as c:
                    c.execute("INSERT INTO users(username,password) VALUES(?,?)",
                              (name, generate_password_hash(pw)))
                return redirect("/login")
            except sqlite3.IntegrityError:
                msg = "Этот ник уже занят."
    form = '<div class="card"><h2>Регистрация</h2><form method="post"><input name="username" placeholder="Никнейм" required minlength="3" maxlength="24"><input type="password" name="password" placeholder="Пароль" required minlength="8"><button>Зарегистрироваться</button></form></div>'
    return page(form, msg)


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        with connect() as c:
            u = c.execute("SELECT * FROM users WHERE username=?",
                          (request.form.get("username", "").strip(),)).fetchone()
        if u and check_password_hash(u["password"], request.form.get("password", "")):
            session.clear()
            session["uid"] = u["id"]
            session["username"] = u["username"]
            return redirect("/")
        msg = "Неверный ник или пароль."
    form = '<div class="card"><h2>Вход</h2><form method="post"><input name="username" placeholder="Никнейм" required><input type="password" name="password" placeholder="Пароль" required><button>Войти</button></form></div>'
    return page(form, msg)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/new", methods=["GET", "POST"])
def new():
    if not session.get("uid"):
        return redirect("/login")
    msg = ""
    sections = ["Новости сервера", "Государственные организации",
                "Жалобы на игроков", "Обсуждения", "Вопросы и помощь"]
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        section = request.form.get("section", "Обсуждения")
        if section not in sections or not 3 <= len(title) <= 100 or not body or len(body) > 10000:
            msg = "Проверь заголовок и текст темы."
        else:
            with connect() as c:
                c.execute("INSERT INTO topics(user_id,section,title,body) VALUES(?,?,?,?)",
                          (session["uid"], section, title, body))
            return redirect("/")
    options = "".join("<option>" + s + "</option>" for s in sections)
    form = '<div class="card"><h2>Создать тему</h2><form method="post"><select name="section">' + options + '</select><input name="title" placeholder="Заголовок" required minlength="3" maxlength="100"><textarea name="body" placeholder="Текст темы" required maxlength="10000"></textarea><button>Опубликовать</button></form></div>'
    return page(form, msg)


@app.route("/section/<path:section>")
def section(section):
    search_text = request.args.get("q", "").strip()[:100]
    sort = request.args.get("sort", "new")
    if sort not in ("new", "old", "active"):
        sort = "new"

    topics = search_topics(search_text, section, sort)
    content = '<h2>📂 ' + html.escape(section) + '</h2>'
    content += """
    <div class="card">
      <form method="get">
        <input name="q" maxlength="100"
          placeholder="Поиск в этом разделе"
          value="""" + html.escape(search_text, quote=True) + """">
        <label>Сортировка</label>
        <select name="sort">
    """

    for value, label in (
        ("new", "Сначала новые"),
        ("old", "Сначала старые"),
        ("active", "Сначала обсуждаемые")
    ):
        selected = " selected" if value == sort else ""
        content += '<option value="' + value + '"' + selected + '>' + label + '</option>'

    content += """
        </select>
        <button type="submit">Найти</button>
        <a href="/section/' + html.escape(section, quote=True) + '">Сбросить</a>
      </form>
    </div>
    """

    if not topics:
        content += '<div class="card"><p>В этом разделе ничего не найдено.</p></div>'
    else:
        for t in topics:
            content += (
                '<div class="card" style="border-left:3px solid #ed263b;">'
                '<a href="/topic/' + str(t["id"]) + '" style="font-size:17px;">'
                + html.escape(t["title"]) + '</a>'
                '<p><small>👤 ' + html.escape(t["username"])
                + ' · 💬 ' + str(t["reply_count"]) + ' ответов</small></p>'
                '</div>'
            )

    content += '<p><a href="/">← На главную</a></p>'
    return page(content)

@app.route("/topic/<int:tid>", methods=["GET", "POST"])
def topic(tid):
    from datetime import datetime

    def show_date(value):
        if not value:
            return "Дата не указана"
        try:
            return datetime.strptime(
                str(value), "%Y-%m-%d %H:%M:%S"
            ).strftime("%d.%m.%Y · %H:%M")
        except (ValueError, TypeError):
            return str(value)

    def role_color(role):
        colors = {
            "Администратор": ("#ff5263", "#401720"),
            "Модератор": ("#62a8ff", "#172b43"),
            "Игрок": ("#b8a0ff", "#29213d")
        }
        return colors.get(role, ("#b8b8c8", "#292933"))

    def avatar(name, color):
        letter = html.escape((name or "?")[:1].upper())
        return (
            '<div style="flex-shrink:0;width:44px;height:44px;'
            'display:flex;align-items:center;justify-content:center;'
            'border-radius:50%;background:' + color[1] + ';'
            'border:2px solid ' + color[0] + ';color:' + color[0] + ';'
            'font-size:20px;font-weight:900;">' + letter + '</div>'
        )

    def role_badge(role):
        safe_role = html.escape(role or "Игрок")
        color = role_color(role or "Игрок")
        return (
            '<span style="display:inline-block;margin-top:4px;'
            'padding:3px 9px;border-radius:20px;'
            'background:' + color[1] + ';color:' + color[0] + ';'
            'border:1px solid ' + color[0] + '66;'
            'font-size:11px;font-weight:800;">'
            + safe_role + '</span>'
        )

    with connect() as c:
        t = c.execute("""
            SELECT topics.*, users.username, users.role
            FROM topics
            JOIN users ON users.id = topics.user_id
            WHERE topics.id=?
        """, (tid,)).fetchone()

        if not t:
            return page("<div class='card'><h2>Тема не найдена</h2></div>"), 404

        if request.method == "POST":
            if not session.get("uid"):
                return redirect("/login")

            body = request.form.get("body", "").strip()
            if body and len(body) <= 5000:
                c.execute(
                    "INSERT INTO posts(topic_id,user_id,body) VALUES(?,?,?)",
                    (tid, session["uid"], body)
                )
                return redirect("/topic/" + str(tid))

        posts = c.execute("""
            SELECT posts.*, users.username, users.role
            FROM posts
            JOIN users ON users.id = posts.user_id
            WHERE topic_id=?
            ORDER BY posts.id
        """, (tid,)).fetchall()

    moderator = can_moderate()
    title = html.escape(t["title"])
    section = html.escape(t["section"])
    author = html.escape(t["username"])
    role = t["role"] or "Игрок"
    body = html.escape(t["body"])
    author_color = role_color(role)

    content = (
        '<p style="margin:0 0 14px;"><a href="/">⌂ Главная</a>'
        ' <span style="color:#777787;">/</span> '
        '<a href="/section/' + section + '">' + section + '</a></p>'
        '<div class="topic-hero">'
        'background:linear-gradient(145deg,#211720,#15151e);">'
        '<div style="color:#ff6878;font-size:12px;font-weight:800;'
        'letter-spacing:1px;">ОБСУЖДЕНИЕ · ' + section + '</div>'
        '<h2 style="font-size:clamp(23px,5vw,32px);margin:12px 0;">'
        + title + '</h2>'
        '<div class="topic-author">'
        'padding:13px;background:#101017;border-radius:12px;'
        'border:1px solid #30303d;margin:14px 0;">'
        + avatar(t["username"], author_color)
        + '<div style="min-width:0;overflow-wrap:anywhere;">'
        '<b><a href="/profile/' + author + '">' + author + '</a></b><br>'
        + role_badge(role)
        + '<div style="font-size:12px;color:#9999aa;margin-top:5px;">'
        '🕒 ' + html.escape(show_date(t["created"])) + '</div>'
        '</div></div>'
        '<div class="topic-message">'
        'line-height:1.8;">' + body + '</div>'
    )

    if moderator:
        content += (
            '<form method="post" action="/moderation/delete-topic/'
            + str(tid)
            + '" onsubmit="return confirm(\'Удалить тему и все ответы?\')">'
            '<button type="submit">🗑️ Удалить тему</button></form>'
        )

    content += '<h2>💬 Ответы (' + str(len(posts)) + ')</h2>'

    if not posts:
        content += (
            '<div class="card" style="text-align:center;">'
            '<p style="font-size:26px;margin:0;">💭</p>'
            '<p>Пока нет ответов. Начни обсуждение первым!</p></div>'
        )

    for index, post in enumerate(posts, start=1):
        post_author = html.escape(post["username"])
        post_role = post["role"] or "Игрок"
        post_body = html.escape(post["body"])
        post_color = role_color(post_role)

        content += (
            '<div class="topic-reply" style="border-left-color:'
            + post_color[0] + ';">'
            '<div class="topic-reply-head">'
            'gap:12px;margin-bottom:14px;">'
            + avatar(post["username"], post_color)
            + '<div style="min-width:0;flex:1;overflow-wrap:anywhere;">'
            '<a href="/profile/' + post_author
            + '" style="font-weight:800;">' + post_author + '</a><br>'
            + role_badge(post_role)
            + '<div style="font-size:12px;color:#9999aa;margin-top:5px;">'
            '🕒 ' + html.escape(show_date(post["created"])) + '</div>'
            '</div><div style="font-size:12px;color:#858596;">#'
            + str(index) + '</div></div>'
            '<div class="topic-reply-body">'
            'line-height:1.8;">' + post_body + '</div>'
        )

        if moderator:
            content += (
                '<form method="post" action="/moderation/delete-post/'
                + str(post["id"])
                + '" onsubmit="return confirm(\'Удалить этот ответ?\')">'
                '<button type="submit">🗑️ Удалить ответ</button></form>'
            )

        content += '</div>'

    if session.get("uid"):
        content += (
            '<div class="topic-compose">'
            '<h2 style="margin-top:0;">✍️ Написать ответ</h2>'
            '<form method="post">'
            '<textarea name="body" required maxlength="5000" '
            'placeholder="Напиши свой ответ..." '
            'style="min-height:150px;"></textarea>'
            '<small>Максимум 5000 символов.</small>'
            '<button type="submit">Отправить ответ →</button>'
            '</form></div>'
        )
    else:
        content += (
            '<div class="card" style="text-align:center;">'
            '<p>Чтобы участвовать в обсуждении, войди в аккаунт.</p>'
            '<a href="/login">Войти</a> · <a href="/register">Регистрация</a>'
            '</div>'
        )

    return page(content)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
