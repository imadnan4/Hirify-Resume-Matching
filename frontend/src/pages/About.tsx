import React from 'react';
import '../styles/about.css';

interface AboutProps {
  onNavigate?: (page: string) => void;
}

export const About: React.FC<AboutProps> = ({ onNavigate }) => {
  return (
    <div className="oatmeal-page oatmeal-about">
      
    <header className="xve xvg xvi xxi yap" id="navbar">
<style>{`:root { --scroll-padding-top: 5.25rem }`}</style>
<nav>
<div className="xvj xvm xvt xwd xwk xwt xxs yag">
<div className="xvm xwf xwk">
<a href="/" className="xvp xwm">
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=olive-950" alt="Oatmeal" className="yam" width="96" height="28"/>
<img src="https://assets.tailwindplus.com/logos/oatmeal-familjen.svg?color=white" alt="Oatmeal" className="xyz" width="96" height="28"/>
</a>
</div>
<div className="xvm xww xzi">
<a href="/pricing.html" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp">Pricing<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="/about.html" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp">About<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp">Docs<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp xzl">Log in<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
</div>
<div className="xvm xwf xwk xwp xwt">
<div className="xvm xwg xwk xwu">
<a href="#" className="xvp xwg xwk xwo xyf xyh xwr xxe yav yba xyp xzf xxp xxt xzj">Log in</a>
<a href="#" className="xvp xwg xwk xwo xyf xyh xwq xxe xyq xxj xze yao yau yaz xxp xxt">Get started</a>
</div>
<button command="show-modal" commandfor="mobile-menu" aria-label="Toggle menu" className="xvp xxe xxn yad yav yba xyp xzf">
<svg viewBox="0 0 24 24" fill="currentColor" className="xvs">
<path  fillRule="evenodd" d="M3.748 8.248a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75ZM3.748 15.75a.75.75 0 0 1 .75-.751h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
</svg>
</button>
</div>
</div>
<el-dialog className="yad">
<dialog id="mobile-menu" className="xzd">
<el-dialog-panel className="xvc xvf xxs xxv yag xxi yap">
<div className="xvm xwp">
<button command="close" commandfor="mobile-menu" aria-label="Toggle menu" className="xvp xxe xxn yav yba xyp xzf">
<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
</svg>
</button>
</div>
<div className="xvl xvm xwj xwv">
<a href="/pricing.html" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp">Pricing<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="/about.html" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp">About<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp">Docs<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
<path  strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
</svg>
</span>
</a>
<a href="#" className="xzc xvp xwk xwn xwr xya xyh yah yav xyp xzl">Log in<span className="xvp xxn xyt xzb yad" aria-hidden="true">
<svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="xvs">
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
<main className="xvh xxc">

<section className="xxw" id="hero">
<div className="xvj xvx xvz xxs xzy yae yag xvm xwy xzh">
<div className="xvm xwf xwj xwl xwo xwv">
<a href="#" data-variant="normal" className="xzc xvd xvp xwe xxa xxd xxf xxq xxu xye xzk xzn xzq xzr xzs yaq yav yaw yax yba xxl xyp xzf">
<span className="xym xzp">2025 Business of the Year</span>
<span className="xvu xvy xzj yar xxm">
</span>
<span className="xvp xwg xwk xwr xyi yav xyp">Learn more <svg width="5" height="8" viewBox="0 0 5 8" fill="currentColor" role="image" className="xvo xwg">
<path  fillRule="evenodd" clipRule="evenodd" d="M.22.22a.75.75 0 011.06 0l3.25 3.25a.75.75 0 010 1.06L1.28 7.78A.75.75 0 01.22 6.72L2.94 4 .22 1.28a.75.75 0 010-1.06z" />
</svg>
</span>
</a>
<h1 className="xxy xyl xyb xyk xzu yav xyp xwc">Your customer success is our mission.</h1>
<div className="xyd xyo yas xvm xwa xwj xwt">
<p>We&#x27;re on a mission to take the human element completely out of customer support — so your team can focus on what matters most, profitability.</p>
</div>
</div>
<div className="xvm xwf xxd xxh xyu xyv xyw xyy yay">
<img className="xza xzg yan" src="https://assets.tailwindplus.com/photos/1.webp" width="1800" height="1600" alt=""/>
<img className="xza yal yan" src="https://assets.tailwindplus.com/photos/1.webp" width="1800" height="945" alt=""/>
</div>
</div>
</section>

<section className="xxw" id="brands">
<div className="xvj xvx xvz xxs xzy yae yag xvm xwj xwx xzo">
<div className="xvm xvz xwj xwv">
<div className="xvm xwj xwr">
<div className="xyf xyi xyo yas">Backed by the best</div>
<h2 className="xxy xym yav xxz xyh xyj xzt xyp">Funded by leading investors.</h2>
</div>
<div className="xyc xyo yas xym">
<p>Oatmeal is backed by investors with decades of experience building the world&#x27;s most boring and predictable B2B SaaS.</p>
</div>
</div>
<div>
<div className="xvn xwh xwr xzm xzv yaa yac yai yaj">
<div className="xvm xwj xwn xwv xxh xxo yaq xxk">
<div className="xvm xwj xwl xwr">
<div className="xvm xvv xwg">
<img src="https://assets.tailwindplus.com/logos/15.svg?color=black&amp;width=110" className="yam" alt="" width="124" height="32"/>
<img src="https://assets.tailwindplus.com/logos/15.svg?color=white&amp;width=110" className="xyz" alt="" width="124" height="32"/>
</div>
<p className="xyf xyo yas">Focused capital for founders building the next generation of pyramid shaped businesses.</p>
</div>
<p className="xyg xyo yas">Investor in Anomaly, Concise, Haptic and more.</p>
</div>
<div className="xvm xwj xwn xwv xxh xxo yaq xxk">
<div className="xvm xwj xwl xwr">
<div className="xvm xvv xwg">
<img src="https://assets.tailwindplus.com/logos/16.svg?color=black&amp;width=120" className="yam" alt="" width="146" height="32"/>
<img src="https://assets.tailwindplus.com/logos/16.svg?color=white&amp;width=120" className="xyz" alt="" width="146" height="32"/>
</div>
<p className="xyf xyo yas">Serving as a tax-efficiency vehicle for investors waiting to move to a tax haven.</p>
</div>
<p className="xyg xyo yas">Investor in Quirk, Looply, Pine Labs and more.</p>
</div>
<div className="xvm xwj xwn xwv xxh xxo yaq xxk">
<div className="xvm xwj xwl xwr">
<div className="xvm xvv xwg">
<img src="https://assets.tailwindplus.com/logos/14.svg?color=black&amp;width=80" className="yam" alt="" width="106" height="32"/>
<img src="https://assets.tailwindplus.com/logos/14.svg?color=white&amp;width=80" className="xyz" alt="" width="106" height="32"/>
</div>
<p className="xyf xyo yas">Investing in potentially volatile bubble markets at an early stage.</p>
</div>
<p className="xyg xyo yas">Investor in Artifact, Umbra, vivid.ai and more.</p>
</div>
</div>
</div>
</div>
</section>

<section className="xxw" id="team">
<div className="xvj xvx xvz xxs xzy yae yag xvm xwj xwx xzo">
<div className="xvm xvz xwj xwv">
<div className="xvm xwj xwr">
<h2 className="xxy xym yav xxz xyh xyj xzt xyp">Our leadership team</h2>
</div>
<div className="xyc xyo yas xym">
<p>Oatmeals&#x27;s leadership team combines decades of experience in private equity, where they honed their skills in cost-cutting and maximizing shareholder value.</p>
</div>
</div>
<div>
<ul role="list" className="xvn xwi xwz xxb xzz">
<li className="xvm xwj xwt xyf">
<div className="xvq xvx xxd xxg xyu xyv xyw xyx xyy yay">
<img src="https://assets.tailwindplus.com/avatars/1.webp?w=800&amp;h=800" alt="" className="xza yan" width="800" height="800"/>
</div>
<div>
<p className="xyi yav xyp">Leslie Alexander</p>
<p className="xyo yas">Co-Founder / CEO</p>
</div>
</li>
<li className="xvm xwj xwt xyf">
<div className="xvq xvx xxd xxg xyu xyv xyw xyx xyy yay">
<img src="https://assets.tailwindplus.com/avatars/2.webp?w=800&amp;h=800" alt="" className="xza yan" width="800" height="800"/>
</div>
<div>
<p className="xyi yav xyp">Michael Foster</p>
<p className="xyo yas">Co-Founder / CTO</p>
</div>
</li>
<li className="xvm xwj xwt xyf">
<div className="xvq xvx xxd xxg xyu xyv xyw xyx xyy yay">
<img src="https://assets.tailwindplus.com/avatars/7.webp?w=800&amp;h=800" alt="" className="xza yan" width="800" height="800"/>
</div>
<div>
<p className="xyi yav xyp">Dries Vincent</p>
<p className="xyo yas">Business Relations</p>
</div>
</li>
</ul>
</div>
</div>
</section>

<section className="xxw" id="features">
<div className="xvj xvx xvz xxs xzy yae yag xvm xwj xwx xzo">
<div className="xvm xvz xwj xwv">
<div className="xvm xwj xwr">
<h2 className="xxy xym yav xxz xyh xyj xzt xyp">Our values.</h2>
</div>
<div className="xyc xyo yas xym">
<p>Work smarter, reply faster, and keep every customer conversation right where it belongs — in one simple inbox, where you can ignore it.</p>
</div>
</div>
<div>
<div className="xvn xwh xwx xzm yaf">
<div className="xvm xwj xwr xyf">
<div className="xvm xwl xws yav xyp">
<div className="xvm xvr xvw xwk">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" strokeWidth="1" role="image" className="xvo">
<path  d="M4.39765 4.6366C4.11422 4.54784 3.8127 4.5 3.5 4.5C1.84315 4.5 0.5 5.84315 0.5 7.5H3.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M8.36337 8.60227C8.45215 8.88572 8.5 9.18727 8.5 9.5C8.5 11.1569 7.15685 12.5 5.5 12.5V9.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M12.5 0.5C12.4999 3.05915 11.5239 5.61872 9.57129 7.57129C8.5287 8.61385 7.31272 9.3774 6.0166 9.86328C4.87091 9.11056 3.88841 8.12913 3.13574 6.9834C3.62163 5.68721 4.38609 4.47135 5.42871 3.42871C7.3813 1.47612 9.94082 0.500033 12.5 0.5ZM8.5 3.5C7.94772 3.5 7.5 3.94772 7.5 4.5C7.5 5.05228 7.94772 5.5 8.5 5.5C9.05229 5.5 9.5 5.05228 9.5 4.5C9.5 3.94772 9.05229 3.5 8.5 3.5Z" fill="currentColor" fill-opacity="0.2" />
<path  d="M12.5 0.5L13 0.500011C13 0.3674 12.9473 0.240219 12.8536 0.146448C12.7598 0.0526775 12.6326 -1.69037e-06 12.5 0L12.5 0.5ZM9.57129 7.57129L9.92484 7.92485L9.92484 7.92484L9.57129 7.57129ZM6.0166 9.86328L5.74206 10.2812C5.87545 10.3688 6.04266 10.3875 6.19211 10.3315L6.0166 9.86328ZM3.13574 6.9834L2.66756 6.80789C2.61154 6.95733 2.63022 7.12454 2.71785 7.25793L3.13574 6.9834ZM5.42871 3.42871L5.07516 3.07516L5.07515 3.07516L5.42871 3.42871ZM12.5 0.5L12 0.499989C11.9999 2.93201 11.0727 5.36274 9.21774 7.21774L9.57129 7.57129L9.92484 7.92484C11.975 5.87471 12.9999 3.18629 13 0.500011L12.5 0.5ZM9.57129 7.57129L9.21774 7.21773C8.22677 8.20867 7.07188 8.9337 5.84109 9.3951L6.0166 9.86328L6.19211 10.3315C7.55356 9.82109 8.83063 9.01902 9.92484 7.92485L9.57129 7.57129ZM6.0166 9.86328L6.29115 9.4454C5.20236 8.73007 4.26871 7.79737 3.55364 6.70887L3.13574 6.9834L2.71785 7.25793C3.50812 8.46089 4.53945 9.49105 5.74206 10.2812L6.0166 9.86328ZM3.13574 6.9834L3.60393 7.1589C4.06526 5.92824 4.79113 4.77342 5.78227 3.78226L5.42871 3.42871L5.07515 3.07516C3.98106 4.16928 3.17801 5.44618 2.66756 6.80789L3.13574 6.9834ZM5.42871 3.42871L5.78226 3.78226C7.63729 1.92724 10.068 1.00003 12.5 1L12.5 0.5L12.5 0C9.81368 3.42428e-05 7.12531 1.025 5.07516 3.07516L5.42871 3.42871ZM8.5 3.5V3C7.67157 3 7 3.67157 7 4.5H7.5H8C8 4.22386 8.22386 4 8.5 4V3.5ZM7.5 4.5H7C7 5.32843 7.67157 6 8.5 6V5.5V5C8.22386 5 8 4.77614 8 4.5H7.5ZM8.5 5.5V6C9.32843 6 10 5.32843 10 4.5H9.5H9C9 4.77614 8.77614 5 8.5 5V5.5ZM9.5 4.5H10C10 3.67157 9.32843 3 8.5 3V3.5V4C8.77614 4 9 4.22386 9 4.5H9.5Z" fill="currentColor" />
<path  d="M1.30213 9.5C0.767377 10.4252 0.5 11.4626 0.5 12.5C1.53741 12.5 2.57482 12.2326 3.5 11.6979" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</div>
<h3 className="xyi">Innovation</h3>
</div>
<div className="xvm xwj xwt xyo yas">
<p>We are constantly pushing the boundaries of what&#x27;s possible, and legal, in customer support to deliver cutting-edge solutions for our clients.</p>
</div>
</div>
<div className="xvm xwj xwr xyf">
<div className="xvm xwl xws yav xyp">
<div className="xvm xvr xvw xwk">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" strokeWidth="1" role="image" className="xvo">
<path  d="M12.5 3.99997C12.5 2.34312 11.1009 0.999971 9.375 0.999971C8.08459 0.999971 6.97685 1.75082 6.5 2.82225C6.02315 1.75082 4.91541 0.999971 3.625 0.999971C1.89911 0.999971 0.5 2.34312 0.5 3.99997C0.5 8.81368 6.5 12 6.5 12C6.5 12 12.5 8.81368 12.5 3.99997Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</div>
<h3 className="xyi">Integrity</h3>
</div>
<div className="xvm xwj xwt xyo yas">
<p>We are driven by a commitment to ethical business practices, transparency, and most of all, maximizing shareholder value.</p>
</div>
</div>
<div className="xvm xwj xwr xyf">
<div className="xvm xwl xws yav xyp">
<div className="xvm xvr xvw xwk">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" strokeWidth="1" role="image" className="xvo">
<path  d="M6.50488 2.50488H8.50488C9.60945 2.50488 10.5049 3.40031 10.5049 4.50488V9.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M8.50977 0.5L6.50976 2.5L8.50977 4.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M12 11C12 11.8284 11.3284 12.5 10.5 12.5C9.67157 12.5 9 11.8284 9 11C9 10.1716 9.67157 9.5 10.5 9.5C11.3284 9.5 12 10.1716 12 11Z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" strokeLinecap="round" />
<path  d="M6.49512 10.4951L4.49512 10.4951C3.39055 10.4951 2.49512 9.59969 2.49512 8.49512L2.49512 3.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M4.49023 12.5L6.49024 10.5L4.49023 8.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M1 2C1 1.17157 1.67157 0.5 2.5 0.5C3.32843 0.5 4 1.17157 4 2C4 2.82843 3.32843 3.5 2.5 3.5C1.67157 3.5 1 2.82843 1 2Z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" strokeLinecap="round" />
</svg>
</div>
<h3 className="xyi">Collaboration</h3>
</div>
<div className="xvm xwj xwt xyo yas">
<p>We believe teamwork makes the dream work, especially when that dream is offshoring local jobs to the lowest bidder.</p>
</div>
</div>
<div className="xvm xwj xwr xyf">
<div className="xvm xwl xws yav xyp">
<div className="xvm xvr xvw xwk">
<svg width="13" height="11" viewBox="0 0 13 11" fill="none" strokeWidth="1" role="image" className="xvo">
<path  d="M6.5 2.5C6.5 3.60457 5.60457 4.5 4.5 4.5C3.39543 4.5 2.5 3.60457 2.5 2.5C2.5 1.39543 3.39543 0.5 4.5 0.5C5.60457 0.5 6.5 1.39543 6.5 2.5Z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M11.5 4C11.5 4.82843 10.8284 5.5 10 5.5C9.17157 5.5 8.5 4.82843 8.5 4C8.5 3.17157 9.17157 2.5 10 2.5C10.8284 2.5 11.5 3.17157 11.5 4Z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M8.5 10.5H0.5C0.5 8.29086 2.29086 6.5 4.5 6.5C6.70914 6.5 8.5 8.29086 8.5 10.5Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M7.97998 8.52659C8.43471 7.90427 9.17008 7.5 9.99986 7.5C11.3806 7.5 12.4999 8.61929 12.4999 10V10.5H8.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</div>
<h3 className="xyi">Diversity</h3>
</div>
<div className="xvm xwj xwt xyo yas">
<p>Diversity can mean many things, but to us it mainly means hiring people from countries with the lowest labour costs.</p>
</div>
</div>
<div className="xvm xwj xwr xyf">
<div className="xvm xwl xws yav xyp">
<div className="xvm xvr xvw xwk">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" strokeWidth="1" role="image" className="xvo">
<path  d="M9.5 2.5L10.5 1.5V2.5H11.5L10.5 3.5H9.5V2.5Z" fill="currentColor" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M6.5 6.5L9.5 3.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M6.37523 4.50383C5.32878 4.56824 4.5 5.43733 4.5 6.5C4.5 7.60457 5.39543 8.5 6.5 8.5C7.56255 8.5 8.43158 7.67139 8.49615 6.6251" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M10.2092 5C10.3967 5.46322 10.5 5.96955 10.5 6.5C10.5 8.70914 8.70914 10.5 6.5 10.5C4.29086 10.5 2.5 8.70914 2.5 6.5C2.5 4.29086 4.29086 2.5 6.5 2.5C7.03045 2.5 7.53678 2.60325 8 2.79076" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
<path  d="M12.0069 4.11417C12.3241 4.84539 12.5 5.65216 12.5 6.5C12.5 9.81371 9.81371 12.5 6.5 12.5C3.18629 12.5 0.5 9.81371 0.5 6.5C0.5 3.18629 3.18629 0.5 6.5 0.5C7.34784 0.5 8.15461 0.675855 8.88583 0.993081" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
</svg>
</div>
<h3 className="xyi">Accountability</h3>
</div>
<div className="xvm xwj xwt xyo yas">
<p>Our customers&#x27; success is our success and their failure is our failure, except in the legal sense where our liability is limited.</p>
</div>
</div>
<div className="xvm xwj xwr xyf">
<div className="xvm xwl xws yav xyp">
<div className="xvm xvr xvw xwk">
<svg width="13" height="13" viewBox="0 0 13 13" fill="none" strokeWidth="1" role="image" className="xvo">
<path  stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" d="m6.5.5 1.347 4.146h4.36L8.68 7.208l1.347 4.146L6.5 8.792l-3.527 2.562L4.32 7.208.793 4.646h4.36L6.5.5Z" />
</svg>
</div>
<h3 className="xyi">Quality</h3>
</div>
<div className="xvm xwj xwt xyo yas">
<p>We believe that you can move fast without breaking things, unless those things are labour laws in third world countries.</p>
</div>
</div>
</div>
</div>
</div>
</section>

<section className="xxw" id="call-to-action">
<div className="xvj xvx xvz xxs xzy yae yag xvm xwj xwx">
<div className="xvm xwj xwv">
<div className="xvm xwb xwj xwr">
<h2 className="xxy xym yav xxz xyh xyj xzt xyp">Have anymore questions?</h2>
</div>
<div className="xyc xyo yas xvm xwa xwj xwt xym">
<p>Chat to someone on our sales team, who will make promises about our roadmap that we won&#x27;t keep.</p>
</div>
</div>
<div className="xvm xwk xwt">
<a href="#" className="xvp xwg xwk xwo xyf xyh xwq xxe xyq xxj xze yao yau yaz xxr xxu">Chat with us</a>
<a href="#" className="xvp xwg xwk xwo xyf xyh xwr xxe yav yba xyp xzf xxr xxu">Book a demo <svg width="5" height="8" viewBox="0 0 5 8" fill="currentColor" role="image" className="xvo">
<path  fillRule="evenodd" clipRule="evenodd" d="M.22.22a.75.75 0 011.06 0l3.25 3.25a.75.75 0 010 1.06L1.28 7.78A.75.75 0 01.22 6.72L2.94 4 .22 1.28a.75.75 0 010-1.06z" />
</svg>
</a>
</div>
</div>
</section>
</main>
<footer className="xxx" id="footer">
<div className="xxw yaq yav xxk xyp">
<div className="xvj xvx xvz xxs xzy yae yag xvm xwj xwy">
<nav className="xvn xwi xwv xyf xzw yab xzx yak">
<div>
<h3>Product</h3>
<ul role="list" className="xvk xvm xwj xwr">
<li className="xyo yas">
<a href="#">Features</a>
</li>
<li className="xyo yas">
<a href="#">Pricing</a>
</li>
<li className="xyo yas">
<a href="#">Integrations</a>
</li>
</ul>
</div>
<div>
<h3>Company</h3>
<ul role="list" className="xvk xvm xwj xwr">
<li className="xyo yas">
<a href="#">About</a>
</li>
<li className="xyo yas">
<a href="#">Careers</a>
</li>
<li className="xyo yas">
<a href="#">Blog</a>
</li>
<li className="xyo yas">
<a href="#">Press Kit</a>
</li>
</ul>
</div>
<div>
<h3>Resources</h3>
<ul role="list" className="xvk xvm xwj xwr">
<li className="xyo yas">
<a href="#">Help Center</a>
</li>
<li className="xyo yas">
<a href="#">API Docs</a>
</li>
<li className="xyo yas">
<a href="#">Status</a>
</li>
<li className="xyo yas">
<a href="#">Contact</a>
</li>
</ul>
</div>
<div>
<h3>Legal</h3>
<ul role="list" className="xvk xvm xwj xwr">
<li className="xyo yas">
<a href="/privacy-policy.html">Privacy Policy</a>
</li>
<li className="xyo yas">
<a href="#">Terms of Service</a>
</li>
<li className="xyo yas">
<a href="#">Security</a>
</li>
</ul>
</div>
<div>
<h3>Connect</h3>
<ul role="list" className="xvk xvm xwj xwr">
<li className="xyo yas">
<a href="#">X</a>
</li>
<li className="xyo yas">
<a href="#">GitHub</a>
</li>
<li className="xyo yas">
<a href="#">YouTube</a>
</li>
</ul>
</div>
</nav>
<div className="xyf xyn yat">© 2025 Oatmeal, Inc.</div>
</div>
</div>
</footer>
  
    </div>
  );
};
