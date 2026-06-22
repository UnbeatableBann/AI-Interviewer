import asyncio
import glob
import importlib
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.config import settings
from src.core.database import Base, engine


async def init_db() -> None:
    print("Importing all entity models dynamically...")
    # Dynamically find and import all models under src/contexts
    model_files = glob.glob("src/contexts/**/models.py", recursive=True)
    for model_file in model_files:
        # Convert path format to python module name
        module_name = (
            model_file.replace("/", ".")
            .replace("\\", ".")
            .replace(".py", "")
        )
        print(f"Importing: {module_name}")
        importlib.import_module(module_name)

    print(f"Target Database URL: {settings.DATABASE_URL}")
    async with engine.begin() as conn:
        print("Creating all registered tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema successfully initialized!")


if __name__ == "__main__":
    asyncio.run(init_db())
