'use strict';
const $ = id => document.getElementById(id);
const training = {red:[[220,30,30],[190,40,35],[240,60,55]],blue:[[30,40,220],[40,65,190],[55,55,240]]};
const centers = Object.fromEntries(Object.entries(training).map(([k,rows])=>[k,[0,1,2].map(i=>rows.reduce((s,r)=>s+r[i],0)/rows.length)]));
function classify(rgb) {
  const ranked = Object.entries(centers).map(([k,c])=>[k,Math.hypot(...rgb.map((x,i)=>x-c[i]))]).sort((a,b)=>a[1]-b[1]);
  return ranked[0][1]<120 ? ranked[0][0] : null;
}
function wavBytes(samples,rate) {
  const b=new ArrayBuffer(44+samples.length*2), v=new DataView(b);
  const str=(p,s)=>[...s].forEach((c,i)=>v.setUint8(p+i,c.charCodeAt(0)));
  str(0,'RIFF');v.setUint32(4,b.byteLength-8,true);str(8,'WAVE');str(12,'fmt ');
  v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);
  v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);
  str(36,'data');v.setUint32(40,samples.length*2,true);
  samples.forEach((x,i)=>v.setInt16(44+i*2,Math.round(Math.max(-1,Math.min(1,x))*32767),true));return b;
}
function search(records,q) {
  const terms=q.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return records.map(r=>({r,score:terms.filter(t=>(r.label+' '+r.text).toLowerCase().includes(t)).length})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).map(x=>x.r);
}
if(typeof module!=='undefined') module.exports={classify,wavBytes,search};
if(typeof document!=='undefined') {
let current=null, held=null, count=0, records=[], writer=null, timer=null, ctx=null, stream=null, chunks=[], processor=null, source=null, url=null, result='';
const msg=s=>{$('status').textContent=s;};
function show(rgb){current=classify(rgb);$('label').textContent=current==='red'?'빨강':current==='blue'?'파랑':'미확정';$('capture').disabled=!current||!!held;}
function sample(rgb){clearInterval(timer);if($('video').srcObject){$('video').srcObject.getTracks().forEach(t=>t.stop());$('video').srcObject=null;}show(rgb);}
$('red').onclick=()=>sample([220,30,30]); $('blue').onclick=()=>sample([30,40,220]);
$('camera').onclick=async()=>{try{if($('video').srcObject)return;const v=$('video');v.srcObject=await navigator.mediaDevices.getUserMedia({video:true});await v.play();clearInterval(timer);timer=setInterval(()=>{if(!v.videoWidth)return;const c=$('canvas').getContext('2d',{willReadFrequently:true});const w=v.videoWidth,h=v.videoHeight,n=Math.min(w,h)/3;c.drawImage(v,(w-n)/2,(h-n)/2,n,n,0,0,32,32);const p=c.getImageData(0,0,32,32).data;const rgb=[0,0,0];for(let i=0;i<p.length;i+=4)for(let j=0;j<3;j++)rgb[j]+=p[i+j]/1024;show(rgb);},300);}catch(e){msg('카메라 오류: '+e.message+' / 샘플 버튼 사용');}};
$('serial').onclick=async()=>{try{if(writer)return;const port=await navigator.serial.requestPort();await port.open({baudRate:115200});writer=port.writable.getWriter();msg('ESP32 연결됨');}catch(e){msg('LED 화면만 사용: '+e.message);}};
async function light(on){$('lamp').classList.toggle('on',on);if(writer)try{await writer.write(new TextEncoder().encode(on?'1\n':'0\n'));}catch(e){msg('Serial 오류: '+e.message);}}
$('capture').onclick=()=>{if(!current||held)return;held={id:++count,label:current==='red'?'빨강':'파랑'};$('count').textContent=count;$('capture').disabled=true;$('record').disabled=false;$('save').disabled=true;$('note').value='';light(true);msg('라벨 확정. 녹음하세요.');};
$('record').onclick=async()=>{try{$('record').disabled=true;stream=await navigator.mediaDevices.getUserMedia({audio:true});ctx=new AudioContext();await ctx.resume();source=ctx.createMediaStreamSource(stream);processor=ctx.createScriptProcessor(4096,1,1);chunks=[];processor.onaudioprocess=e=>{chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));};source.connect(processor);processor.connect(ctx.destination);$('stop').disabled=false;msg('녹음 중… 10초 이내로 말하고 종료');}catch(e){$('record').disabled=false;msg('마이크 오류: '+e.message);}};
$('stop').onclick=async()=>{ $('stop').disabled=true;const rate=ctx.sampleRate;processor.disconnect();source.disconnect();stream.getTracks().forEach(t=>t.stop());await ctx.close();const samples=new Float32Array(chunks.reduce((n,c)=>n+c.length,0));let offset=0;for(const c of chunks){samples.set(c,offset);offset+=c.length;}if(!samples.length){$('record').disabled=false;msg('녹음 길이가 너무 짧습니다. 다시 시도.');return;}if(url)URL.revokeObjectURL(url);url=URL.createObjectURL(new Blob([wavBytes(samples,rate)],{type:'audio/wav'}));$('audio').src=url;$('wav').href=url;$('wav').download='record_'+held.id+'.wav';$('wav').hidden=false;$('stt').disabled=false;$('save').disabled=false;msg('WAV 생성 완료. 재생한 뒤 같은 문장을 STT로 입력하세요.');};
$('stt').onclick=()=>{const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){msg('STT 미지원: 녹음을 듣고 직접 입력하세요.');return;}if(!confirm('음성이 브라우저 음성인식 서비스로 전송될 수 있습니다. 진행할까요?'))return;const r=new SR();r.lang='ko-KR';r.onresult=e=>{$('note').value=e.results[0][0].transcript;msg('변환 결과를 검토/교정하세요.');};r.onerror=e=>msg('STT 오류: '+e.error+' / 직접 입력 가능');r.onend=()=>{$('stt').disabled=!held;$('save').disabled=!held;};$('stt').disabled=true;$('save').disabled=true;try{r.start();}catch(e){$('stt').disabled=false;$('save').disabled=false;msg(e.message);}};
$('save').onclick=()=>{const text=$('note').value.trim();if(!held||!text){msg('기록 문장을 입력하세요.');return;}records.push({...held,text,source:'record_'+held.id+'.wav',verified:true});held=null;$('list').textContent=JSON.stringify(records,null,2);$('capture').disabled=!current;$('save').disabled=true;$('stt').disabled=true;$('record').disabled=true;light(false);msg('지식 저장 완료');};
$('ask').onclick=()=>{const hits=search(records,$('question').value);result=hits.length?hits.map(r=>`[${r.source}] ${r.label}: ${r.text}`).join('\n'):'관련 지식이 없습니다.';$('answer').textContent=result;};
$('voiceQuestion').onclick = () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    msg('음성 질문 미지원: 직접 입력하세요.');
    return;
  }
  if (!confirm('음성이 브라우저 음성인식 서비스로 전송될 수 있습니다. 진행할까요?')) return;
  const recognition = new SR();
  recognition.lang = 'ko-KR';
  recognition.onresult = event => {
    $('question').value = event.results[0][0].transcript;
    $('ask').click();
  };
  recognition.onerror = event => msg('음성 질문 오류: ' + event.error);
  recognition.onend = () => { $('voiceQuestion').disabled = false; };
  $('voiceQuestion').disabled = true;
  try { recognition.start(); }
  catch (error) {
    $('voiceQuestion').disabled = false;
    msg(error.message);
  }
};
$('speak').onclick=()=>{if(!result)return;const u=new SpeechSynthesisUtterance(result);u.lang='ko-KR';speechSynthesis.speak(u);};
$('export').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([records.map(r=>JSON.stringify(r)).join('\n')+'\n'],{type:'application/jsonl'}));a.download='field_knowledge.jsonl';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
}
