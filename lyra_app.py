import os
import sqlite3
import asyncio
import urllib.request
import urllib.parse
import keyboard
import random
import sys
import json
import threading
import socket
import winreg as reg
from datetime import datetime
from collections import Counter
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QStackedWidget, QScrollArea, 
                               QFrame, QGridLayout, QGraphicsDropShadowEffect,
                               QSystemTrayIcon, QMenu, QApplication, QGraphicsBlurEffect,
                               QLineEdit, QComboBox, QCheckBox, QTextBrowser, QDialog, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QObject, QPropertyAnimation, QEasingCurve, QTimer, QUrl
from PySide6.QtGui import QPixmap, QImage, QIcon, QColor, QAction, QPainter, QBrush, QDesktopServices
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import soundcard as sc
import soundfile as sf
from shazamio import Shazam

# Discord RPC Entegrasyonu
try:
    from pypresence import Presence
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False

# ==========================================
# 1. ÇOKLU DİL DESTEĞİ
# ==========================================
LANGS = {
    "tr": {
        "nav_home": "◯     Ana Sayfa", "nav_history": "⏱     Geçmiş", "nav_stats": "📊     İstatistikler", "nav_settings": "❖     Ayarlar", "nav_about": "ⓘ     Hakkında",
        "title_home": "Şu an ne çalıyor?", "status_ready": "LYRA algılamaya hazır.",
        "status_sys": "Sistem dinleniyor...", "status_mic": "Ortam dinleniyor...",
        "status_analyzing": "Analiz ediliyor...", "btn_sys": "Bilgisayar Sesi", "btn_mic": "Ortam Mikrofonu",
        "tray_show": "Göster", "tray_quit": "Tamamen Kapat", "res_close": "Kapat",
        "lyrics_title": "Şarkı Sözleri", "lyrics_loading": "Şarkı sözleri aranıyor...",
        "bio_title": "Şarkı & Sanatçı Detayları", "bio_loading": "Detaylar yükleniyor...",
        "rec_title": "Benzer Sanatçı Keşifleri", "rec_empty": "Bu sanatçıya ait başka keşif yok.",
        "btn_preview": "▶ 30sn Önizleme Dinle", "btn_preview_stop": "⏹ Önizlemeyi Durdur",
        "offline_title": "Çevrimdışı Uyarı",
        "offline_msg": "İnternet bağlantısı tespit edilemedi! Şarkı tanıma, sözler ve önizleme özellikleri internet olmadan çalışamayacaktır.",
        "update_title": "Yeni Güncelleme Mevcut!",
        "update_msg": "LYRA'nın yeni bir sürümü yayınlandı. Şimdi indirmek ister misin?",
        "btn_update": "İndir / Güncelle", "btn_later": "Daha Sonra",
        "hist_title": "Geçmiş", "hist_search": "Geçmişte ara...", "hist_clear": "Listeyi Temizle", "hist_empty": "Tarihçe boş.",
        "stats_title": "Dinleme İstatistikleri", "stats_total": "Toplam Keşfedilen Şarkı", 
        "stats_fav": "Favori Şarkılar", "stats_top_artists": "En Çok Dinlenen Sanatçılar",
        "set_title": "Ayarlar", "set_lang": "Uygulama Dili", "lang_btn": "English (Switch)",
        "set_shortcuts": "Klavye Kısayolları (Değiştirilemez)",
        "shortcuts_desc": "🎤 Mikrofon: Ctrl + Shift + M\n🔊 PC Sesi: Ctrl + Shift + P",
        "set_mic": "Aktif Mikrofon Cihazı", "set_speaker": "Aktif Sistem Ses Kaynağı",
        "set_hud": "HUD Mini Pencere (Şarkı Bulunca Göster)",
        "set_startup": "Windows Başlangıcında Otomatik Başlat",
        "set_close_action": "Kapatma Davranışı",
        "close_ask": "Her Zaman Sor", "close_tray": "Arka Plana Al (Tepsi)", "close_quit": "Direkt Kapat",
        "btn_eval": "Değerlendirme Formu", "note_eval": "Uygulamanın gelişmesine katkı sağlamak için değerlendirme formunu doldurabilirsiniz.",
        "btn_bug": "Bug / Error Formu", "note_bug": "Uygulamanın gelişmesine katkı sağlamak için bug/error formunu doldurabilirsiniz.",
        "about_title": "Hakkında & Lisans",
        "about_text": "<h3>LYRA Müzik Tanıma Sistemi</h3>"
                      "<p>Bu açık kaynaklı uygulama <b>loxy_qwe</b> tarafından geliştirilmiş olup <b>MIT Lisansı</b> ile lisanlanmıştır.</p>"
                      "<p>Kaynak kodlarını inceleyebilir, katkı sağlayabilir veya projeyi GitHub üzerinden takip edebilirsiniz.</p>"
                      "<p><b>Sürüm:</b> v1.1</p>",
        "welcome_title": "LYRA'ya Hoş Geldin!",
        "welcome_desc": "Müzik keşif deneyimini zirveye taşıyan asistanın hazır.<br><br>"
                        "• <b>Bilgisayar Sesi</b> ile içerideki çalan şarkıları anında bul.<br>"
                        "• <b>Ortam Mikrofonu</b> ile dışarıdaki müzikleri yakala.<br>"
                        "• <b>Kısayollar:</b> Ctrl+Shift+P (PC) | Ctrl+Shift+M (Mic)",
        "welcome_btn": "Keşfetmeye Başla",
        "tray_msg": "LYRA arka planda çalışmaya devam ediyor.",
        "err_notfound": "Eşleşme bulunamadı.", "err_conn": "Bağlantı hatası veya ses alınamadı."
    },
    "en": {
        "nav_home": "◯     Home", "nav_history": "⏱     History", "nav_stats": "📊     Statistics", "nav_settings": "❖     Settings", "nav_about": "ⓘ     About",
        "title_home": "What's playing?", "status_ready": "LYRA is ready to listen.",
        "status_sys": "Listening to system...", "status_mic": "Listening to mic...",
        "status_analyzing": "Analyzing...", "btn_sys": "System Audio", "btn_mic": "Microphone",
        "tray_show": "Show", "tray_quit": "Quit", "res_close": "Close",
        "lyrics_title": "Lyrics", "lyrics_loading": "Searching for lyrics...",
        "bio_title": "Song & Artist Details", "bio_loading": "Loading details...",
        "rec_title": "Similar Artist Discoveries", "rec_empty": "No other discoveries for this artist.",
        "btn_preview": "▶ Play 30s Preview", "btn_preview_stop": "⏹ Stop Preview",
        "offline_title": "Offline Warning",
        "offline_msg": "No internet connection detected! Song recognition, lyrics, and preview features will not work without internet.",
        "update_title": "New Update Available!",
        "update_msg": "A new version of LYRA has been released. Would you like to download it now?",
        "btn_update": "Download / Update", "btn_later": "Later",
        "hist_title": "History", "hist_search": "Search history...", "hist_clear": "Clear History", "hist_empty": "History is empty.",
        "stats_title": "Listening Statistics", "stats_total": "Total Discovered Songs", 
        "stats_fav": "Favorite Songs", "stats_top_artists": "Top Artists",
        "set_title": "Settings", "set_lang": "Application Language", "lang_btn": "Türkçe (Değiştir)",
        "set_shortcuts": "Global Shortcuts (Fixed)",
        "shortcuts_desc": "🎤 Microphone: Ctrl + Shift + M\n🔊 PC Audio: Ctrl + Shift + P",
        "set_mic": "Active Microphone Device", "set_speaker": "Active System Audio Source",
        "set_hud": "HUD Mini Window (Show on Song Found)",
        "set_startup": "Run Automatically on Windows Startup",
        "set_close_action": "Close Behavior",
        "close_ask": "Always Ask", "close_tray": "Minimize to Tray", "close_quit": "Quit Directly",
        "btn_eval": "Evaluation Form", "note_eval": "You can fill out the evaluation form to contribute to the development of the application.",
        "btn_bug": "Bug / Error Form", "note_bug": "You can fill out the bug/error form to contribute to the development of the application.",
        "about_title": "About & License",
        "about_text": "<h3>LYRA Music Recognition System</h3>"
                      "<p>This open-source application is developed by <b>loxy_qwe</b> and licensed under the <b>MIT License</b>.</p>"
                      "<p>You can inspect the source code, contribute, or follow the project on GitHub.</p>"
                      "<p><b>Version:</b> v1.1</p>",
        "welcome_title": "Welcome to LYRA!",
        "welcome_desc": "Your ultimate music recognition assistant is ready.<br><br>"
                        "• Use <b>System Audio</b> to detect playing songs instantly.<br>"
                        "• Use <b>Microphone</b> to capture ambient music.<br>"
                        "• <b>Shortcuts:</b> Ctrl+Shift+P (PC) | Ctrl+Shift+M (Mic)",
        "welcome_btn": "Start Exploring",
        "tray_msg": "LYRA is running in the background.",
        "err_notfound": "No match found.", "err_conn": "Connection error or no audio."
    }
}

