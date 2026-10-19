#!/usr/bin/env python3
"""Make a temporally ordered person matte and composite artwork behind a speaker.

macOS Vision supplies the local model; no training data or external upload.
The compositor restores original foreground pixels over the graphic. This is
occlusion, not a generated/reconstructed person. Review hair and hands per shot.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path
import clinic

R = clinic.ROOT

def run(args):
    subprocess.run([str(a) for a in args], check=True)

def clean_person_mask(values):
    """Keep the single presenter's soft edge; reject floating background blobs.

    Vision can assign weak alpha to a balloon above the head. A solid connected
    person core is a more reliable seed than accepting all nonzero output.
    Three mask pixels of dilation retain soft hair edges around that core.
    """
    import numpy as np
    from scipy.ndimage import label,binary_opening,binary_dilation
    core=binary_opening(values>=128,iterations=1)
    components,count=label(core)
    if count==0:raise ValueError('No reliable presenter core in person mask')
    areas=np.bincount(components.ravel());areas[0]=0
    keep=binary_dilation(components==int(areas.argmax()),iterations=3)
    return np.where(keep,values,0).astype(np.uint8)

def prepare(video, folder):
    video = Path(video).resolve(strict=True)
    metadata=clinic.probe(video)
    stream=next(s for s in metadata['streams'] if s['codec_type']=='video')
    if (stream['width'],stream['height'],stream['avg_frame_rate'])!=(1080,1920,'30/1'):
        raise ValueError('Matte input must be a clip-local 1080x1920 / 30 fps portrait render')
    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    frames, masks = folder/'frames', folder/'masks'
    frames.mkdir(exist_ok=True); masks.mkdir(exist_ok=True)
    binary = R/'.cache/bin/person-matte'
    binary.parent.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).with_name('person_matte.swift')
    # A complete run is cached only when both input and implementation match.
    digest = hashlib.sha256(video.read_bytes()+source.read_bytes()+Path(__file__).read_bytes()).hexdigest()
    manifest = folder/'matte.json'
    if manifest.exists() and json.loads(manifest.read_text()).get('signature') == digest:
        data = json.loads(manifest.read_text())
        if Path(data['mask_video']).is_file(): return Path(data['mask_video'])
    if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
        run(['xcrun','swiftc','-O',source,'-o',binary])
    # Clear only derived sequence files owned by this tool, never source media.
    for directory in (frames, masks):
        for p in directory.glob('[0-9]*.png'): p.unlink()
    run([clinic.FF,'-v','error','-y','-i',video,'-an','-vf','fps=30,scale=540:960','-fps_mode','passthrough',frames/'%06d.png'])
    run([binary,frames,masks])
    count = len(list(frames.glob('*.png')))
    if count != len(list(masks.glob('*.png'))): raise ValueError('Incomplete matte sequence')
    from PIL import Image,ImageStat
    import numpy as np
    coverage=[]
    for path in sorted(masks.glob('*.png')):
        with Image.open(path) as image:values=np.array(image.convert('L'))
        image=Image.fromarray(clean_person_mask(values))
        image.save(path)
        coverage.append(ImageStat.Stat(image).mean[0]/255)
    if min(coverage)<.005 or max(coverage)>.995:raise ValueError('Empty or fully opaque person mask; inspect shot before compositing')
    target = folder/'person-mask.mkv'
    run([clinic.FF,'-v','error','-y','-framerate','30','-i',masks/'%06d.png','-frames:v',count,'-c:v','ffv1','-pix_fmt','gray',target])
    clinic.save(manifest, {'signature':digest,'engine':'Apple Vision VNGeneratePersonSegmentationRequest / accurate',
        'input':str(video),'mask_video':str(target),'frames':count,'fps':30,'coverage_range':[min(coverage),max(coverage)],
        'cleanup':'Single presenter connected-core cleanup; three-pixel soft-edge margin',
        'review_status':'Requires visual edge review; numeric coverage is not acceptance'})
    return target

def composite(video, mask, art, output, x, y, width):
    if Path(output).resolve() in [Path(p).resolve() for p in (video,mask,art)]:
        raise ValueError('Composite output must not overwrite an input')
    from PIL import Image
    with Image.open(art) as image:
        if 'A' not in image.getbands() or image.getchannel('A').getextrema() in ((255,255),(0,0)):
            raise ValueError('Artwork must contain visible pixels and actual transparency')
    # All files are clip-local, starting at zero. A graphic may overlap the
    # person, but the original person is restored using the mask afterwards.
    graph = (
        '[0:v]split=2[room][person];'
        '[1:v]scale=1080:1920,format=gray,gblur=sigma=0.6[mask];'
        '[person][mask]alphamerge[fg];'
        f'[2:v]scale={width}:-1,format=rgba,fade=t=in:st=0:d=0.20:alpha=1[art];'
        f'[room][art]overlay=x={x}:y={y}+18*exp(-7*t):shortest=1[layer];'
        '[layer][fg]overlay=0:0:shortest=1,format=yuv420p[out]')
    run([clinic.FF,'-v','error','-y','-i',video,'-i',mask,'-loop','1','-i',art,
         '-filter_complex',graph,'-map','[out]','-map','0:a?','-c:v','libx264','-crf','18','-preset','fast',
         '-c:a','copy','-movflags','+faststart',output])

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('video',type=Path); p.add_argument('--work',type=Path,required=True)
    p.add_argument('--art',type=Path); p.add_argument('--output',type=Path)
    p.add_argument('--x',type=int,default=600); p.add_argument('--y',type=int,default=180); p.add_argument('--width',type=int,default=400)
    a = p.parse_args()
    mask = prepare(a.video,a.work)
    if a.art:
        if not a.output: p.error('--art requires --output')
        a.output.parent.mkdir(parents=True,exist_ok=True)
        composite(a.video,mask,a.art,a.output,a.x,a.y,a.width)
    print(mask)

if __name__ == '__main__': main()
