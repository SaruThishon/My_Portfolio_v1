import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://portfolio_user:portfolio_pass@localhost:5435/portfolio_db')
    print('DB Connected OK:', await conn.fetchval('SELECT version()'))
    await conn.close()

asyncio.run(test())
