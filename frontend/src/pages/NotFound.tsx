import React from 'react';
import '../styles/404.css';

interface NotFoundProps {
  onNavigate?: (page: string) => void;
}

export const NotFound: React.FC<NotFoundProps> = ({ onNavigate }) => {
  return (
    <div className="oatmeal-page oatmeal-404">
      
    <header className="rex rez rfb rgq rit" id="navbar">
<style>{`:root { --scroll-padding-top: 5.25rem }`}</style>
<nav>
<div className="rfc rff rfl rfo rfw rge rgv rin">
<div className="rff rfr rgh rib">
<a href="./pricing-01.html" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl">Pricing<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="./about-01.html" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl">About<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl">Docs<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl rid">Log in<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
</div>
<div className="rff rfw">
<a href="./home-01.html" className="rfi rfy">
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=olive-950" alt="Oatmeal" className="riq" width="96" height="28"/>
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=white" alt="Oatmeal" className="rhr" width="96" height="28"/>
</a>
</div>
<div className="rff rfr rfw rgb rge">
<div className="rff rfs rfw rgf">
<a href="#" className="rfi rfs rfw rga rhf rhg rgd rgn riy rja rhl rhy rgu rgw ric">Log in</a>
<a href="#" className="rfi rfs rfw rga rhf rhg rgc rgn rhm rgr rhx ris rix riz rgu rgw">Get started</a>
</div>
<button command="show-modal" commandfor="mobile-menu" aria-label="Toggle menu" className="rfi rgn rgt rik riy rja rhl rhy">
<svg viewBox="0 0 24 24" fill="currentColor" className="rfj">
<path  fillRule="evenodd" d="M3.748 8.248a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75ZM3.748 15.75a.75.75 0 0 1 .75-.751h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
</svg>
</button>
</div>
</div>
<el-dialog className="rik">
<dialog id="mobile-menu" className="rhu">
<el-dialog-panel className="rev rey rgv rgy rin rgq rit">
<div className="rff rgb">
<button command="close" commandfor="mobile-menu" aria-label="Toggle menu" className="rfi rgn rgt riy rja rhl rhy">
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
</svg>
</button>
</div>
<div className="rfe rff rfv rgg">
<a href="./pricing-01.html" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl">Pricing<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="./about-01.html" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl">About<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl">Docs<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="rht rfi rfw rfz rgd rhc rhg rio riy rhl rid">Log in<span className="rfi rgt rhp rhs rik" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="rfj">
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
<main className="rfa rgm">
<section className="rgz">
<div className="rfc rfm rfn rgv rii ril rin rff rfv rfx rgg">
<h1 className="rhb rhi rhd rhh rif riy rhl">Page not found</h1>
<div className="rhe rhk riv rff rfq rfv rge">
<p>Sorry, but the page you were looking for could not be found.</p>
</div>
<a href="/" className="rfi rfw rgd rhf rhg riy rhl">Go back home <svg width="13" height="7" viewBox="0 0 13 7" fill="none" strokeWidth="1" role="image" className="rfh">
<path  d="M12.5049 3.49512L0.504883 3.49512" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M9.5 6.5L12.5 3.5L9.5 0.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</a>
</div>
</section>
</main>
<footer className="rha" id="footer">
<div className="rgz riu riy rgs rhl">
<div className="rfc rfm rfn rgv rii ril rin rff rfv rgj">
<div className="rfg rft rgk rgl rhf rim">
<form className="rff rfp rfv rgd" action="#">
<p>Stay in the loop</p>
<div className="rff rfv rge rhk riv">
<p>Get customer support tips, product updates and customer stories that you can archive as soon as they arrive.</p>
</div>
<div className="rff rfw rgo rgx rir rjb rgp ria">
<input type="email" placeholder="Email" aria-label="Email" className="rfr rhz riy rhl"/>
<button type="submit" aria-label="Subscribe" className="rfi rfk rfw rga rgn rew rhv rhw rjc rja rhy">
<svg width="13" height="7" viewBox="0 0 13 7" fill="none" strokeWidth="1" role="image" className="rfh">
<path  d="M12.5049 3.49512L0.504883 3.49512" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M9.5 6.5L12.5 3.5L9.5 0.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</button>
</div>
</form>
<nav className="rfg rfu rgg rig rij rip rih">
<div>
<h3>Product</h3>
<ul role="list" className="rfd rff rfv rgd">
<li className="rhk riv">
<a href="#">Features</a>
</li>
<li className="rhk riv">
<a href="#">Pricing</a>
</li>
<li className="rhk riv">
<a href="#">Integrations</a>
</li>
</ul>
</div>
<div>
<h3>Company</h3>
<ul role="list" className="rfd rff rfv rgd">
<li className="rhk riv">
<a href="#">About</a>
</li>
<li className="rhk riv">
<a href="#">Careers</a>
</li>
<li className="rhk riv">
<a href="#">Blog</a>
</li>
<li className="rhk riv">
<a href="#">Press Kit</a>
</li>
</ul>
</div>
<div>
<h3>Resources</h3>
<ul role="list" className="rfd rff rfv rgd">
<li className="rhk riv">
<a href="#">Help Center</a>
</li>
<li className="rhk riv">
<a href="#">API Docs</a>
</li>
<li className="rhk riv">
<a href="#">Status</a>
</li>
<li className="rhk riv">
<a href="#">Contact</a>
</li>
</ul>
</div>
<div>
<h3>Legal</h3>
<ul role="list" className="rfd rff rfv rgd">
<li className="rhk riv">
<a href="./privacy-policy-01.html">Privacy Policy</a>
</li>
<li className="rhk riv">
<a href="#">Terms of Service</a>
</li>
<li className="rhk riv">
<a href="#">Security</a>
</li>
</ul>
</div>
</nav>
</div>
<div className="rff rfw rfz rgi rhf">
<div className="rhj riw">© 2025 Oatmeal, Inc.</div>
<div className="rff rfw rge rie">
<a href="https://x.com" target="_blank" aria-label="X" className="rhq riy rhl">
<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" role="image" className="rfh">
<path  d="M13.6833 10.6218L20.2401 3H18.6864L12.9931 9.61788L8.44583 3H3.20117L10.0775 13.0074L3.20117 21H4.75501L10.7673 14.0113L15.5695 21H20.8141L13.6833 10.6218ZM11.5551 13.0956L10.8584 12.0991L5.31488 4.16971H7.7015L12.1752 10.5689L12.8719 11.5655L18.6871 19.8835H16.3005L11.5551 13.0956Z" />
</svg>
</a>
<a href="https://github.com" target="_blank" aria-label="GitHub" className="rhq riy rhl">
<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" role="image" className="rfh">
<path  fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
</svg>
</a>
<a href="https://www.youtube.com" target="_blank" aria-label="YouTube" className="rhq riy rhl">
<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" role="image" className="rfh">
<path  fillRule="evenodd" d="M19.812 5.418c.861.23 1.538.907 1.768 1.768C21.998 8.746 22 12 22 12s0 3.255-.418 4.814a2.504 2.504 0 0 1-1.768 1.768c-1.56.419-7.814.419-7.814.419s-6.255 0-7.814-.419a2.505 2.505 0 0 1-1.768-1.768C2 15.255 2 12 2 12s0-3.255.417-4.814a2.507 2.507 0 0 1 1.768-1.768C5.744 5 11.998 5 11.998 5s6.255 0 7.814.418ZM15.194 12 10 15V9l5.194 3Z" clipRule="evenodd" />
</svg>
</a>
</div>
</div>
</div>
</div>
</footer>
  
    </div>
  );
};
