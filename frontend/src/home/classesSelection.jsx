import {useState} from "react";
import {CheckboxGroup, Checkbox, Input} from "@heroui/react";
import ClassesList from "../components/classesList.jsx";

export default function ClassesSelection() {
    const [cities] = useState([
        {value: "user-authentication-controller", label: "UserAuthenticationController"},
        {value: "abstract-data-factory", label: "AbstractDataFactory"},
        {value: "payment-gateway-service", label: "PaymentGatewayService"},
        {value: "legacy-system-adapter", label: "LegacySystemAdapter"},
        {value: "global-configuration-manager", label: "GlobalConfigurationManager"},
        {value: "async-message-consumer", label: "AsyncMessageConsumer"},
        {value: "database-connection-pool", label: "DatabaseConnectionPool"},
        {value: "json-response-builder", label: "JsonResponseBuilder"},
        {value: "security-policy-enforcer", label: "SecurityPolicyEnforcer"},
        {value: "xml-http-request-handler", label: "XmlHttpRequestHandler"},
        {value: "main-application-runner", label: "MainApplicationRunner"},
        {value: "customer-repository-impl", label: "CustomerRepositoryImpl"},
        {value: "order-processing-strategy", label: "OrderProcessingStrategy"},
        {value: "email-notification-sender", label: "EmailNotificationSender"},
        {value: "file-system-watcher", label: "FileSystemWatcher"},
        {value: "network-socket-listener", label: "NetworkSocketListener"},
        {value: "cache-invalidation-job", label: "CacheInvalidationJob"},
        {value: "error-logging-aspect", label: "ErrorLoggingAspect"},
        {value: "transaction-rollback-exception", label: "TransactionRollbackException"},
        {value: "virtual-machine-monitor", label: "VirtualMachineMonitor"},
    ]);
    const [selected, setSelected] = useState([]);
    const [keyword, setKeyword] = useState("");
    const [file, setFile] = useState(null);

    const filtered = cities.filter((c) => {
        const q = keyword.trim().toLowerCase();
        return q === "" || c.label.toLowerCase().includes(q) || c.value.toLowerCase().includes(q);
    });

    return (
        <>
            <div className="mb-[30px]">
                <Input
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    label="Cerca le classi del tuo progetto"
                    placeholder="Digita il nome di una classe..."
                    variant="bordered"
                    color="primary"
                    classNames={{
                        label: "text-gray-200",
                        input: "text-gray-200 placeholder:text-gray-400",
                    }}
                />
                <Input
                    type="file"
                    label="Upload your project ziped file..."
                    onChange={(e) => setFile(e.target.files[0])}
                    color="primary"
                    variant="bordered"
                    classNames={{
                        label: "text-gray-200",
                        input: "text-gray-200 placeholder:text-gray-400",
                    }}
                />
                {file && (
                    <span className="text-text-primary mt-2.5 block">
                        Uploaded file: {file.name}, {file.type}
                    </span>
                )}
            </div>
            <div className="h-[240px] overflow-y-auto w-full">
                <CheckboxGroup
                    defaultValue={[]}
                    onValueChange={setSelected}
                    classNames={{
                        label: "text-gray-200",
                    }}
                >
                    {filtered.map((city) => (
                        <Checkbox
                            key={city.value}
                            value={city.value}
                            classNames={{
                                label: "text-gray-200",
                            }}
                        >
                            <span className="text-text-primary">{city.label}</span>
                        </Checkbox>
                    ))}
                </CheckboxGroup>
            </div>
            { selected.length>0 && <span className="text-text-primary block w-full pt-[30px]">
                Selected Class:
                <ClassesList classesList={selected}/>
            </span>}
        </>
    );
}
