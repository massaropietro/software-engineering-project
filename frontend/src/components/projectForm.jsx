import React, { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Input, Textarea, Button, Form } from "@heroui/react";
import { yupResolver } from "@hookform/resolvers/yup";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from 'react-redux';
import { projectSchema } from "../validators/validators.js";
import { updateFormData, resetForm } from "../store/projectSlice.js";
import {paths} from "../constants/constants.js";

export default function ProjectForm() {
    const navigate = useNavigate();
    const dispatch = useDispatch();

    // Leggiamo lo stato attuale da Redux
    const projectState = useSelector((state) => state.project);

    const {
        handleSubmit,
        control,
        watch,
        formState: { errors }
    } = useForm({
        mode: "onChange",
        resolver: yupResolver(projectSchema),
        defaultValues: {
            projectName: projectState.projectName,
            description: projectState.description,
            repoUrl: projectState.repoUrl,
            // IMPORTANTE: Se c'è un file in Redux, lo passiamo come array (formato standard per input file)
            zipFile: projectState.zipFile ? [projectState.zipFile] : null
        }
    });

    const repoUrlValue = watch("repoUrl");
    const zipFileValue = watch("zipFile");

    const isRepoUrlFilled = repoUrlValue && repoUrlValue.length > 0;
    const isZipFileSelected = (zipFileValue && zipFileValue.length > 0) || !!projectState.zipFile;

    useEffect(() => {
        const subscription = watch((value) => {
            let fileObj = undefined;

            // Logica corretta: estraiamo l'oggetto File, non il nome
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
        console.log(projectState)
        return () => subscription.unsubscribe();
    }, [watch, dispatch, projectState.zipFile, projectState]);

    const onSubmit = (data) => {
        const file = data.zipFile ? data.zipFile[0] : null;
        console.log("Form Data:", { ...data, zipFile: file });
        navigate(paths.home);
    };

    const inputStyles = {
        label: "text-gray-200",
        input: "text-gray-200 placeholder:text-gray-400",
    };

    return (
        <Form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6 w-full">
            {/* Project Name */}
            <Controller
                name="projectName"
                control={control}
                render={({ field, fieldState: { invalid } }) => (
                    <Input
                        {...field}
                        label="Project Name"
                        placeholder="Inserisci il nome del progetto"
                        variant="bordered"
                        color="primary"
                        classNames={inputStyles}
                        isInvalid={invalid}
                        errorMessage={errors.projectName?.message}
                    />
                )}
            />

            {/* Description */}
            <Controller
                name="description"
                control={control}
                render={({ field, fieldState: { invalid } }) => (
                    <Textarea
                        {...field}
                        label="Description"
                        placeholder="Descrivi il tuo progetto..."
                        variant="bordered"
                        color="primary"
                        classNames={inputStyles}
                        isInvalid={invalid}
                        errorMessage={errors.description?.message}
                    />
                )}
            />

            {/* Row: Repo URL & Upload File Zip */}
            <div className="flex flex-col md:flex-row w-full gap-4 items-center md:items-start">
                <div className="w-full md:flex-1">
                    <Controller
                        name="repoUrl"
                        control={control}
                        render={({ field, fieldState: { invalid } }) => (
                            <Input
                                {...field}
                                label="Repo URL"
                                placeholder="https://github.com/username/repo"
                                variant="bordered"
                                color="primary"
                                classNames={inputStyles}
                                isInvalid={invalid}
                                errorMessage={errors.repoUrl?.message}
                                isDisabled={isZipFileSelected}
                            />
                        )}
                    />
                </div>

                <div className="flex items-center justify-center md:h-14">
                    <span className="text-gray-200 font-bold">Or</span>
                </div>

                <div className="flex-none">
                    <Controller
                        name="zipFile"
                        control={control}
                        render={({ field: { name, onBlur, onChange, value }, fieldState: { invalid } }) => (
                            <div className="flex flex-col relative">
                                <input
                                    type="file"
                                    id="zip-upload"
                                    className="hidden"
                                    name={name}
                                    onBlur={onBlur}
                                    onChange={(e) => onChange(e.target.files)}
                                    accept=".zip,application/zip"
                                    disabled={isRepoUrlFilled}
                                />
                                <label
                                    htmlFor="zip-upload"
                                    className={`m-0 ${isRepoUrlFilled ? 'cursor-not-allowed' : ''}`}
                                >
                                    <Button
                                        as="span"
                                        color={invalid ? "danger" : "primary"}
                                        variant="solid"
                                        className="cursor-pointer font-bold text-white shadow-lg h-14 px-6"
                                        isDisabled={isRepoUrlFilled}
                                    >
                                        {/* Mostra il nome dal form locale se c'è, altrimenti da Redux */}
                                        {(value && value.length > 0)
                                            ? value[0].name
                                            : (projectState.zipFile ? projectState.zipFile.name : "Upload Zip")}
                                    </Button>
                                </label>
                                {invalid && (
                                    <div className="text-tiny text-danger mt-1 absolute top-full left-0">
                                        {errors.zipFile?.message}
                                    </div>
                                )}
                            </div>
                        )}
                    />
                </div>
            </div>

            <Button
                type="submit"
                color="primary"
                className="mt-2 font-bold text-white shadow-lg mx-auto"
            >
                Invia Progetto
            </Button>
        </Form>
    );
}
