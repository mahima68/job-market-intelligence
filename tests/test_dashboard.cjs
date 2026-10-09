// Behavioral checks for the actual dashboard script, without third-party packages.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root=path.join(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dashboard-demo.html'),'utf8');
const payload=html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{value:'',textContent:'',innerHTML:'',options:[],listeners:{},append(o){if(this.options.length===0)this.value=o.value;this.options.push(o)},addEventListener(e,fn){this.listeners[e]=fn}});return elements.get(id)}
element('data').textContent=payload;
element('role').options.push({value:''});element('location').options.push({value:''});
const captured=[];
const context=vm.createContext({document:{getElementById:element,createElement(tag){return {value:'',textContent:'',click(){captured.push(this.download)}}}},Blob,URL:{createObjectURL(blob){captured.push(blob);return 'blob:test'},revokeObjectURL(){}},setTimeout(){}});
vm.runInContext(script,context);
assert.equal(element('total').textContent,80);
element('role').value='Data Analyst';vm.runInContext('render()',context);
assert.equal(element('total').textContent,16);
element('search').value='no-such-company';vm.runInContext('render()',context);
assert.equal(element('total').textContent,0);assert.match(element('jobs').innerHTML,/No matching postings/);assert.doesNotMatch(element('trend').innerHTML,/NaN|Infinity/);
element('search').value='';element('role').value='';element('trendSkill').value='Python';vm.runInContext('render()',context);
assert.match(element('trendSummary').textContent,/20\.0 percentage points/);
assert.equal(vm.runInContext('csvCell("  =SUM(A1)")',context),'"\'  =SUM(A1)"');
assert.equal(vm.runInContext('csvCell("\\t=1")',context),'"\'\t=1"');
assert.equal(vm.runInContext('csvCell("a\\"b")',context),'"a""b"');
assert.equal(vm.runInContext('csvCell(null)',context),'""');
element('export').onclick();
(async()=>{const csv=await captured[0].text();assert.equal(csv.split('\r\n').length,81);assert.equal(captured[1],'demo-job-postings.csv');console.log('Dashboard behavior checks passed: filters, empty sample, trends, safe CSV and export.');})().catch(error=>{console.error(error);process.exitCode=1});
