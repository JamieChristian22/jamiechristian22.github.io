import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/i)?.[1];
assert.ok(script, 'Homepage needs an inline filter script');
const categories = [...html.matchAll(/<article class="project" data-category="([^"]+)"/g)].map(m => m[1]);
assert.equal(categories.length, 9);

const buttons = ['all','business','data','cloud'].map(filter => ({
  dataset:{filter}, attributes:{}, listeners:{},
  setAttribute(name,value){this.attributes[name]=value;},
  addEventListener(event,fn){this.listeners[event]=fn;}
}));
const cards = categories.map(category => ({dataset:{category},hidden:false}));
const status={textContent:''};
const document={
  querySelectorAll(selector){
    if(selector==='[data-filter]')return buttons;
    if(selector==='[data-category]')return cards;
    throw Error('Unexpected selector: '+selector);
  },
  getElementById(id){
    assert.equal(id,'filter-status');
    return status;
  }
};
runInNewContext(script,{document});
for(const [filter,n] of [['all',9],['business',3],['data',3],['cloud',3],['all',9]]){
  const b=buttons.find(item=>item.dataset.filter===filter);
  assert.equal(typeof b.listeners.click,'function');
  b.listeners.click();
  assert.equal(cards.filter(item=>!item.hidden).length,n,'Filter count for '+filter);
  assert.equal(b.attributes['aria-pressed'],'true');
  assert.equal(buttons.filter(item=>item.attributes['aria-pressed']==='true').length,1);
  assert.equal(status.textContent,'Showing '+n+' featured projects.');
}
console.log('PASS: project filters, ARIA state and live status');
