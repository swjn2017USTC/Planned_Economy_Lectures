/* Dependency-free Node smoke test of the five browser-side interactive calculations. */
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ids=['a-stock','a-ship','a-priority','n-energy','n-raw','b-credit','b-bailout','b-goods','e-loan','e-interest','e-import','f-cap','f-ship'];
const defaults=[100,90,60,80,110,40,10,70,35,7,115,100,85];
const fields=Object.create(null);
function mk(id,val=0){return {id,value:String(val),textContent:'',className:'',style:{},children:[],listeners:{},addEventListener(type,fn){this.listeners[type]=fn},replaceChildren(...x){this.children=x},append(...x){this.children.push(...x)}}}
ids.forEach((id,i)=>fields[id]=mk(id,defaults[i]));
const doc={getElementById(id){return fields[id]||(fields[id]=mk(id))},createElement(name){return mk(name)}};
const code=fs.readFileSync(__dirname+'/../site/assets/experiments.js','utf8');
vm.runInNewContext(code,{document:doc,console,Math});
const check=(slider,out,changed)=>{assert(fields[out].textContent,`${out} initially empty`);const prior=fields[out].textContent;fields[slider].value=String(changed);assert(fields[slider].listeners.input);fields[slider].listeners.input();assert.notStrictEqual(fields[out].textContent,prior,`${out} failed to update`);};
check('a-stock','res-alloc',35);
check('n-energy','res-network',30);
check('b-goods','res-budget',20);
check('e-interest','res-external',14);
check('f-cap','res-forecast',200);
assert(fields['table-external'].innerHTML?.includes('<tr>'));
console.log('PASS: all five interactive modules initialize and respond to slider changes.');
