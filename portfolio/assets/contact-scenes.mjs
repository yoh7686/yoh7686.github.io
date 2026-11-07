export const scenes = [
 {name:'01 / リンゴと皿',item:'リンゴ',target:'空の皿',hint:'リンゴを、右側の空のお皿へ。',result:'扉が開きました。扉からお入りください。',start:[16,88],drop:[68,83,20,25],entrance:[50,40,32,66],row:'0%'},
 {name:'02 / 草の下',item:'松明',target:'砂地に生えた草',hint:'松明を、砂地に生えた草へ。',result:'地下へ降りる階段が現れました。階段からお入りください。',start:[18,70],drop:[55,55,43,58],entrance:[55,55,36,65],row:'50%'},
 {name:'03 / 本棚の奥',item:'本',target:'本棚の空いている場所',hint:'机の本を、本棚の空いている場所へ。',result:'本棚の奥に通路が現れました。通路からお入りください。',start:[22,82],drop:[60,46,14,32],entrance:[80,50,26,79],row:'100%'}
];
export function inside(x,y,box){return Math.abs(x-box[0])<=box[2]/2&&Math.abs(y-box[1])<=box[3]/2;}
export function decodeDestination(config){
 const id=atob(config.formIdEncoded);
 if(!/^1FAIpQL[A-Za-z0-9_-]+$/.test(id))throw new Error('Invalid identifier');
 return ['https:','','docs.google.com','forms','d','e',id,'viewform'].join('/');
}