# ==========================================
# 2. TEMA VE STIL
# ==========================================
STYLESHEET = """
* { font-family: 'Segoe UI', sans-serif; }
QMainWindow { background-color: #000000; }
QWidget { color: #FFFFFF; }
QFrame#Sidebar { background-color: #050505; border-right: 1px solid #111111; }
QPushButton#NavBtn { background-color: transparent; border: none; text-align: left; padding: 18px 20px; font-size: 14px; font-weight: 600; color: #555555; border-radius: 12px; letter-spacing: 1px; }
QPushButton#NavBtn:hover { background-color: #0A0A0A; color: #EEEEEE; }
QPushButton#NavBtn:checked { background-color: #111111; color: #FFFFFF; font-weight: 700; border-left: 3px solid #FFFFFF; border-radius: 8px; }
QLabel#TitleText { font-size: 64px; font-weight: 800; letter-spacing: -2px; }
QLabel#SubtitleText { font-size: 18px; font-weight: 400; color: #666666; letter-spacing: 1px; }
QPushButton#BigActionBtn { background-color: #050505; border: 1px solid #151515; border-radius: 30px; font-size: 20px; font-weight: 600; color: #FFFFFF; }
QPushButton#BigActionBtn:hover { background-color: #0A0A0A; border: 1px solid #333333; }
QPushButton#BigActionBtn:pressed { background-color: #FFFFFF; color: #000000; }
QFrame#SongCard { background-color: #050505; border: 1px solid #111111; border-radius: 16px; margin-bottom: 10px; }
QFrame#SongCard:hover { background-color: #0A0A0A; border: 1px solid #222222; }
QLabel#CardTitle { font-size: 18px; font-weight: 700; border: none; }
QLabel#CardArtist { font-size: 14px; color: #777777; border: none; }
QScrollArea { border: none; background-color: transparent; }
QScrollArea > QWidget > QWidget { background-color: transparent; }
QScrollBar:vertical { background: #000000; width: 4px; margin: 0px; }
QScrollBar::handle:vertical { background: #222222; border-radius: 2px; min-height: 40px; }
QPushButton#ActionLinkBtn { background-color: #111; border: 1px solid #333; border-radius: 20px; padding: 12px 25px; font-size: 15px; font-weight: bold; }
QPushButton#ActionLinkBtn:hover { background-color: #222; border: 1px solid #555; }
QComboBox { background-color: #0A0A0A; border: 1px solid #222; border-radius: 8px; padding: 8px 12px; font-size: 14px; color: #FFF; }
QComboBox::drop-down { border: 0px; }
QComboBox QAbstractItemView { background-color: #0A0A0A; color: #FFF; selection-background-color: #222; }
QCheckBox { font-size: 16px; color: #FFF; spacing: 10px; }
QCheckBox::indicator { width: 20px; height: 20px; background-color: #0A0A0A; border: 1px solid #333; border-radius: 4px; }
QCheckBox::indicator:checked { background-color: #FFF; border: 1px solid #FFF; }

QMessageBox { background-color: #111111; }
QMessageBox QLabel { color: #FFFFFF; background-color: transparent; font-size: 14px; }
QMessageBox QPushButton { background-color: #222222; color: #FFFFFF; border: 1px solid #444444; border-radius: 6px; padding: 6px 16px; min-width: 80px; font-weight: bold; }
QMessageBox QPushButton:hover { background-color: #333333; }
"""

# ==========================================
# 3. VERITABANI YONETIMI (Thread-Safe SQLite)
# ==========================================
class DBManager:
    def __init__(self):
        app_data = os.path.join(os.environ.get('APPDATA', ''), 'LYRA')
        os.makedirs(app_data, exist_ok=True)
        db_path = os.path.join(app_data, 'lyra_data.db')
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.db_lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.db_lock:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                track_id TEXT UNIQUE, 
                title TEXT, 
                artist TEXT, 
                album TEXT, 
                cover_url TEXT, 
                timestamp TEXT, 
                is_favorite INTEGER DEFAULT 0, 
                preview_url TEXT,
                genre TEXT,
                shazam_count INTEGER DEFAULT 0,
                artist_bio TEXT
            )''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
            self.conn.commit()
            
            for col, col_def in [
                ("shazam_count", "INTEGER DEFAULT 0"),
                ("artist_bio", "TEXT"),
                ("genre", "TEXT"),
                ("preview_url", "TEXT")
            ]:
                try:
                    self.cursor.execute(f"ALTER TABLE songs ADD COLUMN {col} {col_def}")
                    self.conn.commit()
                except sqlite3.OperationalError:
                    pass

            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('lang', 'tr')")
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('selected_mic', 'default')")
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('selected_speaker', 'default')")
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('hud_enabled', 'true')")
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('startup_enabled', 'false')")
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('close_action', 'ask')")
            self.cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('first_run', 'true')")
            self.conn.commit()

    def add_song(self, song_data):
        with self.db_lock:
            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute('''INSERT INTO songs (track_id, title, artist, album, cover_url, timestamp, is_favorite, preview_url, genre, shazam_count, artist_bio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(track_id) DO UPDATE SET timestamp=excluded.timestamp, preview_url=excluded.preview_url, genre=excluded.genre, shazam_count=excluded.shazam_count, artist_bio=excluded.artist_bio''', 
                                (song_data['id'], song_data['title'], song_data['artist'], song_data.get('album', ''), song_data.get('cover_url', ''), timestamp_str, 0, song_data.get('preview_url', ''), song_data.get('genre', 'Genel'), song_data.get('shazam_count', 0), song_data.get('artist_bio', '')))
            self.conn.commit()

    def get_setting(self, key):
        with self.db_lock:
            self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
            res = self.cursor.fetchone()
            return res[0] if res else None

    def set_setting(self, key, value):
        with self.db_lock:
            self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            self.conn.commit()

    def toggle_favorite(self, track_id, is_fav):
        with self.db_lock:
            self.cursor.execute('UPDATE songs SET is_favorite = ? WHERE track_id = ?', (1 if is_fav else 0, track_id))
            self.conn.commit()

    def get_history(self):
        with self.db_lock:
            self.cursor.execute('SELECT * FROM songs ORDER BY timestamp DESC')
            return self.cursor.fetchall()

    def clear_history(self):
        with self.db_lock:
            self.cursor.execute('DELETE FROM songs WHERE is_favorite = 0')
            self.conn.commit()

    def get_stats(self):
        with self.db_lock:
            self.cursor.execute("SELECT count(*) FROM songs")
            total = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT count(*) FROM songs WHERE is_favorite = 1")
            favs = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT artist, count(*) as c FROM songs GROUP BY artist ORDER BY c DESC LIMIT 5")
            top_artists = self.cursor.fetchall()
            return total, favs, top_artists

db = DBManager()

# ==========================================
# 4. ASYNC SES & HIZLI TANIMA MOTORU
# ==========================================
class RecognitionSignals(QObject):
    status_changed = Signal(str)
    finished = Signal(dict)
    error = Signal(str)

class AudioRecognizer:
    def __init__(self):
        self.signals = RecognitionSignals()
        self.shazam = Shazam()
        self.is_recording = False
        
        app_data = os.path.join(os.environ.get('APPDATA', ''), 'LYRA')
        os.makedirs(app_data, exist_ok=True)
        self.temp_wav = os.path.join(app_data, 'temp_lyra.wav')

    def _record_chunk(self, is_system, duration=3.2):
        try:
            mic = None
            if is_system:
                sel_id = db.get_setting("selected_speaker")
                loopback_mics = sc.all_microphones(include_loopback=True)
                
                if sel_id and sel_id != "default":
                    try:
                        speaker = sc.get_speaker(id=sel_id)
                        for m in loopback_mics:
                            if speaker.name in m.name or m.name in speaker.name:
                                mic = m
                                break
                    except Exception:
                        pass
                
                if not mic:
                    try:
                        default_spk = sc.default_speaker()
                        for m in loopback_mics:
                            if default_spk.name in m.name or m.name in default_spk.name:
                                mic = m
                                break
                    except Exception:
                        pass
                
                if not mic and loopback_mics:
                    mic = loopback_mics[0]
            else:
                sel_id = db.get_setting("selected_mic")
                if sel_id and sel_id != "default":
                    try:
                        mic = sc.get_microphone(id=sel_id)
                    except Exception:
                        mic = sc.default_microphone()
                else:
                    mic = sc.default_microphone()
            
            if not mic:
                return "Ses cihazı bulunamadı."
            
            with mic.recorder(samplerate=44100) as m:
                data = m.record(numframes=int(44100 * duration))
            
            if data is None or len(data) == 0:
                return "Ses verisi alınamadı."
                
            mono_data = data[:, 0] if len(data.shape) > 1 else data
            sf.write(self.temp_wav, mono_data, 44100)
            return True
        except Exception as e:
            return str(e)

    async def start_recognition(self, is_system=True, lang="tr"):
        if self.is_recording: return
        self.is_recording = True
        
        try:
            mode_text = LANGS[lang]["status_sys"] if is_system else LANGS[lang]["status_mic"]
            self.signals.status_changed.emit(mode_text)
            
            match_found = False
            for attempt in range(2):
                rec_result = await asyncio.to_thread(self._record_chunk, is_system, 3.2)
                if rec_result is not True:
                    self.signals.error.emit(LANGS[lang]["err_conn"])
                    self.is_recording = False
                    return

                if attempt == 0:
                    self.signals.status_changed.emit(LANGS[lang]["status_analyzing"])

                try:
                    out = await self.shazam.recognize(self.temp_wav)
                    if out and 'track' in out:
                        t = out['track']
                        track_id = t.get('key', '')
                        artist_name = t.get('subtitle', 'Unknown')
                        song_title = t.get('title', 'Unknown')
                        
                        shazam_count = 0
                        try:
                            count_res = await self.shazam.listening_counter(track_id=track_id)
                            if isinstance(count_res, dict):
                                shazam_count = count_res.get('counter', 0)
                            elif isinstance(count_res, int):
                                shazam_count = count_res
                        except:
                            pass

                        preview_url = ""
                        try:
                            if 'hub' in t and 'actions' in t['hub']:
                                for action in t['hub']['actions']:
                                    if 'uri' in action and action['uri'].endswith(('.mp3', '.aac', '.m4a', 'preview')):
                                        preview_url = action['uri']
                                        break
                            if not preview_url and 'preview' in t:
                                preview_url = t['preview']
                        except:
                            pass

                        genre = "Genel"
                        try:
                            if 'genres' in t and 'primary' in t['genres']:
                                genre = t['genres']['primary']
                        except:
                            pass

                        artist_bio = f"<b>Sanatçı:</b> {artist_name}<br><b>Şarkı:</b> {song_title}"
                        try:
                            sections = t.get('sections', [])
                            meta_items = []
                            for section in sections:
                                if 'metadata' in section:
                                    for meta in section['metadata']:
                                        m_title = meta.get('title', '')
                                        m_text = meta.get('text', '')
                                        if m_title and m_text:
                                            meta_items.append(f"<b>{m_title}:</b> {m_text}")
                            if meta_items:
                                artist_bio = "<br>".join(meta_items)
                        except:
                            pass

                        result = {
                            'id': str(track_id),
                            'title': song_title,
                            'artist': artist_name,
                            'album': t.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', ''),
                            'cover_url': t.get('images', {}).get('coverarthq', ''),
                            'preview_url': preview_url,
                            'genre': genre,
                            'shazam_count': shazam_count,
                            'artist_bio': artist_bio
                        }
                        db.add_song(result)
                        self.signals.finished.emit(result)
                        match_found = True
                        break
                except Exception:
                    pass
            
            if not match_found:
                self.signals.error.emit(LANGS[lang]["err_notfound"])

        except Exception:
            self.signals.error.emit(LANGS[lang]["err_conn"])
        finally:
            self.is_recording = False
            if os.path.exists(self.temp_wav):
                try: os.remove(self.temp_wav)
                except: pass

