import {Config} from '@remotion/cli/config';
// Practical VP9 speed for reusable alpha assets; visual source remains editable.
Config.overrideFfmpegCommand(({args})=>args.includes('libvpx-vp9')?[...args.slice(0,-1),'-cpu-used','4','-deadline','good',args[args.length-1]]:args);
