import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import About from "./pages/About.jsx";

export default function App() {
  return (
    <div className="mx-auto max-w-[1100px] px-5 pb-16 pt-5">
      <Navbar />

      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      <footer className="mt-10 text-center border-t border-leaf/10 pt-5 text-sm text-ink/50">
        These recommendations are estimates drawn from past rainfall and price patterns
        (2020–2024) — they can be wrong. Treat them as one input to your planting decision,
        not the final word.
      </footer>
    </div>
  );
}
