from aiohttp import web

async def handle_webhook(request):
    data = await request.json()  # Receive JSON data
    print(data)  # Process the incoming data
    return web.Response(text="Webhook received")

app = web.Application()
app.router.add_post('/webhook', handle_webhook)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)

