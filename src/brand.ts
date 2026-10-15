import {Brand} from './types';
export const brands = {
 niolearn: {name: 'NioLearn',bg:'#0B1320',light:'#F7F9FA',accent:'#10B39B',highlight:'#34D1C6',font:'Sora',logo:'assets/brands/niolearn/original-mark.png',tagline:'Navigate More Possibilities.',site:'niolearn.com'},
 atfro: {name: 'ATFRO',bg:'#11130E',light:'#F7F8F1',accent:'#C4E54A',highlight:'#D8F477',font:'Inter',logo:'assets/brands/atfro/original-wordmark.png',tagline:'Growth partnership in practice.',site:'Strategy. Systems. Follow-through.'},
} satisfies Record<Brand,Record<string,string>>;
export const fontCSS = `@font-face{font-family:Sora;src:url('/assets/fonts/Sora.ttf')}@font-face{font-family:Inter;src:url('/assets/fonts/Inter.ttf')}`;