# ==========================================
# 5. UI BİLEŞENLERİ VE YARDIMCI SINIFLAR
# ==========================================
class ClickableCard(QFrame):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(440, 360)
        self.selected_lang = "tr"
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        frame = QFrame(self)
        frame.setStyleSheet("background-color: rgba(10, 10, 10, 245); border: 1px solid #222; border-radius: 20px;")
        f_layout = QVBoxLayout(frame)
        f_layout.setContentsMargins(30, 30, 30, 30)
        f_layout.setSpacing(15)
        
        lang_layout = QHBoxLayout()
        self.btn_tr = QPushButton("🇹🇷 Türkçe")
        self.btn_tr.setStyleSheet("QPushButton { background-color: #222; color: #FFF; border-radius: 8px; padding: 8px; font-size: 13px; font-weight: bold; border: 1px solid #444; } QPushButton:hover { background-color: #333; }")
        self.btn_tr.clicked.connect(lambda: self.set_language("tr"))
        
        self.btn_en = QPushButton("🇬🇧 English")
        self.btn_en.setStyleSheet("QPushButton { background-color: #111; color: #888; border-radius: 8px; padding: 8px; font-size: 13px; font-weight: bold; border: 1px solid #222; } QPushButton:hover { background-color: #222; }")
        self.btn_en.clicked.connect(lambda: self.set_language("en"))
        
        lang_layout.addWidget(self.btn_tr)
        lang_layout.addWidget(self.btn_en)
        f_layout.addLayout(lang_layout)
        
        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFF; border: none;")
        
        self.desc_lbl = QLabel()
        self.desc_lbl.setStyleSheet("font-size: 14px; color: #AAA; border: none;")
        self.desc_lbl.setWordWrap(True)
        
        self.btn_start = QPushButton()
        self.btn_start.setStyleSheet("QPushButton { background-color: #FFF; color: #000; border-radius: 12px; padding: 12px; font-size: 15px; font-weight: bold; } QPushButton:hover { background-color: #DDD; }")
        self.btn_start.clicked.connect(self.accept)
        
        f_layout.addWidget(self.title_lbl)
        f_layout.addWidget(self.desc_lbl)
        f_layout.addStretch()
        f_layout.addWidget(self.btn_start)
        
        layout.addWidget(frame)
        self.update_texts()

    def set_language(self, lang):
        self.selected_lang = lang
        if lang == "tr":
            self.btn_tr.setStyleSheet("QPushButton { background-color: #222; color: #FFF; border-radius: 8px; padding: 8px; font-size: 13px; font-weight: bold; border: 1px solid #444; }")
            self.btn_en.setStyleSheet("QPushButton { background-color: #111; color: #888; border-radius: 8px; padding: 8px; font-size: 13px; font-weight: bold; border: 1px solid #222; }")
        else:
            self.btn_en.setStyleSheet("QPushButton { background-color: #222; color: #FFF; border-radius: 8px; padding: 8px; font-size: 13px; font-weight: bold; border: 1px solid #444; }")
            self.btn_tr.setStyleSheet("QPushButton { background-color: #111; color: #888; border-radius: 8px; padding: 8px; font-size: 13px; font-weight: bold; border: 1px solid #222; }")
        self.update_texts()

    def update_texts(self):
        t = LANGS[self.selected_lang]
        self.title_lbl.setText(t["welcome_title"])
        self.desc_lbl.setText(t["welcome_desc"])
        self.btn_start.setText(t["welcome_btn"])

class CloseDialog(QDialog):
    def __init__(self, lang="tr", parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(420, 260)
        self.choice = None
        self.remember = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        frame = QFrame(self)
        frame.setStyleSheet("background-color: rgba(10, 10, 10, 245); border: 1px solid #222; border-radius: 20px;")
        f_layout = QVBoxLayout(frame)
        f_layout.setContentsMargins(25, 25, 25, 25)
        f_layout.setSpacing(15)
        
        title_text = "Uygulama Kapatılsın mı?" if lang == "tr" else "Close Application?"
        self.title_lbl = QLabel(title_text)
        self.title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFF; border: none;")
        
        desc_text = "Uygulamayı kapatmak istediğinizde ne yapılsın? Arka planda çalışmaya devam edebilir veya tamamen kapatabilirsiniz." if lang == "tr" else "What would you like to do when closing the app? It can run in the background or quit completely."
        self.desc_lbl = QLabel(desc_text)
        self.desc_lbl.setStyleSheet("font-size: 13px; color: #AAA; border: none;")
        self.desc_lbl.setWordWrap(True)
        
        self.chk_remember = QCheckBox("Seçimimi hatırla" if lang == "tr" else "Remember my choice")
        self.chk_remember.setStyleSheet("font-size: 14px; color: #DDD;")
        
        btn_layout = QHBoxLayout()
        self.btn_tray = QPushButton("Arka Plana Al" if lang == "tr" else "Minimize to Tray")
        self.btn_tray.setStyleSheet("QPushButton { background-color: #222; color: #FFF; border-radius: 10px; padding: 10px; font-size: 13px; font-weight: bold; border: 1px solid #444; } QPushButton:hover { background-color: #333; }")
        self.btn_tray.clicked.connect(self.select_tray)
        
        self.btn_quit = QPushButton("Direkt Kapat" if lang == "tr" else "Quit Completely")
        self.btn_quit.setStyleSheet("QPushButton { background-color: #FFF; color: #000; border-radius: 10px; padding: 10px; font-size: 13px; font-weight: bold; } QPushButton:hover { background-color: #DDD; }")
        self.btn_quit.clicked.connect(self.select_quit)
        
        btn_layout.addWidget(self.btn_tray)
        btn_layout.addWidget(self.btn_quit)
        
        f_layout.addWidget(self.title_lbl)
        f_layout.addWidget(self.desc_lbl)
        f_layout.addWidget(self.chk_remember)
        f_layout.addSpacing(10)
        f_layout.addLayout(btn_layout)
        
        layout.addWidget(frame)

    def select_tray(self):
        self.choice = 'tray'
        self.remember = self.chk_remember.isChecked()
        self.accept()

    def select_quit(self):
        self.choice = 'quit'
        self.remember = self.chk_remember.isChecked()
        self.accept()

class WaveformVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(320, 70)
        self.bars = [random.randint(10, 45) for _ in range(18)]
        self.is_active = False
        self.accent_color = QColor(255, 255, 255)
        
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.update_bars)

    def start(self):
        self.is_active = True
        self.timer.start()
        self.show()

    def stop(self):
        self.is_active = False
        self.timer.stop()
        self.hide()

    def set_accent_color(self, color: QColor):
        self.accent_color = color
        self.update()

    def update_bars(self):
        if self.is_active:
            self.bars = [random.randint(12, 62) for _ in range(18)]
            self.update()

    def paintEvent(self, event):
        if not self.is_active:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.accent_color))
        painter.setPen(Qt.NoPen)
        
        bar_width = 10
        spacing = 6
        start_x = (self.width() - (len(self.bars) * (bar_width + spacing))) / 2
        
        for i, h in enumerate(self.bars):
            x = start_x + i * (bar_width + spacing)
            y = (self.height() - h) / 2
            painter.drawRoundedRect(int(x), int(y), bar_width, h, 5, 5)

