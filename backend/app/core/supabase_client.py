import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "").strip()


def _require(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"Falta {name} en backend/.env")
    return value


def get_auth_client() -> Client:
    """Cliente para operaciones de autenticación de usuario."""
    return create_client(
        _require(SUPABASE_URL, "SUPABASE_URL"),
        _require(SUPABASE_PUBLISHABLE_KEY, "SUPABASE_PUBLISHABLE_KEY"),
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )


def get_admin_client() -> Client:
    """Cliente privilegiado. Solo debe usarse en el backend."""
    return create_client(
        _require(SUPABASE_URL, "SUPABASE_URL"),
        _require(SUPABASE_SECRET_KEY, "SUPABASE_SECRET_KEY"),
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )
