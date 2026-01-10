import React, { useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from "@hookform/resolvers/yup";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from 'react-redux';

// Shadcn UI Imports
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";

import { projectSchema } from "../validators/validators.js";
import { updateFormData, resetForm } from "../store/projectSlice.js";
import { paths } from "../constants/constants.js";

export default function ProjectForm() {
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const fileInputRef = useRef(null);

    const projectState = useSelector((state) => state.project);

    const form = useForm({
        mode: "onChange",
        resolver: yupResolver(projectSchema),
        defaultValues: {
            projectName: projectState.projectName,
            description: projectState.description,
            repoUrl: projectState.repoUrl,
            zipFile: projectState.zipFile ? [projectState.zipFile] : null
        }
    });

    const { watch, handleSubmit, formState: { errors } } = form;

    const repoUrlValue = watch("repoUrl");
    const zipFileValue = watch("zipFile");

    const isRepoUrlFilled = repoUrlValue && repoUrlValue.length > 0;
    const isZipFileSelected = (zipFileValue && zipFileValue.length > 0) || !!projectState.zipFile;

    useEffect(() => {
        const subscription = watch((value) => {
            let fileObj = undefined;
            if (value.zipFile && value.zipFile.length > 0) {
                fileObj = value.zipFile[0];
            } else if (value.zipFile && value.zipFile.length === 0) {
                fileObj = null;
            }

            dispatch(updateFormData({
                projectName: value.projectName || "",
                description: value.description || "",
                repoUrl: value.repoUrl || "",
                zipFile: fileObj
            }));
        });
        return () => subscription.unsubscribe();
    }, [watch, dispatch, projectState.zipFile, projectState]);

    const onSubmit = (data) => {
        const file = data.zipFile ? data.zipFile[0] : null;
        console.log("Form Data:", { ...data, zipFile: file });

        dispatch(resetForm());
        navigate(paths.home);
    };

    return (
        <Form {...form}>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 w-full">
                {/* Project Name */}
                <FormField
                    control={form.control}
                    name="projectName"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel className="text-input-foreground">Project Name</FormLabel>
                            <FormControl>
                                <Input
                                    placeholder="Inserisci il nome del progetto"
                                    className="text-input-foreground placeholder:text-gray-400 border-2 border-white h-14"
                                    {...field}
                                />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                {/* Description */}
                <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel className="text-input-foreground">Description</FormLabel>
                            <FormControl>
                                <Textarea
                                    placeholder="Descrivi il tuo progetto..."
                                    className="text-input-foreground placeholder:text-gray-400 border-2 border-white min-h-[100px]"
                                    {...field}
                                />
                            </FormControl>
                            <FormMessage />
                        </FormItem>
                    )}
                />

                {/* Row: Repo URL & Upload File Zip */}
                <div className="flex flex-col md:flex-row w-full gap-4 items-start">
                    <div className="w-full md:flex-1">
                        <FormField
                            control={form.control}
                            name="repoUrl"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel className="text-input-foreground">Repo URL</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="https://github.com/username/repo"
                                            className="text-input-foreground placeholder:text-gray-400 border-2 border-white h-14"
                                            disabled={isZipFileSelected}
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>

                    <div className="w-full md:w-auto flex items-center justify-center pt-2 md:pt-10">
                        <span className="text-input-foreground font-bold">Or</span>
                    </div>

                    <div className="w-full md:w-auto">
                        <FormField
                            control={form.control}
                            name="zipFile"
                            render={({ field: { name, onBlur, onChange, value } }) => (
                                <FormItem>
                                    <FormLabel className="hidden md:block md:invisible">Upload Zip</FormLabel>
                                    <FormControl>
                                        <div className="flex flex-col">
                                            <input
                                                type="file"
                                                ref={fileInputRef}
                                                className="hidden"
                                                name={name}
                                                onBlur={onBlur}
                                                onChange={(e) => onChange(e.target.files)}
                                                accept=".zip,application/zip"
                                                disabled={isRepoUrlFilled}
                                            />
                                            <Button
                                                type="button"
                                                variant={errors.zipFile ? "destructive" : "default"}
                                                // Aggiunto cursor-pointer
                                                className={`cursor-pointer font-bold text-input-foreground shadow-lg w-full md:w-auto px-6 h-14 ${
                                                    !errors.zipFile ? "bg-button hover:bg-button-hover" : ""
                                                }`}
                                                disabled={isRepoUrlFilled}
                                                onClick={() => fileInputRef.current?.click()}
                                            >
                                                {(value && value.length > 0)
                                                    ? value[0].name
                                                    : (projectState.zipFile ? projectState.zipFile.name : "Upload Zip")}
                                            </Button>
                                        </div>
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    </div>
                </div>

                <Button
                    type="submit"
                    size="lg"
                    // Aggiunto cursor-pointer
                    className="cursor-pointer mt-4 font-bold text-input-foreground shadow-lg mx-auto block bg-button hover:bg-button-hover"
                >
                    Invia Progetto
                </Button>
            </form>
        </Form>
    );
}
