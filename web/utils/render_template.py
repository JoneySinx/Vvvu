from info import BIN_CHANNEL, URL
from utils import temp
import urllib.parse
import html
import logging

# Logger Setup
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 🎨 STREAMING TEMPLATE (Fast Finder Premium UI)
# ─────────────────────────────────────────────
watch_tmplt = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading} | Fast Finder</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    <style>
        :root {{
            --primary: #00d2ff;
            --secondary: #3a7bd5;
            --bg-dark: #0f0f1a;
            --text-white: #ffffff;
            --text-gray: #a0aab5;
            --glass-bg: rgba(22, 33, 62, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }}
        
        body {{
            background-color: var(--bg-dark);
            color: var(--text-white);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            position: relative;
        }}

        /* Animated Background Blob */
        .bg-blob {{
            position: absolute;
            top: -20%; left: -10%;
            width: 500px; height: 500px;
            background: linear-gradient(180deg, rgba(58, 123, 213, 0.2) 0%, rgba(0, 210, 255, 0.1) 100%);
            filter: blur(100px);
            border-radius: 50%;
            z-index: 0;
            animation: float 8s infinite alternate ease-in-out;
        }}
        @keyframes float {{
            0% {{ transform: translate(0, 0); }}
            100% {{ transform: translate(50px, 50px); }}
        }}

        /* Navbar Style */
        .navbar {{
            padding: 20px 4%;
            display: flex;
            align-items: center;
            background: rgba(15, 15, 26, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--glass-border);
            position: fixed;
            width: 100%;
            z-index: 100;
            top: 0;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        }}
        
        .logo {{
            font-size: 1.8rem;
            font-weight: 700;
            background: -webkit-linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        /* Main Content */
        .hero-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 100px 20px 40px;
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
            z-index: 10;
        }}

        .player-box {{
            width: 100%;
            position: relative;
            border-radius: 16px;
            overflow: hidden;
            background: #000;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 210, 255, 0.2);
            border: 1px solid var(--glass-border);
        }}

        .video-container video {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .info-section {{
            width: 100%;
            margin-top: 25px;
            text-align: left;
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            padding: 25px;
            border-radius: 16px;
            border: 1px solid var(--glass-border);
        }}

        .title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: var(--text-white);
            word-break: break-word;
        }}

        .controls-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        /* Modern Buttons */
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 12px 24px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            border: none;
            gap: 8px;
        }}

        .btn-download {{
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            color: #0f0f1a;
            box-shadow: 0 5px 15px rgba(0, 210, 255, 0.3);
        }}
        .btn-download:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 210, 255, 0.5);
        }}

        .btn-copy {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-white);
            border: 1px solid var(--glass-border);
        }}
        .btn-copy:hover {{ 
            background: rgba(255, 255, 255, 0.2); 
            transform: translateY(-2px);
        }}

        /* Custom Plyr Theme for Fast Finder */
        .plyr--video {{
            --plyr-color-main: var(--primary);
            --plyr-video-background: #000;
        }}

        /* Toast */
        #toast {{
            visibility: hidden;
            min-width: 250px;
            background: linear-gradient(90deg, var(--secondary), var(--primary));
            color: #0f0f1a;
            text-align: center;
            border-radius: 8px;
            padding: 16px;
            position: fixed;
            z-index: 999;
            right: 30px;
            bottom: 30px;
            font-weight: 700;
            box-shadow: 0 5px 20px rgba(0, 210, 255, 0.4);
        }}
        #toast.show {{ visibility: visible; animation: fadein 0.5s, fadeout 0.5s 2.5s; }}

        @keyframes fadein {{ from {{bottom: 0; opacity: 0;}} to {{bottom: 30px; opacity: 1;}} }}
        @keyframes fadeout {{ from {{bottom: 30px; opacity: 1;}} to {{bottom: 0; opacity: 0;}} }}

        @media (max-width: 768px) {{
            .logo {{ font-size: 1.5rem; }}
            .title {{ font-size: 1.2rem; }}
            .btn {{ width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="bg-blob"></div>

    <div class="navbar">
        <div class="logo"><i class="fas fa-bolt"></i> Fast Finder</div>
    </div>

    <div class="hero-container">
        
        <div class="player-box">
            <video id="player" playsinline controls data-poster="">
                <source src="{src}" type="{mime_type}" />
            </video>
        </div>

        <div class="info-section">
            <div class="title"><i class="fas fa-film" style="color:var(--primary); margin-right:8px;"></i> {file_name}</div>
            
            <div class="controls-row">
                <a href="{src}" class="btn btn-download">
                    <i class="fas fa-download"></i> Direct Download
                </a>

                <button onclick="copyLink()" class="btn btn-copy">
                    <i class="fas fa-link"></i> Copy Link
                </button>
            </div>
        </div>

    </div>

    <div id="toast"><i class="fas fa-check-circle"></i> Link Copied Successfully!</div>

    <script src="https://cdn.plyr.io/3.7.8/plyr.js"></script>
    <script>
        const player = new Plyr('#player', {{
            controls: ['play-large', 'play', 'progress', 'current-time', 'duration', 'settings', 'pip', 'fullscreen'],
            settings: ['speed'],
            hideControls: true
        }});

        function copyLink() {{
            const el = document.createElement('textarea');
            el.value = "{src}";
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            
            var x = document.getElementById("toast");
            x.className = "show";
            setTimeout(function(){{ x.className = x.className.replace("show", ""); }}, 3000);
        }}
    </script>
</body>
</html>
"""

async def media_watch(message_id):
    try:
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
        media = getattr(media_msg, media_msg.media.value, None)
        
        if not media:
            return "<h2>❌ File Not Found or Deleted</h2>"

        src = urllib.parse.urljoin(URL, f'download/{message_id}')
        mime_type = getattr(media, 'mime_type', 'video/mp4')
        tag = mime_type.split('/')[0].strip()
        
        if tag == 'video':
            file_name = html.escape(media.file_name if hasattr(media, 'file_name') else "Video File")
            
            return watch_tmplt.format(
                heading=f"Watch {file_name}",
                file_name=file_name,
                src=src,
                mime_type=mime_type
            )
        else:
            # Fallback for non-video files with matching theme
            return f"""
            <body style="background:#0f0f1a; color:white; display:flex; align-items:center; justify-content:center; height:100vh; font-family:'Segoe UI', sans-serif; margin:0;">
                <div style="text-align:center; background:rgba(22, 33, 62, 0.7); padding:40px; border-radius:16px; border:1px solid rgba(255,255,255,0.1); box-shadow:0 10px 30px rgba(0,0,0,0.5);">
                    <h1 style="margin-bottom:20px; font-size:1.8rem;">⚠️ File Format Not Supported for Streaming</h1>
                    <p style="color:#a0aab5; margin-bottom:30px;">This file is not a video. Please download it to view.</p>
                    <a href="{src}" style="background:linear-gradient(90deg, #3a7bd5, #00d2ff); color:#0f0f1a; font-weight:bold; text-decoration:none; padding:15px 30px; border-radius:30px; display:inline-block; transition:0.3s;">⬇️ Direct Download</a>
                </div>
            </body>
            """
    except Exception as e:
        logger.error(f"Template Error: {e}")
        return f"""
        <body style="background:#0f0f1a; color:#ff4d4d; display:flex; align-items:center; justify-content:center; height:100vh; font-family:sans-serif;">
            <h2>Server Error: {str(e)}</h2>
        </body>
        """
