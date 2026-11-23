
function Sidebar({ activePage, onNavigate }) {
    const navigation = [
        { name: "Dashboard", icon: "◈" },
        { name: "Benchmark History", icon: "◉" },
        { name: "Model Comparison", icon: "◫" },
        { name: "Sustainability", icon: "♧" },
        { name: "Recommendations", icon: "◎" }
    ];

    return (
        <aside className="w-64 min-h-screen shrink-0 bg-[#10352B] text-white flex flex-col p-5">

            {/* Brand */}
            <div className="mb-10">
                <h1 className="text-2xl font-bold text-emerald-400">
                    EcoAI
                </h1>
                <p className="text-xs text-emerald-100/70 mt-1">
                    Sustainable AI Benchmark
                </p>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-2">
                {navigation.map(item => {
                    const isActive = activePage === item.name;

                    return (
                        <button
                            key={item.name}
                            onClick={() => onNavigate(item.name)}
                            className={`w-full text-left px-4 py-3 rounded-lg transition ${
                                isActive
                                    ? "bg-emerald-500/15 text-emerald-400 font-semibold"
                                    : "text-emerald-50 hover:bg-[#205341]"
                            }`}
                        >
                            <span className="mr-3">{item.icon}</span>
                            {item.name}
                        </button>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="border-t border-[#285B49] pt-4">
                <p className="text-xs text-emerald-100/60">
                    EcoAI Benchmark v1.0
                </p>
                <p className="text-xs text-emerald-100/60 mt-1">
                    Built for sustainable AI
                </p>
            </div>

        </aside>
    );
}

export default Sidebar;
