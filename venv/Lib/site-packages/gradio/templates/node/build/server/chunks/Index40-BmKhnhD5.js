import './async-D55cHugf.js';
import { a as attr, g as attr_style, d as bind_props, c as spread_props } from './index-u8mz_F03.js';
import './2-BLdXJizP.js';
import { $ } from './utils.svelte-B2py64Fz.js';
import { s } from './tinycolor-DfhFic3A.js';
import { c } from './BlockTitle-BnJIYf6a.js';
import { G } from './Block-DZmzQwnI.js';
import { W } from './index3-Df92vI-L.js';
export { default as BaseExample } from './Example13-cXK-YGz2.js';
import { e as escape_html } from './escaping-CBnpiEl5.js';
import './context-CBkBucIx.js';
import './index5-BoOEKc6P.js';
import './dev-fallback-Bc5Ork7Y.js';
import './index-Cg-Pg6j3.js';
import './clone-Yk88IHKV.js';
import './Info-DU6zbiUl.js';
import './html-CfyvkLET.js';
import './IconButton-BRnu7KaR.js';
import './Clear-D7Yjckqz.js';

function w(t,e){return s(t).toHexString()}function B(t,e){t.component(s=>{let{value:i=void 0,label:d,info:u,disabled:o,show_label:p,on_input:r=()=>{},on_release:n=()=>{},on_submit:m=()=>{},on_blur:h=()=>{},on_focus:a=()=>{}}=e;w(i),c(s,{show_label:p,info:u,children:c=>{c.push(`<!---->${escape_html(d)}`);},$$slots:{default:true}}),s.push(`<!----> <button class="dialog-button svelte-nbn1m9"${attr("disabled",o,true)}${attr_style("",{background:i})}></button> `),s.push("<!--[!-->"),s.push("<!--]-->"),bind_props(e,{value:i});});}function j(t,e){t.component(s=>{let{$$slots:i,$$events:d,...u}=e;const o=new $(u,{value:"#000000"});o.props.value;let p=o.shared.label||o.i18n("color_picker.color_picker"),r=true,n;function m(h){G(h,{visible:o.shared.visible,elem_id:o.shared.elem_id,elem_classes:o.shared.elem_classes,container:o.shared.container,scale:o.shared.scale,min_width:o.shared.min_width,children:a=>{W(a,spread_props([{autoscroll:o.shared.autoscroll,i18n:o.i18n},o.shared.loading_status,{on_clear_status:()=>o.dispatch("clear_status",o.shared.loading_status)}])),a.push("<!----> "),B(a,{label:p,info:o.props.info,show_label:o.shared.show_label,disabled:!o.shared.interactive,on_input:()=>o.dispatch("input"),on_release:()=>o.dispatch("release",o.props.value),on_submit:()=>o.dispatch("submit"),on_blur:()=>o.dispatch("blur"),on_focus:()=>o.dispatch("focus"),get value(){return o.props.value},set value(c){o.props.value=c,r=false;}}),a.push("<!---->");},$$slots:{default:true}});}do r=true,n=s.copy(),m(n);while(!r);s.subsume(n);});}

export { B as BaseColorPicker, j as default };
//# sourceMappingURL=Index40-BmKhnhD5.js.map
