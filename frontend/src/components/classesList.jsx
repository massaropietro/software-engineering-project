import { ScrollArea } from "@/components/ui/scroll-area";

export default function ClassesList({ classesList }) {
    return (
        <div className="flex w-full flex-wrap md:flex-nowrap gap-4">
            <div className="w-full rounded-md border-2 border-white">
                <ScrollArea className="h-[300px] w-full">
                    <div className="p-1">
                        {classesList.map((item, index) => (
                            <div
                                key={index}
                                className="relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground text-input-foreground"
                            >
                                {item}
                            </div>
                        ))}
                    </div>
                </ScrollArea>
            </div>
        </div>
    );
}
