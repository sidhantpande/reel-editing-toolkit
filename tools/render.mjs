import {spawnSync} from 'node:child_process';
import {existsSync,mkdirSync,readFileSync} from 'node:fs';
const [id='StyleLab',output='exports/style-lab.mp4',...extra]=process.argv.slice(2);
mkdirSync('exports',{recursive:true});
if(id==='Reel'){
 const argument=extra.find(v=>v.startsWith('--props='));
 if(argument){const p=JSON.parse(readFileSync(argument.slice(8),'utf8'));const paths=[...p.clips.map(c=>c.src),...(p.cutBlends??[]).map(c=>c.src),...(p.sfx??[]).map(c=>c.src),p.dialogueAudio,p.music,p.endHoldImage].filter(Boolean);for(const file of paths){if(!existsSync('public/'+file))throw new Error('Missing render input: public/'+file);}}
}

const chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const args=['remotion','render','src/index.ts',id,output,'--concurrency=1','--disallow-parallel-encoding','--gl=swiftshader',...(existsSync(chrome)?['--browser-executable='+chrome,'--chrome-mode=chrome-for-testing']:[]),...(extra.some(v=>v.startsWith('--disable-shared-memory-capture'))?[]:['--disable-shared-memory-capture']),...(extra.some(v=>v.startsWith('--image-format'))?[]:['--image-format=png']),...extra];
const r=spawnSync('npx',args,{stdio:'inherit'});process.exit(r.status??1);
