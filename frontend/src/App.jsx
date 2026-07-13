import { NavLink, Route, Routes } from "react-router-dom";

import ChatPage from "./pages/ChatPage.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import DocumentsPage from "./pages/DocumentsPage.jsx";

const navItems = [
  { to: "/", label: "대시보드", end: true },
  { to: "/documents", label: "문서 관리" },
  { to: "/chat", label: "Q&A 채팅" },
];

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <div>
            <h1 className="text-lg font-semibold text-gray-950">문서 기반 RAG Q&A 앱</h1>
            <p className="mt-1 text-sm text-gray-500">업로드한 문서를 근거로 답변하는 업무용 검색 도구</p>
          </div>
          <nav className="flex gap-1 rounded-md bg-gray-100 p-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    "px-3 py-2 text-sm font-medium transition",
                    isActive ? "bg-white text-gray-950 shadow-sm" : "text-gray-600 hover:text-gray-950",
                  ].join(" ")
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </main>
    </div>
  );
}
