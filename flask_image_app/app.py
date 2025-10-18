from flask import Flask, send_from_directory, render_template_string
import qrcode
import io
import base64
import os
import uuid

app = Flask(__name__)
STATIC_FOLDER = 'static'
DOMAIN = "https://deeputsavrmlauexam-in-department.onrender.com"  # Your domain here

# Ensure static folder exists
os.makedirs(STATIC_FOLDER, exist_ok=True)

# In-memory map of unique ids to image filenames
id_to_image = {}

@app.route('/')
def index():
    image_files = [f for f in os.listdir(STATIC_FOLDER) if os.path.isfile(os.path.join(STATIC_FOLDER, f))]

    # Map ids to images (create new if needed)
    for img in image_files:
        if img not in id_to_image.values():
            uid = str(uuid.uuid4())[:8]
            id_to_image[uid] = img

    qr_list = []
    for uid, img_name in id_to_image.items():
        unique_url = f"{DOMAIN}/images/{uid}"
        qr = qrcode.make(unique_url)
        buf = io.BytesIO()
        qr.save(buf)
        buf.seek(0)
        qr_b64 = base64.b64encode(buf.read()).decode('utf-8')
        qr_list.append({'id': uid, 'image': img_name, 'url': unique_url, 'qr': qr_b64})

    html = '''
    <html>
    <head><title>QR Codes for Static Images</title></head>
    <body>
        <h1>QR Codes for Images</h1>
        {% for item in qr_list %}
            <div style="margin-bottom: 20px;">
                <h3>{{ item.image }} (ID: {{ item.id }})</h3>
                <p>URL: <a href="{{ item.url }}">{{ item.url }}</a></p>
                <img src="data:image/png;base64,{{ item.qr }}" alt="QR Code for {{ item.image }}"/>
            </div>
        {% endfor %}
    </body>
    </html>
    '''
    return render_template_string(html, qr_list=qr_list)

@app.route('/images/<uid>')
def serve_image(uid):
    image_name = id_to_image.get(uid)
    if not image_name:
        return "Image not found", 404
    return send_from_directory(STATIC_FOLDER, image_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
