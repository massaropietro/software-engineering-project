import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import ClassesList from "../components/classesList.jsx";

export default function ClassesSelection() {
    // Rimosso il campo 'value', ora gli oggetti hanno solo 'label'
    const [cities] = useState([
        { label: "UserAuthenticationController" },
        { label: "AbstractDataFactory" },
        { label: "PaymentGatewayService" },
        { label: "LegacySystemAdapter" },
        { label: "GlobalConfigurationManager" },
        { label: "AsyncMessageConsumer" },
        { label: "DatabaseConnectionPool" },
        { label: "JsonResponseBuilder" },
        { label: "SecurityPolicyEnforcer" },
        { label: "XmlHttpRequestHandler" },
        { label: "MainApplicationRunner" },
        { label: "CustomerRepositoryImpl" },
        { label: "OrderProcessingStrategy" },
        { label: "EmailNotificationSender" },
        { label: "FileSystemWatcher" },
        { label: "NetworkSocketListener" },
        { label: "CacheInvalidationJob" },
        { label: "ErrorLoggingAspect" },
        { label: "TransactionRollbackException" },
        { label: "VirtualMachineMonitor" },
    ]);
    const [selected, setSelected] = useState([]);
    const [keyword, setKeyword] = useState("");

    const filtered = cities.filter((c) => {
        const q = keyword.trim().toLowerCase();
        // Filtro solo su label dato che value non esiste più
        return q === "" || c.label.toLowerCase().includes(q);
    });

    const handleCheckboxChange = (checked, label) => {
        if (checked) {
            setSelected((prev) => [...prev, label]);
        } else {
            setSelected((prev) => prev.filter((item) => item !== label));
        }
    };

    // Logica per Select All basata sulla label
    const isAllSelected = cities.length > 0 && selected.length === cities.length;

    const handleSelectAllChange = (checked) => {
        if (checked) {
            setSelected(cities.map((c) => c.label));
        } else {
            setSelected([]);
        }
    };

    const hasSelection = selected.length > 0;

    // Nota: Ho rimosso la logica 'selectedLabels' perché ora 'selected' contiene direttamente le label.

    return (
        <div
            className={`flex flex-col lg:flex-row w-full gap-6 overflow-hidden mx-auto transition-all duration-700 ease-in-out ${
                hasSelection ? "lg:max-w-6xl max-w-xl" : "max-w-xl"
            }`}
        >
            {/* Pannello Sinistro: Selezione */}
            <div
                className={`flex flex-col space-y-6 transition-all duration-700 ease-in-out w-full ${
                    hasSelection ? "lg:w-1/2" : "w-full"
                }`}
            >
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="search-classes" className="text-input-foreground">
                        Cerca le classi del tuo progetto
                    </Label>
                    <Input
                        id="search-classes"
                        type="text"
                        value={keyword}
                        onChange={(e) => setKeyword(e.target.value)}
                        placeholder="Digita il nome di una classe..."
                        className="text-input-foreground placeholder:text-gray-400 border-2 border-white h-14"
                    />
                </div>

                <div className="flex flex-col space-y-2">
                    <div className="flex justify-start">
                        <div className="flex items-center space-x-2">
                            <Checkbox
                                id="select-all"
                                checked={isAllSelected}
                                onCheckedChange={handleSelectAllChange}
                                className="border-white data-[state=checked]:bg-white data-[state=checked]:text-black border-2"
                            />
                            <Label
                                htmlFor="select-all"
                                className="text-sm font-medium leading-none cursor-pointer text-input-foreground"
                            >
                                Seleziona tutto ({cities.length})
                            </Label>
                        </div>
                    </div>

                    <div className="rounded-md border-2 border-white p-4">
                        <ScrollArea className="h-[240px] w-full pr-4">
                            <div className="flex flex-col gap-3">
                                {filtered.map((city) => (
                                    <div key={city.label} className="flex items-center space-x-2">
                                        {/* Utilizzo city.label come ID e valore di riferimento */}
                                        <Checkbox
                                            id={city.label}
                                            checked={selected.includes(city.label)}
                                            className="border-white data-[state=checked]:bg-white data-[state=checked]:text-button border-2"
                                            onCheckedChange={(checked) => handleCheckboxChange(checked, city.label)}
                                        />
                                        <Label
                                            htmlFor={city.label}
                                            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer text-input-foreground"
                                        >
                                            {city.label}
                                        </Label>
                                    </div>
                                ))}
                            </div>
                        </ScrollArea>
                    </div>
                </div>
            </div>

            {/* Pannello Destro: Riepilogo Animato */}
            <div
                className={`flex flex-col space-y-4 overflow-hidden transition-[width,max-height,opacity,transform,padding] duration-700 ease-in-out justify-center ${
                    hasSelection
                        ? "w-full max-h-[1000px] opacity-100 translate-y-0 pt-6 border-t-2 border-white " +
                        "lg:w-1/2 lg:max-h-none lg:translate-x-0 lg:translate-y-0 lg:pt-0 lg:pl-6 lg:border-t-0 lg:border-l-2"
                        : "w-full max-h-0 opacity-0 translate-y-10 p-0 border-0 " +
                        "lg:w-0 lg:max-h-none lg:translate-x-10 lg:translate-y-0"
                }`}
            >
                <div>
                    <span className="text-input-foreground block mb-2 font-medium whitespace-nowrap">
                        Selected Class:
                    </span>
                    {/* Passo direttamente 'selected' che ora contiene le label */}
                    <ClassesList classesList={selected} />
                </div>
            </div>
        </div>
    );
}
