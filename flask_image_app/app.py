from flask import Flask, send_from_directory, render_template_string, url_for
import qrcode
import io
import base64
import os
import uuid

app = Flask(__name__)
STATIC_FOLDER = 'static'  # default static folder
DOMAIN = "https://deeputsavrmlauexam-in-department-8v3z.onrender.com"  # YOUR URL

# Make sure static folder exists
os.makedirs(STATIC_FOLDER, exist_ok=True)

# In-memory dictionary to map UUID to image filename
id_to_image = {}

@app.route('/')
def index():
    # List images in static folder
    images = [f for f in os.listdir(STATIC_FOLDER) if os.path.isfile(os.path.join(STATIC_FOLDER, f))]

    # Assign UUIDs to images if not already mapped
    for img in images:
        if img not in id_to_image.values():
            uid = str(uuid.uuid4())[:8]  # short random id
            id_to_image[uid] = img

    # Generate QR codes for all images
    qr_data = []
    for uid, filename in id_to_image.items():
        url = f"{DOMAIN}/image/{uid}"
        img_qr = qrcode.make(url)
        buffer = io.BytesIO()
        img_qr.save(buffer)
        buffer.seek(0)
        qr_b64 = base64.b64encode(buffer.read()).decode()
        qr_data.append({"id": uid, "filename": filename, "url": url, "qr": qr_b64})

    html = '''
    <html>
    <head><title>Image QR Codes</title></head>
    <body>
        <h1>QR Codes for Images</h1>
        {% for item in qr_data %}
            <div style="margin-bottom: 20px;">
                <h3>{{ item.filename }} (ID: {{ item.id }})</h3>
                <p>URL: <a href="{{ item.url }}">{{ item.url }}</a></p>
                <img src="data:image/png;base64,{{ item.qr }}" alt="QR code for {{ item.filename }}">
            </div>
        {% endfor %}
    </body>
    </html>
    '''
    return render_template_string(html, qr_data=qr_data)

# Endpoint to serve images by UUID
@app.route('/image/<uid>')
def serve_image(uid):
    filename = id_to_image.get(uid)
    if not filename:
        return "Image not found", 404
    return send_from_directory(STATIC_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
