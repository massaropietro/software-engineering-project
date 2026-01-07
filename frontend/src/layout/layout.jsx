import {Outlet} from "react-router-dom";
import {HeroUIProvider} from "@heroui/react";
import React from "react";
import Navigation from "../navbar/navbar.jsx";

export default function Layout() {
    return (
        <HeroUIProvider>
            <div className="min-h-screen bg-background flex flex-col">
                <Navigation/>
                <main className="flex-grow flex items-center justify-center p-6">
                    <div className="w-full max-w-[900px] bg-main rounded-3xl shadow-card p-10">
                        <Outlet />
                    </div>
                </main>
                <footer className="p-4 text-muted text-center">
                    <small>© 2025</small>
                </footer>
            </div>
        </HeroUIProvider>
    );
}
