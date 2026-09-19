import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="RPG 자동차 주차·도로주행", layout="wide", initial_sidebar_state="collapsed")

html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;font-family:Arial,sans-serif;color:#111}
#app{width:100vw;min-height:100vh;background:#fff}
.screen{display:none;min-height:100vh;padding:28px}
.screen.active{display:block}
h1,h2,h3{margin:0 0 18px}
button{font:inherit;color:#111;background:#fff;border:2px solid #111;border-radius:10px;padding:12px 18px;cursor:pointer}
button:hover{background:#eee}
.menu{max-width:900px;margin:0 auto}
.title{text-align:center;font-size:34px;margin:25px 0 35px}
.section{border:2px solid #111;border-radius:14px;padding:20px;margin:16px 0;background:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.choice.selected{background:#111;color:#fff}
.choice.locked{opacity:.4;cursor:not-allowed}
.start{width:100%;font-size:20px;margin-top:15px}
#gameScreen{padding:0;overflow:hidden}
#gameTop{height:62px;border-bottom:2px solid #111;background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 18px;position:relative;z-index:5}
#gameCanvas{display:block;width:100vw;height:calc(100vh - 62px);background:#fff}
#result{position:fixed;inset:0;background:rgba(255,255,255,.96);z-index:20;display:none;align-items:center;justify-content:center}
.resultBox{border:3px solid #111;border-radius:16px;background:#fff;padding:28px;width:min(520px,90vw)}
.resultRow{display:flex;justify-content:space-between;border-bottom:1px solid #aaa;padding:9px 0}
.controls{font-size:13px}
.back{position:absolute;left:15px;top:15px}
</style>
</head>
<body>
<div id="app">

<section id="menuScreen" class="screen active">
  <div class="menu">
    <div class="title">RPG 자동차 주차·도로주행</div>

    <div class="section">
      <h2>게임 모드 선택</h2>
      <div class="grid" id="modeGrid">
        <button class="choice selected" data-mode="free">자유주행</button>
        <button class="choice" data-mode="license">운전면허시험</button>
        <button class="choice" data-mode="parking">주차</button>
      </div>
    </div>

    <div class="section">
      <h2>자동차 선택</h2>
      <div class="grid" id="carGrid"></div>
      <div id="moneyText" style="margin-top:14px;font-weight:bold"></div>
    </div>

    <div class="section">
      <h3>조작</h3>
      <div>↑ 전진　↓ 후진　← 좌회전　→ 우회전　Space 시점 전환</div>
      <div style="margin-top:8px">주행 중 자동차는 화면 안에서 움직이며 도로와 배경은 고정됩니다</div>
    </div>

    <button class="start" id="startBtn">게임 시작</button>
  </div>
</section>

<section id="gameScreen" class="screen">
  <div id="gameTop">
    <div><b id="modeLabel">자유주행</b>　|　<b id="carLabel">모닝</b></div>
    <div>보유금액: <b id="moneyGame">0원</b>　 <button id="finishBtn">종료</button></div>
  </div>
  <canvas id="gameCanvas"></canvas>
</section>

<div id="result">
  <div class="resultBox">
    <h2>주행 결과</h2>
    <div class="resultRow"><span>주행 시간</span><b id="rDrive">0.0초</b></div>
    <div class="resultRow"><span>주차 시간</span><b id="rPark">-</b></div>
    <div class="resultRow"><span>충돌 횟수</span><b id="rCollision">0</b></div>
    <div class="resultRow"><span>차량 방향</span><b id="rAngle">0°</b></div>
    <div class="resultRow"><span>획득 금액</span><b id="rEarn">0원</b></div>
    <button style="width:100%;margin-top:18px" id="menuBtn">메인 화면으로</button>
  </div>
</div>
</div>

<script>
const cars = [
  {id:"morning",name:"모닝",price:0,w:42,h:72,earn:100},
  {id:"sedan",name:"승용차",price:5000,w:46,h:78,earn:130},
  {id:"suv",name:"SUV",price:15000,w:50,h:82,earn:170},
  {id:"truck1",name:"1톤 트럭",price:30000,w:52,h:88,earn:210},
  {id:"truck2",name:"대형 트럭",price:70000,w:58,h:105,earn:280},
  {id:"bmw",name:"BMW",price:150000,w:48,h:80,earn:350},
  {id:"escalade",name:"캐딜락 에스컬레이드",price:250000,w:56,h:90,earn:450},
  {id:"sport",name:"스포츠카",price:400000,w:45,h:74,earn:550}
];

let money = Number(localStorage.getItem("rpgCarMoney") || 0);
let owned = JSON.parse(localStorage.getItem("rpgCarOwned") || '["morning"]');
let selectedMode = "free";
let selectedCar = "morning";

const menuScreen=document.getElementById("menuScreen");
const gameScreen=document.getElementById("gameScreen");
const result=document.getElementById("result");
const carGrid=document.getElementById("carGrid");
const moneyText=document.getElementById("moneyText");

function fmt(n){return Math.floor(n).toLocaleString("ko-KR")+"원"}

function renderCars(){
  carGrid.innerHTML="";
  cars.forEach(c=>{
    const b=document.createElement("button");
    b.className="choice"+(selectedCar===c.id?" selected":"")+(owned.includes(c.id)?"":" locked");
    b.innerHTML=`<b>${c.name}</b><br>${owned.includes(c.id)?"보유":"구매 "+fmt(c.price)}`;
    b.onclick=()=>{
      if(!owned.includes(c.id)){
        if(money>=c.price){
          money-=c.price; owned.push(c.id);
          save();
        }else return;
      }
      selectedCar=c.id;
      renderCars();
    };
    carGrid.appendChild(b);
  });
  moneyText.textContent="보유금액: "+fmt(money);
}
function save(){
  localStorage.setItem("rpgCarMoney",money);
  localStorage.setItem("rpgCarOwned",JSON.stringify(owned));
}
document.querySelectorAll("#modeGrid .choice").forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll("#modeGrid .choice").forEach(x=>x.classList.remove("selected"));
    b.classList.add("selected");
    selectedMode=b.dataset.mode;
  };
});
renderCars();

let canvas,ctx,W,H,keys={},game=null,anim=0;

window.addEventListener("keydown",e=>{
  if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.key)) e.preventDefault();
  keys[e.key]=true;
  if(e.key===" " && game) game.camera=!game.camera;
});
window.addEventListener("keyup",e=>keys[e.key]=false);

