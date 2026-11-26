import { useEffect, useState } from "react";
import { Activity, Database, Server } from "lucide-react";
import { healthAPI } from "../services/api";

function Dashboard() {
    const [backendStatus, setBackendStatus] = useState("Checking...");
    const [databaseStatus, setDatabaseStatus] = useState("Checking...");

    useEffect(() => {
        const checkServices = async () => {
            try {
                const response = await healthAPI.checkBackend();
                setBackendStatus(response.data.status);
            } catch {
                setBackendStatus("unavailable");
            }

            try {
                const response = await healthAPI.checkDatabase();
                setDatabaseStatus(response.data.status);
            } catch {
                setDatabaseStatus("unavailable");
            }
        };

        checkServices();
    }, []);

    return (
        <div className="min-h-screen bg-slate-950 text-white p-10">

            <div className="flex items-center gap-3 mb-3">
                <Activity className="text-blue-500" size={36} />

                <h1 className="text-4xl font-bold">
                    CodePulse
                </h1>
            </div>

            <p className="text-slate-400 mb-10">
                AI-Powered GitHub Repository Auditor
            </p>

            <h2 className="text-xl font-semibold mb-5">
                System Status
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <Server className="text-blue-400 mb-4" />

                    <h3 className="text-lg font-semibold">
                        Backend API
                    </h3>

                    <p className={
                        backendStatus === "healthy"
                            ? "text-green-400 mt-2"
                            : "text-slate-400 mt-2"
                    }>
                        {backendStatus}
                    </p>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <Database className="text-purple-400 mb-4" />

                    <h3 className="text-lg font-semibold">
                        PostgreSQL Database
                    </h3>

                    <p className={
                        databaseStatus === "healthy"
                            ? "text-green-400 mt-2"
                            : "text-slate-400 mt-2"
                    }>
                        {databaseStatus}
                    </p>
                </div>

            </div>
        </div>
    );
}

export default Dashboard;