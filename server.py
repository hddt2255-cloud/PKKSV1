import http.server
import socketserver
import json
import os
import sys
import re
import urllib.parse
import threading
import base64
import urllib.request
import urllib.parse

def bg_upload(file_content, filename, mime_type, apps_script_url, user_name, folder_id=""):
    try:
        if not apps_script_url: return
        b64_data = base64.b64encode(file_content).decode('utf-8')
        payload = {
            'filename': filename,
            'mimeType': mime_type,
            'file': b64_data,
            'user': user_name,
            'folderId': folder_id
        }
        data = urllib.parse.urlencode(payload).encode('utf-8')
        req = urllib.request.Request(apps_script_url, data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        urllib.request.urlopen(req, timeout=60)
        print(f"Background sync to GDrive successful for {filename}")
    except Exception as e:
        print(f"Background upload failed for {filename}: {e}")

def bg_delete(filename, apps_script_url, folder_id=""):
    try:
        if not apps_script_url: return
        payload = {'action': 'delete', 'fileName': filename, 'folderId': folder_id}
        data = urllib.parse.urlencode(payload).encode('utf-8')
        req = urllib.request.Request(apps_script_url, data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        urllib.request.urlopen(req, timeout=60)
        print(f"Background delete from GDrive successful for {filename}")
    except Exception as e:
        print(f"Background delete failed for {filename}: {e}")



# Force UTF-8 encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 8085
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PKKS_FOLDER_NAME = "PKKS 2026"
UPLOADS_DIR = os.path.join(BASE_DIR, PKKS_FOLDER_NAME)

# DATA_DIR and UPLOADS_DIR are now dynamic based on NPSN

INITIAL_USERS = [
  {"id": "abdul_yakub", "name": "Abdul Yakub, S.Ag", "role": "kepsek", "jabatan": "Kepala Sekolah & Evaluator"},
  {"id": "susanti", "name": "Susanti, S.Kom, S.Pd", "role": "guru", "jabatan": "Guru Komputer / TI"},
  {"id": "legina_puspa", "name": "Legina Puspa Wardini,S.Pd.I", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "bintari_kusumaningsih", "name": "Bintari Kusumaningsih, S.H", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "ocha_desy", "name": "Ocha Desy Ariyanti, S.Pd", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "mia_chairunnisa", "name": "Mia Chairunnisa, S.Pd", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "muhammad_irfan", "name": "Muhammad Irfan, S.Pd", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "dwi_erlindawati", "name": "Dwi Erlindawati, M.Pd", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "sherly_mugi", "name": "Sherly Mugi Anugrah, S.E", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "ita_tegowati", "name": "Ita Tegowati, S.Pd.I", "role": "guru", "jabatan": "Guru PAI"},
  {"id": "liko_ranti", "name": "Liko Ranti, S.Pd", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "esthy_ening", "name": "N. Esthy Ening S., S.Sos", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "abdullah", "name": "Abdullah, S.Ag", "role": "guru", "jabatan": "Guru PAI"},
  {"id": "dahlan_setiawan", "name": "Dahlan Setiawan, S.Pd", "role": "guru", "jabatan": "Guru PJOK"},
  {"id": "eko_mulyawan", "name": "Eko Mulyawan, A.Md", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "abdurohim", "name": "Abdurohim, S.Pd", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "muhammad_ali_yusuf", "name": "Muhammad Ali Yusuf", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "yeni_istiyani", "name": "Yeni Istiyani, S.Pd.I", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "indyah_montisari", "name": "Indyah Montisari", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "habib_riyadhi", "name": "Habib Riyadhi", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "rahmat_abdullah", "name": "Rahmat Abdullah", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "misbah_adeline", "name": "Misbah Adeline, S.E", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "hidayat", "name": "Hidayat", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "andi_purnomo", "name": "Andi Purnomo", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "rayhan", "name": "Rayhan", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "tio_rumboko", "name": "Tio Rumboko", "role": "guru", "jabatan": "Guru Kelas"},
  {"id": "puji_astuti", "name": "Puji Astuti", "role": "guru", "jabatan": "Guru Kelas"}
]

DEFAULT_SETTINGS = {
  "namaSekolah": "SDIT ANNISA BOGOR",
  "alamatSekolah": "Jl. Raya Ciomas No. 12, Ciomas, Kabupaten Bogor",
  "namaKepalaSekolah": "Abdul Yakub, S.Ag",
  "defaultPassword": "Sditannisa",
  "tanggalCetak": "Bekasi, 29 September 2026",
  "googleDriveLink": "",
  "users": INITIAL_USERS
}

def load_settings(data_dir=None):
    if data_dir is None: return DEFAULT_SETTINGS
    settings_file = os.path.join(data_dir, 'settings.json')
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception as e:
            print(f"Error reading settings.json: {e}")
    save_settings(DEFAULT_SETTINGS, data_dir)
    return DEFAULT_SETTINGS

def save_settings(data, data_dir=None):
    if data_dir is None:
        return
    settings_file = os.path.join(data_dir, 'settings.json')
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving settings.json: {e}")

def extract_gdrive_folder_id(url_or_id):
    if not url_or_id:
        return None
    url_or_id = url_or_id.strip()
    if 'folders/' in url_or_id:
        return url_or_id.split('folders/')[1].split('?')[0].split('/')[0]
    elif 'id=' in url_or_id:
        return url_or_id.split('id=')[1].split('&')[0]
    elif len(url_or_id) > 15 and '/' not in url_or_id and '.' not in url_or_id:
        return url_or_id
    return None

def upload_file_to_gdrive_api(file_path, orig_name, user_name, folder_link_or_id):
    creds_file = os.path.join(BASE_DIR, 'credentials.json')
    if not os.path.exists(creds_file):
        creds_file = os.path.join(BASE_DIR, 'service_account.json')
    if not os.path.exists(creds_file):
        return None

    folder_id = extract_gdrive_folder_id(folder_link_or_id)
    if not folder_id:
        return None

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)

        file_metadata = {
            'name': f"[{user_name}] {orig_name}",
            'parents': [folder_id]
        }
        
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        mime = mime_types.get(ext, 'application/octet-stream')

        media = MediaFileUpload(file_path, mimetype=mime, resumable=True)
        uploaded = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink, webContentLink').execute()

        try:
            service.permissions().create(fileId=uploaded.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
        except Exception as pe:
            print(f"Permission set note: {pe}")

        return uploaded.get('webViewLink') or uploaded.get('webContentLink')
    except Exception as e:
        print(f"GDrive API Upload error: {e}")
        return None

class PKKSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def get_school_npsn(self):
        return self.headers.get('X-School-NPSN')

    def get_dirs(self, force_npsn=None):
        npsn = force_npsn or self.get_school_npsn()
        if not npsn:
            return None, None, None
        base = os.path.join(BASE_DIR, 'data_schools', npsn)
        uploads = os.path.join(base, PKKS_FOLDER_NAME)
        data = os.path.join(base, 'data_users')
        return base, uploads, data

    def ensure_dirs(self, uploads, data):
        os.makedirs(uploads, exist_ok=True)
        os.makedirs(data, exist_ok=True)


    def translate_path(self, path):
        parsed_path = urllib.parse.urlparse(path).path
        unquoted = urllib.parse.unquote(parsed_path)
        if unquoted == '/' or unquoted == '':
            return os.path.join(BASE_DIR, 'index.html')
        
        _, uploads, _ = self.get_dirs()
        if not uploads:
            return super().translate_path(path)
            
        if unquoted.startswith('/PKKS 2026/') or unquoted.startswith(f'/{PKKS_FOLDER_NAME}/'):
            rel_path = unquoted.split('/', 2)[-1]
            return os.path.join(uploads, rel_path)
        if unquoted.startswith('/uploads/'):
            rel_path = unquoted[len('/uploads/'):]
            return os.path.join(uploads, rel_path)
        return super().translate_path(path)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)

        if parsed_url.path == '/api/pdf-bytes':
            file_name = query.get('file', [''])[0]
            file_name = urllib.parse.unquote(file_name)
            if not file_name:
                self.send_response(400)
                self.end_headers()
                return

            safe_name = os.path.basename(file_name)
            force_npsn = query.get('npsn', [None])[0]
            _, UPLOADS_DIR, _ = self.get_dirs(force_npsn=force_npsn)
            if not UPLOADS_DIR: self.send_response(400); self.end_headers(); return
            filepath = os.path.join(UPLOADS_DIR, safe_name)

            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.send_response(200)
                # application/octet-stream prevents IDM (Internet Download Manager) from intercepting PDF fetch
                content_type = 'application/octet-stream'
                if safe_name.lower().endswith('.png'): content_type = 'image/png'
                elif safe_name.lower().endswith(('.jpg', '.jpeg')): content_type = 'image/jpeg'
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(os.path.getsize(filepath)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.end_headers()
                try:
                    with open(filepath, 'rb') as f:
                        while True:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                except Exception:
                    pass
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        if parsed_url.path == '/api/settings':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(load_settings(self.get_dirs()[2]), ensure_ascii=False).encode('utf-8'))
            return

        if parsed_url.path == '/api/users':
            settings = load_settings(self.get_dirs()[2])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(settings.get('users', []), ensure_ascii=False).encode('utf-8'))
            return

        if parsed_url.path == '/api/data':
            settings = load_settings(self.get_dirs()[2])
            users = settings.get('users', [])
            user_id = query.get('user', ['abdul_yakub'])[0]

            if user_id in ['all', 'semua']:
                combined_scores = {}
                combined_supervisi = {
                    "pangkat": "Gabungan",
                    "mapel": "Seluruh Guru",
                    "jamTatapMuka": "Semua",
                    "semesterKelas": "Semua",
                    "scores": {},
                    "saran": ""
                }
                all_saran = []

                if os.path.exists(self.get_dirs()[2]):
                    DATA_DIR = self.get_dirs()[2]
                    data_files = [f for f in os.listdir(DATA_DIR) if f.startswith('data_') and f.endswith('.json')]
                    for df in data_files:
                        target_uid = df[5:-5]
                        target_uobj = next((u for u in users if u['id'] == target_uid), None)
                        target_uname = target_uobj['name'] if target_uobj else target_uid

                        try:
                            with open(os.path.join(DATA_DIR, df), 'r', encoding='utf-8') as f:
                                udata = json.load(f)

                            uscores = udata.get('scores', {})
                            for item_id, item_val in uscores.items():
                                if item_id not in combined_scores:
                                    combined_scores[item_id] = {"skor": 0, "catatan": "", "uploadedFiles": []}
                                
                                if isinstance(item_val, dict):
                                    if item_val.get('skor', 0) > combined_scores[item_id]['skor']:
                                        combined_scores[item_id]['skor'] = item_val.get('skor', 0)

                                    if item_val.get('catatan'):
                                        n_text = f"[{target_uname}]: {item_val.get('catatan')}"
                                        if combined_scores[item_id]['catatan']:
                                            if n_text not in combined_scores[item_id]['catatan']:
                                                combined_scores[item_id]['catatan'] += f" | {n_text}"
                                        else:
                                            combined_scores[item_id]['catatan'] = n_text

                                    for uf in item_val.get('uploadedFiles', []):
                                        uf_copy = dict(uf)
                                        if not uf_copy.get('user'):
                                            uf_copy['user'] = target_uname
                                        if not any(f.get('id') == uf_copy.get('id') or (f.get('savedName') and f.get('savedName') == uf_copy.get('savedName')) for f in combined_scores[item_id]['uploadedFiles']):
                                            combined_scores[item_id]['uploadedFiles'].append(uf_copy)

                            usuper = udata.get('supervisi', {})
                            if isinstance(usuper, dict):
                                if usuper.get('saran'):
                                    s_text = f"[{target_uname}]: {usuper.get('saran')}"
                                    if s_text not in all_saran:
                                        all_saran.append(s_text)
                                u_sup_scores = usuper.get('scores', {})
                                for s_no, s_val in u_sup_scores.items():
                                    if s_no not in combined_supervisi['scores'] or s_val > combined_supervisi['scores'][s_no]:
                                        combined_supervisi['scores'][s_no] = s_val
                        except Exception as e:
                            print(f"Error merging user data file {df}: {e}")

                combined_supervisi['saran'] = " | ".join(all_saran)

                if os.path.exists(self.get_dirs()[1]):
                    all_disk = os.listdir(self.get_dirs()[1])
                    known = set()
                    for item_id, item_val in combined_scores.items():
                        for uf in item_val.get('uploadedFiles', []):
                            known.add(uf.get('savedName'))
                            known.add(uf.get('name'))

                    for fname in all_disk:
                        if fname not in known and fname.startswith('['):
                            user_label = fname.split(']')[0].replace('[', '').replace('_', ' ')
                            fpath = os.path.join(self.get_dirs()[1], fname)
                            fsize = f"{round(os.path.getsize(fpath) / 1024, 1)} KB"
                            furl = f"/PKKS%202026/{urllib.parse.quote(fname)}"
                            new_file_obj = {
                                "id": f"sync_{int(os.path.getmtime(fpath))}_{fname[:8]}",
                                "name": fname,
                                "savedName": fname,
                                "url": furl,
                                "folder": PKKS_FOLDER_NAME,
                                "user": user_label,
                                "size": fsize
                            }
                            if '1.1' not in combined_scores:
                                combined_scores['1.1'] = {"skor": 0, "uploadedFiles": []}
                            if 'uploadedFiles' not in combined_scores['1.1']:
                                combined_scores['1.1']['uploadedFiles'] = []
                            combined_scores['1.1']['uploadedFiles'].append(new_file_obj)

                data = {
                    "user": "all",
                    "profile": {
                        "namaSekolah": settings.get('namaSekolah', 'SDIT ANNISA BOGOR'),
                        "alamatSekolah": settings.get('alamatSekolah', ''),
                        "namaGuru": "Semuanya (Gabungan Seluruh Guru)",
                        "namaKepalaSekolah": settings.get('namaKepalaSekolah', 'Abdul Yakub, S.Ag'),
                        "tahunPelajaran": "2025/2026"
                    },
                    "scores": combined_scores,
                    "supervisi": combined_supervisi
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
                return

            user_file = os.path.join(self.get_dirs()[2], f"data_{user_id}.json")
            
            user_obj = next((u for u in users if u['id'] == user_id), None)
            user_name = user_obj['name'] if user_obj else user_id

            if os.path.exists(user_file):
                with open(user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "user": user_id,
                    "profile": {
                        "namaSekolah": settings.get('namaSekolah', 'SDIT ANNISA BOGOR'),
                        "alamatSekolah": settings.get('alamatSekolah', ''),
                        "namaGuru": user_name,
                        "namaKepalaSekolah": settings.get('namaKepalaSekolah', 'Abdul Yakub, S.Ag'),
                        "tahunPelajaran": "2025/2026"
                    },
                    "scores": {}
                }

            # Smart Auto-Sync: Scan PKKS 2026 directory for files belonging to this user & clean up deleted files
            if 'scores' not in data:
                data['scores'] = {}

            sanitized_user_prefix = "".join([c for c in user_name if c.isalnum() or c in "_- "]).replace(" ", "_")
            if os.path.exists(self.get_dirs()[1]):
                all_disk_files = set(os.listdir(self.get_dirs()[1]))

                # 1. Clean up missing/deleted files from data
                for item_id, item_val in data['scores'].items():
                    if isinstance(item_val, dict) and 'uploadedFiles' in item_val:
                        item_val['uploadedFiles'] = [
                            uf for uf in item_val['uploadedFiles']
                            if uf.get('savedName') in all_disk_files or uf.get('name') in all_disk_files or uf.get('isDrive')
                        ]

                # 2. Collect existing file names in data
                known_files = set()
                for item_id, item_val in data['scores'].items():
                    if isinstance(item_val, dict) and 'uploadedFiles' in item_val:
                        for uf in item_val['uploadedFiles']:
                            known_files.add(uf.get('savedName'))
                            known_files.add(uf.get('name'))

                for f_name in all_disk_files:
                    # Check if file belongs to this user (e.g. starts with [Susanti_... or contains user name)
                    is_match = f"[{sanitized_user_prefix}" in f_name or f"[{user_id}" in f_name or f"[{user_name}" in f_name
                    if is_match and f_name not in known_files:
                        f_path = os.path.join(self.get_dirs()[1], f_name)
                        f_size_kb = f"{round(os.path.getsize(f_path) / 1024, 1)} KB"
                        f_url = f"/PKKS%202026/{urllib.parse.quote(f_name)}"
                        new_file_obj = {
                            "id": f"sync_{int(os.path.getmtime(f_path))}_{f_name[:8]}",
                            "name": f_name,
                            "savedName": f_name,
                            "url": f_url,
                            "folder": PKKS_FOLDER_NAME,
                            "user": user_name,
                            "size": f_size_kb
                        }
                        if '1.1' not in data['scores']:
                            data['scores']['1.1'] = {"skor": 0, "uploadedFiles": []}
                        if 'uploadedFiles' not in data['scores']['1.1']:
                            data['scores']['1.1']['uploadedFiles'] = []
                        data['scores']['1.1']['uploadedFiles'].append(new_file_obj)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return

        unquoted = urllib.parse.unquote(parsed_url.path)
        if unquoted.startswith('/PKKS 2026/') or unquoted.startswith(f'/{PKKS_FOLDER_NAME}/') or unquoted.startswith('/uploads/'):
            filepath = self.translate_path(self.path)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.send_response(200)
                ext = os.path.splitext(filepath)[1].lower()
                mime_types = {
                    '.pdf': 'application/pdf',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                    '.svg': 'image/svg+xml',
                    '.txt': 'text/plain',
                    '.html': 'text/html',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
                content_type = mime_types.get(ext, 'application/octet-stream')
                self.send_header('Content-Type', content_type)

                is_download = 'download' in query
                disposition = 'attachment' if is_download else 'inline'
                self.send_header('Content-Disposition', f'{disposition}; filename="{os.path.basename(filepath)}"')
                self.send_header('Content-Length', str(os.path.getsize(filepath)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                try:
                    with open(filepath, 'rb') as f:
                        while True:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                except Exception:
                    pass
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        return super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)

        if parsed_url.path == '/api/school-auth':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8')
                data = json.loads(body)
                action = data.get('action', 'login')
                npsn = data.get('npsn', '').strip()
                password = data.get('password', '').strip()
                name = data.get('name', '').strip()
                
                if not npsn:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"status":"error","message":"NPSN wajib diisi"}')
                    return
                    
                schools_db = os.path.join(BASE_DIR, 'schools.json')
                schools = {}
                if os.path.exists(schools_db):
                    with open(schools_db, 'r', encoding='utf-8') as f:
                        schools = json.load(f)
                        
                data_dir = os.path.join(BASE_DIR, 'data_schools', npsn, 'data_users')
                sfile = os.path.join(data_dir, 'settings.json')
                
                if action == 'register':
                    if npsn in schools:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b'{"status":"error","message":"NPSN sudah terdaftar. Silakan login."}')
                        return
                    if not name:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b'{"status":"error","message":"Nama Sekolah wajib diisi"}')
                        return
                        
                    schools[npsn] = {"nama": name, "npsn": npsn}
                    with open(schools_db, 'w', encoding='utf-8') as f:
                        json.dump(schools, f)
                        
                    uploads = os.path.join(BASE_DIR, 'data_schools', npsn, PKKS_FOLDER_NAME)
                    os.makedirs(uploads, exist_ok=True)
                    os.makedirs(data_dir, exist_ok=True)
                    
                    settings_copy = DEFAULT_SETTINGS.copy()
                    settings_copy['namaSekolah'] = name
                    settings_copy['schoolPassword'] = npsn
                    settings_copy['alamatSekolah'] = ""
                    settings_copy['namaKepalaSekolah'] = "Admin Sekolah"
                    settings_copy['defaultPassword'] = "123456"
                    settings_copy['users'] = [{"id": "admin", "name": "Admin Sekolah", "role": "kepsek", "jabatan": "Kepala Sekolah"}]
                    with open(sfile, 'w', encoding='utf-8') as f:
                        json.dump(settings_copy, f, ensure_ascii=False, indent=2)
                        
                    nama_sekolah = name
                else:
                    if npsn not in schools:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b'{"status":"error","message":"NPSN tidak ditemukan."}')
                        return
                        
                    if not os.path.exists(sfile):
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b'{"status":"error","message":"Data sekolah tidak valid."}')
                        return
                        
                    with open(sfile, 'r', encoding='utf-8') as f:
                        school_settings = json.load(f)
                    
                    saved_password = school_settings.get('schoolPassword', npsn)
                    with open('debug_pass.txt', 'a') as f_dbg:
                        f_dbg.write(f"DEBUG LOGIN: action={action!r}, npsn={npsn!r}, req_pass={password!r}, saved_pass={saved_password!r}\n")
                    if password != saved_password:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b'{"status":"error","message":"Password salah!"}')
                        return
                    
                    nama_sekolah = schools[npsn]["nama"]

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"status":"success", "namaSekolah": nama_sekolah}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
            return


        # remove duplicate parsed_url if any
        if self.path == '/api/settings':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                new_settings = json.loads(post_data.decode('utf-8'))
                save_settings(new_settings, self.get_dirs()[2])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Pengaturan berhasil disimpan!"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/login':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                user_id = body.get('username', '').strip()
                password = body.get('password', '').strip()

                settings = load_settings(self.get_dirs()[2])
                users = settings.get('users', [])
                default_pwd = settings.get('defaultPassword', 'Sditannisa')

                user_obj = next((u for u in users if u['id'] == user_id or u['name'].lower() == user_id.lower()), None)
                if user_obj and password == default_pwd:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "success",
                        "message": "Login berhasil!",
                        "user": user_obj
                    }).encode('utf-8'))
                else:
                    self.send_response(401)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "status": "error",
                        "message": f"Username atau Password salah! (Default Password saat ini: {default_pwd})"
                    }).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/save':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                user_id = data.get('user', 'abdul_yakub')
                _, _, data_dir = self.get_dirs()
                if not data_dir:
                    self.send_response(400)
                    self.end_headers()
                    return
                user_file = os.path.join(data_dir, f"data_{user_id}.json")
                with open(user_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Data berhasil disimpan!"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/delete-file':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                body = json.loads(post_data.decode('utf-8'))
                file_name = body.get('filename', '').strip()
                user_id = body.get('user', '').strip()

                if file_name:
                    safe_name = os.path.basename(file_name)
                    file_path = os.path.join(self.get_dirs()[1], safe_name)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            print(f"Successfully deleted physical file: {file_path}")
                            apps_script_url = load_settings(self.get_dirs()[2]).get('appsScriptUrl', '')
                            if not apps_script_url:
                                for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'data_schools')):
                                    if 'settings.json' in files:
                                        try:
                                            with open(os.path.join(root, 'settings.json'), 'r', encoding='utf-8') as sf:
                                                g_s = json.load(sf)
                                                if g_s.get('appsScriptUrl'):
                                                    apps_script_url = g_s.get('appsScriptUrl')
                                                    break
                                        except: pass
                            gdrive_folder_link = load_settings(self.get_dirs()[2]).get('googleDriveLink', '')
                            folder_id = extract_gdrive_folder_id(gdrive_folder_link) or ""
                            
                            if apps_script_url:
                                t = threading.Thread(target=bg_delete, args=(safe_name, apps_script_url, folder_id))
                                t.start()
                        except Exception as e:
                            print(f"Error removing physical file {safe_name}: {e}")

                    if user_id:
                        _, _, data_dir = self.get_dirs()
                        user_file = os.path.join(data_dir, f"data_{user_id}.json") if data_dir else "" 
                        if os.path.exists(user_file):
                            try:
                                with open(user_file, 'r', encoding='utf-8') as f:
                                    udata = json.load(f)
                                if 'scores' in udata:
                                    for item_id, item_val in udata['scores'].items():
                                        if isinstance(item_val, dict) and 'uploadedFiles' in item_val:
                                            item_val['uploadedFiles'] = [
                                                uf for uf in item_val['uploadedFiles']
                                                if uf.get('savedName') != safe_name and uf.get('name') != safe_name
                                            ]
                                with open(user_file, 'w', encoding='utf-8') as f:
                                    json.dump(udata, f, ensure_ascii=False, indent=2)
                            except Exception as e:
                                print(f"Error updating user JSON on delete: {e}")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "File berhasil dihapus secara permanen!"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return

        if self.path == '/api/upload':
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                self.send_response(400)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"error","message":"Invalid Content-Type"}')
                return
            
            boundary_str = content_type.split('boundary=')[1].split(';')[0].strip()
            boundary = ('' if boundary_str.startswith('--') else '--') + boundary_str
            boundary_bytes = boundary.encode('utf-8')

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            parts = body.split(boundary_bytes)
            uploaded_files = []

            user_name_prefix = "Umum"
            for part in parts:
                if b'name="username"' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        val = part[header_end+4:].decode('utf-8', errors='ignore').strip()
                        if val:
                            user_name_prefix = val

            for part in parts:
                if b'filename="' in part:
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        headers_text = part[:header_end].decode('utf-8', errors='ignore')
                        content = part[header_end+4:]
                        if content.endswith(b'\r\n'):
                            content = content[:-2]
                        if content.endswith(b'--'):
                            content = content[:-2]

                        m = re.search(r'filename="([^"]+)"', headers_text)
                        if m:
                            orig_filename = os.path.basename(m.group(1))
                            # Fallback if custom_filename not found in earlier parts (which it should be)
                            custom_name = None
                            for p in parts:
                                if b'name="custom_filename"' in p:
                                    hend = p.find(b'\r\n\r\n')
                                    if hend != -1:
                                        raw_val = p[hend+4:]
                                        if raw_val.endswith(b'\r\n'): raw_val = raw_val[:-2]
                                        if raw_val.endswith(b'--'): raw_val = raw_val[:-2]
                                        if raw_val.endswith(b'\r\n'): raw_val = raw_val[:-2]
                                        custom_name = raw_val.decode('utf-8', errors='ignore').strip()
                                        break
                                        
                            unique_name = custom_name if custom_name else orig_filename
                            save_path = os.path.join(self.get_dirs()[1], unique_name)

                            with open(save_path, 'wb') as f:
                                f.write(content)
                                f.flush()
                                os.fsync(f.fileno())

                            file_url = f"/api/pdf-bytes?npsn={self.get_school_npsn()}&file={urllib.parse.quote(unique_name)}"
                            gdrive_folder_link = load_settings(self.get_dirs()[2]).get('googleDriveLink', '')
                            folder_id = extract_gdrive_folder_id(gdrive_folder_link) or ""
                            apps_script_url = load_settings(self.get_dirs()[2]).get('appsScriptUrl', '')
                            if not apps_script_url:
                                for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'data_schools')):
                                    if 'settings.json' in files:
                                        try:
                                            with open(os.path.join(root, 'settings.json'), 'r', encoding='utf-8') as sf:
                                                g_s = json.load(sf)
                                                if g_s.get('appsScriptUrl'):
                                                    apps_script_url = g_s.get('appsScriptUrl')
                                                    break
                                        except: pass
                            
                            if apps_script_url:
                                mime_type = 'application/pdf'
                                if unique_name.lower().endswith(('.png', '.jpg', '.jpeg')): mime_type = 'image/png'
                                t = threading.Thread(target=bg_upload, args=(content, unique_name, mime_type, apps_script_url, user_name_prefix, folder_id))
                                t.start()

                            uploaded_files.append({
                                "originalName": orig_filename,
                                "savedName": unique_name,
                                "url": file_url,
                                "isDrive": False,
                                "folder": PKKS_FOLDER_NAME,
                                "user": user_name_prefix,
                                "size": len(content)
                            })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": f"File berhasil disimpan ke folder {PKKS_FOLDER_NAME}!",
                "files": uploaded_files
            }).encode('utf-8'))
            return

        self.send_response(404)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    os.chdir(BASE_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PKKSRequestHandler) as httpd:
        print("\n" + "="*65)
        print("SISTEM MULTI-USER PKKS SDIT AN-NISA WEB SERVER")
        print(f"Folder Berkas: PKKS 2026 ({UPLOADS_DIR})")
        print(f"Jumlah Akun Guru/Kepsek: {len(load_settings().get('users', []))}")
        print("="*65)
        print(f"Status: Server Aktif & Berjalan!")
        print(f"URL Browser Direct: http://localhost:{PORT}")
        print("="*65 + "\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")
