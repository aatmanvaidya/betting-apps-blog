"""Build web assets for the site from the research media.

Reads the annotated Meta ads and Instagram scrape on the research volume and writes
images, video clips, halftone posters and a manifest (with Ad Library metadata) to site/assets/.

    uv run --no-project python scripts/build_assets.py
"""
import datetime
import glob
import json
import os
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np

ROOT = "/Volumes/Aatman/research/betting apps/india_intial_work"
MEDIA = f"{ROOT}/final_annotated_non_spam_media/media"
JSONS = f"{ROOT}/final_annotated_non_spam_media/jsons"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "site", "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()

# Meta ads used as single specimens: source (relative to MEDIA) -> output name
ADS_IMG = {
    "Aviator/1754175155501503.png": "aviator_97",
    "Aviator/3468526609950385.png": "aviator_89_hi",
    "Aviator/761664159539052.png": "aviator_predictor",
    "Aviator/1332416754412262.png": "aviator_flew_away",
    "Aviator/1478439166880058.png": "aviator_272",
    "bc_game/1028953478902501.png": "bc_deposit300",
    "bc_game/1447819983335731.png": "bc_72h",
    "bc_game/575726491799134.png": "rummy_instant",
    "1win/1121035472962092.png": "daily_profit",
    "1win/1433370037861910.png": "plane_income",
    "crypto_trading/1137102918442275.png": "tradingview_lookalike",
    "Betting_United__Betting_Tips/1389567492492333.png": "tips_verified",
    "Stake_com/1039516274970829.png": "odds_100safe",
    "Stake_com/1106529784580992.png": "all_hit",
    "color_trading/4215853348647499.png": "telegram_member_service",
    "Lotus365/2818374148318457.png": "lotus_ipl_id",
    "91Club/1252055266700810.png": "loss_cover_hi",
    "91Club/1181739233288479.png": "loss_cover_hi_2",
    "22bet/2659168204293574.png": "ipl_1win",
    "1XBet/1800751520873703.png": "promise_guaranteed",
    "crypto_trading/2053802171814966.png": "promise_withdraw",
}
# Videos: source -> (output name, start, duration)
ADS_VID = {
    "Aviator/1025291126323119.mp4": ("df_kohli_news", 0, 44),
    "Aviator/1187787469658356.mp4": ("df_ambani_news", 0, 33),
    "Aviator/1187933073061195.mp4": ("df_autoclicker", 0, 30),
    "Aviator/1217793813312651.mp4": ("df_kohli_slots", 0, 27),
    "Aviator/657730056955958.mp4": ("testimonial_350", 0, 26),
    "Aviator/1022407352621771.mp4": ("invest200", 0, 24),
    "Aviator/2979907038827559.mp4": ("tez888_influencer", 0, 38),
}
# Poster frame (fraction of the clip) that shows the subject best
POSTER_AT = {"df_kohli_news": .62, "df_ambani_news": .42, "df_autoclicker": .38, "df_kohli_slots": .3,
             "testimonial_350": .3, "invest200": .12, "tez888_influencer": .62}
HALFTONE = {"df_kohli_news", "df_ambani_news", "df_autoclicker", "df_kohli_slots"}


def save_img(im, path, maxside=720, q=80):
    h, w = im.shape[:2]
    s = min(1.0, maxside / max(h, w))
    if s < 1:
        im = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, im, [cv2.IMWRITE_WEBP_QUALITY, q])
    return im.shape[1], im.shape[0]


def frame_at(path, frac=0.3):
    cap = cv2.VideoCapture(path)
    n = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * frac))
    ok, im = cap.read()
    cap.release()
    return im if ok else None


def load(path):
    return frame_at(path, 0.3) if path.endswith(".mp4") else cv2.imread(path)


