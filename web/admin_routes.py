from aiohttp import web
import time
import uuid
from info import ADMIN_USERNAME, ADMIN_PASSWORD
from utils import temp

admin_routes = web.RouteTableDef()

@admin_routes.get('/admin')
async def admin_login_page(request):
    token = request.query.get('token')
    if not hasattr(temp, 'ADMIN_TOKENS'): temp.ADMIN_TOKENS = {}

    if not token or token not in temp.ADMIN_TOKENS:
        return web.Response(text="❌ Invalid or Missing Token! Generate a new link from Telegram.", status=403)
    if time.time() > temp.ADMIN_TOKENS[token]:
        del temp.ADMIN_TOKENS[token]
        return web.Response(text="⏳ Token Expired! Please generate a new link via Telegram.", status=403)

    html = f"""
    <html>
        <head>
            <title>Admin Login</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .login-box {{ background: white; padding: 40px 30px; border-radius: 12px; box-shadow: 0px 8px 20px rgba(0,0,0,0.1); text-align: center; width: 100%; max-width: 320px; }}
                h2 {{ margin-bottom: 20px; color: #333; }}
                input {{ display: block; width: 100%; box-sizing: border-box; margin: 15px 0; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; }}
                button {{ background: #0088cc; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; transition: 0.3s; }}
                button:hover {{ background: #006699; }}
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>🔒 Admin Login</h2>
                <form action="/login" method="post">
                    <input type="hidden" name="token" value="{token}">
                    <input type="text" name="username" placeholder="Enter Username" required>
                    <input type="password" name="password" placeholder="Enter Password" required>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

@admin_routes.post('/login')
async def admin_login_post(request):
    data = await request.post()
    token, username, password = data.get('token'), data.get('username'), data.get('password')

    if not hasattr(temp, 'ADMIN_TOKENS'): temp.ADMIN_TOKENS = {}
    if not hasattr(temp, 'ADMIN_SESSIONS'): temp.ADMIN_SESSIONS = {}

    if not token or token not in temp.ADMIN_TOKENS or time.time() > temp.ADMIN_TOKENS[token]:
        return web.Response(text="⏳ Token Expired or Invalid!", status=403)

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session_id = str(uuid.uuid4())
        temp.ADMIN_SESSIONS[session_id] = temp.ADMIN_TOKENS[token]
        del temp.ADMIN_TOKENS[token]
        response = web.HTTPFound('/dashboard')
        response.set_cookie('admin_session', session_id, max_age=3600)
        return response
    else:
        error_html = f"<html><body style='text-align:center; margin-top:50px;'><h2 style='color:red;'>❌ Invalid Username or Password!</h2><a href='/admin?token={token}'>Try Again</a></body></html>"
        return web.Response(text=error_html, content_type='text/html', status=401)

@admin_routes.get('/dashboard')
async def admin_dashboard(request):
    session_id = request.cookies.get('admin_session')
    if not hasattr(temp, 'ADMIN_SESSIONS'): temp.ADMIN_SESSIONS = {}

    if not session_id or session_id not in temp.ADMIN_SESSIONS:
        return web.Response(text="❌ Unauthorized Access! Please login via Telegram link.", status=403)
    if time.time() > temp.ADMIN_SESSIONS[session_id]:
        del temp.ADMIN_SESSIONS[session_id]
        return web.Response(text="⏳ Session Expired! Please generate a new link from Telegram.", status=403)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Admin Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background: #eef2f3; margin: 0; color: #333; }
            .container { max-width: 900px; margin: auto; }
            .header { background: linear-gradient(135deg, #0088cc, #00d2ff); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h1 { margin: 0; font-size: 26px; }
            .card { background: white; padding: 25px; margin-top: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            
            /* Search Area */
            .search-box { display: flex; gap: 10px; margin-top: 15px; }
            .search-box input { flex: 1; padding: 15px 20px; border: 2px solid #ddd; border-radius: 30px; font-size: 16px; outline: none; transition: 0.3s; }
            .search-box input:focus { border-color: #0088cc; }
            .search-box button { background: #0088cc; color: white; border: none; padding: 15px 30px; border-radius: 30px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; }
            .search-box button:hover { background: #006699; }
            
            /* Status Bar & Pagination */
            .status-bar { display: none; justify-content: space-between; align-items: center; margin-top: 20px; background: #f8f9fa; padding: 10px 20px; border-radius: 8px; border: 1px solid #ddd; }
            .badge { background: #28a745; color: white; padding: 5px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
            .pagination { display: flex; gap: 10px; }
            .pagination button { background: #333; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-size: 14px; }
            .pagination button:hover { background: #555; }
            
            /* Grid & Cards */
            #results { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
            .res-card { background: #fff; padding: 20px; border-radius: 10px; border: 1px solid #eee; box-shadow: 0 2px 10px rgba(0,0,0,0.02); transition: 0.2s; }
            .res-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,136,204,0.1); border-color: #0088cc; }
            .res-title { font-size: 15px; font-weight: bold; margin-bottom: 10px; color: #222; word-wrap: break-word; }
            .res-info { color: #777; font-size: 13px; margin-bottom: 15px; }
            .btn-group { display: flex; gap: 10px; }
            .btn-play, .btn-dl { flex: 1; text-align: center; padding: 10px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: bold; color: white; }
            .btn-play { background: #28a745; } .btn-play:hover { background: #218838; }
            .btn-dl { background: #ffc107; color: black; } .btn-dl:hover { background: #e0a800; }
            
            .loader { text-align: center; color: #0088cc; display: none; margin-top: 20px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👋 Welcome to Admin Dashboard</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Secure Session Active</p>
            </div>

            <div class="card">
                <h3 style="margin-top: 0; display: flex; align-items: center; gap: 8px;">
                    🔍 Live Database Search
                </h3>
                
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search movies, series (e.g. Iron Man)...">
                    <button onclick="performSearch(0)">Search 🔍</button>
                </div>

                <div id="loader" class="loader">Searching Database... ⏳</div>

                <div id="status-bar" class="status-bar">
                    <div id="totalCount" class="badge"></div>
                    <div class="pagination">
                        <button id="prevBtn" onclick="goPrev()" style="display:none;">⬅️ Previous</button>
                        <button id="nextBtn" onclick="goNext()" style="display:none;">Next ➡️</button>
                    </div>
                </div>

                <div id="results"></div>
            </div>
            
        </div>

        <script>
            let currentQuery = "";
            let currentOffset = 0;
            let nextOffsetValue = "";

            async function performSearch(offset) {
                const query = document.getElementById('searchInput').value.trim();
                if (!query) return;

                currentQuery = query;
                currentOffset = offset;

                const resultsDiv = document.getElementById('results');
                const statusBar = document.getElementById('status-bar');
                const totalCount = document.getElementById('totalCount');
                const prevBtn = document.getElementById('prevBtn');
                const nextBtn = document.getElementById('nextBtn');
                const loader = document.getElementById('loader');
                
                resultsDiv.innerHTML = "";
                statusBar.style.display = "none";
                loader.style.display = "block";
                
                try {
                    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&offset=${offset}`);
                    const data = await response.json();
                    
                    loader.style.display = "none";
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<h3 style="color:red; text-align:center; width:100%;">Error: ${data.error}</h3>`;
                        return;
                    }
                    
                    if (data.total === 0) {
                        resultsDiv.innerHTML = '<h3 style="text-align:center; width:100%; color: #555;">❌ No files found!</h3>';
                        return;
                    }

                    // Update Status Bar
                    totalCount.innerHTML = `📊 Found ${data.total} Results`;
                    nextOffsetValue = data.next_offset;

                    // Button Logic
                    prevBtn.style.display = (offset > 0) ? "block" : "none";
                    nextBtn.style.display = (nextOffsetValue !== "") ? "block" : "none";
                    statusBar.style.display = "flex";
                    
                    // Render Cards
                    data.results.forEach(file => {
                        const card = `
                            <div class="res-card">
                                <div class="res-title">${file.name}</div>
                                <div class="res-info">💾 Size: ${file.size} &nbsp;|&nbsp; 📁 ${file.type}</div>
                                <div class="btn-group">
                                    <a href="${file.watch}" target="_blank" class="btn-play">▶️ Play</a>
                                    <a href="${file.download}" class="btn-dl">⬇️ Download</a>
                                </div>
                            </div>
                        `;
                        resultsDiv.innerHTML += card;
                    });
                } catch (err) {
                    loader.style.display = "none";
                    resultsDiv.innerHTML = '<h3 style="color:red; text-align:center; width:100%;">Connection Error!</h3>';
                }
            }

            function goNext() {
                if (nextOffsetValue !== "") performSearch(nextOffsetValue);
            }

            function goPrev() {
                // Assuming 20 items per page
                let newOffset = currentOffset - 20;
                if (newOffset < 0) newOffset = 0;
                performSearch(newOffset);
            }

            // Enter key support
            document.getElementById("searchInput").addEventListener("keypress", function(event) {
                if (event.key === "Enter") performSearch(0);
            });
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')
8