document.getElementById("startBtn").onclick=()=>{
  menuScreen.classList.remove("active");
  gameScreen.classList.add("active");
  startGame();
};
document.getElementById("finishBtn").onclick=finishGame;
document.getElementById("menuBtn").onclick=()=>{
  result.style.display="none";
  gameScreen.classList.remove("active");
  menuScreen.classList.add("active");
  renderCars();
};

function startGame(){
  canvas=document.getElementById("gameCanvas");
  ctx=canvas.getContext("2d");
  resize();
  window.onresize=resize;
  const c=cars.find(x=>x.id===selectedCar);
  game={
    car:c,x:W/2,y:H*0.72,angle:0,speed:0,
    started:performance.now(),collision:0,camera:false
  };
  document.getElementById("modeLabel").textContent=
    selectedMode==="free"?"자유주행":selectedMode==="license"?"운전면허시험":"주차";
  document.getElementById("carLabel").textContent=c.name;
  document.getElementById("moneyGame").textContent=fmt(money);
  cancelAnimationFrame(anim);
  loop();
}
function resize(){
  if(!canvas)return;
  W=canvas.width=window.innerWidth;
  H=canvas.height=window.innerHeight-62;
}
function clamp(v,a,b){return Math.max(a,Math.min(b,v))}
function loop(){
  update();
  draw();
  anim=requestAnimationFrame(loop);
}
function update(){
  if(!game)return;
  const max=4.2;
  if(keys.ArrowUp) game.speed=clamp(game.speed+0.12, -2.0,max);
  else if(keys.ArrowDown) game.speed=clamp(game.speed-0.12,-2.0,max);
  else game.speed*=0.94;

  const steer=(keys.ArrowLeft?-1:0)+(keys.ArrowRight?1:0);
  if(Math.abs(game.speed)>0.05) game.angle += steer*0.045*(game.speed/max);

  game.x += Math.sin(game.angle)*game.speed;
  game.y -= Math.cos(game.angle)*game.speed;

  const roadL=W*0.23,roadR=W*0.77;
  const half=game.car.w/2;
  if(game.x<roadL+half){game.x=roadL+half;game.collision++}
  if(game.x>roadR-half){game.x=roadR-half;game.collision++}
  const top=H*0.08,bottom=H*0.88;
  if(game.y<top+game.car.h/2){game.y=top+game.car.h/2;game.collision++}
  if(game.y>bottom-game.car.h/2){game.y=bottom-game.car.h/2;game.collision++}
}
function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle="#fff";ctx.fillRect(0,0,W,H);

  // 고정된 도로: 흰색 바탕 + 중앙선 + 양쪽 끝 라인만 표시
  const roadL=W*0.23,roadR=W*0.77;
  const top=H*0.08,bottom=H*0.88;
  ctx.strokeStyle="#111";ctx.lineWidth=3;
  ctx.beginPath();ctx.moveTo(roadL,top);ctx.lineTo(roadL,bottom);ctx.stroke();
  ctx.beginPath();ctx.moveTo(roadR,top);ctx.lineTo(roadR,bottom);ctx.stroke();

  ctx.strokeStyle="#777";ctx.lineWidth=3;ctx.setLineDash([28,22]);
  ctx.beginPath();ctx.moveTo(W/2,top);ctx.lineTo(W/2,bottom);ctx.stroke();
  ctx.setLineDash([]);

  drawCar(game.x,game.y,game.angle,game.car);

  ctx.fillStyle="#111";ctx.font="14px Arial";
  ctx.fillText("↑ 전진  ↓ 후진  ← → 조향  |  Space 시점 전환",20,H-22);

  if(game.camera) drawFirstPerson();
}
function drawCar(x,y,a,c){
  ctx.save();ctx.translate(x,y);ctx.rotate(a);
  ctx.fillStyle="#2878ff";
  roundRect(-c.w/2,-c.h/2,c.w,c.h,8);ctx.fill();
  ctx.fillStyle="#bfe5ff";
  roundRect(-c.w*.34,-c.h*.27,c.w*.68,c.h*.22,4);ctx.fill();
  ctx.fillStyle="#bfe5ff";
  roundRect(-c.w*.34,c.h*.05,c.w*.68,c.h*.22,4);ctx.fill();
  ctx.fillStyle="#111";
  ctx.fillRect(-c.w*.53,-c.h*.34,5,15);
  ctx.fillRect(c.w*.48,-c.h*.34,5,15);
  ctx.fillRect(-c.w*.53,c.h*.18,5,15);
  ctx.fillRect(c.w*.48,c.h*.18,5,15);
  ctx.restore();
}
function roundRect(x,y,w,h,r){
  ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();
}
function drawFirstPerson(){
  ctx.fillStyle="rgba(255,255,255,.94)";
  ctx.fillRect(0,0,W,H);
  ctx.strokeStyle="#111";ctx.lineWidth=4;
  ctx.strokeRect(25,25,W-50,H-50);
  ctx.strokeStyle="#777";ctx.lineWidth=3;ctx.setLineDash([28,22]);
  ctx.beginPath();ctx.moveTo(W/2,25);ctx.lineTo(W/2,H-25);ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle="#111";ctx.font="bold 18px Arial";ctx.fillText("1인칭 시점",45,60);
  ctx.strokeRect(30,H-135,W*.23,90);
  ctx.strokeRect(W*.385,H-135,W*.23,90);
  ctx.strokeRect(W*.77,H-135,W*.2,90);
  ctx.font="13px Arial";
  ctx.fillText("왼쪽 사이드미러",45,H-100);
  ctx.fillText("룸미러",W*.47,H-100);
  ctx.fillText("오른쪽 사이드미러",W*.785,H-100);
}
function finishGame(){
  if(!game)return;
  const seconds=(performance.now()-game.started)/1000;
  const earn=game.car.earn + Math.max(0,100-game.collision*10);
  money+=earn;save();
  document.getElementById("rDrive").textContent=seconds.toFixed(1)+"초";
  document.getElementById("rPark").textContent=selectedMode==="parking"?seconds.toFixed(1)+"초":"-";
  document.getElementById("rCollision").textContent=game.collision;
  document.getElementById("rAngle").textContent=Math.round(Math.abs(game.angle*180/Math.PI)%360)+"°";
  document.getElementById("rEarn").textContent=fmt(earn);
  result.style.display="flex";
  cancelAnimationFrame(anim);
  game=null;
}
</script>
</body>
</html>
"""
components.html(html, height=1000, scrolling=False)
