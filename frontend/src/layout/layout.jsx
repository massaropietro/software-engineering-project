import { Outlet } from "react-router-dom";
import React from "react";
import Navigation from "../navbar/navbar.jsx";

export default function Layout() {
    return (
        <div className="min-h-screen bg-background font-sans antialiased flex flex-col">
            <Navigation/>
            <main className="flex-grow flex items-center bg-header justify-center p-6">
                {/* Modificato da max-w-7xl a max-w-5xl per restringere leggermente il contenitore */}
                <div className="w-full max-w-5xl bg-main text-foreground border border-gray-200 dark:border-gray-800 rounded-3xl shadow-lg p-10">
                    <Outlet />
                </div>
            </main>
            <footer className="p-4 text-muted-foreground bg-header  text-center">
                <small>© 2025</small>
            </footer>
        </div>
    );
}
