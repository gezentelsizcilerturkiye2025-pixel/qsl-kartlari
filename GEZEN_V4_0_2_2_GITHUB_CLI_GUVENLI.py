import math
import os

# Program çift tıklanarak da çalıştırıldığında dosya yolları doğru klasörü kullansın.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
import random
import re
import sqlite3
import sys
import webbrowser
import base64
import json
import urllib.request
import urllib.error
import time
from datetime import datetime
from queue import Queue
import threading
import subprocess
import io
import requests

try:
    import pymupdf as fitz  # Güncel PyMuPDF API'si
except ImportError:
    fitz = None

# --- CHROMIUM SÜRÜCÜ VE SES BAYRAKLARI (QApplication'dan Önce Tanımlanmalıdır) ---
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--use-fake-ui-for-media-stream "
    "--enable-features=AudioServiceOutOfProcess "
    "--autoplay-policy=no-user-gesture-required"
)

from PyQt6.QtCore import QEvent, Qt, QTimer, QUrl, QPropertyAnimation, QEasingCurve, QRect, QObject, pyqtSignal, QRunnable, QThreadPool
from PyQt6.QtGui import QAction, QColor, QDesktopServices, QImage, QPixmap, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QGridLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
    QComboBox,
    QProgressDialog,
    QFrame,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QHeaderView,
    QScrollBar,
)

# PyQt6 WebEngine Kontrolü ve Ses/Mikrofon İzin Yapılandırması
try:
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

import database as db
import phonetic

# --- ANARAD KARAMÜRSEL RÖLESİ KOORDİNATLARI (Kocaeli, Karamürsel) ---
ROLE_LAT = 40.6922
ROLE_LON = 29.6161

# QSL kartları paralel hazırlanırken kullanılan ortak önbellek.
_QSL_BACKGROUND_CACHE = None


def tr_normalize(text):
    """Türkçe büyük/küçük karakterleri standart harflere dönüştürür (Arama ve Eşleşme Hassasiyeti İçin)"""
    if not text:
        return ""
    tr_map = str.maketrans("çğıiöşüÇĞİIÖŞÜ", "cgiiosuCGIiOSU")
    return text.translate(tr_map).upper()


# --- TÜM AVRUPA ÜLKELERİ, ŞEHİRLERİ, İLÇELERİ, KASABALARI VE TÜRKİYE 81 İL KOORDİNAT SÖZLÜĞÜ ---
CITY_COORDS = {
    # --- ALMANYA (TÜM EYALETLER, ŞEHİRLER, İLÇELER VE KASABALAR) ---
    "DORPEN": (52.9333, 7.3333),
    "DÖRPEN": (52.9333, 7.3333),
    "BOSAU": (54.1167, 10.4167),
    "PAPENBURG": (53.0833, 7.3833),
    "LEER": (53.2333, 7.4500),
    "EMDEN": (53.3667, 7.2000),
    "OLDENBURG": (53.1434, 8.2148),
    "OSNABRUCK": (52.2799, 8.0472),
    "BREMEN": (53.0793, 8.8017),
    "HAMBURG": (53.5511, 9.9937),
    "KIEL": (54.3233, 10.1228),
    "LUBECK": (53.8655, 10.6866),
    "LÜBECK": (53.8655, 10.6866),
    "ROSTOCK": (54.0924, 12.0991),
    "SCHWERIN": (53.6355, 11.4127),
    "FLENSBURG": (54.7833, 9.4333),
    "GERMANY": (52.5200, 13.4050),
    "ALMANYA": (52.5200, 13.4050),
    "BERLIN": (52.5200, 13.4050),
    "NUREMBERG": (49.4521, 11.0767),
    "NURNBERG": (49.4521, 11.0767),
    "NÜRNBERG": (49.4521, 11.0767),
    "FURTH": (49.4786, 10.9886),
    "FÜRTH": (49.4786, 10.9886),
    "ERLANGEN": (49.5896, 11.0038),
    "SCHWABACH": (49.3288, 11.0238),
    "MUNICH": (48.1351, 11.5820),
    "MUNCHEN": (48.1351, 11.5820),
    "MÜNCHEN": (48.1351, 11.5820),
    "FRANKFURT": (50.1109, 8.6821),
    "OFFENBACH": (50.1030, 8.7600),
    "HANAU": (50.1360, 8.9160),
    "STUTTGART": (48.7758, 9.1829),
    "COLOGNE": (50.9375, 6.9603),
    "KOLN": (50.9375, 6.9603),
    "KÖLN": (50.9375, 6.9603),
    "DUSSELDORF": (51.2277, 6.7735),
    "DORTMUND": (51.5136, 7.4653),
    "ESSEN": (51.4556, 7.0116),
    "HANNOVER": (52.3759, 9.7320),
    "LEIPZIG": (51.3397, 12.3731),
    "DRESDEN": (51.0504, 13.7373),
    "BONN": (50.7374, 7.0982),
    "KARLSRUHE": (49.0069, 8.4037),
    "MANNHEIM": (49.4875, 8.4660),
    "WIESBADEN": (50.0782, 8.2397),
    "AACHEN": (50.7753, 6.0839),
    "FREIBURG": (47.9990, 7.8421),
    # --- FRANSA (BÖLGELER, ŞEHİRLER VE İLÇELER) ---
    "FRANCE": (48.8566, 2.3522),
    "FRANSA": (48.8566, 2.3522),
    "PARIS": (48.8566, 2.3522),
    "LYON": (45.7640, 4.8357),
    "MARSEILLE": (43.2965, 5.3698),
    "TOULOUSE": (43.6047, 1.4442),
    "NICE": (43.7102, 7.2620),
    "STRASBOURG": (48.5734, 7.7521),
    "NANTES": (47.2184, -1.5536),
    "BORDEAUX": (44.8378, -0.5792),
    "LILLE": (50.6292, 3.0573),
    "RENNES": (48.1173, -1.6778),
    "REIMS": (49.2583, 4.0317),
    "LE HAVRE": (49.4944, 0.1079),
    "SAINT ETIENNE": (45.4397, 4.3872),
    "TOULON": (43.1242, 5.928),
    "GRENOBLE": (45.1885, 5.7245),
    "DIJON": (47.3220, 5.0415),
    "ANGERS": (47.4784, -0.5632),
    "NIMES": (43.8367, 4.3601),
    "VILLEURBANNE": (45.7640, 4.8857),
    # --- İTALYA (BÖLGELER, ŞEHİRLER VE İLÇELER) ---
    "ITALY": (41.9028, 12.4964),
    "İTALYA": (41.9028, 12.4964),
    "ROME": (41.9028, 12.4964),
    "ROMA": (41.9028, 12.4964),
    "MILAN": (45.4642, 9.1900),
    "MILANO": (45.4642, 9.1900),
    "NAPLES": (40.8518, 14.2681),
    "NAPOLI": (40.8518, 14.2681),
    "TURIN": (45.0703, 7.6869),
    "TORINO": (45.0703, 7.6869),
    "PALERMO": (38.1157, 13.3615),
    "GENOA": (44.4056, 8.9463),
    "GENOVA": (44.4056, 8.9463),
    "BOLOGNA": (44.4949, 11.3426),
    "FLORENCE": (43.7696, 11.2558),
    "FIRENZE": (43.7696, 11.2558),
    "VENICE": (45.4408, 12.3155),
    "VENEZIA": (45.4408, 12.3155),
    "VERONA": (45.4384, 10.9916),
    "BARI": (41.1171, 16.8719),
    "CATANIA": (37.5079, 15.0830),
    # --- İSPANYA (ŞEHİRLER VE İLÇELER) ---
    "SPAIN": (40.4168, -3.7038),
    "İSPANYA": (40.4168, -3.7038),
    "MADRID": (40.4168, -3.7038),
    "BARCELONA": (41.3851, 2.1734),
    "VALENCIA": (39.4699, -0.3763),
    "SEVILLE": (37.3891, -5.9845),
    "SEVILLA": (37.3891, -5.9845),
    "ZARAGOZA": (41.6488, -0.8891),
    "MALAGA": (36.7213, -4.4214),
    "BILBAO": (43.2630, -2.9350),
    "ALICANTE": (38.3452, -0.4810),
    "CORDOBA": (37.8882, -4.7794),
    "GRANADA": (37.1773, -3.5986),
    # --- HOLLANDA (ŞEHİRLER VE İLÇELER) ---
    "NETHERLANDS": (52.3676, 4.9041),
    "HOLLANDA": (52.3676, 4.9041),
    "AMSTERDAM": (52.3676, 4.9041),
    "ROTTERDAM": (51.9244, 4.4777),
    "THE HAGUE": (52.0705, 4.3007),
    "DEN HAAG": (52.0705, 4.3007),
    "UTRECHT": (52.0907, 5.1214),
    "EINDHOVEN": (51.4416, 5.4697),
    "GRONINGEN": (53.2194, 6.5665),
    "TILBURG": (51.5555, 5.0913),
    "ALMERE": (52.3508, 5.2647),
    "BREDA": (51.5719, 4.7683),
    "NIJMEGEN": (51.8126, 5.8372),
    "ARNHEM": (51.9851, 5.8987),
    # --- BELÇİKA ---
    "BELGIUM": (50.8503, 4.3517),
    "BELÇİKA": (50.8503, 4.3517),
    "BRUSSELS": (50.8503, 4.3517),
    "BRUKSEL": (50.8503, 4.3517),
    "ANTWERP": (51.2194, 4.4025),
    "ANTVERPEN": (51.2194, 4.4025),
    "GHENT": (51.0543, 3.7174),
    "GENT": (51.0543, 3.7174),
    "CHARLEROI": (50.4108, 4.4446),
    "LIEGE": (50.6326, 5.5797),
    "BRUGGE": (51.2093, 3.2247),
    "NAMUR": (50.4674, 4.8719),
    # --- AVUSTURYA ---
    "AUSTRIA": (48.2082, 16.3738),
    "AVUSTURYA": (48.2082, 16.3738),
    "VIENNA": (48.2082, 16.3738),
    "VİYANA": (48.2082, 16.3738),
    "SALZBURG": (47.8095, 13.0550),
    "GRAZ": (47.0707, 15.4395),
    "LINZ": (48.3069, 14.2858),
    "INNSBRUCK": (47.2692, 11.4041),
    "KLAGENFURT": (46.6366, 14.3093),
    "VILLACH": (46.6111, 13.8458),
    # --- İSVİÇRE ---
    "SWITZERLAND": (46.9480, 7.4474),
    "İSVİÇRE": (46.9480, 7.4474),
    "ZURICH": (47.3769, 8.5417),
    "ZÜRICH": (47.3769, 8.5417),
    "GENEVA": (46.2044, 6.1432),
    "CENEVRE": (46.2044, 6.1432),
    "BASEL": (47.5596, 7.5886),
    "BERN": (46.9480, 7.4474),
    "LAUSANNE": (46.5197, 6.6323),
    "LUCERNE": (47.0502, 8.3093),
    "LUKERN": (47.0502, 8.3093),
    "ST GALLEN": (47.4245, 9.3767),
    # --- BİRLEŞİK KRALLIK (İNGİLTERE, İSKOÇYA, GALLER, KUZEY İRLANDA) ---
    "UNITED KINGDOM": (51.5074, -0.1278),
    "UK": (51.5074, -0.1278),
    "ENGLAND": (51.5074, -0.1278),
    "İNGİLTERE": (51.5074, -0.1278),
    "LONDON": (51.5074, -0.1278),
    "LONDRA": (51.5074, -0.1278),
    "MANCHESTER": (53.4808, -2.2426),
    "BIRMINGHAM": (52.4862, -1.8904),
    "LIVERPOOL": (53.4084, -2.9916),
    "GLASGOW": (55.8642, -4.2518),
    "EDINBURGH": (55.9533, -3.1883),
    "BRISTOL": (51.4545, -2.5879),
    "LEEDS": (53.8008, -1.5491),
    "SHEFFIELD": (53.3811, -1.4701),
    "BELFAST": (54.5973, -5.9301),
    "CARDIFF": (51.4816, -3.1791),
    "DUNDEE": (56.4620, -2.9707),
    "ABERDEEN": (57.1497, -2.0943),
    # --- POLONYA ---
    "POLAND": (52.2297, 21.0122),
    "POLONYA": (52.2297, 21.0122),
    "WARSAW": (52.2297, 21.0122),
    "VARŞOVA": (52.2297, 21.0122),
    "KRAKOW": (50.0647, 19.9450),
    "WROCLAW": (51.1079, 17.0385),
    "POZNAN": (52.4064, 16.9252),
    "GDANSK": (54.3520, 18.6466),
    "SZCZECIN": (53.4285, 14.5528),
    # --- YUNANİSTAN ---
    "GREECE": (37.9838, 23.7275),
    "YUNANİSTAN": (37.9838, 23.7275),
    "ATHENS": (37.9838, 23.7275),
    "ATİNA": (37.9838, 23.7275),
    "THESSALONIKI": (40.6401, 22.9444),
    "SELANİK": (40.6401, 22.9444),
    "PATRAS": (38.2466, 21.7345),
    "HERAKLION": (35.3387, 25.1442),
    "LARISSA": (39.6390, 22.4194),
    "RHODES": (36.4340, 28.2176),
    "RODOS": (36.4340, 28.2176),
    # --- BULGARİSTAN ---
    "BULGARIA": (42.6977, 23.3219),
    "BULGARİSTAN": (42.6977, 23.3219),
    "SOFIA": (42.6977, 23.3219),
    "SOFYA": (42.6977, 23.3219),
    "PLOVDIV": (42.1354, 24.7453),
    "FİLİBE": (42.1354, 24.7453),
    "VARNA": (43.2141, 27.9147),
    "BURGAS": (42.5048, 27.4626),
    "RUSE": (43.8356, 25.9657),
    # --- ROMANYA ---
    "ROMANIA": (44.4268, 26.1025),
    "ROMANYA": (44.4268, 26.1025),
    "BUCHAREST": (44.4268, 26.1025),
    "BÜKREŞ": (44.4268, 26.1025),
    "CLUJ-NAPOCA": (46.7712, 23.6236),
    "TIMISOARA": (45.7537, 21.2257),
    "IASI": (47.1585, 27.6014),
    "CONSTANTA": (44.1792, 28.6455),
    # --- MACARİSTAN ---
    "HUNGARY": (47.4979, 19.0402),
    "MACARİSTAN": (47.4979, 19.0402),
    "BUDAPEST": (47.4979, 19.0402),
    "BUDAPEŞTE": (47.4979, 19.0402),
    "DEBRECEN": (47.5316, 21.6273),
    "SZEGED": (46.2530, 20.1484),
    "POCS": (46.0727, 18.2323),
    # --- ÇEKYA / ÇEK CUMHURİYETİ ---
    "CZECH REPUBLIC": (50.0755, 14.4378),
    "CZECHIA": (50.0755, 14.4378),
    "ÇEKYA": (50.0755, 14.4378),
    "PRAGUE": (50.0755, 14.4378),
    "PRAG": (50.0755, 14.4378),
    "BRNO": (49.1951, 16.6068),
    "OSTRAVA": (49.8209, 18.2625),
    # --- İSVEÇ ---
    "SWEDEN": (59.3293, 18.0686),
    "İSVEÇ": (59.3293, 18.0686),
    "STOCKHOLM": (59.3293, 18.0686),
    "GOTHENBURG": (57.7089, 11.9746),
    "GÖTEBORG": (57.7089, 11.9746),
    "MALMO": (55.6050, 13.0038),
    "MALMÖ": (55.6050, 13.0038),
    "UPPSALA": (59.8586, 17.6389),
    # --- NORVEÇ ---
    "NORWAY": (59.9139, 10.7522),
    "NORVEÇ": (59.9139, 10.7522),
    "OSLO": (59.9139, 10.7522),
    "BERGEN": (60.3913, 5.3221),
    "TRONDHEIM": (63.4305, 10.3951),
    "STAVANGER": (58.9700, 5.7331),
    # --- DANİMARKA ---
    "DENMARK": (55.6761, 12.5683),
    "DANİMARKA": (55.6761, 12.5683),
    "COPENHAGEN": (55.6761, 12.5683),
    "KOPENHAG": (55.6761, 12.5683),
    "AARHUS": (56.1629, 10.2039),
    "ODENSE": (55.4038, 10.4024),
    # --- FİNLANDİYA ---
    "FINLAND": (60.1699, 24.9384),
    "FİNLANDİYA": (60.1699, 24.9384),
    "HELSINKI": (60.1699, 24.9384),
    "ESPOO": (60.2054, 24.6559),
    "TAMPERE": (61.4978, 23.7610),
    "TURKU": (60.4518, 22.2666),
    # --- PORTEKİZ ---
    "PORTUGAL": (38.7223, -9.1393),
    "PORTEKİZ": (38.7223, -9.1393),
    "LISBON": (38.7223, -9.1393),
    "LİZBON": (38.7223, -9.1393),
    "PORTO": (41.1579, -8.6291),
    "AMADORA": (38.7597, -9.2339),
    "BRAGA": (41.5454, -8.4265),
    # --- İRLANDA ---
    "IRELAND": (53.3498, -6.2603),
    "İRLANDA": (53.3498, -6.2603),
    "DUBLIN": (53.3498, -6.2603),
    "CORK": (51.8985, -8.4756),
    "LIMERICK": (52.6638, -8.6267),
    "GALWAY": (53.2707, -9.0568),
    # --- UKRAYNA ---
    "UKRAINE": (50.4501, 30.5234),
    "UKRAYNA": (50.4501, 30.5234),
    "KYIV": (50.4501, 30.5234),
    "KİYİV": (50.4501, 30.5234),
    "KHARKIV": (49.9935, 36.2304),
    "ODESA": (46.4825, 30.7233),
    "LVIV": (49.8397, 24.0297),
    "DNIPRO": (48.4647, 35.0462),
    # --- AZERBAYCAN ---
    "AZERBAIJAN": (40.4093, 49.8671),
    "AZERBAYCAN": (40.4093, 49.8671),
    "BAKU": (40.4093, 49.8671),
    "BAKI": (40.4093, 49.8671),
    "GANJA": (40.6828, 46.3606),
    "SUMQAYIT": (40.5897, 49.6686),
    # --- DİĞER AVRUPA ÜLKELERİ ---
    "ICELAND": (64.1466, -21.9426),
    "İZLANDA": (64.1466, -21.9426),
    "REYKJAVIK": (64.1466, -21.9426),
    "ESTONIA": (59.4370, 24.7536),
    "ESTONYA": (59.4370, 24.7536),
    "TALLINN": (59.4370, 24.7536),
    "LATVIA": (56.9496, 24.1052),
    "LETONYA": (56.9496, 24.1052),
    "RIGA": (56.9496, 24.1052),
    "LITHUANIA": (54.6872, 25.2797),
    "LİTVANYA": (54.6872, 25.2797),
    "VILNIUS": (54.6872, 25.2797),
    "SLOVAKIA": (48.1486, 17.1077),
    "SLOVAKYA": (48.1486, 17.1077),
    "BRATISLAVA": (48.1486, 17.1077),
    "SLOVENIA": (46.0569, 14.5058),
    "SLOVENYA": (46.0569, 14.5058),
    "LJUBLJANA": (46.0569, 14.5058),
    "CROATIA": (45.8150, 15.9819),
    "HIRVATİSTAN": (45.8150, 15.9819),
    "ZAGREB": (45.8150, 15.9819),
    "BOSNIA": (43.8563, 18.4131),
    "BOSNA HERSEK": (43.8563, 18.4131),
    "SARAJEVO": (43.8563, 18.4131),
    "SERBIA": (44.7866, 20.4489),
    "SIRBİSTAN": (44.7866, 20.4489),
    "BELGRADE": (44.7866, 20.4489),
    "BELGRAD": (44.7866, 20.4489),
    "MONTENEGRO": (42.4411, 19.2636),
    "KARADAĞ": (42.4411, 19.2636),
    "PODGORICA": (42.4411, 19.2636),
    "ALBANIA": (41.3275, 19.8187),
    "ARNAVUTLUK": (41.3275, 19.8187),
    "TIRANA": (41.3275, 19.8187),
    "NORTH MACEDONIA": (41.9981, 21.4254),
    "MAKEDONYA": (41.9981, 21.4254),
    "SKOPJE": (41.9981, 21.4254),
    "ÜSKÜP": (41.9981, 21.4254),
    "MALTA": (35.9375, 14.3754),
    "VALLETTA": (35.8989, 14.5146),
    "LUXEMBOURG": (49.6116, 6.1319),
    "LÜKSEMBURG": (49.6116, 6.1319),
    "MONACO": (43.7384, 7.4246),
    "LIECHTENSTEIN": (47.1410, 9.5209),
    "VADUZ": (47.1410, 9.5209),
    "SAN MARINO": (43.9424, 12.4578),
    "VATICAN": (41.9029, 12.4534),
    "VATİKAN": (41.9029, 12.4534),
    "ANDORRA": (42.5063, 1.5218),
    # Kahramanmaraş ve İlçeleri
    "KAHRAMANMARAS": (37.5858, 36.9371),
    "MARAS": (37.5858, 36.9371),
    "ELBISTAN": (38.2059, 37.1983),
    "AFSIN": (38.2477, 36.9141),
    "TURKOGLU": (37.3828, 36.8450),
    # Zonguldak & Karadeniz Ereğli
    "ZONGULDAK": (41.4564, 31.7987),
    "KARADENIZ EREGLI": (41.2828, 31.4181),
    "EREGLI": (41.2828, 31.4181),
    "K D Z EREGLI": (41.2828, 31.4181),
    "KDZ EREGLI": (41.2828, 31.4181),
    "DEVREK": (41.2183, 31.9547),
    "CAYCUMA": (41.4228, 32.0783),
    # Kocaeli ve İlçeleri
    "KOCAELI": (40.7654, 29.9408),
    "IZMIT": (40.7654, 29.9408),
    "KORFEZ": (40.7719, 29.7372),
    "ILIMTEPE": (40.8013, 29.7641),
    "GEBZE": (40.8028, 29.4307),
    "DERINCE": (40.7561, 29.8306),
    "BASISKELE": (40.7100, 29.9300),
    "GOLCUK": (40.7181, 29.8225),
    "KARAMURSEL": (40.6922, 29.6161),
    "KARTEPE": (40.7533, 30.0211),
    "KANDIRA": (41.0711, 30.1500),
    "DARICA": (40.7739, 29.4003),
    "DILOVASI": (40.7875, 29.5442),
    "CAYIROVA": (40.8142, 29.3756),
    # İstanbul ve İlçeleri
    "ISTANBUL": (41.0082, 28.9784),
    "TUZLA": (40.8167, 29.3000),
    "PENDIK": (40.8753, 29.2333),
    "KARTAL": (40.8886, 29.1856),
    "MALTEPE": (40.9244, 29.1311),
    "KADIKOY": (40.9901, 29.0292),
    "USKUDAR": (41.0267, 29.0578),
    "ATASEHIR": (40.9833, 29.1167),
    "UMRANIYE": (41.0256, 29.0961),
    "BEYKOZ": (41.1167, 29.1000),
    "SILE": (41.1750, 29.6125),
    "SANCAKTEPE": (40.9900, 29.2300),
    "SULTANBEYLI": (40.9667, 29.2667),
    "SARIYER": (41.1667, 29.0500),
    "BESIKTAS": (41.0428, 29.0075),
    "BEYOGLU": (41.0286, 28.9739),
    "FATIH": (41.0186, 28.9500),
    "BUYUKCEKMECE": (41.0214, 28.5839),
    "KUCUKCEKMECE": (40.9911, 28.7719),
    "SILIVRI": (41.0739, 28.2464),
    "BASAKSEHIR": (41.1000, 28.8000),
    # Diğer İller (Tüm 81 İl Merkezleri)
    "ADANA": (37.0000, 35.3213),
    "ADIYAMAN": (37.7644, 38.2786),
    "AFYONKARAHISAR": (38.7507, 30.5567),
    "AFYON": (38.7507, 30.5567),
    "AGRI": (39.7191, 43.0503),
    "AKSARAY": (38.3687, 34.0370),
    "AMASYA": (40.6499, 35.8353),
    "ANKARA": (39.9334, 32.8597),
    "ANTALYA": (36.8969, 30.7133),
    "ARDAHAN": (41.1105, 42.7022),
    "ARTVIN": (41.1828, 41.8183),
    "AYDIN": (37.8560, 27.8416),
    "BALIKESIR": (39.6484, 27.8826),
    "BARTIN": (41.6358, 32.3375),
    "BATMAN": (37.8812, 41.1351),
    "BAYBURT": (40.2552, 40.2249),
    "BILECIK": (40.1500, 29.9833),
    "BINGOL": (38.8853, 40.4980),
    "BITLIS": (38.4006, 42.1095),
    "BOLU": (40.7358, 31.6061),
    "BURDUR": (37.7203, 30.2908),
    "BURSA": (40.1885, 29.0610),
    "CANAKKALE": (40.1553, 26.4142),
    "CANKIRI": (40.6013, 33.6134),
    "CORUM": (40.5506, 34.9556),
    "DENIZLI": (37.7765, 29.0864),
    "DIYARBAKIR": (37.9144, 40.2306),
    "DUZCE": (40.8438, 31.1565),
    "EDIRNE": (41.6771, 26.5557),
    "ELAZIG": (38.6810, 39.2264),
    "ERZINCAN": (39.7500, 39.5000),
    "ERZURUM": (39.9000, 41.2700),
    "ESKISEHIR": (39.7767, 30.5206),
    "GAZIANTEP": (37.0662, 37.3833),
    "GIRESUN": (40.9128, 38.3895),
    "GUMUSHANE": (40.4600, 39.4814),
    "HAKKARI": (37.5833, 43.7333),
    "HATAY": (36.2000, 36.1667),
    "ANTAKYA": (36.2000, 36.1667),
    "ISKENDERUN": (36.5872, 36.1733),
    "IGDIR": (39.9167, 44.0333),
    "ISPARTA": (37.7644, 30.5564),
    "IZMIR": (38.4237, 27.1428),
    "KARABUK": (41.2061, 32.6203),
    "SAFRANBOLU": (41.2500, 32.6833),
    "KARAMAN": (37.1759, 33.2287),
    "KARS": (40.6167, 43.1000),
    "KASTAMONU": (41.3887, 33.7827),
    "KAYSERI": (38.7312, 35.4787),
    "KILIS": (36.7181, 37.1217),
    "KIRIKKALE": (39.8468, 33.5153),
    "KIRKLARELI": (41.7333, 27.2167),
    "KIRSEHIR": (39.1425, 34.1709),
    "KONYA": (37.8746, 32.4932),
    "KONYA EREGLI": (37.5133, 34.0483),
    "KUTAHYA": (39.4167, 29.9833),
    "MALATYA": (38.3552, 38.3095),
    "MANISA": (38.6191, 27.4289),
    "MARDIN": (37.3212, 40.7245),
    "MERSIN": (36.8000, 34.6333),
    "ICEL": (36.8000, 34.6333),
    "MUGLA": (37.2153, 28.3636),
    "BODRUM": (37.0383, 27.4292),
    "FETHIYE": (36.6217, 29.1164),
    "MARMARIS": (36.8550, 28.2742),
    "MUS": (38.7432, 41.5064),
    "NEVSEHIR": (38.6244, 34.7144),
    "NIGDE": (37.9667, 34.6833),
    "ORDU": (40.9839, 37.8764),
    "OSMANIYE": (37.0742, 36.2478),
    "RIZE": (41.0201, 40.5234),
    "SAKARYA": (40.7569, 30.3783),
    "ADAPAZARI": (40.7731, 30.4000),
    "SERDIVAN": (40.7600, 30.3500),
    "SAPANCA": (40.6908, 30.2694),
    "AKYAZI": (40.6833, 30.6167),
    "HENDEK": (40.7986, 30.7486),
    "SAMSUN": (41.2928, 36.3313),
    "SANLIURFA": (37.1674, 38.7954),
    "URFA": (37.1674, 38.7954),
    "SIIRT": (37.9333, 41.9500),
    "SINOP": (42.0231, 35.1531),
    "SIVAS": (39.7477, 37.0179),
    "SIRNAK": (37.5167, 42.4500),
    "TEKIRDAG": (40.9829, 27.5106),
    "CORLU": (41.1594, 27.8000),
    "TOKAT": (40.3167, 36.5500),
    "TRABZON": (41.0027, 39.7167),
    "TUNCELI": (39.1083, 39.5401),
    "USAK": (38.6823, 29.4082),
    "VAN": (38.4891, 43.4089),
    "YALOVA": (40.6547, 29.2842),
    "YOZGAT": (39.8181, 34.8147),
}


def calculate_distance_to_relay(qth_str):
    if not qth_str or qth_str.strip().upper() == "BİLİNMİYOR":
        return ""

    normalized_qth = tr_normalize(qth_str)

    matched_coord = None
    sorted_keys = sorted(CITY_COORDS.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in normalized_qth:
            matched_coord = CITY_COORDS[key]
            break

    if not matched_coord:
        return ""

    lat2, lon2 = matched_coord

    R = 6371.0
    dlat = math.radians(lat2 - ROLE_LAT)
    dlon = math.radians(lon2 - ROLE_LON)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(ROLE_LAT))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = round(R * c)

    return f"{distance_km} KM"


# --- GITHUB ÜZERİNE OTOMATİK QSL KARTI YÜKLEME ---
# QSL kartları GitHub deposunda tutulur.
# Her PDF oluşturma işleminde depo içindeki eski QSL dosyaları temizlenir
# ve yalnızca o çevrime ait yeni kartlar tek bir Git commit'i ile yayınlanır.
#
# GitHub bağlantı bilgileri.
# Token artık ayrı github_token.txt dosyasından değil, doğrudan main.py
# içindeki GITHUB_TOKEN sabitinden okunur.
GITHUB_OWNER = "gezentelsizcilerturkiye2025-pixel"
GITHUB_REPO = "qsl-kartlari"
GITHUB_BRANCH = "main"
GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
)
# GitHub tokenı kaynak koda gömülmez.
# Yerel bilgisayarda GitHub CLI (gh) tarafından güvenli şekilde saklanan
# kimlik bilgisinden alınır. `gh auth login` bir kez tamamlanmış olmalıdır.
GITHUB_LAST_ERROR = ""
_GITHUB_SESSION = None
_GITHUB_SESSION_LOCK = threading.Lock()


def _get_github_token():
    """GitHub tokenını GitHub CLI'nin yerel kimlik bilgisinden al."""
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "GitHub CLI (gh) bulunamadı. GitHub CLI kurulmalı ve "
            "'gh auth login' ile giriş yapılmalıdır."
        ) from exc
    except Exception as exc:
        raise RuntimeError(
            f"GitHub kimlik bilgisi alınamadı: {type(exc).__name__}: {exc}"
        ) from exc

    token = (result.stdout or "").strip()
    if result.returncode != 0 or not token:
        detail = (result.stderr or result.stdout or "bilinmeyen hata").strip()
        raise RuntimeError(
            "GitHub CLI kimlik doğrulaması bulunamadı. "
            "Önce 'gh auth login' çalıştırılmalıdır. "
            f"Ayrıntı: {detail[:300]}"
        )

    return token


def _get_github_session():
    """Thread'ler arasında güvenli şekilde paylaşılabilen requests Session."""
    global _GITHUB_SESSION
    with _GITHUB_SESSION_LOCK:
        if _GITHUB_SESSION is None:
            _GITHUB_SESSION = requests.Session()
            _GITHUB_SESSION.headers.update({
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Gezen-Telsizciler-NetLog",
            })
            token = _get_github_token()
            if token:
                _GITHUB_SESSION.headers["Authorization"] = f"Bearer {token}"
        return _GITHUB_SESSION


