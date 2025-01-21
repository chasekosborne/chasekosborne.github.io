var T0=60, ans, intm=100, oper="+-";

var flag=false;
var h=4;

function bad()
{
var ele=document.getElementById("tb");
var x=[];
var ele=document.getElementById("tb");

for(r=0; r<ele.rows.length;++r) x[r]=ele.rows[r].cells.length-1;

var yy=[]; for(var k=0;k<100;++k) yy[k]=0;
for(var r=0; r<x.length; ++r) ++yy[x[r]]
for(var k=0;k<100;++k) if(yy[k]>1) return true;

var k=0;
while(yy[k]==0) ++k;
var cnt=0;
for(var kk=k;kk<k+4;++kk) cnt+=yy[kk];
if(cnt>2) return true;

var L=0;
for(var r=0;r<x.length;++r) if(L<x[r]) L=x[r];
if(L<9) return true;


var y=[];
for(var r=0; r<x.length;++r)
{
y[r]=[];
for(var z=0; z<10;++z) {y[r][z]=x[r]%2; x[r]=Math.floor(x[r]/2);}
}
var q=9, sm=0;
while(q>-1 && sm%2==0)
{
--q;
for(var r=0;r<x.length;++r) sm+=y[r][q];
}
if(q<0) return true;



return false;
}

function notyet()
{
var x=[];
var ele=document.getElementById("tb");
var fn=document.getElementById("final");
for(r=0; r<ele.rows.length;++r) x[r]=ele.rows[r].cells.length;
var LL=0;
for(var r=0; r<x.length; ++r) {if(LL<x[r]) LL=x[r];}
//alert(LL);
if(LL==1) 
{
fn.innerHTML="Congratulations, you have become the master of pigs!";
flag=false; return false; 
}
else return true;

}

function fill(R,C)
{
var ele=document.getElementById("tb");
var s="";
for(var k=0;k<C;++k) 
{
if(k>0) s+='<td><img src="../image/nim/g_dot.png" height="80px"';
else s+='<td><img src="../image/nim/g_empty.png" height="80px" ';
s+=
'onClick="if(!flag){changerow(this); if(notyet()) setTimeout(function(){ machinemove(); }, 1000);}">';
s+='</td>';
}
if(C>0) s+='<td><img src="../image/nim/g_currentDot.png" height="80px"></td>';
else s+='<td><img src="../image/nim/g_empty.png" height="80px"></td>';
ele.rows[R].innerHTML=s;
}

function machinemove()
{

var x=[];
var ele=document.getElementById("tb");
var fn=document.getElementById("final");
for(r=0; r<ele.rows.length;++r) x[r]=ele.rows[r].cells.length-1;
var y=[];
for(var r=0; r<x.length;++r)
{
y[r]=[];
for(var z=0; z<10;++z) {y[r][z]=x[r]%2; x[r]=Math.floor(x[r]/2);}
}
var q=9, sm=0;
while(q>-1 && sm%2==0)
{
--q;
for(var r=0;r<x.length;++r) sm+=y[r][q];
}
//alert(q);
var R, C;
var L=100;
for(r=0; r<ele.rows.length;++r) x[r]=ele.rows[r].cells.length;

if(q==-1)
{
var L=0, LL=0;
var y=[]; for(var k=0; k<100;++k) y[k]=0;
for(var r=0; r<x.length; ++r) y[x[r]]=1; 
y[1]=0;

var LLL=0;
for(var r=0; r<x.length; ++r) if(LLL<x[r]) {LLL=x[r];}

R=Math.floor(Math.random()*x.length);
while(x[R]==1 || 2*(x[R]-1)<LLL)
R=Math.floor(Math.random()*x.length);
LL=x[R];

L=1+Math.floor(Math.sqrt(Math.sqrt(Math.random()))*(LL-1.00000001));
while(y[L]>0)
L=1+Math.floor(Math.sqrt(Math.sqrt(Math.random()))*(LL-1.00000001));
//alert(LL+"   "+L);
//if(LL==1) 
//fn.innerHTML="You have won! <p> Come to a Math Club meeting to claim your prize!";
//else
//{
var C=L-1;
fill(R,C);
//}
}

if(q>-1)
{
var d=1, C=0;
var R=-1; for(var r=0;r<x.length;++r) if(y[r][q]==1) R=r;
for(var qq=0; qq<q; ++qq)
{
var ss=y[R][qq]%2; 
for(var r=0;r<x.length;++r) ss=(ss+y[r][qq])%2;
C+=d*ss; d*=2; 
}
for(var qq=q+1; qq<10; ++qq)
{
d*=2; C+=y[R][qq]*d; 
}
fill(R,C);

for(r=0; r<ele.rows.length;++r) x[r]=ele.rows[r].cells.length;
var L=0;
for(var r=0; r<x.length; ++r) if(x[r]>L) {L=x[r];} 
if(L==1) fn.innerHTML="You have lost!";
}

flag=false;
}

function changerow(kk)
{
if(flag) return;
var r, c, R=-1, C=-1;
var ele=document.getElementById("tb");


for(r=0; r<ele.rows.length;++r)
for(c=0; c<ele.rows[r].cells.length;++c)
{
//alert(ele.rows[r].cells[c].firstChild); 
if(ele.rows[r].cells[c].firstChild==kk) {R=r; C=c;}
}
if(R<0) return;
fill(R,C);
flag=true;
}


function strt()
{
var mm=3, rg=9;

var s="";
var ele=document.getElementById("tb");
for(var kk=0; kk<h;++kk)
{
s+="<tr></tr>";
}
ele.innerHTML=s;
for(var kk=0; kk<h;++kk)
{
x=mm+Math.floor(Math.random()*rg);
fill(kk,x);
}
var fn=document.getElementById("final");
fn.innerHTML="Select a green square or pigsty to move the piglet.<br>Bring the last pig home, become the master of pigs.";

if(bad()) strt();

}