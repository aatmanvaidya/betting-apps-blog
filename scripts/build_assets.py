"""Build web assets (images, video clips, mosaic) for the site from the research media."""
import json, os, glob, random, subprocess, sys
import cv2, numpy as np
import imageio_ffmpeg

ROOT = "/Volumes/Aatman/research/betting apps/india_intial_work"
MEDIA = f"{ROOT}/final_annotated_non_spam_media/media"
OUT = os.path.join(os.path.dirname(__file__), "..", "site", "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()

# Meta ads: (source relative to MEDIA, output name)
ADS_IMG = {
    "Aviator/1754175155501503.png": "aviator_97",
    "Aviator/3468526609950385.png": "aviator_89_hi",
    "Aviator/761664159539052.png": "aviator_predictor",
    "Aviator/1332416754412262.png": "aviator_flew_away",
    "Aviator/1478439166880058.png": "aviator_272",
    "bc_game/1028953478902501.png": "bc_deposit300",
    "bc_game/1029024945988476.png": "bc_hindi_5btc",
    "bc_game/1447819983335731.png": "bc_72h",
    "bc_game/575726491799134.png": "rummy_instant",
    "1win/1121035472962092.png": "daily_profit",
    "1win/1433370037861910.png": "plane_income",
    "crypto_trading/1137102918442275.png": "tradingview_lookalike",
    "crypto_trading/1399263664561280.png": "bybit_pi",
    "crypto_trading/1205485327522084.png": "ai_trading_101",
    "Binomo/1220154229359127.png": "binomo_signals",
    "Betting_United__Betting_Tips/1389567492492333.png": "tips_verified",
    "Betting_United__Betting_Tips/1128032355507188.png": "tips_slip",
    "Stake_com/1039516274970829.png": "odds_100safe",
    "Stake_com/1106529784580992.png": "all_hit",
    "color_trading/4215853348647499.png": "telegram_member_service",
    "IPL_win_prediction/3228437113976328.png": "ipl_who_will_win",
    "Lotus365/2818374148318457.png": "lotus_ipl_id",
    "91Club/1252055266700810.png": "loss_cover_hi",
    "22bet/2659168204293574.png": "ipl_1win",
}
# Videos: (source, output, start, duration, keep_audio)
ADS_VID = {
    "Aviator/1025291126323119.mp4": ("df_kohli_news", 0, 44, True),
    "Aviator/1187787469658356.mp4": ("df_ambani_news", 0, 33, True),
    "Aviator/1187933073061195.mp4": ("df_autoclicker", 0, 30, True),
    "Aviator/1217793813312651.mp4": ("df_kohli_slots", 0, 27, True),
    "Aviator/657730056955958.mp4": ("testimonial_350", 0, 26, True),
    "Aviator/1022407352621771.mp4": ("invest200", 0, 24, True),
    "Aviator/2979907038827559.mp4": ("tez888_influencer", 0, 38, True),
}

def save_img(im, path, maxside=720, q=80):
    h, w = im.shape[:2]
    s = min(1.0, maxside / max(h, w))
    if s < 1: im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, im, [cv2.IMWRITE_WEBP_QUALITY, q])
    return im.shape[1], im.shape[0]

def frame_at(path, frac=0.3):
    cap = cv2.VideoCapture(path); n = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * frac)); ok, im = cap.read(); cap.release()
    return im if ok else None

def duotone(im, dark=(16, 12, 14), light=(64, 52, 232), cells=78):
    """Red-on-black halftone used as the poster for deepfake clips (BGR colours)."""
    h0, w0 = im.shape[:2]; scale = 720 / max(h0, w0)
    im = cv2.resize(im, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_CUBIC)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    g = cv2.createCLAHE(2.0, (6, 6)).apply((g * 255).astype(np.uint8)).astype(np.float32) / 255.0
    h, w = g.shape; cell = max(6, w // cells)
    canvas = np.zeros((h, w), np.uint8)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            v = float(g[y:y + cell, x:x + cell].mean()) ** 1.9
            r = (cell * 0.56) * np.sqrt(v)
            if r > 0.8: cv2.circle(canvas, (x + cell // 2, y + cell // 2), int(round(r)), 255, -1, cv2.LINE_AA)
    a = (canvas.astype(np.float32) / 255)[..., None]
    out = np.array(dark, np.float32) * (1 - a) + np.array(light, np.float32) * a
    out = out.astype(np.uint8)
    rng = np.random.default_rng(4)
    for _ in range(5):
        y0 = int(rng.integers(0, h - 12)); hh = int(rng.integers(4, max(5, h // 28)))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], int(rng.integers(-w // 14, w // 14)), axis=1)
    return out

meta = {}
for src, name in ADS_IMG.items():
    im = cv2.imread(f"{MEDIA}/{src}")
    w, h = save_img(im, f"{OUT}/ads/{name}.webp")
    meta[name] = {"src": src, "w": w, "h": h}

for src, (name, ss, dur, audio) in ADS_VID.items():
    p = f"{MEDIA}/{src}"
    cmd = [FF, "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", p,
           "-vf", "scale='min(480,iw)':-2", "-c:v", "libx264", "-preset", "slow", "-crf", "28",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += (["-c:a", "aac", "-b:a", "64k", "-ac", "1"] if audio else ["-an"])
    cmd += [f"{OUT}/video/{name}.mp4"]
    subprocess.run(cmd, check=True)
    im = frame_at(p, 0.35)
    w, h = save_img(im, f"{OUT}/video/{name}.webp", 640)
    save_img(duotone(im), f"{OUT}/video/{name}_duo.webp", 640, 82)
    meta[name] = {"src": src, "w": w, "h": h, "video": True}

# Instagram picks
sel = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
ig = {}
for tag, paths in sel.items():
    ig[tag] = []
    for i, p in enumerate(paths):
        im = cv2.imread(p)
        name = f"{tag}_{i}"
        w, h = save_img(im, f"{OUT}/ig/{name}.webp", 560, 78)
        ig[tag].append({"f": name, "w": w, "h": h, "id": os.path.basename(p).split(".")[0]})

json.dump({"ads": meta, "ig": ig}, open(f"{OUT}/manifest.json", "w"), indent=1)
print("ok", len(meta), sum(len(v) for v in ig.values()))
