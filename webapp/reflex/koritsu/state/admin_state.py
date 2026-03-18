"""State for admin user management page."""

import reflex as rx
import httpx

API = "http://localhost:8001"


class AdminState(rx.State):
    # ── Search ───────────────────────────────────────────────────────────
    search_uuid: str = ""
    search_error: str = ""

    # ── Loaded user data ─────────────────────────────────────────────────
    user_loaded: bool = False
    user_uuid: str = ""
    username: str = ""
    display_name: str = ""
    sub_level: str = ""
    sub_expire_date: str = ""
    tokens_left: int = 0
    icon: str = ""

    # ── Edit fields ──────────────────────────────────────────────────────
    edit_username: str = ""
    edit_display_name: str = ""
    edit_tokens: str = ""
    edit_sub_level: str = ""

    # ── Feedback ─────────────────────────────────────────────────────────
    save_success: str = ""
    save_error: str = ""

    async def search_user(self):
        self.search_error = ""
        self.user_loaded = False
        self.save_success = ""
        self.save_error = ""

        if not self.search_uuid.strip():
            self.search_error = "Enter a UUID"
            return

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{API}/user/{self.search_uuid.strip()}",
                    timeout=5,
                )
                data = resp.json()
        except Exception as e:
            self.search_error = f"Connection error: {e}"
            return

        if "error" in data:
            self.search_error = data["error"]
            return

        ud = data.get("user_data", {})
        self.user_uuid = self.search_uuid.strip()
        self.username = ud.get("username", "")
        self.display_name = ud.get("display_name", "") or ""
        self.sub_level = ud.get("sub_level", "free")
        self.sub_expire_date = ud.get("sub_expire_date", "") or ""
        self.tokens_left = ud.get("tokens_left", 0) or 0
        self.icon = ud.get("icon", "") or ""

        # Pre-fill edit fields
        self.edit_username = self.username
        self.edit_display_name = self.display_name
        self.edit_tokens = str(self.tokens_left)
        self.edit_sub_level = self.sub_level

        self.user_loaded = True

    async def save_username(self):
        self.save_error = ""
        self.save_success = ""
        if self.edit_username == self.username:
            return
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(
                    f"{API}/user/{self.user_uuid}",
                    json={"item": "username", "newitem": self.edit_username},
                    timeout=5,
                )
                data = resp.json()
            if "error" in data:
                self.save_error = data["error"]
            else:
                self.username = self.edit_username
                self.save_success = "Username updated"
        except Exception as e:
            self.save_error = str(e)

    async def save_display_name(self):
        self.save_error = ""
        self.save_success = ""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(
                    f"{API}/user/{self.user_uuid}",
                    json={"item": "display_name", "newitem": self.edit_display_name},
                    timeout=5,
                )
                data = resp.json()
            if "error" in data:
                self.save_error = data["error"]
            else:
                self.display_name = self.edit_display_name
                self.save_success = "Display name updated"
        except Exception as e:
            self.save_error = str(e)

    async def save_tokens(self):
        self.save_error = ""
        self.save_success = ""
        try:
            new_tokens = int(self.edit_tokens)
        except ValueError:
            self.save_error = "Tokens must be a number"
            return

        diff = new_tokens - self.tokens_left
        if diff == 0:
            return

        op = "plus" if diff > 0 else "minus"
        amount = abs(diff)

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.patch(
                    f"{API}/user/{self.user_uuid}",
                    json={"item": "tokens_left", "olditem": op, "newitem": str(amount)},
                    timeout=5,
                )
                data = resp.json()
            if "error" in data:
                self.save_error = data["error"]
            else:
                self.tokens_left = new_tokens
                self.save_success = f"Tokens set to {new_tokens}"
        except Exception as e:
            self.save_error = str(e)

    def set_search_uuid(self, v: str):
        self.search_uuid = v

    def set_edit_username(self, v: str):
        self.edit_username = v

    def set_edit_display_name(self, v: str):
        self.edit_display_name = v

    def set_edit_tokens(self, v: str):
        self.edit_tokens = v

    def set_edit_sub_level(self, v: str):
        self.edit_sub_level = v
