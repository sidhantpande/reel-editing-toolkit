"""Original festive typography, diya artwork and restrained edge-light animation."""
import math
import random
import subprocess


def build(cache, logo, root, seconds, light_cues, restrained=False):
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    sans = root / 'public/assets/fonts/Sora.ttf'
    serif = root / 'workspaces/my-dental-skin-clinic/assets/fonts/cormorantgaramond/CormorantGaramond[wght].ttf'

    def label(draw, text, y, size, colour, elegant=False):
        font = ImageFont.truetype(str(serif if elegant else sans), size)
        if font.get_variation_axes():
            font.set_variation_by_axes([550 if elegant else 400])
        draw.text((540, y), text, font=font, fill=colour, anchor='mt')

    def diya(draw, x, y, scale=1):
        def box(a, b, c, d):
            return (x+a*scale, y+b*scale, x+c*scale, y+d*scale)
        draw.arc(box(-88, -10, 88, 92), 0, 180, fill='#EBC783', width=max(2, round(4*scale)))
        draw.line((x-88*scale, y+36*scale, x+88*scale, y+36*scale), fill='#EBC783', width=max(2, round(3*scale)))
        draw.ellipse(box(-10, -16, 10, 13), fill='#FFE7AC')
        draw.polygon([(x, y-80*scale), (x-17*scale, y-36*scale), (x-9*scale, y-17*scale), (x+6*scale, y-15*scale), (x+18*scale, y-33*scale)], fill='#F4CD7D')

    title = Image.new('RGBA', (1080, 1920))
    draw = ImageDraw.Draw(title)
    for y in range(1160, 1920):
        draw.line((0, y, 1080, y), fill=(18, 15, 18, round(184*((y-1160)/760)**.8)))
    if restrained:
        label(draw, 'Diwali', 1500, 130, '#FFF1CF', True)
        label(draw, 'Colours of joy', 1650, 34, '#FFFFFF')
    else:
        label(draw, 'F E S T I V A L   O F   L I G H T S', 1395, 25, '#FFEBC0')
        label(draw, 'Diwali', 1455, 150, '#FFF1CF', True)
        draw.line((380, 1640, 700, 1640), fill='#E8BE72', width=2)
        label(draw, 'Little hands. Endless light.', 1682, 34, '#FFFFFF')
    title.save(cache / 'title.png')

    end = Image.new('RGB', (1080, 1920), '#102532')
    glow = Image.new('RGBA', end.size)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-300, -300, 650, 650), fill=(195, 123, 35, 64))
    gd.ellipse((650, 1320, 1450, 2220), fill=(195, 123, 35, 58))
    end = Image.alpha_composite(end.convert('RGBA'), glow.filter(ImageFilter.GaussianBlur(140)))
    draw = ImageDraw.Draw(end)
    draw.rounded_rectangle((64, 235, 1016, 1685), radius=470, outline=(230, 191, 117, 115), width=2)
    crest = Image.open(logo).convert('RGBA')
    crest.thumbnail((360, 305))
    end.alpha_composite(crest, ((1080-crest.width)//2, 590))
    diya(draw, 540, 1090, .8)
    label(draw, 'Happy Diwali', 1220, 100, '#FFEBC0', True)
    label(draw, 'May every little creation shine.', 1360, 31, '#F5EADB')
    end.convert('RGB').save(cache / 'ending.png')

    corner = Image.new('RGBA', (1080, 1920))
    crest = Image.open(logo).convert('RGBA')
    crest.thumbnail((176, 176))
    corner.alpha_composite(crest, (44, 64))
    corner.save(cache / 'corner.png')

    if restrained:
        return

    # Black is transparent under screen blending. Only the outer edges carry bokeh.
    ambient = cache / 'edge-lights.mp4'
    if not ambient.exists():
        rng = random.Random(1105)
        particles = [(rng.choice((rng.uniform(-12, 45), rng.uniform(495, 552))), rng.uniform(0, 960), rng.uniform(2, 9), rng.uniform(4, 10), rng.uniform(0, math.tau)) for _ in range(28)]
        command = ['ffmpeg', '-v', 'error', '-nostdin', '-n', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '540x960', '-r', '30', '-i', '-', '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p', str(ambient)]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            for f in range(round(seconds*30)):
                t = f/30
                im = Image.new('RGB', (540, 960))
                d = ImageDraw.Draw(im)
                for x, y, radius, speed, phase in particles:
                    yy = (y-t*speed)%1020-30
                    xx = x+8*math.sin(t*.35+phase)
                    lum = .45+.35*math.sin(t*.8+phase)**2
                    d.ellipse((xx-radius, yy-radius, xx+radius, yy+radius), fill=(int(240*lum), int(161*lum), int(65*lum)))
                im = im.filter(ImageFilter.GaussianBlur(3))
                # Warm light sweeps at selected chapter boundaries; no white flashes.
                pulse = max([max(0, 1-abs(t-cue)/.45) for cue in light_cues] or [0])
                if pulse:
                    light = Image.new('RGB', im.size)
                    ld = ImageDraw.Draw(light)
                    x = -240+520*pulse
                    ld.ellipse((x-300, -200, x+80, 1160), fill=(int(125*pulse), int(64*pulse), int(15*pulse)))
                    from PIL import ImageChops
                    im = ImageChops.screen(im, light.filter(ImageFilter.GaussianBlur(90)))
                proc.stdin.write(im.tobytes())
        finally:
            proc.stdin.close()
        if proc.wait():
            raise RuntimeError('Edge-light animation encoding failed')
