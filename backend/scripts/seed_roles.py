import asyncio
import sys

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.role import Role

DEFAULT_ROLES = [
    {"name": "Owner", "description": "Full access to the organization"},
    {"name": "Admin", "description": "Can manage users and settings"},
    {"name": "Member", "description": "Standard user access"},
]

async def seed_roles() -> None:
    async with AsyncSessionLocal() as session:
        for role_data in DEFAULT_ROLES:
            stmt = select(Role).where(Role.name == role_data["name"])
            result = await session.execute(stmt)
            role = result.scalar_one_or_none()
            
            if not role:
                print(f"Creating role: {role_data['name']}")
                new_role = Role(name=role_data["name"], description=role_data["description"])
                session.add(new_role)
            else:
                print(f"Role already exists: {role_data['name']}")
        
        await session.commit()
        print("Roles seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_roles())
