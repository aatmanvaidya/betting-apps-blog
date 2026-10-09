"""Hero mosaic: a grid of real ad creatives from the corpus, de-duplicated by perceptual hash."""
import os, glob, random
import cv2, numpy as np
from concurrent.futures import ThreadPoolExecutor

MEDIA = "/Volumes/Aatman/research/betting apps/india_intial_work/final_annotated_non_spam_media/media"
OUT = os.path.join(os.path.dirname(__file__), "..", "site", "assets", "img")
FOLDERS = ["Aviator", "Aviator_Game", "bc_game", "Spin_Casino", "1win", "Stake_com", "Stake_game", "20Bet", "22bet",
           "1XBet", "crypto_trading", "Betting_United__Betting_Tips", "Odds96", "96p_in", "color_trading", "91Club",
           "Fun88", "Megapari", "Live_Baccarat", "Jackpot_City_Casino", "betM_sports", "3_Lucky_Casino", "World777",
           "Binomo", "Bet365", "188bet", "Lotus365", "online_betting", "sports_betting", "IPL_win_prediction"]
T, COLS, ROWS = 72, 40, 20
random.seed(11)
cands = []
for f in FOLDERS:
    files = [os.path.join(MEDIA, f, x) for x in os.listdir(os.path.join(MEDIA, f))]
    random.shuffle(files)
    cands += files[:90]
random.shuffle(cands)

def load(p):
    try:
        if p.endswith(".mp4"):
            cap = cv2.VideoCapture(p); n = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * 0.25)); ok, im = cap.read(); cap.release()
            if not ok: return None
        else:
            im = cv2.imread(p)
            if im is None: return None
        h, w = im.shape[:2]; s = min(h, w)
        im = im[(h - s) // 2:(h - s) // 2 + s, (w - s) // 2:(w - s) // 2 + s]
        im = cv2.resize(im, (T, T), interpolation=cv2.INTER_AREA)
        g = cv2.cvtColor(cv2.resize(im, (9, 8)), cv2.COLOR_BGR2GRAY)
        hsh = (g[:, 1:] > g[:, :-1]).flatten()
        if im.std() < 18: return None  # skip near-blank frames
        return im, hsh
    except Exception:
        return None

with ThreadPoolExecutor(10) as ex:
    res = [r for r in ex.map(load, cands) if r]
tiles, hashes = [], []
for im, h in res:
    if any(np.count_nonzero(h != o) < 9 for o in hashes): continue
    tiles.append(im); hashes.append(h)
    if len(tiles) == COLS * ROWS: break
print("tiles", len(tiles))
sheet = np.zeros((ROWS * T, COLS * T, 3), np.uint8)
for i, t in enumerate(tiles):
    sheet[(i // COLS) * T:(i // COLS + 1) * T, (i % COLS) * T:(i % COLS + 1) * T] = t
cv2.imwrite(os.path.join(OUT, "mosaic.webp"), sheet, [cv2.IMWRITE_WEBP_QUALITY, 72])
cv2.imwrite(os.path.join(OUT, "mosaic_preview.jpg"), cv2.resize(sheet, (1440, 720)), [cv2.IMWRITE_JPEG_QUALITY, 70])
