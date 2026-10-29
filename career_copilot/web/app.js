const token = document.querySelector('meta[name="career-token"]').content;
const $ = id => document.getElementById(id);
let state;
const setupPrompt = 'Set up Career Copilot for me. Read AGENTS.md and the career-copilot skill. Ask me for my own résumé, LinkedIn, target roles, locations, and preferences, then save my answers locally. Help me connect my own accounts. Write in a natural voice, like a finance student in their mid-twenties, and confirm my actual background. Prepare my profile, LinkedIn improvements, and a job-search plan. Ask once what actions I want you to handle.';
const prompts = [
  ['Get started', setupPrompt],
  ['Any replies?', 'Check my connected email for application replies, including archived mail, Spam, and Trash if supported. Read the full messages. Separate receipts, assessments, interviews, outreach, and rejections. Save source links and next steps in my tracker. Tell me what you actually checked and any access limits.'],
  ['What needs me?', 'Read my tracker and check relevant current sources. Tell me what needs me next, in priority order, with deadlines in my timezone. Separate my tasks from what you can handle and what is waiting on employers.'],
  ['Find suitable roles', 'Find current jobs that fit my saved profile and preferences. Verify location eligibility and requirements on official employer pages. Check my tracker for duplicates. Explain the fit plainly and prepare applications within the action scope I have approved.'],
  ['Improve my LinkedIn', 'Review my own LinkedIn and résumé. Draft a headline, About section, experience bullets, and skills that fit my target roles. Use my real experience and natural voice. Show me what changes you recommend and save drafts locally.'],
  ['Make the writing sound like me', 'Review my latest draft. Make it sound like a normal person in their mid-twenties, with a finance-student voice. Use simple words, short sentences, and details from my real background. Remove AI phrases, corporate filler, exaggerated experience, and fake enthusiasm. Preserve the facts.'],
  ['Set up a daily routine', 'Help me choose and set up a recurring job-search routine in Codex. Ask for my preferred time, timezone, application target, and action scope if these are missing. Use the native automation tool if available. Stay quiet when nothing meaningful changes. Tell me whether the schedule was actually created.'],
];
const fields = [
  ['name','Full name'],['email','Application email'],['linkedin','LinkedIn URL'],['github','GitHub URL, if useful'],['portfolio','Portfolio or work samples'],['location','Current city and country'],['timezone','Timezone (e.g. America/Sao_Paulo)'],['remote_preference','Remote, hybrid, or in person?'],['target_roles','Target roles',true],['target_locations','Where do you want to work?',true],['salary_preference','Salary preference (include currency and period)',true],['resume_paths','Your current résumé file paths',true],['experience_and_education','Experience and education, with dates',true],['languages','Languages and your actual level',true],['work_authorization','Work authorization and sponsorship by country',true],['availability','Start date, notice, relocation, and schedule',true],['writing_style','How should drafts sound?',true],['excluded_companies','Companies or roles to skip',true],['daily_target','Daily application target (0 = not set)'],
];
function el(tag, cls, value) { const e=document.createElement(tag);if(cls)e.className=cls;if(value!==undefined)e.textContent=value;return e; }
function notice(s) { $('notice').textContent=s; }
async function api(path, data) {
  const options={headers:{'X-Career-Token':token}};
  if(data!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(data);}
  const r=await fetch(path,options);const body=await r.json();if(!r.ok)throw Error(body.error || 'Could not save');return body;
}
function page(id){document.querySelectorAll('.page').forEach(e=>e.hidden=e.id!==id);document.querySelectorAll('nav button').forEach(e=>e.classList.toggle('active',e.dataset.page===id));}
document.querySelectorAll('[data-page]').forEach(e=>e.addEventListener('click',()=>page(e.dataset.page)));
async function copy(value){try{await navigator.clipboard.writeText(value);notice('Copied. Paste it into your Codex chat.');}catch{notice('Clipboard unavailable. Select the message and copy it manually.');}}
function empty(node, message){node.append(el('p','empty',message));}
function taskRow(t, editable=true){
  const row=el('div','row'+(t.done?' task-done':''));const info=el('div');info.append(el('h3','',t.title));
  const due=t.due?(t.due.length===10?t.due:new Date(t.due).toLocaleString(undefined,{timeZone:state.profile.timezone})):'';
  info.append(el('p','',`${{me:'You',assistant:'Assistant',employer:'Employer'}[t.owner]}${due?' · Due '+due+' ('+state.profile.timezone+')':''}${t.application_id?' · Application #'+t.application_id:''}`));
  if(t.notes)info.append(el('p','',t.notes));row.append(info);
  if(editable){const b=el('button','quiet',t.done?'Reopen':'Done');b.addEventListener('click',async()=>{try{await api('/api/task',{id:t.id,done:!t.done});await refresh();}catch(e){notice(e.message);}});row.append(b);}
  return row;
}
function appRow(a, editable=true){
  const row=el('div','row');const info=el('div');info.append(el('div','application-title',a.company));info.append(el('div','application-sub',`${a.role} · #${a.id}`));
  if(a.notes)info.append(el('p','',a.notes));const links=el('div','links');
  try{const url=new URL(a.url);if(url.protocol==='https:'){const link=el('a','','Open role ↗');link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';links.append(link);}}catch{}
  if(editable){const b=el('button','quiet','Edit');b.addEventListener('click',()=>{const form=$('application-form');for(const [k,v]of Object.entries(a))if(form.elements.namedItem(k))form.elements.namedItem(k).value=v;form.scrollIntoView({block:'center'});form.closest('details').open=true;});links.append(b);}
  if(a.submitted_at)info.append(el('p','',`Verified receipt: ${a.submission_evidence}`));if(a.evidence)info.append(el('p','',`Latest evidence: ${a.evidence}`));info.append(links);row.append(info,el('span','badge '+a.status,a.status));return row;
}
function renderApps(){const node=$('applications-list');node.replaceChildren();const search=$('app-search').value.toLowerCase(),filter=$('app-filter').value;const apps=state.applications.filter(a=>(a.company+' '+a.role).toLowerCase().includes(search)&&(!filter||a.status===filter));if(!apps.length)return empty(node,'No applications here yet. Ask Codex to find roles that fit you.');const card=el('div','card');apps.forEach(a=>card.append(appRow(a)));node.append(card);}
function render(){
  const p=state.profile,s=state.summary;$('date-label').textContent=`${s.today} · ${s.timezone}`;$('greeting').textContent=p.name?`Your next chapter, ${p.name.split(' ')[0]}.`:'Let’s get you started.';
  $('stats').replaceChildren();[[s.verified_today+(p.daily_target?' / '+p.daily_target:''),'Verified applications today'],[s.verified_total,'Verified applications in total'],[s.my_tasks,'Next steps that need you']].forEach(([n,label])=>{const card=el('div','stat');card.append(el('strong','',n),el('span','',label));$('stats').append(card);});
  const my=$('my-tasks');my.replaceChildren();const mine=state.tasks.filter(t=>!t.done&&t.owner==='me').slice(0,4);mine.forEach(t=>my.append(taskRow(t)));if(!mine.length)empty(my,'Nothing waiting on you in the tracker. A good moment to plan your next step.');
  const recent=$('recent-apps');recent.replaceChildren();state.applications.slice(0,4).forEach(a=>recent.append(appRow(a,false)));if(!state.applications.length)empty(recent,'Your first application will show up here.');
  $('profile-fields').replaceChildren();fields.forEach(([key,label,wide])=>{const l=el('label',wide?'wide':'',label);const input=el(wide?'textarea':'input');input.name=key;input.value=p[key];if(wide)input.rows=3;if(key==='daily_target'){input.type='number';input.min=0;input.max=100;}l.append(input);$('profile-fields').append(l);});
  const tasks=$('tasks-list');tasks.replaceChildren();for(const owner of ['me','assistant','employer']){const card=el('article','card');card.append(el('h2','',{me:'Needs you',assistant:'The assistant can handle',employer:'Waiting on employers'}[owner]));const rows=state.tasks.filter(t=>t.owner===owner);rows.forEach(t=>card.append(taskRow(t)));if(!rows.length)empty(card,'No next steps recorded.');tasks.append(card);}
  renderApps();
}
async function refresh(){try{state=await api('/api/state');render();}catch(e){notice(e.message);}}
$('setup-prompt').textContent=setupPrompt;$('copy-setup').addEventListener('click',()=>copy(setupPrompt));
for(const [title,prompt]of prompts){const card=el('article','card');card.append(el('h2','',title),el('p','',prompt));const b=el('button','quiet','Copy message →');b.addEventListener('click',()=>copy(prompt));card.append(b);$('prompt-cards').append(card);}
$('profile-form').addEventListener('submit',async e=>{e.preventDefault();try{const values=Object.fromEntries(new FormData(e.target));values.daily_target=Number(values.daily_target);const changes=Object.fromEntries(Object.entries(values).filter(([k,v])=>v!==state.profile[k]));await api('/api/profile',changes);await refresh();notice('Profile saved on this computer.');}catch(err){notice(err.message);}});
$('application-form').addEventListener('submit',async e=>{e.preventDefault();try{const data=Object.fromEntries(new FormData(e.target));if(data.id)data.id=Number(data.id);else delete data.id;await api('/api/application',data);e.target.reset();await refresh();notice('Application saved.');}catch(err){notice(err.message);}});
$('reset-app').addEventListener('click',()=>$('application-form').reset());
$('task-form').addEventListener('submit',async e=>{e.preventDefault();try{const data=Object.fromEntries(new FormData(e.target));data.application_id=data.application_id?Number(data.application_id):null;await api('/api/task',data);e.target.reset();await refresh();notice('Next step saved.');}catch(err){notice(err.message);}});
$('app-search').addEventListener('input',renderApps);$('app-filter').addEventListener('change',renderApps);$('refresh').addEventListener('click',refresh);
(async()=>{try{state=await api('/api/state');state.statuses.forEach(s=>{for(const id of ['app-status','app-filter']){const o=el('option','',s);o.value=s;$(id).append(o);}});render();}catch(e){notice(e.message);}})();
