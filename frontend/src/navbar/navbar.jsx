import {useState} from "react";
import {
    Navbar,
    NavbarBrand,
    NavbarContent,
    NavbarItem,
    NavbarMenuToggle,
    NavbarMenu,
    NavbarMenuItem,
    Button
} from "@heroui/react";
import projectLogo from "../assets/ema-icon-128.svg";

export default function Navigation() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <Navbar
            onMenuOpenChange={setIsMenuOpen}
            position="static"
            className="bg-background-dark h-auto py-4"
            maxWidth="full"
        >
            <NavbarContent justify="start">
                <NavbarMenuToggle
                    aria-label={isMenuOpen ? "Chiudi menu" : "Apri menu"}
                    className="sm:hidden text-main"
                />
                <div />
            </NavbarContent>

            <NavbarContent justify="center">
                <NavbarBrand className="gap-2 items-center cursor-pointer">
                    <img
                        src={projectLogo}
                        alt="Equivalent Mutants Analyzer Logo"
                        className="p-2 w-20 h-20 md:w-24 md:h-24 lg:w-32 lg:h-32 transition-all"
                    />
                    <p className="font-extrabold text-main text-lg md:text-xl lg:text-3xl tracking-tight drop-shadow-sm text-center whitespace-nowrap">
                        Equivalent Mutants Analyzer
                    </p>
                </NavbarBrand>
            </NavbarContent>

            <NavbarContent justify="end" className="hidden sm:flex">
                <NavbarItem>
                    <Button as="a" color="primary" href="#" variant="flat" className="font-bold">
                        About Us
                    </Button>
                </NavbarItem>
            </NavbarContent>

            <NavbarMenu className="bg-background-dark/95 pt-10 gap-4">
                <NavbarMenuItem>
                    <Button
                        as="a"
                        color="primary"
                        href="#"
                        variant="flat"
                        className="font-bold w-full text-lg justify-start p-6"
                    >
                        About Us
                    </Button>
                </NavbarMenuItem>
            </NavbarMenu>
        </Navbar>
    );
}
