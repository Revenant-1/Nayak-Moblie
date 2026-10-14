import os
import sys
import asyncio
from pathlib import Path

# ---------------------------------------------------------------------------
# Load .env
# ---------------------------------------------------------------------------

try:
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] python-dotenv is not installed.")
    print("Run: uv add python-dotenv")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if not ENV_FILE.exists():
    print(f"[ERROR] .env not found at: {ENV_FILE}")
    sys.exit(1)

load_dotenv(ENV_FILE)

print()
print("=" * 60)
print("NAYAK BACKEND CREDENTIAL CHECK")
print("=" * 60)
print()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

results = []


def result(name, passed, message=""):
    results.append((name, passed))

    if passed:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")
        if message:
            # Prevent accidental credential leakage
            safe_message = str(message)
            for key in [
                "GEMINI_API_KEY",
                "GROQ_API_KEY",
                "QDRANT_API_KEY",
                "DATABASE_URL",
                "DIRECT_URL",
                "AUTH_JWT_SECRET",
            ]:
                value = os.getenv(key)
                if value:
                    safe_message = safe_message.replace(value, "***REDACTED***")

            print(f"       {safe_message}")

    print()


def required_env(name):
    value = os.getenv(name)

    if not value:
        result(name, False, "Environment variable is missing or empty.")
        return None

    return value


# ---------------------------------------------------------------------------
# 1. Environment variables
# ---------------------------------------------------------------------------

print("--- Environment configuration ---")
print()

env_names = [
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "AUTH_JWT_SECRET",
    "DATABASE_URL",
    "DIRECT_URL",
    "QDRANT_URL",
    "QDRANT_API_KEY",
]

for name in env_names:
    value = os.getenv(name)

    if value:
        result(f"{name} configured", True)
    else:
        result(f"{name} configured", False, "Missing or empty")


# ---------------------------------------------------------------------------
# 2. JWT secret
# ---------------------------------------------------------------------------

print("--- JWT ---")
print()

try:
    import jwt

    secret = os.getenv("AUTH_JWT_SECRET")

    if not secret:
        raise RuntimeError("AUTH_JWT_SECRET is missing")

    payload = {
        "test": True,
        "purpose": "credential_check",
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    decoded = jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
    )

    if decoded.get("test") is True:
        result("AUTH_JWT_SECRET", True)
    else:
        result("AUTH_JWT_SECRET", False, "Token decoded but payload was incorrect.")

except Exception as exc:
    result("AUTH_JWT_SECRET", False, exc)


# ---------------------------------------------------------------------------
# 3. PostgreSQL DATABASE_URL
# ---------------------------------------------------------------------------

print("--- PostgreSQL / Supabase ---")
print()

try:
    import psycopg

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing")

    # psycopg can connect using the SQLAlchemy URL after removing the
    # SQLAlchemy-specific "+psycopg" portion.
    psycopg_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    with psycopg.connect(
        psycopg_url,
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            value = cursor.fetchone()[0]

    if value == 1:
        result("DATABASE_URL", True)
    else:
        result("DATABASE_URL", False, "Database responded unexpectedly.")

except Exception as exc:
    result("DATABASE_URL", False, exc)


# ---------------------------------------------------------------------------
# 4. PostgreSQL DIRECT_URL
# ---------------------------------------------------------------------------

try:
    import psycopg

    direct_url = os.getenv("DIRECT_URL")

    if not direct_url:
        raise RuntimeError("DIRECT_URL is missing")

    psycopg_url = direct_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    with psycopg.connect(
        psycopg_url,
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            value = cursor.fetchone()[0]

    if value == 1:
        result("DIRECT_URL", True)
    else:
        result("DIRECT_URL", False, "Database responded unexpectedly.")

except Exception as exc:
    result("DIRECT_URL", False, exc)


# ---------------------------------------------------------------------------
# 5. Qdrant
# ---------------------------------------------------------------------------

print("--- Qdrant ---")
print()

try:
    from qdrant_client import QdrantClient

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url:
        raise RuntimeError("QDRANT_URL is missing")

    if not qdrant_key:
        raise RuntimeError("QDRANT_API_KEY is missing")

    client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_key,
        timeout=10,
    )

    # This performs a real authenticated request.
    collections = client.get_collections()

    result(
        "QDRANT_URL + QDRANT_API_KEY",
        True,
        f"{len(collections.collections)} collection(s) available.",
    )

except Exception as exc:
    result(
        "QDRANT_URL + QDRANT_API_KEY",
        False,
        exc,
    )


# ---------------------------------------------------------------------------
# 6. Gemini
# ---------------------------------------------------------------------------

print("--- Gemini ---")
print()

try:
    from google import genai

    gemini_key = os.getenv("GEMINI_API_KEY")

    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=gemini_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly: NAYAK_GEMINI_OK",
    )

    text = (response.text or "").strip()

    if text:
        result(
            "GEMINI_API_KEY",
            True,
            f"API responded: {text[:80]}",
        )
    else:
        result(
            "GEMINI_API_KEY",
            False,
            "API request succeeded but returned an empty response.",
        )

except Exception as exc:
    result("GEMINI_API_KEY", False, exc)


# ---------------------------------------------------------------------------
# 7. Groq
# ---------------------------------------------------------------------------

print("--- Groq ---")
print()

try:
    from groq import Groq

    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        raise RuntimeError("GROQ_API_KEY is missing")

    client = Groq(api_key=groq_key)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: NAYAK_GROQ_OK",
            }
        ],
        max_tokens=20,
    )

    text = response.choices[0].message.content.strip()

    if text:
        result(
            "GROQ_API_KEY",
            True,
            f"API responded: {text[:80]}",
        )
    else:
        result(
            "GROQ_API_KEY",
            False,
            "API request succeeded but returned an empty response.",
        )

except Exception as exc:
    result("GROQ_API_KEY", False, exc)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print()

passed = sum(1 for _, ok in results if ok)
failed = len(results) - passed

print(f"Passed: {passed}")
print(f"Failed: {failed}")
print()

if failed == 0:
    print("All credential/service checks passed.")
else:
    print("Some checks failed.")
    print("Fix the FAILED items before testing the mobile app.")

print()
print("=" * 60)