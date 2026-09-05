import React from 'react';
import '../styles/privacy-policy.css';

interface PrivacyPolicyProps {
  onNavigate?: (page: string) => void;
}

export const PrivacyPolicy: React.FC<PrivacyPolicyProps> = ({ onNavigate }) => {
  return (
    <div className="oatmeal-page oatmeal-privacy-policy">
      
    <header className="sbm sbo sbq scx ses" id="navbar">
<style>{`:root { --scroll-padding-top: 5.25rem }`}</style>
<nav>
<div className="sbr sbu sby scb sch sco sdc sen">
<div className="sbu scd sch">
<a href="/" className="sbw sci">
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=olive-950" alt="Oatmeal" className="seq" width="96" height="28"/>
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=white" alt="Oatmeal" className="sdw" width="96" height="28"/>
</a>
</div>
<div className="sbu scr sec">
<a href="/pricing.html" className="sdy sbw sch scj scn sdi sdm seo sex sdr">Pricing<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="/about.html" className="sdy sbw sch scj scn sdi sdm seo sex sdr">About<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="sdy sbw sch scj scn sdi sdm seo sex sdr">Docs<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="sdy sbw sch scj scn sdi sdm seo sex sdr see">Log in<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
</div>
<div className="sbu scd sch scl sco">
<div className="sbu sce sch scp">
<a href="#" className="sbw sce sch sck sdl sdm scn scw sex sez sdr seb sdb sdd sed">Log in</a>
<a href="#" className="sbw sce sch sck sdl sdm scm scw sds scy sea ser sew sey sdb sdd">Get started</a>
</div>
<button command="show-modal" commandfor="mobile-menu" aria-label="Toggle menu" className="sbw scw sda sel sex sez sdr seb">
<svg viewBox="0 0 24 24" fill="currentColor" className="sbx">
<path  fillRule="evenodd" d="M3.748 8.248a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75ZM3.748 15.75a.75.75 0 0 1 .75-.751h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
</svg>
</button>
</div>
</div>
<el-dialog className="sel">
<dialog id="mobile-menu" className="sdz">
<el-dialog-panel className="sbl sbn sdc sde sen scx ses">
<div className="sbu scl">
<button command="close" commandfor="mobile-menu" aria-label="Toggle menu" className="sbw scw sda sex sez sdr seb">
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
</svg>
</button>
</div>
<div className="sbt sbu scg scq">
<a href="/pricing.html" className="sdy sbw sch scj scn sdi sdm seo sex sdr">Pricing<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="/about.html" className="sdy sbw sch scj scn sdi sdm seo sex sdr">About<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="sdy sbw sch scj scn sdi sdm seo sex sdr">Docs<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="sdy sbw sch scj scn sdi sdm seo sex sdr see">Log in<span className="sbw sda sdv sdx sel" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="sbx">
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
<main className="sbp scv">
<section className="sdf" id="document">
<div className="sbr sbz sca sdc sej sem sen sbu scg scs sef">
<div className="sbu sca scg scq">
<h1 className="sdh sdo sdj sdn seg sex sdr">Privacy Policy</h1>
<div className="sdk sdq seu sbu scc scg sco">
<p>Last updated on December 19, 2025.</p>
</div>
</div>
<div className="scu sdl sfn sfp sfa sfc sfd sfe sff sfg sfi sfj sfq sfr sfl sfm sfk sdq seu sfb sfh sfo sfs sft sca">
<p>Company Inc. (&quot;<strong>Company</strong>,&quot; &quot;<strong>we</strong>,&quot; &quot;<strong>us</strong>,&quot; or &quot;<strong>our</strong>&quot;) respects your privacy and is committed to protecting your personal information. This Privacy Policy describes, in general terms, how we collect, use, store, and protect information when you interact with our websites, products, or services (collectively, the &quot;<strong>Services</strong>&quot;). This policy is provided for informational purposes and is intended to be a general example only.</p>
<h2>Information We Collect and How We Use It</h2>
<p>We may collect information that you voluntarily provide to us when you interact with the Services, such as when you contact us, create an account, or otherwise communicate with us. This information may include basic personal or account details, such as your name, email address, or similar contact information.</p>
<p>We may also automatically collect limited technical or usage information when you use the Services. This may include information such as browser type, device or operating system details, IP address, and general usage data.</p>
<p>Information we collect may be used for purposes such as:</p>
<ul>
<li>Providing and maintaining the Services</li>
<li>Responding to inquiries and communications</li>
<li>Improving features and functionality</li>
<li>Complying with applicable legal obligations</li>
</ul>
<h2>Sharing, Retention, and Security of Information</h2>
<p>We do not sell your personal information. We may share information with third-party service providers who perform services on our behalf, such as hosting or technical support, and only to the extent necessary for them to perform those services. We may also disclose information if required to do so by law or in response to valid legal requests.</p>
<p>We retain information only for as long as reasonably necessary to fulfill the purposes described in this Privacy Policy, unless a longer retention period is required or permitted by law.</p>
<p>We take reasonable administrative, technical, and organizational measures designed to protect information from unauthorized access, use, alteration, or disclosure. However, no method of transmission over the internet or method of electronic storage is completely secure, and we cannot guarantee absolute security.</p>
<h2>Your Choices, Updates, and Contact Information</h2>
<p>You may choose not to provide certain information to us, though doing so may limit your ability to use some features of the Services. Depending on your location, you may have certain rights regarding your personal information under applicable laws.</p>
<p>We may update this Privacy Policy from time to time. Any changes will be reflected by updating the &quot;<strong>Last updated</strong>&quot; date at the top of this page. Continued use of the Services after any changes indicates acceptance of the updated policy.</p>
<p>If you have any questions about this Privacy Policy, please contact us at:</p>
<p>
<strong>Company Inc.</strong>
<br/>Email: <a href="mailto:privacy@example.com">privacy@example.com</a>
<br/>Address: 123 Demo Street, Example City, Country</p>
</div>
</div>
</section>
</main>
<footer className="sdg" id="footer">
<div className="sdf set sex scz sdr">
<div className="sbr sbz sca sdc sej sem sen sbu scg sct">
<nav className="sbv scf scq sdl seh sek sei sep">
<div>
<h3>Product</h3>
<ul role="list" className="sbs sbu scg scn">
<li className="sdq seu">
<a href="#">Features</a>
</li>
<li className="sdq seu">
<a href="#">Pricing</a>
</li>
<li className="sdq seu">
<a href="#">Integrations</a>
</li>
</ul>
</div>
<div>
<h3>Company</h3>
<ul role="list" className="sbs sbu scg scn">
<li className="sdq seu">
<a href="#">About</a>
</li>
<li className="sdq seu">
<a href="#">Careers</a>
</li>
<li className="sdq seu">
<a href="#">Blog</a>
</li>
<li className="sdq seu">
<a href="#">Press Kit</a>
</li>
</ul>
</div>
<div>
<h3>Resources</h3>
<ul role="list" className="sbs sbu scg scn">
<li className="sdq seu">
<a href="#">Help Center</a>
</li>
<li className="sdq seu">
<a href="#">API Docs</a>
</li>
<li className="sdq seu">
<a href="#">Status</a>
</li>
<li className="sdq seu">
<a href="#">Contact</a>
</li>
</ul>
</div>
<div>
<h3>Legal</h3>
<ul role="list" className="sbs sbu scg scn">
<li className="sdq seu">
<a href="/privacy-policy.html">Privacy Policy</a>
</li>
<li className="sdq seu">
<a href="#">Terms of Service</a>
</li>
<li className="sdq seu">
<a href="#">Security</a>
</li>
</ul>
</div>
<div>
<h3>Connect</h3>
<ul role="list" className="sbs sbu scg scn">
<li className="sdq seu">
<a href="#">X</a>
</li>
<li className="sdq seu">
<a href="#">GitHub</a>
</li>
<li className="sdq seu">
<a href="#">YouTube</a>
</li>
</ul>
</div>
</nav>
<div className="sdl sdp sev">© 2025 Oatmeal, Inc.</div>
</div>
</div>
</footer>

    </div>
  );
};