class ImageLoader(QObject):
    image_loaded = Signal(QPixmap)
    
    def load_image(self, url):
        if not url: return
        threading.Thread(target=self._fetch, args=(url,), daemon=True).start()

    def _fetch(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                image = QImage()
                image.loadFromData(data)
                self.image_loaded.emit(QPixmap(image))
        except:
            pass

class LyricsLoader(QObject):
    lyrics_loaded = Signal(str)

    def load_lyrics(self, title, artist, lang):
        threading.Thread(target=self._fetch, args=(title, artist, lang), daemon=True).start()

    def _fetch(self, title, artist, lang):
        try:
            query = urllib.parse.urlencode({"track_name": title, "artist_name": artist})
            url = f"https://lrclib.net/api/search?{query}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'LYRA-App'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and len(data) > 0:
                    lyrics = data[0].get('plainLyrics') or data[0].get('syncedLyrics')
                    if lyrics:
                        self.lyrics_loaded.emit(lyrics)
                        return
                        
            msg = "Bu şarkı için söz bulunamadı." if lang == "tr" else "No lyrics found for this song."
            self.lyrics_loaded.emit(msg)
        except Exception:
            msg = "Şarkı sözleri yüklenemedi." if lang == "tr" else "Failed to load lyrics."
            self.lyrics_loaded.emit(msg)

class HUDWidget(QWidget):
    def __init__(self, song_data, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(360, 95)
        self.song_data = song_data
        
        screen_geo = QApplication.primaryScreen().availableGeometry()
        self.move(screen_geo.width() - 380, screen_geo.height() - 130)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: rgba(10, 10, 10, 245); border: 1px solid #333; border-radius: 16px;")
        f_layout = QHBoxLayout(self.frame)
        f_layout.setContentsMargins(12, 12, 12, 12)
        f_layout.setSpacing(12)
        
        self.cover_lbl = QLabel()
        self.cover_lbl.setFixedSize(65, 65)
        self.cover_lbl.setStyleSheet("background-color: #111; border-radius: 8px;")
        self.cover_lbl.setScaledContents(True)
        f_layout.addWidget(self.cover_lbl)
        
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignVCenter)
        text_layout.setSpacing(2)
        self.title_lbl = QLabel(song_data['title'])
        self.title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFF; border: none;")
        self.artist_lbl = QLabel(song_data['artist'])
        self.artist_lbl.setStyleSheet("font-size: 12px; color: #aaa; border: none;")
        text_layout.addWidget(self.title_lbl)
        text_layout.addWidget(self.artist_lbl)
        f_layout.addLayout(text_layout)
        f_layout.addStretch()
        
        action_layout = QVBoxLayout()
        action_layout.setSpacing(4)
        
        self.is_fav = False
        try:
            with db.db_lock:
                db.cursor.execute("SELECT is_favorite FROM songs WHERE track_id=?", (song_data['id'],))
                res = db.cursor.fetchone()
                if res and res[0] == 1:
                    self.is_fav = True
        except:
            pass
            
        self.fav_btn = QPushButton("♥" if self.is_fav else "♡")
        self.fav_btn.setFixedSize(28, 28)
        self.fav_btn.setStyleSheet("QPushButton { background-color: transparent; color: #FF4444; border: none; font-size: 16px; font-weight: bold; } QPushButton:hover { color: #ff6666; }")
        self.fav_btn.setToolTip("Favorilere Ekle / Çıkar")
        self.fav_btn.clicked.connect(self.toggle_fav)
        
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(28, 28)
        self.copy_btn.setStyleSheet("QPushButton { background-color: transparent; color: #aaa; border: none; font-size: 14px; } QPushButton:hover { color: #FFF; }")
        self.copy_btn.setToolTip("Şarkı Bilgisini Kopyala")
        self.copy_btn.clicked.connect(self.copy_song_info)
        
        action_layout.addWidget(self.fav_btn)
        action_layout.addWidget(self.copy_btn)
        f_layout.addLayout(action_layout)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(22, 22)
        self.close_btn.setStyleSheet("QPushButton { background-color: transparent; color: #777; border: none; font-size: 16px; font-weight: bold; } QPushButton:hover { color: #FFF; }")
        self.close_btn.clicked.connect(self.close)
        f_layout.addWidget(self.close_btn, alignment=Qt.AlignTop)
        
        layout.addWidget(self.frame)
        
        self.loader = ImageLoader()
        self.loader.image_loaded.connect(self.cover_lbl.setPixmap)
        self.loader.load_image(song_data['cover_url'])
        
        self.show()

    def toggle_fav(self):
        self.is_fav = not self.is_fav
        db.toggle_favorite(self.song_data['id'], self.is_fav)
        self.fav_btn.setText("♥" if self.is_fav else "♡")

    def copy_song_info(self):
        try:
            text = f"{self.song_data['title']} - {self.song_data['artist']}"
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(text)
                self.copy_btn.setText("✓")
                QTimer.singleShot(1500, lambda: self.copy_btn.setText("📋"))
        except Exception:
            pass

class SongCard(QFrame):
    def __init__(self, song_data, parent_refresh_cb=None):
        super().__init__()
        self.song_data = song_data
        self.refresh_cb = parent_refresh_cb
        self.setObjectName("SongCard")
        self.setFixedHeight(110)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(25)
        
        self.cover_lbl = QLabel()
        self.cover_lbl.setFixedSize(70, 70)
        self.cover_lbl.setStyleSheet("background-color: #111; border-radius: 8px;")
        self.cover_lbl.setScaledContents(True)
        layout.addWidget(self.cover_lbl)
        
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignVCenter)
        title_lbl = QLabel(song_data[2])
        title_lbl.setObjectName("CardTitle")
        
        genre = song_data[9] if len(song_data) > 9 and song_data[9] else 'Genel'
        count = song_data[10] if len(song_data) > 10 and song_data[10] else 0
        
        count_str = f"  •  <span style='color: #888;'>🔥 {count:,} Shazamed</span>" if count > 0 else ""
        artist_lbl = QLabel(f"{song_data[3]}  •  <span style='color: #33CCFF;'>{genre}</span>{count_str}")
        artist_lbl.setObjectName("CardArtist")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(artist_lbl)
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.fav_btn = QPushButton("♥" if song_data[7] else "♡")
        self.fav_btn.setFixedSize(50, 50)
        self.fav_btn.setStyleSheet("font-size: 26px; background-color: transparent; border: none; color: #FFF;")
        self.fav_btn.clicked.connect(self.toggle_fav)
        layout.addWidget(self.fav_btn)

        self.loader = ImageLoader()
        self.loader.image_loaded.connect(self.cover_lbl.setPixmap)
        self.loader.load_image(song_data[5])

    def toggle_fav(self):
        is_fav = not self.song_data[7]
        db.toggle_favorite(self.song_data[1], is_fav)
        self.song_data = list(self.song_data)
        self.song_data[7] = 1 if is_fav else 0
        self.fav_btn.setText("♥" if self.song_data[7] else "♡")
        if self.refresh_cb: self.refresh_cb()

class KeySignals(QObject):
    sys_trigger = Signal()
    mic_trigger = Signal()

