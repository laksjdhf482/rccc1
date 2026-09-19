import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="RPG 자동차 주차게임", layout="wide")

html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:#111;font-family:Arial,sans-serif}
.screen{display:none;min-height:100vh;padding:28px}
.screen.active{display:block}
.menu{max-width:900px;margin:auto}
.title{text-align:center;font-size:34px;font-weight:bold;margin:28px 0 38px}
.section{border:2px solid #111;border-radius:14px;padding:20px;margin:16px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
button{font:inherit;color:#111;background:#fff;border:2px solid #111;border-radius:10px;padding:12px 18px;cursor:pointer}
button:hover{background:#eee}
.choice.selected{background:#111;color:#fff}
.choice.locked{opacity:.45}
.start{width:100%;font-size:20px;margin-top:15px}
#gameScreen{padding:0;overflow:hidden}
#top{height:62px;border-bottom:2px solid #111;display:flex;align-items:center;justify-content:space-between;padding:0 18px}
#canvas{display:block;width:100vw;height:calc(100vh - 62px);background:#fff}
#result{display:none;position:fixed;inset:0;background:rgba(255,255,255,.96);align-items:center;justify-content:center;z-index:10}
.box{width:min(520px,90vw);border:3px solid #111;border-radius:16px;padding:28px;background:#fff}
.row{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #aaa}
</style>
</head>
<body>

<section id="menu" class="screen active">
<div class="menu">
<div class="title">RPG 자동차 주차게임</div>

<div class="section">
<h2>게임 모드</h2>
<div style="font-size:22px;font-weight:bold">주차</div>
<div style="margin-top:8px">전면주차 · 후진주차 · 평행주차 · 직각주차</div>
</div>

<div class="section">
<h2>자동차 선택</h2>
<div id="cars" class="grid"></div>
<div id="money" style="margin-top:14px;font-weight:bold"></div><div id="debt" style="margin-top:8px;font-weight:bold"></div>
</div>

<div class="section">
<h3>조작</h3>
<div>↑ 전진　↓ 후진　← 좌회전　→ 우회전</div>
<div style="margin-top:8px">주차 공간과 주변 차량은 주차장 배치에 맞춰 표시됩니다</div>
</div>

<button class="start" id="start">주차 시작</button>
</div>
</section>

<section id="game" class="screen">
<div id="top">
<div><b id="typeLabel">후진주차</b>　|　<b id="carLabel">모닝</b></div>
<div>보유금액: <b id="moneyGame">0원</b>　부채: <b id="debtGame">0원</b></div>
</div>
<canvas id="canvas"></canvas>
</section>

<div id="result">
<div class="box">
<h2 id="resultTitle">주차 결과</h2>
<div class="row"><span>주차 시간</span><b id="time">0.0초</b></div>
<div class="row"><span>충돌 횟수</span><b id="collision">0</b></div>
<div class="row"><span>주차 위치 오차</span><b id="posError">0</b></div>
<div class="row"><span>주차 각도 오차</span><b id="angleError">0°</b></div>
<div class="row"><span>주차 정확도</span><b id="accuracy">0%</b></div>
<div class="row"><span>획득 금액</span><b id="earn">0원</b></div>
<button style="width:100%;margin-top:18px" id="back">메인 화면</button>
</div>
</div>

<script>
const cars=[
{id:"morning",name:"모닝",price:0,w:42,h:72,reward:100},
{id:"sedan",name:"승용차",price:5000,w:46,h:78,reward:130},
{id:"suv",name:"SUV",price:15000,w:50,h:82,reward:170},
{id:"truck1",name:"1톤 트럭",price:30000,w:52,h:88,reward:210},
{id:"truck2",name:"대형 트럭",price:70000,w:58,h:105,reward:280},
{id:"bmw",name:"BMW",price:150000,w:48,h:80,reward:350},
{id:"escalade",name:"캐딜락 에스컬레이드",price:250000,w:56,h:90,reward:450},
{id:"sport",name:"스포츠카",price:400000,w:45,h:74,reward:550}
];

let money=Number(localStorage.getItem("parkingMoney")||0);
let debt=Number(localStorage.getItem("parkingDebt")||0);
let owned=JSON.parse(localStorage.getItem("parkingOwned")||'["morning"]');
let selected="morning",canvas,ctx,W,H,game=null,raf;

const parkingTypes=["전면주차","후진주차","평행주차","직각주차"];

function fmt(n){return Math.floor(n).toLocaleString("ko-KR")+"원"}
function save(){
 localStorage.setItem("parkingMoney",money);
 localStorage.setItem("parkingDebt",debt);
 localStorage.setItem("parkingOwned",JSON.stringify(owned));
}
function payDebt(){
 if(debt>0 && money>0){
   const pay=Math.min(money,debt);
   money-=pay;
   debt-=pay;
   save();
 }
}
function renderCars(){
 const box=document.getElementById("cars");box.innerHTML="";
 cars.forEach(c=>{
  const b=document.createElement("button");
  b.className="choice"+(selected===c.id?" selected":"")+(owned.includes(c.id)?"":" locked");
  b.innerHTML="<b>"+c.name+"</b><br>"+(owned.includes(c.id)?"보유":"구매 "+fmt(c.price));
  b.onclick=()=>{
   if(!owned.includes(c.id)){
    if(money<c.price)return;
    money-=c.price;owned.push(c.id);save();
   }
   selected=c.id;renderCars();
  };
  box.appendChild(b);
 });
 payDebt(); document.getElementById("money").textContent="보유금액: "+fmt(money); document.getElementById("debt").textContent="부채: "+fmt(debt);
}
renderCars();

document.getElementById("start").onclick=()=>{
 document.getElementById("menu").classList.remove("active");
 document.getElementById("game").classList.add("active");
 startGame();
};
document.getElementById("back").onclick=()=>{
 document.getElementById("result").style.display="none";
 document.getElementById("game").classList.remove("active");
 document.getElementById("menu").classList.add("active");
 renderCars();
};

window.addEventListener("keydown",e=>{
 if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key))e.preventDefault();
 if(game)game.keys[e.key]=true;
});
window.addEventListener("keyup",e=>{if(game)game.keys[e.key]=false});

function resize(){
 if(!canvas)return;
 W=canvas.width=window.innerWidth;
 H=canvas.height=window.innerHeight-62;
}
window.addEventListener("resize",resize);

function startGame(){
 canvas=document.getElementById("canvas");
 ctx=canvas.getContext("2d");
 resize();

 const c=cars.find(x=>x.id===selected);
 const type=parkingTypes[Math.floor(Math.random()*parkingTypes.length)];

 game={
  car:c,type:type,keys:{},
  x:W/2,y:H*.76,angle:0,speed:0,
  started:performance.now(),collision:0
 };

 document.getElementById("typeLabel").textContent=type;
 document.getElementById("carLabel").textContent=c.name;
 payDebt(); document.getElementById("moneyGame").textContent=fmt(money); document.getElementById("debtGame").textContent=fmt(debt);

 cancelAnimationFrame(raf);
 loop();
}

function loop(){update();draw();raf=requestAnimationFrame(loop)}

function update(){
 if(!game)return;
 let max=3.7;
 if(game.keys.ArrowUp)game.speed=Math.min(max,game.speed+.11);
 else if(game.keys.ArrowDown)game.speed=Math.max(-2,game.speed-.11);
 else game.speed*=.93;

 let steer=(game.keys.ArrowLeft?-1:0)+(game.keys.ArrowRight?1:0);
 if(Math.abs(game.speed)>.05)game.angle+=steer*.052*(game.speed/max);

 game.x+=Math.sin(game.angle)*game.speed;
 game.y-=Math.cos(game.angle)*game.speed;

 const area={l:W*.15,r:W*.85,t:H*.08,b:H*.9};
 const hw=game.car.w/2,hh=game.car.h/2;
 if(game.x<hw+area.l){game.x=hw+area.l;game.collision++}
 if(game.x>area.r-hw){game.x=area.r-hw;game.collision++}
 if(game.y<hh+area.t){game.y=hh+area.t;game.collision++}
 if(game.y>area.b-hh){game.y=area.b-hh;game.collision++}

 // 기존 차량과 접촉하면 즉시 100원 벌금
 const parkedCars=getParkedCars();
 for(const p of parkedCars){
   const dx=game.x-p.x, dy=game.y-p.y;
   const dist=Math.hypot(dx,dy);
   const limit=(Math.max(game.car.w,game.car.h)+Math.max(p.w,p.h))*0.32;
   if(dist<limit){
     game.collision++;
     game.hitPenalty=true;
     game.speed=0;
     finish("collision");
     return;
   }
 }

 // 주차 칸 안에 차량이 들어오고 거의 정지하면 자동 종료
 const slot=getSlot();
 if(slot){
   const inside=
     Math.abs(game.x-slot.x)<slot.w*.36 &&
     Math.abs(game.y-slot.y)<slot.h*.36;
   const angleDeg=Math.abs((((game.angle*180/Math.PI)+180)%180)-0);
   const aligned=Math.min(angleDeg,180-angleDeg)<15;
   if(inside && Math.abs(game.speed)<0.25 && aligned){
     finish("parked");
   }
 }
}
function getSlot(){
 const cx=W*.5;
 if(game.type==="평행주차") return {x:W*.52,y:H*.5,w:145,h:65};
 if(game.type==="전면주차") return {x:cx,y:H*.42,w:78,h:125};
 if(game.type==="직각주차") return {x:cx,y:H*.48,w:82,h:125};
 return {x:cx,y:H*.55,w:75,h:125};
}
function getParkedCars(){
 const cx=W*.5, py=H*.5;
 if(game.type==="평행주차") return [
   {x:W*.30,y:py,w:125,h:52},{x:W*.74,y:py,w:125,h:52}
 ];
 if(game.type==="전면주차") return [
   {x:cx-115,y:H*.42,w:48,h:95},{x:cx+115,y:H*.42,w:48,h:95}
 ];
 if(game.type==="직각주차") return [
   {x:cx-125,y:H*.48,w:50,h:100},{x:cx+125,y:H*.48,w:50,h:100}
 ];
 return [
   {x:cx-115,y:H*.55,w:48,h:95},{x:cx+115,y:H*.55,w:48,h:95}
 ];
}

function draw(){
 ctx.clearRect(0,0,W,H);
 ctx.fillStyle="#fff";ctx.fillRect(0,0,W,H);

 // 주차장/도로는 고정된 하나의 장면이며, 장면 자체는 주차 유형에 따라 바뀜
 if(game.type==="평행주차")drawParallel();
 else if(game.type==="전면주차")drawFront();
 else if(game.type==="직각주차")drawPerpendicular();
 else drawReverse();

 drawCar(game.x,game.y,game.angle,game.car);
 ctx.fillStyle="#111";ctx.font="14px Arial";
 ctx.fillText("↑ 전진  ↓ 후진  ← → 조향",20,H-20);
}

function line(x1,y1,x2,y2,w=3){
 ctx.strokeStyle="#111";ctx.lineWidth=w;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();
}
function parked(x,y,w,h,vertical=false){
 ctx.save();ctx.translate(x,y);
 if(vertical)ctx.rotate(Math.PI/2);
 ctx.fillStyle="#fff";ctx.strokeStyle="#111";ctx.lineWidth=3;
 ctx.fillRect(-w/2,-h/2,w,h);ctx.strokeRect(-w/2,-h/2,w,h);
 ctx.fillStyle="#ddd";ctx.fillRect(-w*.35,-h*.28,w*.7,h*.22);
 ctx.restore();
}
function slot(x,y,w,h,vertical=false){
 ctx.save();ctx.translate(x,y);
 if(vertical)ctx.rotate(Math.PI/2);
 ctx.strokeStyle="#111";ctx.lineWidth=3;ctx.strokeRect(-w/2,-h/2,w,h);
 ctx.restore();
}
function drawReverse(){
 // 후진주차: 아래쪽 주차라인, 양옆에 주차된 차량
 const cx=W*.5, py=H*.55;
 slot(cx,py,75,125,true);
 parked(cx-115,py,48,95,true);
 parked(cx+115,py,48,95,true);
 line(W*.15,H*.15,W*.85,H*.15);
 line(W*.15,H*.15,W*.15,H*.9);
 line(W*.85,H*.15,W*.85,H*.9);
}
function drawFront(){
 const cx=W*.5,py=H*.42;
 slot(cx,py,78,125,true);
 parked(cx-115,py,48,95,true);
 parked(cx+115,py,48,95,true);
 line(W*.15,H*.15,W*.85,H*.15);
 line(W*.15,H*.15,W*.15,H*.9);
 line(W*.85,H*.15,W*.85,H*.9);
}
function drawPerpendicular(){
 const y=H*.48;
 slot(W*.5,y,82,125,true);
 parked(W*.5-125,y,50,100,true);
 parked(W*.5+125,y,50,100,true);
 line(W*.15,H*.15,W*.85,H*.15);
 line(W*.15,H*.15,W*.15,H*.9);
 line(W*.85,H*.15,W*.85,H*.9);
}
function drawParallel(){
 const y=H*.5;
 slot(W*.52,y,145,65,false);
 parked(W*.30,y,125,52,false);
 parked(W*.74,y,125,52,false);
 line(W*.15,H*.2,W*.85,H*.2);
 line(W*.15,H*.82,W*.85,H*.82);
}

function drawCar(x,y,a,c){
 ctx.save();ctx.translate(x,y);ctx.rotate(a);
 ctx.fillStyle="#2878ff";
 round(-c.w/2,-c.h/2,c.w,c.h,8);ctx.fill();
 ctx.fillStyle="#bfe5ff";
 round(-c.w*.34,-c.h*.27,c.w*.68,c.h*.22,4);ctx.fill();
 round(-c.w*.34,c.h*.05,c.w*.68,c.h*.22,4);ctx.fill();
 ctx.fillStyle="#111";
 ctx.fillRect(-c.w*.53,-c.h*.34,5,15);
 ctx.fillRect(c.w*.48,-c.h*.34,5,15);
 ctx.fillRect(-c.w*.53,c.h*.18,5,15);
 ctx.fillRect(c.w*.48,c.h*.18,5,15);
 ctx.restore();
}
function round(x,y,w,h,r){
 ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);
 ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);
 ctx.arcTo(x,y,x+w,y,r);ctx.closePath();
}

function finish(reason){
 if(!game)return;
 const c=game.car;
 const seconds=(performance.now()-game.started)/1000;
 const slot=getSlot();
 const posError=Math.round(Math.hypot(game.x-slot.x,game.y-slot.y));
 const angleError=Math.round(Math.abs((game.angle*180/Math.PI)%180));
 let accuracy=Math.max(0,Math.min(100,100-posError*.25-angleError*.35-game.collision*10));

 if(reason==="collision"){
   // 충돌 벌금 100원, 돈이 없으면 부채로 기록
   if(money>=100) money-=100;
   else debt+=100-money, money=0;
   accuracy=0;
 }

 const reward=Math.max(30,Math.round(c.reward*(accuracy/100)));
 if(reason==="parked") money+=reward;
 save();

 document.getElementById("time").textContent=seconds.toFixed(1)+"초";
 document.getElementById("collision").textContent=game.collision;
 document.getElementById("posError").textContent=posError+"px";
 document.getElementById("angleError").textContent=angleError+"°";
 document.getElementById("accuracy").textContent=Math.round(accuracy)+"%";
 document.getElementById("earn").textContent=reason==="collision"?"-100원":fmt(reward);

 document.getElementById("result").style.display="flex";
 cancelAnimationFrame(raf);game=null;
}
</script>
</body>
</html>
"""

components.html(html, height=1000, scrolling=False)