def _github_request(method, url, **kwargs):
    """GitHub API çağrısı; kısa timeout ve anlaşılır hata."""
    token = _get_github_token()
    if not token:
        raise RuntimeError(
            "GitHub tokenı main.py içindeki GITHUB_TOKEN alanında bulunamadı."
        )

    session = _get_github_session()
    headers = kwargs.pop("headers", {})
    headers = dict(headers)
    headers.setdefault("Authorization", f"Bearer {token}")
    headers.setdefault("Accept", "application/vnd.github+json")
    headers.setdefault("X-GitHub-Api-Version", "2022-11-28")
    headers.setdefault("User-Agent", "Gezen-Telsizciler-NetLog")
    kwargs["headers"] = headers
    kwargs.setdefault("timeout", (10, 90))

    response = session.request(method, url, **kwargs)
    if not response.ok:
        try:
            detail = response.json().get("message", response.text[:500])
        except Exception:
            detail = response.text[:500]
        raise RuntimeError(
            f"GitHub HTTP {response.status_code}: {detail}"
        )
    return response


def github_qsl_filename(callsign_only, archive_stamp):
    """GitHub'da benzersiz, URL-dostu QSL dosya yolu."""
    raw = str(callsign_only or "").strip().upper()
    clean = tr_normalize(raw).lower()
    safe = re.sub(r"[^a-z0-9._-]+", "_", clean)
    safe = safe.strip("._-") or "unknown"
    return f"qsl/{archive_stamp}_{safe}.jpg"


def get_qsl_public_url(callsign_only, archive_stamp=None, expires_in=None):
    """GitHub raw URL'sini üretir."""
    if not archive_stamp:
        archive_stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{GITHUB_RAW_BASE}/{github_qsl_filename(callsign_only, archive_stamp)}"


def _github_get_base_commit_and_tree():
    """main dalının mevcut commit ve tree SHA değerlerini al."""
    ref_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/git/ref/heads/{GITHUB_BRANCH}"
    )
    ref_data = _github_request("GET", ref_url).json()
    commit_sha = ref_data["object"]["sha"]

    commit_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/git/commits/{commit_sha}"
    )
    commit_data = _github_request("GET", commit_url).json()
    return commit_sha, commit_data["tree"]["sha"]


def _github_list_existing_files(tree_sha):
    """Mevcut Git tree içindeki dosyaları listeler."""
    tree_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/git/trees/{tree_sha}?recursive=1"
    )
    data = _github_request("GET", tree_url).json()
    return [
        item["path"]
        for item in data.get("tree", [])
        if item.get("type") == "blob"
    ]


def _github_create_blob(file_bytes):
    """QSL JPEG baytlarını GitHub Git Blob nesnesine yükler."""
    blob_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/blobs"
    )
    encoded = base64.b64encode(file_bytes).decode("ascii")
    last_error = None
    for attempt in range(1, 4):
        try:
            data = _github_request(
                "POST",
                blob_url,
                json={"content": encoded, "encoding": "base64"},
                timeout=(15, 180),
            ).json()
            return data["sha"]
        except Exception as e:
            last_error = e
            if attempt < 3:
                time.sleep(1.5 * attempt)
    raise last_error


def _github_commit_qsl_batch(qsl_items, archive_stamp):
    """
    QSL kartlarının tamamını tek Git commit'inde yayınlar.

    qsl_items:
        [(relative_path, file_bytes), ...]

    Avantajı:
      - Eski kartların temizlenmesi tek commit'te yapılır.
      - PDF'ler paralel blob olarak gönderilir.
      - Kullanıcı her kart için 2 ayrı Contents API çağrısı beklemez.
    """
    global GITHUB_LAST_ERROR
    GITHUB_LAST_ERROR = ""

    if not qsl_items:
        raise RuntimeError("Yüklenecek QSL kartı bulunamadı.")

    base_commit_sha, base_tree_sha = _github_get_base_commit_and_tree()
    existing_files = _github_list_existing_files(base_tree_sha)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    workers = min(6, max(1, len(qsl_items)))
    blob_results = [None] * len(qsl_items)
    failures = []

    def make_blob(index, item):
        rel_path, pdf_bytes = item
        try:
            return index, _github_create_blob(pdf_bytes), None
        except Exception as e:
            return index, None, f"{rel_path}: {type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(make_blob, i, item)
            for i, item in enumerate(qsl_items)
        ]
        for future in as_completed(futures):
            idx, sha, error = future.result()
            if error:
                failures.append(error)
            else:
                blob_results[idx] = sha
            print(
                f"GitHub QSL yükleme: "
                f"{sum(x is not None for x in blob_results)}/{len(qsl_items)} tamamlandı."
            )

    if failures:
        raise RuntimeError(
            "Bazı QSL kartlarının GitHub blob yüklemesi başarısız:\n"
            + "\n".join(failures[:10])
        )

    new_paths = {item[0] for item in qsl_items}

    # ARŞİV: Eski QSL kartlarına dokunma.
    # Her çevrim benzersiz tarih+saat+mikrosaniye adı kullandığı için
    # eski kartlar korunur ve iki hafta sonra bile indirilebilir.
    # base_tree mevcut eski dosyaları zaten korur; yalnızca yeni kartları ekle.
    tree_entries = []

    for (rel_path, _), blob_sha in zip(qsl_items, blob_results):
        tree_entries.append({
            "path": rel_path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha,
        })

    tree_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees"
    )
    tree_data = _github_request(
        "POST",
        tree_url,
        json={
            "base_tree": base_tree_sha,
            "tree": tree_entries,
        },
    ).json()
    new_tree_sha = tree_data["sha"]

    commit_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/commits"
    )
    commit_data = _github_request(
        "POST",
        commit_url,
        json={
            "message": f"QSL kartları - çevrim {archive_stamp}",
            "tree": new_tree_sha,
            "parents": [base_commit_sha],
        },
    ).json()
    new_commit_sha = commit_data["sha"]

    ref_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/git/refs/heads/{GITHUB_BRANCH}"
    )
    _github_request(
        "PATCH",
        ref_url,
        json={"sha": new_commit_sha, "force": False},
    )

    print(
        f"GitHub QSL: {len(qsl_items)} kart yayınlandı. "
        f"Eski dosya sayısı={len(existing_files)}; çevrim={archive_stamp}"
    )
    return True


def upload_qsl_bytes_to_github(pdf_bytes, callsign_only, archive_stamp=None):
    """
    Tek kartı GitHub blob olarak hazırlar.
    Toplu export sırasında gerçek commit işlemi _github_commit_qsl_batch
    tarafından yapılır.
    """
    if not archive_stamp:
        archive_stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    rel_path = github_qsl_filename(callsign_only, archive_stamp)
    sha = _github_create_blob(pdf_bytes)
    return rel_path, sha


def upload_qsl_to_github(pdf_path, callsign_only, archive_stamp=None, max_retries=2, verify=False):
    """Eski çağrılarla uyumluluk için dosyadan GitHub'a yükleyici."""
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    rel_path, _ = upload_qsl_bytes_to_github(
        pdf_bytes, callsign_only, archive_stamp=archive_stamp
    )

    # Tek kart için de ayrı commit oluştur.
    _github_commit_qsl_batch(
        [(rel_path, pdf_bytes)],
        archive_stamp or datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
    )
    return True


def delete_all_qsl_from_github():
    """
    GitHub deposundaki mevcut dosyaları temizlemek için compatibility
    yardımcı fonksiyonu. Toplu PDF işleminde ayrı ayrı silme yapılmaz;
    silmeler tek commit içinde gerçekleştirilir.
    """
    base_commit_sha, base_tree_sha = _github_get_base_commit_and_tree()
    existing_files = _github_list_existing_files(base_tree_sha)
    if not existing_files:
        return True

    tree_entries = [
        {"path": path, "mode": "100644", "type": "blob", "sha": None}
        for path in existing_files
    ]

    tree_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees"
    )
    new_tree_sha = _github_request(
        "POST",
        tree_url,
        json={"base_tree": base_tree_sha, "tree": tree_entries},
    ).json()["sha"]

    commit_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/commits"
    )
    commit_sha = _github_request(
        "POST",
        commit_url,
        json={
            "message": "Eski QSL kartlarını temizle",
            "tree": new_tree_sha,
            "parents": [base_commit_sha],
        },
    ).json()["sha"]

    ref_url = (
        f"{GITHUB_API_BASE}/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/git/refs/heads/{GITHUB_BRANCH}"
    )
    _github_request("PATCH", ref_url, json={"sha": commit_sha, "force": False})
    return True


# --- BİREYSEL QSL KARTI PDF OLUŞTURUCU ---
def generate_single_qsl_pdf(callsign, name, qth, theme_name, output_filename, timestamp=None, net_controllers=None):
    """
    Kullanıcının verdiği nostaljik QSL kartı görselini doğrudan PDF zemini olarak
    kullanır. Kartın üzerindeki sabit bilgiler görselde hazırdır; değişken bilgiler
    (çağrı işareti, isim, QTH, tarih/saat ve röle mesafesi) ilgili boş alanlara yazılır.
    """
    # QSL arka planı her kartta diskten tekrar açılmasın.
    # Bir kez RAM'e alınır ve bütün kartlar aynı ImageReader'ı kullanır.
    global _QSL_BACKGROUND_CACHE

    if _QSL_BACKGROUND_CACHE is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        background_candidates = [
            os.path.join(script_dir, "qsl_card_background.png"),
            os.path.join(script_dir, "qsl_card_background(1).png"),
            os.path.join(script_dir, "qsl_card_background(2).png"),
            os.path.join(script_dir, "qsl_card_background(3).png"),
        ]

        try:
            for filename in sorted(os.listdir(script_dir)):
                if (
                    filename.lower().startswith("qsl_card_background")
                    and filename.lower().endswith(".png")
                ):
                    full_path = os.path.join(script_dir, filename)
                    if full_path not in background_candidates:
                        background_candidates.append(full_path)
        except Exception:
            pass

        background_file = next(
            (f for f in background_candidates if os.path.isfile(f)), None
        )
        if not background_file:
            raise FileNotFoundError(
                "Nostaljik QSL kartı arka planı bulunamadı. "
                "qsl_card_background*.png dosyasını main.py ile aynı klasöre koyun."
            )

        from PIL import Image as PILImage

        with PILImage.open(background_file) as bg:
            bg_width, bg_height = bg.size
            bg_copy = bg.convert("RGBA").copy()

        # PNG arka planını bir kez JPEG'e çevir.
        # optimize=True özellikle çok sayıda kartta CPU'yu gereksiz yere artırıyordu.
        # 85 kalite görseli okunaklı tutarken dosya boyutunu ve üretim süresini düşürür.
        jpeg_buffer = io.BytesIO()
        bg_copy.convert("RGB").save(
            jpeg_buffer,
            format="JPEG",
            quality=85,
            optimize=False,
        )
        jpeg_bytes = jpeg_buffer.getvalue()
        _QSL_BACKGROUND_CACHE = (
            jpeg_bytes,
            bg_width,
            bg_height,
        )

    jpeg_bytes, bg_width, bg_height = _QSL_BACKGROUND_CACHE
    # ImageReader nesnesini her iş parçacığında ayrı oluştur:
    # ortak seek konumu nedeniyle paralel PDF üretiminde yarış oluşmasın.
    bg_reader = ImageReader(io.BytesIO(jpeg_bytes))

    # 100 px = yaklaşık 1 inch mantığıyla, görsel oranını koruyan PDF boyutu.
    page_width = 1105.2
    page_height = page_width * (bg_height / bg_width)

    c = canvas.Canvas(output_filename, pagesize=(page_width, page_height))

    # Arka plan görseli kartın tamamını kaplar.
    c.drawImage(
        bg_reader,
        0,
        0,
        width=page_width,
        height=page_height,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )

    # Görsel koordinatlarını PDF koordinatlarına çeviren yardımcılar.
    sx = page_width / float(bg_width)
    sy = page_height / float(bg_height)

    def X(px):
        return px * sx

    def Y(py):
        # Görselde koordinat 0 üstte, PDF'de 0 altta.
        return page_height - (py * sy)

    font_name = FONT_NAME if "FONT_NAME" in globals() else "Helvetica"
    bold_font = BOLD_FONT_NAME if "BOLD_FONT_NAME" in globals() else "Helvetica-Bold"

    def fit_text(text_value, max_width_px, start_size=16, min_size=8, bold=True):
        """Metni verilen piksel genişliğine sığacak puntoyu bul."""
        value = str(text_value or "").strip()
        if not value:
            return "", start_size
        size = start_size
        font = bold_font if bold else font_name
        while size > min_size:
            if c.stringWidth(value, font, size) <= X(max_width_px):
                break
            size -= 0.5
        return value, max(size, min_size)

    def draw_centered(text_value, center_x_px, baseline_y_px, max_width_px,
                      start_size=16, min_size=8, bold=True):
        value, size = fit_text(
            text_value, max_width_px, start_size=start_size,
            min_size=min_size, bold=bold
        )
        if not value:
            return
        c.setFont(bold_font if bold else font_name, size)
        c.drawCentredString(X(center_x_px), Y(baseline_y_px), value)

    def draw_left(text_value, x_px, baseline_y_px, max_width_px,
                  start_size=14, min_size=8, bold=True):
        value, size = fit_text(
            text_value, max_width_px, start_size=start_size,
            min_size=min_size, bold=bold
        )
        if not value:
            return
        c.setFont(bold_font if bold else font_name, size)
        c.drawString(X(x_px), Y(baseline_y_px), value)

    # ---------------------------------------------------------------
    # 1) TO RADIO / ÇAĞRI İŞARETİ
    # Kartta "TO RADIO" hücresinin altındaki boş alan.
    # ---------------------------------------------------------------
    draw_centered(
        str(callsign or "").strip().upper(),
        center_x_px=569,
        baseline_y_px=547,
        max_width_px=190,
        start_size=24,
        min_size=13,
        bold=True,
    )

    # ---------------------------------------------------------------
    # 2) TARİH ve SAAT
    # Çevrim kaydında saklanan tarih/saat kullanılır.
    # Böylece QSL kartındaki bilgi, kayıt altına alınan operatör ile birebir aynı kalır.
    # ---------------------------------------------------------------
    recorded_dt = None
    if timestamp:
        raw_ts = str(timestamp).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                recorded_dt = datetime.strptime(raw_ts, fmt)
                break
            except ValueError:
                pass
        if recorded_dt is None:
            try:
                recorded_dt = datetime.fromisoformat(raw_ts)
            except Exception:
                recorded_dt = None

    if recorded_dt is None:
        recorded_dt = datetime.now()

    draw_centered(
        recorded_dt.strftime("%d.%m.%Y"),
        center_x_px=780,
        baseline_y_px=547,
        max_width_px=165,
        start_size=24,
        min_size=10,
        bold=True,
    )
    draw_centered(
        recorded_dt.strftime("%H:%M:%S"),
        center_x_px=955,
        baseline_y_px=547,
        max_width_px=145,
        start_size=24,
        min_size=9,
        bold=True,
    )

    # ---------------------------------------------------------------
    # 3) SOL ALT / RADIO OPERATOR alanı
    # İsim, görseldeki operatör satırının içine yazılır.
    # ---------------------------------------------------------------
    # RADIO OPERATOR alanı: yazı hem yatay hem dikey ortalıdır.
    # OPERATÖR İSMİ: kutu içinde yatay + dikey ortalı, büyük ve kalın.
    # Operatör ismi 1 cm sola kaydırıldı.
    # Operatör ismi 5 mm daha sola kaydırıldı.
    draw_centered(
        str(name or "").strip().upper(),
        center_x_px=233,
        baseline_y_px=565,
        max_width_px=300,
        start_size=24,
        min_size=11,
        bold=True,
    )

    # QTH / KONUM alanı.
    draw_centered(
        str(qth or "").strip().upper(),
        center_x_px=238,
        baseline_y_px=680,
        max_width_px=345,
        start_size=24,
        min_size=11,
        bold=True,
    )

    # ---------------------------------------------------------------
    # 4) RÖLE MESAFESİ
    # ---------------------------------------------------------------
    dist_str = calculate_distance_to_relay(qth)
    # Kartta "km" ibaresi zaten basılıdır. Bu yüzden yalnızca sayısal
    # değeri (veya BİLİNMİYOR) yazıyoruz; "KM" tekrar edilmez.
    if dist_str:
        dist_value = str(dist_str).upper().replace(" KM", "").replace("KM", "").strip()
    else:
        dist_value = "BİLİNMİYOR"
    draw_centered(
        dist_value,
        center_x_px=720,
        baseline_y_px=768,
        max_width_px=95,
        start_size=24,
        min_size=10,
        bold=True,
    )

    # ---------------------------------------------------------------
    # 5) KÜRESEL QSL KARTI / TEMA
    # NOTES / MESSAGE kutusunun içine doğrudan yazılır.
    # Operatör adıyla aynı yazı karakteri, aynı 20 pt başlangıç boyutu
    # ve aynı kalınlık kullanılır. Arka plan/underlay eklenmez.
    theme_text = str(theme_name or "").strip()
    if theme_text:
        THEME_FONT_SIZE = 20
        THEME_MIN_SIZE = 11
        THEME_MAX_WIDTH = 330

        # Temayı kutuya sığacak şekilde en fazla 3 satıra böl.
        words = theme_text.split()
        lines = []
        current = ""
        while words:
            word = words.pop(0)
            candidate = (current + " " + word).strip()
            if not current or c.stringWidth(candidate, bold_font, THEME_FONT_SIZE) <= X(THEME_MAX_WIDTH):
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)

        # Çok uzun tema adlarında aynı karakter görünümünü koruyarak
        # yalnızca kutuya sığması için yazı puntosunu küçült.
        while len(lines) > 3 and THEME_FONT_SIZE > THEME_MIN_SIZE:
            THEME_FONT_SIZE -= 0.5
            words = theme_text.split()
            lines = []
            current = ""
            while words:
                word = words.pop(0)
                candidate = (current + " " + word).strip()
                if not current or c.stringWidth(candidate, bold_font, THEME_FONT_SIZE) <= X(THEME_MAX_WIDTH):
                    current = candidate
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)

        lines = lines[:3]

        # Örnekteki koyu bordo tonu; doğrudan kartın üzerindedir.
        c.setFillColorRGB(0.42, 0.05, 0.03)

        # Dünya görselinin altında, NOTES / MESSAGE kutusunun orta-alt
        # bölümüne dengeli şekilde yerleştir.
        line_gap = 30
        # Notlar / Mesaj kutusundaki tema 2 cm yukarı kaydırıldı.
        # 100 px/inç koordinat sisteminde 2 cm ≈ 79 px.
        # NOTES / MESSAGE içindeki tema 1 cm daha yukarı kaydırıldı.
        # NOTES / MESSAGE içindeki tema yazısı 2 mm aşağı kaydırıldı.
        # Mevcut 100 px/inç koordinat ölçeğinde 2 mm ≈ 8 px.
        if len(lines) == 1:
            baselines = [584]
        elif len(lines) == 2:
            baselines = [569, 599]
        else:
            baselines = [554, 584, 614]

        for line, baseline in zip(lines, baselines):
            draw_centered(
                line,
                center_x_px=1275,
                baseline_y_px=baseline,
                max_width_px=THEME_MAX_WIDTH,
                start_size=THEME_FONT_SIZE,
                min_size=THEME_MIN_SIZE,
                bold=True,
            )

    # ---------------------------------------------------------------
    # 5) SAĞ ÜST / NET CONTROL
    # Ana sayfadaki "Çevrimi Yapan Operatörler" bölümünde görünen
    # çağrı işareti + isim bilgisi QSL kartındaki sağ üst kutulara
    # BİREBİR aktarılır.
    #
    # Koordinatlar, kullanıcının verdiği gerçek QSL kartı görseli
    # (1535 x 1024 px) üzerinden ölçülmüştür.
    #
    # Sağ üstte 4 adet "ÇEVRİM OPERATÖRÜ:" kutusu vardır:
    #   1. kutu: yaklaşık y=256..309
    #   2. kutu: yaklaşık y=312..364
    #   3. kutu: yaklaşık y=367..418
    #   4. kutu: yaklaşık y=422..474
    #
    # NET CONTROL: etiketinin hemen sağındaki boş alana operatör bilgisi yazılır.
    # ---------------------------------------------------------------
    if net_controllers:
        controller_entries = []

        for controller in net_controllers:
            if len(controller) >= 2:
                controller_callsign = str(controller[0] or "").strip().upper()
                controller_name = str(controller[1] or "").strip().upper()

                if controller_callsign and controller_name:
                    controller_entries.append(
                        f"{controller_callsign} - {controller_name}"
                    )
                elif controller_name:
                    controller_entries.append(controller_name)
                elif controller_callsign:
                    controller_entries.append(controller_callsign)

        if controller_entries:
            # Gerçek kart ölçüsü: 1535 x 1024 px.
            # İsimlerin yazılacağı boş alan yaklaşık x=1260..1480 px.
            # "NET CONTROL:" etiketinin hemen sağındaki boş alan.
            # Kullanıcı isteği: çağrı işareti + isim, iki nokta üst üste
            # işaretinin hemen ardından, siyah ve 10 punto.
            CTRL_FONT_SIZE = 12  # Çevrim operatörü yazıları 12 punto
            CTRL_MIN_SIZE = 8
            CTRL_X = 1236  # Çevrim operatörü isimleri 5 mm sağa kaydırıldı (yaklaşık 19 px).  # Çevrim operatörü isimleri 1 cm sola kaydırıldı (yaklaşık 38 px).
            CTRL_MAX_WIDTH = 220

            # Gerçek kart görselindeki dört kutunun baseline konumları.
            CTRL_BASELINES = [287, 343, 398, 453]

            # Kartta yalnızca 4 Net Control kutusu vardır.
            for idx, controller_text in enumerate(controller_entries[:4]):
                value, size = fit_text(
                    controller_text,
                    CTRL_MAX_WIDTH,
                    start_size=CTRL_FONT_SIZE,
                    min_size=CTRL_MIN_SIZE,
                    bold=True,
                )
                if value:
                    c.setFillColor(colors.black)
                    c.setFont(bold_font, size)
                    c.drawString(
                        X(CTRL_X),
                        Y(CTRL_BASELINES[idx]),
                        value,
                    )

    # Sağ taraftaki teknik bilgi alanları: 17 punto, mevcut kalın font.
    # Kart üzerindeki eski baskının üzerine aynı bilgileri temiz ve okunaklı
    # biçimde yazar; kullanıcı istediği ölçüde doğrudan bu değerleri gösterir.
    TECH_FONT_SIZE = 17

    # Teknik metinleri sağ panelde tek satır/uygun genişlikte yaz.
    technical_items = [
        ("RÖLE: ANARAD - MATRAD", 900, 1045, 400),
        ("ECHOLINK: YM2KDB - YM2KCL", 900, 1085, 500),
        ("RÖLE FREKANSI: 439.375 MHz / 439.4125 MHz", 900, 1125, 500),
        ("MOD: FM/VOICE", 900, 1165, 400),
    ]
    for txt, x_px, y_px, width_px in technical_items:
        draw_left(
            txt,
            x_px=x_px,
            baseline_y_px=y_px,
            max_width_px=width_px,
            start_size=TECH_FONT_SIZE,
            min_size=10,
            bold=True,
        )

    # Kartın sabit teknik bilgileri kullanıcı tarafından istenen şekilde
    # görselin kendisinde zaten bulunuyor:
    # FREKANS 439.375 MHz / 439.4125 MHz
    # RÖLE ANARAD - MATRAD
    # BAND UHF
    # MODE FM
    # RAPOR 59
    # ECHOLINK YM2KDB

    c.showPage()
    c.save()


# --- QSL GÖREV İŞÇİSİ ---
# QSL kartları artık kayıt girildiğinde internete tek tek yüklenmez.
# Yükleme yalnızca "PDF ÇEVRİM LİSTESİ OLUŞTUR" sırasında toplu yapılır.
class QSLTaskRunner(QRunnable):
    def __init__(self, callsign, name, qth, session_id, timestamp=None):
        super().__init__()
        self.callsign = callsign
        self.name = name
        self.qth = qth
        self.session_id = session_id
        self.timestamp = timestamp
        self.setAutoDelete(True)

    def run(self):
        # Bilerek boş bırakıldı: PDF export sırasında toplu GitHub commit'i yapılır.
        return


# --- PDF DIŞA AKTARIMI İÇİN GUI THREAD SİNYALLERİ ---
class PDFExportSignals(QObject):
    finished = pyqtSignal(str, str, bool)


# --- ÇOKLU DİL SÖZLÜĞÜ ---
TRANSLATIONS = {
    "TR": {
        "window_title": "Gezen Telsizciler Türkiye Çevrimi",
        "dir_btn": "📂 Operatör Veri Tabanı",
        "ctrl_btn": "🎙️ Çevrimi Yapan Operatörler",
        "stats_btn": "📊 Çevrim İstatistikleri",
        "logbook_btn": "📖 Logbook (Geçmiş Sorgula)",
        "gift_menu": "🎁 Hediye Sistemi",
        "qsl_menu": "🌐 TEMALI QSL KARTI",
        "echolink_btn": "🌐 ECHOLINK",
        "demo_menu": "🚀 Demo Modu",
        "normal_menu": "🔙 Normal Moda Dön",
        "lang_menu": "🌐 Dil / Language / Sprache",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_en": "🇬🇧 English",
        "lang_de": "🇩🇪 Deutsch",
        "header_title": "GEZEN TELSİZCİLER TÜRKİYE ÇEVRİMİ",
        "date_lbl": "TARİH",
        "time_lbl": "SAAT",
        "no_controller": "ÇEVRİMİ YAPAN OPERATÖR TANIMLANMADI",
        "controllers_prefix": "ÇEVRİMİ YAPAN OPERATÖRLER:",
        "center_title": "ÇEVRİM KAYIT VE GİRİŞ EKRANI",
        "callsign_lbl": "ÇAĞRI İŞARETİ",
        "callsign_ph": "Büyük harfle yazılır veya listeden seçilir...",
        "name_lbl": "İSİM SOYİSİM",
        "name_ph": "İsim büyük harfe çevrilir...",
        "qth_lbl": "QTH / KONUM",
        "qth_ph": "Konum büyük harfe çevrilir (Örn: DÖRPEN, GERMANY)...",
        "notes_lbl": "NOTLAR",
        "notes_ph": "Not büyük harfe çevrilir veya direkt yazılır...",
        "save_btn": "KAYDET (ENTER)",
        "close_net_btn": "🔒 KAYITLARI DURDUR",
        "open_net_btn": "🔓 KAYITLARI AÇ",
        "right_title": "KAYIT ALTINA ALINAN OPERATÖRLER",
        "total_part": "TOPLAM KATILIM",
        "th_call": "ÇAĞRI İŞARETİ",
        "th_name": "İSİM",
        "th_qth": "QTH",
        "th_dist": "RÖLE MESAFESİ",
        "th_notes": "NOTLAR",
        "th_date": "TARİH",
        "th_gift": "HEDİYE",
        "del_rec_btn": "SEÇİLİ KAYDI SİL",
        "draw_btn": "ÇEKİLİŞ YAP / ROLLE RAFFLE",
        "live_raffle_btn": "📺 CANLI ÇEKİLİŞ EKRANI",
        "pdf_btn": "PDF ÇEVRİM LİSTESİ OLUŞTUR",
        "reset_btn": "♻ KOMPLE LİSTEYİ SIFIRLA (YENİ OTURUM)",
        "echolink_count": "EchoLink Katılımı",
        "analog_count": "Analog Katılımı",
        "stats_format": "🌐 EchoLink: {e_count} (%{e_pct})  |  📻 Analog: {a_count} (%{a_pct})",
    },
    "EN": {
        "window_title": "Gezen Telsizciler Turkey Net",
        "dir_btn": "📂 Operator Database",
        "ctrl_btn": "🎙️ Net Controllers",
        "stats_btn": "📊 Net Statistics",
        "logbook_btn": "📖 Logbook (Query History)",
        "gift_menu": "🎁 Gift System",
        "qsl_menu": "🌐 Global QSL Card",
        "echolink_btn": "🌐 ECHOLINK",
        "demo_menu": "🚀 Demo Mode",
        "normal_menu": "🔙 Back to Normal Mode",
        "lang_menu": "🌐 Dil / Language / Sprache",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_en": "🇬🇧 English",
        "lang_de": "🇩🇪 Deutsch",
        "header_title": "GEZEN TELSİZCİLER TÜRKİYE ÇEVRİMİ",
        "date_lbl": "DATE",
        "time_lbl": "TIME",
        "no_controller": "NO NET CONTROLLER DEFINED",
        "controllers_prefix": "NET CONTROLLERS:",
        "center_title": "NET CHECK-IN & ENTRY SCREEN",
        "callsign_lbl": "CALLSIGN",
        "callsign_ph": "Type in uppercase or select from list...",
        "name_lbl": "NAME SURNAME",
        "name_ph": "Name converted to uppercase...",
        "qth_lbl": "QTH / LOCATION",
        "qth_ph": "Location converted to uppercase...",
        "notes_lbl": "NOTES",
        "notes_ph": "Notes converted to uppercase...",
        "save_btn": "SAVE (ENTER)",
        "close_net_btn": "🔒 STOP REGISTRATIONS",
        "open_net_btn": "🔓 OPEN REGISTRATIONS",
        "right_title": "LOGGED OPERATORS",
        "total_part": "TOTAL PARTICIPANTS",
        "th_call": "CALLSIGN",
        "th_name": "NAME",
        "th_qth": "QTH",
        "th_dist": "RELAY DIST.",
        "th_notes": "NOTES",
        "th_date": "DATE",
        "th_gift": "PRIZE",
        "del_rec_btn": "DELETE SELECTED RECORD",
        "draw_btn": "RUN RAFFLE / DRAW",
        "live_raffle_btn": "📺 LIVE RAFFLE SCREEN",
        "pdf_btn": "CREATE PDF NET LIST",
        "reset_btn": "♻ RESET FULL LIST (NEW SESSION)",
        "echolink_count": "EchoLink Participation",
        "analog_count": "Analog Participation",
        "stats_format": "🌐 EchoLink: {e_count} ({e_pct}%)  |  📻 Analog: {a_count} ({a_pct}%)",
    },
    "DE": {
        "window_title": "Gezen Telsizciler Türkei Net",
        "dir_btn": "📂 Operatoren-Datenbank",
        "ctrl_btn": "🎙️ Netto-Controller",
        "stats_btn": "📊 Netzstatistiken",
        "logbook_btn": "📖 Logbuch (Historie abfragen)",
        "gift_menu": "🎁 Geschenksystem",
        "qsl_menu": "🌐 Globale QSL-Karte",
        "echolink_btn": "🌐 ECHOLINK",
        "demo_menu": "🚀 Demo-Modus",
        "normal_menu": "🔙 Zurück zum Normalmodus",
        "lang_menu": "🌐 Dil / Language / Sprache",
        "lang_tr": "🇹🇷 Türkçe",
        "lang_en": "🇬🇧 English",
        "lang_de": "🇩🇪 Deutsch",
        "header_title": "GEZEN TELSİZCİLER TÜRKİYE ÇEVRİMİ",
        "date_lbl": "DATUM",
        "time_lbl": "ZEIT",
        "no_controller": "KEIN NETZ-CONTROLLER DEFINIERT",
        "controllers_prefix": "NETZ-CONTROLLER:",
        "center_title": "NETZ-EINCHECKEN & EINGABEBILDSCHIRM",
        "callsign_lbl": "RUFZEICHEN",
        "callsign_ph": "In Großbuchstaben eingeben oder aus Liste wählen...",
        "name_lbl": "VORNAME NACHNAME",
        "name_ph": "Name in Großbuchstaben umgewandelt...",
        "qth_lbl": "QTH / STANDORT",
        "qth_ph": "Standort in Großbuchstaben umgewandelt...",
        "notes_lbl": "NOTIZEN",
        "notes_ph": "Notizen eingeben...",
        "save_btn": "SPEICHERN (ENTER)",
        "close_net_btn": "🔒 REGISTRIERUNGEN STOPPEN",
        "open_net_btn": "🔓 REGISTRIERUNGEN ÖFFNEN",
        "right_title": "PROTOKOLLIERTE OPERATOREN",
        "total_part": "GESAMTE TEILNEHMER",
        "th_call": "RUFZEICHEN",
        "th_name": "NAME",
        "th_qth": "QTH",
        "th_dist": "RELAIS DISTANZ",
        "th_notes": "NOTIZEN",
        "th_date": "DATUM",
        "th_gift": "PREIS",
        "del_rec_btn": "AUSGEWÄHLTEN DATENSATZ LÖSCHEN",
        "draw_btn": "VERLOSUNG STARTEN",
        "live_raffle_btn": "📺 LIVE-VERLOSUNG",
        "pdf_btn": "PDF-NETZLISTE ERSTELLEN",
        "reset_btn": "♻ GESAMTE LISTE ZURÜCKSETZEN (NEUE SITZUNG)",
        "echolink_count": "EchoLink-Teilnahme",
        "analog_count": "Analog-Teilnahme",
        "stats_format": "🌐 EchoLink: {e_count} ({e_pct}%)  |  📻 Analog: {a_count} ({a_pct}%)",
    },
}


