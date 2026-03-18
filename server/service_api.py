from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import sqlite3 as sq
import uuid
from pydantic import BaseModel
import hashlib
from dotenv import load_dotenv
import os
import random
from PIL import Image, ImageDraw
from contextlib import asynccontextmanager
from balancer import balancer, router as balancer_router
import asyncio
import sys
import tempfile

load_dotenv()

# ── Fragmos handler for Balancer ─────────────────────────────────────────────

_MODULES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../modules/fragmos"))


async def _fragmos_handler(payload: dict) -> dict:
    """
    Balancer handler for fragmos pipeline.
    payload: {code, user_uuid, model_id, token_budget, cfg}
    Returns: {xml_path, tokens, charged_tokens}
    """
    code = payload.get("code", "")
    user_uuid = payload.get("user_uuid", "")
    model_id = payload.get("model_id")
    token_budget = payload.get("token_budget")
    cfg = payload.get("cfg", {})

    if not code.strip():
        raise ValueError("Empty code")
    if not model_id:
        raise ValueError("model_id is required")

    # Prepare file paths
    user_dir = f"files/users/{user_uuid}/fragmos"
    os.makedirs(user_dir, exist_ok=True)

    slug = str(uuid.uuid4())[:8]
    fname = f"Схема_{slug}.xml"
    xml_path = os.path.join(user_dir, fname)

    tmp_dir = tempfile.mkdtemp(prefix="fragmos_")
    code_path = os.path.join(tmp_dir, "code.txt")

    with open(code_path, "w", encoding="utf-8") as f:
        f.write(code)

    def _run():
        if _MODULES_DIR not in sys.path:
            sys.path.insert(0, _MODULES_DIR)
        from pipeline import run as pipeline_run  # type: ignore
        result_path, charged = pipeline_run(
            code_path, xml_path,
            cfg_overrides=cfg,
            model_id=model_id,
            token_budget=token_budget,
        )
        return result_path, charged

    try:
        result_path, charged = await asyncio.to_thread(_run)
    finally:
        try:
            os.remove(code_path)
            os.rmdir(tmp_dir)
        except OSError:
            pass

    return {
        "xml_path": result_path,
        "xml_filename": fname,
        "charged_tokens": charged,
    }


balancer.register_handler("fragmos", _fragmos_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    balancer.start()
    yield
    balancer.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(balancer_router)
DB_PATH = os.getenv("DATABASE_NAME")

# Раздаём файлы из files/ по URL /files/...
os.makedirs("files", exist_ok=True)
app.mount("/files", StaticFiles(directory="files"), name="files")

#SQL
#-------------------------------------------------------
def get_db():
    conn = sq.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sq.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            uuid        TEXT PRIMARY KEY,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            icon TEXT,
            display_name TEXT,
            sub_level TEXT NOT NULL DEFAULT 'free',
            sub_expire_date DATETIME,
            tokens_left INT DEFAULT 0
        )
    """)
    # Добавляем display_name если таблица уже существует без неё
    try:
        conn.execute("ALTER TABLE users ADD COLUMN display_name TEXT")
    except sq.OperationalError:
        pass
    # Добавляем referred_by для отслеживания реферальных регистраций
    try:
        conn.execute("ALTER TABLE users ADD COLUMN referred_by TEXT")
    except sq.OperationalError:
        pass
    conn.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_uuid  TEXT NOT NULL,
            ref_uuid    TEXT UNIQUE NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            referral_count INT DEFAULT 0,
            FOREIGN KEY (owner_uuid) REFERENCES users(uuid)
        )
    """)
    conn.commit()
    conn.close()

init_db()
#------------------------------------------------------

