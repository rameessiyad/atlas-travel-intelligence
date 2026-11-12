export default function Header() {
  return (
    <header className="flex items-center gap-3">
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,#4f46e5,#7c3aed)] shadow-lg shadow-indigo-500/30">
        <svg viewBox="0 0 24 24" className="h-6 w-6 text-white" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="9" />
          <path d="m15.5 8.5-2 5-5 2 2-5 5-2Z" />
        </svg>
      </div>
      <div>
        <h1 className="text-xl font-bold tracking-tight">Atlas</h1>
        <p className="text-xs text-slate-500">Personal Travel Intelligence</p>
      </div>
    </header>
  );
}