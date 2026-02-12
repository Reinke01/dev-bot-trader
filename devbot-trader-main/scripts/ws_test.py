import asyncio
import websockets

async def main():
    uri = 'ws://localhost:8000/api/v1/ws/logs/9439b2ff-b44a-4961-83ad-ba32fa1fc7a7'
    try:
        async with websockets.connect(uri) as ws:
            print(f'Conectado a {uri}')
            # Listen for messages for ~15 seconds
            async def reader():
                try:
                    async for msg in ws:
                        print('MSG:', msg)
                except Exception as e:
                    print('Reader error:', e)

            task = asyncio.create_task(reader())
            await asyncio.sleep(15)
            task.cancel()
    except Exception as e:
        print('Erro ao conectar:', e)

if __name__ == '__main__':
    asyncio.run(main())
