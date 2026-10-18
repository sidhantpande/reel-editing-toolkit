"""Sample/frame accounting for a spoken clinic end-card without dialogue overlap."""
def validate_video_frames(stream,expected_frames):
 """Reject short picture streams even when container/audio duration looks correct."""
 if stream.get('avg_frame_rate')!='30/1' or int(stream.get('nb_frames',0))!=expected_frames:
  raise ValueError(f'Video frame count/rate differs from expected {expected_frames} frames at 30 fps')
 if abs(float(stream.get('duration',0))-expected_frames/30)>.001:
  raise ValueError('Video stream duration differs from its frame count')

def finish_timing(base_frames,outro_frames,dissolve_frames=8,gap_frames=4,fps=30):
 if any(type(v) is not int for v in (base_frames,outro_frames,dissolve_frames,gap_frames,fps)):
  raise ValueError('Timing must use integer frames')
 if fps!=30 or base_frames<=dissolve_frames or outro_frames<1 or dissolve_frames<1 or gap_frames<0:
  raise ValueError('Invalid end-card timing')
 return {'fps':fps,'base_frames':base_frames,'outro_frames':outro_frames,'dissolve_frames':dissolve_frames,'gap_frames':gap_frames,'video_outro_start_frame':base_frames-dissolve_frames,'audio_outro_start_frame':base_frames+gap_frames,'outro_hold_extra_frames':gap_frames+dissolve_frames,'total_frames':base_frames+gap_frames+outro_frames,'samples_per_frame':48000//fps}