def generate_icon(user_id: str, folder: str):
    """
    Генерирует identicon — 5x5 сетка с симметрией как у GitHub.
    Seed берётся из uuid — каждый раз одна и та же картинка для одного юзера.
    Сохраняет в files/users/{uuid}/icon.png
    """
    rng = random.Random(user_id)  # детерминированный random на основе uuid

    # случайный цвет (не слишком тёмный и не слишком светлый)
    r = rng.randint(50, 200)
    g = rng.randint(50, 200)
    b = rng.randint(50, 200)
    color = (r, g, b)
    bg = (240, 240, 240)

    grid = 5
    cell = 60  # размер одной ячейки в пикселях
    size = grid * cell

    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)

    # генерируем только левую половину (3 колонки), зеркалим на правую
    for row in range(grid):
        for col in range(3):
            if rng.random() > 0.5:
                x = col * cell
                y = row * cell
                draw.rectangle([x, y, x + cell, y + cell], fill=color)
                # зеркало
                mirror_col = grid - 1 - col
                if mirror_col != col:
                    x2 = mirror_col * cell
                    draw.rectangle([x2, y, x2 + cell, y + cell], fill=color)

    icon_path = os.path.join(folder, "icon.png")
    img.save(icon_path)
    return icon_path

#CURL CLASS
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Update(BaseModel):
    item: str
    newitem: str
    olditem: str = ""  # нужен только при смене пароля



#API SETTINGS

@app.get("/")
async def root():
    return {"status": "Koritsu API running"}


@app.post("/register")
def register(data: RegisterRequest):
    user_id = str(uuid.uuid4())

    password_hash = hashlib.sha256((data.password + user_id).encode()).hexdigest()

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (uuid, username, password) VALUES (?, ?, ?)",
            (user_id, data.username, password_hash)
        )
        try:
            user_folder = f"files/users/{user_id}"
            os.makedirs(f"{user_folder}/fragmos", exist_ok=True)
            os.makedirs(f"{user_folder}/engrafo", exist_ok=True)
            icon_path = generate_icon(user_id, user_folder)
            conn.execute("UPDATE users SET icon = ? WHERE uuid = ?", (icon_path, user_id))
        except Exception as e:
            return {"error": f"Some internal error {e}"}
        conn.commit()
    except sq.IntegrityError:
        return {"error": "Username already taken"}
    finally:
        conn.close()

    return {"success": f"User {data.username} created!"}


@app.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (data.username,)
    ).fetchone()
    conn.close()

    if row is None:
        return {"error": "User not found!"}

    password_hash = hashlib.sha256((data.password + row["uuid"]).encode()).hexdigest()

    if password_hash == row["password"]:
        return {"success": "Auth true", "uuid": row["uuid"]}
    else:
        return {"error": "Username or password is incorrect!"}

@app.get("/user/{uuid}")
def get_user_data(uuid: str):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE uuid = ?", (uuid,)).fetchone()
    conn.close()
    if row is None:
        return {"error": "User not exist"}
    else:
        return {"user_data": {
            "username": row["username"],
            "display_name": row["display_name"],
            "icon": row["icon"],
            "sub_level": row["sub_level"],
            "sub_expire_date": row["sub_expire_date"],
            "tokens_left": row["tokens_left"],
        }}

@app.get("/user/{uuid}/{folder}")
def get_user_folder_files(uuid: str, folder: str):
    if folder not in ("fragmos", "engrafo"):
        return {"error": "Unable to get folder"}
    if folder == "engrafo":
        return {"error": "Service not available"}

    folder_path = f"files/users/{uuid}/fragmos"
    if not os.path.exists(folder_path):
        return {"error": "User folder not found"}
    files = [f for f in os.listdir(folder_path) if f.endswith(".xml")]
    return {"files": files}


