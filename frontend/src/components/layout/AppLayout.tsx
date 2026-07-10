import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useAuthStore } from "@/stores/authStore";
import logo from "@/assets/logo.png";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `press-feedback nav-link ${isActive ? "nav-link-active" : ""}`;

export function AppLayout() {
  const navigate = useNavigate();
  const clearTokens = useAuthStore((state) => state.clearTokens);

  const handleLogout = () => {
    clearTokens();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <header className="glass-chrome sticky top-0 z-50">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4">
          <div className="flex items-center gap-6">
            <div>
              <img
                src={logo}
                alt="OpenPulse"
                className="h-9 w-auto mix-blend-screen"
              />
              <h1 className="mt-1 text-lg font-semibold tracking-tight text-white">
                Market Terminal
              </h1>
            </div>
            <nav className="flex items-center gap-1">
              <NavLink to="/dashboard" className={navLinkClass}>
                Dashboard
              </NavLink>
              <NavLink to="/events" className={navLinkClass}>
                Events
              </NavLink>
              <NavLink to="/settings" className={navLinkClass}>
                Settings
              </NavLink>
            </nav>
          </div>
          <Button variant="ghost" onClick={handleLogout}>
            Log out
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
