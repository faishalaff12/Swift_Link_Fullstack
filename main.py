from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import string
import random
import datetime

app = FastAPI(title="SwiftLink API")

# In-Memory Database
db_links = {}
db_analytics = {}

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class LinkRequest(BaseModel):
    original_url: str

# --- API ENDPOINTS ---

@app.post("/api/shorten")
def shorten_url(request: LinkRequest):
    if not request.original_url.startswith("http"):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    short_id = generate_short_id()
    db_links[short_id] = request.original_url
    db_analytics[short_id] = {
        "clicks": 0,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return {"short_id": short_id, "original_url": request.original_url}

@app.get("/api/analytics")
def get_analytics():
    # Menggabungkan data link dan analitik
    dashboard_data = []
    for short_id, url in db_links.items():
        data = db_analytics[short_id]
        dashboard_data.append({
            "short_id": short_id,
            "original_url": url,
            "clicks": data["clicks"],
            "created_at": data["created_at"]
        })
    # Mengurutkan data dari yang terbaru
    return sorted(dashboard_data, key=lambda x: x["created_at"], reverse=True)

# --- ROUTING & FRONTEND ---

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    if short_id in db_links:
        # Menambah counter klik
        db_analytics[short_id]["clicks"] += 1
        return RedirectResponse(url=db_links[short_id])
    raise HTTPException(status_code=404, detail="Link not found")

@app.get("/", response_class=HTMLResponse)
def read_index():
    # Membaca file HTML Frontend
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import os
    import uvicorn
    # Mengambil port otomatis dari Railway, atau pakai 8000 kalau di laptop lokal
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)