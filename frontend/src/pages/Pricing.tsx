import React from 'react';
import '../styles/pricing.css';

interface PricingProps {
  onNavigate?: (page: string) => void;
}

export const Pricing: React.FC<PricingProps> = ({ onNavigate }) => {
  return (
    <div className="oatmeal-page oatmeal-pricing">
      
    <header className="xrb xrd xrf xtl xww" id="navbar">
<style>{`:root { --scroll-padding-top: 5.25rem }`}</style>
<nav>
<div className="xrg xrm xrv xsc xsl xsu xtu xwn">
<div className="xrm xsf xsl">
<a href="/" className="xrq xsn">
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=olive-950" alt="Oatmeal" className="xwq" width="96" height="28"/>
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=white" alt="Oatmeal" className="xvl" width="96" height="28"/>
</a>
</div>
<div className="xrm xsx xvv">
<a href="/pricing.html" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz">Pricing<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="/about.html" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz">About<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz">Docs<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz xvx">Log in<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
</div>
<div className="xrm xsf xsl xsq xsu">
<div className="xrm xsg xsl xsv">
<a href="#" className="xrq xsg xsl xsp xuo xuq xss xtf xxb xxe xuz xvt xts xtv xvw">Log in</a>
<a href="#" className="xrq xsg xsl xsp xuo xuq xsr xtf xva xtm xvs xwu xxa xxd xts xtv">Get started</a>
</div>
<button command="show-modal" commandfor="mobile-menu" aria-label="Toggle menu" className="xrq xtf xtp xwi xxb xxe xuz xvt">
<svg viewBox="0 0 24 24" fill="currentColor" className="xrt">
<path  fillRule="evenodd" d="M3.748 8.248a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75ZM3.748 15.75a.75.75 0 0 1 .75-.751h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
</svg>
</button>
</div>
</div>
<el-dialog className="xwi">
<dialog id="mobile-menu" className="xvp">
<el-dialog-panel className="xra xrc xtu xty xwn xtl xww">
<div className="xrm xsq">
<button command="close" commandfor="mobile-menu" aria-label="Toggle menu" className="xrq xtf xtp xxb xxe xuz xvt">
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
</svg>
</button>
</div>
<div className="xrk xrm xsj xsw">
<a href="/pricing.html" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz">Pricing<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="/about.html" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz">About<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz">Docs<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xvo xrq xsl xso xss xuh xuq xwo xxb xuz xvx">Log in<span className="xrq xtp xvd xvn xwi" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xrt">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
</div>
</el-dialog-panel>
</dialog>
</el-dialog>
</nav>
</header>
<main className="xre xtd">

<section className="xtz" id="hero">
<div className="xrg xrx xry xtu xwf xwk xwn xrm xsj xsl xsw">
<h1 className="xuf xuv xui xut xwc xxb xuz xsb xud">Simple Pricing.</h1>
<div className="xul xuy xwy xrm xse xsj xsu xud">
<p>Simplify your shared inbox, collaborate effortlessly, and give every customer a reply that feels personal, even if it was written by a bot.</p>
</div>
</div>
</section>

<section className="xtz" id="pricing">
<div className="xrg xrx xry xtu xwf xwk xwn">
<div className="xrn xsh xta xth xtq xwm xwx xtn">
<div className="xrm xsj xsm xso xsy xtr xvy">
<div className="xrm xsj xsw">
<h2 className="xuf xuw xxb xug xuq xus xwb xuz">No setup fees. No contracts. Cancel anytime.</h2>
<div className="xuk xuy xwy xrm xsj xsu xuw">
<p>Commitment free, because we are banking on the fact that you&#x27;ll forget that you&#x27;re even paying us.</p>
</div>
</div>
<a href="#" className="xrq xsg xsl xsp xuo xuq xsr xtf xva xtm xvs xwu xxa xxd xtt xtw">Start free trial</a>
</div>
<div className="xtg xtr xvy xtl xww">
<div className="xrm xsk xss">
<p className="xuj xwa xup xuu xxb xuz">$49</p>
<div className="xul xuy xwy">/mo</div>
</div>
<ul className="xrk xrn xsh xst xwg xwl">
<li className="xrm xst xum">
<span className="xrm xrs xsg xsl xsp xti xtm xwv">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrr xto">
<path  d="M1.5 6.5L5.5 11.5L11.5 1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</span>
<p className="xuy xwy">Unlimited mailboxes</p>
</li>
<li className="xrm xst xum">
<span className="xrm xrs xsg xsl xsp xti xtm xwv">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrr xto">
<path  d="M1.5 6.5L5.5 11.5L11.5 1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</span>
<p className="xuy xwy">Unlimited team members</p>
</li>
<li className="xrm xst xum">
<span className="xrm xrs xsg xsl xsp xti xtm xwv">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrr xto">
<path  d="M1.5 6.5L5.5 11.5L11.5 1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</span>
<p className="xuy xwy">Inbox Agent</p>
</li>
<li className="xrm xst xum">
<span className="xrm xrs xsg xsl xsp xti xtm xwv">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrr xto">
<path  d="M1.5 6.5L5.5 11.5L11.5 1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</span>
<p className="xuy xwy">Collision detection</p>
</li>
<li className="xrm xst xum">
<span className="xrm xrs xsg xsl xsp xti xtm xwv">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrr xto">
<path  d="M1.5 6.5L5.5 11.5L11.5 1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</span>
<p className="xuy xwy">Snippets and templates</p>
</li>
<li className="xrm xst xum">
<span className="xrm xrs xsg xsl xsp xti xtm xwv">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrr xto">
<path  d="M1.5 6.5L5.5 11.5L11.5 1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</span>
<p className="xuy xwy">Reporting dashboard</p>
</li>
<li className="xrm xst xum">
<span className="xrm xrs xsg xsl xsp xti xtm xwv">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrr xto">
<path  d="M1.5 6.5L5.5 11.5L11.5 1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</span>
<p className="xuy xwy">Slack integration</p>
</li>
</ul>
</div>
</div>
</div>
</section>

<section className="xtz" id="testimonial">
<div className="xrg xrx xry xtu xwf xwk xwn">
<figure className="xxb xuz">
<blockquote className="xrg xrm xsd xsj xsu xud xuf xuw xvq xvr xuh xuq xuu xvz">
<p>Oatmeal has completely transformed our customer support operations. The blend of AI efficiency and human empathy has allowed us to provide exceptional service while significantly reducing costs.</p>
</blockquote>
<figcaption className="xrl xrm xsj xsl">
<div className="xrm xru xte xtf xve xvf xvg xvi xvj xxc">
<img src="https://assets.tailwindplus.com/avatars/10.webp?size=160" alt="" className="xvm xwt" width="160" height="160"/>
</div>
<p className="xrj xud xun xur">Jordan Rogers</p>
<p className="xud xun xuy xwy">Founder at Anomaly</p>
</figcaption>
</figure>
</div>
</section>

<section className="xtz" id="faqs">
<div className="xrg xrm xrz xsj xsw xtu xwj xwn">
<div className="xrm xsj xsw">
<h2 className="xuf xuw xxb xug xuq xus xwb xuz">Questions &amp; Answers</h2>
</div>
<div className="xtb xtj xwr xws xtc xtk">
<div id="faq-1">
<button type="button" id="faq-1-question" command="--toggle" commandfor="faq-1-answer" className="xrm xrx xsm xso xsw xtx xue xuk xuz xxb">Do I need a credit card to start the free trial?<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvu">
<path  d="M6.5 0.5V12.5" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M12.5049 6.49512L0.504883 6.49512" strokeLinecap="round" strokeLinejoin="round" />
</svg>
<svg width="13" height="1" viewBox="0 0 13 1" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvk">
<path  stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" d="M12.505.5h-12" />
</svg>
</button>
<el-disclosure id="faq-1-answer" hidden className="xrh xrm xsj xss xub xuc xuo xuy xwy">Yes, but don&#x27;t worry, you won&#x27;t be charged until the trial period is over. We won&#x27;t send you an email reminding you when this happens because we are really hoping you&#x27;ll forget and we can keep charging you until your cards expires</el-disclosure>
</div>
<div id="faq-2">
<button type="button" id="faq-2-question" command="--toggle" commandfor="faq-2-answer" className="xrm xrx xsm xso xsw xtx xue xuk xuz xxb">Can my whole team use the same inbox?<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvu">
<path  d="M6.5 0.5V12.5" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M12.5049 6.49512L0.504883 6.49512" strokeLinecap="round" strokeLinejoin="round" />
</svg>
<svg width="13" height="1" viewBox="0 0 13 1" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvk">
<path  stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" d="M12.505.5h-12" />
</svg>
</button>
<el-disclosure id="faq-2-answer" hidden className="xrh xrm xsj xss xub xuc xuo xuy xwy">Yes, the more the merrier! Oatmeal works best when your entire company has access. We will charge you per additional seat, but we won&#x27;t tell you about this until you get your invoice.</el-disclosure>
</div>
<div id="faq-3">
<button type="button" id="faq-3-question" command="--toggle" commandfor="faq-3-answer" className="xrm xrx xsm xso xsw xtx xue xuk xuz xxb">Is the AI agent actually a bunch of people in India?<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvu">
<path  d="M6.5 0.5V12.5" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M12.5049 6.49512L0.504883 6.49512" strokeLinecap="round" strokeLinejoin="round" />
</svg>
<svg width="13" height="1" viewBox="0 0 13 1" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvk">
<path  stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" d="M12.505.5h-12" />
</svg>
</button>
<el-disclosure id="faq-3-answer" hidden className="xrh xrm xsj xss xub xuc xuo xuy xwy">Not just India! We have people in lots of countries around the world pretending to be an AI, including some that are currently under sanctions, so we can&#x27;t legally mention them here.</el-disclosure>
</div>
<div id="faq-4">
<button type="button" id="faq-4-question" command="--toggle" commandfor="faq-4-answer" className="xrm xrx xsm xso xsw xtx xue xuk xuz xxb">Does Oatmeal replace my email client?<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvu">
<path  d="M6.5 0.5V12.5" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M12.5049 6.49512L0.504883 6.49512" strokeLinecap="round" strokeLinejoin="round" />
</svg>
<svg width="13" height="1" viewBox="0 0 13 1" fill="none" stroke="currentColor" strokeWidth="1" role="image" className="xrp xrw xvk">
<path  stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" d="M12.505.5h-12" />
</svg>
</button>
<el-disclosure id="faq-4-answer" hidden className="xrh xrm xsj xss xub xuc xuo xuy xwy">Absolutely. The idea is that we transition you away from email entirely, so you become completely dependent on our service. Like a parasite living off a host.</el-disclosure>
</div>
</div>
</div>
</section>

<section className="xtz" id="call-to-action">
<div className="xrg xrx xry xtu xwf xwk xwn xrm xsj xsl xsy">
<div className="xrm xsj xsw">
<h2 className="xuf xuw xxb xug xuq xus xwb xuz xsa xud">Have anymore questions?</h2>
<div className="xuk xuy xwy xrm xrz xsj xsu xud xuw">
<p>Chat to someone on our sales team, who will make promises about our roadmap that we won&#x27;t keep.</p>
</div>
</div>
<div className="xrm xsl xsu">
<a href="#" className="xrq xsg xsl xsp xuo xuq xsr xtf xva xtm xvs xwu xxa xxd xtt xtw">Chat with us</a>
<a href="#" className="xrq xsg xsl xsp xuo xuq xss xtf xxb xxe xuz xvt xtt xtw">Book a demo <svg width="5" height="8" viewBox="0 0 5 8" fill="currentColor" role="image" className="xrp">
<path  fillRule="evenodd" clipRule="evenodd" d="M.22.22a.75.75 0 011.06 0l3.25 3.25a.75.75 0 010 1.06L1.28 7.78A.75.75 0 01.22 6.72L2.94 4 .22 1.28a.75.75 0 010-1.06z" />
</svg>
</a>
</div>
</div>
</section>
</main>
<footer className="xua" id="footer">
<div className="xtz xwx xxb xtn xuz">
<div className="xrg xrx xry xtu xwf xwk xwn xrm xsj xsz">
<nav className="xrn xsi xsw xuo xwd xwh xwe xwp">
<div>
<h3>Product</h3>
<ul role="list" className="xri xrm xsj xss">
<li className="xuy xwy">
<a href="#">Features</a>
</li>
<li className="xuy xwy">
<a href="#">Pricing</a>
</li>
<li className="xuy xwy">
<a href="#">Integrations</a>
</li>
</ul>
</div>
<div>
<h3>Company</h3>
<ul role="list" className="xri xrm xsj xss">
<li className="xuy xwy">
<a href="#">About</a>
</li>
<li className="xuy xwy">
<a href="#">Careers</a>
</li>
<li className="xuy xwy">
<a href="#">Blog</a>
</li>
<li className="xuy xwy">
<a href="#">Press Kit</a>
</li>
</ul>
</div>
<div>
<h3>Resources</h3>
<ul role="list" className="xri xrm xsj xss">
<li className="xuy xwy">
<a href="#">Help Center</a>
</li>
<li className="xuy xwy">
<a href="#">API Docs</a>
</li>
<li className="xuy xwy">
<a href="#">Status</a>
</li>
<li className="xuy xwy">
<a href="#">Contact</a>
</li>
</ul>
</div>
<div>
<h3>Legal</h3>
<ul role="list" className="xri xrm xsj xss">
<li className="xuy xwy">
<a href="/privacy-policy.html">Privacy Policy</a>
</li>
<li className="xuy xwy">
<a href="#">Terms of Service</a>
</li>
<li className="xuy xwy">
<a href="#">Security</a>
</li>
</ul>
</div>
<div>
<h3>Connect</h3>
<ul role="list" className="xri xrm xsj xss">
<li className="xuy xwy">
<a href="#">X</a>
</li>
<li className="xuy xwy">
<a href="#">GitHub</a>
</li>
<li className="xuy xwy">
<a href="#">YouTube</a>
</li>
</ul>
</div>
</nav>
<div className="xuo xux xwz">© 2025 Oatmeal, Inc.</div>
</div>
</div>
</footer>
  
    </div>
  );
};
