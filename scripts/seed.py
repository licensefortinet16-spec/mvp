import asyncio
from app.core.db import AsyncSessionLocal
from app.models.domain import Tenant
from app.core.config import settings
from app.core.logging import setup_logging, logger

async def seed_tenant():
    setup_logging()
    logger.info("seed.starting")

    async with AsyncSessionLocal() as session:
        # Verifica se já existe
        from sqlalchemy import select
        result = await session.execute(
            select(Tenant).where(
                Tenant.waba_id == settings.meta_waba_id,
                Tenant.phone_number_id == settings.meta_phone_number_id
            )
        )
        existing_tenant = result.scalar_one_or_none()

        if existing_tenant:
            logger.info("seed.tenant_exists", tenant_id=existing_tenant.id)
            return

        new_tenant = Tenant(
            waba_id=settings.meta_waba_id,
            phone_number_id=settings.meta_phone_number_id,
            name="Tenant de Teste MVP"
        )
        session.add(new_tenant)
        await session.commit()
        logger.info("seed.tenant_created", waba_id=settings.meta_waba_id)

if __name__ == "__main__":
    asyncio.run(seed_tenant())
