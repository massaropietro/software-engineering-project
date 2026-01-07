import {createBrowserRouter, RouterProvider} from "react-router-dom";
import Layout from "./layout/layout.jsx";
import React from "react";
import ClassesSelection from "./home/classesSelection.jsx";
import { paths } from "./constants/constants.js";
import ProjectForm from "./components/projectForm.jsx";

const router = createBrowserRouter([
    {
        path: paths.home,
        element: <Layout />,
        children: [
            {
                index: true,
                element: <ProjectForm />
            },
            {
                path: paths.analyze,
                element: <ClassesSelection />
            },
        ],
    },
])

export default function App(){
    return <RouterProvider router={router} />;
}