def get_text(lang, key):
    return TRANSLATIONS.get(lang, TRANSLATIONS["TR"]).get(
        key, TRANSLATIONS["TR"].get(key, key)
    )


def get_or_create_session_id():
    if os.path.exists("session_id.txt"):
        with open("session_id.txt", "r") as f:
            return f.read().strip()
    else:
        new_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        with open("session_id.txt", "w") as f:
            f.write(new_id)
        return new_id


try:
    pdfmetrics.registerFont(TTFont("Arial", "C:\\Windows\\Fonts\\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "C:\\Windows\\Fonts\\arialbd.ttf"))
    FONT_NAME = "Arial"
    BOLD_FONT_NAME = "Arial-Bold"
except:
    FONT_NAME = "Helvetica"
    BOLD_FONT_NAME = "Helvetica-Bold"


def sort_key_callsign(callsign_str):
    call = str(callsign_str).strip().upper().split(" ")[0]
    number = 99
    suffix = call

    if call.startswith("TA"):
        prefix_order = 0
        rest = call[2:]
    elif call.startswith("TB"):
        prefix_order = 1
        rest = call[2:]
    else:
        prefix_order = 2
        rest = call

    if rest and rest[0].isdigit():
        number = int(rest[0])
        suffix = rest[1:]
    else:
        number = 99
        suffix = rest

    return (prefix_order, number, suffix)


# --- KÜRESEL / ÖZEL GÜNLER QSL KARTI YÖNETİM DİALOGU ---
class GlobalQSLDialog(QDialog):
    """Küresel/Özel QSL tema seçimi ve tema kütüphanesi yönetimi."""

    DEFAULT_THEMES = [
        "GEZEN TELSİZCİLER TÜRKİYE KURULUŞ YILDÖNÜMÜ",
        "HAFTALIK GEZEN TELSİZCİLER TÜRKİYE ÇEVRİMİ",
        "18 NİSAN DÜNYA AMATÖR\nTELSİZCİLER GÜNÜ",
        "29 EKİM – 4 KASIM KIZILAY\nHAFTASI QSL KARTI",
        "YENİ YIL QSL KARTI",
        "YILIN SON ÇEVRİMİ QSL KARTI",
        "RAMAZAN BAYRAMI QSL KARTI",
        "KURBAN BAYRAMI QSL KARTI",
        "ANNELER GÜNÜ ÖZEL ÇEVRİMİ",
        "BABALAR GÜNÜ ÖZEL ÇEVRİMİ",
        "18 MART ÇANAKKALE ZAFERİ VE\nŞEHİTLER GÜNÜ",
        "10 KASIM ATATÜRK’Ü ANMA GÜNÜ",
        "23 NİSAN ULUSAL EGEMENLİK VE\nÇOCUK BAYRAMI",
        "19 MAYIS GENÇLİK VE SPOR\nBAYRAMI",
        "30 AĞUSTOS ZAFER BAYRAMI",
        "29 EKİM CUMHURİYET BAYRAMI",
        "6 ŞUBAT 2023 KAHRAMANMARAŞ\nVE HATAY DEPREMLERİ",
        "17 AĞUSTOS 1999 MARMARA\nDEPREMİ (GÖLCÜK / KOCAELİ)",
        "12 KASIM 1999 DÜZCE DEPREMİ",
        "6 ŞUBAT 2023 KAHRAMANMARAŞ\nVE HATAY DEPREMLERİ",
        "23 EKİM 2011 VAN DEPREMİ",
        "26 ARALIK 1939 ERZİNCAN\nDEPREMİ",
    ]

    def __init__(self, parent=None, lang="TR"):
        super().__init__(parent)
        self.lang = lang
        self.parent_window = parent
        self.setWindowTitle(
            "Küresel ve Özel Günler QSL Kartı Seçimi / Tema Yönetimi"
            if lang == "TR"
            else "Global & Special Days QSL Card Selection / Theme Manager"
        )
        self.resize(720, 600)
        self.setStyleSheet("""
            QDialog { background-color: #F8F9FA; }
            QPushButton {
                background-color: #E9ECEF;
                color: #212529;
                border: 1px solid #ADB5BD;
                font-weight: bold;
                padding: 8px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #DEE2E6;
                color: #000000;
            }
            QMessageBox QPushButton {
                background-color: #E9ECEF;
                color: #212529;
                border: 1px solid #ADB5BD;
                min-width: 80px;
                min-height: 28px;
                padding: 5px 16px;
            }
            QMessageBox QPushButton:hover {
                background-color: #CED4DA;
                color: #000000;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title_lbl = QLabel(
            "Çevrim için QSL kartı temasını seçin. Aşağıdaki butonlarla tema ekleyebilir, düzenleyebilir veya silebilirsiniz."
            if lang == "TR"
            else "Select a QSL card theme. You can add, edit or delete themes with the buttons below."
        )
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #0D47A1;")
        title_lbl.setWordWrap(True)
        layout.addWidget(title_lbl)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #CED4DA;
                border-radius: 6px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #0D47A1;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.list_widget, 1)

        theme_note_group = QGroupBox("TEMA NOTES / MESSAGE ALANINDA YAZILSIN MI?")
        theme_note_layout = QHBoxLayout(theme_note_group)

        self.radio_theme_note_yes = QRadioButton("EVET")
        self.radio_theme_note_no = QRadioButton("HAYIR")
        self.theme_note_group = QButtonGroup(self)
        self.theme_note_group.addButton(self.radio_theme_note_yes)
        self.theme_note_group.addButton(self.radio_theme_note_no)
        self.radio_theme_note_yes.setChecked(True)

        theme_note_layout.addWidget(self.radio_theme_note_yes)
        theme_note_layout.addWidget(self.radio_theme_note_no)
        layout.addWidget(theme_note_group)

        manage_layout = QHBoxLayout()

        self.btn_add = QPushButton("➕ TEMA EKLE")
        self.btn_add.setStyleSheet("QPushButton { background:#198754; } QPushButton:hover { background:#157347; }")
        self.btn_add.clicked.connect(self.add_theme)

        self.btn_edit = QPushButton("✏️ SEÇİLİ TEMAYI DÜZENLE")
        self.btn_edit.setStyleSheet("QPushButton { background:#0D6EFD; } QPushButton:hover { background:#0B5ED7; }")
        self.btn_edit.clicked.connect(self.edit_theme)


        manage_layout.addWidget(self.btn_add)
        manage_layout.addWidget(self.btn_edit)
        layout.addLayout(manage_layout)

        info_lbl = QLabel(
            "Yeni temalar program kapanıp açılsa bile saklanır. Tema adı QSL kartında kullanılacak başlık olarak kaydedilir."
            if lang == "TR"
            else "New themes are saved permanently. The theme name is stored as the title used for the QSL card."
        )
        info_lbl.setStyleSheet("color:#495057; font-size:11px;")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)

        btn_layout = QHBoxLayout()

        self.btn_delete = QPushButton(
            "SEÇİLİ TEMAYI SİL" if lang == "TR" else "DELETE SELECTED THEME"
        )
        self.btn_delete.setStyleSheet(
            "QPushButton { background:#C62828; color:white; font-weight:bold; padding:6px 12px; } "
            "QPushButton:hover { background:#A91E1E; }"
        )
        self.btn_delete.clicked.connect(self.delete_selected_theme)

        self.btn_select = QPushButton(
            "SEÇ" if lang == "TR" else "SELECT"
        )
        self.btn_select.setStyleSheet(
            "QPushButton { background:#198754; color:white; font-weight:bold; padding:6px 16px; } "
            "QPushButton:hover { background:#157347; }"
        )
        self.btn_select.clicked.connect(self.save_selection)

        self.btn_cancel = QPushButton("İPTAL" if lang == "TR" else "CANCEL")
        self.btn_cancel.setStyleSheet("QPushButton { background:#6C757D; } QPushButton:hover { background:#5A6268; }")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("SEÇİMİ KAYDET" if lang == "TR" else "SAVE SELECTION")
        self.btn_save.setStyleSheet("QPushButton { background:#0D47A1; } QPushButton:hover { background:#1565C0; }")
        self.btn_save.clicked.connect(self.save_selection)

        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.ensure_theme_table()
        self.load_theme_library()
        self.load_current_selection()

    def db_connect(self):
        return sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)

    def ensure_theme_table(self):
        conn = self.db_connect()
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS qsl_theme_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_name TEXT NOT NULL UNIQUE,
                    sort_order INTEGER NOT NULL DEFAULT 0
                )
            """)
            cur.execute("SELECT COUNT(*) FROM qsl_theme_library")
            count = cur.fetchone()[0]
            if count == 0:
                for idx, theme in enumerate(self.DEFAULT_THEMES):
                    cur.execute(
                        "INSERT OR IGNORE INTO qsl_theme_library(theme_name, sort_order) VALUES (?, ?)",
                        (theme, idx)
                    )
            conn.commit()
        finally:
            conn.close()

    def load_theme_library(self):
        conn = self.db_connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT theme_name FROM qsl_theme_library ORDER BY sort_order, id"
            )
            self.events_list = [row[0] for row in cur.fetchall()]
        finally:
            conn.close()

        self.list_widget.clear()
        self.list_widget.addItems(self.events_list)

    def add_theme(self):
        title = "Yeni QSL Teması Ekle"
        prompt = (
            "Yeni tema adını yazın. Alt satıra geçmek için \\n kullanabilirsiniz:"
            if self.lang == "TR"
            else "Enter the new theme name. Use \\n for a line break:"
        )
        value, ok = QInputDialog.getText(self, title, prompt)
        if not ok:
            return
        value = value.strip().upper()
        if not value:
            return

        conn = self.db_connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COALESCE(MAX(sort_order), -1) + 1 FROM qsl_theme_library")
            next_order = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO qsl_theme_library(theme_name, sort_order) VALUES (?, ?)",
                (value, next_order)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Uyarı", "Bu tema zaten mevcut.")
            return
        finally:
            conn.close()

        self.load_theme_library()
        items = self.list_widget.findItems(value, Qt.MatchFlag.MatchExactly)
        if items:
            self.list_widget.setCurrentItem(items[0])

    def edit_theme(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Uyarı", "Önce düzenlenecek temayı seçin.")
            return

        old_name = item.text()
        value, ok = QInputDialog.getText(
            self,
            "Temayı Düzenle",
            "Yeni tema adı:",
            text=old_name
        )
        if not ok:
            return

        new_name = value.strip().upper()
        if not new_name or new_name == old_name:
            return

        conn = self.db_connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE qsl_theme_library SET theme_name=? WHERE theme_name=?",
                (new_name, old_name)
            )
            if cur.rowcount == 0:
                QMessageBox.warning(self, "Hata", "Tema bulunamadı.")
                return

            # Daha önce bu tema seçilmiş oturumları da yeni isimle güncelle.
            cur.execute(
                "UPDATE session_qsl_theme SET theme_name=? WHERE theme_name=?",
                (new_name, old_name)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Uyarı", "Bu isimde bir tema zaten mevcut.")
            return
        finally:
            conn.close()

        self.load_theme_library()
        items = self.list_widget.findItems(new_name, Qt.MatchFlag.MatchExactly)
        if items:
            self.list_widget.setCurrentItem(items[0])

    def delete_selected_theme(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "Uyarı",
                "Önce silinecek temayı seçin." if self.lang == "TR"
                else "Please select a theme to delete."
            )
            return

        theme_name = item.text()

        # EVET / HAYIR düğmelerini açıkça görünür yap.
        confirm = QMessageBox(self)
        confirm.setWindowTitle("TEMAYI SİL")
        confirm.setText(
            f"“{theme_name}” temasını silmek istediğinizden emin misiniz?"
        )
        confirm.setIcon(QMessageBox.Icon.Question)

        yes_btn = confirm.addButton(
            "EVET", QMessageBox.ButtonRole.YesRole
        )
        no_btn = confirm.addButton(
            "HAYIR", QMessageBox.ButtonRole.NoRole
        )
        confirm.setDefaultButton(no_btn)

        confirm.setStyleSheet("""
            QMessageBox {
                background-color: #F2F2F2;
            }
            QMessageBox QLabel {
                color: #000000;
                font-size: 13px;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 7px 20px;
                min-width: 90px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                color: #000000;
            }
        """)
        confirm.exec()

        if confirm.clickedButton() is not yes_btn:
            return

        conn = self.db_connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM qsl_theme_library WHERE theme_name=?",
                (theme_name,)
            )
            cur.execute(
                "DELETE FROM session_qsl_theme WHERE theme_name=?",
                (theme_name,)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            QMessageBox.warning(
                self,
                "Hata",
                f"Tema silinemedi: {e}"
            )
            return
        finally:
            conn.close()

        self.load_theme_library()
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)


    def load_current_selection(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_qsl_theme (
                    session_id TEXT PRIMARY KEY,
                    theme_name TEXT
                )
            """)
            session_id = self.parent_window.net_session_id if self.parent_window else get_or_create_session_id()
            cursor.execute(
                "SELECT theme_name FROM session_qsl_theme WHERE session_id=?",
                (session_id,)
            )
            res = cursor.fetchone()
            conn.close()

            if res and res[0]:
                items = self.list_widget.findItems(res[0], Qt.MatchFlag.MatchExactly)
                if items:
                    self.list_widget.setCurrentItem(items[0])
                    return

            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
        except Exception:
            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)

    def save_selection(self):
        selected_item = self.list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self,
                "Uyarı",
                "Lütfen bir tema seçin!" if self.lang == "TR" else "Please select a theme!"
            )
            return

        selected_theme = selected_item.text()
        theme_note_visible = self.radio_theme_note_yes.isChecked()
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_qsl_theme (
                    session_id TEXT PRIMARY KEY,
                    theme_name TEXT
                )
            """)
            session_id = self.parent_window.net_session_id if self.parent_window else get_or_create_session_id()
            cursor.execute(
                "INSERT OR REPLACE INTO session_qsl_theme(session_id, theme_name) VALUES (?, ?)",
                (session_id, selected_theme)
            )
            conn.commit()
            conn.close()

            if self.parent_window is not None:
                self.parent_window.show_theme_in_notes = theme_note_visible

            if self.lang == "TR":
                note_status = (
                    "HAYIR işaretlendi: Tema QSL kartının NOTES / MESSAGE alanında gösterilmeyecek."
                    if not theme_note_visible
                    else "EVET işaretlendi: Tema QSL kartının NOTES / MESSAGE alanında gösterilecek."
                )
                info_message = (
                    f"Küresel QSL Kartı teması başarıyla kaydedildi:\n\n"
                    f"{selected_theme}\n\n{note_status}"
                )
            else:
                note_status = (
                    "NO selected: The theme will not be shown in the QSL card NOTES / MESSAGE area."
                    if not theme_note_visible
                    else "YES selected: The theme will be shown in the QSL card NOTES / MESSAGE area."
                )
                info_message = (
                    f"Global QSL Card theme saved successfully:\n\n"
                    f"{selected_theme}\n\n{note_status}"
                )

            QMessageBox.information(
                self,
                "Başarılı" if self.lang == "TR" else "Success",
                info_message
            )
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kayıt sırasında hata oluştu: {str(e)}")


class NetStatisticsDialog(QDialog):
    def __init__(self, parent=None, lang="TR"):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "Çevrim İstatistikleri Arşivi"
            if lang == "TR"
            else (
                "Net Statistics Archive"
                if lang == "EN"
                else "Netto-Statistikarchiv"
            )
        )
        self.resize(750, 480)
        self.parent_window = parent

        layout = QVBoxLayout()

        info_text = (
            "Kaydedilen tüm çevrim istatistikleri. Seçerek silebilir veya tüm"
            " arşiv istatistiklerini sıfırlayabilirsiniz:"
            if lang == "TR"
            else (
                "All saved net statistics. You can select and delete them or"
                " reset all:"
                if lang == "EN"
                else "Gespeicherte Netzstatistiken:"
            )
        )
        info_lbl = QLabel(info_text)
        info_lbl.setStyleSheet("color: #004D40; font-weight: bold;")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)

        self.table = QTableWidget(0, 6)
        th1 = "NO"
        th2 = (
            "TARİH / OTURUM"
            if lang == "TR"
            else ("DATE / SESSION" if lang == "EN" else "DATUM / SITZUNG")
        )
        th3 = (
            "TOPLAM KATILIM"
            if lang == "TR"
            else ("TOTAL PARTICIPANTS" if lang == "EN" else "GESAMTE TEILNEHMER")
        )
        th4 = "ECHOLİNK" if lang == "TR" else ("ECHOLINK" if lang == "EN" else "ECHOLINK")
        th5 = "ANALOG" if lang == "TR" else ("ANALOG" if lang == "EN" else "ANALOG")
        th6 = (
            "ORANLAR (%)"
            if lang == "TR"
            else ("RATIOS (%)" if lang == "EN" else "VERHÄLTNIS (%)")
        )
        self.table.setHorizontalHeaderLabels([th1, th2, th3, th4, th5, th6])
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_delete_selected = QPushButton(
            "Seçili İstatistiği Sil"
            if lang == "TR"
            else (
                "Delete Selected Statistic"
                if lang == "EN"
                else "Ausgewählte Statistik löschen"
            )
        )
        btn_delete_selected.clicked.connect(self.delete_selected_stat)
        btn_delete_selected.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
        """)

        btn_delete_all = QPushButton(
            "Tüm İstatistikleri Sıfırla"
            if lang == "TR"
            else (
                "Reset All Statistics"
                if lang == "EN"
                else "Alle Statistiken zurücksetzen"
            )
        )
        btn_delete_all.clicked.connect(self.delete_all_stats)
        btn_delete_all.setStyleSheet("""
            QPushButton {
                background-color: #C62828;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8E0000;
            }
        """)

        btn_layout.addWidget(btn_delete_selected)
        btn_layout.addWidget(btn_delete_all)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_stats()

    def load_stats(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, session_id, session_date, total_count, echolink_count,"
            " analog_count, echolink_pct, analog_pct FROM net_session_stats"
            " ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        conn.close()

        for idx, row in enumerate(rows):
            self.table.insertRow(idx)
            db_id = row[0]

            item_no = QTableWidgetItem(str(idx + 1))
            item_no.setData(Qt.ItemDataRole.UserRole, db_id)
            item_no.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_no.setFlags(item_no.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 0, item_no)

            item_date = QTableWidgetItem(str(row[2]))
            item_date.setFlags(item_date.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 1, item_date)

            item_tot = QTableWidgetItem(str(row[3]))
            item_tot.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_tot.setFlags(item_tot.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 2, item_tot)

            item_echo = QTableWidgetItem(f"{row[4]} (%{round(row[6], 1)})")
            item_echo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_echo.setFlags(item_echo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 3, item_echo)

            item_analog = QTableWidgetItem(f"{row[5]} (%{round(row[7], 1)})")
            item_analog.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_analog.setFlags(item_analog.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 4, item_analog)

            item_ratio = QTableWidgetItem(
                f"EchoLink: %{round(row[6], 1)}  |  Analog: %{round(row[7], 1)}"
            )
            item_ratio.setFlags(item_ratio.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 5, item_ratio)

    def delete_selected_stat(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return

        item = self.table.item(current_row, 0)
        db_id = item.data(Qt.ItemDataRole.UserRole)

        msg = (
            "Seçilen istatistik kaydını silmek istediğinize emin misiniz?"
            if self.lang == "TR"
            else "Are you sure you want to delete the selected statistic record?"
        )
        reply = QMessageBox.question(
            self,
            "Silme Onayı",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM net_session_stats WHERE id=?", (db_id,)
            )
            conn.commit()
            conn.close()
            self.load_stats()

    def delete_all_stats(self):
        msg = (
            "Tüm istatistik arşivini sıfırlamak istediğinize emin misiniz?"
            if self.lang == "TR"
            else "Are you sure you want to reset all statistics records?"
        )
        reply = QMessageBox.question(
            self,
            "Tümünü Sıfırlama Onayı",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM net_session_stats")
            conn.commit()
            conn.close()
            self.load_stats()


class NetControllersDialog(QDialog):
    def __init__(self, parent=None, lang="TR"):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "Çevrimi Yapan Operatörler Yönetimi"
            if lang == "TR"
            else (
                "Net Controllers Management"
                if lang == "EN"
                else "Netto-Controller Verwaltung"
            )
        )
        self.resize(500, 400)

        self.parent_window = parent
        self.session_id = (
            parent.net_session_id if parent else get_or_create_session_id()
        )

        layout = QVBoxLayout()

        controller_form = QFormLayout()
        self.input_ctrl_call = QLineEdit()
        self.input_ctrl_call.setPlaceholderText(
            "Çağrı işareti (Örn: TA2TTL)"
            if lang == "TR"
            else (
                "Callsign (e.g. TA2TTL)" if lang == "EN" else "Rufzeichen (z.B. TA2TTL)"
            )
        )
        self.input_ctrl_call.setStyleSheet(
            "border: 1px solid #004D40; border-radius: 3px; padding: 4px;"
        )
        self.input_ctrl_call.returnPressed.connect(self.save_net_controller)

        self.input_ctrl_name = QLineEdit()
        self.input_ctrl_name.setPlaceholderText(
            "İsim Soyisim"
            if lang == "TR"
            else ("Name Surname" if lang == "EN" else "Vorname Nachname")
        )
        self.input_ctrl_name.setStyleSheet(
            "border: 1px solid #004D40; border-radius: 3px; padding: 4px;"
        )
        self.input_ctrl_name.returnPressed.connect(self.save_net_controller)

        controller_form.addRow(
            "ÇAĞRI İŞARETİ:"
            if lang == "TR"
            else ("CALLSIGN:" if lang == "EN" else "RUFZEICHEN:"),
            self.input_ctrl_call,
        )
        controller_form.addRow(
            "İSİM SOYİSİM:"
            if lang == "TR"
            else ("NAME SURNAME:" if lang == "EN" else "VORNAME NACHNAME:"),
            self.input_ctrl_name,
        )
        layout.addLayout(controller_form)

        btn_text = (
            "Çevrimi Yapanı Ekle (ENTER)"
            if lang == "TR"
            else (
                "Add Net Controller (ENTER)"
                if lang == "EN"
                else "Net Controller Hinzufügen (ENTER)"
            )
        )
        btn_add_ctrl = QPushButton(btn_text)
        btn_add_ctrl.clicked.connect(self.save_net_controller)
        btn_add_ctrl.setStyleSheet("""
            QPushButton {
                background-color: #003300;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #001A00;
            }
        """)
        layout.addWidget(btn_add_ctrl)

        self.table_controllers = QTableWidget(0, 3)
        th1 = "NO"
        th2 = (
            "ÇAĞRI İŞARETİ"
            if lang == "TR"
            else ("CALLSIGN" if lang == "EN" else "RUFZEICHEN")
        )
        th3 = "İSİM" if lang == "TR" else ("NAME" if lang == "EN" else "NAME")
        self.table_controllers.setHorizontalHeaderLabels([th1, th2, th3])
        self.table_controllers.setColumnWidth(0, 50)
        self.table_controllers.horizontalHeader().setStretchLastSection(True)
        self.table_controllers.verticalHeader().setVisible(False)

        self.table_controllers.setStyleSheet("""
            QTableWidget {
                border: 1px solid #B2DFDB;
                gridline-color: #B2DFDB;
                background-color: #FFFFFF;
            }
            QTableWidget::item {
                border: none;
                border-bottom: 1px solid #E0F2F1;
                border-right: 1px solid #E0F2F1;
                padding: 4px;
            }
            QHeaderView::section {
                border: none;
                border-bottom: 1px solid #B2DFDB;
                border-right: 1px solid #B2DFDB;
                background-color: #E8F5E9;
                color: #003300;
                font-weight: bold;
                padding: 4px;
            }
        """)

        layout.addWidget(self.table_controllers)

        btn_del_text = (
            "Seçili Operatörü Sil"
            if lang == "TR"
            else (
                "Delete Selected Operator"
                if lang == "EN"
                else "Ausgewählten Operator löschen"
            )
        )
        btn_del_ctrl = QPushButton(btn_del_text)
        btn_del_ctrl.clicked.connect(self.delete_net_controller)
        btn_del_ctrl.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
        """)
        layout.addWidget(btn_del_ctrl)

        self.setLayout(layout)
        self.load_controllers()

    def load_controllers(self):
        self.table_controllers.setRowCount(0)
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, callsign, name FROM net_controllers WHERE session_id=? ORDER"
            " BY id ASC",
            (self.session_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        for row_idx, row_data in enumerate(rows):
            self.table_controllers.insertRow(row_idx)

            num_item = QTableWidgetItem(str(row_idx + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFlags(num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            num_item.setData(Qt.ItemDataRole.UserRole, row_data[0])
            num_item.setBackground(QColor("#E8F5E9"))
            self.table_controllers.setItem(row_idx, 0, num_item)

            for col_idx in range(2):
                val = (
                    str(row_data[col_idx + 1])
                    .upper()
                    .replace("i", "İ")
                    .replace("ı", "I")
                    if row_data[col_idx + 1]
                    else ""
                )
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, row_data[0])
                self.table_controllers.setItem(row_idx, col_idx + 1, item)

    def save_net_controller(self):
        callsign = self.input_ctrl_call.text().strip().upper().split(" ")[0]
        name = (
            self.input_ctrl_name.text()
            .strip()
            .upper()
            .replace("i", "İ")
            .replace("ı", "I")
        )

        if not callsign or not name:
            return

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO net_controllers (session_id, callsign, name) VALUES (?,"
                " ?, ?)",
                (self.session_id, callsign, name),
            )
            conn.commit()
            conn.close()
            self.input_ctrl_call.clear()
            self.input_ctrl_name.clear()
            self.load_controllers()

            if self.parent_window and hasattr(
                self.parent_window, "update_net_controllers_label"
            ):
                self.parent_window.update_net_controllers_label()

            self.input_ctrl_call.setFocus()
        except Exception as e:
            conn.close()
            QMessageBox.warning(self, "Hata", f"Kayıt hatası: {str(e)}")

    def delete_net_controller(self):
        current_row = self.table_controllers.currentRow()
        if current_row < 0:
            return

        item = self.table_controllers.item(current_row, 1)
        db_id = item.data(Qt.ItemDataRole.UserRole)

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM net_controllers WHERE id=?", (db_id,))
        conn.commit()
        conn.close()
        self.load_controllers()

        if self.parent_window and hasattr(
            self.parent_window, "update_net_controllers_label"
        ):
            self.parent_window.update_net_controllers_label()


class OperatorDirectoryDialog(QDialog):
    def __init__(self, parent=None, lang="TR"):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "Operatör Veri Tabanı (Düzenlenebilir)"
            if lang == "TR"
            else (
                "Operator Database (Editable)"
                if lang == "EN"
                else "Operatoren-Datenbank (Bearbeitbar)"
            )
        )
        self.setSizeGripEnabled(True)
        self.resize(780, 520)
        self.parent_window = parent

        layout = QVBoxLayout()

        is_demo = self.parent_window and getattr(
            self.parent_window, "is_demo_mode", False
        )
        if is_demo:
            info_text = (
                "Demo Modu Operatör Havuzu (Yalnızca demo oturumuna ait kayıtlar"
                " gösterilmektedir):"
                if lang == "TR"
                else (
                    "Demo Mode Operator Pool (Only records belonging to the demo"
                    " session are shown):"
                    if lang == "EN"
                    else "Demo-Modus Operatoren-Pool:"
                )
            )
        else:
            info_text = (
                "Kayıtlı çevrim operatörleri havuzu. Herhangi bir hücreyi düzenleyip"
                " enter tuşuna bastığınızda güncellenir:"
                if lang == "TR"
                else (
                    "Registered net operators pool. When you edit any cell and press"
                    " enter, records are updated:"
                    if lang == "EN"
                    else "Registrierter Netto-Betreiber-Pool."
                )
            )
        info_lbl = QLabel(info_text)
        info_lbl.setStyleSheet("color: #004D40; font-weight: bold;")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)

        search_layout = QHBoxLayout()
        search_label = QLabel(
            "🔍 Arama (Çağrı İşareti / İsim):"
            if lang == "TR"
            else (
                "🔍 Search (Callsign / Name):"
                if lang == "EN"
                else "🔍 Suche (Rufzeichen / Name):"
            )
        )
        search_label.setStyleSheet("font-weight: bold; color: #003300;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Aramak istediğiniz çağrı işaretini veya ismi yazın..."
            if lang == "TR"
            else (
                "Type callsign or name to search..."
                if lang == "EN"
                else "Rufzeichen oder Namen zum Suchen eingeben..."
            )
        )
        self.search_input.setStyleSheet(
            "border: 1px solid #004D40; border-radius: 3px; padding: 5px;"
            " background-color: #FFFFFF;"
        )
        self.search_input.textChanged.connect(self.filter_data)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table = QTableWidget(0, 4)
        th1 = (
            "ÇAĞRI İŞARETİ"
            if lang == "TR"
            else ("CALLSIGN" if lang == "EN" else "RUFZEICHEN")
        )
        th2 = (
            "İSİM SOYİSİM"
            if lang == "TR"
            else ("NAME SURNAME" if lang == "EN" else "VORNAME NACHNAME")
        )
        th3 = (
            "QTH / KONUM"
            if lang == "TR"
            else ("QTH / LOCATION" if lang == "EN" else "QTH / STANDORT")
        )
        th4 = "NOTLAR" if lang == "TR" else ("NOTES" if lang == "EN" else "NOTIZEN")
        self.table.setHorizontalHeaderLabels([th1, th2, th3, th4])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        btn_delete_one = QPushButton(
            "Seçili Operatörü Sil"
            if lang == "TR"
            else (
                "Delete Selected Operator"
                if lang == "EN"
                else "Ausgewählten Operator löschen"
            )
        )
        btn_delete_one.clicked.connect(self.delete_selected_operator)
        btn_delete_one.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
        """)

        btn_delete_all = QPushButton(
            "Komple Operatör Veri Tabanını Sil"
            if lang == "TR"
            else (
                "Delete Full Operator Database"
                if lang == "EN"
                else "Gesamte Operatoren-Datenbank löschen"
            )
        )
        btn_delete_all.clicked.connect(self.delete_all_operators)
        btn_delete_all.setStyleSheet("""
            QPushButton {
                background-color: #9B1C1C;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #8E0000;
            }
        """)

        btn_layout.addWidget(btn_delete_one)
        btn_layout.addWidget(btn_delete_all)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS operator_pool (id INTEGER PRIMARY KEY"
            " AUTOINCREMENT, callsign TEXT UNIQUE, name TEXT, qth TEXT, notes TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS demo_operator_pool (id INTEGER PRIMARY KEY"
            " AUTOINCREMENT, callsign TEXT UNIQUE, name TEXT, qth TEXT, notes TEXT)"
        )
        try:
            cursor.execute("ALTER TABLE operator_pool ADD COLUMN notes TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE demo_operator_pool ADD COLUMN notes TEXT")
        except:
            pass

        is_demo = self.parent_window and getattr(
            self.parent_window, "is_demo_mode", False
        )
        if is_demo:
            cursor.execute(
                "SELECT id, callsign, name, qth, notes FROM demo_operator_pool"
            )
        else:
            cursor.execute("SELECT id, callsign, name, qth, notes FROM operator_pool")

        fetched_rows = cursor.fetchall()
        conn.close()

        self.all_rows = sorted(fetched_rows, key=lambda x: sort_key_callsign(x[1]))

        self.populate_table(self.all_rows)
        self.table.blockSignals(False)

    def populate_table(self, rows):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            db_id = row_data[0]
            old_callsign_val = str(row_data[1]).upper() if row_data[1] else ""

            for col_idx in range(4):
                val = (
                    str(row_data[col_idx + 1])
                    .upper()
                    .replace("i", "İ")
                    .replace("ı", "I")
                    if row_data[col_idx + 1]
                    else ""
                )
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, db_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, old_callsign_val)
                self.table.setItem(row_idx, col_idx, item)
        self.table.blockSignals(False)

    def filter_data(self, text):
        search_query = (
            text.strip().upper().replace("i", "İ").replace("ı", "I")
        )
        if not search_query:
            self.populate_table(self.all_rows)
            return

        filtered_rows = []
        for row in self.all_rows:
            callsign = str(row[1]).upper() if row[1] else ""
            name = (
                str(row[2]).upper().replace("i", "İ").replace("ı", "I")
                if row[2]
                else ""
            )
            qth = (
                str(row[3]).upper().replace("i", "İ").replace("ı", "I")
                if row[3]
                else ""
            )
            notes = (
                str(row[4]).upper().replace("i", "İ").replace("ı", "I")
                if row[4]
                else ""
            )

            if (
                search_query in callsign
                or search_query in name
                or search_query in qth
                or search_query in notes
            ):
                filtered_rows.append(row)

        self.populate_table(filtered_rows)

    def on_item_changed(self, item):
        if not item:
            return

        row = item.row()
        column = item.column()
        db_id = item.data(Qt.ItemDataRole.UserRole)
        old_callsign = item.data(Qt.ItemDataRole.UserRole + 1)
        new_value = (
            item.text().strip().upper().replace("i", "İ").replace("ı", "I")
        )

        if column == 0:
            field_name = "callsign"
        elif column == 1:
            field_name = "name"
        elif column == 2:
            field_name = "qth"
        elif column == 3:
            field_name = "notes"
        else:
            return

        is_demo = self.parent_window and getattr(
            self.parent_window, "is_demo_mode", False
        )
        table_name = "demo_operator_pool" if is_demo else "operator_pool"

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"UPDATE {table_name} SET {field_name}=? WHERE id=?", (new_value, db_id)
            )

            if self.parent_window and hasattr(self.parent_window, "net_session_id"):
                session_id = self.parent_window.net_session_id
                if column == 0:
                    cursor.execute(
                        "UPDATE logs SET callsign=? WHERE callsign=? AND session_id=?",
                        (new_value, old_callsign, session_id),
                    )
                elif column == 1:
                    call_item = self.table.item(row, 0)
                    current_call = (
                        call_item.text().strip().upper() if call_item else old_callsign
                    )
                    cursor.execute(
                        "UPDATE logs SET op_name=? WHERE callsign=? AND session_id=?",
                        (new_value, current_call, session_id),
                    )
                elif column == 2:
                    call_item = self.table.item(row, 0)
                    current_call = (
                        call_item.text().strip().upper() if call_item else old_callsign
                    )
                    cursor.execute(
                        "UPDATE logs SET qth=? WHERE callsign=? AND session_id=?",
                        (new_value, current_call, session_id),
                    )
                elif column == 3:
                    call_item = self.table.item(row, 0)
                    current_call = (
                        call_item.text().strip().upper() if call_item else old_callsign
                    )
                    cursor.execute(
                        "UPDATE logs SET notes=? WHERE callsign=? AND session_id=?",
                        (new_value, current_call, session_id),
                    )

            conn.commit()
            conn.close()

            if column == 0:
                item.setData(Qt.ItemDataRole.UserRole + 1, new_value)

            self.load_data()
            if self.parent_window and hasattr(
                self.parent_window, "load_operator_pool_from_db"
            ):
                self.parent_window.load_operator_pool_from_db()
            if self.parent_window and hasattr(self.parent_window, "refresh_table"):
                self.parent_window.refresh_table()
        except Exception as e:
            conn.close()
            self.load_data()

    def delete_selected_operator(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return

        item = self.table.item(current_row, 0)
        if not item:
            return

        callsign = item.text().strip()
        if not callsign:
            return

        msg = (
            f"'{callsign}' çağrı işaretli operatörü silmek istediğinize emin misiniz?"
            if self.lang == "TR"
            else (
                f"Are you sure you want to delete the operator with callsign '{callsign}'?"
                if self.lang == "EN"
                else (
                    "Möchten Sie den Operator mit dem Rufzeichen "
                    f"'{callsign}' wirklich löschen?"
                )
            )
        )
        reply = QMessageBox.question(
            self,
            "Silme Onayı",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        db_id = item.data(Qt.ItemDataRole.UserRole)
        is_demo = bool(
            self.parent_window and
            getattr(self.parent_window, "is_demo_mode", False)
        )
        table_name = "demo_operator_pool" if is_demo else "operator_pool"

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()

        try:
            # 1) Operatör veri tabanındaki seçili kaydı sil.
            cursor.execute(
                f"DELETE FROM {table_name} WHERE id=?",
                (db_id,)
            )

            # 2) ANA SAYFADAKİ "KAYIT ALTINA ALINAN OPERATÖRLER"
            #    listesi logs tablosundan oluşturuluyor.
            #    Bu yüzden aynı çağrı işaretine ait aktif oturum kayıtlarını
            #    doğrudan logs tablosundan da siliyoruz.
            parent = self.parent_window
            current_user_id = (
                parent.current_user[0]
                if parent is not None and getattr(parent, "current_user", None)
                else None
            )
            current_session_id = (
                parent.net_session_id
                if parent is not None and getattr(parent, "net_session_id", None)
                else None
            )

            if current_user_id is not None and current_session_id:
                # Önce mevcut oturumdaki logs kayıtlarını bul.
                cursor.execute(
                    "SELECT id, callsign FROM logs "
                    "WHERE user_id=? AND session_id=?",
                    (current_user_id, current_session_id),
                )
                log_rows = cursor.fetchall()

                # Ana listedeki gösterim de çağrı işaretini ilk boşlukta
                # kesebildiği için karşılaştırmayı normalize ediyoruz.
                wanted = callsign.strip().upper()
                ids_to_delete = []

                for log_id, log_call in log_rows:
                    stored = str(log_call or "").strip().upper()
                    displayed = stored.split(" ")[0] if stored else ""

                    if stored == wanted or displayed == wanted:
                        ids_to_delete.append(log_id)

                for log_id in ids_to_delete:
                    cursor.execute(
                        "DELETE FROM logs WHERE id=?",
                        (log_id,)
                    )

            conn.commit()

        except Exception as e:
            conn.rollback()
            QMessageBox.warning(
                self,
                "Hata",
                f"Operatör silinirken hata oluştu:\n{e}"
            )
            conn.close()
            return

        conn.close()

        # 3) Hem veri tabanı penceresini hem ana sayfadaki listeyi
        #    hemen yeniden yükle.
        self.load_data()

        if parent and hasattr(parent, "load_operator_pool_from_db"):
            parent.load_operator_pool_from_db()

        if parent and hasattr(parent, "refresh_table"):
            parent.refresh_table()


    def delete_all_operators(self):
        if self.table.rowCount() == 0:
            return

        is_demo = self.parent_window and getattr(
            self.parent_window, "is_demo_mode", False
        )
        table_name = "demo_operator_pool" if is_demo else "operator_pool"

        if is_demo:
            warn_msg = (
                "Demo modundasınız! Komple operatör veri tabanını silmek"
                " üzeresiniz. Emin misiniz?"
                if self.lang == "TR"
                else (
                    "You are in demo mode! You are about to delete the full operator"
                    " database. Are you sure?"
                    if self.lang == "EN"
                    else "Sie befinden sich im Demo-Modus!"
                )
            )
        else:
            warn_msg = (
                "Komple operatör veri tabanını silmek istediğinize emin misiniz?"
                if self.lang == "TR"
                else (
                    "Are you sure you want to delete the full operator database?"
                    if self.lang == "EN"
                    else "Gesamte Operatoren-Datenbank löschen?"
                )
            )

        reply = QMessageBox.question(
            self,
            "Komple Silme Onayı",
            warn_msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name}")
            conn.commit()
            conn.close()

            if self.parent_window and hasattr(
                self.parent_window, "load_operator_pool_from_db"
            ):
                self.parent_window.load_operator_pool_from_db()
            if self.parent_window and hasattr(self.parent_window, "refresh_table"):
                self.parent_window.refresh_table()

            self.load_data()
            if self.parent_window and hasattr(
                self.parent_window, "load_operator_pool_from_db"
            ):
                self.parent_window.load_operator_pool_from_db()
            if self.parent_window and hasattr(self.parent_window, "refresh_table"):
                self.parent_window.refresh_table()


class LogbookDialog(QDialog):
    def __init__(self, parent=None, lang="TR"):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "Logbook - Operatör Çevrim Geçmişi"
            if lang == "TR"
            else (
                "Logbook - Operator Net History"
                if lang == "EN"
                else "Logbuch - Netto-Betreiber-Historie"
            )
        )
        self.resize(700, 520)
        self.parent_window = parent

        layout = QVBoxLayout()

        info_text = (
            "Bir operatörün tüm geçmiş çevrim katılımlarını görmek için çağrı"
            " işaretini yazın:"
            if lang == "TR"
            else (
                "Type callsign to see all past net participations of an operator:"
                if lang == "EN"
                else "Geben Sie das Rufzeichen ein:"
            )
        )
        info_lbl = QLabel(info_text)
        info_lbl.setStyleSheet("color: #004D40; font-weight: bold;")
        layout.addWidget(info_lbl)

        search_layout = QHBoxLayout()
        search_label = QLabel(
            "ÇAĞRI İŞARETİ:"
            if lang == "TR"
            else ("CALLSIGN:" if lang == "EN" else "RUFZEICHEN:")
        )
        search_label.setStyleSheet("font-weight: bold; color: #003300;")

        self.input_search_call = QLineEdit()
        self.input_search_call.setPlaceholderText(
            "Örn: TA2TTL (Büyük harfle yazın veya seçin)"
            if lang == "TR"
            else ("e.g. TA2TTL" if lang == "EN" else "z.B. TA2TTL")
        )
        self.input_search_call.setStyleSheet(
            "border: 1px solid #004D40; border-radius: 3px; padding: 5px;"
            " background-color: #FFFFFF;"
        )

        self.setup_completer()

        btn_search = QPushButton(
            "Sorgula" if lang == "TR" else ("Query" if lang == "EN" else "Abfragen")
        )
        btn_search.clicked.connect(self.search_logbook)
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #00796B;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #004D40;
            }
        """)
        self.input_search_call.returnPressed.connect(self.search_logbook)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.input_search_call)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        self.lbl_summary = QLabel(
            "Toplam Katılım: -"
            if lang == "TR"
            else (
                "Total Participation: -"
                if lang == "EN"
                else "Gesamte Teilnahme: -"
            )
        )
        self.lbl_summary.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1B5E20; margin-top: 5px;"
        )
        layout.addWidget(self.lbl_summary)

        self.table_logbook = QTableWidget(0, 5)
        th1 = "NO"
        th2 = (
            "TARIH / SAAT"
            if lang == "TR"
            else ("DATE / TIME" if lang == "EN" else "DATUM / ZEIT")
        )
        th3 = "İSİM" if lang == "TR" else ("NAME" if lang == "EN" else "NAME")
        th4 = "QTH" if lang == "TR" else ("QTH" if lang == "EN" else "QTH")
        th5 = (
            "RÖLE MESAFESİ"
            if lang == "TR"
            else ("RELAY DIST." if lang == "EN" else "RELAIS DIST.")
        )
        self.table_logbook.setHorizontalHeaderLabels([th1, th2, th3, th4, th5])
        self.table_logbook.setColumnWidth(0, 50)
        self.table_logbook.horizontalHeader().setStretchLastSection(True)
        self.table_logbook.verticalHeader().setVisible(False)
        layout.addWidget(self.table_logbook)

        btn_layout = QHBoxLayout()

        btn_delete_single = QPushButton(
            "Seçili Kaydı Sil"
            if lang == "TR"
            else (
                "Delete Selected Record"
                if lang == "EN"
                else "Ausgewählten Datensatz löschen"
            )
        )
        btn_delete_single.clicked.connect(self.delete_single_logbook_record)
        btn_delete_single.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
        """)

        btn_reset_logbook = QPushButton(
            "Logbook'u Sıfırla"
            if lang == "TR"
            else (
                "Reset Logbook" if lang == "EN" else "Logbuch zurücksetzen"
            )
        )
        btn_reset_logbook.clicked.connect(self.reset_logbook_database)
        btn_reset_logbook.setStyleSheet("""
            QPushButton {
                background-color: #C62828;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8E0000;
            }
        """)

        btn_layout.addWidget(btn_delete_single)
        btn_layout.addWidget(btn_reset_logbook)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def setup_completer(self):
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()

            is_demo = self.parent_window and getattr(
                self.parent_window, "is_demo_mode", False
            )
            if is_demo:
                demo_session = getattr(
                    self.parent_window, "demo_session_id", "demo_session_id_9999"
                )
                cursor.execute(
                    "SELECT DISTINCT callsign FROM logs WHERE callsign IS NOT NULL AND"
                    " session_id=?",
                    (demo_session,),
                )
            else:
                cursor.execute(
                    "SELECT DISTINCT callsign FROM logs WHERE callsign IS NOT NULL AND"
                    " session_id != 'demo_session_id_9999'"
                )

            rows = cursor.fetchall()
            conn.close()
            calls = [r[0] for r in rows if r[0]]
            completer = QCompleter(calls, self)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
            self.input_search_call.setCompleter(completer)
        except:
            pass

    def search_logbook(self):
        callsign = self.input_search_call.text().strip().upper().split(" ")[0]
        if not callsign:
            return

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()

        is_demo = self.parent_window and getattr(
            self.parent_window, "is_demo_mode", False
        )
        if is_demo:
            demo_session = getattr(
                self.parent_window, "demo_session_id", "demo_session_id_9999"
            )
            cursor.execute(
                "SELECT id, timestamp, op_name, qth FROM logs WHERE callsign=? AND"
                " session_id=? ORDER BY timestamp DESC",
                (callsign, demo_session),
            )
        else:
            cursor.execute(
                "SELECT id, timestamp, op_name, qth FROM logs WHERE callsign=? AND"
                " session_id != 'demo_session_id_9999' ORDER BY timestamp DESC",
                (callsign,),
            )

        rows = cursor.fetchall()
        conn.close()

        self.table_logbook.setRowCount(0)
        count = len(rows)
        summary_text = (
            f"'{callsign}' Çağrı İşaretli Operatörün Toplam Katılım Sayısı:"
            f" {count}"
            if self.lang == "TR"
            else (
                f"Total Participations for Callsign '{callsign}': {count}"
                if self.lang == "EN"
                else (
                    f"Gesamte Teilnahmen für Rufzeichen '{callsign}': {count}"
                )
            )
        )
        self.lbl_summary.setText(summary_text)

        for idx, row_data in enumerate(rows):
            self.table_logbook.insertRow(idx)

            num_item = QTableWidgetItem(str(idx + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFlags(num_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            num_item.setData(Qt.ItemDataRole.UserRole, row_data[0])
            self.table_logbook.setItem(idx, 0, num_item)

            date_item = QTableWidgetItem(str(row_data[1]))
            date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            date_item.setData(Qt.ItemDataRole.UserRole, row_data[0])
            self.table_logbook.setItem(idx, 1, date_item)

            name_item = QTableWidgetItem(
                str(row_data[2])
                .upper()
                .replace("i", "İ")
                .replace("ı", "I")
                if row_data[2]
                else ""
            )
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, row_data[0])
            self.table_logbook.setItem(idx, 2, name_item)

            raw_qth = (
                str(row_data[3]).upper().replace("i", "İ").replace("ı", "I")
                if row_data[3]
                else ""
            )
            dist = calculate_distance_to_relay(raw_qth)

            qth_item = QTableWidgetItem(raw_qth)
            qth_item.setFlags(qth_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            qth_item.setData(Qt.ItemDataRole.UserRole, row_data[0])
            self.table_logbook.setItem(idx, 3, qth_item)

            dist_item = QTableWidgetItem(dist if dist else "-")
            dist_item.setFlags(dist_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            dist_item.setData(Qt.ItemDataRole.UserRole, row_data[0])
            self.table_logbook.setItem(idx, 4, dist_item)

    def delete_single_logbook_record(self):
        current_row = self.table_logbook.currentRow()
        if current_row < 0:
            return

        item = self.table_logbook.item(current_row, 0)
        db_id = item.data(Qt.ItemDataRole.UserRole)

        date_item = self.table_logbook.item(current_row, 1)
        date_str = date_item.text() if date_item else ""

        msg = (
            f"Seçilen bu geçmiş katılım kaydını ({date_str}) silmek istediğinize"
            " emin misiniz?"
            if self.lang == "TR"
            else (
                f"Are you sure you want to delete this selected past participation"
                f" record ({date_str})?"
                if self.lang == "EN"
                else "Möchten Sie den ausgewählten vergangenen Datensatz löschen?"
            )
        )
        reply = QMessageBox.question(
            self,
            "Silme Onayı",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logs WHERE id=?", (db_id,))
            conn.commit()
            conn.close()

            self.search_logbook()
            self.setup_completer()

    def reset_logbook_database(self):
        msg = (
            "Tüm Logbook geçmişini sıfırlamak istediğinize emin misiniz? Bu işlem"
            " geri alınamaz!"
            if self.lang == "TR"
            else (
                "Are you sure you want to reset all Logbook history?"
                if self.lang == "EN"
                else "Möchten Sie den Logbuch-Verlauf wirklich zurücksetzen?"
            )
        )
        reply = QMessageBox.question(
            self,
            "Logbook Sıfırlama Onayı",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()

            is_demo = self.parent_window and getattr(
                self.parent_window, "is_demo_mode", False
            )
            if is_demo:
                demo_session = getattr(
                    self.parent_window, "demo_session_id", "demo_session_id_9999"
                )
                cursor.execute("DELETE FROM logs WHERE session_id=?", (demo_session,))
            else:
                cursor.execute(
                    "DELETE FROM logs WHERE session_id != 'demo_session_id_9999'"
                )

            conn.commit()
            conn.close()

            self.input_search_call.clear()
            self.table_logbook.setRowCount(0)
            self.lbl_summary.setText(
                "Toplam Katılım: -"
                if self.lang == "TR"
                else (
                    "Total Participation: -"
                    if self.lang == "EN"
                    else "Gesamte Teilnahme: -"
                )
            )
            self.setup_completer()


class GiftEditDialog(QDialog):
    def __init__(self, parent=None, lang="TR"):
        super().__init__(parent)
        self.lang = lang
        self.parent_window = parent
        self.setWindowTitle(
            "Çekiliş Hediyeleri Yönetimi"
            if lang == "TR"
            else ("Raffle Gifts Management" if lang == "EN" else "Verlosungsgeschenke Verwaltung")
        )
        self.resize(520, 700)

        main_layout = QVBoxLayout(self)

        info_lbl = QLabel(
            "Hediyeyi yazın. ENTER yeni satır açmaz. "
            "Aşağıdaki butona basarak sınırsız sayıda yeni hediye satırı ekleyebilirsiniz. "
            "Beğenmediğiniz satırı SİL ile kaldırabilirsiniz."
        )
        info_lbl.setWordWrap(True)
        main_layout.addWidget(info_lbl)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.form_layout = QFormLayout(scroll_widget)
        self.form_layout.setVerticalSpacing(6)
        self.gift_rows = []
        self.load_gifts_from_db()
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area, 1)

        # Yeni hediye ekleme butonu
        self.btn_add_new = QPushButton("YENİ SATIR EKLE")
        self.btn_add_new.clicked.connect(self.append_new_gift_row)
        main_layout.addWidget(self.btn_add_new)

        # Tam sıfırlama butonu: büyük kırmızı, en altta.
        self.btn_reset_all = QPushButton("🗑 TÜM HEDİYELERİ TEK TUŞLA SİL")
        self.btn_reset_all.setMinimumHeight(48)
        self.btn_reset_all.setStyleSheet("""
            QPushButton {
                background-color: #C62828;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #A91E1E;
            }
        """)
        self.btn_reset_all.clicked.connect(self.reset_all_gifts_confirmed)
        main_layout.addWidget(self.btn_reset_all)

        # Kaydet / İptal sadece düğmeyle çalışır.
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.save_gifts)
        self.button_box.rejected.connect(self.reject)
        for b in self.button_box.buttons():
            b.setAutoDefault(False)
            b.setDefault(False)
        main_layout.addWidget(self.button_box)

    def _session_where(self):
        is_demo = bool(
            self.parent_window and getattr(self.parent_window, "is_demo_mode", False)
        )
        if is_demo:
            return "session_id=?", (
                getattr(
                    self.parent_window,
                    "demo_session_id",
                    "demo_session_id_9999",
                ),
            )
        return "(session_id IS NULL OR session_id != 'demo_session_id_9999')", ()

    def load_gifts_from_db(self):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self.gift_rows.clear()

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        try:
            try:
                cur.execute("ALTER TABLE gifts ADD COLUMN session_id TEXT")
            except sqlite3.OperationalError:
                pass

            where, params = self._session_where()
            cur.execute(
                "SELECT id, gift_number, name, is_assigned "
                f"FROM gifts WHERE {where} ORDER BY gift_number",
                params,
            )
            rows = cur.fetchall()
        finally:
            conn.close()

        for row in rows:
            self.create_row_ui(*row)

    def create_row_ui(self, g_id, g_num, g_name, is_assigned):
        line_edit = QLineEdit(
            str(g_name or "").upper().replace("i", "İ").replace("ı", "I")
        )
        line_edit.setPlaceholderText(f"{g_num}. Hediye ismini yazın...")
        line_edit.installEventFilter(self)

        btn_del = QPushButton("SİL")
        btn_del.setFixedWidth(55)
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
        """)
        btn_del.clicked.connect(
            lambda checked=False, le=line_edit, gid=g_id:
            self.delete_single_gift_row(gid, le)
        )

        if int(is_assigned or 0) == 1:
            line_edit.setReadOnly(True)
            # Verilmiş hediyelerde isim değiştirilemez; ancak SİL düğmesi
            # yine de aktif kalır ve satırın silinmesine izin verir.
            line_edit.setStyleSheet(
                "background-color:#E0E0E0; color:#757575; text-decoration:line-through;"
            )
            label = QLabel(f"Hediye {g_num} (Verildi):")
        else:
            label = QLabel(f"Hediye {g_num}:")

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(line_edit, 1)
        row_layout.addWidget(btn_del, 0)

        self.form_layout.addRow(label, row_widget)
        self.gift_rows.append((g_id, line_edit, btn_del, int(is_assigned or 0), label))

    def eventFilter(self, obj, event):
        if (
            event.type() == QEvent.Type.KeyPress
            and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
            and isinstance(obj, QLineEdit)
        ):
            # ENTER kesinlikle yeni hediye satırı açmaz.
            # Yeni satır yalnızca aşağıdaki "AŞAĞIYA YENİ HEDİYE SATIRI EKLE"
            # butonuna basıldığında oluşturulur.
            if any(row[1] is obj for row in self.gift_rows):
                return True
        return super().eventFilter(obj, event)

    def append_new_gift_row(self):
        # Her basışta yalnızca BİR yeni satır oluştur.
        next_num = len(self.gift_rows) + 1
        self.create_row_ui(None, next_num, "", 0)
        self.gift_rows[-1][1].setFocus()

    def delete_single_gift_row(self, g_id, line_edit):
        """
        SİL düğmesine basılan tek satırı kaldırır.
        Qt'nin removeRow() sırasında widget'ı silmesi ihtimaline karşı
        line_edit'e removeRow() sonrasında tekrar erişilmez.
        """
        try:
            row_index = next(
                (i for i, row in enumerate(self.gift_rows) if row[1] is line_edit),
                -1,
            )
            if row_index < 0:
                return

            # Önce satırın Python referanslarını al.
            row_data = self.gift_rows[row_index]
            row_widget = line_edit.parentWidget()

            # Veritabanında kayıtlıysa sadece o kaydı sil.
            if g_id is not None:
                conn = sqlite3.connect(
                    "gezen_telsizciler_net.db",
                    timeout=10.0,
                )
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "DELETE FROM gifts WHERE id=?",
                        (int(g_id),),
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    conn.close()

            # Önce QFormLayout'tan tam olarak bu satırı çıkar.
            # Sayısal satır indeksine güvenmek yerine satırın kapsayıcı
            # widget'ını kullanıyoruz; böylece SİL düğmesi hangi satırda
            # olursa olsun doğru kayıt kaldırılır.
            if row_widget is not None:
                self.form_layout.removeRow(row_widget)
            else:
                self.form_layout.removeRow(row_index)

            # Kendi listemizden de çıkar.
            self.gift_rows.pop(row_index)

            # Satırın kapsayıcısını Qt'nin event loop'una güvenli şekilde bırak.
            if row_widget is not None:
                try:
                    row_widget.deleteLater()
                except RuntimeError:
                    pass

            # Görünen sıra numaralarını yeniden düzenle.
            for i, item in enumerate(self.gift_rows, start=1):
                try:
                    item[4].setText(
                        f"Hediye {i} (Verildi):"
                        if item[3] == 1
                        else f"Hediye {i}:"
                    )
                except RuntimeError:
                    # Qt widget'ı removeRow tarafından zaten temizlendiyse
                    # onu atla; program çalışmaya devam eder.
                    continue

        except Exception as e:
            QMessageBox.critical(
                self,
                "Hediye Silme Hatası",
                f"Hediye silinemedi:\n\n{e}",
            )

    def reset_all_gifts_confirmed(self):
        reply = QMessageBox.question(
            self,
            "TÜM HEDİYELERİ SİL",
            "Listedeki TÜM HEDİYELERİ kalıcı olarak silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        try:
            where, params = self._session_where()
            cur.execute(f"DELETE FROM gifts WHERE {where}", params)
            conn.commit()
        finally:
            conn.close()

        self.load_gifts_from_db()

    def save_gifts(self):
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        try:
            try:
                cur.execute("ALTER TABLE gifts ADD COLUMN session_id TEXT")
            except sqlite3.OperationalError:
                pass

            is_demo = bool(
                self.parent_window and getattr(self.parent_window, "is_demo_mode", False)
            )
            session_id = (
                getattr(
                    self.parent_window,
                    "demo_session_id",
                    "demo_session_id_9999",
                )
                if is_demo else None
            )

            # Düzenlenebilir/verilmemiş hediyeler bu pencerenin yeni listesi olarak yazılır.
            if is_demo:
                cur.execute(
                    "DELETE FROM gifts WHERE is_assigned=0 AND session_id=?",
                    (session_id,),
                )
            else:
                cur.execute(
                    "DELETE FROM gifts WHERE is_assigned=0 AND "
                    "(session_id IS NULL OR session_id != 'demo_session_id_9999')"
                )

            counter = 1
            for g_id, line_edit, btn_del, is_assigned, label in self.gift_rows:
                name = (
                    line_edit.text().strip().upper()
                    .replace("i", "İ").replace("ı", "I")
                )
                if is_assigned == 1:
                    continue
                if name:
                    cur.execute(
                        "INSERT INTO gifts "
                        "(gift_number, name, is_assigned, session_id) "
                        "VALUES (?, ?, 0, ?)",
                        (counter, name, session_id),
                    )
                    counter += 1

            conn.commit()
        finally:
            conn.close()

        self.accept()


class LiveRaffleWheel(QWidget):
    """Canlı çekiliş ekranındaki görsel çark."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.names = []
        self.angle = 0.0
        self.pointer_angle = -90.0
        self.setMinimumSize(220, 220)

    def set_names(self, names):
        self.names = list(names or [])
        self.update()

    def set_angle(self, angle):
        self.angle = float(angle)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height()) - 24
        if side <= 20:
            return
        x = (self.width() - side) / 2
        y = (self.height() - side) / 2
        rect = QRect(int(x), int(y), int(side), int(side))
        n = max(1, len(self.names))
        span = 360.0 / n

        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        painter.translate(-self.width() / 2, -self.height() / 2)
        for i in range(n):
            # Renkler dönüşümlü tutulur; çok kalabalık listelerde isim yerine numara gösterilir.
            r = 238 if i % 2 == 0 else 214
            g = 232 if i % 2 == 0 else 220
            b = 194 if i % 2 == 0 else 175
            painter.setBrush(QColor(r, g, b))
            painter.setPen(QColor(105, 95, 65))
            painter.drawPie(rect, int(i * span * 16), int(span * 16))

            if n <= 24:
                painter.save()
                painter.translate(self.width() / 2, self.height() / 2)
                painter.rotate(i * span + span / 2)
                painter.translate(side * 0.31, 0)
                painter.rotate(90)
                painter.setPen(QColor(45, 45, 45))
                font = painter.font()
                font.setPointSize(max(6, min(9, int(115 / max(12, n)))))
                font.setBold(True)
                painter.setFont(font)
                text = str(self.names[i])[:12]
                painter.drawText(-35, -7, 70, 14, Qt.AlignmentFlag.AlignCenter, text)
                painter.restore()
        painter.restore()

        # Merkez ve sabit gösterge oku.
        painter.setBrush(QColor(120, 100, 55))
        painter.setPen(QColor(75, 60, 35))
        painter.drawEllipse(self.width() // 2 - 16, self.height() // 2 - 16, 32, 32)
        painter.setBrush(QColor(170, 40, 40))
        painter.setPen(QColor(120, 30, 30))
        points = [
            (self.width() - 7, self.height() // 2),
            (self.width() - 34, self.height() // 2 - 11),
            (self.width() - 34, self.height() // 2 + 11),
        ]
        from PyQt6.QtCore import QPointF
        painter.drawPolygon([QPointF(*pt) for pt in points])
        painter.end()


class LiveRaffleScreen(QDialog):
    """Canlı yayın ekranı: solda %75 operatör listesi, sağda %25 eski tip çekiliş ekranı."""
    def __init__(self, parent, lang="TR"):
        super().__init__(parent)
        self.parent_window = parent
        self.lang = lang
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refresh_records)
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_raffle)
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._update_countdown)
        self._elapsed_ms = 0
        self._duration_ms = 10000
        self._pending_winner = None
        self._pending_gift = None
        self._draw_callback = None
        self._candidates = []
        self._last_record_signature = None
        self._all_rows = []
        self._visible_rows = 21
        self._list_columns = 10

        self.setWindowTitle("📺 CANLI ÇEKİLİŞ EKRANI" if lang == "TR" else ("📺 LIVE RAFFLE SCREEN" if lang == "EN" else "📺 LIVE-VERLOSUNG"))
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)
        self.resize(max(1050, int(parent.width() * 0.90)), max(650, int(parent.height() * 0.88)))

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        self.title = QLabel("📺 CANLI ÇEKİLİŞ EKRANI")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size:20px; font-weight:bold; color:#37474F; padding:6px;")
        root.addWidget(self.title)

        # Ana canlı ekran: yaklaşık %80 operatör kayıtları, %20 çekiliş paneli.
        # Operatörler 10 sütun x 21 satır halinde gösterilir; böylece 210 kayıt
        # aynı anda görünür, fazlası yatay kaydırmayla sağa alınır.
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        root.addLayout(content_layout, 1)

        # %80: çevrim kayıt listesi - 10 sütun x 18 satır
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("font-size:15px; font-weight:bold; color:#0D47A1;")
        left_layout.addWidget(self.lbl_count)

        # Operatör listesi: ekranda 10 sütun x 21 operatör görünür.
        # Toplam kayıt sayısı 200'ü aşarsa QTableWidget'ın kendi yatay
        # kaydırma çubuğu ile sağa/sola gidilerek tüm sütunlar görülür.
        table_wrap = QHBoxLayout()
        table_wrap.setContentsMargins(0, 0, 0, 0)
        table_wrap.setSpacing(4)

        self.table_live = QTableWidget(self._visible_rows, self._list_columns)
        self.table_live.setHorizontalHeaderLabels(["OPERATÖRLER"] * self._list_columns)
        self.table_live.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_live.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_live.setAlternatingRowColors(False)
        self.table_live.setWordWrap(True)
        self.table_live.verticalHeader().setVisible(False)
        self.table_live.horizontalHeader().setStretchLastSection(False)
        self.table_live.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_live.verticalHeader().setDefaultSectionSize(42)
        self.table_live.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_live.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table_live.horizontalScrollBar().setSingleStep(1)
        self.table_live.horizontalScrollBar().setPageStep(10)
        self.table_live.setToolTip("210'den fazla operatör varsa sağa/sola kaydırın")
        table_wrap.addWidget(self.table_live, 1)
        left_layout.addLayout(table_wrap, 1)
        content_layout.addWidget(left, 4)

        # %20: profesyonel canlı çekiliş paneli, çark yok
        right = QWidget()
        right.setObjectName("liveRafflePanel")
        right.setStyleSheet("""
            QWidget#liveRafflePanel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #111827, stop:0.55 #172033, stop:1 #0b1220);
                border: 1px solid #334155;
                border-radius: 14px;
            }
            QLabel#liveSectionTitle {
                color: #94a3b8; font-size: 10px; font-weight: bold; letter-spacing: 1px;
                padding: 2px;
            }
            QLabel#liveGift {
                color: #f8fafc; font-size: 15px; font-weight: bold;
                background: #1f2937; border: 1px solid #475569; border-radius: 9px; padding: 10px;
            }
            QLabel#liveTimer {
                color: #fbbf24; font-size: 12px; font-weight: bold; padding: 2px;
            }
            QLabel#liveSlot {
                color: #f8fafc; font-size: 19px; font-weight: bold;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1e293b,stop:0.5 #172554,stop:1 #312e81);
                border: 2px solid #6366f1; border-radius: 14px; padding: 16px;
            }
            QLabel#liveStatus {
                color: #cbd5e1; font-size: 11px; font-weight: bold; padding: 4px;
            }
            QPushButton#liveDrawButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #a9a65d,stop:1 #c1bd73);
                color: #182018; font-size: 12px; font-weight: bold;
                border: 1px solid #777442; border-radius: 8px; padding: 10px;
            }
            QPushButton#liveDrawButton:hover { background: #c8c47b; }
            QPushButton#liveDrawButton:disabled { background: #475569; color: #94a3b8; border-color: #475569; }
        """)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.setSpacing(7)

        self.lbl_live_section = QLabel("●  CANLI ÇEKİLİŞ")
        self.lbl_live_section.setObjectName("liveSectionTitle")
        self.lbl_live_section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.lbl_live_section)

        self.lbl_gift = QLabel("🎁  ÖDÜL SEÇİLMEDİ")
        self.lbl_gift.setObjectName("liveGift")
        self.lbl_gift.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_gift.setWordWrap(True)
        right_layout.addWidget(self.lbl_gift)

        self.lbl_timer = QLabel("Kalan Süre: 10 Saniye")
        self.lbl_timer.setObjectName("liveTimer")
        self.lbl_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.lbl_timer)

        self.lbl_slot = QLabel("ÇEKİLİŞ BAŞLIYOR...")
        self.lbl_slot.setObjectName("liveSlot")
        self.lbl_slot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_slot.setWordWrap(True)
        self.lbl_slot.setMinimumHeight(120)
        self.lbl_slot.setMaximumHeight(230)
        right_layout.addWidget(self.lbl_slot, 0)

        self.lbl_status = QLabel("Çekiliş için hazır")
        self.lbl_status.setObjectName("liveStatus")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        right_layout.addWidget(self.lbl_status)

        # Asıl kazananın hediyeyi kabul/ret kararı için geçici karar alanı.
        self.decision_widget = QWidget()
        decision_layout = QHBoxLayout(self.decision_widget)
        decision_layout.setContentsMargins(0, 0, 0, 0)
        decision_layout.setSpacing(6)
        self.btn_accept_gift = QPushButton("✅ HEDİYEYİ KABUL ETTİ")
        self.btn_decline_gift = QPushButton("❌ HEDİYEDEN VAZGEÇTİ")
        for btn in (self.btn_accept_gift, self.btn_decline_gift):
            btn.setMinimumHeight(34)
            btn.setVisible(False)
        self.btn_accept_gift.setStyleSheet("background:#166534;color:white;font-weight:bold;border:1px solid #22c55e;border-radius:7px;padding:7px;")
        self.btn_decline_gift.setStyleSheet("background:#991b1b;color:white;font-weight:bold;border:1px solid #ef4444;border-radius:7px;padding:7px;")
        self.btn_accept_gift.clicked.connect(self.parent_window.accept_gift_assignment)
        self.btn_decline_gift.clicked.connect(self.parent_window.decline_gift_assignment)
        decision_layout.addWidget(self.btn_accept_gift)
        decision_layout.addWidget(self.btn_decline_gift)
        right_layout.addWidget(self.decision_widget)

        self.btn_manage_gifts = QPushButton("🗂️  HEDİYE ATAMALARINI YÖNET")
        self.btn_manage_gifts.setMinimumHeight(34)
        self.btn_manage_gifts.setStyleSheet("background:#334155;color:#f8fafc;font-weight:bold;border:1px solid #64748b;border-radius:7px;padding:7px;")
        self.btn_manage_gifts.clicked.connect(self.parent_window.manage_gift_assignments)
        right_layout.addWidget(self.btn_manage_gifts)

        self.btn_live_draw = QPushButton("🎁  ÇEKİLİŞİ BAŞLAT")
        self.btn_live_draw.setObjectName("liveDrawButton")
        self.btn_live_draw.setMinimumHeight(40)
        self.btn_live_draw.clicked.connect(self.start_draw_from_screen)
        right_layout.addWidget(self.btn_live_draw)
        # Koyu çekiliş panelinin altında kalan boş alanı kazanan kartı için kullan.
        right_column = QWidget()
        right_column_layout = QVBoxLayout(right_column)
        # Sağ çekiliş panelini soldaki OPERATÖRLER başlığıyla aynı üst hizaya getir.
        # Soldaki sayaç satırının yüksekliği kadar üst boşluk bırakılır.
        right_column_layout.setContentsMargins(0, 32, 0, 0)
        right_column_layout.setSpacing(8)
        right_column_layout.addWidget(right, 0, Qt.AlignmentFlag.AlignTop)

        # Kazananlar: her talihli kendi kutusunda, 2 sütun halinde gösterilir.
        # Dikey/yatay kaydırma yok; 7-8 kazanan aynı anda görünür.
        self.bottom_winner_panel = QFrame()
        self.bottom_winner_panel.setObjectName("bottomWinnerPanel")
        self.bottom_winner_panel.setStyleSheet("""
            QFrame#bottomWinnerPanel {
                background: transparent;
                border: 0px;
            }
            QFrame#winnerCard {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #04382d, stop:0.5 #044a39, stop:1 #011f18);
                border: 2px solid #0a8f70;
                border-radius: 10px;
            }
            QLabel#winnerRank {
                color: #fde68a; font-size: 10px; font-weight: bold;
            }
            QLabel#winnerCall {
                color: #ffffff; font-size: 19px; font-weight: bold;
            }
            QLabel#winnerName {
                color: #d1fae5; font-size: 12px; font-weight: bold;
            }
            QLabel#winnerGift {
                color: #fde68a; font-size: 12px; font-weight: bold;
            }
        """)
        self.bottom_winner_grid = QGridLayout(self.bottom_winner_panel)
        self.bottom_winner_grid.setContentsMargins(0, 0, 0, 0)
        self.bottom_winner_grid.setHorizontalSpacing(8)
        self.bottom_winner_grid.setVerticalSpacing(8)
        self.bottom_winner_grid.setColumnStretch(0, 1)
        self.bottom_winner_grid.setColumnStretch(1, 1)
        self.bottom_winner_panel.setVisible(False)
        right_column_layout.addWidget(self.bottom_winner_panel, 1)

        content_layout.addWidget(right_column, 1, Qt.AlignmentFlag.AlignTop)

        self.refresh_records()
        self._refresh_timer.start(1000)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._fit_live_columns)

    def closeEvent(self, event):
        self._refresh_timer.stop()
        self._anim_timer.stop()
        self._countdown_timer.stop()
        super().closeEvent(event)

    def _fit_live_columns(self):
        """İlk 10 sütunu ekranda yan yana göster; fazlası yatay kaydırılır."""
        if not hasattr(self, "table_live"):
            return
        total = self.table_live.columnCount()
        if total <= 0:
            return
        viewport_width = max(700, self.table_live.viewport().width())
        visible_width = max(90, viewport_width // self._list_columns)
        for col in range(total):
            self.table_live.setColumnWidth(col, visible_width)

    def _update_bottom_winners(self):
        """Bu oturumdaki kazananları ayrı kutular halinde, tamamı görünür şekilde göster."""
        parent = self.parent_window
        winner_ids = set(getattr(parent, "session_winner_ids", set()))

        # Önce eski kutuları temizle.
        while self.bottom_winner_grid.count():
            item = self.bottom_winner_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not winner_ids:
            self.bottom_winner_panel.setVisible(False)
            return

        rows_by_id = {row[0]: row for row in self._all_rows}
        ordered_ids = []

        # Çekiliş sırasını geçici atama tablosundan al.
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cur = conn.cursor()
            cur.execute(
                "SELECT primary_operator_id, backup_operator_id FROM gift_assignments "
                "WHERE session_id=? ORDER BY id ASC",
                (parent.net_session_id,),
            )
            for primary_id, backup_id in cur.fetchall():
                for op_id in (primary_id, backup_id):
                    if op_id in winner_ids and op_id not in ordered_ids:
                        ordered_ids.append(op_id)
            conn.close()
        except Exception:
            pass

        for op_id in winner_ids:
            if op_id not in ordered_ids:
                ordered_ids.append(op_id)

        # 2 sütun: 8 kazanan = 4 sıra. Böylece tek bakışta tamamı görünür.
        for no, op_id in enumerate(ordered_ids, 1):
            row = rows_by_id.get(op_id)
            if not row:
                continue

            callsign = str(row[1] or "").split(" ")[0].upper()
            op_name = str(row[2] or "").upper().replace("i", "İ").replace("ı", "I")
            gift = str(getattr(parent, "session_winner_prizes", {}).get(op_id, "") or "")

            card = QFrame()
            card.setObjectName("winnerCard")
            card.setMinimumHeight(84)
            card.setMaximumHeight(108)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(6, 5, 6, 5)
            card_layout.setSpacing(1)

            rank = QLabel(f"🏆 {no}. KAZAN TALİHLİSİ")
            rank.setObjectName("winnerRank")
            rank.setAlignment(Qt.AlignmentFlag.AlignCenter)

            call = QLabel(callsign)
            call.setObjectName("winnerCall")
            call.setAlignment(Qt.AlignmentFlag.AlignCenter)

            name = QLabel(op_name)
            name.setObjectName("winnerName")
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name.setWordWrap(True)

            gift_label = QLabel(f"🎁 {gift}")
            gift_label.setObjectName("winnerGift")
            gift_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            gift_label.setWordWrap(True)

            card_layout.addWidget(rank)
            card_layout.addWidget(call)
            card_layout.addWidget(name)
            card_layout.addWidget(gift_label)

            grid_index = no - 1
            grid_row = grid_index // 2
            grid_col = grid_index % 2
            self.bottom_winner_grid.addWidget(card, grid_row, grid_col)

        self.bottom_winner_panel.setVisible(True)
        self.bottom_winner_panel.updateGeometry()

    def _render_visible_records(self):
        rows = self._all_rows
        visible_rows = self._visible_rows
        total_columns = max(self._list_columns, (len(rows) + visible_rows - 1) // visible_rows)

        self.table_live.setRowCount(visible_rows)
        self.table_live.setColumnCount(total_columns)
        self.table_live.setHorizontalHeaderLabels(["OPERATÖRLER"] * total_columns)
        self.table_live.clearContents()

        for index, row in enumerate(rows):
            if index >= visible_rows * total_columns:
                break

            row = rows[index]
            db_id = row[0]
            col = index // visible_rows
            row_idx = index % visible_rows
            callsign = str(row[1] or "").split(" ")[0].upper()
            op_name = str(row[2] or "").upper().replace("i", "İ").replace("ı", "I")
            qth = str(row[3] or "").upper().replace("i", "İ").replace("ı", "I")

            text = f"{index + 1}. {callsign}\n{op_name}\n{qth}"
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            font = item.font()
            font.setPointSize(9)
            font.setBold(False)
            item.setFont(font)

            if db_id in self.parent_window.session_winner_ids:
                item.setBackground(QColor("#FFF9C4"))
                item.setForeground(QColor("#5D4E00"))
                item.setText(f"🏆 {index + 1}. {callsign}\n{op_name}\n{qth}")
            else:
                item.setBackground(QColor("#F5F5F5" if index % 2 else "#FFFFFF"))
                item.setForeground(QColor("#263238"))

            self.table_live.setItem(row_idx, col, item)

        # Son satır/sütundaki boş alanları boş bırak.
        self.lbl_count.setText(f"KAYITLI OPERATÖRLER: {len(rows)}")

    def refresh_records(self):
        parent = self.parent_window
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cur = conn.cursor()
            cur.execute(
                "SELECT id, callsign, op_name, qth FROM logs WHERE user_id=? AND session_id=? ORDER BY id ASC",
                (parent.current_user[0], parent.net_session_id),
            )
            rows = cur.fetchall()
            conn.close()
        except Exception:
            return

        signature = tuple(rows) + tuple(sorted(parent.session_winner_ids))
        if signature == self._last_record_signature:
            return
        self._last_record_signature = signature
        self._all_rows = rows

        # 10 sütun x 21 operatör = 210 görünür kayıt. Daha fazlası için
        # QTableWidget'ın kendi yatay kaydırma çubuğu otomatik açılır.
        self._render_visible_records()
        self._update_bottom_winners()
        QTimer.singleShot(0, self._fit_live_columns)

    def start_draw_from_screen(self):
        if self._anim_timer.isActive() or self._countdown_timer.isActive():
            return
        self.parent_window.run_live_raffle()

    def start_spin(self, candidates, gift_number, gift_name, winner, finished_callback):
        """Çekiliş isim akışını çalıştırır: Hediye 1 = 10 sn, Hediye 2 ve sonrası = 6 sn."""
        if not candidates:
            return
        # Süre operatör sayısına göre değil, HEDİYE NUMARASINA göre belirlenir.
        # Hediye 1 = 8 saniye; Hediye 2 ve sonrası = 5 saniye.
        try:
            gift_no = int(gift_number)
        except (TypeError, ValueError):
            gift_no = 1
        self._duration_ms = 8000 if gift_no == 1 else 5000
        self._candidates = list(candidates)
        self._pending_winner = winner
        self._pending_gift = gift_name
        self._draw_callback = finished_callback
        self.lbl_gift.setText(f"🎁 ÖDÜL: {gift_name}")
        self.lbl_status.setText("ÇEKİLİŞ DEVAM EDİYOR...")
        self.btn_live_draw.setEnabled(False)
        self._elapsed_ms = 0
        self._anim_timer.start(75)
        self._countdown_timer.start(100)

    def _animate_raffle(self):
        if not self._candidates:
            return
        rand_cand = random.choice(self._candidates)
        self.lbl_slot.setText(f"🎯 {rand_cand[1]}  •  {rand_cand[2]} ({rand_cand[3]})".upper())

    def _update_countdown(self):
        self._elapsed_ms += 100
        rem = max(0, round((self._duration_ms - self._elapsed_ms) / 1000, 1))
        self.lbl_timer.setText(f"Kalan Süre: {rem} Saniye")
        if self._elapsed_ms >= self._duration_ms:
            self._anim_timer.stop()
            self._countdown_timer.stop()
            self._show_winner()

    def _show_winner(self):
        winner = self._pending_winner
        gift = self._pending_gift
        if not winner:
            return
        self.lbl_timer.setText("🎉 ÇEKİLİŞ TAMAMLANDI! 🎉")
        self.lbl_timer.setStyleSheet("font-size:12px; font-weight:bold; color:#4ade80; padding:2px;")
        self.lbl_slot.setStyleSheet("font-size:22px; font-weight:bold; color:#ffffff; background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #064e3b,stop:0.5 #065f46,stop:1 #022c22); border:2px solid #10b981; border-radius:14px; padding:14px;")
        self.lbl_slot.setText(f"<span style='color:#fde68a;font-size:16px;'>🏆  KAZANAN OPERATÖR  🏆</span><br><br><span style='font-size:36px;color:#ffffff;font-weight:bold;'>{winner[1]}</span><br><span style='font-size:20px;color:#d1fae5;'>{winner[2]} • {winner[3]}</span>")
        self.lbl_status.setText(f"🎁 {gift} • ASIL KAZANANIN KARARI BEKLENİYOR")
        self._update_bottom_winners()
        self.btn_live_draw.setEnabled(False)
        self.btn_accept_gift.setVisible(False)
        self.btn_decline_gift.setVisible(False)
        self.refresh_records()
        callback = self._draw_callback
        self._pending_winner = None
        self._pending_gift = None
        self._draw_callback = None
        if callback:
            callback(winner, gift)


    def show_gift_assignment(self, winner, backup, gift_name, assignment_id):
        self.btn_accept_gift.setVisible(True)
        self.btn_decline_gift.setVisible(True)
        self.btn_live_draw.setEnabled(False)
        backup_text = (
            f"<br><span style='font-size:13px;color:#fde68a;'>YEDEK: {backup[1]} • {backup[2]} • {backup[3]}</span>"
            if backup else
            "<br><span style='font-size:13px;color:#fca5a5;'>YEDEK BULUNAMADI</span>"
        )
        self.lbl_status.setText(f"🎁 {gift_name} • ASIL KAZANANIN KARARI BEKLENİYOR{backup_text}")

    def finish_gift_decision(self, status):
        self.btn_accept_gift.setVisible(False)
        self.btn_decline_gift.setVisible(False)
        self.btn_live_draw.setEnabled(True)
        if status == "PRIMARY_ACCEPTED":
            self.lbl_status.setText("✅ ASIL OPERATÖR HEDİYEYİ KABUL ETTİ • YEDEK SERBEST")
        else:
            self.lbl_status.setText("HEDİYE ATAMASI TAMAMLANDI")

    def show_backup_winner(self, backup, gift_name):
        self.btn_accept_gift.setVisible(False)
        self.btn_decline_gift.setVisible(False)
        self.btn_live_draw.setEnabled(True)
        self.lbl_timer.setText("🎉 YEDEĞE DEVREDİLDİ! 🎉")
        self.lbl_slot.setText(
            f"<span style='color:#fde68a;font-size:16px;'>🏆  YENİ KAZANAN  🏆</span><br><br>"
            f"<span style='font-size:36px;color:#ffffff;font-weight:bold;'>{backup[1]}</span><br>"
            f"<span style='font-size:20px;color:#d1fae5;'>{backup[2]}</span>"
        )
        self.lbl_status.setText(f"🎁 {gift_name} • YEDEK OPERATÖRE VERİLDİ")
        self._update_bottom_winners()



class RaffleAnimationDialog(QDialog):
    def __init__(self, candidates, gift_name, parent=None, lang="TR"):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(
            "Çekiliş Heyecanı 🏆"
            if lang == "TR"
            else (
                "Raffle Excitement 🏆" if lang == "EN" else "Verlosungsspannung 🏆"
            )
        )
        self.resize(540, 360)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        self.candidates = candidates
        self.gift_name = gift_name
        self.winner = random.choice(candidates)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:1 #1e293b);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        self.lbl_title = QLabel(f"🎁 ÖDÜL: {self.gift_name}")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #38bdf8; 
            background-color: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 8px;
            padding: 10px;
        """)
        layout.addWidget(self.lbl_title)

        initial_seconds = int(self.total_duration_ms / 1000)
        timer_text = (
            f"Kalan Süre: {initial_seconds} Saniye"
            if lang == "TR"
            else (
                f"Time Remaining: {initial_seconds} Seconds"
                if lang == "EN"
                else f"Verbleibende Zeit: {initial_seconds} Sekunden"
            )
        )
        self.lbl_timer = QLabel(timer_text)
        self.lbl_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_timer.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #f43f5e; background: transparent;"
        )
        layout.addWidget(self.lbl_timer)

        start_text = (
            "ÇEKİLİŞ BAŞLIYOR..."
            if lang == "TR"
            else (
                "RAFFLE STARTING..."
                if lang == "EN"
                else "VERLOSUNG BEGINNT..."
            )
        )
        self.lbl_slot = QLabel(start_text)
        self.lbl_slot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_slot.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #e2e8f0; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e1b4b, stop:1 #311042);
            border: 2px solid #818cf8; 
            border-radius: 12px; 
            padding: 22px;
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(129, 140, 248, 120))
        shadow.setOffset(0, 0)
        self.lbl_slot.setGraphicsEffect(shadow)
        
        layout.addWidget(self.lbl_slot)
        layout.addSpacing(5)

        btn_ongoing_text = (
            "ÇEKİLİŞ DEVAM EDİYOR..."
            if lang == "TR"
            else (
                "RAFFLE IN PROGRESS..."
                if lang == "EN"
                else "VERLOSUNG LÄUFT..."
            )
        )
        self.btn_action = QPushButton(btn_ongoing_text)
        self.btn_action.setEnabled(False)
        self.btn_action.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #db2777);
                color: white; 
                font-weight: bold; 
                font-size: 14px; 
                padding: 12px; 
                border-radius: 8px;
                border: none;
            }
            QPushButton:disabled {
                background: #334155;
                color: #94a3b8;
            }
        """)
        layout.addWidget(self.btn_action)

        self.setLayout(layout)

        self.elapsed_ms = 0
        parent_winners = getattr(parent, "session_winner_ids", set())
        self.total_duration_ms = 10000 if len(parent_winners) == 0 else 6000

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(75)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(100)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            event.ignore()
        else:
            super().keyPressEvent(event)

    def animate(self):
        rand_cand = random.choice(self.candidates)
        display_text = f"🎯 {rand_cand[1]}  •  {rand_cand[2]}  ({rand_cand[3]})"
        self.lbl_slot.setText(display_text.upper())

    def update_countdown(self):
        self.elapsed_ms += 100
        rem = max(0, round((self.total_duration_ms - self.elapsed_ms) / 1000, 1))
        timer_text = (
            f"Kalan Süre: {rem} Saniye"
            if self.lang == "TR"
            else (
                f"Time Remaining: {rem} Seconds"
                if self.lang == "EN"
                else f"Verbleibende Zeit: {rem} Sekunden"
            )
        )
        self.lbl_timer.setText(timer_text)

        if self.elapsed_ms >= self.total_duration_ms:
            self.anim_timer.stop()
            self.countdown_timer.stop()
            self.show_winner()

    def show_winner(self):
        complete_text = (
            "🎉 ÇEKİLİŞ TAMAMLANDI! 🎉"
            if self.lang == "TR"
            else ("🎉 RAFFLE COMPLETED! 🎉" if self.lang == "EN" else "🎉 VERLOSUNG ABGESCHLOSSEN! 🎉")
        )
        winner_label = (
            "🏆 KAZANAN OPERATÖR 🏆"
            if self.lang == "TR"
            else ("🏆 WINNING OPERATOR 🏆" if self.lang == "EN" else "🏆 GEWINNER OPERATOR 🏆")
        )
        self.lbl_timer.setText(complete_text)
        self.lbl_timer.setStyleSheet("font-size: 13px; font-weight: bold; color: #4ade80;")
        
        self.lbl_slot.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #ffffff; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #064e3b, stop:1 #022c22);
            border: 2px solid #10b981; 
            border-radius: 12px; 
            padding: 22px;
        """)
        self.lbl_slot.setText(
            f"<span style='color: #34d399; font-size: 14px;'>{winner_label}</span><br><br>"
            f"<span style='font-size: 24px; color: #ffffff;'>{self.winner[1]}</span><br>"
            f"<span style='font-size: 15px; color: #94a3b8;'>{self.winner[2]} ({self.winner[3]})</span>".upper()
        )

        close_text = (
            "KAPAT" if self.lang == "TR" else ("CLOSE" if self.lang == "EN" else "SCHLIESSEN")
        )
        self.btn_action.setText(close_text)
        self.btn_action.setEnabled(True)
        self.btn_action.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #059669);
            }
        """)
        self.btn_action.clicked.connect(self.accept)

    def get_winner(self):
        return self.winner


class NetLogWindow(QMainWindow):
    def __init__(self, user_info):
        self.show_theme_in_notes = True
        super().__init__()
        self.current_user = user_info
        self.lang = "TR"
        self.is_demo_mode = False
        self.current_notes = ""
        self.pending_echolink_callsign = None
        self.registration_closed = False
        self.raffle_completed = False
        # Çekiliş sonuçları yalnızca uygulama açıkken tutulur; veritabanına yazılmaz.
        self.session_winner_ids = set()
        self.session_winner_prizes = {}
        self.drawn_gift_ids = set()
        # Hediye asıl/yedek atamaları yalnızca mevcut uygulama oturumunda
        # geçerlidir. Detayları SQLite'ta geçici tutulur ve program açılışında
        # otomatik temizlenir.
        self.current_gift_assignment_id = None

        self.real_session_id = get_or_create_session_id()
        self.demo_session_id = "demo_session_id_9999"
        self.net_session_id = self.real_session_id

        self.init_database_structure()
        self.initUI()
        self._load_session_control_state()
        self._sync_registration_controls()

        self.echolink_tx_timer = QTimer(self)
        self.echolink_tx_timer.timeout.connect(self.check_echolink_tx_status)
        self.echolink_tx_timer.start(1500)

    import sqlite3
    import os

    def init_database_structure(self):
        try:
            db_path = os.path.join(os.getcwd(), "gezen_telsizciler_net.db")
            conn = sqlite3.connect(db_path, timeout=10.0)
            cursor = conn.cursor()

            # Logs tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    callsign TEXT,
                    op_name TEXT,
                    qth TEXT,
                    notes TEXT,
                    timestamp TEXT,
                    session_id TEXT,
                    is_winner INTEGER DEFAULT 0,
                    prize TEXT,
                    is_echolink INTEGER DEFAULT 0
                )
            """)

            # Gifts tablosu (Hediye bölümünün çökmesini engelleyen tablo)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gifts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    gift_number INTEGER, 
                    name TEXT, 
                    is_assigned INTEGER DEFAULT 0,
                    session_id TEXT
                )
            """)

            # Diğer tablolar (Eksik sütun eklemeleri dahil)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS net_controllers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    callsign TEXT,
                    name TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operator_pool (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    callsign TEXT UNIQUE, 
                    name TEXT, 
                    qth TEXT,
                    notes TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS net_session_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    session_date TEXT,
                    total_count INTEGER,
                    echolink_count INTEGER,
                    analog_count INTEGER,
                    echolink_pct REAL,
                    analog_pct REAL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS net_session_control (
                    session_id TEXT PRIMARY KEY,
                    registration_closed INTEGER DEFAULT 0
                )
            """)

            # Hediye çekilişlerinin asıl/yedek eşleşmeleri geçicidir.
            # Program her açıldığında eski oturumdan kalan atamalar temizlenir;
            # hediye ve operatör kayıtlarına dokunulmaz.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gift_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    gift_id INTEGER NOT NULL,
                    gift_name TEXT NOT NULL,
                    primary_operator_id INTEGER,
                    primary_callsign TEXT,
                    primary_name TEXT,
                    primary_qth TEXT,
                    backup_operator_id INTEGER,
                    backup_callsign TEXT,
                    backup_name TEXT,
                    backup_qth TEXT,
                    status TEXT NOT NULL DEFAULT 'PRIMARY_PENDING',
                    assigned_at TEXT,
                    decided_at TEXT
                )
            """)
            cursor.execute("DELETE FROM gift_assignments")

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Veritabanı kurulum hatası: {e}")

    def open_directory_dialog(self):
        dialog = OperatorDirectoryDialog(self, lang=self.lang)
        dialog.exec()

    def open_controllers_dialog(self):
        dialog = NetControllersDialog(self, lang=self.lang)
        dialog.exec()
        self.update_net_controllers_label()

    def open_statistics_dialog(self):
        dialog = NetStatisticsDialog(self, lang=self.lang)
        dialog.exec()

    def open_gift_editor(self):
        # Hediye Sistemi artık gerçek bir QMenu değil, doğrudan tıklanabilen
        # bir QAction'dır. Böylece fareyle üzerine gelmek hiçbir şey yapmaz.
        dialog = GiftEditDialog(self, lang=self.lang)
        dialog.exec()

    def open_qsl_dialog(self):
        dialog = GlobalQSLDialog(self, lang=self.lang)
        # QSL kartları QSL penceresi kapanırken yeniden üretilmez.
        # QSL üretimi yalnızca PDF ÇEVRİM LİSTESİ OLUŞTUR işlemi
        # sonrasında arka planda yapılır.
        dialog.exec()

    def open_logbook_dialog(self):
        dialog = LogbookDialog(self, lang=self.lang)
        dialog.exec()

    def open_echolink(self):
        url = "https://webapp.echolink.org/"
        if hasattr(self, "echolink_container"):
            self.echolink_container.setVisible(True)
            if HAS_WEBENGINE and hasattr(self, "web_view"):
                self.web_view.setUrl(QUrl(url))

    def on_feature_permission_requested(self, url, feature):
        if HAS_WEBENGINE:
            self.web_view.page().setFeaturePermission(
                url, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )

    def check_echolink_tx_status(self):
        if (
            not HAS_WEBENGINE
            or not hasattr(self, "echolink_container")
            or not self.echolink_container.isVisible()
        ):
            return

        js_code = """
        (function() {
            var bodyText = document.body.innerText;
            var lines = bodyText.split('\\n');
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                if (line.startsWith('>')) {
                    var parts = line.replace('>', '').trim().split(' ');
                    if (parts.length > 0 && parts[0].length > 1) {
                        return parts[0].toUpperCase();
                    }
                }
            }
            return "";
        })();
        """
        self.web_view.page().runJavaScript(js_code, self.handle_echolink_tx_result)

    def handle_echolink_tx_result(self, callsign):
        try:
            if self.registration_closed or not callsign:
                return

            clean_call = callsign.strip().upper().split(" ")[0]
            ignored_calls = ["YM2KDB-R", "YM2KDB", "RÖLE", "REPEATER"]

            # ECHOLINK'TE Y ile başlayan çağrı işaretleri kesinlikle çevrim
            # kayıtlarına alınmaz ve kayıt giriş ekranına da aktarılmaz.
            if clean_call.startswith("Y"):
                return
            if clean_call in ignored_calls or len(clean_call) < 3:
                return

            conn = None
            try:
                conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=15.0)
                cursor = conn.cursor()

                # Aynı çağrı işareti bu oturumda kayıtlıysa tekrar ekleme.
                cursor.execute(
                    "SELECT 1 FROM logs WHERE callsign=? AND session_id=?",
                    (clean_call, self.net_session_id),
                )
                if cursor.fetchone():
                    return

                pool_table = "demo_operator_pool" if self.is_demo_mode else "operator_pool"
                cursor.execute(
                    f"SELECT name, qth, notes FROM {pool_table} WHERE callsign=?",
                    (clean_call,),
                )
                pool_record = cursor.fetchone()

                if pool_record:
                    # Veri tabanında kayıtlı operatör: isim/QTH bilgisi mevcut
                    # olduğundan doğrudan çevrim kayıtlarına kaydet.
                    op_name = pool_record[0] or ""
                    op_qth = pool_record[1] or ""
                    op_notes = pool_record[2] or ""

                    # Kayıtlı operatörün adı veya QTH'si eksikse manuel girişe bırak.
                    if not op_name or not op_qth:
                        self._fill_unknown_echolink_operator(clean_call)
                        return

                    cursor.execute(
                        "INSERT INTO logs (user_id, callsign, op_name, qth, notes, "
                        "timestamp, session_id, is_winner, is_echolink) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1)",
                        (
                            self.current_user[0], clean_call, op_name, op_qth, op_notes,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                            self.net_session_id,
                        ),
                    )
                    new_log_id = cursor.lastrowid
                    conn.commit()
                    self.refresh_table()
                    self._highlight_latest_operator(new_log_id)
                else:
                    # Veri tabanında YOKSA kesinlikle otomatik kaydetme.
                    # Sadece çağrı işaretini sol taraftaki kayıt formuna yaz,
                    # isim/soyisim alanına imleci otomatik geçir; kullanıcı
                    # isim ve QTH'yi girip normal KAYDET ile tamamlasın.
                    self._fill_unknown_echolink_operator(clean_call)
            finally:
                if conn is not None:
                    try:
                        conn.close()
                    except Exception:
                        pass
        except Exception as e:
            print("EchoLink otomatik kayıt hatası:", type(e).__name__, str(e))

    def _fill_unknown_echolink_operator(self, clean_call):
        """EchoLink'ten gelen bilinmeyen operatörü forma alır; aynı operatör
        konuşmaya devam ederse kullanıcının yazdığı bilgileri ASLA silmez."""
        try:
            # EchoLink aynı çağrı işaretini her 1,5 saniyede bir tekrar
            # bildirebilir. Kullanıcı henüz kaydetmeden aynı operatör tekrar
            # konuşursa formu yeniden temizlemek isim/QTH girişini siler.
            if self.pending_echolink_callsign == clean_call:
                return

            self.pending_echolink_callsign = clean_call

            self.input_callsign.blockSignals(True)
            try:
                self.input_callsign.setText(clean_call)
            finally:
                self.input_callsign.blockSignals(False)

            # Yalnızca YENİ bir bilinmeyen operatör geldiğinde alanları temizle.
            self.input_name.clear()
            self.input_qth.clear()
            self.input_notes.clear()
            self.current_notes = ""
            self.lbl_phonetic.setText(phonetic.get_phonetic(clean_call))

            # İsim/Soyisim alanına otomatik geç.
            self.input_name.setFocus()
            self.input_name.selectAll()
        except Exception:
            pass

    def trigger_background_qsl(self, callsign_only, op_name, qth_val, timestamp=None):
        task = QSLTaskRunner(callsign_only, op_name, qth_val, self.net_session_id, timestamp)
        QThreadPool.globalInstance().start(task)

    def regenerate_all_session_qsps(self):
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT callsign, op_name, qth, timestamp FROM logs WHERE session_id=?",
                (self.net_session_id,)
            )
            rows = cursor.fetchall()
            conn.close()

            for call, name, qth, timestamp in rows:
                self.trigger_background_qsl(call, name, qth, timestamp)
        except Exception:
            pass

    def toggle_demo_mode(self):
        if not self.is_demo_mode:
            self.is_demo_mode = True
            self.net_session_id = self.demo_session_id

            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM net_controllers WHERE session_id=?",
                (self.net_session_id,),
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO net_controllers (session_id, callsign, name) VALUES"
                    " (?, ?, ?)",
                    (self.net_session_id, "TA2TTL", "DENİZ ERTÜRK"),
                )

            cursor.execute("SELECT COUNT(*) FROM demo_operator_pool")
            if cursor.fetchone()[0] == 0:
                demo_operators = [
                    (
                        "TA1ABC",
                        "AHMET YILMAZ",
                        "İSTANBUL / PENDİK",
                        "CİHAZ: YAESU FT-710",
                    ),
                    (
                        "DL1XYZ",
                        "HANS MUELLER",
                        "NUREMBERG, GERMANY",
                        "AVRUPA KATILIMI",
                    ),
                    ("TA3ZZZ", "AYŞE KAYA", "İZMİR", "MOBİL İSTASYON"),
                    (
                        "TA2KTM",
                        "CEMAL ÇELİK",
                        "KOCAELİ / İZMİT",
                        "GEZEN TELSİZCİLER ÜYESİ",
                    ),
                ]
                for call, name, qth, notes in demo_operators:
                    cursor.execute(
                        "INSERT OR IGNORE INTO demo_operator_pool (callsign, name, qth,"
                        " notes) VALUES (?, ?, ?, ?)",
                        (call, name, qth, notes),
                    )

            cursor.execute(
                "SELECT COUNT(*) FROM logs WHERE session_id=?", (self.net_session_id,)
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "SELECT callsign, name, qth, notes FROM demo_operator_pool"
                )
                for call, name, qth, notes in cursor.fetchall():
                    cursor.execute(
                        "INSERT INTO logs (user_id, callsign, op_name, qth, notes,"
                        " timestamp, session_id, is_winner, is_echolink) VALUES (?, ?, ?, ?, ?, ?, ?,"
                        " 0, 1)",
                        (
                            self.current_user[0],
                            call,
                            name,
                            qth,
                            "",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            self.net_session_id,
                        ),
                    )

            conn.commit()
            conn.close()

            self.action_demo.setVisible(False)
            self.action_normal.setVisible(True)

            msg = (
                "Demo moduna geçildi! Program tamamen demo oturumuna özel"
                " kayıtlarla çalışmaktadır."
                if self.lang == "TR"
                else (
                    "Switched to Demo Mode!"
                    if self.lang == "EN"
                    else "In den Demo-Modus gewechselt!"
                )
            )
            QMessageBox.information(self, "Demo Modu", msg)
        else:
            self.is_demo_mode = False
            self.net_session_id = self.real_session_id

            self.action_demo.setVisible(True)
            self.action_normal.setVisible(False)

            msg = (
                "Normal moda geri dönüldü."
                if self.lang == "TR"
                else (
                    "Returned to Normal Mode."
                    if self.lang == "EN"
                    else "Zum Normalmodus zurückgekehrt."
                )
            )
            QMessageBox.information(self, "Normal Mod", msg)

        self.update_menu_style()
        self.update_net_controllers_label()
        self.load_operator_pool_from_db()
        self.refresh_table()
        self._load_session_control_state()
        self._sync_registration_controls()

    def change_language(self, lang_code):
        self.lang = lang_code
        self.retranslate_ui()

    def update_menu_style(self):
        menubar = self.menuBar()
        if self.is_demo_mode:
            menubar.setStyleSheet("""
                QMenuBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFE082, stop:1 #FFB74D);
                    border-bottom: 2px solid #F57C00;
                    padding: 4px;
                }
                QMenuBar::item {
                    background-color: #FFB74D;
                    color: #3E2723;
                    font-weight: bold;
                    padding: 6px 12px;
                    margin-right: 4px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    border: 1px solid #F57C00;
                }
                QMenuBar::item:selected {
                    background-color: #FFA726;
                    color: #000000;
                }
                QMenu {
                    background-color: #FFE0B2;
                    border: 1px solid #F57C00;
                }
                QMenu::item {
                    padding: 6px 20px;
                    color: #3E2723;
                }
                QMenu::item:selected {
                    background-color: #FFB74D;
                    color: #000000;
                    font-weight: bold;
                }
            """)
        else:
            menubar.setStyleSheet("")

    def initUI(self):
        self.setWindowTitle(get_text(self.lang, "window_title"))
        self.resize(1400, 800)

        menubar = self.menuBar()
        self.update_menu_style()

        self.action_open_dir = QAction("📂 Operatör Veri Tabanı (0)", self)
        self.action_open_dir.triggered.connect(self.open_directory_dialog)
        menubar.addAction(self.action_open_dir)

        self.action_open_controllers = QAction(
            "🎙️ Çevrimi Yapan Operatörler", self
        )
        self.action_open_controllers.triggered.connect(self.open_controllers_dialog)
        menubar.addAction(self.action_open_controllers)

        self.action_open_stats = QAction("📊 Çevrim İstatistikleri", self)
        self.action_open_stats.triggered.connect(self.open_statistics_dialog)
        menubar.addAction(self.action_open_stats)

        self.action_open_logbook = QAction("📖 Logbook (Geçmiş Sorgula)", self)
        self.action_open_logbook.triggered.connect(self.open_logbook_dialog)
        menubar.addAction(self.action_open_logbook)

        # Hediye Sistemi özel olarak doğrudan tıklanan bir QAction olarak
        # ekleniyor. QMenu/aboutToShow kullanılmıyor; böylece mouse hover
        # kesinlikle pencere açmıyor.
        self.menu_gifts = QAction("🎁 Hediye Sistemi", self)
        self.menu_gifts.triggered.connect(self.open_gift_editor)
        menubar.addAction(self.menu_gifts)

        self.action_qsl = QAction(get_text(self.lang, "qsl_menu"), self)
        self.action_qsl.triggered.connect(self.open_qsl_dialog)
        menubar.addAction(self.action_qsl)

        self.action_echolink = QAction(get_text(self.lang, "echolink_btn"), self)
        self.action_echolink.triggered.connect(self.open_echolink)
        menubar.addAction(self.action_echolink)

        self.action_demo = QAction(get_text(self.lang, "demo_menu"), self)
        self.action_demo.triggered.connect(self.toggle_demo_mode)
        menubar.addAction(self.action_demo)

        self.action_normal = QAction(get_text(self.lang, "normal_menu"), self)
        self.action_normal.triggered.connect(self.toggle_demo_mode)
        menubar.addAction(self.action_normal)
        self.action_normal.setVisible(False)

        self.menu_lang = menubar.addMenu("🌐 Dil / Language")
        self.act_tr = QAction("🇹🇷 Türkçe", self)
        self.act_tr.triggered.connect(lambda: self.change_language("TR"))
        self.act_en = QAction("🇬🇧 English", self)
        self.act_en.triggered.connect(lambda: self.change_language("EN"))
        self.act_de = QAction("🇩🇪 Deutsch", self)
        self.act_de.triggered.connect(lambda: self.change_language("DE"))
        self.menu_lang.addAction(self.act_tr)
        self.menu_lang.addAction(self.act_en)
        self.menu_lang.addAction(self.act_de)

        # Çevrim kayıt kontrolü: menü çubuğunun hemen altında küçük sekme.
        registration_bar = QHBoxLayout()
        registration_bar.setContentsMargins(0, 2, 0, 2)
        registration_bar.addStretch(1)
        self.btn_close_net = QPushButton()
        self.btn_close_net.setFixedSize(190, 30)
        self.btn_close_net.setStyleSheet("QPushButton { background-color: #D6CE91; color: white; border: 1px solid #9F9760; border-radius: 5px; padding: 3px 8px; } QPushButton:hover { background-color: #C2B979; } QPushButton:pressed { background-color: #ADA564; }")
        self.btn_close_net.clicked.connect(self.toggle_net_registrations)
        self.btn_close_net.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 10px;
                border: 1px solid #990000;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
            QPushButton:pressed {
                background-color: #801818;
            }
            QPushButton:disabled {
                background-color: #D98A8A;
                color: #777777;
            }
        """)
        registration_bar.addWidget(self.btn_close_net, 0, Qt.AlignmentFlag.AlignRight)

        main_container = QWidget()
        self.full_layout = QVBoxLayout()
        self.full_layout.addLayout(registration_bar)

        header_area = QHBoxLayout()

        logo_path = None
        for ext in [".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"]:
            test_path = f"logo{ext}"
            if os.path.exists(test_path):
                logo_path = test_path
                break

        if logo_path:
            logo_label = QLabel()
            img = QImage(logo_path).convertToFormat(QImage.Format.Format_ARGB32)
            for x in range(img.width()):
                for y in range(img.height()):
                    pixel = img.pixelColor(x, y)
                    if (
                        pixel.red() > 240
                        and pixel.green() > 240
                        and pixel.blue() > 240
                    ):
                        img.setPixelColor(x, y, QColor(0, 0, 0, 0))

            pixmap = QPixmap.fromImage(img)
            logo_label.setPixmap(
                pixmap.scaled(
                    115,
                    115,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            logo_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            logo_label.setFixedSize(115, 115)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Logo büyütülmüş durumda; negatif üst marj logonun üst kısmını
            # pencere tarafından kırpıyordu. Marj kaldırılarak logo eksiksiz gösterilir.
            logo_label.setStyleSheet("background-color: transparent; border: none;")
            header_area.addWidget(logo_label)

        title_widget = QWidget()
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.header_label = QLabel(get_text(self.lang, "header_title"))
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #1A237E; "
            "padding-bottom: 30px;"
        )
        title_layout.addWidget(self.header_label)

        self.lbl_datetime = QLabel()
        self.lbl_datetime.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_datetime.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #004D40;"
        )
        title_layout.addWidget(self.lbl_datetime)

        self.lbl_net_controllers_main = QLabel()
        self.lbl_net_controllers_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_net_controllers_main.setWordWrap(True)
        self.lbl_net_controllers_main.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #37474F; margin-top: 3px;"
        )
        title_layout.addWidget(self.lbl_net_controllers_main)

        title_widget.setLayout(title_layout)
        header_area.addWidget(title_widget, 1)

        self.full_layout.addLayout(header_area)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

        self.update_net_controllers_label()

        main_layout = QHBoxLayout()

        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.center_title_label = QLabel()
        self.center_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #0D47A1; padding: 6px;"
            " background-color: #E3F2FD; border-radius: 4px;"
        )
        center_layout.addWidget(self.center_title_label)

        self.lbl_call_title = QLabel()
        center_layout.addWidget(self.lbl_call_title)

        self.input_callsign = QLineEdit()
        self.input_callsign.returnPressed.connect(self.save_record)
        center_layout.addWidget(self.input_callsign)

        self.setup_callsign_completer()

        self.lbl_phonetic = QLabel("-")
        self.lbl_phonetic.setWordWrap(True)
        self.lbl_phonetic.setStyleSheet("color: gray; font-style: italic;")
        center_layout.addWidget(self.lbl_phonetic)

        self.lbl_name_title = QLabel()
        center_layout.addWidget(self.lbl_name_title)

        self.input_name = QLineEdit()
        self.input_name.textChanged.connect(self.on_main_name_text_changed)
        self.input_name.returnPressed.connect(self.save_record)
        center_layout.addWidget(self.input_name)

        self.lbl_qth_title = QLabel()
        center_layout.addWidget(self.lbl_qth_title)

        self.input_qth = QLineEdit()
        self.input_qth.textChanged.connect(self.on_main_qth_text_changed)
        self.input_qth.returnPressed.connect(self.save_record)
        center_layout.addWidget(self.input_qth)

        self.lbl_notes_title = QLabel()
        center_layout.addWidget(self.lbl_notes_title)

        self.input_notes = QLineEdit()
        self.input_notes.textChanged.connect(self.on_main_notes_text_changed)
        self.input_notes.returnPressed.connect(self.save_record)
        center_layout.addWidget(self.input_notes)

        self.btn_save = QPushButton()
        self.btn_save.clicked.connect(self.save_record)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #00796B;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #004D40;
            }
        """)
        center_layout.addWidget(self.btn_save)

        if HAS_WEBENGINE:
            self.map_view = QWebEngineView()
            self.map_view.setMaximumHeight(230 + 265 + 21)
            center_layout.addWidget(self.map_view)

            # OpenStreetMap attribution haritanın DIŞINDA, sol altta.
            self.lbl_map_attr = QLabel("© OpenStreetMap contributors")
            self.lbl_map_attr.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.lbl_map_attr.setStyleSheet(
                "font-size: 10px; color: #555555; padding: 0px 0px 0px 4px;"
            )
            center_layout.addWidget(self.lbl_map_attr)
        else:
            self.list_bottom_distances = QListWidget()
            self.list_bottom_distances.setMaximumHeight(200 + 265)
            center_layout.addWidget(self.list_bottom_distances)

        right_layout = QVBoxLayout()

        right_top_layout = QHBoxLayout()
        self.right_title_label = QLabel()
        self.right_title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.right_title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1B5E20; padding: 6px;"
            " background-color: #E8F5E9; border-radius: 4px;"
        )

        self.lbl_stats_header = QLabel()
        self.lbl_stats_header.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_stats_header.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #0277BD; padding: 6px 10px;"
            " background-color: #E1F5FE; border: 1px solid #B3E5FC; border-radius: 4px;"
        )

        right_top_layout.addWidget(self.right_title_label, 1)

        self.qsl_enabled_checkbox = QCheckBox("QSL KARTI OLUŞTUR")
        self.qsl_enabled_checkbox.setChecked(True)
        self.qsl_enabled_checkbox.setStyleSheet(
            "QCheckBox { font-weight: bold; padding: 4px; }"
        )
        right_top_layout.addWidget(self.qsl_enabled_checkbox, 0)

        self.btn_operator_search = QPushButton("🔎 ARA")
        self.btn_operator_search.setFixedSize(105, 38)
        self.btn_operator_search.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #222222;
                font-size: 13px;
                font-weight: 600;
                border: 1px solid #AAAAAA;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        self.btn_operator_search.clicked.connect(self.toggle_operator_search)
        right_top_layout.addWidget(self.btn_operator_search, 0)

        right_top_layout.addWidget(self.lbl_stats_header, 0)
        right_layout.addLayout(right_top_layout)

        self.operator_search_bar = QWidget()
        search_bar_layout = QHBoxLayout(self.operator_search_bar)
        search_bar_layout.setContentsMargins(0, 2, 0, 4)
        search_bar_layout.setSpacing(6)
        self.operator_search_input = QLineEdit()
        self.operator_search_input.setFixedWidth(300)
        self.operator_search_input.setPlaceholderText(
            "ÇAĞRI İŞARETİ VEYA İSİM SOYİSİM ARA..."
        )
        self.operator_search_input.setClearButtonEnabled(True)
        self.operator_search_input.setStyleSheet("""
            QLineEdit {
                background: #FFFFFF;
                color: #000000;
                border: 2px solid #AAAAAA;
                border-radius: 5px;
                padding: 7px 10px;
                font-size: 13px;
                font-weight: normal;
            }
        """)
        self.operator_search_input.returnPressed.connect(
            self.search_logged_operators
        )
        self.btn_do_operator_search = QPushButton("ARA")
        self.btn_do_operator_search.setFixedWidth(75)
        self.btn_do_operator_search.setStyleSheet("""
            QPushButton {
                background: #E0E0E0;
                color: #222222;
                font-weight: 600;
                border: 1px solid #AAAAAA;
                border-radius: 5px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background: #D0D0D0;
            }
        """)
        self.btn_do_operator_search.clicked.connect(
            self.search_logged_operators
        )
        search_bar_layout.addWidget(self.operator_search_input, 0)
        search_bar_layout.addWidget(self.btn_do_operator_search, 0)
        search_bar_layout.addStretch(1)
        right_layout.addWidget(self.operator_search_bar)
        self.operator_search_bar.setVisible(False)

        self.lbl_counter = QLabel()
        self.lbl_counter.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(self.lbl_counter)


        self.table = QTableWidget(0, 7)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self.table.itemChanged.connect(self.on_table_item_changed)
        right_layout.addWidget(self.table)

        self.btn_delete_record = QPushButton()
        self.btn_delete_record.clicked.connect(self.delete_record)
        self.btn_delete_record.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
        """)
        right_layout.addWidget(self.btn_delete_record)

        self.btn_draw = QPushButton()
        self.btn_draw.clicked.connect(self.open_live_raffle_screen)
        self.btn_draw.setStyleSheet("""
            QPushButton {
                background-color: #F34723;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D93C1F;
            }
        """)
        right_layout.addWidget(self.btn_draw)

        self.btn_export = QPushButton()
        self.btn_export.clicked.connect(self.export_pdf)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1B5E20;
            }
        """)
        right_layout.addWidget(self.btn_export)

        self.btn_reset_all = QPushButton()
        self.btn_reset_all.clicked.connect(self.action_reset_full_list)
        self.btn_reset_all.setStyleSheet("""
            QPushButton {
                background-color: #C62828;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #8E0000;
            }
        """)
        right_layout.addWidget(self.btn_reset_all)

        self.echolink_container = QWidget()
        echolink_layout = QVBoxLayout(self.echolink_container)
        echolink_layout.setContentsMargins(0, 0, 0, 0)

        echolink_header = QHBoxLayout()
        echolink_title = QLabel("🌐 ECHOLINK WEB APP")
        echolink_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #0D47A1;")

        btn_close_echolink = QPushButton("KAPAT")
        btn_close_echolink.setFixedWidth(85)
        btn_close_echolink.setStyleSheet("""
            QPushButton {
                background-color: #B22222;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #9B1C1C;
            }
        """)
        btn_close_echolink.clicked.connect(
            lambda: self.echolink_container.setVisible(False)
        )

        echolink_header.addWidget(echolink_title)
        echolink_header.addWidget(btn_close_echolink)
        echolink_layout.addLayout(echolink_header)

        if HAS_WEBENGINE:
            self.web_view = QWebEngineView()
            page = self.web_view.page()

            page.settings().setAttribute(
                QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False
            )

            profile_dir = os.path.abspath("./echolink_profile")
            os.makedirs(profile_dir, exist_ok=True)

            profile = page.profile()
            profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
            )
            profile.setPersistentStoragePath(profile_dir)
            profile.setCachePath(os.path.join(profile_dir, "cache"))

            page.featurePermissionRequested.connect(
                self.on_feature_permission_requested
            )

            self.web_view.setUrl(QUrl("https://webapp.echolink.org/"))
            echolink_layout.addWidget(self.web_view)
        else:
            lbl_no_web = QLabel(
                "Gömülü tarayıcı için 'PyQt6-WebEngine' kütüphanesi"
                " yüklenmelidir.\n(pip install PyQt6-WebEngine)"
            )
            lbl_no_web.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_no_web.setWordWrap(True)
            lbl_no_web.setStyleSheet(
                "background-color: #FFF3E0; border: 1px solid #FFE0B2; padding:"
                " 20px; color: #E65100; font-weight: bold;"
            )
            echolink_layout.addWidget(lbl_no_web)

        self.echolink_container.setVisible(False)

        main_layout.addLayout(center_layout, 4)
        main_layout.addLayout(right_layout, 6)
        main_layout.addWidget(self.echolink_container, 4)

        self.full_layout.addLayout(main_layout)

        self.lbl_trademark_footer = QLabel(
            "EchoLink® ilgili hak sahiplerinin tescilli markasıdır."
        )
        self.lbl_trademark_footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_trademark_footer.setStyleSheet(
            "font-size: 9px; color: #555555; font-style: italic; padding-right: 6px;"
        )

        self.footer_label = QLabel()
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.footer_label.setStyleSheet(
            "font-size: 10px; font-weight: normal; color: #000000; padding: 2px 6px;"
            " font-family: monospace;"
        )

        self.full_layout.addWidget(self.lbl_trademark_footer)
        self.full_layout.addWidget(self.footer_label)

        main_container.setLayout(self.full_layout)
        self.setCentralWidget(main_container)

        self.retranslate_ui()
        self.load_operator_pool_from_db()
        self.refresh_table()

    def toggle_operator_search(self):
        """ARA alanını göster/gizle."""
        visible = not self.operator_search_bar.isVisible()
        self.operator_search_bar.setVisible(visible)
        if visible:
            self.operator_search_input.setFocus()
            self.operator_search_input.selectAll()
        else:
            self.operator_search_input.clear()
            self.search_logged_operators()

    def search_logged_operators(self):
        """Kayıtlı operatörleri çağrı işareti veya isim/soyisim ile filtrele."""
        if not hasattr(self, "operator_search_input"):
            return

        query = self.operator_search_input.text().strip().upper()
        query = query.replace("İ", "I").replace("ı", "i").upper()

        for row in range(self.table.rowCount()):
            call_item = self.table.item(row, 0)
            name_item = self.table.item(row, 1)

            callsign = call_item.text().strip().upper() if call_item else ""
            name = name_item.text().strip().upper() if name_item else ""

            # Hem çağrı işareti hem de isim/soyisim alanında arama yapılır.
            normalized_callsign = callsign.replace("İ", "I")
            normalized_name = name.replace("İ", "I")

            match = (
                not query
                or query in normalized_callsign
                or query in normalized_name
            )
            self.table.setRowHidden(row, not match)

        # Eşleşen ilk satıra git.
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                self.table.selectRow(row)
                self.table.scrollToItem(
                    self.table.item(row, 0),
                    QAbstractItemView.ScrollHint.PositionAtCenter
                )
                break

    def update_relay_map(self):
        if not HAS_WEBENGINE or not hasattr(self, "map_view"):
            return

        markers_js = ""
        polylines_js = ""
        if hasattr(self, "raw_rows") and self.raw_rows:
            for row_data in self.raw_rows:
                callsign = str(row_data[1]).split(" ")[0].upper()
                op_name = (
                    str(row_data[2]).upper().replace("i", "İ").replace("ı", "I")
                )
                qth = str(row_data[3]).upper() if row_data[3] else "BİLİNMİYOR"

                matched_coord = None
                normalized_qth = tr_normalize(qth)
                sorted_keys = sorted(CITY_COORDS.keys(), key=len, reverse=True)
                for key in sorted_keys:
                    if key in normalized_qth:
                        matched_coord = CITY_COORDS[key]
                        break

                if matched_coord:
                    lat, lon = matched_coord
                    popup_text = f"<b>{callsign}</b><br>{op_name}<br>QTH: {qth}"
                    markers_js += (
                        f"L.marker([{lat}, {lon}]).addTo(map).bindPopup('{popup_text}');\n"
                    )
                    polylines_js += (
                        f"L.polyline([[{ROLE_LAT}, {ROLE_LON}], [{lat}, {lon}]], "
                        "{color: 'blue', weight: 2, opacity: 0.6, dashArray: '5, 5'}).addTo(map);\n"
                    )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                html, body, #map {{ width: 100%; height: 100%; margin: 0; padding: 0; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{ROLE_LAT}, {ROLE_LON}], 7);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);

                var relayIcon = L.icon({{
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
                }});
                L.marker([{ROLE_LAT}, {ROLE_LON}], {{icon: relayIcon}}).addTo(map)
                    .bindPopup("<b>Anarad Karamürsel Rölesi</b><br>Kocaeli (YM2KDB)");

                {markers_js}
                {polylines_js}
            </script>
        </body>
        </html>
        """
        self.map_view.setHtml(html_content)

    def on_table_item_changed(self, item):
        if not item:
            return

        column = item.column()
        # 0=Çağrı işareti, 1=İsim, 2=QTH, 5=Notlar
        if column not in [0, 1, 2, 5]:
            return

        db_id = item.data(Qt.ItemDataRole.UserRole)
        if not db_id:
            return

        new_value = item.text().strip().upper().replace("i", "İ").replace("ı", "I")

        if column == 0:
            # Çağrı işaretinin TAMAMINI koru.
            # Örn: TA2TTL/PORTATIF, TA2TTL/MOBILE, TA2TTL/1 vb.
            # Burada boşluğa göre kesme YOK; "/" sonrasındaki bölüm de korunur.
            if not new_value:
                self.refresh_table()
                return
        elif column == 5 and new_value == "-":
            new_value = ""

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, user_id, callsign, op_name, qth, notes, timestamp, "
                "session_id, is_winner, prize, is_echolink FROM logs WHERE id=?",
                (db_id,),
            )
            old_row = cursor.fetchone()
            if not old_row:
                conn.close()
                self.refresh_table()
                return

            old_callsign = str(old_row[2]).strip().upper()
            pool_table = "demo_operator_pool" if self.is_demo_mode else "operator_pool"

            if column == 0:
                if new_value == old_callsign:
                    conn.close()
                    return

                # Aynı çağrı işareti bu oturumda varsa işlem yapma.
                cursor.execute(
                    "SELECT 1 FROM logs WHERE callsign=? AND session_id=? AND id<>?",
                    (new_value, self.net_session_id, db_id),
                )
                if cursor.fetchone():
                    QMessageBox.warning(
                        self,
                        "Uyarı",
                        f"'{new_value}' çağrı işareti bu oturumda zaten kayıtlı."
                    )
                    conn.close()
                    self.refresh_table()
                    return

                # ==========================================================
                # ÖZEL YENİ OPERATÖR KURALI
                #
                # Çağrı işaretinin içinde, ilk çağrı işaretinden SONRA "/"
                # varsa ve "/" sonrasında bir ifade bulunuyorsa:
                #
                #     TA2TTL -> TA2TTL/PORTATIF
                #     TA2TTL -> TA2TTL/MOBILE
                #     TA2TTL -> TA2TTL/1
                #
                # ESKİ TA2TTL KAYDINA DOKUNULMAZ.
                # Yeni çağrı işareti ayrı bir operatör olarak eklenir.
                # ==========================================================
                slash_pos = new_value.find("/")
                is_new_slash_operator = (
                    slash_pos > 0
                    and slash_pos < len(new_value) - 1
                    and not old_callsign.endswith("/")
                )

                if is_new_slash_operator:
                    # Yeni çağrı işareti operator_pool'da zaten var mı?
                    cursor.execute(
                        f"SELECT 1 FROM {pool_table} WHERE callsign=?",
                        (new_value,),
                    )
                    if cursor.fetchone():
                        QMessageBox.warning(
                            self,
                            "Uyarı",
                            f"'{new_value}' zaten operatör veri tabanında kayıtlı."
                        )
                        conn.close()
                        self.refresh_table()
                        return

                    # ------------------------------------------------------
                    # 1) YENİ operator_pool kaydı
                    # ------------------------------------------------------
                    cursor.execute(
                        f"INSERT INTO {pool_table} (callsign, name, qth, notes) "
                        f"VALUES (?, ?, ?, ?)",
                        (
                            new_value,
                            old_row[3],
                            old_row[4],
                            old_row[5] or "",
                        ),
                    )

                    # ------------------------------------------------------
                    # 2) ESKİ logs satırına UPDATE YOK!
                    #    Aynı bilgilerle YENİ logs satırı oluştur.
                    # ------------------------------------------------------
                    cursor.execute(
                        "INSERT INTO logs "
                        "(user_id, callsign, op_name, qth, notes, timestamp, "
                        "session_id, is_winner, prize, is_echolink) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            old_row[1],
                            new_value,
                            old_row[3],
                            old_row[4],
                            old_row[5],
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            self.net_session_id,
                            0,
                            None,
                            1 if new_value == self.pending_echolink_callsign else 0,
                        ),
                    )

                    # Yeni logs kaydını son kayıt olarak göstermek için.
                    self._last_added_db_id = cursor.lastrowid

                else:
                    # "/" özel kuralına girmeyen normal çağrı işareti
                    # değişikliği: mevcut operatör yeniden adlandırılır.
                    cursor.execute(
                        "UPDATE logs SET callsign=? WHERE id=?",
                        (new_value, db_id),
                    )
                    cursor.execute(
                        f"UPDATE {pool_table} SET callsign=? WHERE callsign=?",
                        (new_value, old_callsign),
                    )

            elif column == 1:
                cursor.execute(
                    "UPDATE logs SET op_name=? WHERE id=?",
                    (new_value, db_id),
                )
                cursor.execute(
                    f"UPDATE {pool_table} SET name=? WHERE callsign=?",
                    (new_value, old_callsign),
                )

            elif column == 2:
                cursor.execute(
                    "UPDATE logs SET qth=? WHERE id=?",
                    (new_value, db_id),
                )
                cursor.execute(
                    f"UPDATE {pool_table} SET qth=? WHERE callsign=?",
                    (new_value, old_callsign),
                )

            elif column == 5:
                cursor.execute(
                    "UPDATE logs SET notes=? WHERE id=?",
                    (new_value, db_id),
                )
                try:
                    cursor.execute(
                        f"UPDATE {pool_table} SET notes=? WHERE callsign=?",
                        (new_value, old_callsign),
                    )
                except sqlite3.OperationalError:
                    pass

            conn.commit()

        except Exception as e:
            conn.rollback()
            QMessageBox.warning(
                self,
                "Düzenleme Hatası",
                f"Değişiklik kaydedilemedi:\n{e}",
            )
        finally:
            conn.close()

        self.table.blockSignals(True)
        try:
            self.load_operator_pool_from_db()
            self.refresh_table()
        finally:
            self.table.blockSignals(False)

        if (
            column == 0
            and "slash_pos" in locals()
            and is_new_slash_operator
            and hasattr(self, "_last_added_db_id")
        ):
            self._highlight_latest_operator(self._last_added_db_id)

    def retranslate_ui(self):
        self.setWindowTitle(get_text(self.lang, "window_title"))
        self.action_open_controllers.setText(get_text(self.lang, "ctrl_btn"))
        self.action_open_stats.setText(get_text(self.lang, "stats_btn"))
        self.action_open_logbook.setText(get_text(self.lang, "logbook_btn"))
        self.menu_gifts.setText(get_text(self.lang, "gift_menu"))
        self.action_qsl.setText(get_text(self.lang, "qsl_menu"))
        self.action_echolink.setText(get_text(self.lang, "echolink_btn"))
        self.action_demo.setText(get_text(self.lang, "demo_menu"))
        self.action_normal.setText(get_text(self.lang, "normal_menu"))
        self.menu_lang.setTitle(get_text(self.lang, "lang_menu"))

        self.header_label.setText(get_text(self.lang, "header_title"))
        self.center_title_label.setText(get_text(self.lang, "center_title"))

        self.lbl_call_title.setText(get_text(self.lang, "callsign_lbl"))
        self.input_callsign.setPlaceholderText(
            get_text(self.lang, "callsign_ph")
        )

        self.lbl_name_title.setText(get_text(self.lang, "name_lbl"))
        self.input_name.setPlaceholderText(get_text(self.lang, "name_ph"))

        self.lbl_qth_title.setText(get_text(self.lang, "qth_lbl"))
        self.input_qth.setPlaceholderText(get_text(self.lang, "qth_ph"))

        self.lbl_notes_title.setText(get_text(self.lang, "notes_lbl"))
        self.input_notes.setPlaceholderText(get_text(self.lang, "notes_ph"))

        self.btn_save.setText(get_text(self.lang, "save_btn"))

        if hasattr(self, "lbl_dist_box_title"):
            self.lbl_dist_box_title.setText("")

        th1 = get_text(self.lang, "th_call")
        th2 = get_text(self.lang, "th_name")
        th3 = get_text(self.lang, "th_qth")
        th4 = get_text(self.lang, "th_dist")
        th5 = get_text(self.lang, "th_date")
        th6 = get_text(self.lang, "th_notes")
        th7 = get_text(self.lang, "th_gift")
        self.table.setHorizontalHeaderLabels(
            [th1, th2, th3, th4, th5, th6, th7]
        )

        self.btn_delete_record.setText(get_text(self.lang, "del_rec_btn"))
        self.btn_draw.setText(get_text(self.lang, "draw_btn"))
        self._update_registration_button_text()
        self.btn_export.setText(get_text(self.lang, "pdf_btn"))
        self.btn_reset_all.setText(get_text(self.lang, "reset_btn"))

        self.footer_label.setText(
            "Sürüm v 4.0.2    BUILD: 20260904 Program Sorumlusu   © 2026 DENİZ ERTÜRK TA2TTL"
        )

        self.update_net_controllers_label()
        self.load_operator_pool_from_db()
        self.refresh_table()

    def update_net_controllers_label(self):
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT callsign, name FROM net_controllers WHERE session_id=? ORDER"
                " BY id ASC",
                (self.net_session_id,),
            )
            controllers = cursor.fetchall()
            conn.close()

            prefix = get_text(self.lang, "controllers_prefix")
            no_ctrl = get_text(self.lang, "no_controller")
            if controllers:
                ctrl_list = [f"{c[0]} - {c[1]}" for c in controllers]
                self.lbl_net_controllers_main.setText(
                    f"{prefix} {', '.join(ctrl_list)}".upper()
                )
                self.lbl_net_controllers_main.setVisible(True)
            else:
                self.lbl_net_controllers_main.setText(no_ctrl)
                self.lbl_net_controllers_main.setVisible(True)
        except Exception:
            self.lbl_net_controllers_main.setVisible(False)

    def update_datetime(self):
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M:%S")
        d_lbl = get_text(self.lang, "date_lbl")
        t_lbl = get_text(self.lang, "time_lbl")
        self.lbl_datetime.setText(
            f"{d_lbl}: {date_str}    |    {t_lbl}: {time_str}"
        )

    def action_reset_full_list(self):
        if self.is_demo_mode:
            msg = (
                "Demo modundasınız. Komple çevrim kayıt listesini silmek"
                " istediğinize emin misiniz?"
                if self.lang == "TR"
                else ("Are you sure?" if self.lang == "EN" else "Sicher?")
            )
        else:
            msg = (
                "Komple çevrim kayıt listesini sıfırlamak (yeni oturum açmak)"
                " istediğinize emin misiniz?"
                if self.lang == "TR"
                else ("Are you sure?" if self.lang == "EN" else "Sicher?")
            )

        reply = QMessageBox.question(
            self,
            "Komple Sıfırlama Onayı",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if self.is_demo_mode:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM logs WHERE session_id=?", (self.demo_session_id,)
            )
            cursor.execute(
                "DELETE FROM net_controllers WHERE session_id=?", (self.demo_session_id,)
            )
            conn.commit()
            conn.close()
        else:
            new_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            with open("session_id.txt", "w") as f:
                f.write(new_id)
            self.net_session_id = new_id

        self.registration_closed = False
        self.raffle_completed = False
        self.session_winner_ids.clear()
        self.session_winner_prizes.clear()
        self.drawn_gift_ids.clear()
        self.current_gift_assignment_id = None
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            conn.execute("DELETE FROM gift_assignments")
            conn.commit()
            conn.close()
        except Exception:
            pass
        self._sync_registration_controls()

        self.refresh_table()
        self.update_net_controllers_label()

    def delete_record(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return

        item = self.table.item(current_row, 0)
        callsign = item.text()

        msg = (
            f"'{callsign}' çağrı işaretli operatör silmek istediğinize emin"
            " misiniz?"
            if self.lang == "TR"
            else ("Are you sure?" if self.lang == "EN" else "Sicher?")
        )
        reply = QMessageBox.question(
            self,
            "Silme Onayı",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            db_id = item.data(Qt.ItemDataRole.UserRole)
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logs WHERE id=?", (db_id,))
            conn.commit()
            conn.close()
            self.refresh_table()

    def setup_callsign_completer(self):
        pool_suggestions = []
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS operator_pool (id INTEGER PRIMARY KEY"
                " AUTOINCREMENT, callsign TEXT UNIQUE, name TEXT, qth TEXT, notes"
                " TEXT)"
            )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS demo_operator_pool (id INTEGER PRIMARY"
                " KEY AUTOINCREMENT, callsign TEXT UNIQUE, name TEXT, qth TEXT, notes"
                " TEXT)"
            )
            try:
                cursor.execute("ALTER TABLE operator_pool ADD COLUMN notes TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE demo_operator_pool ADD COLUMN notes TEXT")
            except:
                pass

            if self.is_demo_mode:
                cursor.execute(
                    "SELECT callsign, name, qth, notes FROM demo_operator_pool"
                )
            else:
                cursor.execute("SELECT callsign, name, qth, notes FROM operator_pool")

            fetched_rows = cursor.fetchall()
            conn.close()

            sorted_rows = sorted(fetched_rows, key=lambda x: sort_key_callsign(x[0]))

            for r in sorted_rows:
                qth_val = (
                    r[2].upper().replace("i", "İ").replace("ı", "I")
                    if r[2]
                    else "BİLİNMİYOR"
                )
                name_val = (
                    r[1].upper().replace("i", "İ").replace("ı", "I")
                    if r[1]
                    else "BİLİNMİYOR"
                )
                notes_val = (
                    r[3].upper().replace("i", "İ").replace("ı", "I") if r[3] else ""
                )
                pool_suggestions.append(
                    f"{r[0]} {name_val} ({qth_val}) | {notes_val}".strip(" |")
                )
        except:
            pass

        self.completer = QCompleter(pool_suggestions, self)
        self.completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        self.completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        self.completer.activated.connect(self.on_completer_activated)
        self.input_callsign.setCompleter(self.completer)

        if not getattr(self, "_callsign_signal_connected", False):
            self.input_callsign.textChanged.connect(self.on_callsign_text_changed)
            self._callsign_signal_connected = True

    def on_callsign_text_changed(self, text):
        if getattr(self, "_updating_callsign_text", False):
            return
        upper_text = text.upper().replace("i", "İ").replace("ı", "I")
        if text != upper_text:
            self._updating_callsign_text = True
            try:
                cursor_pos = self.input_callsign.cursorPosition()
                self.input_callsign.setText(upper_text)
                self.input_callsign.setCursorPosition(min(cursor_pos, len(upper_text)))
            finally:
                self._updating_callsign_text = False

        clean_call = upper_text.split(" ")[0]
        self.lbl_phonetic.setText(phonetic.get_phonetic(clean_call))

    def on_main_name_text_changed(self, text):
        upper_text = text.upper().replace("i", "İ").replace("ı", "I")
        self.input_name.textChanged.disconnect()
        cursor_pos = self.input_name.cursorPosition()
        self.input_name.setText(upper_text)
        self.input_name.setCursorPosition(cursor_pos)
        self.input_name.textChanged.connect(self.on_main_name_text_changed)

    def on_main_qth_text_changed(self, text):
        upper_text = text.upper().replace("i", "İ").replace("ı", "I")
        self.input_qth.textChanged.disconnect()
        cursor_pos = self.input_qth.cursorPosition()
        self.input_qth.setText(upper_text)
        self.input_qth.setCursorPosition(cursor_pos)
        self.input_qth.textChanged.connect(self.on_main_qth_text_changed)

    def on_main_notes_text_changed(self, text):
        upper_text = text.upper().replace("i", "İ").replace("ı", "I")
        self.input_notes.textChanged.disconnect()
        cursor_pos = self.input_notes.cursorPosition()
        self.input_notes.setText(upper_text)
        self.input_notes.setCursorPosition(cursor_pos)
        self.input_notes.textChanged.connect(self.on_main_notes_text_changed)

    def on_completer_activated(self, text):
        self.parse_and_fill_fields(text)

    def parse_and_fill_fields(self, full_text):
        try:
            parts = full_text.strip().split(" ")
            callsign = parts[0].upper()

            try:
                self.input_callsign.textChanged.disconnect()
            except:
                pass
            self.input_callsign.setText(callsign)
            self.input_callsign.textChanged.connect(self.on_callsign_text_changed)

            qth_val = "BİLİNMİYOR"
            notes_val = ""

            if "|" in full_text:
                main_part, notes_part = full_text.split("|", 1)
                notes_val = (
                    notes_part.strip().upper().replace("i", "İ").replace("ı", "I")
                )
                full_text_for_qth = main_part
            else:
                full_text_for_qth = full_text

            if "(" in full_text_for_qth and ")" in full_text_for_qth:
                qth_val = (
                    full_text_for_qth.split("(")[1]
                    .split(")")[0]
                    .upper()
                    .replace("i", "İ")
                    .replace("ı", "I")
                )
                name_val = (
                    full_text_for_qth.split(callsign)[1]
                    .split("(")[0]
                    .strip()
                    .upper()
                    .replace("i", "İ")
                    .replace("ı", "I")
                )
            else:
                name_val = (
                    " ".join(parts[1:]).upper().replace("i", "İ").replace("ı", "I")
                )

            try:
                self.input_name.textChanged.disconnect()
            except:
                pass
            self.input_name.setText(name_val)
            self.input_name.textChanged.connect(self.on_main_name_text_changed)

            try:
                self.input_qth.textChanged.disconnect()
            except:
                pass
            self.input_qth.setText(qth_val)
            self.input_qth.textChanged.connect(self.on_main_qth_text_changed)

            self.current_notes = notes_val
            try:
                self.input_notes.textChanged.disconnect()
            except:
                pass
            self.input_notes.setText(notes_val)
            self.input_notes.textChanged.connect(self.on_main_notes_text_changed)

            self.lbl_phonetic.setText(phonetic.get_phonetic(callsign))
        except:
            pass

    def load_operator_pool_from_db(self):
        self.setup_callsign_completer()
        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()
            if self.is_demo_mode:
                cursor.execute("SELECT COUNT(*) FROM demo_operator_pool")
            else:
                cursor.execute("SELECT COUNT(*) FROM operator_pool")
            pool_count = cursor.fetchone()[0]
            conn.close()
            dir_text = (
                "Operatör Veri Tabanı"
                if self.lang == "TR"
                else ("Operator Database" if self.lang == "EN" else "Operatoren-Datenbank")
            )
            self.action_open_dir.setText(f"📂 {dir_text} ({pool_count})")
        except:
            pass

    def save_record(self):
        if self.registration_closed:
            return
        conn = None
        try:
            callsign = self.input_callsign.text().strip().upper().split(" ")[0]
            name = self.input_name.text().strip().upper().replace("i", "İ").replace("ı", "I")
            qth = self.input_qth.text().strip().upper().replace("i", "İ").replace("ı", "I")
            notes = self.input_notes.text().strip().upper().replace("i", "İ").replace("ı", "I")

            if not notes and self.current_notes:
                notes = self.current_notes.strip().upper().replace("i", "İ").replace("ı", "I")

            if not callsign or not name or not qth:
                return

            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=15.0)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT 1 FROM logs WHERE callsign=? AND session_id=?",
                (callsign, self.net_session_id),
            )
            if cursor.fetchone():
                conn.close()
                conn = None
                msg = (
                    f"'{callsign}' çağrı işaretli operatör bu oturumda zaten kayıtlı!"
                    if self.lang == "TR" else "Already logged!"
                )
                QMessageBox.warning(self, "Uyarı", msg)
                self.input_callsign.clear()
                self.input_name.clear()
                self.input_qth.clear()
                self.input_notes.clear()
                self.current_notes = ""
                self.input_callsign.setFocus()
                self.input_callsign.selectAll()
                return

            is_echolink_val = 1 if callsign == self.pending_echolink_callsign else 0

            cursor.execute(
                "INSERT INTO logs (user_id, callsign, op_name, qth, notes, timestamp, "
                "session_id, is_winner, is_echolink) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)",
                (
                    self.current_user[0],
                    callsign,
                    name,
                    qth,
                    notes,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                    self.net_session_id,
                    is_echolink_val,
                ),
            )

            if callsign == self.pending_echolink_callsign:
                self.pending_echolink_callsign = None

            pool_table = "demo_operator_pool" if self.is_demo_mode else "operator_pool"
            cursor.execute(
                f"SELECT 1 FROM {pool_table} WHERE callsign=?",
                (callsign,),
            )
            if cursor.fetchone():
                cursor.execute(
                    f"UPDATE {pool_table} SET name=?, qth=? WHERE callsign=?",
                    (name, qth, callsign),
                )
            else:
                cursor.execute(
                    f"INSERT INTO {pool_table} (callsign, name, qth) VALUES (?, ?, ?)",
                    (callsign, name, qth),
                )

            self._last_added_db_id = cursor.lastrowid
            conn.commit()
            conn.close()
            conn = None

            self.input_callsign.clear()
            self.input_name.clear()
            self.input_qth.clear()
            self.input_notes.clear()
            self.current_notes = ""

            self.load_operator_pool_from_db()
            self.refresh_table()
            self._highlight_latest_operator(
                getattr(self, "_last_added_db_id", None)
            )
            self.input_callsign.setFocus()

        except Exception as e:
            if conn is not None:
                try:
                    conn.rollback()
                    conn.close()
                except Exception:
                    pass

            print("save_record güvenli hata:", type(e).__name__, str(e))
            try:
                QMessageBox.warning(
                    self,
                    "Kayıt Hatası",
                    "Operatör kaydedilirken bir hata oluştu. Program kapatılmadı.",
                )
            except Exception:
                pass

    def _highlight_latest_operator(self, db_id=None):
        """Listeyi yeni eklenen operatörün bulunduğu son kayda kaydır."""
        target_row = -1

        if db_id:
            for r in range(self.table.rowCount()):
                it = self.table.item(r, 0)
                if it and it.data(Qt.ItemDataRole.UserRole) == db_id:
                    target_row = r
                    break

        # ID eşleşmesi yoksa en son satırı hedefle.
        if target_row < 0 and self.table.rowCount() > 0:
            target_row = self.table.rowCount() - 1

        if target_row < 0:
            return

        self.table.blockSignals(True)
        try:
            item = self.table.item(target_row, 0)
            if item:
                self.table.scrollToItem(
                    item,
                    QAbstractItemView.ScrollHint.PositionAtBottom
                )

            scrollbar = self.table.verticalScrollBar()
            if scrollbar:
                scrollbar.setValue(scrollbar.maximum())
        finally:
            self.table.blockSignals(False)

    def _load_session_control_state(self):
        """Mevcut oturumun kayıt kapatma ve çekiliş durumunu yükler."""
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT registration_closed FROM net_session_control WHERE session_id=?",
                (self.net_session_id,),
            )
            row = cursor.fetchone()
            self.registration_closed = bool(row and row[0])

            # Çekiliş sonuçları artık veritabanından okunmaz; yalnızca mevcut
            # uygulama oturumunda RAM üzerinde tutulur.
        finally:
            conn.close()

    def _save_session_control_state(self):
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO net_session_control "
                "(session_id, registration_closed) VALUES (?, ?)",
                (self.net_session_id, 1 if self.registration_closed else 0),
            )
            conn.commit()
        finally:
            conn.close()

    def _update_registration_button_text(self):
        if not hasattr(self, "btn_close_net"):
            return
        key = "open_net_btn" if self.registration_closed else "close_net_btn"
        self.btn_close_net.setText(get_text(self.lang, key))

    def _sync_registration_controls(self):
        """Kayıt giriş ekranı ve EchoLink kayıtlarını birlikte aç/kapat."""
        enabled = not self.registration_closed

        for widget_name in (
            "input_callsign", "input_name", "input_qth", "input_notes", "btn_save"
        ):
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.setEnabled(enabled)

        if hasattr(self, "btn_draw"):
            # ÇEKİLİŞ YAP butonu kayıt girişlerinden bağımsızdır.
            # Kayıtlar durdurulduğunda butona basılarak çekiliş bölümüne geçilebilir.
            self.btn_draw.setEnabled(
                not getattr(self, "_pdf_export_running", False)
            )

        if hasattr(self, "btn_close_net"):
            # Kayıt kapatma kararı çekilişe bağlı değildir. Çevrim bittiğinde
            # operatör istediği anda bu butondan kayıtları durdurabilir.
            self.btn_close_net.setEnabled(True)
            self._update_registration_button_text()

    def toggle_net_registrations(self):
        """Kayıtları durdurur veya daha önce durdurulduysa yeniden açar."""
        if self.registration_closed:
            self.registration_closed = False
            self.pending_echolink_callsign = None
            self._save_session_control_state()
            self._sync_registration_controls()
            QMessageBox.information(
                self,
                "Kayıtlar Açıldı",
                "Çevrim kayıtları yeniden açıldı. EchoLink ve manuel kayıt girişinden yeni kayıt alınabilir.",
            )
            return

        reply = QMessageBox.question(
            self,
            "Kayıtları Durdur",
            "Çevrim bitti. EchoLink ve manuel kayıt girişinden yeni kayıtları durdurmak istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.registration_closed = True
        self.pending_echolink_callsign = None
        self._save_session_control_state()
        self._sync_registration_controls()
        if hasattr(self, "btn_draw"):
            self.btn_draw.setEnabled(True)

        QMessageBox.information(
            self,
            "Kayıtlar Durduruldu",
            "Çevrim kayıtları durduruldu. EchoLink ve manuel kayıt girişinden yeni kayıt alınmayacak.",
        )

    def refresh_table(self):
        self.table.blockSignals(True)
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, callsign, op_name, qth, notes, timestamp, is_winner, prize, is_echolink"
            " FROM logs WHERE user_id=? AND session_id=? ORDER BY id ASC",
            (self.current_user[0], self.net_session_id),
        )
        fetched_rows = cursor.fetchall()

        self.raw_rows = fetched_rows

        if self.is_demo_mode:
            cursor.execute("SELECT COUNT(*) FROM demo_operator_pool")
        else:
            cursor.execute("SELECT COUNT(*) FROM operator_pool")
        pool_count = cursor.fetchone()[0]
        conn.close()

        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(self.raw_rows):
            self.table.insertRow(row_idx)
            db_id = row_data[0]

            clean_call = str(row_data[1]).split(" ")[0].upper()
            item_call = QTableWidgetItem(clean_call)
            item_call.setData(Qt.ItemDataRole.UserRole, db_id)
            item_call.setFlags(item_call.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 0, item_call)

            item_name = QTableWidgetItem(
                str(row_data[2]).upper().replace("i", "İ").replace("ı", "I")
            )
            item_name.setData(Qt.ItemDataRole.UserRole, db_id)
            self.table.setItem(row_idx, 1, item_name)

            raw_qth = str(row_data[3]).upper().replace("i", "İ").replace("ı", "I")
            dist_str = calculate_distance_to_relay(raw_qth)

            item_qth = QTableWidgetItem(raw_qth)
            item_qth.setData(Qt.ItemDataRole.UserRole, db_id)
            self.table.setItem(row_idx, 2, item_qth)

            item_dist = QTableWidgetItem(dist_str if dist_str else "-")
            item_dist.setData(Qt.ItemDataRole.UserRole, db_id)
            item_dist.setFlags(item_dist.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 3, item_dist)

            item_date = QTableWidgetItem(str(row_data[5]))
            item_date.setData(Qt.ItemDataRole.UserRole, db_id)
            item_date.setFlags(item_date.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 4, item_date)

            formatted_notes = (
                str(row_data[4]).upper().replace("i", "İ").replace("ı", "I")
                if row_data[4]
                else "-"
            )
            item_notes = QTableWidgetItem(formatted_notes)
            item_notes.setData(Qt.ItemDataRole.UserRole, db_id)
            self.table.setItem(row_idx, 5, item_notes)

            prize_val = row_data[7] if row_data[7] else self.session_winner_prizes.get(db_id, "-")
            prize_item = QTableWidgetItem(
                str(prize_val).upper().replace("i", "İ").replace("ı", "I")
            )
            prize_item.setFlags(prize_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row_idx, 6, prize_item)

            if row_data[6] == 1 or db_id in self.session_winner_ids:
                prize_str = str(prize_val).upper() if prize_val and prize_val != "-" else ""
                if "1." in prize_str or prize_str.startswith("1 "):
                    row_color = QColor("#C8E6C9")
                else:
                    row_color = QColor("#FFF9C4")

                for col in range(self.table.columnCount()):
                    it = self.table.item(row_idx, col)
                    if it:
                        it.setBackground(row_color)

        participant_count = len(self.raw_rows)
        total_text = get_text(self.lang, "total_part")
        right_title_text = get_text(self.lang, "right_title")
        self.lbl_counter.setText(f"{total_text}: {participant_count}")
        self.right_title_label.setText(f"{right_title_text} ({participant_count})")

        echolink_count = sum(1 for r in self.raw_rows if len(r) > 8 and r[8] == 1)
        analog_count = participant_count - echolink_count

        if participant_count > 0:
            e_pct = round((echolink_count / participant_count) * 100, 1)
            a_pct = round((analog_count / participant_count) * 100, 1)
        else:
            e_pct = 0.0
            a_pct = 0.0

        stats_text = (
            f"🌐 EchoLink: {echolink_count} (%{e_pct})  |  "
            f"📻 Analog: {analog_count} (%{a_pct})"
        )
        self.lbl_stats_header.setText(stats_text)

        if participant_count > 0:
            try:
                conn_s = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
                cur_s = conn_s.cursor()
                cur_s.execute(
                    "INSERT OR REPLACE INTO net_session_stats (session_id, session_date,"
                    " total_count, echolink_count, analog_count, echolink_pct,"
                    " analog_pct) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        self.net_session_id,
                        datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                        participant_count,
                        echolink_count,
                        analog_count,
                        e_pct,
                        a_pct,
                    ),
                )
                conn_s.commit()
                conn_s.close()
            except:
                pass

        dir_text = (
            "Operatör Veri Tabanı"
            if self.lang == "TR"
            else ("Operator Database" if self.lang == "EN" else "Operatoren-Datenbank")
        )
        self.action_open_dir.setText(f"📂 {dir_text} ({pool_count})")
        self.table.blockSignals(False)

        self.update_relay_map()

    def open_live_raffle_screen(self):
        """Canlı ekranı %75 operatör listesi + %25 eski tip çekiliş paneli olarak açar."""
        if getattr(self, "live_raffle_screen", None) is None:
            self.live_raffle_screen = LiveRaffleScreen(self, lang=self.lang)
        else:
            self.live_raffle_screen.lang = self.lang
            self.live_raffle_screen.refresh_records()
        self.live_raffle_screen.show()
        self.live_raffle_screen.raise_()
        self.live_raffle_screen.activateWindow()

    def run_live_raffle(self):
        """Canlı ekrandan hediye çekilişini yapar ve otomatik bir yedek seçer."""
        if self.current_gift_assignment_id:
            QMessageBox.information(self, "Çekiliş", "Önce mevcut hediyenin asıl/yedek kararını tamamlayın.")
            return
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, callsign, op_name, qth FROM logs WHERE user_id=? AND session_id=? ORDER BY id ASC",
            (self.current_user[0], self.net_session_id),
        )
        all_candidates = cur.fetchall()
        # Kazananlar ve başka bir hediyenin halen yedeği olan operatörler
        # yeni çekilişte aday olamaz. Asıl kabul ederse yedeği serbest kalır.
        cur.execute(
            "SELECT backup_operator_id FROM gift_assignments WHERE status='PRIMARY_PENDING' AND backup_operator_id IS NOT NULL"
        )
        active_backup_ids = {r[0] for r in cur.fetchall()}
        candidates = [
            r for r in all_candidates
            if r[0] not in self.session_winner_ids and r[0] not in active_backup_ids
        ]

        is_demo = self.is_demo_mode
        session_filter = self.demo_session_id if is_demo else "normal"
        if is_demo:
            cur.execute(
                "SELECT id, gift_number, name FROM gifts WHERE is_assigned=0 AND name IS NOT NULL AND TRIM(name) != '' AND session_id=? ORDER BY gift_number",
                (session_filter,),
            )
        else:
            cur.execute(
                "SELECT id, gift_number, name FROM gifts WHERE is_assigned=0 AND name IS NOT NULL AND TRIM(name) != '' AND (session_id IS NULL OR session_id != 'demo_session_id_9999') ORDER BY gift_number"
            )
        gifts = [g for g in cur.fetchall() if g[0] not in self.drawn_gift_ids]
        conn.close()

        if len(candidates) < 2:
            QMessageBox.information(self, "Çekiliş", "Asıl ve yedek operatör seçilebilmesi için en az 2 uygun operatör gerekir.")
            return
        if not gifts:
            QMessageBox.warning(self, "Çekiliş", "Çekiliş için kullanılabilir hediye bulunamadı.")
            return

        gift_options = [f"{g[1]}. HEDİYE: {g[2]}" for g in gifts]
        selected, ok = QInputDialog.getItem(
            self, "Hediye Seçimi", "Çekiliş için hediyeyi seçin:", gift_options, 0, False
        )
        if not ok or not selected:
            return

        gift_index = gift_options.index(selected)
        gift_id, gift_number, gift_name = gifts[gift_index]
        winner = random.choice(candidates)
        remaining = [r for r in candidates if r[0] != winner[0]]
        backup = random.choice(remaining)

        self.open_live_raffle_screen()
        self.live_raffle_screen.start_spin(
            candidates, gift_number, gift_name, winner,
            lambda w, g: self._finish_live_raffle(w, g, gift_id, backup)
        )

    def _finish_live_raffle(self, winner, gift_name, gift_id, backup=None):
        """Asıl kazanan + yedek kaydını geçici DB tablosuna oluşturur."""
        if not winner:
            return

        if backup is None or backup[0] == winner[0]:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cur = conn.cursor()
            cur.execute(
                "SELECT id, callsign, op_name, qth FROM logs WHERE user_id=? AND session_id=? AND id<>? ORDER BY id ASC",
                (self.current_user[0], self.net_session_id, winner[0]),
            )
            backup_candidates = [r for r in cur.fetchall() if r[0] not in self.session_winner_ids]
            conn.close()
            backup = random.choice(backup_candidates) if backup_candidates else None

        self.session_winner_ids.add(winner[0])
        self.session_winner_prizes[winner[0]] = gift_name
        self.drawn_gift_ids.add(gift_id)
        self.raffle_completed = True
        self.current_gift_assignment_id = None

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO gift_assignments (session_id, gift_id, gift_name, primary_operator_id, primary_callsign, primary_name, primary_qth, backup_operator_id, backup_callsign, backup_name, backup_qth, status, assigned_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PRIMARY_PENDING', ?)",
            (
                self.net_session_id, gift_id, gift_name,
                winner[0], winner[1], winner[2], winner[3],
                backup[0] if backup else None, backup[1] if backup else None,
                backup[2] if backup else None, backup[3] if backup else None,
                datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            ),
        )
        self.current_gift_assignment_id = cur.lastrowid
        conn.commit()
        conn.close()

        self._sync_registration_controls()
        self.refresh_table()
        if getattr(self, "live_raffle_screen", None):
            self.live_raffle_screen.show_gift_assignment(winner, backup, gift_name, self.current_gift_assignment_id)
            self.live_raffle_screen.refresh_records()

    def accept_gift_assignment(self):
        assignment_id = self.current_gift_assignment_id
        if not assignment_id:
            return
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        cur.execute(
            "UPDATE gift_assignments SET status='PRIMARY_ACCEPTED', decided_at=? WHERE id=? AND status='PRIMARY_PENDING'",
            (datetime.now().strftime("%d.%m.%Y %H:%M:%S"), assignment_id),
        )
        conn.commit()
        conn.close()
        if getattr(self, "live_raffle_screen", None):
            self.live_raffle_screen.finish_gift_decision("PRIMARY_ACCEPTED")
        self.current_gift_assignment_id = None

    def decline_gift_assignment(self):
        assignment_id = self.current_gift_assignment_id
        if not assignment_id:
            return
        reply = QMessageBox.question(
            self, "Hediye Onayı",
            "Asıl kazanan hediyeden vazgeçti. Hediye yedek operatöre devredilsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        cur.execute(
            "SELECT backup_operator_id, backup_callsign, backup_name, backup_qth, gift_name, primary_operator_id FROM gift_assignments WHERE id=? AND status='PRIMARY_PENDING'",
            (assignment_id,),
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            return
        backup_id, backup_call, backup_name, backup_qth, gift_name, primary_id = row
        cur.execute(
            "UPDATE gift_assignments SET status='BACKUP_PENDING' WHERE id=?",
            (assignment_id,),
        )
        conn.commit()
        conn.close()

        if primary_id in self.session_winner_ids:
            self.session_winner_ids.remove(primary_id)
        self.session_winner_prizes.pop(primary_id, None)

        if backup_id:
            self.session_winner_ids.add(backup_id)
            self.session_winner_prizes[backup_id] = gift_name
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cur = conn.cursor()
            cur.execute(
                "UPDATE gift_assignments SET status='BACKUP_ACCEPTED', decided_at=? WHERE id=?",
                (datetime.now().strftime("%d.%m.%Y %H:%M:%S"), assignment_id),
            )
            conn.commit()
            conn.close()
            self.current_gift_assignment_id = None
            self._sync_registration_controls()
            self.refresh_table()
            if getattr(self, "live_raffle_screen", None):
                backup = (backup_id, backup_call, backup_name, backup_qth)
                self.live_raffle_screen.show_backup_winner(backup, gift_name)
                self.live_raffle_screen.refresh_records()
        else:
            QMessageBox.warning(self, "Yedek Operatör", "Bu hediye için yedek operatör bulunamadı.")

    def manage_gift_assignments(self):
        """Bu oturumdaki geçici hediye atamalarını görüntüler ve kabul edilmiş hediyeyi iptal etmeyi sağlar."""
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        cur.execute(
            "SELECT id, gift_id, gift_name, primary_operator_id, primary_callsign, primary_name, backup_operator_id, backup_callsign, backup_name, status "
            "FROM gift_assignments WHERE session_id=? ORDER BY id",
            (self.net_session_id,),
        )
        assignments = cur.fetchall()
        conn.close()

        if not assignments:
            QMessageBox.information(self, "Hediye Atamaları", "Bu oturumda kayıtlı hediye ataması bulunmuyor.")
            return

        labels = []
        status_text = {
            "PRIMARY_PENDING": "⏳ ASIL BEKLİYOR",
            "PRIMARY_ACCEPTED": "✅ ASIL KABUL ETTİ",
            "BACKUP_PENDING": "⏳ YEDEK BEKLİYOR",
            "BACKUP_ACCEPTED": "🏆 YEDEK KABUL ETTİ",
        }
        for a in assignments:
            labels.append(f"{a[2]} | ASIL: {a[4]} - {a[5]} | YEDEK: {a[7] or '-'} - {a[8] or '-'} | {status_text.get(a[9], a[9])}")

        selected, ok = QInputDialog.getItem(
            self, "Hediye Atamaları", "İşlem yapılacak hediye atamasını seçin:", labels, 0, False
        )
        if not ok or not selected:
            return
        idx = labels.index(selected)
        assignment = assignments[idx]
        assignment_id, gift_id, gift_name, primary_id, primary_call, primary_name, backup_id, backup_call, backup_name, status = assignment

        if status not in ("PRIMARY_ACCEPTED", "BACKUP_ACCEPTED"):
            QMessageBox.information(
                self, "Hediye Ataması",
                "Bu hediye henüz kesinleşmedi. Önce asıl/yedek kararının tamamlanması gerekiyor.",
            )
            return

        reply = QMessageBox.question(
            self, "Hediye İptali",
            f"{gift_name} hediyesinin {primary_call if status == 'PRIMARY_ACCEPTED' else backup_call} üzerindeki ataması iptal edilsin mi?\n\nHediye tekrar çekilişe açılacaktır.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cur = conn.cursor()
        cur.execute("DELETE FROM gift_assignments WHERE id=?", (assignment_id,))
        conn.commit()
        conn.close()

        # İptal edilen kazananı mevcut uygulama oturumunda tekrar kullanılabilir yap.
        operator_id = primary_id if status == "PRIMARY_ACCEPTED" else backup_id
        if operator_id is not None:
            self.session_winner_ids.discard(operator_id)
            self.session_winner_prizes.pop(operator_id, None)

        # İptal edilen hediye tekrar çekilişe dahil olabilir.
        self.drawn_gift_ids.discard(gift_id)

        self.refresh_table()
        if getattr(self, "live_raffle_screen", None):
            self.live_raffle_screen.refresh_records()
        QMessageBox.information(self, "Hediye İptali", "Hediye ataması iptal edildi. Hediye yeniden çekilişe açıldı.")

    def run_raffle(self):
        conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, callsign, op_name, qth FROM logs WHERE user_id=? AND session_id=? ORDER BY id ASC",
            (self.current_user[0], self.net_session_id),
        )
        candidates = [r for r in cursor.fetchall() if r[0] not in self.session_winner_ids]

        if not candidates:
            conn.close()
            return

        is_demo = self.is_demo_mode
        session_filter = self.demo_session_id if is_demo else "normal"

        if is_demo:
            cursor.execute(
                "SELECT id, gift_number, name FROM gifts WHERE is_assigned=0 AND name"
                " IS NOT NULL AND TRIM(name) != '' AND session_id=? ORDER BY"
                " gift_number",
                (session_filter,),
            )
        else:
            cursor.execute(
                "SELECT id, gift_number, name FROM gifts WHERE is_assigned=0 AND name"
                " IS NOT NULL AND TRIM(name) != '' AND (session_id IS NULL OR"
                " session_id != 'demo_session_id_9999') ORDER BY gift_number"
            )

        available_gifts = [g for g in cursor.fetchall() if g[0] not in self.drawn_gift_ids]

        if not available_gifts:
            conn.close()
            return

        gift_options = [f"{g[1]}. HEDİYE: {g[2]}" for g in available_gifts]

        title_sel = (
            "Hediye Seçimi"
            if self.lang == "TR"
            else ("Gift Selection" if self.lang == "EN" else "Geschenkauswahl")
        )
        label_sel = (
            f"Mevcut {len(available_gifts)} adet hediye için çekiliş seçin:"
            if self.lang == "TR"
            else ("Select gift:" if self.lang == "EN" else "Wählen:")
        )
        selected_gift_str, ok = QInputDialog.getItem(
            self, title_sel, label_sel, gift_options, 0, False
        )

        if ok and selected_gift_str:
            selected_index = gift_options.index(selected_gift_str)
            gift_id = available_gifts[selected_index][0]
            gift_name = available_gifts[selected_index][2]

            conn.close()

            anim_dialog = RaffleAnimationDialog(
                candidates, gift_name, self, lang=self.lang
            )
            if anim_dialog.exec() == QDialog.DialogCode.Accepted:
                winner = anim_dialog.get_winner()
                if winner:
                    # Kazanan ve hediye sonucu veritabanına KAYDEDİLMEZ.
                    self.session_winner_ids.add(winner[0])
                    self.session_winner_prizes[winner[0]] = gift_name
                    self.drawn_gift_ids.add(gift_id)
                    self.raffle_completed = True
                    self._sync_registration_controls()
                    self.refresh_table()
        else:
            conn.close()

    def export_pdf(self):
        """
        QSL kartlarını paralel olarak GitHub'a yükler ve ardından ana PDF raporunu
        oluşturur. Böylece PDF içindeki bütün "QSL İndir" bağlantıları, gerçekten
        GitHub'da mevcut olan dosyalara gider.

        QSL kartları export worker thread'inde ve paralel hazırlanır/yüklenir;
        GUI thread'i kilitlenmez. JPEG önbelleği sayesinde kart PDF'leri küçüktür
        ve 70-80 operatör için yükleme süresi azaltılmıştır.
        """
        if getattr(self, "_pdf_export_running", False):
            return

        try:
            conn = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT callsign, name FROM net_controllers WHERE session_id=?",
                (self.net_session_id,),
            )
            net_controllers = cursor.fetchall()

            cursor.execute(
                "SELECT theme_name FROM session_qsl_theme WHERE session_id=?",
                (self.net_session_id,),
            )
            theme_res = cursor.fetchone()
            active_qsl_theme = (
                theme_res[0]
                if theme_res and theme_res[0]
                else "Standart Gezen Telsizciler QSL Kartı"
            )

            cursor.execute(
                "SELECT callsign, op_name, qth, timestamp, notes, prize, is_winner FROM"
                " logs WHERE user_id=? AND session_id=? ORDER BY id ASC",
                (self.current_user[0], self.net_session_id),
            )
            fetched_rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            try:
                conn.close()
            except Exception:
                pass
            QMessageBox.critical(
                self,
                "PDF Hatası",
                f"Çevrim kayıtları okunamadı:\n{type(e).__name__}: {e}",
            )
            return

        if not fetched_rows:
            QMessageBox.warning(
                self,
                "Uyarı",
                "PDF oluşturulacak kayıt bulunamadı!"
                if self.lang == "TR" else "No records!",
            )
            return

        qsl_enabled = (
            self.qsl_enabled_checkbox.isChecked()
            if hasattr(self, "qsl_enabled_checkbox")
            else True
        )

        archive_stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.last_qsl_archive_stamp = archive_stamp if qsl_enabled else None
        filename = f"cevrim_raporu_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        self._pdf_export_running = True
        self.btn_export.setEnabled(False)
        old_button_text = self.btn_export.text()
        self.btn_export.setText(
            (
                "PDF + QSL OLUŞTURULUYOR..."
                if qsl_enabled
                else "PDF OLUŞTURULUYOR (QSL YOK)..."
            )
            if self.lang == "TR"
            else (
                "CREATING PDF + QSL..."
                if qsl_enabled
                else "CREATING PDF (NO QSL)..."
            )
        )

        if not hasattr(self, "_pdf_export_signals"):
            self._pdf_export_signals = PDFExportSignals()
            self._pdf_export_signals.finished.connect(self._on_pdf_export_finished)

        def _worker():
            try:
                # ---------------------------------------------------------
                # 1) QSL KARTLARI (kullanıcı seçimine göre)
                # ---------------------------------------------------------
                if qsl_enabled:
                    qsl_rows = list(fetched_rows)
                    qsl_archive_stamp = archive_stamp
                    qsl_theme = active_qsl_theme
                    qsl_controllers = list(net_controllers)

                    from concurrent.futures import ThreadPoolExecutor, as_completed

                    def _make_qsl(row):
                        qsl_call, qsl_name, qsl_qth, qsl_timestamp = row[:4]
                        qsl_raw = str(qsl_call).strip().upper()
                        rel_path = github_qsl_filename(qsl_raw, qsl_archive_stamp)
                        try:
                            qsl_buffer = io.BytesIO()
                            generate_single_qsl_pdf(
                                qsl_raw,
                                qsl_name,
                                qsl_qth,
                                qsl_theme if getattr(self, "show_theme_in_notes", True) else "",
                                qsl_buffer,
                                qsl_timestamp,
                                qsl_controllers,
                            )
                            pdf_bytes = qsl_buffer.getvalue()
                            if not pdf_bytes:
                                return rel_path, None, f"{qsl_raw}: QSL PDF boş."

                            if fitz is None:
                                return (
                                    rel_path,
                                    None,
                                    f"{qsl_raw}: PyMuPDF (fitz) kurulu değil."
                                )

                            pdf_doc = fitz.open(
                                stream=pdf_bytes,
                                filetype="pdf"
                            )
                            try:
                                page = pdf_doc.load_page(0)
                                pix = page.get_pixmap(
                                    matrix=fitz.Matrix(1.0, 1.0),
                                    alpha=False,
                                )
                                jpeg_bytes = pix.tobytes(
                                    "jpeg",
                                    jpg_quality=80
                                )
                            finally:
                                pdf_doc.close()

                            if not jpeg_bytes:
                                return rel_path, None, f"{qsl_raw}: QSL JPEG boş."

                            return rel_path, jpeg_bytes, None

                        except Exception as e:
                            return (
                                rel_path,
                                None,
                                f"{qsl_raw}: {type(e).__name__}: {e}",
                            )

                    qsl_items = []
                    failures = []
                    workers = min(8, max(1, len(qsl_rows)))

                    with ThreadPoolExecutor(max_workers=workers) as executor:
                        futures = [
                            executor.submit(_make_qsl, row)
                            for row in qsl_rows
                        ]
                        for future in as_completed(futures):
                            rel_path, jpeg_bytes, error = future.result()
                            if error:
                                failures.append(error)
                            else:
                                qsl_items.append((rel_path, jpeg_bytes))

                    if failures:
                        raise RuntimeError(
                            "Bazı QSL kartları oluşturulamadı:\n"
                            + "\n".join(failures[:10])
                        )

                    qsl_items.sort(key=lambda item: item[0])

                    _github_commit_qsl_batch(
                        qsl_items,
                        qsl_archive_stamp,
                    )

                    print(
                        f"QSL: {len(qsl_items)} kart GitHub'a yüklendi. "
                        f"Çevrim={qsl_archive_stamp}"
                    )
                else:
                    print(
                        "QSL KARTI OLUŞTUR seçimi kapalı: "
                        "Bu çevrim için QSL kartı oluşturulmayacak."
                    )

                # ---------------------------------------------------------
                # 2) QSL'LER GITHUB'DA HAZIRKEN ANA PDF RAPORUNU OLUŞTUR.
                #    Böylece rapordaki bütün bağlantılar hazır dosyalara gider.
                # ---------------------------------------------------------
                doc = SimpleDocTemplate(
                    filename,
                    pagesize=letter,
                    rightMargin=30,
                    leftMargin=30,
                    topMargin=30,
                    bottomMargin=30,
                )
                story = []
                text_style = ParagraphStyle(
                    "TextStyle", fontName=FONT_NAME, fontSize=10, leading=14
                )
                header_style = ParagraphStyle(
                    "HeaderStyle", fontName=FONT_NAME, fontSize=10,
                    leading=12, textColor=colors.white
                )

                ctrl_str = ""
                if net_controllers:
                    ctrl_list = [
                        f"{idx}. {c[0]} {c[1]}"
                        for idx, c in enumerate(net_controllers, 1)
                    ]
                    ctrl_prefix = (
                        "ÇEVRİMİ YAPAN OPERATÖRLER:"
                        if self.lang == "TR" else "NET CONTROLLERS:"
                    )
                    ctrl_str = f"<br/><b>{ctrl_prefix}</b> {', '.join(ctrl_list)}"

                rep_title = "ÇEVRİM RAPORU" if self.lang == "TR" else "NET REPORT"
                dt_title = "TARİH / SAAT" if self.lang == "TR" else "DATE / TIME"
                tot_title = "TOPLAM KATILIM SAYISI" if self.lang == "TR" else "TOTAL PARTICIPANTS"
                qsl_theme_title = "KÜRESEL QSL KARTI / TEMA" if self.lang == "TR" else "GLOBAL QSL CARD / THEME"

                info_text = (
                    f"<b>{rep_title}</b><br/><br/><b>{dt_title}:</b>"
                    f" {datetime.now().strftime('%d.%m.%Y %H:%M')}{ctrl_str}"
                    f"<br/><b>{qsl_theme_title}:</b>"
                    f" <font color='#0D47A1'><b>{active_qsl_theme}</b></font>"
                    f"<br/><b>{tot_title}:</b> {len(fetched_rows)}"
                )

                header_main_title = (
                    "GEZEN TELSİZCİLER TÜRKIYE ÇEVRİMİ"
                    if self.lang == "TR" else "GEZEN TELSİZCİLER TURKEY NET"
                )
                combined_text = (
                    f"<para align=left><font color='#B71C1C' size=20>"
                    f"<b>{header_main_title}</b></font><br/><br/>{info_text}</para>"
                )
                info_paragraph = Paragraph(combined_text, text_style)

                logo_file = None
                for ext in [".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"]:
                    test_path = f"logo{ext}"
                    if os.path.exists(test_path):
                        logo_file = test_path
                        break

                if logo_file:
                    logo_img = Image(logo_file, width=100, height=100)
                    header_header_data = [[logo_img, info_paragraph]]
                else:
                    header_header_data = [["[LOGO BULUNAMADI]", info_paragraph]]

                header_table = Table(header_header_data, colWidths=[120, 435])
                header_table.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (1, 0), (1, 0), 20),
                ]))
                story.append(header_table)
                story.append(Spacer(1, 20))

                # Çekiliş gerçekten bu uygulama oturumunda yapıldıysa, kazananlar
                # PDF listesinde gösterilir. Kazanan bilgisi yalnızca uygulama
                # belleğinde tutulduğu için logs tablosundaki prize alanına bağlı
                # kalınmaz. Çekiliş yapılmadıysa HEDİYE ve NOTLAR sütunları hiç
                # oluşturulmaz.
                has_draw_occurred = bool(getattr(self, "session_winner_prizes", {})) or any(
                    row[6] == 1 and row[5] for row in fetched_rows
                )

                winner_prizes_by_call = {}
                if getattr(self, "session_winner_prizes", None):
                    conn_w = None
                    try:
                        conn_w = sqlite3.connect("gezen_telsizciler_net.db", timeout=10.0)
                        cur_w = conn_w.cursor()
                        winner_ids = list(self.session_winner_prizes.keys())
                        placeholders = ",".join("?" for _ in winner_ids)
                        if placeholders:
                            cur_w.execute(
                                f"SELECT id, callsign FROM logs WHERE id IN ({placeholders})",
                                winner_ids,
                            )
                            winner_prizes_by_call = {
                                str(call).strip().upper(): self.session_winner_prizes.get(op_id, "")
                                for op_id, call in cur_w.fetchall()
                            }
                        conn_w.close()
                    except Exception:
                        try:
                            conn_w.close()
                        except Exception:
                            pass
                h_no = "NO"
                h_call = "ÇAĞRI İŞARETİ" if self.lang == "TR" else "CALLSIGN"
                h_name = "İSİM" if self.lang == "TR" else "NAME"
                h_qth = "QTH"
                h_dist = "MESAFE" if self.lang == "TR" else "DIST."
                h_notes = "NOTLAR" if self.lang == "TR" else "NOTES"
                h_gift = "HEDİYE" if self.lang == "TR" else "PRIZE"
                h_qsl_link = "QSL KARTI" if self.lang == "TR" else "QSL CARD"

                if has_draw_occurred:
                    table_header_row = [
                        Paragraph(f"<b>{h_no}</b>", header_style),
                        Paragraph(f"<b>{h_call}</b>", header_style),
                        Paragraph(f"<b>{h_name}</b>", header_style),
                        Paragraph(f"<b>{h_qth}</b>", header_style),
                        Paragraph(f"<b>{h_dist}</b>", header_style),
                        Paragraph(f"<b>{h_notes}</b>", header_style),
                        Paragraph(f"<b>{h_gift}</b>", header_style),
                    ]
                    col_widths = [25, 65, 70, 95, 50, 85, 80]
                    if qsl_enabled:
                        table_header_row.append(
                            Paragraph(f"<b>{h_qsl_link}</b>", header_style)
                        )
                        col_widths.append(80)
                else:
                    table_header_row = [
                        Paragraph(f"<b>{h_no}</b>", header_style),
                        Paragraph(f"<b>{h_call}</b>", header_style),
                        Paragraph(f"<b>{h_name}</b>", header_style),
                        Paragraph(f"<b>{h_qth}</b>", header_style),
                        Paragraph(f"<b>{h_dist}</b>", header_style),
                    ]
                    col_widths = [30, 75, 85, 160, 65]
                    if qsl_enabled:
                        table_header_row.append(
                            Paragraph(f"<b>{h_qsl_link}</b>", header_style)
                        )
                        col_widths.append(135)

                table_data = [table_header_row]
                row_backgrounds = []

                for idx, row in enumerate(fetched_rows, 1):
                    full_call = str(row[0]).strip().upper()
                    # Çekiliş bu oturumda yapıldıysa kazananın hediyesi
                    # uygulamadaki güncel çekiliş sonucundan alınır.
                    if full_call in winner_prizes_by_call:
                        prize_value = winner_prizes_by_call[full_call]
                    else:
                        prize_value = row[5]
                    prize_text = (
                        str(prize_value).upper().replace("i", "İ").replace("ı", "I")
                        if prize_value else "-"
                    )
                    is_winner = row[6] or (full_call in winner_prizes_by_call)
                    raw_qth_pdf = str(row[2]).upper().replace("i", "İ").replace("ı", "I")
                    dist_pdf = calculate_distance_to_relay(raw_qth_pdf)

                    # Presigned URL önceden hazırlanır; dosyanın kendisi arka planda yüklenir.
                    qsl_cell_content = None
                    if qsl_enabled:
                        qsl_url = get_qsl_public_url(
                            full_call,
                            archive_stamp=archive_stamp
                        )
                        link_text = "QSL İndir" if self.lang == "TR" else "Download"
                        qsl_cell_content = (
                            f"<font color='#0D47A1'><u><a href='{qsl_url}'>"
                            f"{link_text}</a></u></font>"
                        )

                    base = [
                        Paragraph(str(idx), ParagraphStyle("CenterNo", fontName=FONT_NAME, fontSize=9, leading=11, alignment=1)),
                        Paragraph(full_call, ParagraphStyle("BoldCall", fontName=FONT_NAME, fontSize=10, leading=12, fontStyle="bold")),
                        Paragraph(str(row[1]).upper().replace("i", "İ").replace("ı", "I"), text_style),
                        Paragraph(raw_qth_pdf, text_style),
                        Paragraph(dist_pdf if dist_pdf else "-", text_style),
                    ]
                    if has_draw_occurred:
                        base.extend([
                            Paragraph(str(row[4]).upper().replace("i", "İ").replace("ı", "I") if row[4] else "-", text_style),
                            Paragraph(prize_text, text_style),
                        ])
                        if qsl_enabled:
                            base.append(Paragraph(qsl_cell_content, text_style))
                    elif qsl_enabled:
                        base.append(Paragraph(qsl_cell_content, text_style))
                    table_data.append(base)

                    if is_winner == 1 and has_draw_occurred:
                        if "1." in prize_text or prize_text.startswith("1 "):
                            row_backgrounds.append(colors.HexColor("#C8E6C9"))
                        else:
                            row_backgrounds.append(colors.HexColor("#FFF9C4"))
                    else:
                        row_backgrounds.append(
                            colors.white if idx % 2 != 0 else colors.HexColor("#F5F5F5")
                        )

                log_title = Table(table_data, colWidths=col_widths)
                table_style_commands = [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A237E")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
                for r_idx, color in enumerate(row_backgrounds, start=1):
                    table_style_commands.append(("BACKGROUND", (0, r_idx), (-1, r_idx), color))
                log_title.setStyle(TableStyle(table_style_commands))
                story.append(log_title)
                doc.build(story)

                # Ana PDF artık QSL dosyaları GitHub'da hazır olduktan sonra oluşturuldu.
                self._pdf_export_signals.finished.emit(filename, "", True)

            except Exception as e:
                self._pdf_export_signals.finished.emit(
                    filename,
                    f"{type(e).__name__}: {e}",
                    False,
                )

        threading.Thread(
            target=_worker,
            name=f"PDF-EXPORT-{archive_stamp}",
            daemon=True,
        ).start()

    def _on_pdf_export_finished(self, filename, error_text, success):
        self._pdf_export_running = False
        try:
            self.btn_export.setEnabled(True)
            self.btn_export.setText(get_text(self.lang, "pdf_btn"))
        except Exception:
            pass

        if success:
            QMessageBox.information(
                self,
                "Bilgi",
                f"PDF raporu başarıyla oluşturuldu:\n\n{filename}\n\n"
                "QSL kartları GitHub'a yüklendi.\n"
                "Ana PDF için beklemeniz gerekmez."
                if self.lang == "TR"
                else f"PDF report created successfully:\n\n{filename}\n\n"
                     "QSL cards have been uploaded to GitHub.",
            )
        else:
            QMessageBox.critical(
                self,
                "PDF Hatası",
                "PDF oluşturulamadı:\n\n" + str(error_text),
            )



def repair_users_table_for_startup():
    """
    Mevcut SQLite users tablosunun şemasını bozmaz.
    Eski/yeni sürümlerde bulunabilecek zorunlu kolonları kontrol eder.
    Özellikle username NOT NULL gibi eski şema farklarını güvenli şekilde ele alır.
    """
    db_path = "gezen_telsizciler_net.db"
    conn = sqlite3.connect(db_path, timeout=10.0)
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='users'"
        )
        if cur.fetchone() is None:
            cur.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT,
                    callsign TEXT,
                    name TEXT,
                    qth TEXT
                )
            """)
            conn.commit()
            return

        # Mevcut tabloya dokunmadan gerçek kolonları oku.
        cur.execute("PRAGMA table_info(users)")
        info = cur.fetchall()

        # Eski şemada username zorunluysa eksikse ekle.
        columns = {row[1].lower() for row in info}
        if "username" not in columns:
            try:
                cur.execute("ALTER TABLE users ADD COLUMN username TEXT")
            except sqlite3.OperationalError:
                pass

        conn.commit()
    finally:
        conn.close()


def ensure_startup_user():
    """
    Mevcut users tablosuna dokunmadan TA2TTL hesabını bulur veya oluşturur.
    ÖNEMLİ: Hem username hem callsign UNIQUE olabileceği için önce iki alanda
    ayrı ayrı arama yapılır. Böylece aynı kullanıcı ikinci kez INSERT edilmez.
    """
    db_path = "gezen_telsizciler_net.db"
    conn = sqlite3.connect(db_path, timeout=10.0)
    cur = conn.cursor()

    try:
        cur.execute("PRAGMA table_info(users)")
        info = cur.fetchall()

        if not info:
            raise RuntimeError("users tablosu bulunamadı veya okunamadı.")

        columns = {row[1].lower(): row for row in info}

        def has(col):
            return col.lower() in columns

        def col(col):
            return columns[col.lower()][1]

        # ---------------------------------------------------------
        # 1) ÖNCE MEVCUT HESABI ARA.
        # username UNIQUE ise username üzerinden,
        # callsign UNIQUE ise callsign üzerinden ayrı ayrı bak.
        # ---------------------------------------------------------
        existing = None

        if has("username"):
            cur.execute(
                f'SELECT * FROM users WHERE UPPER(COALESCE("{col("username")}", ""))=? LIMIT 1',
                ("TA2TTL",),
            )
            existing = cur.fetchone()

        if existing is None and has("callsign"):
            cur.execute(
                f'SELECT * FROM users WHERE UPPER(COALESCE("{col("callsign")}", ""))=? LIMIT 1',
                ("TA2TTL",),
            )
            existing = cur.fetchone()

        def value_for_column(column_name):
            c = column_name.lower()

            if c in ("username", "callsign", "user_name", "login"):
                return "TA2TTL"
            if c in ("password", "passwd", "pass"):
                return "123456"
            if c in ("name", "full_name", "operator_name", "display_name"):
                return "DENİZ ERTÜRK"
            if c in ("qth", "location", "city"):
                return "KOCAELİ"
            if c in ("role", "user_role"):
                return "admin"
            if c in ("is_admin", "admin", "active", "is_active", "enabled"):
                return 1

            return ""

        # ---------------------------------------------------------
        # 2) HESAP ZATEN VARSA:
        # username/callsign gibi UNIQUE alanları gereksiz yere
        # değiştirme. Böylece UNIQUE constraint oluşmaz.
        # ---------------------------------------------------------
        if existing is not None:
            user_id = existing[0]
            set_parts = []
            values = []

            for col_name, row in columns.items():
                if col_name == "id":
                    continue

                # UNIQUE kimlik alanlarını mevcut değer olarak bırak.
                # Özellikle username=TA2TTL zaten varsa tekrar yazmak gereksiz.
                if col_name in ("username", "callsign", "user_name", "login"):
                    continue

                if col_name in (
                    "password", "passwd", "pass",
                    "name", "full_name", "operator_name", "display_name",
                    "qth", "location", "city",
                    "role", "user_role",
                    "is_admin", "admin",
                    "active", "is_active", "enabled"
                ):
                    set_parts.append(f'"{row[1]}"=?')
                    values.append(value_for_column(row[1]))
                elif bool(row[3]) and row[4] is None:
                    # Yalnızca gerçekten zorunlu ve default olmayan alan.
                    set_parts.append(f'"{row[1]}"=?')
                    values.append(value_for_column(row[1]))

            if set_parts:
                values.append(user_id)
                cur.execute(
                    f'UPDATE users SET {", ".join(set_parts)} WHERE id=?',
                    values,
                )

        else:
            # -----------------------------------------------------
            # 3) HESAP YOKSA:
            # Sadece mevcut ve gerekli kolonları kullanarak INSERT et.
            # username ve callsign aynı anda varsa ikisine de TA2TTL
            # vermek yerine UNIQUE çakışma ihtimalini önlemek için
            # username kimlik olarak kullanılır; callsign boş bırakılır
            # (NOT NULL ise güvenli varsayılan uygulanır).
            # -----------------------------------------------------
            insert_cols = []
            insert_values = []

            for col_name, row in columns.items():
                if col_name == "id":
                    continue

                not_null = bool(row[3])
                default_value = row[4]

                if col_name == "username":
                    insert_cols.append(f'"{row[1]}"')
                    insert_values.append("TA2TTL")
                elif col_name == "callsign":
                    # username ve callsign UNIQUE ise ikisini de aynı
                    # değere zorlamak yerine callsign'i boş bırak.
                    # Kolon NOT NULL ise boş string geçerli bir değerdir.
                    insert_cols.append(f'"{row[1]}"')
                    insert_values.append("")
                elif col_name in (
                    "password", "passwd", "pass",
                    "name", "full_name", "operator_name", "display_name",
                    "qth", "location", "city",
                    "role", "user_role",
                    "is_admin", "admin",
                    "active", "is_active", "enabled"
                ):
                    insert_cols.append(f'"{row[1]}"')
                    insert_values.append(value_for_column(row[1]))
                elif not_null and default_value is None:
                    insert_cols.append(f'"{row[1]}"')
                    insert_values.append(value_for_column(row[1]))

            if not insert_cols:
                raise RuntimeError("users tablosuna eklenecek uygun kolon bulunamadı.")

            placeholders = ", ".join(["?"] * len(insert_cols))
            cur.execute(
                f'INSERT INTO users ({", ".join(insert_cols)}) '
                f'VALUES ({placeholders})',
                insert_values,
            )
            user_id = cur.lastrowid

        conn.commit()

        # ---------------------------------------------------------
        # 4) NetLogWindow için (id, callsign, name, qth) üret.
        # ---------------------------------------------------------
        cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row_data = cur.fetchone()

        def fetch_value(wanted, fallback=""):
            wanted = wanted.lower()
            if wanted in columns:
                value = row_data[columns[wanted][0]]
                return value if value is not None else fallback
            return fallback

        callsign = fetch_value("callsign", "")
        if not str(callsign).strip():
            callsign = fetch_value("username", "TA2TTL")

        name = fetch_value("name", "")
        if not str(name).strip():
            name = fetch_value("full_name", "DENİZ ERTÜRK")

        qth = fetch_value("qth", "")
        if not str(qth).strip():
            qth = fetch_value("location", "KOCAELİ")

        return (user_id, callsign, name, qth)

    finally:
        conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        # Veritabanı altyapısını hazırla.
        db.init_db()
        repair_users_table_for_startup()

        # ÖNEMLİ:
        # db.add_user() ve db.login_user() kullanılmıyor.
        # users tablosunun gerçek şemasına göre doğrudan giriş hesabı hazırlanıyor.
        user = ensure_startup_user()

        if user:
            mainWin = NetLogWindow(user)
            mainWin.show()
            sys.exit(app.exec())
        else:
            QMessageBox.critical(
                None,
                "Giriş Hatası",
                "TA2TTL kullanıcı hesabı hazırlanamadı.",
            )

    except Exception as e:
        import traceback

        err_msg = traceback.format_exc()
        QMessageBox.critical(
            None,
            "HATA DETAYI",
            f"Program başlatılırken bir hata oluştu:\n\n{err_msg}",
        )
