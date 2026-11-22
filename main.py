<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box}
body{margin:0;background:#111;overflow:hidden}
#score{color:white;text-align:center;font-size:32px;font-weight:bold;padding:10px;background:#000}
#road{width:100vw;height:calc(100vh - 190px);background:#333;position:relative;overflow:hidden;border-left:8px solid yellow;border-right:8px solid yellow}
#car{width:90px;height:150px;position:absolute;bottom:20px;left:calc(50% - 45px);font-size:85px;line-height:150px;text-align:center}
.enemy{width:90px;height:150px;position:absolute;font-size:85px;line-height:150px;text-align:center}
#btns{display:flex;justify-content:space-around;padding:10px;background:#000}
button{width:45vw;height:90px;font-size:50px;border-radius:20px;background:#444;color:white;border:none}
</style>
</head>
<body>
<div id="score">ОЧКИ: 0</div>
<div id="road"><div id="car">🚗</div></div>
<div id="btns">
<button onclick="move(-1)">⬅️</button>
<button onclick="move(1)">➡️</button>
</div>
<script>
let car=document.getElementById('car');
let road=document.getElementById('road');
let x=window.innerWidth/2-45, score=0, speed=6;
function move(d){ x+=d*90; if(x<5)x=5; if(x>window.innerWidth-95)x=window.innerWidth-95; car.style.left=x+'px'; }
function spawn(){
  let e=document.createElement('div');
  e.className='enemy'; e.innerHTML='🚙';
  let lanes=[5, window.innerWidth/4, window.innerWidth/2-45, window.innerWidth*0.75-90, window.innerWidth-95];
  e.style.left=lanes[Math.floor(Math.random()*5)]+'px';
  e.style.top='-160px'; road.appendChild(e);
  let y=-160;
  let iv=setInterval(()=>{
    y+=speed; e.style.top=y+'px';
    if(y>window.innerHeight){ clearInterval(iv); e.remove(); score++; document.getElementById('score').innerHTML='ОЧКИ: '+score; }
    if(y>window.innerHeight-400 && y<window.innerHeight-200 && Math.abs(parseInt(e.style.left)-x)<70){
      alert('АВАРИЯ! Очки: '+score); location.reload();
    }
  },20);
}
setInterval(spawn,800);
setInterval(()=>{ speed+=0.3 },4000);
// свайп пальцем
let sx=0;
document.addEventListener('touchstart',e=>sx=e.touches[0].clientX);
document.addEventListener('touchmove',e=>{ let dx=e.touches[0].clientX-sx; if(dx>40){move(1);sx=e.touches[0].clientX} if(dx<-40){move(-1);sx=e.touches[0].clientX} });
</script>
</body>
</html>
