// file: 'app/src/components/classesList.jsx'
import {Listbox, ListboxItem} from "@heroui/react";

const ListboxWrapper = ({children}) => (
    <div className="w-full border-small px-1 py-2 rounded-small border-default-200 dark:border-default-100">
        {children}
    </div>
);

export default function ClassesList({classesList}) {
    return (
        <div className="flex w-full flex-wrap md:flex-nowrap gap-4">
            <ListboxWrapper>
                <Listbox
                    isVirtualized
                    className="w-full"
                    label={"Select from 1000 items"}
                    placeholder="Select..."
                    virtualization={{
                        maxListboxHeight: 300,
                        itemHeight: 60,
                    }}
                >
                    {classesList.map((item, index) => (
                        <ListboxItem key={index} value={item}>
                            {item}
                        </ListboxItem>
                    ))}
                </Listbox>
            </ListboxWrapper>
        </div>
    );
}