@app.post("/user/{uuid}/avatar")
async def upload_avatar(uuid: str, file: UploadFile = File(...)):
    """Загрузка аватарки пользователя. Принимает только PNG."""
    conn = get_db()
    row = conn.execute("SELECT uuid FROM users WHERE uuid = ?", (uuid,)).fetchone()
    conn.close()
    if row is None:
        return {"error": "User not exist"}

    # Проверяем формат — только PNG
    if file.content_type != "image/png" or not (file.filename or "").lower().endswith(".png"):
        # Делаем вид что всё хорошо, но ничего не сохраняем
        return {"success": "Avatar updated"}

    user_folder = f"files/users/{uuid}"
    os.makedirs(user_folder, exist_ok=True)
    icon_path = os.path.join(user_folder, "icon.png")

    contents = await file.read()
    with open(icon_path, "wb") as f:
        f.write(contents)

    conn = get_db()
    conn.execute("UPDATE users SET icon = ? WHERE uuid = ?", (icon_path, uuid))
    conn.commit()
    conn.close()

    return {"success": "Avatar updated", "icon": icon_path}


@app.patch("/user/{uuid}")
def update_item(uuid: str, data: Update):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE uuid = ?", (uuid,)).fetchone()

    if row is None:
        conn.close()
        return {"error": "User not exist"}

    match data.item:
        case "username":
            taken = conn.execute("SELECT uuid FROM users WHERE username = ?", (data.newitem,)).fetchone()
            if taken is not None:
                conn.close()
                return {"error": "Username already taken"}
            conn.execute("UPDATE users SET username = ? WHERE uuid = ?", (data.newitem, uuid))
            conn.commit()
            conn.close()
            return {"success": f"Username changed to {data.newitem}"}

        case "password":
            # проверяем старый пароль
            old_hash = hashlib.sha256((data.olditem + row["uuid"]).encode()).hexdigest()
            if old_hash != row["password"]:
                conn.close()
                return {"error": "Old password is incorrect"}
            new_hash = hashlib.sha256((data.newitem + row["uuid"]).encode()).hexdigest()
            conn.execute("UPDATE users SET password = ? WHERE uuid = ?", (new_hash, uuid))
            conn.commit()
            conn.close()
            return {"success": "Password changed"}

        case "display_name":
            conn.execute("UPDATE users SET display_name = ? WHERE uuid = ?", (data.newitem, uuid))
            conn.commit()
            conn.close()
            return {"success": f"Display name changed to {data.newitem}"}

        case "icon":
            # newitem = имя файла иконки (файл уже должен быть загружен отдельно)
            icon_path = f"files/users/{uuid}/{data.newitem}"
            if not os.path.exists(icon_path):
                conn.close()
                return {"error": "Icon file not found"}
            conn.execute("UPDATE users SET icon = ? WHERE uuid = ?", (icon_path, uuid))
            conn.commit()
            conn.close()
            return {"success": "Icon updated"}

        case "tokens_left":
            if data.olditem == "minus":
                amount = int(data.newitem)
                new_balance = row["tokens_left"] - amount
                if new_balance < 0:
                    conn.close()
                    return {"error": "Not enough tokens"}
                conn.execute("UPDATE users SET tokens_left = ? WHERE uuid = ?", (new_balance, uuid))
                conn.commit()
                conn.close()
                return {"success": f"Tokens left: {new_balance}"}
            if data.olditem == "plus":
                amount = int(data.newitem)
                new_balance = row["tokens_left"] + amount
                if new_balance < 0:
                    conn.close()
                    return {"error": "Not enough tokens"}
                conn.execute("UPDATE users SET tokens_left = ? WHERE uuid = ?", (new_balance, uuid))
                conn.commit()
                conn.close()
                return {"success": f"Tokens left: {new_balance}"}

        case _:
            conn.close()
            return {"error": f"Unknown field: {data.item}"}


# ── Реферальная программа ─────────────────────────────────────────────────────

@app.post("/user/{uuid}/referral")
def create_referral(uuid: str):
    """Создать реферальный код для пользователя (если ещё нет)."""
    conn = get_db()
    user = conn.execute("SELECT uuid FROM users WHERE uuid = ?", (uuid,)).fetchone()
    if user is None:
        conn.close()
        return {"error": "User not exist"}

    existing = conn.execute("SELECT ref_uuid FROM referrals WHERE owner_uuid = ?", (uuid,)).fetchone()
    if existing:
        conn.close()
        return {"ref_uuid": existing["ref_uuid"]}

    import uuid as uuid_mod
    ref_uuid = str(uuid_mod.uuid4())
    conn.execute(
        "INSERT INTO referrals (owner_uuid, ref_uuid) VALUES (?, ?)",
        (uuid, ref_uuid)
    )
    conn.commit()
    conn.close()
    return {"ref_uuid": ref_uuid}


