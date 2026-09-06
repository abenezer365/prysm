import { useLayoutEffect } from "react";
import { useLocation } from "react-router-dom";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export default function MotionSystem() {
  const { pathname } = useLocation();
  useLayoutEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return undefined;
    const context = gsap.context(() => {
      gsap.fromTo(".route-stage", { autoAlpha: 0, y: 18 }, { autoAlpha: 1, y: 0, duration: .55, ease: "power3.out", clearProps: "transform,opacity,visibility" });
      gsap.utils.toArray(".route-stage main > section, .route-stage > section, .route-stage .viewport-section").forEach((section) => {
        gsap.fromTo(section.children, { autoAlpha: 0, y: 26 }, { autoAlpha: 1, y: 0, duration: .65, stagger: .055, ease: "power3.out", scrollTrigger: { trigger: section, start: "top 84%", once: true } });
      });
    });
    return () => context.revert();
  }, [pathname]);
  return null;
}