def halftone(im, paper=(216, 232, 242), ink=(38, 51, 191), cells=110):
    """Risograph-style halftone: red ink dots on paper, dot size follows darkness (BGR colours)."""
    h0, w0 = im.shape[:2]
    scale = 720 / max(h0, w0)
    im = cv2.resize(im, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_CUBIC)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    g = cv2.createCLAHE(2.0, (6, 6)).apply(g).astype(np.float32) / 255.0
    h, w = g.shape
    cell = max(6, w // cells)
    canvas = np.zeros((h, w), np.uint8)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            d = (1 - float(g[y:y + cell, x:x + cell].mean())) ** 1.1
            r = (cell * 0.62) * np.sqrt(d)
            if r > 0.7:
                cv2.circle(canvas, (x + cell // 2, y + cell // 2), int(round(r)), 255, -1, cv2.LINE_AA)
    a = (canvas.astype(np.float32) / 255)[..., None]
    out = (np.array(paper, np.float32) * (1 - a) + np.array(ink, np.float32) * a).astype(np.uint8)
    rng = np.random.default_rng(4)  # a few misregistered bands, like a cheap print run
    for _ in range(4):
        y0 = int(rng.integers(0, h - 12))
        hh = int(rng.integers(4, max(5, h // 30)))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], int(rng.integers(-w // 16, w // 16)), axis=1)
    return out


def ad_records():
    ads = {}
    for f in glob.glob(f"{JSONS}/*.json"):
        for r in json.load(open(f)):
            ads.setdefault(r["id"], r)
    return ads


def meta_for(src, ads):
    a = ads.get(os.path.basename(src).split(".")[0])
    if not a:
        return {}
    s, e = a["ad_delivery_start_time"], a.get("ad_delivery_stop_time")
    days = (datetime.date.fromisoformat(e) - datetime.date.fromisoformat(s)).days + 1 if e else None
    return {"page": a["page_name"], "start": s, "stop": e, "days": days,
            "cap": (a.get("ad_creative_link_captions") or [""])[0],
            "title": (a.get("ad_creative_link_titles") or [""])[0],
            "body": (a.get("ad_creative_bodies") or [""])[0][:300],
            "plat": a["publisher_platforms"]}


def main():
    for d in ("ads", "video", "ig", "cat"):
        os.makedirs(f"{OUT}/{d}", exist_ok=True)
    ads = ad_records()
    manifest = {"ads": {}, "cat": {}}

    for src, name in ADS_IMG.items():
        w, h = save_img(cv2.imread(f"{MEDIA}/{src}"), f"{OUT}/ads/{name}.webp")
        manifest["ads"][name] = {"w": w, "h": h, **meta_for(src, ads)}

    for src, (name, ss, dur) in ADS_VID.items():
        p = f"{MEDIA}/{src}"
        subprocess.run([FF, "-y", "-loglevel", "error", "-ss", str(ss), "-t", str(dur), "-i", p,
                        "-vf", "scale='min(480,iw)':-2", "-c:v", "libx264", "-preset", "slow", "-crf", "28",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "64k", "-ac", "1",
                        f"{OUT}/video/{name}.mp4"], check=True)
        im = frame_at(p, POSTER_AT.get(name, .35))
        w, h = save_img(im, f"{OUT}/video/{name}.webp", 720)
        if name in HALFTONE:
            save_img(halftone(im), f"{OUT}/video/{name}_duo.webp", 720, 82)
        manifest["ads"][name] = {"w": w, "h": h, "video": True, **meta_for(src, ads)}

    # Example strips for "What the ads sold"
    cats = json.load(open(os.path.join(HERE, "category_examples.json")))
    for cat, srcs in cats.items():
        manifest["cat"][cat] = []
        for i, src in enumerate(srcs):
            name = f"{cat}_{i}"
            w, h = save_img(load(f"{MEDIA}/{src}"), f"{OUT}/cat/{name}.webp", 420, 76)
            manifest["cat"][cat].append(name)
            manifest["ads"][name] = {"w": w, "h": h, "dir": "cat", **meta_for(src, ads)}

    # Instagram posts
    picks = json.load(open(os.path.join(HERE, "instagram_picks.json")))
    for tag, paths in picks["hashtags"].items():
        for i, p in enumerate(paths):
            save_img(cv2.imread(f"{ROOT}/{p}"), f"{OUT}/ig/{tag}_{i}.webp", 560, 78)
    for name, p in picks["extra"].items():
        save_img(cv2.imread(f"{ROOT}/{p}"), f"{OUT}/ig/{name}.webp", 560, 78)

    json.dump(manifest, open(f"{OUT}/manifest.json", "w"), indent=1, ensure_ascii=False)
    print("ads", len(manifest["ads"]), "categories", {k: len(v) for k, v in manifest["cat"].items()})


if __name__ == "__main__":
    main()