# ==========================================
# 6. ANA PENCERE
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LYRA v1.1")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(STYLESHEET)
        
        self.lang = db.get_setting("lang") or "tr"
        self.history_filter_mode = "all"
        self.recognizer = AudioRecognizer()
        self.recognizer.signals.status_changed.connect(self.update_status)
        self.recognizer.signals.finished.connect(self.show_result)
        self.recognizer.signals.error.connect(self.show_error)
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(0.35)
        self.media_player.setAudioOutput(self.audio_output)
        self.current_preview_url = ""

        self.hud_window = None
        self.setup_discord_rpc()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setup_sidebar(main_layout)
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages, 1)

        self.page_home = self.create_home_page()
        self.page_result = self.create_result_page()
        self.page_history = self.create_history_page()
        self.page_stats = self.create_stats_page()
        self.page_settings = self.create_settings_page()
        self.page_about = self.create_about_page()

        self.pages.addWidget(self.page_home)
        self.pages.addWidget(self.page_result)
        self.pages.addWidget(self.page_history)
        self.pages.addWidget(self.page_stats)
        self.pages.addWidget(self.page_settings)
        self.pages.addWidget(self.page_about)

        self.setup_tray()
        self.setup_global_shortcuts()
        self.apply_language()

        QTimer.singleShot(500, self.check_first_run_and_internet)
        QTimer.singleShot(2000, self.check_for_updates) # Otomatik Güncelleme Kontrolü

    def check_internet_connection(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    def check_for_updates(self):
        """Arka planda GitHub repositorinden güncellemeleri kontrol eder"""
        def _task():
            try:
                # Senin repository'ne göre ayarlandı: loxy-qwe/lyra-app
                update_url = "https://raw.githubusercontent.com/loxy-qwe/lyra-app/main/version.json"
                req = urllib.request.Request(update_url, headers={'User-Agent': 'LYRA-App'})
                with urllib.request.urlopen(req, timeout=3) as res:
                    data = json.loads(res.read().decode('utf-8'))
                    remote_version = data.get("version", "1.1")
                    download_url = data.get("url", "https://github.com/loxy-qwe/lyra-app/releases")
                    
                    if remote_version != "1.1": 
                        QTimer.singleShot(0, lambda: self.show_update_dialog(remote_version, download_url))
            except:
                pass
        threading.Thread(target=_task, daemon=True).start()

    def show_update_dialog(self, new_ver, dl_url):
        t = LANGS[self.lang]
        box = QMessageBox(self)
        box.setWindowTitle(t["update_title"])
        box.setText(f"{t['update_msg']}\n\n<b>Mevcut Sürüm:</b> v1.1<br><b>Yeni Sürüm:</b> v{new_ver}")
        btn_update = box.addButton(t["btn_update"], QMessageBox.AcceptRole)
        btn_later = box.addButton(t["btn_later"], QMessageBox.RejectRole)
        box.exec()
        
        if box.clickedButton() == btn_update:
            QDesktopServices.openUrl(QUrl(dl_url))

    def check_first_run_and_internet(self):
        if not self.check_internet_connection():
            t = LANGS[self.lang]
            QMessageBox.warning(self, t["offline_title"], t["offline_msg"])

        if db.get_setting("first_run") == "true":
            dlg = WelcomeDialog(self)
            if dlg.exec() == QDialog.Accepted:
                self.lang = dlg.selected_lang
                db.set_setting("lang", self.lang)
                db.set_setting("first_run", "false")
                self.apply_language()

    def setup_discord_rpc(self):
        self.rpc = None
        if DISCORD_AVAILABLE:
            try:
                client_id = "YOUR_DISCORD_CLIENT_ID"
                if client_id != "YOUR_DISCORD_CLIENT_ID":
                    self.rpc = Presence(client_id)
                    self.rpc.connect()
            except Exception:
                self.rpc = None

    def update_discord_presence(self, title, artist):
        if self.rpc:
            try:
                self.rpc.update(
                    details=f"Dinliyor: {title}",
                    state=f"Sanatçı: {artist}",
                    large_image="logo",
                    large_text="LYRA App",
                    start=int(datetime.now().timestamp())
                )
            except Exception:
                pass

    def setup_tray(self):
        if os.path.exists("logo.png"):
            tray_icon_obj = QIcon("logo.png")
        else:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(255, 255, 255))
            tray_icon_obj = QIcon(pixmap)

        self.tray_icon = QSystemTrayIcon(tray_icon_obj, self)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_menu = QMenu()
        
        self.act_show = QAction("Göster", self)
        self.act_show.triggered.connect(self.restore_window_state)
        self.act_quit = QAction("Çıkış", self)
        self.act_quit.triggered.connect(self.force_quit_app)
        
        self.tray_menu.addAction(self.act_show)
        self.tray_menu.addAction(self.act_quit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.hide()
            else:
                self.restore_window_state()

    def restore_window_state(self):
        if self.isMaximized():
            self.showMaximized()
        else:
            self.show()
        self.activateWindow()

    def closeEvent(self, event):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()

        if hasattr(self, 'real_quit') and self.real_quit:
            if self.rpc:
                try: self.rpc.close()
                except: pass
            event.accept()
            return

        action = db.get_setting("close_action") or "ask"

        if action == "tray":
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("LYRA", LANGS[self.lang]["tray_msg"], QSystemTrayIcon.Information, 2000)
        elif action == "quit":
            self.real_quit = True
            if self.rpc:
                try: self.rpc.close()
                except: pass
            event.accept()
        else:
            dlg = CloseDialog(self.lang, self)
            if dlg.exec() == QDialog.Accepted:
                if dlg.choice == 'tray':
                    if dlg.remember:
                        db.set_setting("close_action", "tray")
                    event.ignore()
                    self.hide()
                    self.tray_icon.showMessage("LYRA", LANGS[self.lang]["tray_msg"], QSystemTrayIcon.Information, 2000)
                elif dlg.choice == 'quit':
                    if dlg.remember:
                        db.set_setting("close_action", "quit")
                    self.real_quit = True
                    if self.rpc:
                        try: self.rpc.close()
                        except: pass
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()

    def force_quit_app(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()
        if self.rpc:
            try: self.rpc.close()
            except: pass
        self.real_quit = True
        QApplication.quit()

    def setup_global_shortcuts(self):
        self.key_sigs = KeySignals()
        self.key_sigs.sys_trigger.connect(lambda: self.trigger_from_shortcut(True))
        self.key_sigs.mic_trigger.connect(lambda: self.trigger_from_shortcut(False))
        keyboard.add_hotkey('ctrl+shift+p', self.key_sigs.sys_trigger.emit)
        keyboard.add_hotkey('ctrl+shift+m', self.key_sigs.mic_trigger.emit)

    def trigger_from_shortcut(self, is_sys):
        threading.Thread(target=lambda: asyncio.run(self.recognizer.start_recognition(is_system=is_sys, lang=self.lang)), daemon=True).start()

    def setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(25, 40, 25, 40)
        
        logo_label = QLabel()
        logo_label.setFixedSize(50, 50)
        logo_label.setScaledContents(True)
        if os.path.exists("logo.png"):
            logo_label.setPixmap(QPixmap("logo.png"))
        else:
            logo_label.setText("LYRA")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            
        layout.addWidget(logo_label)
        layout.addSpacing(30)

        self.btn_home = QPushButton()
        self.btn_history = QPushButton()
        self.btn_stats = QPushButton()
        self.btn_settings = QPushButton()
        self.btn_about = QPushButton()
        
        self.btn_home.clicked.connect(lambda checked=False: self.switch_page(0, self.btn_home))
        self.btn_history.clicked.connect(lambda checked=False: self.goto_history('all'))
        self.btn_stats.clicked.connect(lambda checked=False: self.switch_page(3, self.btn_stats))
        self.btn_settings.clicked.connect(lambda checked=False: self.switch_page(4, self.btn_settings))
        self.btn_about.clicked.connect(lambda checked=False: self.switch_page(5, self.btn_about))

        for btn in [self.btn_home, self.btn_history, self.btn_stats, self.btn_settings, self.btn_about]:
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            layout.addWidget(btn)
            
        self.btn_home.setChecked(True)
        layout.addStretch()
        parent_layout.addWidget(sidebar)

    def goto_history(self, mode="all"):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            if hasattr(self, 'btn_preview'):
                self.btn_preview.setText(LANGS[self.lang]["btn_preview"])

        self.history_filter_mode = mode
        if hasattr(self, 'search_input'):
            self.search_input.blockSignals(True)
            self.search_input.clear()
            self.search_input.blockSignals(False)
        self.switch_page(2, self.btn_history)

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        self.lbl_home_title = QLabel()
        self.lbl_home_title.setObjectName("TitleText")
        self.lbl_home_title.setAlignment(Qt.AlignCenter)
        
        self.status_label = QLabel()
        self.status_label.setObjectName("SubtitleText")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.visualizer = WaveformVisualizer()
        self.visualizer.hide()

        self.pulse_anim = QPropertyAnimation(self.status_label, b"windowOpacity")
        self.pulse_anim.setDuration(1000)
        self.pulse_anim.setStartValue(1.0)
        self.pulse_anim.setEndValue(0.3)
        self.pulse_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.pulse_anim.setLoopCount(-1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)

        self.sys_btn = QPushButton()
        self.sys_btn.setObjectName("BigActionBtn")
        self.sys_btn.setFixedSize(280, 280)
        self.sys_btn.clicked.connect(lambda: threading.Thread(target=lambda: asyncio.run(self.recognizer.start_recognition(True, self.lang)), daemon=True).start())

        self.mic_btn = QPushButton()
        self.mic_btn.setObjectName("BigActionBtn")
        self.mic_btn.setFixedSize(280, 280)
        self.mic_btn.clicked.connect(lambda: threading.Thread(target=lambda: asyncio.run(self.recognizer.start_recognition(False, self.lang)), daemon=True).start())

        btn_layout.addStretch()
        btn_layout.addWidget(self.sys_btn)
        btn_layout.addWidget(self.mic_btn)
        btn_layout.addStretch()

        layout.addStretch()
        layout.addWidget(self.lbl_home_title)
        layout.addSpacing(10)
        layout.addWidget(self.status_label)
        layout.addSpacing(15)
        layout.addWidget(self.visualizer, alignment=Qt.AlignCenter)
        layout.addSpacing(40)
        layout.addLayout(btn_layout)
        layout.addStretch()
        return page

    def create_result_page(self):
        page = QWidget()
        main_grid = QGridLayout(page)
        main_grid.setContentsMargins(0, 0, 0, 0)
        
        self.res_bg_lbl = QLabel()
        self.res_bg_lbl.setScaledContents(True)
        bg_blur = QGraphicsBlurEffect()
        bg_blur.setBlurRadius(100)
        self.res_bg_lbl.setGraphicsEffect(bg_blur)
        
        self.res_overlay = QLabel()
        self.res_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 225);")
        
        fg_widget = QWidget()
        main_h_layout = QHBoxLayout(fg_widget)
        main_h_layout.setAlignment(Qt.AlignCenter)
        main_h_layout.setSpacing(40)
        
        # SOL KOLON
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setAlignment(Qt.AlignCenter)
        
        cover_container = QFrame()
        cover_container.setFixedSize(260, 260)
        cover_layout = QVBoxLayout(cover_container)
        cover_layout.setContentsMargins(0,0,0,0)
        
        self.res_cover = QLabel()
        self.res_cover.setFixedSize(260, 260)
        self.res_cover.setStyleSheet("background-color: #0A0A0A; border-radius: 16px;")
        self.res_cover.setScaledContents(True)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        self.res_cover.setGraphicsEffect(shadow)
        cover_layout.addWidget(self.res_cover)
        
        self.res_title = QLabel()
        self.res_title.setStyleSheet("font-size: 26px; font-weight: bold; margin-top: 10px; border: none;")
        self.res_title.setAlignment(Qt.AlignCenter)
        self.res_title.setWordWrap(True)
        
        self.res_artist = QLabel()
        self.res_artist.setStyleSheet("font-size: 15px; color: #AAA; border: none;")
        self.res_artist.setAlignment(Qt.AlignCenter)
        
        self.res_genre = QLabel()
        self.res_genre.setStyleSheet("font-size: 13px; color: #33CCFF; border: none; font-weight: bold;")
        self.res_genre.setAlignment(Qt.AlignCenter)

        self.res_counter = QLabel()
        self.res_counter.setStyleSheet("font-size: 12px; color: #888; border: none; margin-top: 2px;")
        self.res_counter.setAlignment(Qt.AlignCenter)
        self.res_counter.hide()
        
        links_layout = QHBoxLayout()
        self.btn_spotify = QPushButton("Spotify")
        self.btn_spotify.setObjectName("ActionLinkBtn")
        self.btn_spotify.setStyleSheet("color: #1DB954;")
        
        self.btn_youtube = QPushButton("YouTube")
        self.btn_youtube.setObjectName("ActionLinkBtn")
        self.btn_youtube.setStyleSheet("color: #FF0000;")
        
        links_layout.addWidget(self.btn_spotify)
        links_layout.addWidget(self.btn_youtube)

        self.btn_preview = QPushButton()
        self.btn_preview.setObjectName("ActionLinkBtn")
        self.btn_preview.setStyleSheet("color: #33CCFF; background-color: rgba(0, 50, 80, 100);")
        self.btn_preview.clicked.connect(self.toggle_preview_playback)

        self.res_back_btn = QPushButton()
        self.res_back_btn.setStyleSheet("QPushButton { background-color: transparent; border: 1px solid #444; border-radius: 20px; padding: 8px 25px; font-size: 13px; color: #FFF; } QPushButton:hover { background-color: #111; }")
        self.res_back_btn.clicked.connect(lambda: self.switch_page(0, self.btn_home))
        
        left_layout.addWidget(cover_container, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.res_title)
        left_layout.addWidget(self.res_artist)
        left_layout.addWidget(self.res_genre)
        left_layout.addWidget(self.res_counter)
        left_layout.addSpacing(8)
        left_layout.addLayout(links_layout)
        left_layout.addSpacing(4)
        left_layout.addWidget(self.btn_preview, alignment=Qt.AlignCenter)
        left_layout.addSpacing(10)
        left_layout.addWidget(self.res_back_btn, alignment=Qt.AlignCenter)

        # SAĞ KOLON
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setAlignment(Qt.AlignTop)
        right_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.lyrics_heading = QLabel()
        self.lyrics_heading.setStyleSheet("font-size: 14px; font-weight: bold; color: #777; border: none; margin-bottom: 2px;")
        
        self.res_lyrics = QTextBrowser()
        self.res_lyrics.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.res_lyrics.setMinimumHeight(150); self.res_lyrics.setMaximumHeight(240)
        self.res_lyrics.setStyleSheet("background-color: rgba(15, 15, 15, 230); border: 1px solid #222; border-radius: 12px; color: #DDD; font-size: 13px; padding: 10px;")
        self.res_lyrics.setOpenExternalLinks(True)

        self.bio_heading = QLabel()
        self.bio_heading.setStyleSheet("font-size: 14px; font-weight: bold; color: #777; border: none; margin-top: 8px; margin-bottom: 2px;")
        
        self.res_bio = QTextBrowser()
        self.res_bio.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.res_bio.setFixedHeight(95)
        self.res_bio.setStyleSheet("background-color: rgba(15, 15, 15, 230); border: 1px solid #222; border-radius: 12px; color: #CCC; font-size: 12px; padding: 10px;")

        self.recommend_heading = QLabel()
        self.recommend_heading.setStyleSheet("font-size: 14px; font-weight: bold; color: #777; border: none; margin-top: 8px; margin-bottom: 2px;")
        
        self.recommend_scroll = QScrollArea()
        self.recommend_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.recommend_scroll.setFixedHeight(110)
        self.recommend_scroll.setWidgetResizable(True)
        self.recommend_content = QWidget()
        self.recommend_layout = QVBoxLayout(self.recommend_content)
        self.recommend_layout.setAlignment(Qt.AlignTop)
        self.recommend_scroll.setWidget(self.recommend_content)

        right_layout.addWidget(self.lyrics_heading)
        right_layout.addWidget(self.res_lyrics)
        right_layout.addWidget(self.bio_heading)
        right_layout.addWidget(self.res_bio)
        right_layout.addWidget(self.recommend_heading)
        right_layout.addWidget(self.recommend_scroll)

        main_h_layout.addWidget(left_container)
        main_h_layout.addWidget(right_container)
        
        main_grid.addWidget(self.res_bg_lbl, 0, 0)
        main_grid.addWidget(self.res_overlay, 0, 0)
        main_grid.addWidget(fg_widget, 0, 0)
        
        return page

    def toggle_preview_playback(self):
        t = LANGS[self.lang]
        if not self.current_preview_url:
            return
            
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            self.btn_preview.setText(t["btn_preview"])
        else:
            self.media_player.setSource(QUrl(self.current_preview_url))
            self.audio_output.setVolume(0.35)
            self.media_player.play()
            self.btn_preview.setText(t["btn_preview_stop"])

    def create_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 60, 60, 60)
        
        self.lbl_hist_title = QLabel()
        self.lbl_hist_title.setObjectName("TitleText")
        self.lbl_hist_title.setStyleSheet("font-size: 42px;")
        
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet("background-color: #0A0A0A; border: 1px solid #222; border-radius: 12px; padding: 12px 20px; font-size: 16px; color: #FFF;")
        self.search_input.textChanged.connect(self.load_history_view)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.history_layout = QVBoxLayout(scroll_content)
        self.history_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)
        
        hist_btn_layout = QHBoxLayout()
        hist_btn_layout.addStretch()
        
        self.btn_clear_hist = QPushButton()
        self.btn_clear_hist.clicked.connect(self.clear_history)
        self.btn_clear_hist.setStyleSheet("QPushButton { background-color: transparent; color: #555; border: none; font-size: 14px; text-align: right; } QPushButton:hover { color: #FF4444; }")
        
        hist_btn_layout.addWidget(self.btn_clear_hist)

        layout.addWidget(self.lbl_hist_title)
        layout.addSpacing(15)
        layout.addWidget(self.search_input)
        layout.addSpacing(20)
        layout.addWidget(scroll)
        layout.addLayout(hist_btn_layout)
        return page

    def create_stats_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 60, 60, 60)
        
        self.lbl_stats_title = QLabel()
        self.lbl_stats_title.setObjectName("TitleText")
        self.lbl_stats_title.setStyleSheet("font-size: 42px;")

        layout.addWidget(self.lbl_stats_title)
        layout.addSpacing(30)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.stats_grid_layout = QGridLayout(scroll_content)
        self.stats_grid_layout.setAlignment(Qt.AlignTop)
        self.stats_grid_layout.setSpacing(20)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        return page

    def load_stats_view(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            if hasattr(self, 'btn_preview'):
                self.btn_preview.setText(LANGS[self.lang]["btn_preview"])

        for i in reversed(range(self.stats_grid_layout.count())): 
            widget = self.stats_grid_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
            
        total, favs, top_artists = db.get_stats()
        t = LANGS[self.lang]
        
        card1 = ClickableCard()
        card1.setStyleSheet("background-color: #050505; border: 1px solid #1a1a1a; border-radius: 16px; padding: 25px;")
        card1.setCursor(Qt.PointingHandCursor)
        card1.clicked.connect(lambda: self.goto_history("all"))
        l1 = QVBoxLayout(card1)
        l1.addWidget(QLabel(f"<span style='color: #888; font-size: 14px;'>🎵  {t['stats_total']}</span><br><br><b style='font-size: 40px; color: #FFF;'>{total}</b>"))
        self.stats_grid_layout.addWidget(card1, 0, 0)
        
        card2 = ClickableCard()
        card2.setStyleSheet("background-color: #050505; border: 1px solid #1a1a1a; border-radius: 16px; padding: 25px;")
        card2.setCursor(Qt.PointingHandCursor)
        card2.clicked.connect(lambda: self.goto_history("favorites"))
        l2 = QVBoxLayout(card2)
        l2.addWidget(QLabel(f"<span style='color: #888; font-size: 14px;'>❤️  {t['stats_fav']}</span><br><br><b style='font-size: 40px; color: #FF4444;'>{favs}</b>"))
        self.stats_grid_layout.addWidget(card2, 0, 1)
        
        card3 = QFrame()
        card3.setStyleSheet("background-color: #050505; border: 1px solid #1a1a1a; border-radius: 16px; padding: 25px;")
        l3 = QVBoxLayout(card3)
        artist_text = f"<span style='color: #888; font-size: 14px;'>👑  {t['stats_top_artists']}</span><br><br>"
        if top_artists:
            for idx, (artist, count) in enumerate(top_artists, 1):
                artist_text += f"<div style='margin-bottom: 8px;'><span style='font-size: 15px; color: #FFF; font-weight: bold;'>{idx}. {artist}</span> <span style='color: #777; float: right;'>({count} keşif)</span></div>"
        else:
            artist_text += "<span style='color: #555; font-size: 15px;'>Henüz veri yok.</span>"
        l3.addWidget(QLabel(artist_text))
        self.stats_grid_layout.addWidget(card3, 1, 0, 1, 2)

    def create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 60, 60, 60)
        
        self.lbl_about_title = QLabel()
        self.lbl_about_title.setObjectName("TitleText")
        self.lbl_about_title.setStyleSheet("font-size: 42px;")
        layout.addWidget(self.lbl_about_title)
        layout.addSpacing(30)
        
        self.about_browser = QTextBrowser()
        self.about_browser.setOpenExternalLinks(True)
        self.about_browser.setStyleSheet("background-color: #050505; border: 1px solid #151515; border-radius: 16px; padding: 25px; font-size: 16px; color: #CCC;")
        
        layout.addWidget(self.about_browser)
        layout.addStretch()
        return page

    def create_settings_page(self):
        page = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(60, 60, 60, 60)
        
        self.lbl_set_title = QLabel()
        self.lbl_set_title.setObjectName("TitleText")
        self.lbl_set_title.setStyleSheet("font-size: 42px;")
        layout.addWidget(self.lbl_set_title)
        layout.addSpacing(30)
        
        form = QGridLayout()
        form.setSpacing(20)
        
        self.lbl_set_lang = QLabel()
        self.lbl_set_lang.setStyleSheet("font-size: 18px; color: #888;")
        self.btn_lang_toggle = QPushButton()
        self.btn_lang_toggle.setStyleSheet("background-color: #111; border-radius: 8px; padding: 10px; font-size: 16px;")
        self.btn_lang_toggle.clicked.connect(self.toggle_language)
        
        self.lbl_set_keys = QLabel()
        self.lbl_set_keys.setStyleSheet("font-size: 18px; color: #888;")
        self.keys_desc_lbl = QLabel()
        self.keys_desc_lbl.setStyleSheet("font-size: 15px; color: #FFF; font-weight: bold;")

        self.lbl_mic_sel = QLabel()
        self.lbl_mic_sel.setStyleSheet("font-size: 18px; color: #888;")
        self.mic_combo = QComboBox()
        self.mic_combo.currentIndexChanged.connect(self.save_mic_selection)

        self.lbl_speaker_sel = QLabel()
        self.lbl_speaker_sel.setStyleSheet("font-size: 18px; color: #888;")
        self.speaker_combo = QComboBox()
        self.speaker_combo.currentIndexChanged.connect(self.save_speaker_selection)

        self.lbl_close_action = QLabel()
        self.lbl_close_action.setStyleSheet("font-size: 18px; color: #888;")
        self.close_combo = QComboBox()
        self.close_combo.currentIndexChanged.connect(self.save_close_action_selection)

        self.hud_checkbox = QCheckBox()
        self.hud_checkbox.stateChanged.connect(self.save_hud_selection)

        self.startup_checkbox = QCheckBox()
        self.startup_checkbox.stateChanged.connect(self.save_startup_selection)

        self.eval_btn = QPushButton()
        self.eval_btn.setObjectName("ActionLinkBtn")
        self.eval_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://forms.gle/cknEtKhUusU3Bze97")))
        self.eval_note_lbl = QLabel()
        self.eval_note_lbl.setStyleSheet("font-size: 13px; color: #777; font-style: italic;")
        self.eval_note_lbl.setWordWrap(True)

        self.bug_btn = QPushButton()
        self.bug_btn.setObjectName("ActionLinkBtn")
        self.bug_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://forms.gle/zFYLUHzHGHVQ6xzh9")))
        self.bug_note_lbl = QLabel()
        self.bug_note_lbl.setStyleSheet("font-size: 13px; color: #777; font-style: italic;")
        self.bug_note_lbl.setWordWrap(True)

        self.populate_audio_devices()
        
        form.addWidget(self.lbl_set_lang, 0, 0)
        form.addWidget(self.btn_lang_toggle, 0, 1)
        form.addWidget(self.lbl_mic_sel, 1, 0)
        form.addWidget(self.mic_combo, 1, 1)
        form.addWidget(self.lbl_speaker_sel, 2, 0)
        form.addWidget(self.speaker_combo, 2, 1)
        form.addWidget(self.lbl_close_action, 3, 0)
        form.addWidget(self.close_combo, 3, 1)
        form.addWidget(self.hud_checkbox, 4, 0, 1, 2)
        form.addWidget(self.startup_checkbox, 5, 0, 1, 2)
        
        form.addWidget(self.eval_btn, 6, 0)
        form.addWidget(self.eval_note_lbl, 6, 1)
        form.addWidget(self.bug_btn, 7, 0)
        form.addWidget(self.bug_note_lbl, 7, 1)
        
        form.addWidget(self.lbl_set_keys, 8, 0)
        form.addWidget(self.keys_desc_lbl, 8, 1)
        
        layout.addLayout(form)
        layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        return page

    def populate_audio_devices(self):
        try:
            self.mic_combo.clear()
            self.mic_combo.addItem("Sistem Varsayılanı", "default")
            for mic in sc.all_microphones():
                self.mic_combo.addItem(mic.name, mic.id)

            saved_mic = db.get_setting("selected_mic")
            idx = self.mic_combo.findData(saved_mic)
            if idx >= 0: self.mic_combo.setCurrentIndex(idx)
        except:
            pass

        try:
            self.speaker_combo.clear()
            self.speaker_combo.addItem("Sistem Varsayılanı (Hoparlör)", "default")
            for spk in sc.all_speakers():
                self.speaker_combo.addItem(spk.name, spk.id)

            saved_spk = db.get_setting("selected_speaker")
            idx2 = self.speaker_combo.findData(saved_spk)
            if idx2 >= 0: self.speaker_combo.setCurrentIndex(idx2)
        except:
            pass

        try:
            self.close_combo.clear()
            t = LANGS[self.lang]
            self.close_combo.addItem(t["close_ask"], "ask")
            self.close_combo.addItem(t["close_tray"], "tray")
            self.close_combo.addItem(t["close_quit"], "quit")

            saved_close = db.get_setting("close_action") or "ask"
            idx3 = self.close_combo.findData(saved_close)
            if idx3 >= 0: self.close_combo.setCurrentIndex(idx3)
        except:
            pass
            
        saved_hud = db.get_setting("hud_enabled")
        self.hud_checkbox.setChecked(saved_hud == "true")

        saved_startup = db.get_setting("startup_enabled")
        self.startup_checkbox.setChecked(saved_startup == "true")

    def save_mic_selection(self, index):
        dev_id = self.mic_combo.itemData(index)
        if dev_id: db.set_setting("selected_mic", dev_id)

    def save_speaker_selection(self, index):
        dev_id = self.speaker_combo.itemData(index)
        if dev_id: db.set_setting("selected_speaker", dev_id)

    def save_close_action_selection(self, index):
        val = self.close_combo.itemData(index)
        if val: db.set_setting("close_action", val)

    def save_hud_selection(self, state):
        is_checked = "true" if self.hud_checkbox.isChecked() else "false"
        db.set_setting("hud_enabled", is_checked)

    def save_startup_selection(self, state):
        is_checked = self.startup_checkbox.isChecked()
        db.set_setting("startup_enabled", "true" if is_checked else "false")
        self.update_windows_registry(is_checked)

    def update_windows_registry(self, enable):
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "LYRA"
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
            if enable:
                if getattr(sys, 'frozen', False):
                    app_path = sys.executable
                else:
                    app_path = os.path.abspath(__file__)
                reg.SetValueEx(key, app_name, 0, reg.REG_SZ, f'"{app_path}"')
            else:
                try:
                    reg.DeleteValue(key, app_name)
                except WindowsError:
                    pass
            reg.CloseKey(key)
        except Exception:
            pass

    def toggle_language(self):
        self.lang = "en" if self.lang == "tr" else "tr"
        db.set_setting("lang", self.lang)
        self.apply_language()

    def apply_language(self):
        t = LANGS[self.lang]
        self.btn_home.setText(t["nav_home"])
        self.btn_history.setText(t["nav_history"])
        self.btn_stats.setText(t["nav_stats"])
        self.btn_settings.setText(t["nav_settings"])
        self.btn_about.setText(t["nav_about"])
        
        self.lbl_home_title.setText(t["title_home"])
        self.status_label.setText(t["status_ready"])
        self.sys_btn.setText(t["btn_sys"])
        self.mic_btn.setText(t["btn_mic"])
        
        self.res_back_btn.setText(t["res_close"])
        self.lyrics_heading.setText(t["lyrics_title"])
        self.bio_heading.setText(t["bio_title"])
        self.recommend_heading.setText(t["rec_title"])
        
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            if hasattr(self, 'btn_preview'):
                self.btn_preview.setText(t["btn_preview_stop"])
        else:
            if hasattr(self, 'btn_preview'):
                self.btn_preview.setText(t["btn_preview"])
        
        self.lbl_hist_title.setText(t["hist_title"])
        self.search_input.setPlaceholderText(t["hist_search"])
        self.btn_clear_hist.setText(t["hist_clear"])

        self.lbl_stats_title.setText(t["stats_title"])
        
        self.lbl_set_title.setText(t["set_title"])
        self.lbl_set_lang.setText(t["set_lang"])
        self.btn_lang_toggle.setText(t["lang_btn"])
        self.lbl_set_keys.setText(t["set_shortcuts"])
        self.keys_desc_lbl.setText(t["shortcuts_desc"])
        self.lbl_mic_sel.setText(t["set_mic"])
        self.lbl_speaker_sel.setText(t["set_speaker"])
        self.lbl_close_action.setText(t["set_close_action"])
        self.hud_checkbox.setText(t["set_hud"])
        self.startup_checkbox.setText(t["set_startup"])
        
        current_data = self.close_combo.currentData() if hasattr(self, 'close_combo') else "ask"
        if hasattr(self, 'close_combo'):
            self.close_combo.blockSignals(True)
            self.close_combo.clear()
            self.close_combo.addItem(t["close_ask"], "ask")
            self.close_combo.addItem(t["close_tray"], "tray")
            self.close_combo.addItem(t["close_quit"], "quit")
            idx = self.close_combo.findData(current_data)
            if idx >= 0: self.close_combo.setCurrentIndex(idx)
            self.close_combo.blockSignals(False)

        self.eval_btn.setText(t["btn_eval"])
        self.eval_note_lbl.setText(t["note_eval"])
        self.bug_btn.setText(t["btn_bug"])
        self.bug_note_lbl.setText(t["note_bug"])

        self.lbl_about_title.setText(t["about_title"])
        self.about_browser.setHtml(t["about_text"])
        
        self.act_show.setText(t["tray_show"])
        self.act_quit.setText(t["tray_quit"])

    def switch_page(self, index, active_btn):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()
            if hasattr(self, 'btn_preview'):
                self.btn_preview.setText(LANGS[self.lang]["btn_preview"])

        self.pages.setCurrentIndex(index)
        for btn in [self.btn_home, self.btn_history, self.btn_stats, self.btn_settings, self.btn_about]:
            btn.setChecked(False)
        active_btn.setChecked(True)
        if index == 2: self.load_history_view()
        elif index == 3: self.load_stats_view()

    def update_status(self, text):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 500;")
        if "dinleniyor" in text.lower() or "listening" in text.lower() or "analiz" in text.lower():
            self.pulse_anim.start()
            self.visualizer.start()
        else:
            self.pulse_anim.stop()
            self.status_label.setWindowOpacity(1.0)
            self.visualizer.stop()

    def show_result(self, result):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.stop()

        self.pulse_anim.stop()
        self.visualizer.stop()
        self.status_label.setWindowOpacity(1.0)
        self.status_label.setText(LANGS[self.lang]["status_ready"])
        self.status_label.setStyleSheet("color: #666666; font-size: 18px;")
        
        self.res_title.setText(result['title'])
        self.res_artist.setText(result['artist'])
        self.res_genre.setText(f"Müzik Türü: {result.get('genre', 'Genel')}")
        
        shazam_count = result.get('shazam_count', 0)
        if shazam_count > 0:
            self.res_counter.setText(f"🔥 Dünya Çapında {shazam_count:,} Keşif")
            self.res_counter.show()
        else:
            self.res_counter.hide()
        
        self.res_bio.setText(result.get('artist_bio', LANGS[self.lang]["bio_loading"]))

        self.current_preview_url = result.get('preview_url', '')
        if self.current_preview_url:
            self.btn_preview.show()
            self.btn_preview.setText(LANGS[self.lang]["btn_preview"])
        else:
            self.btn_preview.hide()

        self.update_discord_presence(result['title'], result['artist'])
        
        query = f"{result['title']} {result['artist']}"
        
        try:
            self.btn_spotify.clicked.disconnect()
        except RuntimeError:
            pass
        try:
            self.btn_youtube.clicked.disconnect()
        except RuntimeError:
            pass
        
        self.btn_spotify.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://open.spotify.com/search/{query}")))
        self.btn_youtube.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://www.youtube.com/results?search_query={query}")))
        
        self.res_lyrics.setText(LANGS[self.lang]["lyrics_loading"])
        self.lyrics_fetcher = LyricsLoader()
        self.lyrics_fetcher.lyrics_loaded.connect(self.res_lyrics.setText)
        self.lyrics_fetcher.load_lyrics(result['title'], result['artist'], self.lang)

        for i in reversed(range(self.recommend_layout.count())):
            w = self.recommend_layout.itemAt(i).widget()
            if w: w.deleteLater()
            
        with db.db_lock:
            db.cursor.execute("SELECT title, artist FROM songs WHERE artist LIKE ? AND track_id != ? LIMIT 4", (f"%{result['artist']}%", result['id']))
            similar_songs = db.cursor.fetchall()
        
        if similar_songs:
            for s_title, s_artist in similar_songs:
                rec_card = QFrame()
                rec_card.setStyleSheet("background-color: rgba(20, 20, 20, 200); border: 1px solid #222; border-radius: 8px; padding: 6px;")
                rec_h = QHBoxLayout(rec_card)
                rec_h.setContentsMargins(8, 6, 8, 6)
                lbl_info = QLabel(f"<b>{s_title}</b><br><span style='color: #aaa; font-size: 11px;'>{s_artist}</span>")
                lbl_info.setStyleSheet("border: none; color: #FFF;")
                rec_h.addWidget(lbl_info)
                self.recommend_layout.addWidget(rec_card)
        else:
            lbl_none = QLabel(LANGS[self.lang]["rec_empty"])
            lbl_none.setStyleSheet("color: #555; font-size: 13px; border: none; padding: 10px;")
            self.recommend_layout.addWidget(lbl_none)

        def handle_images(pixmap):
            self.res_cover.setPixmap(pixmap)
            self.res_bg_lbl.setPixmap(pixmap)
            
            try:
                img = pixmap.toImage().scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                r_total, g_total, b_total, count = 0, 0, 0, 0
                for x in range(0, img.width(), 3):
                    for y in range(0, img.height(), 3):
                        c = img.pixelColor(x, y)
                        r_total += c.red()
                        g_total += c.green()
                        b_total += c.blue()
                        count += 1
                if count > 0:
                    avg_color = QColor(r_total // count, g_total // count, b_total // count)
                    if avg_color.lightness() < 50:
                        avg_color = avg_color.lighter(180)
                    self.visualizer.set_accent_color(avg_color)
            except:
                self.visualizer.set_accent_color(QColor(255, 255, 255))

        self.loader = ImageLoader()
        self.loader.image_loaded.connect(handle_images)
        self.loader.load_image(result['cover_url'])
        
        self.restore_window_state()
        self.switch_page(1, self.btn_home)
        
        if db.get_setting("hud_enabled") == "true":
            if self.hud_window:
                self.hud_window.close()
            self.hud_window = HUDWidget(result)
        
        self.tray_icon.showMessage("LYRA - Şarkı Bulundu!", f"{result['title']} - {result['artist']}", QSystemTrayIcon.Information, 4000)

    def show_error(self, err_msg):
        self.pulse_anim.stop()
        self.visualizer.stop()
        self.status_label.setWindowOpacity(1.0)
        self.status_label.setText(err_msg)
        self.status_label.setStyleSheet("color: #FF4444; font-size: 18px;")
        
        self.restore_window_state()
        
        self.tray_icon.showMessage("LYRA Hatası", err_msg, QSystemTrayIcon.Warning, 3000)
            
        async def reset_label():
            await asyncio.sleep(3)
            self.status_label.setText(LANGS[self.lang]["status_ready"])
            self.status_label.setStyleSheet("color: #666666; font-size: 18px;")
        asyncio.create_task(reset_label())

    def load_history_view(self):
        for i in reversed(range(self.history_layout.count())): 
            widget = self.history_layout.itemAt(i).widget()
            if widget: widget.deleteLater()
            
        songs = db.get_history()
        
        if getattr(self, 'history_filter_mode', 'all') == 'favorites':
            songs = [s for s in songs if s[7] == 1]
            
        filter_text = self.search_input.text().lower().strip() if hasattr(self, 'search_input') else ""
        
        filtered_songs = [
            s for s in songs 
            if filter_text in str(s[2]).lower() or filter_text in str(s[3]).lower() or (len(s) > 9 and s[9] and filter_text in str(s[9]).lower())
        ] if filter_text else songs

        if not filtered_songs:
            lbl = QLabel(LANGS[self.lang]["hist_empty"])
            lbl.setStyleSheet("color: #333; font-size: 18px; font-weight: 500;")
            self.history_layout.addWidget(lbl)
            return
            
        for song in filtered_songs:
            self.history_layout.addWidget(SongCard(song, parent_refresh_cb=self.load_history_view))

    def clear_history(self):
        db.clear_history()
        self.load_history_view()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())