@app.get("/user/{uuid}/referral")
def get_referral(uuid: str):
    """Получить реферальные данные пользователя."""
    conn = get_db()
    user = conn.execute("SELECT uuid FROM users WHERE uuid = ?", (uuid,)).fetchone()
    if user is None:
        conn.close()
        return {"error": "User not exist"}

    row = conn.execute("SELECT * FROM referrals WHERE owner_uuid = ?", (uuid,)).fetchone()
    conn.close()

    if row is None:
        return {"referral": None}

    return {"referral": {
        "ref_uuid": row["ref_uuid"],
        "referral_count": row["referral_count"],
        "created_at": row["created_at"],
    }}


@app.post("/register/ref/{ref_uuid}")
def register_with_referral(ref_uuid: str, data: RegisterRequest):
    """Регистрация по реферальной ссылке — увеличивает счётчик рефералов."""
    conn = get_db()

    ref_row = conn.execute("SELECT * FROM referrals WHERE ref_uuid = ?", (ref_uuid,)).fetchone()
    if ref_row is None:
        conn.close()
        return {"error": "Referral code not found"}

    user_id = str(uuid.uuid4())
    password_hash = hashlib.sha256((data.password + user_id).encode()).hexdigest()

    try:
        conn.execute(
            "INSERT INTO users (uuid, username, password, referred_by) VALUES (?, ?, ?, ?)",
            (user_id, data.username, password_hash, ref_uuid)
        )
        try:
            user_folder = f"files/users/{user_id}"
            os.makedirs(f"{user_folder}/fragmos", exist_ok=True)
            os.makedirs(f"{user_folder}/engrafo", exist_ok=True)
            icon_path = generate_icon(user_id, user_folder)
            conn.execute("UPDATE users SET icon = ? WHERE uuid = ?", (icon_path, user_id))
        except Exception as e:
            return {"error": f"Some internal error {e}"}

        conn.execute(
            "UPDATE referrals SET referral_count = referral_count + 1 WHERE ref_uuid = ?",
            (ref_uuid,)
        )
        conn.commit()
    except sq.IntegrityError:
        conn.close()
        return {"error": "Username already taken"}
    finally:
        conn.close()

    return {"success": f"User {data.username} created!"}


@app.get("/user/{uuid}/referral/details")
def get_referral_details(uuid: str):
    """Получить список пользователей, зарегистрированных по реферальной ссылке."""
    conn = get_db()
    user = conn.execute("SELECT uuid FROM users WHERE uuid = ?", (uuid,)).fetchone()
    if user is None:
        conn.close()
        return {"error": "User not exist"}

    ref_row = conn.execute("SELECT ref_uuid FROM referrals WHERE owner_uuid = ?", (uuid,)).fetchone()
    if ref_row is None:
        conn.close()
        return {"referrals": []}

    referred = conn.execute(
        "SELECT username, created_at FROM users WHERE referred_by = ? ORDER BY created_at DESC",
        (ref_row["ref_uuid"],)
    ).fetchall()
    conn.close()

    result = []
    for r in referred:
        date_str = (r["created_at"] or "")[:10]
        result.append({
            "name": r["username"],
            "earnings": "0 бонусов",
            "date": date_str,
            "status": "active",
        })

    return {"referrals": result}


@app.get("/ref/{ref_uuid}/validate")
def validate_referral(ref_uuid: str):
    """Проверить, существует ли реферальный код."""
    conn = get_db()
    row = conn.execute("SELECT ref_uuid FROM referrals WHERE ref_uuid = ?", (ref_uuid,)).fetchone()
    conn.close()
    if row is None:
        return {"valid": False}
    return {"valid": True}
