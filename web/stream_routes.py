import math
import secrets
import mimetypes
import logging
from urllib.parse import quote
from aiohttp import web
from info import BIN_CHANNEL
from utils import temp
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 🏠 ROOT ROUTE (PREMIUM FAST FINDER UI)
# ─────────────────────────────────────────────
@routes.get("/", allow_head=True)
async def root_route_handler(request):
    bot_username = getattr(temp, 'U_NAME', 'AutoFilterBot')
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fast Finder | Streaming Hub</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #00f2fe;
                --secondary: #4facfe;
                --dark-bg: #0b0c10;
                --glass-bg: rgba(17, 25, 40, 0.75);
                --glass-border: rgba(255, 255, 255, 0.125);
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }}
            
            body {{
                background-color: var(--dark-bg);
                color: #ffffff;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                position: relative;
                overflow: hidden;
            }}

            /* Animated Background Blob */
            .bg-blob {{
                position: absolute;
                width: 600px;
                height: 600px;
                background: linear-gradient(180deg, rgba(79, 172, 254, 0.3) 0%, rgba(0, 242, 254, 0.1) 100%);
                filter: blur(100px);
                border-radius: 50%;
                animation: float 10s infinite ease-in-out alternate;
                z-index: 0;
            }}
            @keyframes float {{
                0% {{ transform: translate(-10%, -10%) scale(1); }}
                100% {{ transform: translate(10%, 10%) scale(1.1); }}
            }}

            /* Admin Button */
            .admin-login-btn {{
                position: absolute;
                top: 25px;
                right: 30px;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                color: white;
                padding: 10px 20px;
                border-radius: 30px;
                text-decoration: none;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid var(--glass-border);
                transition: all 0.3s ease;
                z-index: 100;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .admin-login-btn:hover {{
                background: linear-gradient(90deg, var(--secondary), var(--primary));
                box-shadow: 0 0 20px rgba(0, 242, 254, 0.4);
                transform: translateY(-2px);
                border-color: transparent;
            }}

            /* Glassmorphism Container */
            .glass-panel {{
                background: var(--glass-bg);
                backdrop-filter: blur(16px) saturate(180%);
                -webkit-backdrop-filter: blur(16px) saturate(180%);
                border: 1px solid var(--glass-border);
                padding: 50px 40px;
                border-radius: 24px;
                box-shadow: 0 30px 60px rgba(0,0,0,0.4);
                width: 90%;
                max-width: 500px;
                text-align: center;
                z-index: 10;
                position: relative;
            }}

            .icon-wrapper {{
                font-size: 50px;
                background: -webkit-linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 15px;
            }}

            h1 {{
                font-size: 2.2rem;
                font-weight: 700;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }}
            
            p.subtitle {{
                color: #a0aab5;
                font-size: 15px;
                margin-bottom: 35px;
                font-weight: 300;
            }}

            .search-wrapper {{
                position: relative;
                margin-bottom: 25px;
            }}
            .search-wrapper i {{
                position: absolute;
                left: 20px;
                top: 50%;
                transform: translateY(-50%);
                color: #a0aab5;
                font-size: 18px;
            }}
            input[type="text"] {{
                width: 100%;
                padding: 18px 20px 18px 50px;
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: rgba(0, 0, 0, 0.3);
                color: white;
                font-size: 16px;
                outline: none;
                transition: all 0.3s ease;
            }}
            input[type="text"]:focus {{
                border-color: var(--primary);
                background: rgba(0, 0, 0, 0.5);
                box-shadow: inset 0 0 0 1px var(--primary), 0 0 15px rgba(0, 242, 254, 0.2);
            }}

            button.search-btn {{
                width: 100%;
                padding: 16px;
                border-radius: 16px;
                border: none;
                background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
                color: white;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }}
            button.search-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(79, 172, 254, 0.4);
            }}
            button.search-btn:active {{
                transform: translateY(1px);
            }}

            .footer-text {{
                margin-top: 30px;
                font-size: 13px;
                color: #6b7280;
                font-weight: 300;
            }}
            .footer-text a {{
                color: var(--primary);
                text-decoration: none;
                font-weight: 600;
                transition: opacity 0.2s;
            }}
            .footer-text a:hover {{ opacity: 0.8; }}
        </style>
    </head>
    <body>
        <div class="bg-blob"></div>

        <a href="/admin" class="admin-login-btn">
            <i class="fas fa-shield-alt"></i> Admin Panel
        </a>

        <div class="glass-panel">
            <div class="icon-wrapper">
                <i class="fas fa-bolt"></i>
            </div>
            <h1>Fast Finder</h1>
            <p class="subtitle">Search Movies, Series & Anime Instantly</p>
            
            <div class="search-wrapper">
                <i class="fas fa-search"></i>
                <input type="text" id="searchInput" placeholder="Enter movie name (e.g. Iron Man)..." autocomplete="off">
            </div>
            
            <button class="search-btn" onclick="startSearch()">
                Explore on Telegram <i class="fas fa-arrow-right"></i>
            </button>
            
            <div class="footer-text">
                Powered by <a href="https://t.me/{bot_username}">Auto Filter Bot</a>
            </div>
        </div>

        <script>
            function startSearch() {{
                var query = document.getElementById("searchInput").value.trim();
                if(query) {{
                    window.location.href = "https://t.me/{bot_username}?start=" + encodeURIComponent(query);
                }} else {{
                    window.location.href = "https://t.me/{bot_username}";
                }}
            }}

            document.getElementById("searchInput").addEventListener("keypress", function(event) {{
                if (event.key === "Enter") {{
                    startSearch();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

# ─────────────────────────────────────────────
# 📺 STREAM / WATCH ROUTE
# ─────────────────────────────────────────────
@routes.get("/watch/{message_id}")
async def watch_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return web.Response(text=await media_watch(message_id), content_type='text/html')
    except ValueError:
        return web.Response(status=400, text="Invalid Message ID")
    except Exception as e:
        logger.error(f"Watch Error: {e}")
        return web.Response(status=500, text="Internal Server Error")

# ─────────────────────────────────────────────
# 📥 DOWNLOAD ROUTE
# ─────────────────────────────────────────────
@routes.get("/download/{message_id}")
async def download_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return await media_download(request, message_id)
    except ValueError:
        return web.Response(status=400, text="Invalid Message ID")
    except Exception as e:
        logger.error(f"Download Error: {e}")
        return web.Response(status=500, text="Internal Server Error")

# ─────────────────────────────────────────────
# 🚀 CORE STREAMING LOGIC (KOYEB OPTIMIZED)
# ─────────────────────────────────────────────
async def media_download(request, message_id: int):
    try:
        # 1. Fetch Message safely
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
        if not media_msg or not media_msg.media:
            return web.Response(status=404, text="File Not Found or Removed")
            
        media = getattr(media_msg, media_msg.media.value, None)
        if not media:
            return web.Response(status=404, text="Media Not Supported")

        file_size = media.file_size
        
        # 2. ✅ FIX: Smart Filename Generator
        file_name = getattr(media, 'file_name', None)
        if not file_name:
            if getattr(media_msg, 'video', None):
                file_name = f"video_{secrets.token_hex(3)}.mp4"
            elif getattr(media_msg, 'audio', None):
                file_name = f"audio_{secrets.token_hex(3)}.mp3"
            else:
                file_name = f"file_{secrets.token_hex(3)}.bin"
        
        mime_type = getattr(media, 'mime_type', None)
        if not mime_type:
            mime_guess = mimetypes.guess_type(file_name)[0]
            mime_type = mime_guess if mime_guess else "application/octet-stream"

        # 3. Handle Range Headers Safely
        range_header = request.headers.get('Range', 0)
        
        try:
            if range_header:
                from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
                from_bytes = int(from_bytes)
                until_bytes = int(until_bytes) if until_bytes else file_size - 1
            else:
                from_bytes = 0
                until_bytes = file_size - 1
        except Exception:
            from_bytes = 0
            until_bytes = file_size - 1

        if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
            return web.Response(
                status=416,
                body="416: Range Not Satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"}
            )

        # 4. Calculate Chunks
        req_length = until_bytes - from_bytes + 1
        new_chunk_size = await chunk_size(req_length)
        offset = await offset_fix(from_bytes, new_chunk_size)
        
        first_part_cut = from_bytes - offset
        last_part_cut = (until_bytes % new_chunk_size) + 1
        part_count = math.ceil(req_length / new_chunk_size)

        # 5. Generate Stream Body
        body = TGCustomYield().yield_file(
            media_msg, offset, first_part_cut, last_part_cut, part_count, new_chunk_size
        )

        # 6. Return Response
        encoded_filename = quote(file_name)
        
        headers = {
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Disposition": f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}',
            "Accept-Ranges": "bytes",
            "Content-Length": str(req_length)
        }

        return web.Response(
            status=206 if range_header else 200,
            body=body,
            headers=headers
        )

    except Exception as e:
        logger.error(f"Stream Error: {e}")
        return web.Response(status=500, text="Server Error during streaming")
