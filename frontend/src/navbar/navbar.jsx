import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import projectLogo from '@/assets/ema-icon-128.svg'

export default function Navigation() {
    return (
        <header className="bg-header h-20">
            <div className="container relative mx-auto flex h-full items-center px-4">
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                    <Link to="/" className="flex items-center gap-4 whitespace-nowrap">
                        <img src={projectLogo}
                             alt="Equivalent Mutants Analyzer Logo"
                             className="h-14 w-14" />
                        <span className="hidden md:block font-extrabold text-main text-lg md:text-xl lg:text-3xl tracking-tight drop-shadow-sm text-center whitespace-nowrap">Equivalent Mutants Analyzer</span>
                    </Link>
                </div>

                <nav className="ml-auto flex items-center">
                    <Button asChild className="bg-cta text-cta-foreground hover:bg-cta-hover focus-visible:ring-2 focus-visible:ring-cta-ring font-bold text-lg h-12 px-6">
                        <Link to="/about">About Us</Link>
                    </Button>
                </nav>
            </div>
        </header>
    );
};
