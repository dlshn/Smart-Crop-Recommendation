import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/about", label: "About" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Close the mobile menu on route change (any nav click)
  const closeMenu = () => setOpen(false);

  const linkClass = ({ isActive }) =>
    [
      "relative rounded-full px-4 py-2 text-sm font-semibold transition-colors duration-200",
      isActive ? "text-leaf" : "text-ink/60 hover:text-leaf",
    ].join(" ");

  return (
    <nav
      className={[
        "sticky top-4 z-20 mb-6 rounded-none border border-leaf/15 bg-white/85 backdrop-blur-md transition-shadow duration-300",
        scrolled ? "shadow-lg" : "shadow-soft",
      ].join(" ")}
    >
      <div className="flex items-center justify-between px-5 py-3.5">
        <NavLink to="/" className="text-[1.05rem] font-bold tracking-wide text-leaf" onClick={closeMenu}>
          SmartCrop
        </NavLink>

        {/* Desktop links */}
        <div className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.end} className={linkClass}>
              {({ isActive }) => (
                <>
                  {link.label}
                  <span
                    className={[
                      "absolute inset-x-4 -bottom-0.5 h-0.5 rounded-full bg-leaf transition-opacity duration-200",
                      isActive ? "opacity-100" : "opacity-0",
                    ].join(" ")}
                  />
                </>
              )}
            </NavLink>
          ))}
        </div>

        {/* Mobile hamburger */}
        <button
          type="button"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
          className="flex h-9 w-9 items-center justify-center rounded-full border border-leaf/20 text-ink/70 transition-colors hover:text-leaf md:hidden"
        >
          <span className="relative block h-3.5 w-4">
            <span
              className={[
                "absolute left-0 top-0 h-0.5 w-4 rounded-full bg-current transition-transform duration-200",
                open ? "translate-y-[6px] rotate-45" : "",
              ].join(" ")}
            />
            <span
              className={[
                "absolute left-0 top-1.5 h-0.5 w-4 rounded-full bg-current transition-opacity duration-200",
                open ? "opacity-0" : "opacity-100",
              ].join(" ")}
            />
            <span
              className={[
                "absolute left-0 top-3 h-0.5 w-4 rounded-full bg-current transition-transform duration-200",
                open ? "-translate-y-[6px] -rotate-45" : "",
              ].join(" ")}
            />
          </span>
        </button>
      </div>

      {/* Mobile dropdown panel */}
      <div
        className={[
          "grid overflow-hidden transition-[grid-template-rows] duration-300 ease-out md:hidden",
          open ? "grid-rows-[1fr]" : "grid-rows-[0fr]",
        ].join(" ")}
      >
        <div className="min-h-0">
          <div className="flex flex-col gap-1 border-t border-leaf/10 px-3 pb-3 pt-2">
            {LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                onClick={closeMenu}
                className={({ isActive }) =>
                  [
                    "rounded-xl px-3 py-2.5 text-sm font-semibold transition-colors",
                    isActive ? "bg-leaf/10 text-leaf" : "text-ink/60 hover:bg-cream hover:text-leaf",
                  ].join(" ")
                }
              >
                {link.label}
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
